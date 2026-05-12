"""JSON receipt validation helpers."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

from .model import Verdict, utc_timestamp



def _jsonschema_available() -> bool:
    return importlib.util.find_spec("jsonschema") is not None



def validate_json_file(path: str | Path, schema_path: str | Path) -> dict[str, Any]:
    """Validate a JSON file against schema.

    If jsonschema dependency is unavailable, returns FAIL_WITH_MESSAGE to avoid fake pass.
    """
    payload_path = Path(path).expanduser().resolve()
    schema_file = Path(schema_path).expanduser().resolve()

    result: dict[str, Any] = {
        "schema_version": "imperium.validation_result.v0_1",
        "timestamp_utc": utc_timestamp(),
        "path": str(payload_path),
        "schema_path": str(schema_file),
        "valid": False,
        "verdict": Verdict.FAIL.value,
        "errors": [],
    }

    try:
        with payload_path.open("r", encoding="utf-8") as payload_handle:
            payload = json.load(payload_handle)
        with schema_file.open("r", encoding="utf-8") as schema_handle:
            schema = json.load(schema_handle)
    except Exception as exc:
        result["errors"].append(f"Failed to load JSON or schema: {exc}")
        return result

    if not _jsonschema_available():
        result["verdict"] = "FAIL_WITH_MESSAGE"
        result["errors"].append("jsonschema dependency is not installed.")
        return result

    from jsonschema import Draft202012Validator  # type: ignore[import-not-found]

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda err: err.path)

    if errors:
        result["errors"] = [err.message for err in errors]
        result["verdict"] = Verdict.FAIL.value
        result["valid"] = False
        return result

    result["valid"] = True
    result["verdict"] = Verdict.PASS.value
    return result
