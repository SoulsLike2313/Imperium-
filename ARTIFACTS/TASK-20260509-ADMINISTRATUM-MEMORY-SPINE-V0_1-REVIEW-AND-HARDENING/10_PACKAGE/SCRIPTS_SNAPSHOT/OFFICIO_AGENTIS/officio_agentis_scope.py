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
    parser.add_argument('--recipe-path', required=True)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--root', default=r'E:\IMPERIUM')
    args = parser.parse_args()

    root = Path(args.root)
    task_id = args.task_id
    artifact = root / 'ARTIFACTS' / task_id
    recipe_path = Path(args.recipe_path)

    doctr_receipt_path = artifact / '03_RECEIPTS' / '00_doctrinarium_preflight_receipt.json'
    blockers = []
    if not doctr_receipt_path.exists():
        blockers.append(f'Missing Doctrinarium receipt: {doctr_receipt_path}')
        doctr_verdict = 'MISSING'
    else:
        doctr_receipt = json.loads(doctr_receipt_path.read_text(encoding='utf-8-sig'))
        doctr_verdict = doctr_receipt.get('verdict', 'UNKNOWN')

    if doctr_verdict.startswith('FAIL') or doctr_verdict.startswith('BLOCKED'):
        blockers.append(f'Doctrinarium verdict not passable: {doctr_verdict}')

    scope_path = root / 'ORGANS' / 'OFFICIO_AGENTIS' / 'SCOPES' / task_id / 'AGENT_SCOPE.json'
    scope = {
        'schema_version': 'AGENT_SCOPE_V0_1',
        'task_id': task_id,
        'allowed_actions': [
            'read_task_recipe',
            'write_allowed_output_paths_only',
            'append_memory_events',
            'run_one_dummy_safe_stage',
            'write_receipts_and_audit',
            'stop_on_blocked_or_fail'
        ],
        'forbidden_actions': [
            'delete',
            'move',
            'cleanup',
            'archive_recursive_scan',
            'sanctum_modification',
            'vm2_activation',
            'throne_contact',
            'watcher_background_process',
            'final_readiness_claim',
            'baseline_claim_without_owner_acceptance'
        ],
        'owner_report_language': 'ru',
        'reporting_style': 'evidence_first',
        'stop_on_uncertainty': True,
        'stop_on_blocked_gate': True,
        'created_at': now_iso()
    }
    write_json(scope_path, scope)

    hashes = {}
    for pth in [recipe_path, doctr_receipt_path, scope_path]:
        if pth.exists():
            hashes[str(pth)] = sha256_of_file(pth)

    verdict = 'PASS_SCOPE_READY' if not blockers else 'BLOCKED_OWNER_DECISION_REQUIRED'
    next_action = 'Proceed to Administratum context event.' if not blockers else 'Resolve scope blockers and rerun.'

    receipt = {
        'schema_version': 'RECEIPT_V0_1',
        'task_id': task_id,
        'run_id': args.run_id,
        'stage_id': None,
        'actor': 'PC_SERVITOR',
        'organ': 'OFFICIO_AGENTIS',
        'input_paths': [str(recipe_path), str(doctr_receipt_path)],
        'output_paths': [
            str(scope_path),
            str(artifact / '03_RECEIPTS' / '01_officio_agentis_scope_receipt.json')
        ],
        'hashes': hashes,
        'verdict': verdict,
        'blockers': blockers,
        'next_action': next_action,
        'created_at': now_iso(),
        'no_delete_policy_observed': True,
        'no_archive_scan_policy_observed': True,
        'no_throne_policy_observed': True,
        'notes_ru': 'Скоуп агента сформирован с явными запретами и режимом evidence-first.'
    }

    receipt_path = artifact / '03_RECEIPTS' / '01_officio_agentis_scope_receipt.json'
    write_json(receipt_path, receipt)

    return 0 if not blockers else 2


if __name__ == '__main__':
    raise SystemExit(main())
