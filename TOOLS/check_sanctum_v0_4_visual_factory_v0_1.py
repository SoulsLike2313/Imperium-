#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

TASK_ID = "TASK-20260513-STEP7_1F-STEP7_2-BUNDLE-ROUTE-ASSET-REGISTRATION-SANCTUM-V0_4"

V04_REL = "SANCTUM/sanctum_v0_4_visual_factory_qt.py"
V029_REL = "SANCTUM/sanctum_v0_29_qt.py"
DOC_REL = "DOCS/SANCTUM_V0_4_VISUAL_FACTORY_PROTOTYPE.md"
REPORT_REL = "CURRENT_STATE/SANCTUM_V0_4_VISUAL_PROTOTYPE_REPORT_20260513.md"
ROUTE_REG_REL = "REGISTRY/BUNDLE_ROUTE_REGISTRY.json"
MANIFEST_REL = "ASSETS/ASSET_MANIFEST.json"

EXPECTED_CANONICAL_VM2 = "/home/vboxuser2/IMPERIUM_WORK/VM2_BUNDLES/"


def add_unique(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def read_json_obj(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.exists():
        return None, f"missing_file:{path.as_posix()}"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return None, f"invalid_json:{path.as_posix()}:{type(exc).__name__}"
    if not isinstance(payload, dict):
        return None, f"invalid_json_type:{path.as_posix()}"
    return payload, None


def run_git(repo_root: Path, args: list[str]) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as exc:  # noqa: BLE001
        return False, f"git_exception:{type(exc).__name__}:{exc}"
    if result.returncode != 0:
        return False, (result.stderr or result.stdout).strip()
    return True, result.stdout.strip()


def build_report(repo_root: Path) -> dict[str, Any]:
    passes: list[str] = []
    warnings: list[str] = []
    blocked: list[str] = []

    for rel in [V04_REL, V029_REL, DOC_REL, REPORT_REL, ROUTE_REG_REL, MANIFEST_REL]:
        path = repo_root / rel
        if path.exists():
            passes.append(f"file_exists:{rel}")
        else:
            add_unique(blocked, f"missing_required_file:{rel}")

    route_reg, route_err = read_json_obj(repo_root / ROUTE_REG_REL)
    if route_err:
        add_unique(blocked, route_err)
    elif route_reg is not None:
        canonical = route_reg.get("canonical_vm2_outbox")
        if canonical == EXPECTED_CANONICAL_VM2:
            passes.append("route_registry_canonical_vm2_outbox_ok")
        else:
            add_unique(blocked, f"route_registry_canonical_vm2_outbox_mismatch:{canonical}")

    manifest, manifest_err = read_json_obj(repo_root / MANIFEST_REL)
    if manifest_err:
        add_unique(blocked, manifest_err)
    elif manifest is not None:
        if manifest.get("owner_confirmation_required") is True:
            passes.append("asset_manifest_owner_confirmation_required_true")
        else:
            add_unique(blocked, "asset_manifest_owner_confirmation_required_must_be_true")

    v04_path = repo_root / V04_REL
    if v04_path.exists():
        source = v04_path.read_text(encoding="utf-8", errors="replace")
        if "BUNDLE_ROUTE_REGISTRY" in source:
            passes.append("v0_4_references_bundle_route_registry")
        else:
            add_unique(blocked, "v0_4_missing_bundle_route_registry_reference")

        if "experimental" in source.lower() or "Prototype" in source:
            passes.append("v0_4_marked_as_prototype")
        else:
            add_unique(warnings, "v0_4_prototype_label_not_explicit")

        try:
            py_compile.compile(str(v04_path), doraise=True)
            passes.append("py_compile_v0_4_pass")
        except Exception as exc:  # noqa: BLE001
            add_unique(blocked, f"py_compile_v0_4_failed:{type(exc).__name__}:{exc}")

    ok_status, status_out = run_git(repo_root, ["status", "--short", "--", V029_REL])
    if not ok_status:
        add_unique(blocked, f"git_status_failed_for_v0_29:{status_out}")
    else:
        if status_out.strip().startswith("D"):
            add_unique(blocked, "v0_29_deleted_forbidden")
        elif status_out.strip().startswith(" M") or status_out.strip().startswith("M"):
            add_unique(warnings, "v0_29_modified_detected_check_for_baseline_preservation")
        else:
            passes.append("v0_29_present_and_not_deleted")

    truth_path = repo_root / "CURRENT_STATE/ARC5_PREFIRE_CURRENT_TRUTH_20260513.json"
    if truth_path.exists():
        truth, err = read_json_obj(truth_path)
        if err:
            add_unique(warnings, f"current_truth_invalid_optional:{err}")
        elif truth is not None:
            if truth.get("act5_execution_ready") is False:
                passes.append("current_truth_act5_execution_ready_false")
            else:
                add_unique(blocked, "current_truth_act5_execution_ready_must_be_false")
            if truth.get("ready_for_agent_status") is False:
                passes.append("current_truth_ready_for_agent_false")
            else:
                add_unique(blocked, "current_truth_ready_for_agent_must_be_false")

    verdict = "PASS" if not blocked else "BLOCKED"
    return {
        "task_id": TASK_ID,
        "repo_root": str(repo_root),
        "verdict": verdict,
        "passes": passes,
        "warnings": warnings,
        "blocked": blocked,
    }


def print_human(report: dict[str, Any]) -> None:
    print("=== PASS ===")
    for item in report["passes"] or ["(none)"]:
        print(f"- {item}")

    print("\n=== WARN ===")
    if report["warnings"]:
        for item in report["warnings"]:
            print(f"- {item}")
    else:
        print("- (none)")

    print("\n=== BLOCKED ===")
    if report["blocked"]:
        for item in report["blocked"]:
            print(f"- {item}")
    else:
        print("- (none)")

    print("\n=== SUMMARY ===")
    print(f"task_id: {report['task_id']}")
    print(f"verdict: {report['verdict']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Sanctum v0.4 visual factory prototype")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--json", action="store_true", help="Print JSON report")
    args = parser.parse_args()

    report = build_report(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human(report)

    return 0 if report["verdict"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
