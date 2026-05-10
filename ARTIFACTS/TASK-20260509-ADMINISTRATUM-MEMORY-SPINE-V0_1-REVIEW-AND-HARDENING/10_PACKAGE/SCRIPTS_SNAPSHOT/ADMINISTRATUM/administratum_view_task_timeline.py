#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--task-id', required=True)
    parser.add_argument('--root', default=r'E:\IMPERIUM')
    args = parser.parse_args()

    root = Path(args.root)
    timeline = root / 'ORGANS' / 'ADMINISTRATUM' / 'MEMORY' / 'TASKS' / args.task_id / 'TASK_TIMELINE.jsonl'
    if not timeline.exists():
        print(f'Timeline not found: {timeline}')
        return 1

    lines = [ln for ln in timeline.read_text(encoding='utf-8-sig').splitlines() if ln.strip()]
    for ln in lines:
        evt = json.loads(ln)
        print(f"{evt.get('created_at')} | {evt.get('event_type')} | {evt.get('summary_ru')} | {evt.get('verdict')}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
