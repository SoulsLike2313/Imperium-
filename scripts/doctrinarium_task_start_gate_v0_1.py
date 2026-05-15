"""Task start gate checker for Doctrinarium STAGE-5."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List

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
STAGE_ID = "STAGE-5"
REQUEST_DEFAULT = DOCTRINARIUM_ROOT / "GATES" / "task_start_gate_request_v0_1.json"
VERDICT_REPORT = REPORTS_DIR / "task_start_gate_verdict_report.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", default=TASK_ID)
    parser.add_argument("--requesting-agent", default="PC Servitor")
    parser.add_argument("--mode", default="cold_executor")
    parser.add_argument("--request-path", default=str(REQUEST_DEFAULT))
    return parser.parse_args()


def compute_blockers() -> Dict[str, List[str]]:
    blockers: List[str] = []
    warnings: List[str] = []
    evidence_paths: List[str] = []

    report_paths = {
        "law_registry": REPORTS_DIR / "law_registry_validation_report.json",
        "law_integrity": REPORTS_DIR / "law_integrity_report.json",
        "organ_health": REPORTS_DIR / "organ_health_verdict_report.json",
    }
    docs: Dict[str, Dict[str, object]] = {}
    for name, path in report_paths.items():
        rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
        if not path.exists():
            blockers.append(f"missing_required_report:{name}")
            continue
        docs[name] = load_json(path)
        evidence_paths.append(rel)

    lr_verdict = str(docs.get("law_registry", {}).get("verdict", ""))
    if lr_verdict != "PASS":
        blockers.append("law_registry_not_pass")

    li_verdict = str(docs.get("law_integrity", {}).get("verdict", ""))
    if li_verdict != "PASS":
        blockers.append("law_integrity_not_pass")

    oh_verdict = str(docs.get("organ_health", {}).get("verdict", ""))
    if oh_verdict not in ("PASS", "PASS_WITH_WARNINGS"):
        blockers.append("organ_health_report_not_pass")
    health_state = str(docs.get("organ_health", {}).get("health_verdict", ""))
    if health_state != "HEALTHY":
        blockers.append("organ_health_not_healthy")
    if oh_verdict == "PASS_WITH_WARNINGS":
        warnings.append("organ_health_has_non_blocking_warnings")

    return {"blockers": blockers, "warnings": warnings, "evidence_paths": evidence_paths}


def decide_gate(blockers: List[str]) -> Dict[str, object]:
    allow_execution = not blockers
    verdict = "ALLOW" if allow_execution else "BLOCK"
    reasons = blockers if blockers else ["all_required_checks_passed"]
    return {"allow_execution": allow_execution, "verdict": verdict, "reasons": reasons}


def main() -> int:
    args = parse_args()
    request_path = Path(args.request_path)
    request_path.parent.mkdir(parents=True, exist_ok=True)

    request_doc = {
        "schema_version": "imperium.doctrinarium.task_start_gate_request.v0_1",
        "task_id": args.task_id,
        "requesting_agent": args.requesting_agent,
        "mode": args.mode,
        "requested_utc": now_utc(),
        "provenance": {"source": "doctrinarium_task_start_gate_v0_1.py"},
        "timestamp_utc": now_utc(),
    }
    dump_json(request_path, request_doc)

    computed = compute_blockers()
    blockers = computed["blockers"]
    warnings = computed["warnings"]
    evidence_paths = [str(request_path.relative_to(REPO_ROOT)).replace("\\", "/")] + computed["evidence_paths"]

    decision = decide_gate(blockers)
    allow_execution = bool(decision["allow_execution"])
    verdict = str(decision["verdict"])

    # Built-in self-test: any explicit blocker list must force BLOCK.
    self_test_decision = decide_gate(["sample_blocker"])
    self_test_ok = (
        self_test_decision["allow_execution"] is False and self_test_decision["verdict"] == "BLOCK"
    )
    if not self_test_ok:
        blockers.append("self_test_failed_blocker_did_not_block")
        decision = decide_gate(blockers)
        allow_execution = bool(decision["allow_execution"])
        verdict = str(decision["verdict"])

    report = build_report_base(
        report_id="doctrinarium.task_start_gate.v0_1",
        task_id=TASK_ID,
        stage_id=STAGE_ID,
    )
    report.update(
        {
            "started_utc": now_utc(),
            "completed_utc": now_utc(),
            "request": request_doc,
            "task_id": args.task_id,
            "verdict": verdict,
            "allow_execution": allow_execution,
            "reasons": decision["reasons"],
            "warnings": warnings,
            "blockers": blockers,
            "evidence_paths": evidence_paths,
            "provenance": {"source": "doctrinarium_task_start_gate_v0_1.py"},
            "self_test": {
                "forced_blockers_result": self_test_decision["verdict"],
                "passed": self_test_ok,
            },
        }
    )
    dump_json(VERDICT_REPORT, report)
    return 0 if allow_execution else 1


if __name__ == "__main__":
    raise SystemExit(main())
