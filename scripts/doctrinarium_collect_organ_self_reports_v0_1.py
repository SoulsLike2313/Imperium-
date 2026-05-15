"""Collect organ self-reports for Doctrinarium STAGE-4."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from doctrinarium_common_v0_1 import (
    DOCTRINARIUM_ROOT,
    REPORTS_DIR,
    REPO_ROOT,
    build_report_base,
    dump_json,
    load_json,
    now_utc,
)


TASK_ID = "TASK-20260515-DOCTRINARIUM-MVP-V0_1"
STAGE_ID = "STAGE-4"
COLLECTION_REPORT = REPORTS_DIR / "organ_self_report_collection_report.json"
COLLECTED_DIR = DOCTRINARIUM_ROOT / "ORGAN_HEALTH" / "COLLECTED_SELF_REPORTS"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--required-organs",
        default="DOCTRINARIUM",
        help="Comma-separated organ list for required self-reports.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    required_organs = [item.strip() for item in args.required_organs.split(",") if item.strip()]
    collected: List[str] = []
    missing: List[str] = []
    warnings: List[str] = []
    blockers: List[str] = []

    COLLECTED_DIR.mkdir(parents=True, exist_ok=True)

    for organ_id in required_organs:
        source_path = REPO_ROOT / "ORGANS" / organ_id / "REPORTS" / "organ_self_report_v0_1.json"
        if not source_path.exists():
            missing.append(organ_id)
            continue
        try:
            data = load_json(source_path)
            target_path = COLLECTED_DIR / f"{organ_id}_self_report.json"
            dump_json(target_path, data)
            collected.append(organ_id)
        except Exception as exc:  # pragma: no cover - diagnostic path
            blockers.append(f"self_report_parse_failed:{organ_id}:{exc}")

    if missing:
        warnings.append(f"missing_self_reports:{','.join(missing)}")

    verdict = "PASS" if not blockers else "FAIL"
    report = build_report_base(
        report_id="doctrinarium.organ_self_report_collection.v0_1",
        task_id=TASK_ID,
        stage_id=STAGE_ID,
    )
    report.update(
        {
            "started_utc": now_utc(),
            "completed_utc": now_utc(),
            "verdict": verdict,
            "required_organs": required_organs,
            "organs_collected": collected,
            "missing_organs": missing,
            "warnings": warnings,
            "blockers": blockers,
            "evidence_paths": [
                str((COLLECTED_DIR / f"{organ_id}_self_report.json").relative_to(REPO_ROOT)).replace("\\", "/")
                for organ_id in collected
            ],
        }
    )
    dump_json(COLLECTION_REPORT, report)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

