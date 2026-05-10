#!/usr/bin/env python3
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--task-id', required=True)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--root', default=r'E:\IMPERIUM')
    parser.add_argument('--review-package-root', default='')
    parser.add_argument('--enforce-extended-checks', action='store_true')
    args = parser.parse_args()

    root = Path(args.root)
    task_id = args.task_id
    artifact = root / 'ARTIFACTS' / task_id

    rules_path = root / 'ORGANS' / 'INQUISITION' / 'AUDIT_RULES' / 'POST_STAGE_AUDIT_RULES.json'
    receipts_dir = artifact / '03_RECEIPTS'
    dummy_output = artifact / '02_OUTPUTS' / 'dummy_stage_output.json'
    stage_receipt_path = receipts_dir / '05_stage_001_receipt.json'

    blockers = []
    fails = []
    findings = []

    if not rules_path.exists():
        blockers.append(f'Missing rules file: {rules_path}')
        rules = {}
    else:
        rules = json.loads(rules_path.read_text(encoding='utf-8-sig'))

    required_receipts = rules.get('required_receipts', [])
    forbidden_roots = [x.upper() for x in rules.get('forbidden_output_roots', [])]

    parsed_receipts = {}
    for rn in required_receipts:
        rp = receipts_dir / rn
        if not rp.exists():
            blockers.append(f'Missing required receipt: {rp}')
            continue
        try:
            parsed_receipts[rn] = json.loads(rp.read_text(encoding='utf-8-sig'))
        except Exception as ex:
            fails.append(f'Invalid JSON receipt {rp}: {ex}')

    if not dummy_output.exists():
        blockers.append(f'Missing dummy output: {dummy_output}')

    stage_receipt = None
    if stage_receipt_path.exists():
        try:
            stage_receipt = json.loads(stage_receipt_path.read_text(encoding='utf-8-sig'))
        except Exception as ex:
            fails.append(f'Invalid stage receipt JSON: {ex}')

    if stage_receipt and dummy_output.exists():
        expected_hash = stage_receipt.get('hashes', {}).get(str(dummy_output))
        actual_hash = sha256_of_file(dummy_output)
        if not expected_hash:
            fails.append('Stage receipt has no dummy output hash entry.')
        elif expected_hash != actual_hash:
            fails.append('Dummy output hash mismatch against stage receipt.')
        else:
            findings.append('Dummy output hash matches stage receipt.')

    for rn, rd in parsed_receipts.items():
        for op in rd.get('output_paths', []):
            u = str(op).upper()
            for fr in forbidden_roots:
                if u.startswith(fr):
                    fails.append(f'Forbidden output path in {rn}: {op}')

    prohibited_claim_phrases = [
        'claim full system readiness',
        'proved full system readiness',
        'final continuity ready',
        'baseline accepted'
    ]
    scan_candidates = [
        artifact / '07_CONTINUITY_CANDIDATE' / 'CONTINUITY_CANDIDATE.md',
        artifact / '08_OWNER_SUMMARY' / 'OWNER_SUMMARY.md'
    ]
    for pth in scan_candidates:
        if pth.exists():
            txt = pth.read_text(encoding='utf-8-sig').lower()
            for phrase in prohibited_claim_phrases:
                if phrase in txt:
                    hit_lines = [ln.strip() for ln in txt.splitlines() if phrase in ln]
                    actionable = False
                    for ln in hit_lines:
                        if 'do not' in ln or 'not proven' in ln or 'не доказано' in ln:
                            continue
                        actionable = True
                    if actionable:
                        fails.append(f'Prohibited claim phrase found in {pth.name}: {phrase}')

    # Fake canon claim detection: canon cannot be claimed unless doctrinarium verdict is canonical.
    doctr_receipt_path = receipts_dir / '00_doctrinarium_preflight_receipt.json'
    doctr_verdict = 'UNKNOWN'
    if doctr_receipt_path.exists():
        try:
            doctr_verdict = json.loads(doctr_receipt_path.read_text(encoding='utf-8-sig')).get('verdict', 'UNKNOWN')
        except Exception:
            doctr_verdict = 'UNKNOWN'
    canon_claim_phrases = [
        'canon doctrine ready',
        'canon_owner_approved',
        'доктрина канонична',
        'каноническая доктрина подтверждена'
    ]
    if doctr_verdict != 'CANON_DOCTRINE_READY':
        for pth in scan_candidates:
            if pth.exists():
                txt = pth.read_text(encoding='utf-8-sig').lower()
                for phrase in canon_claim_phrases:
                    if phrase.lower() in txt:
                        fails.append(f'Potential fake canon claim in {pth.name}: {phrase}')

    if args.enforce_extended_checks:
        continuity_json = artifact / '07_CONTINUITY_CANDIDATE' / 'CONTINUITY_CANDIDATE.json'
        expected_08 = str(receipts_dir / '08_continuity_candidate_receipt.json')
        if continuity_json.exists():
            try:
                cc = json.loads(continuity_json.read_text(encoding='utf-8-sig'))
                receipt_chain = [str(x) for x in cc.get('receipt_chain', [])]
                if expected_08 not in receipt_chain:
                    fails.append('Continuity candidate receipt_chain missing 08_continuity_candidate_receipt.json path.')
            except Exception as ex:
                fails.append(f'Invalid continuity candidate JSON: {ex}')
        else:
            blockers.append(f'Missing continuity candidate JSON for extended check: {continuity_json}')

        if args.review_package_root:
            pkg_root = Path(args.review_package_root)
            snapshot_root = pkg_root / '10_PACKAGE' / 'SCRIPTS_SNAPSHOT'
            required_snapshots = [
                snapshot_root / 'DOCTRINARIUM' / 'doctrinarium_preflight.py',
                snapshot_root / 'OFFICIO_AGENTIS' / 'officio_agentis_scope.py',
                snapshot_root / 'ADMINISTRATUM' / 'administratum_record_event.py',
                snapshot_root / 'ADMINISTRATUM' / 'administratum_build_current_state.py',
                snapshot_root / 'ADMINISTRATUM' / 'administratum_view_task_timeline.py',
                snapshot_root / 'ADMINISTRATUM' / 'administratum_build_continuity_candidate.py',
                snapshot_root / 'ADMINISTRATUM' / 'imperium_task_start.ps1',
                snapshot_root / 'ASTRONOMICON' / 'astronomicon_load_route.py',
                snapshot_root / 'MECHANICUS' / 'mechanicus_resolve_scripts.py',
                snapshot_root / 'MECHANICUS' / 'mechanicus_dummy_stage.py',
                snapshot_root / 'INQUISITION' / 'inquisition_post_stage_audit.py'
            ]
            for req in required_snapshots:
                if not req.exists():
                    fails.append(f'Missing script snapshot file: {req}')
        else:
            blockers.append('Extended checks requested but review package root is empty.')

    manifest_path = artifact / '04_MANIFESTS' / 'MANIFEST.json'
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
            files = manifest.get('files', [])
            if str(manifest_path) in files:
                fails.append('Manifest self-reference detected.')
        except Exception as ex:
            fails.append(f'Invalid manifest JSON: {ex}')

    temp_hits = []
    for pth in artifact.rglob('*'):
        if pth.is_file():
            nm = pth.name.lower()
            if nm.endswith('.tmp') or nm.endswith('.temp') or nm.endswith('.bak') or nm.startswith('~'):
                temp_hits.append(str(pth))
    if temp_hits:
        fails.append('Dirty temp files found: ' + '; '.join(temp_hits))

    if fails:
        verdict = 'FAIL_AUDIT'
        next_action = 'Fix audit failures and rerun.'
    elif blockers:
        verdict = 'BLOCKED_OWNER_DECISION_REQUIRED'
        next_action = 'Provide missing required artifacts/receipts and rerun.'
    else:
        verdict = 'PASS_AUDIT'
        next_action = 'Proceed to current state build.'

    audit_payload = {
        'schema_version': 'INQUISITION_POST_STAGE_AUDIT_V0_1',
        'task_id': task_id,
        'run_id': args.run_id,
        'verdict': verdict,
        'findings': findings,
        'blockers': blockers,
        'failures': fails,
        'created_at': now_iso()
    }

    audit_path = artifact / '06_AUDITS' / 'INQUISITION_POST_STAGE_AUDIT.json'
    write_json(audit_path, audit_payload)

    receipt_path = receipts_dir / '06_inquisition_post_stage_receipt.json'
    hashes = {}
    for pth in [rules_path, stage_receipt_path, dummy_output, audit_path]:
        if pth.exists():
            hashes[str(pth)] = sha256_of_file(pth)

    receipt = {
        'schema_version': 'RECEIPT_V0_1',
        'task_id': task_id,
        'run_id': args.run_id,
        'stage_id': 'STAGE-001',
        'actor': 'PC_SERVITOR',
        'organ': 'INQUISITION',
        'input_paths': [str(rules_path), str(receipts_dir), str(dummy_output)],
        'output_paths': [str(audit_path), str(receipt_path)],
        'hashes': hashes,
        'verdict': verdict,
        'blockers': blockers + fails,
        'next_action': next_action,
        'created_at': now_iso(),
        'no_delete_policy_observed': True,
        'no_archive_scan_policy_observed': True,
        'no_throne_policy_observed': True,
        'notes_ru': 'Постэтапный аудит завершен с проверкой receipt-цепочки и целостности output.'
    }
    write_json(receipt_path, receipt)

    return 0 if verdict == 'PASS_AUDIT' else 2


if __name__ == '__main__':
    raise SystemExit(main())
