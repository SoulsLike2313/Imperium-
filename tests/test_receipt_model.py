from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from imperium.receipts.model import create_warning_receipt



def test_warning_receipt_has_schema_version_and_timestamp() -> None:
    receipt = create_warning_receipt(
        source="tests",
        warning_code="TEST_WARNING",
        message="warning",
    )

    assert receipt["schema_version"] == "imperium.warning_receipt.v0_1"
    assert "timestamp_utc" in receipt
    assert receipt["timestamp_utc"]
