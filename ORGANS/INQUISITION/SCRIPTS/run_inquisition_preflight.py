#!/usr/bin/env python3
"""Run bounded Inquisition preflight over route artifacts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

FORBIDDEN = {
    "latest_bundle": re.compile(r"latest[-_ ]bundle", re.IGNORECASE),
    "throne": re.compile(r"(throne[_\-\s]?(contact|connect|activate|enable))|(contact\s+throne)", re.IGNORECASE),
    "watcher_autosync": re.compile(
        r"(enable|start|create|launch)[^\n]{0,24}(watcher|autosync|background automation)"
        r"|((watcher|autosync)[^\n]{0,24}(enable|start|create|launch))",
        re.IGNORECASE,
    ),
}
DESTRUCTIVE = re.compile(
    r"rm\s+-rf|Remove-Item\s+.+-Recurse|shutil\.rmtree|os\.remove\(|unlink\(|rmdir\(|delete\s+(file|folder)",
    re.IGNORECASE,
)
FAKE_GREEN = re.compile(r"CONTINUITY_GREEN|LIVE_ORGAN|PRODUCTION_READY", re.IGNORECASE)
LEGACY_STAGE = re.compile(r"\bSTAGE-(PC|VM2)-\d{3}\b", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run Inquisition preflight and emit route reports.")
    p.add_argument("--scan-dir", required=True)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--task-id", required=True)
    p.add_argument("--run-id", required=True)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    scan_dir = Path(args.scan_dir).resolve()
    out = Path(args.output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    forbidden_hits = {k: [] for k in FORBIDDEN}
    fake_green_hits = []
    legacy_hits = []
    destructive_hits = []
    duplicate_names = {}
    name_index = {}

    for p in scan_dir.rglob("*"):
        if p.is_file():
            rel = str(p.relative_to(scan_dir)).replace("\\", "/")
            name_index.setdefault(p.name.lower(), []).append(rel)
            if p.suffix.lower() in {".md", ".txt", ".json", ".py"}:
                text = p.read_text(encoding="utf-8", errors="ignore")
                for key, rx in FORBIDDEN.items():
                    count = len(rx.findall(text))
                    if count:
                        forbidden_hits[key].append({"path": rel, "count": count})
                fg = len(FAKE_GREEN.findall(text))
                if fg:
                    fake_green_hits.append({"path": rel, "count": fg})
                lg = len(LEGACY_STAGE.findall(text))
                if lg:
                    legacy_hits.append({"path": rel, "count": lg})
                dg = len(DESTRUCTIVE.findall(text))
                if dg:
                    destructive_hits.append({"path": rel, "count": dg})

    for name, paths in name_index.items():
        if len(paths) > 1:
            duplicate_names[name] = paths

    forbidden_ref_count = sum(len(v) for v in forbidden_hits.values())
    destructive_effective = [row for row in destructive_hits if not row["path"].lower().endswith("deletion_proposals.md")]
    drift_duplicate_report = {
        "task_id": args.task_id,
        "run_id": args.run_id,
        "legacy_stage_id_hits": legacy_hits,
        "duplicate_filename_count": len(duplicate_names),
        "duplicate_filenames": duplicate_names,
        "verdict": "PASS_DRIFT_DUPLICATE" if not legacy_hits else "WARN_LEGACY_STAGE_IDS_PRESENT",
    }
    forbidden_refs_report = {
        "task_id": args.task_id,
        "run_id": args.run_id,
        "forbidden_hits": forbidden_hits,
        "destructive_hits": destructive_hits,
        "destructive_effective": destructive_effective,
        "forbidden_ref_count": forbidden_ref_count,
        "verdict": "PASS_FORBIDDEN_REFS"
        if forbidden_ref_count == 0 and not destructive_effective
        else "FAIL_FORBIDDEN_REFS",
    }
    fake_green_report = {
        "task_id": args.task_id,
        "run_id": args.run_id,
        "fake_green_hits": fake_green_hits,
        "verdict": "PASS_NO_FAKE_GREEN" if not fake_green_hits else "FAIL_FAKE_GREEN_DETECTED",
    }
    preflight = {
        "task_id": args.task_id,
        "run_id": args.run_id,
        "scope": str(scan_dir),
        "checks": [
            "forbidden refs",
            "legacy stage id drift",
            "duplicate filenames",
            "fake green markers",
        ],
        "verdict": "PASS_INQUISITION_PREFLIGHT"
        if forbidden_refs_report["verdict"] == "PASS_FORBIDDEN_REFS" and fake_green_report["verdict"] == "PASS_NO_FAKE_GREEN"
        else "BLOCKED_INQUISITION_PREFLIGHT",
    }

    (out / "INQUISITION_PREFLIGHT_REPORT.json").write_text(json.dumps(preflight, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "DRIFT_DUPLICATE_REPORT.json").write_text(json.dumps(drift_duplicate_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "FORBIDDEN_REFS_REPORT.json").write_text(json.dumps(forbidden_refs_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "FAKE_GREEN_REPORT.json").write_text(json.dumps(fake_green_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "DELETION_PROPOSALS.md").write_text(
        "# DELETION PROPOSALS\n\nNo delete actions executed.\nProposal-only mode.\n",
        encoding="utf-8",
    )
    (out / "INQUISITION_STOP_OR_PASS_RECEIPT.json").write_text(
        json.dumps(
            {
                "task_id": args.task_id,
                "run_id": args.run_id,
                "stage_id": "INQUISITION-STAGE-001",
                "status": "PASS" if preflight["verdict"] == "PASS_INQUISITION_PREFLIGHT" else "BLOCKED",
                "forbidden_ref_count": forbidden_ref_count,
                "next_allowed_action": "PC-STAGE-001" if preflight["verdict"] == "PASS_INQUISITION_PREFLIGHT" else "OWNER_REVIEW_REQUIRED",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(preflight, ensure_ascii=False, indent=2))
    return 0 if preflight["verdict"] == "PASS_INQUISITION_PREFLIGHT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
