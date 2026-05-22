#!/usr/bin/env python3
"""Validate Sanctum NG truth shell artifacts and report status."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

TASK_ID = "TASK-20260522-NEWGEN-SANCTUM-TRUTH-SHELL-VM3-V0_1"
REQUIRED_PHASES = set(range(1, 11))
STATUS_ORDER = {"PASS": 0, "WARN": 1, "BLOCK": 2}


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[3]
    default_state = default_repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/sanctum_ng_state.generated.json"
    default_schema = default_repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/CONTRACTS/sanctum_ng_state.schema.json"
    default_report_dir = default_repo_root / "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260522-NEWGEN-SANCTUM-TRUTH-SHELL-VM3-V0_1"
    default_output = default_report_dir / "VALIDATOR_REPORT.json"

    parser = argparse.ArgumentParser(description="Validate Sanctum NG truth shell artifacts.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--state", type=Path, default=default_state)
    parser.add_argument("--schema", type=Path, default=default_schema)
    parser.add_argument("--report-dir", type=Path, default=default_report_dir)
    parser.add_argument("--output", type=Path, default=default_output)
    return parser.parse_args()


def add_check(
    checks: list[dict[str, str]],
    warnings: list[str],
    blockers: list[str],
    check_id: str,
    ok: bool,
    detail_ok: str,
    detail_fail: str,
    fail_level: str = "BLOCK",
) -> None:
    if ok:
        checks.append({"check_id": check_id, "status": "PASS", "details": detail_ok})
        return

    checks.append({"check_id": check_id, "status": fail_level, "details": detail_fail})
    if fail_level == "WARN":
        warnings.append(f"{check_id}:{detail_fail}")
    else:
        blockers.append(f"{check_id}:{detail_fail}")


def load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "missing"
    except json.JSONDecodeError as exc:
        return None, f"json_decode_error:{exc}"
    if not isinstance(value, dict):
        return None, "not_json_object"
    return value, None


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    state_path = args.state.resolve()
    schema_path = args.schema.resolve()
    report_dir = args.report_dir.resolve()
    output_path = args.output.resolve()

    checks: list[dict[str, str]] = []
    warnings: list[str] = []
    blockers: list[str] = []

    required_app_files = [
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/index.html",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/styles.css",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/app.js",
    ]

    required_report_files = [
        report_dir / "OWNER_REPORT_RU.md",
        report_dir / "FINAL_RECEIPT.json",
        report_dir / "OFFICIO_ROLE_ACK_OR_WARN.json",
        report_dir / "DOCTRINARIUM_LAW_ACK_OR_WARN.json",
        report_dir / "SUPER_SKEPTICISM_ACK.json",
        report_dir / "CONTEXT_WINDOW_USAGE_NOTE.md",
        report_dir / "NEXT_TASK_IMPROVEMENT_REPORT.md",
        report_dir / "NEXT_TASK_IMPROVEMENT_REPORT.json",
        report_dir / "KPD_SLICE.md",
        report_dir / "GATE_ACK.md",
    ]

    add_check(
        checks,
        warnings,
        blockers,
        "required_files_exist",
        state_path.exists() and schema_path.exists(),
        "state and schema files exist",
        "state or schema file missing",
    )

    schema_obj, schema_err = load_json(schema_path)
    add_check(
        checks,
        warnings,
        blockers,
        "schema_parse",
        schema_obj is not None,
        "schema parses as JSON object",
        f"schema parse failed ({schema_err})",
    )

    state_obj, state_err = load_json(state_path)
    add_check(
        checks,
        warnings,
        blockers,
        "state_parse",
        state_obj is not None,
        "state parses as JSON object",
        f"state parse failed ({state_err})",
    )

    phases: list[dict[str, Any]] = []
    if state_obj is not None:
        required_keys = {"schema_id", "task_id", "mode", "phases", "limitations"}
        has_required_keys = required_keys.issubset(state_obj.keys())
        add_check(
            checks,
            warnings,
            blockers,
            "minimum_shape",
            has_required_keys,
            "minimum required keys are present",
            "minimum required keys are missing",
        )

        phases_raw = state_obj.get("phases", [])
        if isinstance(phases_raw, list):
            phases = [p for p in phases_raw if isinstance(p, dict)]

        phase_numbers = {int(p.get("phase_no")) for p in phases if isinstance(p.get("phase_no"), int)}
        add_check(
            checks,
            warnings,
            blockers,
            "phase_coverage_1_10",
            REQUIRED_PHASES.issubset(phase_numbers),
            "all phases 1..10 are present",
            f"missing phases: {sorted(REQUIRED_PHASES - phase_numbers)}",
        )

        proved_without_evidence = []
        for phase in phases:
            if phase.get("status") == "PROVED":
                refs = phase.get("evidence_refs")
                if not isinstance(refs, list) or not any(str(ref).strip() for ref in refs):
                    proved_without_evidence.append(phase.get("phase_no"))
        add_check(
            checks,
            warnings,
            blockers,
            "no_proved_without_evidence",
            not proved_without_evidence,
            "all PROVED phases have evidence refs",
            f"PROVED without evidence refs: {proved_without_evidence}",
        )

        mode_ok = state_obj.get("mode") == "READ_ONLY_FOUNDATION"
        add_check(
            checks,
            warnings,
            blockers,
            "mode_read_only_foundation",
            mode_ok,
            "mode is READ_ONLY_FOUNDATION",
            "mode mismatch",
        )

        truth_flags = state_obj.get("truth_flags", {})
        flags_ok = (
            isinstance(truth_flags, dict)
            and truth_flags.get("production_ready") is False
            and truth_flags.get("live_backend") is False
            and truth_flags.get("autonomous_execution") is False
        )
        add_check(
            checks,
            warnings,
            blockers,
            "forbidden_production_claims_absent",
            flags_ok,
            "truth flags block production/live/autonomous claims",
            "truth flags violate forbidden claim policy",
        )

    add_check(
        checks,
        warnings,
        blockers,
        "app_files_exist",
        all(path.exists() for path in required_app_files),
        "app files exist",
        "one or more app files are missing",
    )

    add_check(
        checks,
        warnings,
        blockers,
        "report_files_exist",
        all(path.exists() for path in required_report_files),
        "required report files exist",
        "one or more required report files are missing",
    )

    add_check(
        checks,
        warnings,
        blockers,
        "schema_id_match",
        bool(schema_obj and schema_obj.get("title") == "SANCTUM_NG_STATE_V0_1"),
        "schema title matches SANCTUM_NG_STATE_V0_1",
        "schema title mismatch",
        fail_level="WARN",
    )

    verdict = "PASS"
    if blockers:
        verdict = "BLOCK"
    elif warnings:
        verdict = "WARN"

    report = {
        "schema_version": "0.1",
        "task_id": TASK_ID,
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "verdict": verdict,
        "checks": checks,
        "warnings": warnings,
        "blockers": blockers,
        "state_path": state_path.relative_to(repo_root).as_posix() if state_path.exists() else str(state_path),
        "schema_path": schema_path.relative_to(repo_root).as_posix() if schema_path.exists() else str(schema_path),
        "report_dir": report_dir.relative_to(repo_root).as_posix() if report_dir.exists() else str(report_dir),
        "no_fake_green_note": "PASS/WARN here validates bounded foundation truth shell only; no production or autonomy claim is made.",
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"validator_verdict={verdict}")
    print(f"validator_report={output_path.relative_to(repo_root).as_posix()}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
