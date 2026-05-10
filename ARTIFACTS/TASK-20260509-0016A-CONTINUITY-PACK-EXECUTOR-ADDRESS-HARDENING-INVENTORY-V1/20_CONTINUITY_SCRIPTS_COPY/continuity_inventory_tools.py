#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List

from continuity_common import compile_py_files, now_utc, read_json_safe, sha256_file, write_json, write_text

KNOWN_CLASSES = [
    "00_REGISTRY",
    "01_CORE_LIB",
    "10_PC_VM2_PIPELINE",
    "15_STAGE_COORDINATION",
    "20_CONTINUITY",
    "30_BUNDLE_VALIDATION",
    "40_OWNER_MANUAL",
    "50_READONLY_EXPLORER",
    "60_SANCTUM_PREP",
    "90_LEGACY_QUARANTINE",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory tools and registry status")
    parser.add_argument("--imperium-root", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    root = Path(args.imperium_root).resolve()
    tools_root = root / "SSH_COMMAND_LIBRARY" / "06_TOOLS"

    class_records: List[Dict[str, Any]] = []
    py_files: List[Path] = []
    for cls in KNOWN_CLASSES:
        p = tools_root / cls
        scripts = sorted([x for x in p.rglob("*.py")]) if p.exists() else []
        py_files.extend(scripts)
        class_records.append(
            {
                "tool_class": cls,
                "path": str(p),
                "exists": p.exists(),
                "script_count": len(scripts),
            }
        )

    compiled_ok, compile_errors = compile_py_files(py_files)

    registry_path = tools_root / "00_REGISTRY" / "TOOLS_MASTER_INDEX.json"
    registry_status: Dict[str, Any] = {
        "registry_path": str(registry_path),
        "exists": registry_path.exists(),
        "parse_error": None,
        "total_tools": 0,
        "active_tools": 0,
        "placeholder_tools": 0,
        "hash_checked_count": 0,
        "hash_mismatch_count": 0,
        "missing_active_files": 0,
    }
    mismatches: List[Dict[str, Any]] = []

    if registry_path.exists():
        data, err = read_json_safe(registry_path)
        if err:
            registry_status["parse_error"] = err
        else:
            entries = data.get("tools", []) if isinstance(data, dict) else []
            registry_status["total_tools"] = len(entries)
            for e in entries:
                status = str(e.get("status", "")).upper()
                if status in {"ACTIVE", "ACTIVE_NEEDS_SPECULUM", "ACTIVE_LOCAL_DRYRUN_ONLY"}:
                    registry_status["active_tools"] += 1
                if status in {"PLACEHOLDER_CONTRACT", "LEGACY_CANDIDATE", "LEGACY_QUARANTINE"}:
                    registry_status["placeholder_tools"] += 1

                if status in {"ACTIVE", "ACTIVE_NEEDS_SPECULUM", "ACTIVE_LOCAL_DRYRUN_ONLY"}:
                    path = e.get("absolute_path")
                    if not path:
                        registry_status["missing_active_files"] += 1
                        continue
                    fp = Path(path)
                    if not fp.exists():
                        registry_status["missing_active_files"] += 1
                        continue
                    registry_status["hash_checked_count"] += 1
                    expected = str(e.get("sha256", "")).lower()
                    got = sha256_file(fp)
                    if expected and expected != got:
                        registry_status["hash_mismatch_count"] += 1
                        mismatches.append(
                            {
                                "tool_id": e.get("tool_id"),
                                "path": str(fp),
                                "expected": expected,
                                "actual": got,
                            }
                        )

    verdict = "PASS"
    if not registry_status["exists"] or registry_status["parse_error"]:
        verdict = "PARTIAL"
    if registry_status["hash_mismatch_count"] > 0 or registry_status["missing_active_files"] > 0:
        verdict = "PARTIAL"

    payload = {
        "generated_at_utc": now_utc(),
        "tools_root": str(tools_root),
        "classes": class_records,
        "python_compile": {
            "checked_files": len(py_files),
            "compiled_ok": compiled_ok,
            "compile_error_count": len(compile_errors),
            "compile_errors": compile_errors,
        },
        "registry_status": registry_status,
        "registry_mismatches": mismatches,
        "verdict": verdict,
    }

    write_json(Path(args.output_json), payload)

    lines = [
        "# 0016A TOOLS INVENTORY",
        "",
        f"generated_at_utc: {payload['generated_at_utc']}",
        f"tools_root: {payload['tools_root']}",
        "",
        "## Classes",
    ]
    for c in class_records:
        lines.append(f"- {c['tool_class']}: exists={str(c['exists']).lower()} script_count={c['script_count']}")
    lines.extend(
        [
            "",
            "## Registry",
            f"- exists: {str(registry_status['exists']).lower()}",
            f"- total_tools: {registry_status['total_tools']}",
            f"- active_tools: {registry_status['active_tools']}",
            f"- placeholder_tools: {registry_status['placeholder_tools']}",
            f"- hash_mismatch_count: {registry_status['hash_mismatch_count']}",
            f"- missing_active_files: {registry_status['missing_active_files']}",
            "",
            f"verdict: {verdict}",
        ]
    )
    write_text(Path(args.output_md), "\n".join(lines))

    print(f"continuity_inventory_tools: scripts={len(py_files)} verdict={verdict}")
    return 0 if verdict in {"PASS", "PARTIAL"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
