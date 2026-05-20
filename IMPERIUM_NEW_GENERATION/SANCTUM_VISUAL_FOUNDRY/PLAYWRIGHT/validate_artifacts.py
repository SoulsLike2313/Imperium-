from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "SCHEMAS"
REPORTS = ROOT / "REPORTS"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_required_fields(data: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in schema.get("required", []):
        if field not in data:
            errors.append(f"missing required field: {field}")
    return errors


def validate_manifest_shape(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    components = data.get("components")
    if not isinstance(components, list) or not components:
        return ["components must be a non-empty array"]
    for i, item in enumerate(components):
        if not isinstance(item, dict):
            errors.append(f"components[{i}] must be object")
            continue
        for key in ("id", "name", "states"):
            if key not in item:
                errors.append(f"components[{i}] missing {key}")
    return errors


def build_report() -> dict[str, Any]:
    intake_path = ROOT / "OWNER_INTAKE" / "owner_visual_intake_v0_1.json"
    contract_path = ROOT / "CONTRACTS" / "visual_contract_mechanicus_console_v0_1.json"
    tokens_json_path = ROOT / "TOKENS" / "design_tokens_mechanicus_console_v0_1.json"
    tokens_css_path = ROOT / "TOKENS" / "design_tokens_mechanicus_console_v0_1.css"
    manifest_path = ROOT / "COMPONENTS" / "component_state_manifest_mechanicus_console_v0_1.json"
    screenshot_index_path = ROOT / "SCREENSHOTS" / "screenshot_index.json"

    intake_schema = load_json(SCHEMAS / "owner_visual_intake.schema.json")
    contract_schema = load_json(SCHEMAS / "visual_contract.schema.json")
    tokens_schema = load_json(SCHEMAS / "design_tokens_min.schema.json")
    manifest_schema = load_json(SCHEMAS / "component_state_manifest.schema.json")

    intake_data = load_json(intake_path)
    contract_data = load_json(contract_path)
    tokens_data = load_json(tokens_json_path)
    manifest_data = load_json(manifest_path)
    screenshot_index = load_json(screenshot_index_path)

    checks: list[dict[str, Any]] = []

    intake_errors = validate_required_fields(intake_data, intake_schema)
    checks.append(
        {
            "name": "owner_intake_schema_min",
            "path": str(intake_path),
            "ok": not intake_errors,
            "errors": intake_errors,
        }
    )

    contract_errors = validate_required_fields(contract_data, contract_schema)
    checks.append(
        {
            "name": "visual_contract_schema_min",
            "path": str(contract_path),
            "ok": not contract_errors,
            "errors": contract_errors,
        }
    )

    tokens_errors = validate_required_fields(tokens_data, tokens_schema)
    checks.append(
        {
            "name": "design_tokens_schema_min",
            "path": str(tokens_json_path),
            "ok": not tokens_errors,
            "errors": tokens_errors,
        }
    )

    css_ok = tokens_css_path.exists() and tokens_css_path.stat().st_size > 100
    checks.append(
        {
            "name": "design_tokens_css_export",
            "path": str(tokens_css_path),
            "ok": css_ok,
            "errors": [] if css_ok else ["token css export missing or empty"],
        }
    )

    manifest_errors = validate_required_fields(manifest_data, manifest_schema)
    manifest_errors.extend(validate_manifest_shape(manifest_data))
    checks.append(
        {
            "name": "component_manifest_schema_min",
            "path": str(manifest_path),
            "ok": not manifest_errors,
            "errors": manifest_errors,
        }
    )

    files = screenshot_index.get("files", [])
    required_shots = {
        "mechanicus_slice_full_1366x768.png",
        "mechanicus_slice_full_1920x1080.png",
        "mechanicus_slice_top_truth_strip.png",
        "mechanicus_slice_right_panel_visible.png",
        "mechanicus_slice_raw_secondary.png",
    }
    files_ok = isinstance(files, list) and required_shots.issubset(set(files))
    checks.append(
        {
            "name": "screenshot_evidence_set",
            "path": str(screenshot_index_path),
            "ok": files_ok,
            "errors": [] if files_ok else ["required screenshot files missing in screenshot_index"],
        }
    )

    verdict = "PASS" if all(item["ok"] for item in checks) else "BLOCK"
    return {
        "task_id": "TASK-20260520-NEWGEN-VISUAL-CONTRACT-TO-TOKENS-AND-MECHANICUS-SLICE-PC-V0_1",
        "generated_at_utc": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "validator": "validate_artifacts.py",
        "checks": checks,
        "verdict": verdict,
    }


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    report = build_report()
    out_path = REPORTS / "validation_report.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(out_path)
    print(report["verdict"])


if __name__ == "__main__":
    main()
