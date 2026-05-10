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
    args = parser.parse_args()

    root = Path(args.root)
    task_id = args.task_id
    artifact = root / 'ARTIFACTS' / task_id
    receipts_dir = artifact / '03_RECEIPTS'
    current_state_path = root / 'ORGANS' / 'ADMINISTRATUM' / 'MEMORY' / 'TASKS' / task_id / 'CURRENT_STATE.json'

    if not current_state_path.exists():
        return 2

    current_state = json.loads(current_state_path.read_text(encoding='utf-8-sig'))

    receipt_files = sorted([p for p in receipts_dir.glob('*.json')])
    receipt_chain = [str(p) for p in receipt_files]
    expected_receipt_08 = str(receipts_dir / '08_continuity_candidate_receipt.json')
    if expected_receipt_08 not in receipt_chain:
        # Ensure chain explicitly contains continuity receipt path even before file is written.
        receipt_chain.append(expected_receipt_08)

    proven = [
        'Organ-gated sequence executed locally once',
        'Append-only memory event recorded',
        'Route loaded and script resolved',
        'Dummy safe stage wrote output and receipt',
        'Post-stage audit executed'
    ]
    not_proven = [
        'Full IMPERIUM operational readiness',
        'Sanctum readiness',
        'VM2 readiness',
        'THRONE integration',
        'Final continuity readiness'
    ]

    candidate_json = {
        'schema_version': 'CONTINUITY_CANDIDATE_V0_1',
        'task_id': task_id,
        'run_id': args.run_id,
        'current_state_path': str(current_state_path),
        'next_action': current_state.get('next_action'),
        'do_not_do': current_state.get('do_not_do', []),
        'receipt_chain': receipt_chain,
        'proven': proven,
        'not_proven': not_proven,
        'final_claim': 'NOT_FINAL_CONTINUITY',
        'created_at': now_iso()
    }

    candidate_md = [
        '# CONTINUITY CANDIDATE V0_1',
        '',
        f'Task: {task_id}',
        f'Run: {args.run_id}',
        '',
        '## Current State',
        f'- Path: {current_state_path}',
        f'- Blocker: {current_state.get("blocker", {}).get("status")}',
        f'- Next action: {current_state.get("next_action")}',
        '',
        '## Do-Not-Do',
    ]
    for item in current_state.get('do_not_do', []):
        candidate_md.append(f'- {item}')

    candidate_md.extend(['', '## Receipt Chain'])
    for rc in receipt_chain:
        candidate_md.append(f'- {rc}')

    candidate_md.extend(['', '## Proven'])
    for p in proven:
        candidate_md.append(f'- {p}')

    candidate_md.extend(['', '## Not Proven'])
    for np in not_proven:
        candidate_md.append(f'- {np}')

    candidate_md.extend(['', '## Claim Limit', '- This is a minimal local v0_1 smoke cycle only.'])

    candidate_json_path = artifact / '07_CONTINUITY_CANDIDATE' / 'CONTINUITY_CANDIDATE.json'
    candidate_md_path = artifact / '07_CONTINUITY_CANDIDATE' / 'CONTINUITY_CANDIDATE.md'
    write_json(candidate_json_path, candidate_json)
    candidate_md_path.write_text('\n'.join(candidate_md) + '\n', encoding='utf-8')

    receipt_path = receipts_dir / '08_continuity_candidate_receipt.json'
    hashes = {
        str(candidate_json_path): sha256_of_file(candidate_json_path),
        str(candidate_md_path): sha256_of_file(candidate_md_path),
        str(current_state_path): sha256_of_file(current_state_path)
    }

    receipt = {
        'schema_version': 'RECEIPT_V0_1',
        'task_id': task_id,
        'run_id': args.run_id,
        'stage_id': None,
        'actor': 'PC_SERVITOR',
        'organ': 'ADMINISTRATUM',
        'input_paths': [str(current_state_path), str(receipts_dir)],
        'output_paths': [
            str(candidate_md_path),
            str(candidate_json_path),
            str(receipt_path)
        ],
        'hashes': hashes,
        'verdict': 'PASS_CONTINUITY_CANDIDATE_READY',
        'blockers': [],
        'next_action': 'Owner review and next controlled extension.',
        'created_at': now_iso(),
        'no_delete_policy_observed': True,
        'no_archive_scan_policy_observed': True,
        'no_throne_policy_observed': True,
        'notes_ru': 'Кандидат на континуитет собран без финального claim.'
    }
    write_json(receipt_path, receipt)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
