#!/usr/bin/env python3
"""Build a sample Gatepack V0.1 from Gate Registry V0.1."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REGISTRY_PATH = Path("ORGANS/DOCTRINARIUM/GATES/GATE_REGISTRY_V0_1.json")
OUT_DIR = Path("ORGANS/DOCTRINARIUM/GATES/GATEPACKS")
OUT_JSON = OUT_DIR / "GATEPACK_TASK_SECOND_BRAIN_V07_VISUAL_BOUNDARY_CONTRACT_V0_1.json"
OUT_MD = OUT_DIR / "GATEPACK_TASK_SECOND_BRAIN_V07_VISUAL_BOUNDARY_CONTRACT_V0_1.md"

TASK_ID = "TASK-SECOND-BRAIN-V07-VISUAL-BOUNDARY-CONTRACT"
REQUIRED_GATES = [
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


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    repo_root = Path.cwd()
    if not (repo_root / ".git").exists():
        raise SystemExit("Run from repository root.")

    if not REGISTRY_PATH.exists():
        raise SystemExit(f"Missing registry file: {REGISTRY_PATH}")

    registry_raw = REGISTRY_PATH.read_bytes()
    registry = load_json(REGISTRY_PATH)
    gate_ids = {g.get("gate_id") for g in registry.get("gates", []) if isinstance(g, dict)}

    missing = [gid for gid in REQUIRED_GATES if gid not in gate_ids]
    if missing:
        raise SystemExit(f"Registry missing required gates: {missing}")

    payload = {
        "task_id": TASK_ID,
        "generated_at": now_utc(),
        "current_head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "source_registry": str(REGISTRY_PATH).replace("\\", "/"),
        "source_registry_sha256": sha256_bytes(registry_raw),
        "task_purpose": "Define strict visual-boundary contract admission for Second Brain V0.7 follow-up task.",
        "allowed_paths": [
            "ORGANS/DOCTRINARIUM/GATES/",
            "ORGANS/OFFICIO_AGENTIS/RESPONSE_CONTRACTS/",
            "ORGANS/MECHANICUS/SCRIPTORIUM/GATE_RUNNERS/",
            "ORGANS/ADMINISTRATUM/GATE_RECEIPTS/",
            "ORGANS/ADMINISTRATUM/REPORTS/",
            "ORGANS/INQUISITION/GATE_AUDITS/",
        ],
        "forbidden_paths": [
            "IMPERIUM_TEST_VERSION/SECOND_BRAIN/",
            "KILO_TEST/",
            ".kilo/",
            "SANCTUM/",
            "RUNTIME/",
            "MEMORY_ZONES/",
            "any app/server/js/css/html runtime files",
            "visual assets/screenshots/zip files",
        ],
        "required_gates": REQUIRED_GATES,
        "expected_receipts": [
            "git_truth_receipt",
            "scope_boundary_receipt",
            "gate_ack_receipt",
            "before_after_receipt",
            "truth_binding_receipt",
            "performance_receipt_if_claimed",
        ],
        "stop_conditions": [
            "HEAD mismatch from expected task start hash.",
            "Forbidden path appears in diff.",
            "No-delete or no-runtime-mutation law would be violated.",
            "Evidence receipts cannot be produced for a PASS claim.",
        ],
        "gate_ack_required": True,
        "no_gate_ack_no_work": True,
    }

    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    payload["gatepack_sha256"] = sha256_bytes(canonical)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Sample Gatepack V0.1",
        "",
        f"- task_id: `{payload['task_id']}`",
        f"- generated_at: `{payload['generated_at']}`",
        f"- current_head: `{payload['current_head']}`",
        f"- source_registry: `{payload['source_registry']}`",
        f"- source_registry_sha256: `{payload['source_registry_sha256']}`",
        f"- gatepack_sha256: `{payload['gatepack_sha256']}`",
        f"- gate_ack_required: `{payload['gate_ack_required']}`",
        f"- no_gate_ack_no_work: `{payload['no_gate_ack_no_work']}`",
        "",
        "## Required Gates",
    ]
    for gate_id in payload["required_gates"]:
        lines.append(f"- `{gate_id}`")
    lines.extend(["", "## Allowed Paths"])
    for path in payload["allowed_paths"]:
        lines.append(f"- `{path}`")
    lines.extend(["", "## Forbidden Paths"])
    for path in payload["forbidden_paths"]:
        lines.append(f"- `{path}`")
    lines.extend(["", "## Expected Receipts"])
    for receipt in payload["expected_receipts"]:
        lines.append(f"- `{receipt}`")
    lines.extend(["", "## Stop Conditions"])
    for condition in payload["stop_conditions"]:
        lines.append(f"- {condition}")

    OUT_MD.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    print(str(OUT_JSON))
    print(str(OUT_MD))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
