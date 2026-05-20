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
    required = schema.get("required", [])
    for key in required:
        if key not in data:
            errors.append(f"missing required field: {key}")
    return errors


def validate_component_manifest(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    components = data.get("components")
    if not isinstance(components, list) or not components:
        return ["components must be a non-empty array"]
    for index, item in enumerate(components):
        if not isinstance(item, dict):
            errors.append(f"components[{index}] must be object")
            continue
        for field in ("id", "name", "states"):
            if field not in item:
                errors.append(f"components[{index}] missing {field}")
        if "states" in item and not isinstance(item["states"], list):
            errors.append(f"components[{index}].states must be array")
    return errors


def build_report() -> dict[str, Any]:
    contract_path = ROOT / "CONTRACTS" / "visual_contract.json"
    tokens_path = ROOT / "TOKENS" / "design_tokens_mechanicus_console_v0_1.json"
    manifest_path = ROOT / "COMPONENTS" / "component_state_manifest.json"
    intake_path = ROOT / "OWNER_INTAKE" / "owner_visual_intake.json"
    screenshot_index_path = ROOT / "SCREENSHOTS" / "screenshot_index.json"

    contract_schema = load_json(SCHEMAS / "visual_contract.schema.json")
    tokens_schema = load_json(SCHEMAS / "design_tokens_min.schema.json")
    manifest_schema = load_json(SCHEMAS / "component_state_manifest.schema.json")

    contract_data = load_json(contract_path)
    tokens_data = load_json(tokens_path)
    manifest_data = load_json(manifest_path)
    intake_data = load_json(intake_path)
    screenshot_index = load_json(screenshot_index_path)

    checks = []

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
            "path": str(tokens_path),
            "ok": not tokens_errors,
            "errors": tokens_errors,
        }
    )

    manifest_errors = validate_required_fields(manifest_data, manifest_schema)
    manifest_errors.extend(validate_component_manifest(manifest_data))
    checks.append(
        {
            "name": "component_manifest_schema_min",
            "path": str(manifest_path),
            "ok": not manifest_errors,
            "errors": manifest_errors,
        }
    )

    intake_ok = isinstance(intake_data.get("must_have_regions"), list) and len(intake_data["must_have_regions"]) >= 5
    checks.append(
        {
            "name": "owner_intake_shape",
            "path": str(intake_path),
            "ok": intake_ok,
            "errors": [] if intake_ok else ["must_have_regions missing or too short"],
        }
    )

    files = screenshot_index.get("files", [])
    screenshots_ok = isinstance(files, list) and len(files) >= 6
    checks.append(
        {
            "name": "screenshot_index_presence",
            "path": str(screenshot_index_path),
            "ok": screenshots_ok,
            "errors": [] if screenshots_ok else ["screenshot index missing required files"],
        }
    )

    verdict = "PASS" if all(item["ok"] for item in checks) else "BLOCK"
    return {
        "task_id": "TASK-20260520-NEWGEN-SANCTUM-VISUAL-FOUNDRY-MECHANICUS-CONSOLE-SLICE-V0_1",
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

