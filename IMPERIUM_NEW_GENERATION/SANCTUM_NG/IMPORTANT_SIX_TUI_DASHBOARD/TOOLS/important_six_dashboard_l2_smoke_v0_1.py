#!/usr/bin/env python3
"""API smoke for Important Six dashboard L2 action surface."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

TASK_ID = "TASK-20260524-NEWGEN-DASHBOARD-L2-CONTROL-ACTION-SURFACE-PC-V0_1"

REQUIRED_ACTIONS = [
    "ADMIN_FULL_NEWGEN_FILE_AUDIT",
    "ADMIN_BUILD_CONTINUITY_PACK",
    "TRANSFER_SEND_TASKPACK_VM2_DRY_RUN",
    "TRANSFER_SEND_TASKPACK_VM3_DRY_RUN",
    "TRANSFER_FETCH_REPORT_VM2_DRY_RUN",
    "TRANSFER_FETCH_REPORT_VM3_DRY_RUN",
    "MECHANICUS_CHECK_REQUIRED_TOOLS",
    "MECHANICUS_CHECK_SCRIPTS_VALIDATORS",
    "INQUISITION_REPO_HYGIENE_AUDIT",
    "INQUISITION_FAKE_GREEN_RISK_SCAN",
    "ASTRONOMICON_REGISTER_TASK_DRAFT",
    "DIFF_COMPARE_HEADS",
    "OWNER_RECORD_DIFF_DECISION",
    "OWNER_QUESTIONS_LIST",
    "OWNER_RECORD_NOTE_OR_DECISION",
]

REQUIRED_GROUPS = {
    "Administratum",
    "Transfer Zone",
    "Mechanicus",
    "Inquisition",
    "Astronomicon",
    "Diff / Approval",
    "Owner Intent / Questions",
}

REGISTRY_REQUIRED_FIELDS = {
    "action_id",
    "owner_organ",
    "label_ru",
    "description",
    "safety_class",
    "writes_allowed",
    "output_root",
    "handler",
    "dry_run_supported",
    "receipt_required",
    "dashboard_button_group",
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[4]
    default_report_root = (
        repo_root
        / "IMPERIUM_NEW_GENERATION"
        / "REPORTS"
        / "TASK-20260524-NEWGEN-DASHBOARD-L2-CONTROL-ACTION-SURFACE-PC-V0_1"
    )
    parser = argparse.ArgumentParser(description="Run Important Six dashboard L2 API smoke.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8766")
    parser.add_argument("--timeout-sec", type=float, default=70.0)
    parser.add_argument("--report-root", type=Path, default=default_report_root)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fetch_json(url: str, timeout_sec: float) -> dict[str, Any] | list[Any]:
    with urllib.request.urlopen(url, timeout=timeout_sec) as response:
        raw = response.read().decode("utf-8")
    return json.loads(raw)


def post_json(url: str, payload: dict[str, Any], timeout_sec: float) -> tuple[int, dict[str, Any] | list[Any]]:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_sec) as response:
            raw = response.read().decode("utf-8")
            return int(response.status), json.loads(raw)
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload_json = json.loads(raw)
        except json.JSONDecodeError:
            payload_json = {"raw_error": raw}
        return int(exc.code), payload_json


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[4]
    base_url = args.base_url.rstrip("/")
    report_root = args.report_root.resolve()
    report_root.mkdir(parents=True, exist_ok=True)

    output_path = args.output.resolve() if args.output else report_root / "dashboard_l2_action_api_smoke_report.json"
    registry_validation_path = report_root / "action_registry_validation_report.json"
    sample_receipts_index_path = report_root / "sample_action_receipts_index.json"
    json_parse_report_path = report_root / "json_parse_validation_report.json"

    steps: list[dict[str, Any]] = []
    blockers: list[str] = []
    warnings: list[str] = []
    receipt_paths: list[str] = []

    def add_step(name: str, status: str, details: Any) -> None:
        steps.append({"step": name, "status": status, "details": details})
        if status == "BLOCK":
            blockers.append(name)
        elif status == "WARN":
            warnings.append(name)

    # Base endpoint checks.
    for endpoint in ("/api/status", "/api/actions", "/api/action-history", "/api/owner-questions", "/api/diff/status"):
        url = f"{base_url}{endpoint}"
        try:
            payload = fetch_json(url, args.timeout_sec)
            add_step(f"get_{endpoint}", "PASS", {"url": url, "json_type": type(payload).__name__})
            if endpoint == "/api/actions" and isinstance(payload, dict):
                groups = payload.get("groups", {})
                group_names = set(groups.keys()) if isinstance(groups, dict) else set()
                missing_groups = sorted(REQUIRED_GROUPS - group_names)
                add_step(
                    "required_groups_check",
                    "PASS" if not missing_groups else "BLOCK",
                    {"found": sorted(group_names), "missing": missing_groups},
                )
        except Exception as exc:  # noqa: BLE001
            add_step(f"get_{endpoint}", "BLOCK", {"url": url, "error": str(exc)})

    # Registry fields and required actions from /api/actions.
    registry_actions: list[dict[str, Any]] = []
    try:
        api_actions = fetch_json(f"{base_url}/api/actions", args.timeout_sec)
        if isinstance(api_actions, dict) and isinstance(api_actions.get("groups"), dict):
            for group, items in api_actions["groups"].items():
                if not isinstance(items, list):
                    continue
                for item in items:
                    if isinstance(item, dict):
                        entry = dict(item)
                        entry["dashboard_button_group"] = entry.get("dashboard_button_group", group)
                        registry_actions.append(entry)
    except Exception as exc:  # noqa: BLE001
        add_step("collect_registry_actions", "BLOCK", str(exc))

    found_action_ids = {str(entry.get("action_id")) for entry in registry_actions}
    missing_actions = [action_id for action_id in REQUIRED_ACTIONS if action_id not in found_action_ids]
    add_step(
        "required_actions_check",
        "PASS" if not missing_actions else "BLOCK",
        {"found_count": len(found_action_ids), "missing_actions": missing_actions},
    )

    registry_checks: list[dict[str, Any]] = []
    registry_has_block = False
    for entry in registry_actions:
        action_id = str(entry.get("action_id", "UNKNOWN"))
        missing_fields = sorted(REGISTRY_REQUIRED_FIELDS - set(entry.keys()))
        status = "PASS" if not missing_fields else "BLOCK"
        if status == "BLOCK":
            registry_has_block = True
        registry_checks.append({"action_id": action_id, "status": status, "missing_fields": missing_fields})
    registry_validation_payload = {
        "schema_id": "important_six_action_registry_validation_report_v0_1",
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "verdict": "BLOCK" if registry_has_block else "PASS",
        "checks": registry_checks,
    }
    write_json(registry_validation_path, registry_validation_payload)

    # Run required actions.
    payloads_by_action = {
        "OWNER_RECORD_DIFF_DECISION": {"decision": "NEEDS_REWORK", "note_ru": "Smoke: проверка записи решения Owner."},
        "OWNER_RECORD_NOTE_OR_DECISION": {
            "organ": "OFFICIO_AGENTIS",
            "severity": "MEDIUM",
            "question": "Smoke note",
            "required_decision": "OWNER_REVIEW",
            "note_ru": "Smoke: проверка owner note записи.",
        },
    }

    for action_id in REQUIRED_ACTIONS:
        payload = payloads_by_action.get(action_id, {})
        url = f"{base_url}/api/actions/{action_id}/run"
        try:
            status_code, result = post_json(url, payload, args.timeout_sec)
            if isinstance(result, dict):
                status = str(result.get("status", "BLOCK")).upper()
                receipt_path = result.get("receipt_path")
                if isinstance(receipt_path, str):
                    receipt_paths.append(receipt_path)
            else:
                status = "BLOCK"
            if status_code >= 400 or status == "BLOCK":
                add_step(f"run_{action_id}", "BLOCK", {"http_status": status_code, "result": result})
            elif status == "WARN":
                add_step(f"run_{action_id}", "WARN", {"http_status": status_code, "result": result})
            else:
                add_step(f"run_{action_id}", "PASS", {"http_status": status_code, "result": result})
        except Exception as exc:  # noqa: BLE001
            add_step(f"run_{action_id}", "BLOCK", {"error": str(exc)})

        # last-result check
        try:
            last_payload = fetch_json(f"{base_url}/api/actions/{action_id}/last-result", args.timeout_sec)
            ok = isinstance(last_payload, dict) and last_payload.get("action_id") == action_id
            add_step(f"last_{action_id}", "PASS" if ok else "BLOCK", last_payload)
        except Exception as exc:  # noqa: BLE001
            add_step(f"last_{action_id}", "BLOCK", {"error": str(exc)})

    # Direct endpoint check for owner decision record.
    try:
        decision_url = f"{base_url}/api/owner-intent/decision"
        status_code, result = post_json(
            decision_url,
            {"decision": "APPROVE", "note_ru": "Smoke: direct endpoint check."},
            args.timeout_sec,
        )
        if status_code >= 400:
            add_step("direct_owner_intent_decision_endpoint", "BLOCK", {"http_status": status_code, "result": result})
        else:
            add_step("direct_owner_intent_decision_endpoint", "PASS", {"http_status": status_code, "result": result})
    except Exception as exc:  # noqa: BLE001
        add_step("direct_owner_intent_decision_endpoint", "BLOCK", {"error": str(exc)})

    # Receipts index from action run outputs.
    receipt_records: list[dict[str, Any]] = []
    for rel_path in sorted(set(receipt_paths)):
        abs_path = repo_root / rel_path
        exists = abs_path.exists()
        receipt_records.append({"receipt_path": rel_path, "exists": exists})
    sample_receipts_index = {
        "schema_id": "important_six_sample_action_receipts_index_v0_1",
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "receipts": receipt_records,
    }
    write_json(sample_receipts_index_path, sample_receipts_index)

    verdict = "PASS"
    if blockers:
        verdict = "BLOCK"
    elif warnings:
        verdict = "WARN"

    smoke_report = {
        "schema_id": "important_six_dashboard_l2_action_api_smoke_report_v0_1",
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "base_url": base_url,
        "verdict": verdict,
        "blockers": blockers,
        "warnings": warnings,
        "steps": steps,
    }
    write_json(output_path, smoke_report)

    # Parse-check generated JSON outputs.
    parse_checks: list[dict[str, Any]] = []
    for path in (
        output_path,
        registry_validation_path,
        sample_receipts_index_path,
    ):
        try:
            parsed = json.loads(path.read_text(encoding="utf-8"))
            parse_checks.append({"path": str(path), "status": "PASS", "json_type": type(parsed).__name__})
        except Exception as exc:  # noqa: BLE001
            parse_checks.append({"path": str(path), "status": "BLOCK", "error": str(exc)})
    parse_report = {
        "schema_id": "important_six_dashboard_l2_json_parse_validation_report_v0_1",
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "verdict": "PASS" if all(item["status"] == "PASS" for item in parse_checks) else "BLOCK",
        "checks": parse_checks,
    }
    write_json(json_parse_report_path, parse_report)

    return 0 if not blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
