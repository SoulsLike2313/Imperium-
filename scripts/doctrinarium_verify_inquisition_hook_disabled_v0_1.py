"""Generate and verify disabled Inquisition hook packet for STAGE-6."""

from __future__ import annotations

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
STAGE_ID = "STAGE-6"
PACKET_PATH = DOCTRINARIUM_ROOT / "INQUISITION_HOOKS" / "inquisition_hook_packet_v0_1.json"
REPORT_PATH = REPORTS_DIR / "inquisition_hook_disabled_report.json"


def main() -> int:
    warnings = []
    blockers = []
    evidence_paths = []

    violation_report_path = REPORTS_DIR / "violation_record_report.json"
    if violation_report_path.exists():
        violation_report = load_json(violation_report_path)
        evidence_paths.append(str(violation_report_path.relative_to(REPO_ROOT)).replace("\\", "/"))
    else:
        violation_report = {}
        warnings.append("violation_report_not_found_for_packet_context")

    packet = {
        "schema_version": "imperium.doctrinarium.inquisition_hook_packet.v0_1",
        "packet_id": f"HOOK-{now_utc().replace(':', '').replace('-', '')}",
        "hook_status": "disabled",
        "disabled_reason": "Inquisition organ is not implemented in v0.1; active hook is forbidden.",
        "would_send_to": [],
        "send_attempted": False,
        "related_violation_id": violation_report.get("violation_id", "N/A"),
        "evidence_paths": evidence_paths,
        "provenance": {"source": "doctrinarium_verify_inquisition_hook_disabled_v0_1.py"},
        "timestamp_utc": now_utc(),
    }
    dump_json(PACKET_PATH, packet)
    evidence_paths.append(str(PACKET_PATH.relative_to(REPO_ROOT)).replace("\\", "/"))

    if packet["hook_status"] != "disabled":
        blockers.append("hook_status_not_disabled")
    if not packet.get("disabled_reason"):
        blockers.append("missing_disabled_reason")
    if packet.get("send_attempted") is not False:
        blockers.append("hook_packet_implies_send_attempt")
    if packet.get("would_send_to"):
        blockers.append("hook_packet_has_delivery_targets")

    verdict = "PASS" if not blockers else "FAIL"

    report = build_report_base(
        report_id="doctrinarium.inquisition_hook_disabled.v0_1",
        task_id=TASK_ID,
        stage_id=STAGE_ID,
    )
    report.update(
        {
            "started_utc": now_utc(),
            "completed_utc": now_utc(),
            "verdict": verdict,
            "hook_state": packet["hook_status"],
            "disabled_reason": packet["disabled_reason"],
            "send_attempted": packet["send_attempted"],
            "warnings": warnings,
            "blockers": blockers,
            "evidence_paths": evidence_paths,
        }
    )
    dump_json(REPORT_PATH, report)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

