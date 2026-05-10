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
    parser.add_argument('--stage-id', default='STAGE-001')
    parser.add_argument('--root', default=r'E:\IMPERIUM')
    args = parser.parse_args()

    root = Path(args.root)
    task_id = args.task_id
    artifact = root / 'ARTIFACTS' / task_id

    output_path = artifact / '02_OUTPUTS' / 'dummy_stage_output.json'
    payload = {
        'schema_version': 'DUMMY_STAGE_OUTPUT_V0_1',
        'task_id': task_id,
        'run_id': args.run_id,
        'stage_id': args.stage_id,
        'status': 'DUMMY_SAFE_WRITE_DONE',
        'notes_ru': 'Безопасный тестовый этап выполнен локально.',
        'created_at': now_iso()
    }
    write_json(output_path, payload)
    output_hash = sha256_of_file(output_path)

    receipt_path = artifact / '03_RECEIPTS' / '05_stage_001_receipt.json'
    receipt = {
        'schema_version': 'RECEIPT_V0_1',
        'task_id': task_id,
        'run_id': args.run_id,
        'stage_id': args.stage_id,
        'actor': 'PC_SERVITOR',
        'organ': 'MECHANICUS',
        'input_paths': [str(artifact / '01_ROUTE' / 'STAGE_MAP.json')],
        'output_paths': [str(output_path), str(receipt_path)],
        'hashes': {
            str(output_path): output_hash
        },
        'verdict': 'PASS_STAGE_EXECUTED',
        'blockers': [],
        'next_action': 'Proceed to Inquisition post-stage audit.',
        'created_at': now_iso(),
        'no_delete_policy_observed': True,
        'no_archive_scan_policy_observed': True,
        'no_throne_policy_observed': True,
        'notes_ru': 'Dummy stage выполнил только безопасную запись выходного файла и receipt.'
    }
    write_json(receipt_path, receipt)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
