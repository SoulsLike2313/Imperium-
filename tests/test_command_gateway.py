from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from imperium.security.command_gateway import run_allowed



def _write_allowlist(path: Path) -> None:
    payload = {
        "schema_version": "imperium.command_allowlist.v0_1",
        "commands": [
            {
                "schema_version": "imperium.command_allow_entry.v0_1",
                "command_id": "test.echo",
                "description": "Test echo command",
                "risk_level": "LOW",
                "allowed_argv_template": ["python3", "-c", "print('ok')"],
                "allowed_modes": ["dev", "operator"],
                "receipt_required": True,
            }
        ],
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")



def test_command_gateway_blocks_unknown_command_id(tmp_path: Path) -> None:
    allowlist = tmp_path / "allowlist.json"
    _write_allowlist(allowlist)

    receipt = run_allowed(
        "does.not.exist",
        allowlist_path=allowlist,
        root=tmp_path,
        cwd=tmp_path,
    )

    assert receipt["allowed"] is False
    assert receipt["verdict"] == "BLOCKED"



def test_dry_run_command_creates_receipt_without_execution(tmp_path: Path) -> None:
    allowlist = tmp_path / "allowlist.json"
    _write_allowlist(allowlist)

    receipt = run_allowed(
        "test.echo",
        dry_run=True,
        allowlist_path=allowlist,
        root=tmp_path,
        cwd=tmp_path,
    )

    assert receipt["allowed"] is True
    assert receipt["dry_run"] is True
    assert receipt["exit_code"] is None
    assert receipt["argv"] == ["python3", "-c", "print('ok')"]
