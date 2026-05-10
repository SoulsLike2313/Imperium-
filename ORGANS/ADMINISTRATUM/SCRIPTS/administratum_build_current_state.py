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


def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


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

    receipt_names = [
        '00_doctrinarium_preflight_receipt.json',
        '01_officio_agentis_scope_receipt.json',
        '02_administratum_context_receipt.json',
        '03_astronomicon_route_receipt.json',
        '04_mechanicus_script_resolution_receipt.json',
        '05_stage_001_receipt.json',
        '06_inquisition_post_stage_receipt.json'
    ]

    latest_receipts = {}
    blockers = []
    blocked_or_fail = []
    for name in receipt_names:
        rp = receipts_dir / name
        if not rp.exists():
            blockers.append(f'Missing required receipt: {rp}')
            continue
        data = read_json(rp)
        verdict = data.get('verdict', 'UNKNOWN')
        latest_receipts[name] = {'path': str(rp), 'verdict': verdict}
        if verdict.startswith('BLOCKED') or verdict.startswith('FAIL'):
            blocked_or_fail.append(f'{name}:{verdict}')

    timeline = root / 'ORGANS' / 'ADMINISTRATUM' / 'MEMORY' / 'TASKS' / task_id / 'TASK_TIMELINE.jsonl'
    current_state_path = root / 'ORGANS' / 'ADMINISTRATUM' / 'MEMORY' / 'TASKS' / task_id / 'CURRENT_STATE.json'
    system_current_path = root / 'ORGANS' / 'ADMINISTRATUM' / 'MEMORY' / 'CURRENT' / 'SYSTEM_CURRENT_STATE.json'
    active_tasks_path = root / 'ORGANS' / 'ADMINISTRATUM' / 'MEMORY' / 'CURRENT' / 'ACTIVE_TASKS.json'
    dummy_output = artifact / '02_OUTPUTS' / 'dummy_stage_output.json'

    do_not_do = [
        'Do not claim full system readiness',
        'Do not claim Sanctum readiness',
        'Do not claim VM2 readiness',
        'Do not claim final continuity readiness',
        'Do not perform delete/move/cleanup',
        'Do not scan ARCHIVE recursively'
    ]

    if blockers or blocked_or_fail:
        blocker_state = {
            'status': 'BLOCKED_OWNER_DECISION_REQUIRED',
            'details': blockers + blocked_or_fail
        }
        next_action = 'Resolve blocked/failed gate and rerun from entrypoint.'
        verdict = 'BLOCKED_OWNER_DECISION_REQUIRED'
    else:
        blocker_state = {'status': 'NONE', 'details': []}
        next_action = 'Review continuity candidate and decide next extension step.'
        verdict = 'PASS_CURRENT_STATE_READY'

    current_state = {
        'schema_version': 'TASK_CURRENT_STATE_V0_1',
        'task_id': task_id,
        'run_id': args.run_id,
        'source_of_truth': [
            str(receipts_dir),
            str(timeline)
        ],
        'blocker': blocker_state,
        'next_action': next_action,
        'do_not_do': do_not_do,
        'latest_receipts': latest_receipts,
        'latest_artifacts': {
            'dummy_output': str(dummy_output) if dummy_output.exists() else None,
            'audit': str(artifact / '06_AUDITS' / 'INQUISITION_POST_STAGE_AUDIT.json')
        },
        'owner_acceptance_state': 'NOT_ACCEPTED',
        'updated_at': now_iso()
    }

    write_json(current_state_path, current_state)

    system_state = {
        'schema_version': 'SYSTEM_CURRENT_STATE_V0_1',
        'last_task_id': task_id,
        'last_run_id': args.run_id,
        'last_task_state_path': str(current_state_path),
        'updated_at': now_iso()
    }
    write_json(system_current_path, system_state)

    active_tasks = {
        'schema_version': 'ACTIVE_TASKS_V0_1',
        'active_tasks': [
            {
                'task_id': task_id,
                'state': blocker_state['status'],
                'current_state_path': str(current_state_path)
            }
        ],
        'updated_at': now_iso()
    }
    write_json(active_tasks_path, active_tasks)

    snapshot_path = artifact / '07_CONTINUITY_CANDIDATE' / 'CURRENT_STATE_SNAPSHOT.json'
    write_json(snapshot_path, current_state)

    receipt_path = receipts_dir / '07_task_summary_receipt.json'
    hashes = {}
    for pth in [current_state_path, system_current_path, active_tasks_path, snapshot_path]:
        if pth.exists():
            hashes[str(pth)] = sha256_of_file(pth)

    receipt = {
        'schema_version': 'RECEIPT_V0_1',
        'task_id': task_id,
        'run_id': args.run_id,
        'stage_id': None,
        'actor': 'PC_SERVITOR',
        'organ': 'ADMINISTRATUM',
        'input_paths': [str(receipts_dir), str(timeline)],
        'output_paths': [
            str(current_state_path),
            str(snapshot_path),
            str(system_current_path),
            str(active_tasks_path),
            str(receipt_path)
        ],
        'hashes': hashes,
        'verdict': verdict,
        'blockers': blocker_state['details'],
        'next_action': next_action,
        'created_at': now_iso(),
        'no_delete_policy_observed': True,
        'no_archive_scan_policy_observed': True,
        'no_throne_policy_observed': True,
        'notes_ru': 'Собрано текущее состояние задачи на основе цепочки receipt и таймлайна.'
    }
    write_json(receipt_path, receipt)

    return 0 if verdict.startswith('PASS') else 2


if __name__ == '__main__':
    raise SystemExit(main())
