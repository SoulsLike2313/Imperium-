#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path
from typing import Any, Dict, List

from continuity_common import (
    create_sha256s_file,
    now_utc,
    path_hygiene_stats,
    read_json_safe,
    remove_generated_caches,
    sha256_file,
    write_json,
    write_text,
)


def load_json(path: Path) -> Dict[str, Any]:
    data, err = read_json_safe(path)
    if err or data is None:
        raise ValueError(f"failed_to_read_json:{path}:{err}")
    return data


def copy_if_exists(src: Path, dst: Path) -> bool:
    if not src.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(src.read_bytes())
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Build continuity pack from step outputs")
    parser.add_argument("--imperium-root", required=True)
    parser.add_argument("--task-root", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-pack-dir", required=True)
    parser.add_argument("--step-data-dir", required=True)
    parser.add_argument("--step-receipts-dir", required=True)
    parser.add_argument("--executor-receipt", required=False)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    imperium_root = Path(args.imperium_root).resolve()
    task_root = Path(args.task_root).resolve()
    pack_dir = Path(args.output_pack_dir).resolve()
    step_data_dir = Path(args.step_data_dir).resolve()
    step_receipts_dir = Path(args.step_receipts_dir).resolve()

    pack_dir.mkdir(parents=True, exist_ok=True)
    remove_generated_caches(pack_dir)

    inputs = {
        "address": load_json(step_data_dir / "address_hardening.json"),
        "artifacts": load_json(step_data_dir / "artifacts_inventory.json"),
        "manual": load_json(step_data_dir / "manual_proofs_inventory.json"),
        "tools": load_json(step_data_dir / "tools_inventory.json"),
        "tasks": load_json(step_data_dir / "tasks_inventory.json"),
        "receipts": load_json(step_data_dir / "receipts_scan.json"),
        "ledgers": load_json(step_data_dir / "ledgers_scan.json"),
        "blockers": load_json(step_data_dir / "known_blockers.json"),
    }

    # Copy core JSON artifacts
    write_json(pack_dir / "ADDRESS_MAP.json", inputs["address"])
    write_json(pack_dir / "ARTIFACTS_INVENTORY.json", inputs["artifacts"])
    write_json(pack_dir / "MANUAL_PROOFS_INVENTORY.json", inputs["manual"])
    write_json(pack_dir / "TOOLS_INVENTORY.json", inputs["tools"])
    write_json(pack_dir / "TASKS_INVENTORY.json", inputs["tasks"])
    write_json(pack_dir / "RECEIPTS_INDEX.json", inputs["receipts"])
    write_json(pack_dir / "LEDGER_INDEX.json", inputs["ledgers"])
    write_json(pack_dir / "REGISTRY_STATUS.json", inputs["tools"].get("registry_status", {}))

    # Markdown copies / generated
    address_md_src = step_data_dir / "address_hardening.md"
    if not copy_if_exists(address_md_src, pack_dir / "ADDRESS_MAP.md"):
        write_text(pack_dir / "ADDRESS_MAP.md", "# ADDRESS_MAP\n\nMissing step markdown; see ADDRESS_MAP.json")

    blockers = inputs["blockers"].get("blockers", [])
    known_blockers_md = ["# KNOWN_BLOCKERS", ""]
    if blockers:
        for b in blockers:
            known_blockers_md.append(
                f"- {b.get('blocker_id')} [{b.get('severity')}]: {b.get('message')} | evidence={b.get('evidence_path')}"
            )
    else:
        known_blockers_md.append("- NONE")
    write_text(pack_dir / "KNOWN_BLOCKERS.md", "\n".join(known_blockers_md))

    # Metrics
    artifact_records = inputs["artifacts"].get("records", [])
    manual_records = inputs["manual"].get("records", [])
    task_records = inputs["tasks"].get("records", [])
    receipts_count = int(inputs["receipts"].get("receipts_count", 0))
    ledger_files_count = int(inputs["ledgers"].get("ledger_files_count", 0))

    bundles_count = sum(1 for r in artifact_records if r.get("has_zip_bundle")) + sum(1 for r in manual_records if r.get("has_zip"))
    sha256_sidecars_count = sum(1 for r in artifact_records if r.get("has_sha256")) + sum(1 for r in manual_records if r.get("has_zip_sha256"))
    manifests_count = sum(1 for r in artifact_records if r.get("has_manifest_json")) + sum(1 for r in manual_records if r.get("has_manifest"))
    owner_reports_count = len([x for x in inputs["receipts"].get("records", []) if "OWNER_SUMMARY" in (x.get("file_name") or "") or "AGENT_FINAL_RESPONSE" in (x.get("file_name") or "")])

    active_tools_count = int(inputs["tools"].get("registry_status", {}).get("active_tools", 0))
    registry_hash_mismatch_count = int(inputs["tools"].get("registry_status", {}).get("hash_mismatch_count", 0))

    addr_findings = inputs["address"].get("findings", [])
    manual_wrong_layer = sum(1 for f in addr_findings if f.get("type") == "manual_artifact_outside_manual_layer")
    latest_findings = sum(1 for f in addr_findings if "latest" in str(f.get("type", "")).lower() or "latest" in str(f.get("note", "")).lower())

    pycache_count = len([p for p in (imperium_root / "SSH_COMMAND_LIBRARY" / "06_TOOLS").rglob("__pycache__") if p.is_dir()])
    pycache_count += len([p for p in (imperium_root / "SSH_COMMAND_LIBRARY" / "06_TOOLS").rglob("*.pyc") if p.is_file()])
    pycache_count += len([p for p in (imperium_root / "SSH_COMMAND_LIBRARY" / "06_TOOLS").rglob("*.pyo") if p.is_file()])

    unknown_status_count = sum(1 for r in artifact_records if r.get("status_guess") == "UNKNOWN") + sum(1 for r in manual_records if (r.get("evidence_verdict") or "").upper() == "UNKNOWN")
    blocked_tasks_count = sum(1 for r in artifact_records if r.get("status_guess") == "BLOCKED")
    repair_required_count = sum(1 for r in artifact_records if r.get("status_guess") == "REPAIR_REQUIRED")

    manual_probe_records = [r for r in manual_records if r.get("scope") == "MANUAL_PROBE"]
    manual_probe_records.sort(key=lambda x: x.get("modified_time", 0), reverse=True)
    last_manual_probe_task = manual_probe_records[0].get("task_id") if manual_probe_records else None

    runtime_records = [r for r in artifact_records if r.get("detected_task_id")]
    runtime_records.sort(key=lambda x: x.get("modified_time", 0), reverse=True)
    last_runtime_task = runtime_records[0].get("detected_task_id") if runtime_records else None

    known_blockers_count = len(blockers)
    next_task = inputs["blockers"].get("recommended_next_task_id") or "NEEDS_OWNER_CONFIRMATION"

    address_verdict = str(inputs["address"].get("verdict", "WARNING"))
    continuity_verdict = "CONTINUITY_GREEN"
    if address_verdict == "BLOCKED":
        continuity_verdict = "CONTINUITY_RED"
    elif known_blockers_count > 0 or repair_required_count > 0 or registry_hash_mismatch_count > 0 or unknown_status_count > 0:
        continuity_verdict = "CONTINUITY_YELLOW"

    metrics = {
        "artifact_folders_count": len(artifact_records),
        "manual_proof_folders_count": len(manual_records),
        "task_folders_count": len(task_records),
        "bundles_count": bundles_count,
        "sha256_sidecars_count": sha256_sidecars_count,
        "manifests_count": manifests_count,
        "receipts_count": receipts_count,
        "owner_reports_count": owner_reports_count,
        "ledger_files_count": ledger_files_count,
        "active_tools_count": active_tools_count,
        "registry_hash_mismatch_count": registry_hash_mismatch_count,
        "manual_artifacts_in_wrong_layer_count": manual_wrong_layer,
        "latest_path_findings_count": latest_findings,
        "pycache_findings_count": pycache_count,
        "unknown_status_count": unknown_status_count,
        "blocked_tasks_count": blocked_tasks_count,
        "repair_required_count": repair_required_count,
        "known_blockers_count": known_blockers_count,
        "last_detected_manual_probe_task_id": last_manual_probe_task,
        "last_detected_runtime_task_id": last_runtime_task,
        "next_recommended_task_id": next_task,
        "continuity_verdict": continuity_verdict,
    }
    write_json(pack_dir / "METRICS.json", metrics)

    # State / next steps / summary
    current_state = [
        "# CURRENT_STATE",
        "",
        f"continuity_verdict: {continuity_verdict}",
        f"address_verdict: {address_verdict}",
        f"known_blockers_count: {known_blockers_count}",
        f"artifact_folders_count: {len(artifact_records)}",
        f"manual_proof_folders_count: {len(manual_records)}",
        f"active_tools_count: {active_tools_count}",
        "",
        "Manual proofs are inventoried as OWNER_MANUAL_PROOF layer, separate from generated artifacts.",
    ]
    write_text(pack_dir / "CURRENT_STATE.md", "\n".join(current_state))

    next_steps = [
        "# NEXT_STEPS",
        "",
        f"recommended_next_task_id: {next_task}",
        "",
        "1. Keep VM2/E2E blocked until required prerequisites are closed.",
        "2. Resolve stage-id schema mismatch before new pipeline claims.",
        "3. Run Speculum hard review for continuity executor base.",
    ]
    write_text(pack_dir / "NEXT_STEPS.md", "\n".join(next_steps))

    owner_summary = [
        "# CONTINUITY_OWNER_SUMMARY",
        "",
        f"continuity_verdict: {continuity_verdict}",
        f"known_blockers_count: {known_blockers_count}",
        f"manual_proof_folders_count: {len(manual_records)}",
        f"next_recommended_task_id: {next_task}",
        "",
        "This continuity pack is generated from filesystem evidence, not from narrative memory.",
    ]
    write_text(pack_dir / "CONTINUITY_OWNER_SUMMARY.md", "\n".join(owner_summary))

    # Copy executor receipt if already present
    executor_receipt_path = Path(args.executor_receipt) if args.executor_receipt else None
    if executor_receipt_path and executor_receipt_path.exists():
        copy_if_exists(executor_receipt_path, pack_dir / "EXECUTOR_RUN_RECEIPT.json")
    else:
        write_json(
            pack_dir / "EXECUTOR_RUN_RECEIPT.json",
            {
                "task_id": task_root.name,
                "run_id": args.run_id,
                "status": "PENDING_FINALIZATION",
                "created_at_utc": now_utc(),
            },
        )

    # Copy step receipts and reports
    step_receipts_out = pack_dir / "STEP_RECEIPTS"
    step_reports_out = pack_dir / "STEP_REPORTS"
    step_receipts_out.mkdir(parents=True, exist_ok=True)
    step_reports_out.mkdir(parents=True, exist_ok=True)

    if step_receipts_dir.exists():
        for rec in step_receipts_dir.rglob("*.json"):
            target = step_receipts_out / rec.name
            target.write_bytes(rec.read_bytes())

    for report in sorted(step_data_dir.glob("*.md")):
        target = step_reports_out / report.name
        target.write_bytes(report.read_bytes())

    # Index
    index = {
        "task_id": task_root.name,
        "run_id": args.run_id,
        "created_at_utc": now_utc(),
        "continuity_verdict": continuity_verdict,
        "address_verdict": address_verdict,
        "known_blockers_count": known_blockers_count,
        "manual_layer_status": "SEPARATED",
        "paths": {
            "address_map": "ADDRESS_MAP.json",
            "artifacts_inventory": "ARTIFACTS_INVENTORY.json",
            "manual_proofs_inventory": "MANUAL_PROOFS_INVENTORY.json",
            "tools_inventory": "TOOLS_INVENTORY.json",
            "tasks_inventory": "TASKS_INVENTORY.json",
            "receipts_index": "RECEIPTS_INDEX.json",
            "ledger_index": "LEDGER_INDEX.json",
            "metrics": "METRICS.json",
            "known_blockers": "KNOWN_BLOCKERS.md",
        },
    }
    write_json(pack_dir / "CONTINUITY_INDEX.json", index)

    # Manifest + SHA256 for continuity pack folder
    files = sorted([p for p in pack_dir.rglob("*") if p.is_file()])
    manifest = {
        "task_id": task_root.name,
        "run_id": args.run_id,
        "created_at_utc": now_utc(),
        "file_count": len(files),
        "files": [p.relative_to(pack_dir).as_posix() for p in files],
        "control_files": ["MANIFEST.json", "SHA256SUMS.txt"],
        "control_hash_policy": {
            "sha256_includes_manifest": True,
            "sha256_includes_self": False,
            "path_style": "archive_relative_posix",
        },
    }
    write_json(pack_dir / "MANIFEST.json", manifest)
    create_sha256s_file(pack_dir, pack_dir / "SHA256SUMS.txt", exclude_names=["SHA256SUMS.txt"])

    # Build ZIP + sidecar at task root
    zip_path = task_root / "CONTINUITY_PACK.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file in sorted([p for p in pack_dir.rglob("*") if p.is_file()]):
            arcname = file.relative_to(pack_dir).as_posix()
            zf.write(file, arcname=arcname)

    zip_hash = sha256_file(zip_path)
    write_text(task_root / "CONTINUITY_PACK.zip.sha256", f"{zip_hash}  CONTINUITY_PACK.zip")

    # Path hygiene stats on zip names
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
    hygiene = path_hygiene_stats(names)

    out = {
        "generated_at_utc": now_utc(),
        "task_root": str(task_root),
        "continuity_pack_dir": str(pack_dir),
        "continuity_pack_zip": str(zip_path),
        "continuity_pack_zip_sha256": zip_hash,
        "zip_hygiene": hygiene,
        "metrics": metrics,
        "continuity_verdict": continuity_verdict,
        "verdict": "PASS" if continuity_verdict in {"CONTINUITY_GREEN", "CONTINUITY_YELLOW"} else "BLOCKED",
    }
    write_json(Path(args.output_json), out)

    md = [
        "# 0016A CONTINUITY PACK BUILD REPORT",
        "",
        f"generated_at_utc: {out['generated_at_utc']}",
        f"continuity_pack_dir: {out['continuity_pack_dir']}",
        f"continuity_pack_zip: {out['continuity_pack_zip']}",
        f"continuity_pack_zip_sha256: {zip_hash}",
        f"continuity_verdict: {continuity_verdict}",
        f"zip_hygiene: {hygiene}",
        f"verdict: {out['verdict']}",
    ]
    write_text(Path(args.output_md), "\n".join(md))

    print(f"continuity_pack_build: continuity_verdict={continuity_verdict} zip={zip_path}")
    return 0 if out["verdict"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
