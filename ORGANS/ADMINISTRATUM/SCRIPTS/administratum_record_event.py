#!/usr/bin/env python3
import argparse
import datetime as dt
import hashlib
import json
import uuid
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


def append_jsonl(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(obj, ensure_ascii=False) + '\n')


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--task-id', required=True)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--root', default=r'E:\IMPERIUM')
    parser.add_argument('--organ', default='ADMINISTRATUM')
    parser.add_argument('--actor', default='PC_SERVITOR')
    parser.add_argument('--event-type', default='CONTEXT_LOADED')
    parser.add_argument('--summary-ru', default='Контекст задачи загружен и память готова к записи.')
    parser.add_argument('--verdict', default='PASS_CONTEXT_RECORDED')
    parser.add_argument('--receipt-paths', nargs='*', default=[])
    parser.add_argument('--output-paths', nargs='*', default=[])
    args = parser.parse_args()

    root = Path(args.root)
    task_id = args.task_id
    artifact = root / 'ARTIFACTS' / task_id

    system_events = root / 'ORGANS' / 'ADMINISTRATUM' / 'MEMORY' / 'CHRONICLE' / 'system_events.jsonl'
    task_events = root / 'ORGANS' / 'ADMINISTRATUM' / 'MEMORY' / 'CHRONICLE' / 'task_events.jsonl'
    timeline = root / 'ORGANS' / 'ADMINISTRATUM' / 'MEMORY' / 'TASKS' / task_id / 'TASK_TIMELINE.jsonl'
    memory_index = root / 'ORGANS' / 'ADMINISTRATUM' / 'MEMORY' / 'TASKS' / task_id / 'TASK_MEMORY_INDEX.json'

    event = {
        'event_id': f'EVT-{uuid.uuid4()}',
        'task_id': task_id,
        'run_id': args.run_id,
        'organ': args.organ,
        'actor': args.actor,
        'event_type': args.event_type,
        'summary_ru': args.summary_ru,
        'verdict': args.verdict,
        'receipt_paths': args.receipt_paths,
        'output_paths': args.output_paths,
        'created_at': now_iso()
    }

    append_jsonl(system_events, event)
    append_jsonl(task_events, event)
    append_jsonl(timeline, event)

    index_payload = {
        'schema_version': 'TASK_MEMORY_INDEX_V0_1',
        'task_id': task_id,
        'last_event_id': event['event_id'],
        'timeline_path': str(timeline),
        'system_events_path': str(system_events),
        'task_events_path': str(task_events),
        'updated_at': now_iso()
    }
    write_json(memory_index, index_payload)

    receipt_path = artifact / '03_RECEIPTS' / '02_administratum_context_receipt.json'
    hashes = {
        str(system_events): sha256_of_file(system_events),
        str(task_events): sha256_of_file(task_events),
        str(timeline): sha256_of_file(timeline),
        str(memory_index): sha256_of_file(memory_index)
    }

    receipt = {
        'schema_version': 'RECEIPT_V0_1',
        'task_id': task_id,
        'run_id': args.run_id,
        'stage_id': None,
        'actor': args.actor,
        'organ': 'ADMINISTRATUM',
        'input_paths': [],
        'output_paths': [
            str(system_events),
            str(task_events),
            str(timeline),
            str(memory_index),
            str(receipt_path)
        ],
        'hashes': hashes,
        'verdict': 'PASS_CONTEXT_RECORDED',
        'blockers': [],
        'next_action': 'Proceed to Astronomicon route load.',
        'created_at': now_iso(),
        'no_delete_policy_observed': True,
        'no_archive_scan_policy_observed': True,
        'no_throne_policy_observed': True,
        'notes_ru': 'Событие контекста добавлено в append-only память и таймлайн задачи.'
    }
    write_json(receipt_path, receipt)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
