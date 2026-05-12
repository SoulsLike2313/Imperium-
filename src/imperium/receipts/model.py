"""Receipt models used by verification spine gates and reports."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any


class Verdict(str, Enum):
    PASS = "PASS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"



def utc_timestamp() -> str:
    """Return UTC timestamp in ISO8601 format."""
    return datetime.now(timezone.utc).isoformat()



def create_basic_receipt(
    receipt_id: str,
    verdict: str,
    *,
    schema_version: str = "imperium.basic_receipt.v0_1",
    warnings: list[str] | None = None,
    errors: list[str] | None = None,
    **extra_fields: Any,
) -> dict[str, Any]:
    """Create a minimal receipt envelope with standard fields."""
    payload: dict[str, Any] = {
        "schema_version": schema_version,
        "receipt_id": receipt_id,
        "timestamp_utc": utc_timestamp(),
        "verdict": verdict,
        "warnings": warnings or [],
        "errors": errors or [],
    }
    payload.update(extra_fields)
    return payload



def create_warning_receipt(
    source: str,
    warning_code: str,
    message: str,
    *,
    context: dict[str, Any] | None = None,
    schema_version: str = "imperium.warning_receipt.v0_1",
) -> dict[str, Any]:
    """Create a warning receipt with portability-safe structured fields."""
    return {
        "schema_version": schema_version,
        "timestamp_utc": utc_timestamp(),
        "source": source,
        "warning_code": warning_code,
        "message": message,
        "context": context or {},
        "verdict": Verdict.PASS_WITH_WARNINGS.value,
    }
