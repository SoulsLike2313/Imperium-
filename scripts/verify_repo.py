#!/usr/bin/env python3
"""Run minimal IMPERIUM verification spine gates and emit runtime report."""

from __future__ import annotations

import json
from pathlib import Path
import py_compile
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
SCRIPT_ROOT = REPO_ROOT / "scripts"
for path in (SRC_ROOT, SCRIPT_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from imperium.config import load_config
from imperium.receipts.model import Verdict, create_basic_receipt, utc_timestamp

from no_pycache_tracked import run_gate as run_no_pycache_tracked
from no_raw_subprocess import run_gate as run_no_raw_subprocess
from public_private_boundary_scan import run_gate as run_public_private_boundary_scan
from receipt_portability_check import run_gate as run_receipt_portability_check


RUNTIME_SUBDIR = Path(".imperium_runtime/verification_spine")
REPORT_FILE = "VERIFY_REPO_REPORT.json"
VERDICT_FILE = "VERIFY_REPO_VERDICT.md"
RECEIPT_FILE = "VERIFY_REPO_RECEIPT.json"

PY_COMPILE_TARGETS = [
    Path("src/imperium/config.py"),
    Path("src/imperium/security/path_policy.py"),
    Path("src/imperium/security/command_gateway.py"),
    Path("src/imperium/receipts/model.py"),
    Path("src/imperium/receipts/validator.py"),
    Path("scripts/verify_repo.py"),
    Path("scripts/no_pycache_tracked.py"),
    Path("scripts/no_raw_subprocess.py"),
    Path("scripts/public_private_boundary_scan.py"),
    Path("scripts/receipt_portability_check.py"),
]



def _gate_py_compile(repo_root: Path) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    errors: list[str] = []

    for rel_path in PY_COMPILE_TARGETS:
        abs_path = repo_root / rel_path
        if not abs_path.exists():
            errors.append(f"Missing compile target: {rel_path.as_posix()}")
            continue
        try:
            py_compile.compile(str(abs_path), doraise=True)
        except py_compile.PyCompileError as exc:
            blockers.append(f"{rel_path.as_posix()}: {exc.msg}")
        except Exception as exc:
            blockers.append(f"{rel_path.as_posix()}: {exc}")

    verdict = Verdict.PASS.value
    if blockers or errors:
        verdict = Verdict.FAIL.value

    return {
        "schema_version": "imperium.verification_gate.v0_1",
        "gate_id": "python_py_compile",
        "timestamp_utc": utc_timestamp(),
        "verdict": verdict,
        "blockers": blockers,
        "warnings": warnings,
        "errors": errors,
        "metrics": {
            "targets": len(PY_COMPILE_TARGETS),
            "blockers": len(blockers),
            "errors": len(errors),
        },
    }



def _count_warnings(gate: dict[str, Any]) -> int:
    metrics = gate.get("metrics", {})
    if isinstance(metrics, dict) and isinstance(metrics.get("warnings"), int):
        return metrics["warnings"]
    warnings = gate.get("warnings", [])
    return len(warnings) if isinstance(warnings, list) else 0



def _count_blockers(gate: dict[str, Any]) -> int:
    metrics = gate.get("metrics", {})
    if isinstance(metrics, dict):
        for key in ("blockers_new_spine", "pycache_findings", "blockers"):
            if isinstance(metrics.get(key), int):
                return metrics[key]
    blockers = gate.get("blockers", [])
    return len(blockers) if isinstance(blockers, list) else 0



def _overall_verdict(gates: list[dict[str, Any]]) -> str:
    if any(gate.get("verdict") in {Verdict.FAIL.value, Verdict.BLOCKED.value} for gate in gates):
        return Verdict.FAIL.value
    if any(gate.get("verdict") == Verdict.PASS_WITH_WARNINGS.value for gate in gates):
        return Verdict.PASS_WITH_WARNINGS.value
    return Verdict.PASS.value



def _write_verdict_md(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# VERIFY REPO VERDICT",
        "",
        f"- schema_version: {report['schema_version']}",
        f"- timestamp_utc: {report['timestamp_utc']}",
        f"- repo_root: {report['repo_root']}",
        f"- overall_verdict: {report['overall_verdict']}",
        f"- gates: {report['counts']['gates']}",
        f"- blockers: {report['counts']['blockers']}",
        f"- warnings: {report['counts']['warnings']}",
        "",
        "## Gate Verdicts",
    ]
    for gate in report["gates"]:
        lines.append(f"- {gate['gate_id']}: {gate['verdict']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")



def run_verification(root: Path | None = None) -> dict[str, Any]:
    config = load_config(explicit_root=root, mode="dev")
    repo_root = config.root_path

    gates = [
        run_no_pycache_tracked(repo_root),
        run_no_raw_subprocess(repo_root),
        run_public_private_boundary_scan(repo_root),
        run_receipt_portability_check(repo_root),
        _gate_py_compile(repo_root),
    ]

    blockers = sum(_count_blockers(gate) for gate in gates)
    warnings = sum(_count_warnings(gate) for gate in gates)
    overall = _overall_verdict(gates)

    report = {
        "schema_version": "imperium.verification_report.v0_1",
        "timestamp_utc": utc_timestamp(),
        "repo_root": str(repo_root),
        "overall_verdict": overall,
        "gates": gates,
        "counts": {
            "gates": len(gates),
            "blockers": blockers,
            "warnings": warnings,
        },
    }

    runtime_dir = repo_root / RUNTIME_SUBDIR
    runtime_dir.mkdir(parents=True, exist_ok=True)

    report_path = runtime_dir / REPORT_FILE
    verdict_path = runtime_dir / VERDICT_FILE
    receipt_path = runtime_dir / RECEIPT_FILE

    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    _write_verdict_md(verdict_path, report)

    receipt = create_basic_receipt(
        "imperium.verify_repo",
        overall,
        schema_version="imperium.verify_repo_receipt.v0_1",
        warnings=[f"warnings={warnings}"] if warnings else [],
        errors=[],
        report_path=str(report_path),
        verdict_path=str(verdict_path),
        counts=report["counts"],
    )
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    report["artifacts"] = {
        "report": str(report_path),
        "verdict": str(verdict_path),
        "receipt": str(receipt_path),
    }
    return report



def main() -> int:
    report = run_verification()
    summary = {
        "schema_version": report["schema_version"],
        "timestamp_utc": report["timestamp_utc"],
        "repo_root": report["repo_root"],
        "overall_verdict": report["overall_verdict"],
        "counts": report["counts"],
        "gate_verdicts": [
            {"gate_id": gate["gate_id"], "verdict": gate["verdict"]}
            for gate in report["gates"]
        ],
        "artifacts": report.get("artifacts", {}),
    }
    print(json.dumps(summary, indent=2))
    return 1 if report["overall_verdict"] == Verdict.FAIL.value else 0


if __name__ == "__main__":
    raise SystemExit(main())
