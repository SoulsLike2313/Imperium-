#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

TASK_ID = "TASK-20260513-VISUAL-FACTORY-MINIMUM-V0_1"

RUNTIME_REL = ".imperium_runtime/visual_factory_minimum_check"
REPORT_NAME = "VISUAL_FACTORY_MINIMUM_CHECK_REPORT.json"
VERDICT_NAME = "VISUAL_FACTORY_MINIMUM_CHECK_VERDICT.md"
RECEIPT_NAME = "VISUAL_FACTORY_MINIMUM_CHECK_RECEIPT.json"

REQUIRED_DIRS = [
    "ASSETS",
    "ASSETS/DATA",
    "ASSETS/REFERENCES/ACCEPTED",
    "ASSETS/REFERENCES/REJECTED",
    "ASSETS/REFERENCES/CANDIDATE",
    "ASSETS/REFERENCES/MATERIALS",
    "ASSETS/REFERENCES/LAYOUT",
    "ASSETS/REFERENCES/DENSITY",
    "ASSETS/REFERENCES/GLOW",
    "ASSETS/REFERENCES/CARDS_PANELS",
    "ASSETS/REFERENCES/ORBIT_CORE",
    "ASSETS/REFERENCES/NAVIGATION",
    "ASSETS/REFERENCES/ORGAN_DASHBOARD",
    "ASSETS/REFERENCES/SANCTUM_CORE",
    "ASSETS/INBOX_OWNER_VISUAL_SORTING",
    "ASSETS/INBOX_OWNER_VISUAL_SORTING/RAW_SCREENSHOTS",
    "ASSETS/INBOX_OWNER_VISUAL_SORTING/ANNOTATED_SCREENSHOTS",
    "ASSETS/INBOX_OWNER_VISUAL_SORTING/TEXT_NOTES",
    "ASSETS/INBOX_OWNER_VISUAL_SORTING/SERVITOR_SORTING_OUTPUT",
    "ASSETS/INBOX_OWNER_VISUAL_SORTING/SERVITOR_SORTING_OUTPUT/INTERPRETATION_CARDS",
    "SANCTUM/DESIGN_SYSTEM",
    "SANCTUM/UI_LAB",
    "DOCS",
]

REQUIRED_FILES = [
    "ASSETS/README_ASSETS.md",
    "ASSETS/OWNER_VISUAL_PREFERENCES.md",
    "ASSETS/ASSET_MANIFEST.json",
    "ASSETS/DATA/.gitkeep",
    "ASSETS/INBOX_OWNER_VISUAL_SORTING/README_OWNER_DROPBOX.md",
    "ASSETS/INBOX_OWNER_VISUAL_SORTING/OWNER_DROPBOX_PROTOCOL.md",
    "ASSETS/INBOX_OWNER_VISUAL_SORTING/RAW_SCREENSHOTS/.gitkeep",
    "ASSETS/INBOX_OWNER_VISUAL_SORTING/ANNOTATED_SCREENSHOTS/.gitkeep",
    "ASSETS/INBOX_OWNER_VISUAL_SORTING/TEXT_NOTES/OWNER_SORTING_NOTES.md",
    "ASSETS/INBOX_OWNER_VISUAL_SORTING/SERVITOR_SORTING_OUTPUT/README_SERVITOR_SORTING_OUTPUT.md",
    "ASSETS/INBOX_OWNER_VISUAL_SORTING/SERVITOR_SORTING_OUTPUT/SORTING_REPORT_TEMPLATE.md",
    "ASSETS/INBOX_OWNER_VISUAL_SORTING/SERVITOR_SORTING_OUTPUT/ASSET_MANIFEST_PATCH_TEMPLATE.json",
    "ASSETS/INBOX_OWNER_VISUAL_SORTING/SERVITOR_SORTING_OUTPUT/VISUAL_RULES_PATCH_TEMPLATE.md",
    "ASSETS/INBOX_OWNER_VISUAL_SORTING/SERVITOR_SORTING_OUTPUT/INTERPRETATION_CARDS/.gitkeep",
    "ASSETS/INBOX_OWNER_VISUAL_SORTING/SERVITOR_SORTING_OUTPUT/INTERPRETATION_CARDS/INTERPRETATION_CARD_TEMPLATE.md",
    "SANCTUM/DESIGN_SYSTEM/README_DESIGN_SYSTEM.md",
    "SANCTUM/DESIGN_SYSTEM/DESIGN_TOKENS_V0_1.json",
    "SANCTUM/DESIGN_SYSTEM/VISUAL_BUDGET_V0_1.json",
    "SANCTUM/DESIGN_SYSTEM/SANCTUM_VISUAL_RULES_V0_1.md",
    "SANCTUM/DESIGN_SYSTEM/COMPONENT_STYLE_GUIDE_V0_1.md",
    "SANCTUM/UI_LAB/README_UI_LAB.md",
    "SANCTUM/UI_LAB/UI_EXPERIMENT_LEDGER_V0_1.json",
    "SANCTUM/UI_LAB/GOLDEN_SCREENSHOT_MANIFEST_V0_1.json",
    "DOCS/VISUAL_FACTORY_MINIMUM_V0_1.md",
    "SANCTUM/sanctum_v0_29_qt.py",
]

DOCTRINE_LINES = [
    "Raw screenshot is evidence, not canon.",
    "Servitor interpretation is proposal, not canon.",
    "Owner confirmation turns interpretation into accepted visual rule.",
]

JSON_FILES = [
    "ASSETS/ASSET_MANIFEST.json",
    "ASSETS/INBOX_OWNER_VISUAL_SORTING/SERVITOR_SORTING_OUTPUT/ASSET_MANIFEST_PATCH_TEMPLATE.json",
    "SANCTUM/DESIGN_SYSTEM/DESIGN_TOKENS_V0_1.json",
    "SANCTUM/DESIGN_SYSTEM/VISUAL_BUDGET_V0_1.json",
    "SANCTUM/UI_LAB/UI_EXPERIMENT_LEDGER_V0_1.json",
    "SANCTUM/UI_LAB/GOLDEN_SCREENSHOT_MANIFEST_V0_1.json",
]

OPTIONAL_REGISTRY_FILE = "REGISTRY/SCRIPT_REGISTRY.json"
CHECKER_REL = "TOOLS/check_visual_factory_minimum_v0_1.py"


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def add_unique(items: list[str], message: str) -> None:
    if message not in items:
        items.append(message)


def run_git(repo_root: Path, args: list[str]) -> tuple[bool, str]:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as exc:  # noqa: BLE001
        return False, f"git_exception:{type(exc).__name__}:{exc}"

    if completed.returncode != 0:
        return False, (completed.stderr or completed.stdout).strip()
    return True, completed.stdout.strip()


def read_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return None, f"invalid_json:{path.as_posix()}:{type(exc).__name__}"
    if not isinstance(raw, dict):
        return None, f"invalid_json_type:{path.as_posix()}:expected_object"
    return raw, None


def write_runtime_artifacts(repo_root: Path, report: dict[str, Any]) -> dict[str, str]:
    runtime_dir = repo_root / RUNTIME_REL
    runtime_dir.mkdir(parents=True, exist_ok=True)

    report_path = runtime_dir / REPORT_NAME
    verdict_path = runtime_dir / VERDICT_NAME
    receipt_path = runtime_dir / RECEIPT_NAME

    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines: list[str] = [
        "# Visual Factory Minimum Check v0.1",
        "",
        f"- task_id: {TASK_ID}",
        f"- generated_at_utc: {report.get('generated_at_utc')}",
        f"- verdict: {report.get('verdict')}",
        f"- pass_count: {len(report.get('passes', []))}",
        f"- warn_count: {len(report.get('warnings', []))}",
        f"- blocked_count: {len(report.get('blocked', []))}",
    ]

    if report.get("blocked"):
        lines.extend(["", "## BLOCKED"])
        lines.extend(f"- {item}" for item in report["blocked"])
    if report.get("warnings"):
        lines.extend(["", "## WARN"])
        lines.extend(f"- {item}" for item in report["warnings"])
    if report.get("passes"):
        lines.extend(["", "## PASS"])
        lines.extend(f"- {item}" for item in report["passes"])

    verdict_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    receipt = {
        "schema_version": "imperium.visual_factory_minimum_check_receipt.v0_1",
        "task_id": TASK_ID,
        "generated_at_utc": now_utc(),
        "verdict": report.get("verdict"),
        "report_path": str(report_path),
        "verdict_path": str(verdict_path),
    }
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {
        "report_path": str(report_path),
        "verdict_path": str(verdict_path),
        "receipt_path": str(receipt_path),
    }


def build_report(repo_root: Path) -> dict[str, Any]:
    passes: list[str] = []
    warnings: list[str] = []
    blocked: list[str] = []

    for rel in REQUIRED_DIRS:
        target = repo_root / rel
        if target.is_dir():
            passes.append(f"dir_exists:{rel}")
        else:
            add_unique(blocked, f"missing_required_dir:{rel}")

    for rel in REQUIRED_FILES:
        target = repo_root / rel
        if target.exists():
            passes.append(f"file_exists:{rel}")
        else:
            add_unique(blocked, f"missing_required_file:{rel}")

    for rel in JSON_FILES:
        target = repo_root / rel
        if not target.exists():
            add_unique(blocked, f"missing_json_file:{rel}")
            continue
        parsed, err = read_json(target)
        if err:
            add_unique(blocked, err)
            continue
        passes.append(f"json_valid:{rel}")

        if rel.endswith("ASSET_MANIFEST.json"):
            status = parsed.get("status")
            if status == "structure_seed_only":
                passes.append("asset_manifest_status_structure_seed_only")
            elif status == "proposed_registration_pending_owner_confirmation":
                passes.append("asset_manifest_status_step7_2_proposed_registration_ok")
                add_unique(
                    warnings,
                    "asset_manifest_status_is_step7_2_proposal_mode_not_structure_seed_only",
                )
            else:
                add_unique(
                    blocked,
                    "asset_manifest_status_must_be_structure_seed_only_or_step7_2_proposal_mode",
                )

            if parsed.get("owner_confirmation_required") is True:
                passes.append("asset_manifest_owner_confirmation_required_true")
            else:
                add_unique(blocked, "asset_manifest_owner_confirmation_required_must_be_true")

            if parsed.get("rule") == "raw assets are evidence, not canon":
                passes.append("asset_manifest_rule_raw_assets_not_canon_ok")
            else:
                add_unique(blocked, "asset_manifest_rule_mismatch_raw_assets_not_canon")

    protocol_path = repo_root / "ASSETS/INBOX_OWNER_VISUAL_SORTING/OWNER_DROPBOX_PROTOCOL.md"
    if protocol_path.exists():
        protocol_text = protocol_path.read_text(encoding="utf-8")
        for line in DOCTRINE_LINES:
            if line in protocol_text:
                passes.append(f"doctrine_line_present:{line}")
            else:
                add_unique(blocked, f"missing_doctrine_line:{line}")

    registry_path = repo_root / OPTIONAL_REGISTRY_FILE
    if registry_path.exists():
        parsed, err = read_json(registry_path)
        if err:
            add_unique(warnings, f"script_registry_invalid_skip_optional_check:{err}")
        else:
            scripts = parsed.get("scripts")
            if isinstance(scripts, list):
                checker_found = any(
                    isinstance(item, dict) and item.get("path") == CHECKER_REL for item in scripts
                )
                if checker_found:
                    passes.append("script_registry_contains_visual_factory_checker")
                else:
                    add_unique(
                        warnings,
                        "script_registry_missing_visual_factory_checker_entry_optional",
                    )
            else:
                add_unique(warnings, "script_registry_scripts_field_invalid_optional")
    else:
        add_unique(warnings, "script_registry_not_found_optional")

    ok_diff, diff_out = run_git(repo_root, ["diff", "--name-only"])
    if not ok_diff:
        add_unique(blocked, f"git_diff_failed:{diff_out}")
    else:
        changed = {line.strip() for line in diff_out.splitlines() if line.strip()}
        if "SANCTUM/sanctum_v0_29_qt.py" in changed:
            add_unique(blocked, "sanctum_runtime_file_modified_forbidden")
        else:
            passes.append("sanctum_runtime_file_not_modified")

    ok_status, status_out = run_git(repo_root, ["status", "--short"])
    if ok_status:
        passes.append("git_status_short_collected")
        if "SANCTUM/sanctum_v0_29_qt.py" in status_out:
            add_unique(blocked, "sanctum_runtime_file_present_in_git_status")
    else:
        add_unique(blocked, f"git_status_failed:{status_out}")

    ok_head, head_out = run_git(repo_root, ["rev-parse", "HEAD"])
    if ok_head:
        passes.append(f"git_head:{head_out}")
    else:
        add_unique(blocked, f"git_head_failed:{head_out}")

    verdict = "PASS" if not blocked else "BLOCKED"
    return {
        "schema_version": "imperium.visual_factory_minimum_check.v0_1",
        "task_id": TASK_ID,
        "generated_at_utc": now_utc(),
        "repo_root": str(repo_root),
        "verdict": verdict,
        "passes": passes,
        "warnings": warnings,
        "blocked": blocked,
    }


def print_human(report: dict[str, Any], artifacts: dict[str, str]) -> None:
    print("=== PASS ===")
    if report["passes"]:
        for item in report["passes"]:
            print(f"- {item}")
    else:
        print("- (none)")

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
    print(f"verdict: {report['verdict']}")
    print(f"task_id: {TASK_ID}")
    print(f"report_path: {artifacts['report_path']}")
    print(f"verdict_path: {artifacts['verdict_path']}")
    print(f"receipt_path: {artifacts['receipt_path']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Step 7.1 Visual Factory Minimum structure seed.")
    parser.add_argument("--repo-root", default=".", help="Repository root (default: current directory)")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout")
    parser.add_argument("--human", action="store_true", help="Print human-readable PASS/WARN/BLOCKED sections")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    report = build_report(repo_root)
    artifacts = write_runtime_artifacts(repo_root, report)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.human or not args.json:
        print_human(report, artifacts)

    return 0 if report["verdict"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
