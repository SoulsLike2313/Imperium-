#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List

from continuity_common import now_utc, safe_read_text, write_json, write_text


def add_blocker(items: List[Dict[str, Any]], blocker_id: str, severity: str, status: str, message: str, evidence_path: str, next_step: str) -> None:
    items.append(
        {
            "blocker_id": blocker_id,
            "severity": severity,
            "status": status,
            "message": message,
            "evidence_path": evidence_path,
            "next_step": next_step,
        }
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan known blockers from artifacts and manual proofs")
    parser.add_argument("--imperium-root", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    root = Path(args.imperium_root).resolve()
    artifacts_root = root / "ARTIFACTS"
    manual_root = artifacts_root / "_MANUAL_PROOFS"
    blockers: List[Dict[str, Any]] = []

    # Blocker 1: stage-id schema mismatch evidence
    stage_mismatch_evidence = manual_root / "TASK-20260509-0014F0-VM2-LIVE-MANUAL-PROBE-V1" / "OWNER_SUMMARY_VM2_LIVE_MANUAL_PROBE.md"
    if stage_mismatch_evidence.exists():
        txt = safe_read_text(stage_mismatch_evidence)
        if "rejects PC-STAGE-001" in txt and "accepts STAGE-PC-001" in txt:
            add_blocker(
                blockers,
                blocker_id="BLK-STAGE-ID-SCHEMA-MISMATCH",
                severity="P1",
                status="OPEN",
                message="Current send_prompt_to_vm2.py stage-id format mismatch: rejects PC-STAGE-001, accepts STAGE-PC-001.",
                evidence_path=str(stage_mismatch_evidence),
                next_step="TASK-20260509-0016B-CONTINUITY-PLUS-STAGE-ID-REPAIR-DECISION",
            )

    # Blocker 2: stale 0014E1 internal reports superseded by owner-manual proof
    stale_evidence = manual_root / "TASK-20260508-0014E1-RUNTIME-EVIDENCE-PACKAGING-REPAIR-V1"
    if stale_evidence.exists():
        add_blocker(
            blockers,
            blocker_id="WRN-0014E1-STALE-INTERNAL-SUPERSEDED",
            severity="P2",
            status="TRACKED",
            message="0014E1 had stale internal packaging report history; owner-manual final hash proof exists and should be treated as superseding evidence.",
            evidence_path=str(stale_evidence),
            next_step="Keep manual supersession evidence attached to continuity handoff.",
        )

    # Blocker 3: 0014D skeleton-only
    d1 = artifacts_root / "TASK-20260508-0014D-IMPERIUM-STAGE-COORDINATION-SKELETON-AND-SPECULUM-SNAPSHOT-V1"
    if d1.exists():
        add_blocker(
            blockers,
            blocker_id="WRN-0014D-SKELETON-ONLY",
            severity="P2",
            status="OPEN",
            message="0014D is a skeleton contract layer and not a full coordination runtime implementation.",
            evidence_path=str(d1),
            next_step="Rely on 0014E+ and future tasks for runtime evidence.",
        )

    # Blocker 4: 0014F full local dry-run not yet done (task folder missing)
    has_0014f = any(p.name.startswith("TASK-20260508-0014F-") or p.name.startswith("TASK-20260509-0014F-") for p in artifacts_root.iterdir() if p.is_dir())
    if not has_0014f:
        add_blocker(
            blockers,
            blocker_id="BLK-0014F-NOT-DONE",
            severity="P1",
            status="OPEN",
            message="Full local coordination dry-run task 0014F not detected in normal artifact layer.",
            evidence_path=str(artifacts_root),
            next_step="Execute 0014F local multi-stage dry-run before 0015.",
        )

    # Blocker 5: 0014G harness not yet done
    has_0014g = any(p.name.startswith("TASK-20260508-0014G-") or p.name.startswith("TASK-20260509-0014G-") for p in artifacts_root.iterdir() if p.is_dir())
    if not has_0014g:
        add_blocker(
            blockers,
            blocker_id="BLK-0014G-NOT-DONE",
            severity="P1",
            status="OPEN",
            message="0014G agent/script harness task not detected in artifact layer.",
            evidence_path=str(artifacts_root),
            next_step="Implement and verify 0014G before 0015 E2E readiness claim.",
        )

    # Blocker 6: 0015 blocked until 0014F+0014G
    if (not has_0014f) or (not has_0014g):
        add_blocker(
            blockers,
            blocker_id="BLK-0015-BLOCKED-BY-0014F-0014G",
            severity="P0",
            status="OPEN",
            message="0015 PC-VM2 E2E remains blocked until both 0014F and 0014G are completed and reviewed.",
            evidence_path=str(artifacts_root),
            next_step="Do not start 0015 yet.",
        )

    recommended = "TASK-20260509-0016B-CONTINUITY-PLUS-STAGE-ID-REPAIR-DECISION"
    payload = {
        "generated_at_utc": now_utc(),
        "known_blockers_count": len(blockers),
        "blockers": blockers,
        "recommended_next_task_id": recommended,
        "verdict": "PARTIAL" if blockers else "PASS",
    }
    write_json(Path(args.output_json), payload)

    lines = [
        "# KNOWN_BLOCKERS",
        "",
        f"generated_at_utc: {payload['generated_at_utc']}",
        f"known_blockers_count: {len(blockers)}",
        "",
        "## Blockers",
    ]
    if blockers:
        for b in blockers:
            lines.append(
                f"- {b['blocker_id']} [{b['severity']}] {b['status']}: {b['message']} | evidence={b['evidence_path']} | next={b['next_step']}"
            )
    else:
        lines.append("- NONE")
    lines.append("")
    lines.append(f"recommended_next_task_id: {recommended}")
    lines.append(f"verdict: {payload['verdict']}")
    write_text(Path(args.output_md), "\n".join(lines))

    print(f"continuity_scan_known_blockers: count={len(blockers)} verdict={payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
