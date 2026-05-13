#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

TASK_ID = "TASK-20260513-SANCTUM-DASHBOARD-V0_5-WORKING-PROTOTYPE"

REQUIRED_FILES = [
    "SANCTUM/UI_LAB/V0_5_DASHBOARD_PROTOTYPE/index.html",
    "SANCTUM/UI_LAB/V0_5_DASHBOARD_PROTOTYPE/styles.css",
    "SANCTUM/UI_LAB/V0_5_DASHBOARD_PROTOTYPE/dashboard.js",
    "SANCTUM/UI_LAB/V0_5_DASHBOARD_PROTOTYPE/dashboard_data.json",
    "SANCTUM/UI_LAB/V0_5_DASHBOARD_PROTOTYPE/README.md",
    "SANCTUM/DASHBOARD/DASHBOARD_INDEX_V0_5.json",
    "SANCTUM/DASHBOARD/README_DASHBOARD_V0_5.md",
    "DOCS/SANCTUM_DASHBOARD_V0_5_WORKING_PROTOTYPE.md",
    "DOCS/SANCTUM_V0_4_INSPECTION_VERDICT_20260513.md",
    "CURRENT_STATE/SANCTUM_DASHBOARD_V0_5_REPORT_20260513.md",
    "TOOLS/build_sanctum_dashboard_v0_5_data.py",
    "TOOLS/check_sanctum_dashboard_v0_5.py",
]

REQUIRED_ORGANS = {
    "CUSTODES",
    "INQUISITION",
    "MECHANICUS",
    "ADMINISTRATUM",
    "ASTRONOMICON",
    "STRATEGIUM",
    "OFFICIO_AGENTIS",
    "THRONE",
    "SCHOLA_IMPERIALIS",
    "DOCTRINARIUM",
}

FIRST_FOUR = {
    "DOCTRINARIUM",
    "ADMINISTRATUM",
    "ASTRONOMICON",
    "OFFICIO_AGENTIS",
}

REQUIRED_BUTTON_IDS = [
    "btn-toggle-orbit-animation",
    "btn-show-all-organs",
    "btn-show-guide-organs",
    "btn-show-warnings",
    "btn-filter-assets-accepted",
    "btn-filter-assets-candidate",
    "btn-filter-assets-rejected",
    "btn-clear-asset-filters",
    "btn-show-route-policy",
    "btn-show-action-registry",
    "btn-show-reports",
    "btn-compact-mode-toggle",
    "btn-clear-console",
]

FORBIDDEN_TEXT_PATTERNS = [
    "TODO" + " button",
    "placeholder" + " button",
    "fake" + " green",
    "READY_FOR_AGENT" + " true",
]


def add_unique(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


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


def read_json(path: Path) -> tuple[Any | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:  # noqa: BLE001
        return None, f"invalid_json:{path.as_posix()}:{type(exc).__name__}"


def file_text(path: Path) -> str:
    try:
        data = path.read_bytes()
    except Exception:
        return ""
    if b"\x00" in data:
        return ""
    return data.decode("utf-8", errors="replace")


def build_report(repo_root: Path) -> dict[str, Any]:
    passes: list[str] = []
    warnings: list[str] = []
    blocked: list[str] = []

    for rel in REQUIRED_FILES:
        if (repo_root / rel).exists():
            passes.append(f"file_exists:{rel}")
        else:
            add_unique(blocked, f"missing_required_file:{rel}")

    data_path = repo_root / "SANCTUM/UI_LAB/V0_5_DASHBOARD_PROTOTYPE/dashboard_data.json"
    data_payload, err = read_json(data_path)
    if err:
        add_unique(blocked, err)
        data_payload = None
    if isinstance(data_payload, dict):
        organ_index = data_payload.get("organ_index")
        if not isinstance(organ_index, list):
            add_unique(blocked, "dashboard_data.organ_index_not_list")
            organ_index = []
        seen_organs = {item.get("organ_id") for item in organ_index if isinstance(item, dict)}
        missing_organs = sorted(REQUIRED_ORGANS - {item for item in seen_organs if isinstance(item, str)})
        if missing_organs:
            add_unique(blocked, f"dashboard_data_missing_organs:{missing_organs}")
        else:
            passes.append("dashboard_data_contains_all_10_organs")

        first_four = data_payload.get("first_four_guides")
        if not isinstance(first_four, dict):
            add_unique(blocked, "dashboard_data.first_four_guides_not_object")
        else:
            missing_first_four = sorted([key for key in FIRST_FOUR if key not in first_four])
            if missing_first_four:
                add_unique(blocked, f"first_four_guides_missing:{missing_first_four}")
            else:
                passes.append("first_four_guides_present")

        if isinstance(data_payload.get("asset_summary"), dict):
            passes.append("asset_summary_present")
        else:
            add_unique(blocked, "asset_summary_missing_or_invalid")

        action_index = data_payload.get("action_index")
        if isinstance(action_index, list):
            passes.append("action_index_present")
            if not action_index:
                add_unique(warnings, "action_index_empty")
        else:
            add_unique(blocked, "action_index_missing_or_invalid")

        bundle_route = data_payload.get("bundle_route")
        if isinstance(bundle_route, dict):
            canonical = bundle_route.get("canonical_vm2_outbox")
            priority = bundle_route.get("source_priority_order")
            if canonical == "/home/vboxuser2/IMPERIUM_WORK/VM2_BUNDLES/":
                passes.append("bundle_route_canonical_vm2_outbox_ok")
            else:
                add_unique(blocked, f"bundle_route_canonical_mismatch:{canonical}")

            if isinstance(priority, list) and priority and priority[0] == canonical:
                passes.append("bundle_route_canonical_is_primary")
            else:
                add_unique(blocked, "bundle_route_primary_not_canonical")
        else:
            add_unique(blocked, "bundle_route_missing_or_invalid")

        if data_payload.get("gate_truth", {}).get("ready_for_agent") is False:
            passes.append("gate_truth_ready_for_agent_false")
        else:
            add_unique(blocked, "gate_truth_ready_for_agent_must_be_false")

        if data_payload.get("gate_truth", {}).get("act5_execution_ready") is False:
            passes.append("gate_truth_act5_execution_ready_false")
        else:
            add_unique(blocked, "gate_truth_act5_execution_ready_must_be_false")

        # Guard against global false full-operational claims.
        if isinstance(organ_index, list):
            full_operational_count = 0
            for organ in organ_index:
                if not isinstance(organ, dict):
                    continue
                if str(organ.get("readiness_level", "")).strip() == "LEVEL_7_FULLY_OPERATIONAL":
                    full_operational_count += 1
            if full_operational_count > 0:
                add_unique(blocked, f"organs_claim_full_operational_count:{full_operational_count}")
            else:
                passes.append("no_full_operational_claims_detected")

    index_path = repo_root / "SANCTUM/DASHBOARD/DASHBOARD_INDEX_V0_5.json"
    index_payload, err = read_json(index_path)
    if err:
        add_unique(blocked, err)
        index_payload = None
    if isinstance(index_payload, dict):
        passes.append("dashboard_index_json_valid")

    html_path = repo_root / "SANCTUM/UI_LAB/V0_5_DASHBOARD_PROTOTYPE/index.html"
    html = file_text(html_path)
    if 'href="styles.css"' in html and 'src="dashboard.js"' in html:
        passes.append("index_html_references_css_and_js")
    else:
        add_unique(blocked, "index_html_missing_styles_or_js_reference")

    js_path = repo_root / "SANCTUM/UI_LAB/V0_5_DASHBOARD_PROTOTYPE/dashboard.js"
    js = file_text(js_path)
    for button_id in REQUIRED_BUTTON_IDS:
        if button_id in js:
            passes.append(f"button_handler_marker_present:{button_id}")
        else:
            add_unique(blocked, f"button_handler_missing:{button_id}")

    if "Object.entries(map).forEach" in js and "addEventListener('click'" in js:
        passes.append("dashboard_js_handler_binding_present")
    else:
        add_unique(blocked, "dashboard_js_handler_binding_missing")

    ok, status_short = run_git(repo_root, ["status", "--short"])
    changed_files: list[str] = []
    if ok:
        for line in status_short.splitlines():
            raw = line.rstrip()
            if len(raw) < 4:
                continue
            path_part = raw[3:]
            if " -> " in path_part:
                path_part = path_part.split(" -> ", 1)[1]
            changed_files.append(path_part.strip())
        changed_files = sorted(set(changed_files))
        passes.append("git_status_name_scan_ok")
    else:
        add_unique(warnings, f"git_status_name_scan_failed:{status_short}")

    if "SANCTUM/sanctum_v0_29_qt.py" in changed_files:
        add_unique(blocked, "baseline_sanctum_v0_29_modified")
    else:
        passes.append("baseline_sanctum_v0_29_not_modified")

    if not (repo_root / "SANCTUM/sanctum_v0_29_qt.py").exists():
        add_unique(blocked, "baseline_sanctum_v0_29_missing")
    else:
        passes.append("baseline_sanctum_v0_29_exists")

    # Prevent EE / v0.30EE / R1 / R2 revival in changed paths.
    ee_hits = [
        path for path in changed_files
        if "v0.30EE" in path or "SANCTUM_EE" in path or "/EE/" in path or "_R1" in path or "_R2" in path
    ]
    if ee_hits:
        add_unique(blocked, f"legacy_ee_r1_r2_touch_detected:{ee_hits}")
    else:
        passes.append("no_ee_r1_r2_revival_in_changed_paths")

    # Scan changed text files for forbidden phrases.
    for rel in changed_files:
        path = repo_root / rel
        if not path.exists() or not path.is_file():
            continue
        text = file_text(path)
        if not text:
            continue
        lowered = text.lower()
        for pattern in FORBIDDEN_TEXT_PATTERNS:
            if pattern.lower() in lowered:
                add_unique(blocked, f"forbidden_text_detected:{rel}:{pattern}")

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
    print(f"task_id: {report['task_id']}")
    print(f"verdict: {report['verdict']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Sanctum Dashboard v0.5 working prototype")
    parser.add_argument("--repo-root", default=".", help="Repo root")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args()

    report = build_report(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human(report)

    return 0 if report["verdict"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
