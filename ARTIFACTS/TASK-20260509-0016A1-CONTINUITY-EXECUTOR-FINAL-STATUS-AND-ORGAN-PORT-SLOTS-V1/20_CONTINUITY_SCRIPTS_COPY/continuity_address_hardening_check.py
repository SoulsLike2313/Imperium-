#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List

from continuity_common import now_utc, write_json, write_text, has_latest_pattern


REQUIRED_ROOTS = [
    {
        "id": "IMPERIUM_ROOT",
        "relative": ".",
        "path_type": "root",
        "allowed_use": "Primary local workspace root.",
        "blocked_use": "No THRONE transfer and no unknown path redirection.",
        "critical": True,
    },
    {
        "id": "ARTIFACTS_ROOT",
        "relative": "ARTIFACTS",
        "path_type": "artifact_root",
        "allowed_use": "Task artifacts and continuity packs.",
        "blocked_use": "Do not mix manual proofs into normal artifact layer.",
        "critical": True,
    },
    {
        "id": "MANUAL_PROOFS_ROOT",
        "relative": "ARTIFACTS/_MANUAL_PROOFS",
        "path_type": "manual_proof_root",
        "allowed_use": "OWNER_MANUAL proof layer.",
        "blocked_use": "Do not treat as normal generated artifacts.",
        "critical": False,
    },
    {
        "id": "SSH_COMMAND_LIBRARY_ROOT",
        "relative": "SSH_COMMAND_LIBRARY",
        "path_type": "command_library",
        "allowed_use": "SSH routing context and tools registry layers.",
        "blocked_use": "No raw secrets in generated continuity pack.",
        "critical": True,
    },
    {
        "id": "TOOLS_ROOT",
        "relative": "SSH_COMMAND_LIBRARY/06_TOOLS",
        "path_type": "tools_root",
        "allowed_use": "Cemented tool root.",
        "blocked_use": "Active tools outside this root are hygiene warnings.",
        "critical": True,
    },
    {
        "id": "CONTINUITY_TOOLS_ROOT",
        "relative": "SSH_COMMAND_LIBRARY/06_TOOLS/20_CONTINUITY",
        "path_type": "continuity_tools",
        "allowed_use": "Continuity subsystem scripts.",
        "blocked_use": "No watcher/daemon behavior.",
        "critical": True,
    },
    {
        "id": "PC_VM2_PIPELINE_ROOT",
        "relative": "SSH_COMMAND_LIBRARY/06_TOOLS/10_PC_VM2_PIPELINE",
        "path_type": "pipeline_tools",
        "allowed_use": "PC-VM2 pipeline scripts registry.",
        "blocked_use": "No live VM2 actions in this task.",
        "critical": False,
    },
    {
        "id": "REGISTRY_ROOT",
        "relative": "SSH_COMMAND_LIBRARY/06_TOOLS/00_REGISTRY",
        "path_type": "registry_root",
        "allowed_use": "Tool index and layout contracts.",
        "blocked_use": "Do not mark unknown tools as active.",
        "critical": False,
    },
]


def evaluate_path(path: Path, critical: bool) -> str:
    if not path.exists():
        return "BLOCKED" if critical else "UNKNOWN"
    text = str(path)
    if has_latest_pattern(text):
        return "BLOCKED"
    lowered = text.lower()
    if "verify_extract" in lowered or "temp" in lowered:
        return "WARNING"
    if "throne" in lowered:
        return "BLOCKED"
    return "PASS"


def main() -> int:
    parser = argparse.ArgumentParser(description="Continuity address hardening check")
    parser.add_argument("--imperium-root", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    root = Path(args.imperium_root).resolve()
    records: List[Dict[str, Any]] = []
    findings: List[Dict[str, str]] = []
    critical_blocked = False

    for spec in REQUIRED_ROOTS:
        rel = spec["relative"]
        p = root if rel == "." else (root / rel)
        status = evaluate_path(p, bool(spec["critical"]))
        if status == "BLOCKED" and spec["critical"]:
            critical_blocked = True
        records.append(
            {
                "root_id": spec["id"],
                "exists": p.exists(),
                "absolute_path": str(p),
                "path_type": spec["path_type"],
                "allowed_use": spec["allowed_use"],
                "blocked_use": spec["blocked_use"],
                "status": status,
            }
        )

    artifacts_root = root / "ARTIFACTS"
    manual_root = artifacts_root / "_MANUAL_PROOFS"
    if artifacts_root.exists():
        for child in artifacts_root.iterdir():
            if child.is_dir() and child.name != "_MANUAL_PROOFS" and "MANUAL" in child.name.upper():
                findings.append(
                    {
                        "type": "manual_artifact_outside_manual_layer",
                        "path": str(child),
                        "status": "WARNING",
                        "note": "Manual-looking folder is outside _MANUAL_PROOFS layer.",
                    }
                )

    tools_root = root / "SSH_COMMAND_LIBRARY" / "06_TOOLS"
    if tools_root.exists():
        top_tools = root / "SSH_COMMAND_LIBRARY"
        for file_name in ("send_prompt_to_vm2.py", "fetch_vm2_stage_bundle.py"):
            p = top_tools / file_name
            if p.exists():
                findings.append(
                    {
                        "type": "active_tool_outside_tools_root",
                        "path": str(p),
                        "status": "WARNING",
                        "note": "Legacy script path exists outside cemented 06_TOOLS root.",
                    }
                )

    verdict = "PASS"
    if critical_blocked:
        verdict = "BLOCKED"
    elif any(r["status"] in {"WARNING", "UNKNOWN"} for r in records) or findings:
        verdict = "WARNING"

    payload = {
        "generated_at_utc": now_utc(),
        "imperium_root": str(root),
        "manual_proofs_root": str(manual_root),
        "roots": records,
        "findings": findings,
        "verdict": verdict,
        "no_vm2_contact": True,
        "no_real_e2e": True,
        "no_throne": True,
        "no_watchers": True,
        "no_latest": True,
    }

    write_json(Path(args.output_json), payload)

    lines = [
        "# 0016A ADDRESS HARDENING REPORT",
        "",
        f"generated_at_utc: {payload['generated_at_utc']}",
        f"imperium_root: {payload['imperium_root']}",
        "",
        "## Roots",
    ]
    for rec in records:
        lines.append(f"- {rec['root_id']}: status={rec['status']} exists={str(rec['exists']).lower()} path={rec['absolute_path']}")
    lines.append("")
    lines.append("## Findings")
    if findings:
        for f in findings:
            lines.append(f"- {f['type']}: status={f['status']} path={f['path']} note={f['note']}")
    else:
        lines.append("- NONE")
    lines.append("")
    lines.append(f"verdict: {verdict}")
    write_text(Path(args.output_md), "\n".join(lines))

    print(f"continuity_address_hardening_check: verdict={verdict} output={args.output_json}")
    return 0 if verdict in {"PASS", "WARNING"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
