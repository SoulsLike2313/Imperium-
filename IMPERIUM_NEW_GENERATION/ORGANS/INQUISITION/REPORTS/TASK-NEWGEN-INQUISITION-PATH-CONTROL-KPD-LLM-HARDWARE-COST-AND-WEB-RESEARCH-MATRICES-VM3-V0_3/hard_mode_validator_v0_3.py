#!/usr/bin/env python3
"""Validate the TASK V0_3 hard-mode cost matrix report pack."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

TASK_ID = "TASK-NEWGEN-INQUISITION-PATH-CONTROL-KPD-LLM-HARDWARE-COST-AND-WEB-RESEARCH-MATRICES-VM3-V0_3"
REQUIRED_FILES = [
    "matrix_spine_hard_mode_cost_v0_3.md",
    "matrix_spine_hard_mode_cost_v0_3.json",
    "local_step_matrix_v0_3.schema.json",
    "global_caps_carry_matrix_v0_3.schema.json",
    "kpd_efficiency_matrix_v0_3.schema.json",
    "llm_cost_context_output_matrix_v0_3.schema.json",
    "hardware_local_agent_cost_matrix_v0_3.schema.json",
    "web_research_cost_source_quality_matrix_v0_3.schema.json",
    "fake_cost_saving_matrix_v0_3.schema.json",
    "matrix_strength_comparison_v0_3.md",
    "hard_mode_validator_v0_3.py",
    "web_research_summary.md",
    "web_research_sources.json",
    "web_research_dossier.zip",
    "pc_transfer_receipt.json",
    "vm2_next_task_handoff_note.md",
    "cost_scoreboard_receipt.json",
    "artifact_retention_gate_receipt.json",
    "final_owner_summary_ru.md",
    "commit_push_receipt.json",
]
SCHEMA_IDS = [
    "local_step_matrix_v0_3",
    "global_caps_carry_matrix_v0_3",
    "kpd_efficiency_matrix_v0_3",
    "llm_cost_context_output_matrix_v0_3",
    "hardware_local_agent_cost_matrix_v0_3",
    "web_research_cost_source_quality_matrix_v0_3",
    "fake_cost_saving_matrix_v0_3",
]
EXAMPLE_FILES = [
    "examples/local_pass_global_caps_carried.example.json",
    "examples/local_fail_exact_gates.example.json",
    "examples/cost_improvement_pass.example.json",
    "examples/fake_cost_saving_fail.example.json",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-dir", required=True)
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()

    started = time.perf_counter()
    report_dir = Path(args.report_dir)
    checks = []
    failures = []
    warnings = []

    for rel in REQUIRED_FILES:
        path = report_dir / rel
        ok = path.exists() and path.stat().st_size > 0
        checks.append({"check_id": f"FILE:{rel}", "status": "PASS" if ok else "FAIL"})
        if not ok:
            failures.append(f"missing_or_empty:{rel}")

    pack = load_json(report_dir / "matrix_spine_hard_mode_cost_v0_3.json")
    if pack.get("task_id") != TASK_ID:
        failures.append("matrix_pack_task_id_mismatch")
    for schema_id in SCHEMA_IDS:
        schema_path = report_dir / f"{schema_id}.schema.json"
        schema = load_json(schema_path)
        matrix_key = schema_id.replace("_v0_3", "")
        if schema.get("properties", {}).get("matrix_id", {}).get("const") != schema_id:
            failures.append(f"schema_const_mismatch:{schema_id}")
        found = pack.get(matrix_key) or pack.get(schema_id)
        if not found:
            failures.append(f"matrix_missing_in_pack:{schema_id}")
        elif found.get("matrix_id") != schema_id:
            failures.append(f"matrix_id_mismatch:{schema_id}")
        elif not found.get("items"):
            failures.append(f"matrix_items_empty:{schema_id}")

    sources = load_json(report_dir / "web_research_sources.json")
    official = [s for s in sources if str(s.get("trust_level", "")).startswith("PRIMARY")]
    if len(sources) < 12:
        failures.append("web_research_source_count_below_12")
    if len(official) < 8:
        failures.append("primary_source_count_below_8")

    fake = pack["fake_cost_saving_matrix"]["items"]
    required_traps = {"DROP_REQUIRED_RECEIPT", "SKIP_READ_FIRST", "NO_RESEARCH_CLAIM", "UNMEASURED_COST_AS_SAVING"}
    present_traps = {item.get("trap_id") for item in fake}
    missing_traps = sorted(required_traps - present_traps)
    if missing_traps:
        failures.append("fake_economy_traps_missing:" + ",".join(missing_traps))

    hardware = pack["hardware_local_agent_cost_matrix"]["items"]
    if not any(item.get("measurement_state") == "UNKNOWN_NOT_INSTRUMENTED" for item in hardware):
        warnings.append("no_unknown_not_instrumented_hardware_metric")

    for rel in EXAMPLE_FILES:
        path = report_dir / rel
        if not path.exists():
            failures.append(f"example_missing:{rel}")
        else:
            data = load_json(path)
            if "FAIL" in rel and data.get("final") != "FAIL":
                failures.append(f"example_fail_contract_wrong:{rel}")

    dossier = report_dir / "web_research_dossier.zip"
    if dossier.exists():
        with zipfile.ZipFile(dossier, "r") as zf:
            names = set(zf.namelist())
        for required in ["web_research_summary.md", "web_research_sources.json", "web_research_receipt.json"]:
            if required not in names:
                failures.append(f"dossier_missing:{required}")

    verdict = "PASS_WITH_WARNINGS" if not failures else "FAIL"
    receipt = {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "validator": "hard_mode_validator_v0_3.py",
        "report_dir": str(report_dir),
        "checks": checks,
        "failures": failures,
        "warnings": warnings,
        "source_count": len(sources),
        "primary_source_count": len(official),
        "wall_seconds": round(time.perf_counter() - started, 6),
        "validated_files": [
            {"path": rel, "sha256": sha256_file(report_dir / rel)}
            for rel in REQUIRED_FILES
            if (report_dir / rel).exists()
        ],
        "verdict": verdict,
        "clean_pass_allowed": False,
        "replay_state": "INQUISITOR_REPLAY_FOR_TARGET",
    }
    if args.write_receipt:
        (report_dir / "validator_run_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
