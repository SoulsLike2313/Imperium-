#!/usr/bin/env python3
"""
Emit stage signal
Status: SKELETON_CONTRACT
Implementation: REQUIRED
"""

import argparse
import json
import sys
from datetime import datetime, timezone

STATUS = "SKELETON_CONTRACT"
IMPLEMENTATION = "IMPLEMENTATION_REQUIRED"


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_args():
    p = argparse.ArgumentParser(description="Emit stage signal (skeleton contract)")
    p.add_argument("--task-id", help="TASK_ID")
    p.add_argument("--stage-id", help="STAGE_ID")
    p.add_argument("--run-id", help="RUN_ID")
    p.add_argument("--contour-id", help="CONTOUR_ID")
    p.add_argument("--output", help="Optional output path")
    return p.parse_args()


def main():
    args = parse_args()
    payload = {
        "tool": "STAGE_SIGNAL_EMIT",
        "status": STATUS,
        "implementation": IMPLEMENTATION,
        "timestamp_utc": utc_now(),
        "task_id": args.task_id,
        "stage_id": args.stage_id,
        "run_id": args.run_id,
        "contour_id": args.contour_id,
        "note": "Skeleton only. Do not use for production or real E2E."
    }
    text = json.dumps(payload, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    print(text)
    return 2


if __name__ == "__main__":
    sys.exit(main())
