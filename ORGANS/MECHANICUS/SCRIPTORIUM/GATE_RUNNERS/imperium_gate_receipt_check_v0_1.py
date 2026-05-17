#!/usr/bin/env python3
"""Validate sample gatepack contract and emit gate receipt check report."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REGISTRY_PATH = Path("ORGANS/DOCTRINARIUM/GATES/GATE_REGISTRY_V0_1.json")
GATEPACK_PATH = Path("ORGANS/DOCTRINARIUM/GATES/GATEPACKS/GATEPACK_TASK_SECOND_BRAIN_V07_VISUAL_BOUNDARY_CONTRACT_V0_1.json")
OUT_DIR = Path("ORGANS/ADMINISTRATUM/GATE_RECEIPTS")
OUT_JSON = OUT_DIR / "GATE_RECEIPT_CHECK_REPORT_V0_1.json"
OUT_MD = OUT_DIR / "GATE_RECEIPT_CHECK_REPORT_V0_1.md"

REQUIRED_FIELDS = [
    "task_id",
    "generated_at",
    "current_head",
    "source_registry",
    "source_registry_sha256",
    "task_purpose",
    "allowed_paths",
    "forbidden_paths",
    "required_gates",
    "expected_receipts",
    "stop_conditions",
    "gate_ack_required",
    "no_gate_ack_no_work",
    "gatepack_sha256",
]

MANDATORY_GATES = [
    "GATE-U00-GIT-TRUTH",
    "GATE-U01-ROLE-ACK",
    "GATE-U02-SCOPE-BOUNDARY",
    "GATE-U03-NO-FEATURE-DRIFT",
    "GATE-U04-EVIDENCE-RECEIPT",
    "GATE-U05-STOP-CONDITIONS",
    "GATE-U08-REPO-PURITY",
    "GATE-U09-NO-FAKE-GREEN",
    "GATE-UI00-TRUTH-BINDING",
    "GATE-VIS00-PERFORMANCE-BUDGET",
    "GATE-VIS01-DECORATIVE-SEMANTIC-SPLIT",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def add_check(checks: list[dict], name: str, ok: bool, detail: str) -> None:
    checks.append({"check": name, "ok": ok, "detail": detail})


def main() -> int:
    repo_root = Path.cwd()
    if not (repo_root / ".git").exists():
        raise SystemExit("Run from repository root.")

    checks: list[dict] = []

    try:
        registry = load_json(REGISTRY_PATH)
        add_check(checks, "registry_json_parses", True, "Registry JSON parsed.")
    except Exception as exc:  # noqa: BLE001
        registry = {}
        add_check(checks, "registry_json_parses", False, f"Failed to parse registry: {exc}")

    try:
        gatepack = load_json(GATEPACK_PATH)
        add_check(checks, "gatepack_json_parses", True, "Gatepack JSON parsed.")
    except Exception as exc:  # noqa: BLE001
        gatepack = {}
        add_check(checks, "gatepack_json_parses", False, f"Failed to parse gatepack: {exc}")

    missing_fields = [field for field in REQUIRED_FIELDS if field not in gatepack]
    add_check(
        checks,
        "gatepack_required_fields",
        len(missing_fields) == 0,
        "All required fields present." if not missing_fields else f"Missing fields: {', '.join(missing_fields)}",
    )

    registry_gate_ids = {item.get("gate_id") for item in registry.get("gates", []) if isinstance(item, dict)}
    required_gates = gatepack.get("required_gates", [])
    if not isinstance(required_gates, list):
        required_gates = []

    missing_in_registry = [gid for gid in required_gates if gid not in registry_gate_ids]
    add_check(
        checks,
        "gatepack_gates_exist_in_registry",
        len(missing_in_registry) == 0,
        "All referenced gates exist in registry." if not missing_in_registry else f"Missing in registry: {', '.join(missing_in_registry)}",
    )

    missing_mandatory = [gid for gid in MANDATORY_GATES if gid not in required_gates]
    add_check(
        checks,
        "mandatory_gates_present",
        len(missing_mandatory) == 0,
        "All mandatory gates present." if not missing_mandatory else f"Missing mandatory gates: {', '.join(missing_mandatory)}",
    )

    add_check(
        checks,
        "gate_ack_required_true",
        gatepack.get("gate_ack_required") is True,
        "gate_ack_required must be true.",
    )
    add_check(
        checks,
        "no_gate_ack_no_work_true",
        gatepack.get("no_gate_ack_no_work") is True,
        "no_gate_ack_no_work must be true.",
    )

    expected_receipts = gatepack.get("expected_receipts", [])
    stop_conditions = gatepack.get("stop_conditions", [])
    add_check(
        checks,
        "expected_receipts_not_empty",
        isinstance(expected_receipts, list) and len(expected_receipts) > 0,
        "expected_receipts must be a non-empty list.",
    )
    add_check(
        checks,
        "stop_conditions_not_empty",
        isinstance(stop_conditions, list) and len(stop_conditions) > 0,
        "stop_conditions must be a non-empty list.",
    )

    verdict = "PASS" if all(item["ok"] for item in checks) else "FAIL"
    current_head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()

    report = {
        "generated_at": now_utc(),
        "current_head": current_head,
        "registry_path": str(REGISTRY_PATH).replace("\\", "/"),
        "gatepack_path": str(GATEPACK_PATH).replace("\\", "/"),
        "checks": checks,
        "summary": {
            "total": len(checks),
            "passed": sum(1 for item in checks if item["ok"]),
            "failed": sum(1 for item in checks if not item["ok"]),
        },
        "verdict": verdict,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# GATE RECEIPT CHECK REPORT V0.1",
        "",
        f"- generated_at: `{report['generated_at']}`",
        f"- current_head: `{report['current_head']}`",
        f"- registry_path: `{report['registry_path']}`",
        f"- gatepack_path: `{report['gatepack_path']}`",
        f"- verdict: `{report['verdict']}`",
        "",
        "| Check | Result | Detail |",
        "|---|---|---|",
    ]
    for item in checks:
        lines.append(f"| {item['check']} | {'PASS' if item['ok'] else 'FAIL'} | {item['detail']} |")
    lines.extend(
        [
            "",
            f"- total_checks: {report['summary']['total']}",
            f"- passed: {report['summary']['passed']}",
            f"- failed: {report['summary']['failed']}",
        ]
    )
    OUT_MD.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    print(str(OUT_JSON))
    print(str(OUT_MD))
    return 0 if verdict == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
