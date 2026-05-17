#!/usr/bin/env python3
"""Checker for Second Brain Neural Base V0.4."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run(cmd: list[str], cwd: Path) -> dict:
    proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, check=False)
    return {
        "command": " ".join(cmd),
        "exit_code": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def parse_json(path: Path) -> tuple[bool, str]:
    try:
        json.loads(path.read_text(encoding="utf-8-sig"))
        return True, "ok"
    except Exception as exc:
        return False, str(exc)


def add(checks: list[dict], fails: list[str], warns: list[str], name: str, passed: bool, detail: str, level: str = "FAIL") -> None:
    checks.append({"name": name, "passed": passed, "detail": detail, "level": level})
    if passed:
        return
    if level == "WARN":
        warns.append(f"{name}: {detail}")
    else:
        fails.append(f"{name}: {detail}")


def main() -> int:
    script_path = Path(__file__).resolve()
    base_dir = script_path.parents[1]
    repo_root = script_path.parents[4]
    tv_root = script_path.parents[3]
    reports_dir = base_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    required_files = [
      "README.md",
      "ARCHITECTURE.md",
      "VISUAL_DIRECTION.md",
      "FEATURE_MODULE_CONTRACT.md",
      "BACKEND_TRUTH_CONTRACT.md",
      "ACTION_SAFETY_CONTRACT.md",
      "ROADMAP_TO_FULL_NEURAL_OPERATOR.md",
      "registry/neural_feature_registry.json",
      "registry/neural_visual_tokens.json",
      "registry/neural_truth_matrix.json",
      "registry/neural_action_registry.json",
      "features/second_brain_runtime.feature.json",
      "features/delta_window.feature.json",
      "features/agent_exchange.feature.json",
      "features/testing_field.feature.json",
      "app/neural_base_v0_4.html",
      "app/neural_base_v0_4.css",
      "app/neural_base_v0_4.js",
      "tools/build_neural_base_snapshot_v0_4.py",
      "tools/check_neural_base_v0_4.py"
    ]

    checks: list[dict] = []
    failures: list[str] = []
    warnings: list[str] = []

    # Required files
    for rel in required_files:
        p = base_dir / rel
        add(checks, failures, warnings, f"exists:{rel}", p.exists(), "present" if p.exists() else "missing")
        if p.exists() and p.is_file():
            add(checks, failures, warnings, f"nonempty:{rel}", p.stat().st_size > 20, f"size={p.stat().st_size}")

    # JSON parse
    json_files = [
        base_dir / "registry/neural_feature_registry.json",
        base_dir / "registry/neural_visual_tokens.json",
        base_dir / "registry/neural_truth_matrix.json",
        base_dir / "registry/neural_action_registry.json",
        base_dir / "features/second_brain_runtime.feature.json",
        base_dir / "features/delta_window.feature.json",
        base_dir / "features/agent_exchange.feature.json",
        base_dir / "features/testing_field.feature.json",
    ]
    for p in json_files:
        ok, detail = parse_json(p)
        add(checks, failures, warnings, f"json:{p.name}", ok, detail)

    feature_registry = json.loads((base_dir / "registry/neural_feature_registry.json").read_text(encoding="utf-8-sig"))
    feature_ids = {f.get("id") for f in feature_registry.get("features", [])}
    for needed in {"second_brain_runtime", "delta_window", "agent_exchange", "testing_field"}:
        add(checks, failures, warnings, f"feature_id:{needed}", needed in feature_ids, "present" if needed in feature_ids else "missing")

    truth = json.loads((base_dir / "registry/neural_truth_matrix.json").read_text(encoding="utf-8-sig"))
    for idx, mapping in enumerate(truth.get("mappings", []), start=1):
        desc_ok = bool(mapping.get("description"))
        src_ok = isinstance(mapping.get("source_patterns"), list) and len(mapping.get("source_patterns")) > 0
        add(checks, failures, warnings, f"truth_desc:{idx}", desc_ok, "has description" if desc_ok else "missing description")
        add(checks, failures, warnings, f"truth_sources:{idx}", src_ok, "has source patterns" if src_ok else "missing source patterns")

    actions = json.loads((base_dir / "registry/neural_action_registry.json").read_text(encoding="utf-8-sig")).get("actions", [])
    for action in actions:
        action_id = action.get("action_id", "unknown_action")
        a_type = action.get("type")
        status = str(action.get("status", ""))
        command = str(action.get("command", ""))
        if a_type == "MUTATING_DISABLED":
            add(checks, failures, warnings, f"mutating_disabled:{action_id}", command == "", "disabled command empty" if command == "" else "disabled action has command")
            add(checks, failures, warnings, f"mutating_status:{action_id}", status.startswith("DISABLED"), "status starts with DISABLED" if status.startswith("DISABLED") else f"status={status}")
        else:
            add(checks, failures, warnings, f"safe_action_cmd:{action_id}", command != "", "command exists" if command != "" else "enabled action missing command")

    # Build snapshot
    build_res = run([sys.executable, str(base_dir / "tools/build_neural_base_snapshot_v0_4.py")], base_dir)
    add(checks, failures, warnings, "snapshot_build_exit", build_res["exit_code"] == 0, f"exit={build_res['exit_code']} stderr={build_res['stderr']}")
    snap_path = base_dir / "reports/neural_base_snapshot_v0_4.json"
    add(checks, failures, warnings, "snapshot_exists", snap_path.exists(), "present" if snap_path.exists() else "missing")
    if snap_path.exists():
        ok, detail = parse_json(snap_path)
        add(checks, failures, warnings, "snapshot_parse", ok, detail)

    # Scope safety by git status
    status_res = run(["git", "status", "--short"], repo_root)
    changed = [line for line in status_res["stdout"].splitlines() if line.strip()]
    outside = []
    for line in changed:
        parts = line.strip().split(maxsplit=1)
        path = parts[1] if len(parts) > 1 else ""
        normalized = path.replace("\\", "/")
        if normalized and not normalized.startswith("IMPERIUM_TEST_VERSION/"):
            outside.append(line)
    add(checks, failures, warnings, "scope_only_imperium_test_version", len(outside) == 0, "ok" if len(outside) == 0 else f"outside_changes={outside}")

    # Canonical Delta Window path must exist in TESTING_FIELD
    active_delta = tv_root / "TESTING_FIELD" / "DELTA_WINDOW"
    add(
        checks,
        failures,
        warnings,
        "delta_window_active_path_exists",
        active_delta.exists(),
        "TESTING_FIELD/DELTA_WINDOW present" if active_delta.exists() else "TESTING_FIELD/DELTA_WINDOW missing",
    )

    overall = "PASS"
    if failures:
        overall = "FAIL"
    elif warnings:
        overall = "WARN"

    report = {
        "checker": "check_neural_base_v0_4.py",
        "timestamp_utc": utc_now(),
        "scope_path": str(base_dir),
        "overall": overall,
        "checks_total": len(checks),
        "failures_count": len(failures),
        "warnings_count": len(warnings),
        "checks": checks,
        "failures": failures,
        "warnings": warnings,
        "build_snapshot_result": build_res,
    }

    report_path = base_dir / "reports/neural_base_check_report_v0_4.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("=== Neural Base V0.4 Checker ===")
    print(f"overall: {overall}")
    print(f"checks: {len(checks)}")
    print(f"failures: {len(failures)}")
    print(f"warnings: {len(warnings)}")
    print(f"report: {report_path}")

    return 0 if overall != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
