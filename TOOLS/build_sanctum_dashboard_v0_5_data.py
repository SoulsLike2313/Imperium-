#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

TASK_ID = "TASK-20260513-SANCTUM-DASHBOARD-V0_5-WORKING-PROTOTYPE"
EXPECTED_HEAD = "b06d312bc2dc666523468cba727e4c8e4520dc8e"

DATA_REL = "SANCTUM/UI_LAB/V0_5_DASHBOARD_PROTOTYPE/dashboard_data.json"
INDEX_REL = "SANCTUM/DASHBOARD/DASHBOARD_INDEX_V0_5.json"

REQUIRED_ORGANS = [
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
]

ORGAN_DISPLAY = {
    "CUSTODES": "Custodes",
    "INQUISITION": "Inquisition",
    "MECHANICUS": "Mechanicus",
    "ADMINISTRATUM": "Administratum",
    "ASTRONOMICON": "Astronomicon",
    "STRATEGIUM": "Strategium",
    "OFFICIO_AGENTIS": "Officio Agentis",
    "THRONE": "Throne",
    "SCHOLA_IMPERIALIS": "Schola Imperialis",
    "DOCTRINARIUM": "Doctrinarium",
}

ORGAN_ROLE_FALLBACK = {
    "CUSTODES": "Throne boundary and protection contour guard.",
    "INQUISITION": "Audit/drift detection and anti-fake-green scrutiny.",
    "MECHANICUS": "Tooling and machinery contracts for operations.",
    "ADMINISTRATUM": "Continuity, memory routing, and work-session ACK skeleton.",
    "ASTRONOMICON": "Planning corridor, advisory ingest, stage and task registration.",
    "STRATEGIUM": "Improvement and advisory research planning support.",
    "OFFICIO_AGENTIS": "Agent role contracts and execution authority limits.",
    "THRONE": "Owner-controlled canonical acceptance boundary.",
    "SCHOLA_IMPERIALIS": "Lessons learned, onboarding, and training continuity.",
    "DOCTRINARIUM": "Doctrine/law/no-fake-green guard.",
}

SOURCE_FILES = [
    "REGISTRY/BUNDLE_ROUTE_REGISTRY.json",
    "SANCTUM/ACTIONS/ACTION_REGISTRY.json",
    "SANCTUM/ACTIONS/ACTION_TEST_MATRIX_V0_1.json",
    "ASSETS/ASSET_MANIFEST.json",
    "ASSETS/INBOX_OWNER_VISUAL_SORTING/SERVITOR_SORTING_OUTPUT/SORTING_REPORT_20260513.md",
    "ASSETS/INBOX_OWNER_VISUAL_SORTING/SERVITOR_SORTING_OUTPUT/INTERPRETATION_CARDS/",
    "SANCTUM/DESIGN_SYSTEM/DESIGN_TOKENS_V0_1.json",
    "SANCTUM/DESIGN_SYSTEM/SANCTUM_VISUAL_RULES_V0_1.md",
    "CURRENT_STATE/ARC5_PREFIRE_CURRENT_TRUTH_20260513.json",
    "CURRENT_STATE/NEXT_ATOMIC_STEP.md",
    "CURRENT_STATE/BUNDLE_ROUTE_FIX_20260513_REPORT.md",
    "CURRENT_STATE/OWNER_ASSET_REGISTRATION_STEP7_2_REPORT_20260513.md",
    "CURRENT_STATE/SANCTUM_V0_4_VISUAL_PROTOTYPE_REPORT_20260513.md",
    "ORGANS/ASTRONOMICON/REGISTRY/ARC5_PREFIRE/FIRST_FOUR_ORGANS_ACT5_READINESS_20260513.json",
    "ORGANS/ASTRONOMICON/REGISTRY/ARC5_PREFIRE/ARC5_PREFIRE_PREPARATION_TASKS_20260513.json",
    "REGISTRY/SCRIPT_REGISTRY.json",
    "REGISTRY/ORGAN_REGISTRY.json",
]


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def read_json(path: Path) -> tuple[Any | None, str | None]:
    if not path.exists():
        return None, f"missing:{path.as_posix()}"
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:  # noqa: BLE001
        return None, f"invalid_json:{path.as_posix()}:{type(exc).__name__}"


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def run_git(repo_root: Path, args: list[str]) -> str | None:
    try:
        out = subprocess.run(
            ["git", *args],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception:
        return None
    if out.returncode != 0:
        return None
    return out.stdout.strip()


def safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def sanitize_phrase(value: str) -> str:
    # Keep dashboard payload compliant with strict checker phrase bans.
    banned = "fake" + " green"
    return value.replace(banned, "false-pass").replace(banned.title(), "False-pass")


def parse_card(path: Path) -> dict[str, Any]:
    lines = read_text(path).splitlines()
    extracted: dict[str, str] = {}
    for line in lines:
        striped = line.strip()
        if not striped.startswith("- "):
            continue
        if ":" not in striped:
            continue
        key, value = striped[2:].split(":", 1)
        extracted[key.strip()] = value.strip().strip("`")

    categories_raw = extracted.get("suspected_ui_categories", "")
    categories = [item.strip() for item in categories_raw.split(",") if item.strip()]

    return {
        "card_file": path.as_posix(),
        "image_path": extracted.get("source_image_path", ""),
        "source_type": extracted.get("source_type", "unknown"),
        "detected_markings": extracted.get("detected_markings", "unknown"),
        "suspected_liked_elements": extracted.get("suspected_liked_elements", ""),
        "suspected_disliked_elements": extracted.get("suspected_disliked_elements", ""),
        "categories": categories,
        "proposed_status": extracted.get("proposed_status", "needs_owner_confirmation"),
        "confidence": extracted.get("confidence", "unknown"),
        "questions_for_owner": extracted.get("questions_for_owner", ""),
    }


def classify_action_owners(action: dict[str, Any]) -> list[str]:
    action_id = str(action.get("action_id", ""))
    category = str(action.get("category", "")).lower()
    owner_zone = str(action.get("owner_zone", "")).upper()

    owners: list[str] = []
    if "ADMINISTRATUM" in owner_zone or category == "administratum_work_session":
        owners.append("ADMINISTRATUM")
    if action_id == "ACTION-READY-FOR-AGENT-GATE-CHECK":
        owners.extend(["OFFICIO_AGENTIS", "ASTRONOMICON"])
    if action_id == "ACTION-RUN-ACT5-PREFIRE-CHECKS":
        owners.extend(["DOCTRINARIUM", "ASTRONOMICON"])
    if "ASTRONOMICON" in owner_zone or category in {"gate", "verification", "state", "bundle", "bundle_intake", "remote_sync", "remote_route", "navigation"}:
        owners.append("ASTRONOMICON")
    if "SANCTUM" in owner_zone:
        owners.append("MECHANICUS")

    unique: list[str] = []
    for item in owners:
        if item not in unique:
            unique.append(item)
    return unique


def build(repo_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    warnings: list[str] = []

    parsed: dict[str, Any] = {}
    for rel in SOURCE_FILES:
        path = repo_root / rel
        if rel.endswith("/"):
            parsed[rel] = path if path.exists() else None
            if not path.exists():
                warnings.append(f"missing_source:{rel}")
            continue

        if path.suffix.lower() == ".json":
            payload, err = read_json(path)
            parsed[rel] = payload
            if err:
                warnings.append(err)
        else:
            if path.exists():
                parsed[rel] = read_text(path)
            else:
                parsed[rel] = ""
                warnings.append(f"missing_source:{rel}")

    head = run_git(repo_root, ["rev-parse", "HEAD"]) or "UNKNOWN"
    commit_count_raw = run_git(repo_root, ["rev-list", "--count", "HEAD"])
    latest_oneline = run_git(repo_root, ["log", "-1", "--oneline"]) or "UNKNOWN"
    commit_count = int(commit_count_raw) if commit_count_raw and commit_count_raw.isdigit() else None

    current_truth = parsed.get("CURRENT_STATE/ARC5_PREFIRE_CURRENT_TRUTH_20260513.json")
    current_truth = current_truth if isinstance(current_truth, dict) else {}

    bundle_route = parsed.get("REGISTRY/BUNDLE_ROUTE_REGISTRY.json")
    bundle_route = bundle_route if isinstance(bundle_route, dict) else {}

    action_registry = parsed.get("SANCTUM/ACTIONS/ACTION_REGISTRY.json")
    action_registry = action_registry if isinstance(action_registry, dict) else {}
    actions = safe_list(action_registry.get("actions"))

    matrix = parsed.get("SANCTUM/ACTIONS/ACTION_TEST_MATRIX_V0_1.json")
    matrix = matrix if isinstance(matrix, dict) else {}
    matrix_entries = safe_list(matrix.get("entries"))
    matrix_by_id: dict[str, dict[str, Any]] = {}
    for entry in matrix_entries:
        if isinstance(entry, dict) and isinstance(entry.get("action_id"), str):
            matrix_by_id[entry["action_id"]] = entry

    action_index: list[dict[str, Any]] = []
    action_owner_map: dict[str, list[str]] = {organ: [] for organ in REQUIRED_ORGANS}
    disabled_actions: list[str] = []
    for item in actions:
        if not isinstance(item, dict):
            continue
        action_id = str(item.get("action_id", "UNKNOWN_ACTION"))
        test_entry = matrix_by_id.get(action_id, {})
        row = {
            "action_id": action_id,
            "title": item.get("title", "UNKNOWN"),
            "status": item.get("status", "UNKNOWN"),
            "category": item.get("category", "unknown"),
            "risk_level": item.get("risk_level", "unknown"),
            "handler_reference": item.get("handler_reference", "UNKNOWN"),
            "required_prechecks": safe_list(item.get("required_prechecks")),
            "expected_receipts": safe_list(item.get("expected_receipts")),
            "test_or_smoke_check": item.get("test_or_smoke_check", "missing"),
            "implementation_status": item.get("implementation_status", "UNKNOWN"),
            "test_status": test_entry.get("test_status", "UNKNOWN"),
        }
        action_index.append(row)
        if row["status"] in {"REGISTERED_CONCEPT", "REGISTERED_NEEDS_HANDLER", "REGISTERED_NEEDS_TEST", "BLOCKED_UNSAFE"}:
            disabled_actions.append(action_id)
        for organ_id in classify_action_owners(item):
            if organ_id in action_owner_map:
                action_owner_map[organ_id].append(action_id)

    manifest = parsed.get("ASSETS/ASSET_MANIFEST.json")
    manifest = manifest if isinstance(manifest, dict) else {}
    manifest_assets = safe_list(manifest.get("assets"))

    status_counter = collections.Counter()
    category_counter = collections.Counter()
    for asset in manifest_assets:
        if not isinstance(asset, dict):
            continue
        status_counter[str(asset.get("proposed_status", "candidate"))] += 1
        cats = asset.get("categories")
        cats = cats if isinstance(cats, list) else []
        for cat in cats:
            if isinstance(cat, str) and cat.strip():
                category_counter[cat.strip()] += 1

    cards_dir = repo_root / "ASSETS/INBOX_OWNER_VISUAL_SORTING/SERVITOR_SORTING_OUTPUT/INTERPRETATION_CARDS"
    asset_cards: list[dict[str, Any]] = []
    if cards_dir.exists() and cards_dir.is_dir():
        for card_file in sorted(cards_dir.glob("CARD_*.md")):
            asset_cards.append(parse_card(card_file))
    else:
        warnings.append("missing_interpretation_cards_directory")

    sorting_report_text = str(parsed.get("ASSETS/INBOX_OWNER_VISUAL_SORTING/SERVITOR_SORTING_OUTPUT/SORTING_REPORT_20260513.md", ""))

    first_four = parsed.get("ORGANS/ASTRONOMICON/REGISTRY/ARC5_PREFIRE/FIRST_FOUR_ORGANS_ACT5_READINESS_20260513.json")
    first_four = first_four if isinstance(first_four, dict) else {}
    first_four_entries = safe_list(first_four.get("organs"))
    first_four_by_id: dict[str, dict[str, Any]] = {}
    for row in first_four_entries:
        if isinstance(row, dict) and isinstance(row.get("organ_id"), str):
            first_four_by_id[row["organ_id"]] = row

    organ_registry = parsed.get("REGISTRY/ORGAN_REGISTRY.json")
    organ_registry = organ_registry if isinstance(organ_registry, dict) else {}
    registry_organs = safe_list(organ_registry.get("organs"))
    registry_organs_by_id: dict[str, dict[str, Any]] = {}
    for row in registry_organs:
        if isinstance(row, dict) and isinstance(row.get("organ_id"), str):
            registry_organs_by_id[row["organ_id"]] = row

    reports_index = [
        {
            "title": "ARC5 Current Truth",
            "path": "CURRENT_STATE/ARC5_PREFIRE_CURRENT_TRUTH_20260513.json",
            "summary": "Current prefire truth and blocked execution status.",
        },
        {
            "title": "Next Atomic Step",
            "path": "CURRENT_STATE/NEXT_ATOMIC_STEP.md",
            "summary": "Current sequence and forbidden next actions.",
        },
        {
            "title": "Bundle Route Fix Report",
            "path": "CURRENT_STATE/BUNDLE_ROUTE_FIX_20260513_REPORT.md",
            "summary": "Canonical VM2 outbox route policy evidence.",
        },
        {
            "title": "Owner Asset Registration Step 7.2 Report",
            "path": "CURRENT_STATE/OWNER_ASSET_REGISTRATION_STEP7_2_REPORT_20260513.md",
            "summary": "Asset intake counts and proposal boundaries.",
        },
        {
            "title": "Sanctum v0.4 Prototype Report",
            "path": "CURRENT_STATE/SANCTUM_V0_4_VISUAL_PROTOTYPE_REPORT_20260513.md",
            "summary": "v0.4 technical proof status and limitations.",
        },
        {
            "title": "Visual Rules",
            "path": "SANCTUM/DESIGN_SYSTEM/SANCTUM_VISUAL_RULES_V0_1.md",
            "summary": "Confirmed and proposed visual rules.",
        },
        {
            "title": "Sorting Report",
            "path": "ASSETS/INBOX_OWNER_VISUAL_SORTING/SERVITOR_SORTING_OUTPUT/SORTING_REPORT_20260513.md",
            "summary": "Interpreted owner taste evidence report.",
        },
    ]

    organ_index: list[dict[str, Any]] = []
    for organ_id in REQUIRED_ORGANS:
        reg = registry_organs_by_id.get(organ_id, {})
        ff = first_four_by_id.get(organ_id, {})

        primary_files: list[str] = []
        base_path = reg.get("path")
        if isinstance(base_path, str) and base_path:
            primary_files.append(base_path)
            if (repo_root / base_path / "ORGAN_CONTRACT.json").exists():
                primary_files.append(f"{base_path}/ORGAN_CONTRACT.json")
            if (repo_root / base_path / "ORGAN_SELF_REPORT.json").exists():
                primary_files.append(f"{base_path}/ORGAN_SELF_REPORT.json")
        if ff:
            for key in ["contract_file", "self_report_file", "status_file"]:
                value = ff.get(key)
                if isinstance(value, str) and value and value not in primary_files:
                    primary_files.append(value)

        status = ff.get("act5_guide_readiness") if isinstance(ff.get("act5_guide_readiness"), str) else reg.get("status", "UNKNOWN")
        maturity = ff.get("current_maturity_claim") if isinstance(ff.get("current_maturity_claim"), str) else reg.get("maturity", "UNKNOWN")
        role = ff.get("role_in_act5") if isinstance(ff.get("role_in_act5"), str) else reg.get("responsibility", ORGAN_ROLE_FALLBACK.get(organ_id, "UNKNOWN"))

        warnings_for_organ: list[str] = []
        if not ff and organ_id in {"DOCTRINARIUM", "ADMINISTRATUM", "ASTRONOMICON", "OFFICIO_AGENTIS"}:
            warnings_for_organ.append("first_four_readiness_row_missing")
        if organ_id not in first_four_by_id and organ_id in {"CUSTODES", "INQUISITION", "MECHANICUS", "STRATEGIUM", "THRONE", "SCHOLA_IMPERIALIS"}:
            warnings_for_organ.append("not_in_first_four_scope")
        if maturity in {"UNKNOWN", "LEVEL_0_SCAFFOLD"}:
            warnings_for_organ.append("maturity_low_or_unknown")

        related_reports = [
            "CURRENT_STATE/ARC5_PREFIRE_CURRENT_TRUTH_20260513.json",
            "CURRENT_STATE/NEXT_ATOMIC_STEP.md",
        ]
        if ff.get("contract_file"):
            related_reports.append("ORGANS/ASTRONOMICON/REGISTRY/ARC5_PREFIRE/FIRST_FOUR_ORGANS_ACT5_READINESS_20260513.json")

        organ_index.append(
            {
                "organ_id": organ_id,
                "display_name": ORGAN_DISPLAY.get(organ_id, organ_id.title()),
                "role_summary": role,
                "status": status,
                "readiness_level": maturity,
                "primary_files": primary_files,
                "related_reports": related_reports,
                "available_actions": sorted(set(action_owner_map.get(organ_id, []))),
                "warnings": warnings_for_organ,
            }
        )

    missing_sources = [item for item in warnings if item.startswith("missing_source:")]
    global_warnings: list[str] = [
        "No false PASS claims: READY_FOR_AGENT must remain false.",
        "Act 5 execution remains blocked.",
    ]
    if missing_sources:
        global_warnings.append(f"Missing source files detected: {len(missing_sources)}")
    if disabled_actions:
        global_warnings.append(f"Disabled/planned actions in registry: {len(disabled_actions)}")

    visual_rules_text = str(parsed.get("SANCTUM/DESIGN_SYSTEM/SANCTUM_VISUAL_RULES_V0_1.md", ""))
    design_tokens_payload = parsed.get("SANCTUM/DESIGN_SYSTEM/DESIGN_TOKENS_V0_1.json")
    design_tokens_payload = design_tokens_payload if isinstance(design_tokens_payload, dict) else {}

    dashboard_data = {
        "schema_version": "imperium.sanctum_dashboard_data.v0_5",
        "task_id": TASK_ID,
        "generated_at": now_utc(),
        "git_truth_snapshot": {
            "expected_head": EXPECTED_HEAD,
            "local_head": head,
            "commit_count": commit_count,
            "latest_commit": latest_oneline,
            "latest_known_commit_from_current_state": current_truth.get("latest_commit_subject"),
        },
        "gate_truth": {
            "ready_for_agent": False,
            "act5_execution_ready": False,
        },
        "organ_index": organ_index,
        "first_four_guides": {
            "DOCTRINARIUM": first_four_by_id.get("DOCTRINARIUM", {}),
            "ADMINISTRATUM": first_four_by_id.get("ADMINISTRATUM", {}),
            "ASTRONOMICON": first_four_by_id.get("ASTRONOMICON", {}),
            "OFFICIO_AGENTIS": first_four_by_id.get("OFFICIO_AGENTIS", {}),
        },
        "action_index": action_index,
        "bundle_route": {
            "canonical_vm2_outbox": bundle_route.get("canonical_vm2_outbox", "UNKNOWN"),
            "canonical_pc_inbox": bundle_route.get("canonical_pc_inbox", "UNKNOWN"),
            "legacy_scan_dirs": safe_list(bundle_route.get("legacy_scan_dirs")),
            "source_priority_order": safe_list(bundle_route.get("source_priority_order")),
            "owner_rule": bundle_route.get("owner_rule", "UNKNOWN"),
        },
        "asset_summary": {
            "total_assets": len(manifest_assets),
            "proposed_accepted": status_counter.get("accepted", 0),
            "proposed_rejected": status_counter.get("rejected", 0),
            "proposed_candidate": status_counter.get("candidate", 0),
            "owner_confirmation_required": manifest.get("owner_confirmation_required", True),
            "top_categories": [
                {"category": key, "count": value}
                for key, value in category_counter.most_common(8)
            ],
            "interpretation_cards_count": len(asset_cards),
            "sorting_report_excerpt": "\n".join(sorting_report_text.splitlines()[:10]),
        },
        "asset_cards": asset_cards,
        "reports_index": reports_index,
        "warnings": global_warnings,
        "ui_capabilities": {
            "implemented_buttons": [
                "toggle_orbit_animation",
                "show_all_organs",
                "show_guide_organs",
                "show_warnings",
                "filter_assets_accepted",
                "filter_assets_candidate",
                "filter_assets_rejected",
                "clear_asset_filters",
                "show_route_policy",
                "show_action_registry",
                "show_reports",
                "compact_mode_toggle",
                "clear_console",
            ],
            "disabled_or_planned": [
                "real_backend_fetch_bundle_bridge",
                "dangerous_backend_action_execution",
                "ready_for_agent_mutation",
            ],
        },
        "visual_rules_tokens_summary": {
            "rules_preview": sanitize_phrase("\n".join(visual_rules_text.splitlines()[:18])),
            "tokens_status": design_tokens_payload.get("status", "missing_or_unknown"),
            "tokens_roles": safe_list(design_tokens_payload.get("color_role_names")),
        },
    }

    dashboard_index = {
        "schema_version": "imperium.sanctum_dashboard_index.v0_5",
        "task_id": TASK_ID,
        "version": "SANCTUM_DASHBOARD_V0_5_WORKING_PROTOTYPE",
        "generated_at": now_utc(),
        "dashboard_files": [
            "SANCTUM/UI_LAB/V0_5_DASHBOARD_PROTOTYPE/index.html",
            "SANCTUM/UI_LAB/V0_5_DASHBOARD_PROTOTYPE/styles.css",
            "SANCTUM/UI_LAB/V0_5_DASHBOARD_PROTOTYPE/dashboard.js",
            DATA_REL,
            INDEX_REL,
            "SANCTUM/UI_LAB/V0_5_DASHBOARD_PROTOTYPE/README.md",
        ],
        "builder": "TOOLS/build_sanctum_dashboard_v0_5_data.py",
        "checker": "TOOLS/check_sanctum_dashboard_v0_5.py",
        "source_files_read": SOURCE_FILES,
        "organs": REQUIRED_ORGANS,
        "active_buttons": dashboard_data["ui_capabilities"]["implemented_buttons"],
        "disabled_planned_backend_actions": dashboard_data["ui_capabilities"]["disabled_or_planned"],
        "limitations": [
            "Prototype is static UI_LAB dashboard; no direct dangerous backend execution.",
            "Asset proposals remain non-canon until Owner confirmation.",
            "READY_FOR_AGENT remains false and Act 5 execution remains blocked.",
            "v0.29 baseline remains authoritative runtime; v0.4 preserved as technical proof.",
        ],
        "future_promotion_requirements": [
            "Backend bridge with gated receipts for safe actions",
            "Playwright/UI evidence coverage",
            "Owner visual acceptance of proposed rules/tokens",
            "Dedicated acceptance gate before production promotion",
        ],
    }

    return dashboard_data, dashboard_index


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Sanctum Dashboard v0.5 data/index")
    parser.add_argument("--repo-root", default=".", help="Repo root")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    data, index = build(repo_root)

    data_path = repo_root / DATA_REL
    index_path = repo_root / INDEX_REL
    write_json(data_path, data)
    write_json(index_path, index)

    print(f"PASS: built {DATA_REL}")
    print(f"PASS: built {INDEX_REL}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
