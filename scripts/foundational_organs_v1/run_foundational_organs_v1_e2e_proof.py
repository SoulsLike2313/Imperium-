from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from common import (
    LIVE_TASK_ROOT,
    ORGANS,
    TASK_ID,
    hardening_stage_report_map,
    rel,
    utc_now,
    write_json,
    write_stage_artifacts,
)


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_corridor(paths: dict[str, Path]) -> tuple[bool, list[str]]:
    missing = [name for name, path in paths.items() if not path.exists()]
    if missing:
        return False, [f"missing:{name}" for name in missing]
    return True, []


def run() -> int:
    now = utc_now()
    head = git_head()
    stage_sources = hardening_stage_report_map()

    astron = Path("ORGANS/ASTRONOMICON/V1/CORRIDOR/stage_map_v1.json")
    admin_route = Path("ORGANS/ADMINISTRATUM/V1/CORRIDOR/route_sheet_v1.json")
    admin_packet = Path("ORGANS/ADMINISTRATUM/V1/CORRIDOR/work_packet_v1.json")
    admin_receipt = Path("ORGANS/ADMINISTRATUM/REPORTS/V1/admin_stage_completion_receipt_v1.json")
    officio_read = Path("ORGANS/OFFICIO_AGENTIS/REPORTS/V1/role_read_receipt_v1.json")
    doctrinarium_gate = Path("ORGANS/DOCTRINARIUM/REPORTS/V1/task_start_gate_verdict_v1.json")
    sanctum_aggregate = Path("SANCTUM/DASHBOARD_DATA/FOUNDATIONAL_ORGANS_V1/sanctum_aggregate_state.json")

    required = {
        "stage_map": astron,
        "route_sheet": admin_route,
        "work_packet": admin_packet,
        "stage_completion_receipt": admin_receipt,
        "officio_role_read_receipt": officio_read,
        "task_start_gate_verdict": doctrinarium_gate,
        "sanctum_aggregate": sanctum_aggregate,
    }
    ok, blockers = evaluate_corridor({k: Path.cwd() / v for k, v in required.items()})
    success_checks: list[dict[str, Any]] = []
    if ok:
        gate = load_json(Path.cwd() / doctrinarium_gate)
        success_checks.append({"check": "task_start_gate_verdict", "value": gate.get("verdict"), "result": "PASS" if gate.get("verdict") == "ALLOW" else "FAIL"})
        for organ in ORGANS:
            state_path = Path(organ["base"]) / "V1" / "DASHBOARD_DATA" / "dashboard_state.json"
            if state_path.exists():
                state = load_json(state_path)
                success_checks.append(
                    {
                        "check": f"{organ['id']}_dashboard_state",
                        "status": state.get("status"),
                        "stale_status": state.get("stale_status"),
                        "result": "PASS" if state.get("stale_status") == "fresh" else "FAIL",
                    }
                )
            else:
                success_checks.append({"check": f"{organ['id']}_dashboard_state", "result": "FAIL", "reason": "missing"})
                blockers.append(f"missing_dashboard_state:{organ['id']}")
    else:
        success_checks.append({"check": "corridor_files_present", "result": "FAIL", "blockers": blockers})

    success_verdict = "PASS" if all(row.get("result") == "PASS" for row in success_checks) and not blockers else "FAIL"

    controlled_missing = required.copy()
    controlled_missing["officio_role_read_receipt"] = Path("ORGANS/OFFICIO_AGENTIS/REPORTS/V1/role_read_receipt_v1_DOES_NOT_EXIST.json")
    fail_ok, fail_blockers = evaluate_corridor({k: Path.cwd() / v for k, v in controlled_missing.items()})
    controlled_failure_verdict = "PASS" if (not fail_ok and any("officio_role_read_receipt" in item for item in fail_blockers)) else "FAIL"

    verdict = "PASS" if success_verdict == "PASS" and controlled_failure_verdict == "PASS" else "FAIL"
    report_path = LIVE_TASK_ROOT / "E2E_PROOF" / "live_e2e_proof_report_v1.json"
    write_json(
        report_path,
        {
            "task_id": TASK_ID,
            "stage_id": "STAGE-19",
            "generated_at_utc": now,
            "git_head": head,
            "success_path": {
                "required_files": {k: str(v) for k, v in required.items()},
                "checks": success_checks,
                "blockers": blockers,
                "verdict": success_verdict,
            },
            "controlled_failure_path": {
                "scenario": "missing_officio_role_read_receipt",
                "blockers": fail_blockers,
                "verdict": controlled_failure_verdict,
            },
            "verdict": verdict,
        },
    )

    write_stage_artifacts(
        19,
        source_hardening_report_path=stage_sources.get(19),
        live_outputs=[rel(report_path)],
        checks_run=["python scripts/foundational_organs_v1/run_foundational_organs_v1_e2e_proof.py"],
        verdict=verdict,
        warnings=[],
        blockers=[] if verdict == "PASS" else ["e2e_proof_failed"],
        self_repairs=[],
        retry_count=0,
        notes="live_e2e_proof",
    )
    print(verdict)
    print(rel(report_path))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(run())
