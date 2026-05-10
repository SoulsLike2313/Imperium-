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

    stage_map_path = artifact / '01_ROUTE' / 'STAGE_MAP.json'
    registry_path = root / 'ORGANS' / 'MECHANICUS' / 'REGISTRY' / 'SCRIPT_REGISTRY.json'
    blockers = []

    if not stage_map_path.exists():
        blockers.append(f'Missing route stage map: {stage_map_path}')
    if not registry_path.exists():
        blockers.append(f'Missing script registry: {registry_path}')

    resolved = []
    if not blockers:
        stage_map = json.loads(stage_map_path.read_text(encoding='utf-8-sig'))
        registry = json.loads(registry_path.read_text(encoding='utf-8-sig'))
        scripts = registry.get('scripts', [])
        by_stage_type = {}
        for s in scripts:
            by_stage_type[s.get('stage_type')] = s

        for stg in stage_map.get('stages', []):
            stype = stg.get('stage_type')
            target = by_stage_type.get(stype)
            if not target:
                blockers.append(f'No registry script for stage type: {stype}')
                continue
            script_path = Path(target['path'])
            if not script_path.exists():
                blockers.append(f'Registry script path missing: {script_path}')
                continue
            resolved.append({
                'stage_id': stg.get('stage_id'),
                'stage_type': stype,
                'script_id': target.get('script_id'),
                'script_path': str(script_path),
                'script_sha256': sha256_of_file(script_path)
            })

    verdict = 'PASS_SCRIPT_RESOLVED' if not blockers else 'BLOCKED_OWNER_DECISION_REQUIRED'
    next_action = 'Proceed to stage execution.' if not blockers else 'Fix registry/stage map blockers.'

    resolution_payload = {
        'schema_version': 'SCRIPT_RESOLUTION_V0_1',
        'task_id': task_id,
        'run_id': args.run_id,
        'resolved': resolved,
        'blockers': blockers,
        'created_at': now_iso()
    }
    resolution_path = artifact / '03_RECEIPTS' / '04_mechanicus_script_resolution_receipt.json'

    hashes = {}
    for pth in [stage_map_path, registry_path]:
        if pth.exists():
            hashes[str(pth)] = sha256_of_file(pth)

    receipt = {
        'schema_version': 'RECEIPT_V0_1',
        'task_id': task_id,
        'run_id': args.run_id,
        'stage_id': None,
        'actor': 'PC_SERVITOR',
        'organ': 'MECHANICUS',
        'input_paths': [str(stage_map_path), str(registry_path)],
        'output_paths': [str(resolution_path)],
        'hashes': hashes,
        'verdict': verdict,
        'blockers': blockers,
        'next_action': next_action,
        'created_at': now_iso(),
        'no_delete_policy_observed': True,
        'no_archive_scan_policy_observed': True,
        'no_throne_policy_observed': True,
        'notes_ru': 'Скрипт для этапа успешно разрешен по реестру.' if not blockers else 'Резолв скрипта заблокирован.',
        'resolved_scripts': resolved
    }

    write_json(resolution_path, receipt)
    return 0 if not blockers else 2


if __name__ == '__main__':
    raise SystemExit(main())
