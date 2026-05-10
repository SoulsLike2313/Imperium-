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
    task_dir = root / 'ORGANS' / 'ASTRONOMICON' / 'TASKS' / task_id

    stage_map_path = task_dir / 'STAGE_MAP.json'
    pass_criteria_path = task_dir / 'PASS_CRITERIA.json'

    blockers = []
    if not stage_map_path.exists():
        blockers.append(f'Missing STAGE_MAP: {stage_map_path}')
    if not pass_criteria_path.exists():
        blockers.append(f'Missing PASS_CRITERIA: {pass_criteria_path}')

    stage_map = {}
    if not blockers:
        stage_map = json.loads(stage_map_path.read_text(encoding='utf-8-sig'))
        stages = stage_map.get('stages', [])
        if len(stages) != 1:
            blockers.append('Stage map must contain exactly one stage for v0_1 smoke.')
        else:
            stage = stages[0]
            if stage.get('stage_id') != 'STAGE-001':
                blockers.append('Single stage id must be STAGE-001.')
            if stage.get('stage_type') != 'DUMMY_SAFE_WRITE':
                blockers.append('Single stage type must be DUMMY_SAFE_WRITE.')
            expected = str(stage.get('expected_output', ''))
            forbidden_roots = [r'E:\IMPERIUM\ARCHIVE', r'E:\IMPERIUM\SANCTUM', r'E:\IMPERIUM\THRONE']
            for fr in forbidden_roots:
                if expected.upper().startswith(fr.upper()):
                    blockers.append(f'Expected output points to forbidden root: {expected}')

    out_stage_map = artifact / '01_ROUTE' / 'STAGE_MAP.json'
    out_pass_criteria = artifact / '01_ROUTE' / 'PASS_CRITERIA.json'
    if not blockers:
        write_json(out_stage_map, stage_map)
        pass_data = json.loads(pass_criteria_path.read_text(encoding='utf-8-sig'))
        write_json(out_pass_criteria, pass_data)

    verdict = 'PASS_ROUTE_READY' if not blockers else 'BLOCKED_OWNER_DECISION_REQUIRED'
    next_action = 'Proceed to Mechanicus script resolution.' if not blockers else 'Fix route blockers before rerun.'

    hashes = {}
    for pth in [stage_map_path, pass_criteria_path, out_stage_map, out_pass_criteria]:
        if pth.exists():
            hashes[str(pth)] = sha256_of_file(pth)

    receipt = {
        'schema_version': 'RECEIPT_V0_1',
        'task_id': task_id,
        'run_id': args.run_id,
        'stage_id': None,
        'actor': 'PC_SERVITOR',
        'organ': 'ASTRONOMICON',
        'input_paths': [str(stage_map_path), str(pass_criteria_path)],
        'output_paths': [
            str(out_stage_map),
            str(out_pass_criteria),
            str(artifact / '03_RECEIPTS' / '03_astronomicon_route_receipt.json')
        ],
        'hashes': hashes,
        'verdict': verdict,
        'blockers': blockers,
        'next_action': next_action,
        'created_at': now_iso(),
        'no_delete_policy_observed': True,
        'no_archive_scan_policy_observed': True,
        'no_throne_policy_observed': True,
        'notes_ru': 'Маршрут загружен и проверен на запретные корни вывода.'
    }

    receipt_path = artifact / '03_RECEIPTS' / '03_astronomicon_route_receipt.json'
    write_json(receipt_path, receipt)
    return 0 if not blockers else 2


if __name__ == '__main__':
    raise SystemExit(main())
