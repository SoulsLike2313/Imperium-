#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from continuity_common import (
    create_sha256s_file,
    now_utc,
    owner_report_text,
    read_json_safe,
    remove_generated_caches,
    write_json,
    write_text,
)

TASK_ID_DEFAULT = "TASK-20260509-0016A-CONTINUITY-PACK-EXECUTOR-ADDRESS-HARDENING-INVENTORY-V1"


def iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_command_live(cmd: List[str], cwd: Path) -> Tuple[int, List[str], List[str]]:
    proc = subprocess.Popen(
        cmd,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    out_lines: List[str] = []
    err_lines: List[str] = []

    assert proc.stdout is not None
    assert proc.stderr is not None

    while True:
        line = proc.stdout.readline()
        if line:
            text = line.rstrip("\n")
            out_lines.append(text)
            print(text)
        else:
            if proc.poll() is not None:
                break

    stderr_text = proc.stderr.read()
    if stderr_text:
        for line in stderr_text.splitlines():
            err_lines.append(line)
            print(line)

    rc = proc.wait()
    return rc, out_lines, err_lines


def load_verdict(path: Path) -> str:
    if not path.exists():
        return "UNKNOWN"
    data, err = read_json_safe(path)
    if err or not isinstance(data, dict):
        return "UNKNOWN"
    for key in ("final_verdict", "verdict", "continuity_verdict"):
        if key in data:
            return str(data[key])
    return "UNKNOWN"


def summarize_step_verdict(verdicts: List[str], rc_list: List[int]) -> str:
    up = [v.upper() for v in verdicts if v]
    if any(rc != 0 for rc in rc_list):
        if any(v in {"BLOCKED", "FAIL", "CONTINUITY_RED"} for v in up):
            return "BLOCKED"
        return "PARTIAL"
    if any(v in {"BLOCKED", "FAIL", "CONTINUITY_RED"} for v in up):
        return "BLOCKED"
    if any(v in {"PASS_AS_CONTINUITY_EXECUTOR_BASE", "PASS_AS_LOCAL_RUNTIME_PRIMITIVES"} for v in up):
        return "PASS"
    if any(v in {"PARTIAL", "WARNING", "CONTINUITY_YELLOW", "UNKNOWN"} for v in up):
        return "PARTIAL"
    return "PASS"


def copy_continuity_scripts(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.rglob("*"):
        if item.is_dir():
            continue
        rel = item.relative_to(src)
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, target)


def build_task_manifest(task_root: Path, task_id: str) -> None:
    files = sorted([p for p in task_root.rglob("*") if p.is_file()])
    manifest = {
        "task_id": task_id,
        "created_at_utc": now_utc(),
        "file_count": len(files),
        "files": [p.relative_to(task_root).as_posix() for p in files],
        "control_files": ["MANIFEST.json", "SHA256SUMS.txt"],
        "control_hash_policy": {
            "sha256_includes_manifest": True,
            "sha256_includes_self": False,
            "path_style": "archive_relative_posix",
        },
    }
    write_json(task_root / "MANIFEST.json", manifest)
    create_sha256s_file(task_root, task_root / "SHA256SUMS.txt", exclude_names=["SHA256SUMS.txt"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Run continuity pack executor with visible step flow")
    parser.add_argument("--imperium-root", required=True)
    parser.add_argument("--mode", default="manual-visible")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    args = parser.parse_args()

    imperium_root = Path(args.imperium_root).resolve()
    tools_root = imperium_root / "SSH_COMMAND_LIBRARY" / "06_TOOLS" / "20_CONTINUITY"
    task_root = imperium_root / "ARTIFACTS" / args.task_id

    reports_dir = task_root / "REPORTS"
    receipts_dir = task_root / "RECEIPTS"
    step_receipts_dir = receipts_dir / "STEP_RECEIPTS"
    step_reports_dir = reports_dir / "STEP_REPORTS"
    step_data_dir = reports_dir / "STEP_DATA"
    pack_dir = task_root / "CONTINUITY_PACK"

    for d in (task_root, reports_dir, receipts_dir, step_receipts_dir, step_reports_dir, step_data_dir, pack_dir, task_root / "20_CONTINUITY_SCRIPTS_COPY"):
        d.mkdir(parents=True, exist_ok=True)

    remove_generated_caches(task_root)

    run_id = f"RUN-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
    executor_receipt_path = receipts_dir / "EXECUTOR_RUN_RECEIPT.json"
    executor_receipt = {
        "task_id": args.task_id,
        "run_id": run_id,
        "started_at_utc": iso_now(),
        "mode": args.mode,
        "status": "RUNNING",
        "producer_type": "PC_SERVITOR",
        "no_vm2_contact": True,
        "no_real_e2e": True,
        "no_throne": True,
        "no_watchers": True,
        "no_latest": True,
        "steps": [],
    }
    write_json(executor_receipt_path, executor_receipt)

    steps: List[Dict[str, Any]] = [
        {
            "id": "STEP-001",
            "name": "Address hardening check",
            "purpose": "Validate stable roots and detect dirty address usage.",
            "commands": [
                {
                    "script": "continuity_address_hardening_check.py",
                    "args": [
                        "--imperium-root", str(imperium_root),
                        "--output-json", str(step_data_dir / "address_hardening.json"),
                        "--output-md", str(step_data_dir / "address_hardening.md"),
                    ],
                    "verdict_json": step_data_dir / "address_hardening.json",
                }
            ],
            "fatal": False,
            "outputs": [str(step_data_dir / "address_hardening.json"), str(step_data_dir / "address_hardening.md")],
        },
        {
            "id": "STEP-002",
            "name": "Artifact inventory",
            "purpose": "Inventory normal task artifacts under ARTIFACTS (excluding manual layer).",
            "commands": [
                {
                    "script": "continuity_inventory_artifacts.py",
                    "args": [
                        "--imperium-root", str(imperium_root),
                        "--output-json", str(step_data_dir / "artifacts_inventory.json"),
                        "--output-md", str(step_data_dir / "artifacts_inventory.md"),
                    ],
                    "verdict_json": step_data_dir / "artifacts_inventory.json",
                }
            ],
            "fatal": False,
            "outputs": [str(step_data_dir / "artifacts_inventory.json"), str(step_data_dir / "artifacts_inventory.md")],
        },
        {
            "id": "STEP-003",
            "name": "Manual proofs inventory",
            "purpose": "Inventory OWNER_MANUAL_PROOF layer separately.",
            "commands": [
                {
                    "script": "continuity_inventory_manual_proofs.py",
                    "args": [
                        "--imperium-root", str(imperium_root),
                        "--output-json", str(step_data_dir / "manual_proofs_inventory.json"),
                        "--output-md", str(step_data_dir / "manual_proofs_inventory.md"),
                    ],
                    "verdict_json": step_data_dir / "manual_proofs_inventory.json",
                }
            ],
            "fatal": False,
            "outputs": [str(step_data_dir / "manual_proofs_inventory.json"), str(step_data_dir / "manual_proofs_inventory.md")],
        },
        {
            "id": "STEP-004",
            "name": "Tools and tasks inventory",
            "purpose": "Inventory tools root, registry status, and task index.",
            "commands": [
                {
                    "script": "continuity_inventory_tools.py",
                    "args": [
                        "--imperium-root", str(imperium_root),
                        "--output-json", str(step_data_dir / "tools_inventory.json"),
                        "--output-md", str(step_data_dir / "tools_inventory.md"),
                    ],
                    "verdict_json": step_data_dir / "tools_inventory.json",
                },
                {
                    "script": "continuity_inventory_tasks.py",
                    "args": [
                        "--imperium-root", str(imperium_root),
                        "--output-json", str(step_data_dir / "tasks_inventory.json"),
                        "--output-md", str(step_data_dir / "tasks_inventory.md"),
                    ],
                    "verdict_json": step_data_dir / "tasks_inventory.json",
                },
            ],
            "fatal": False,
            "outputs": [
                str(step_data_dir / "tools_inventory.json"), str(step_data_dir / "tools_inventory.md"),
                str(step_data_dir / "tasks_inventory.json"), str(step_data_dir / "tasks_inventory.md"),
            ],
        },
        {
            "id": "STEP-005",
            "name": "Receipts scan",
            "purpose": "Index receipts and owner response traces across artifacts.",
            "commands": [
                {
                    "script": "continuity_scan_receipts.py",
                    "args": [
                        "--imperium-root", str(imperium_root),
                        "--output-json", str(step_data_dir / "receipts_scan.json"),
                        "--output-md", str(step_data_dir / "receipts_scan.md"),
                    ],
                    "verdict_json": step_data_dir / "receipts_scan.json",
                }
            ],
            "fatal": False,
            "outputs": [str(step_data_dir / "receipts_scan.json"), str(step_data_dir / "receipts_scan.md")],
        },
        {
            "id": "STEP-006",
            "name": "Ledgers scan",
            "purpose": "Index task ledger files and parse health.",
            "commands": [
                {
                    "script": "continuity_scan_ledgers.py",
                    "args": [
                        "--imperium-root", str(imperium_root),
                        "--output-json", str(step_data_dir / "ledgers_scan.json"),
                        "--output-md", str(step_data_dir / "ledgers_scan.md"),
                    ],
                    "verdict_json": step_data_dir / "ledgers_scan.json",
                }
            ],
            "fatal": False,
            "outputs": [str(step_data_dir / "ledgers_scan.json"), str(step_data_dir / "ledgers_scan.md")],
        },
        {
            "id": "STEP-007",
            "name": "Known blockers scan",
            "purpose": "Detect currently known protocol/runtime blockers and warnings.",
            "commands": [
                {
                    "script": "continuity_scan_known_blockers.py",
                    "args": [
                        "--imperium-root", str(imperium_root),
                        "--output-json", str(step_data_dir / "known_blockers.json"),
                        "--output-md", str(step_data_dir / "known_blockers.md"),
                    ],
                    "verdict_json": step_data_dir / "known_blockers.json",
                }
            ],
            "fatal": False,
            "outputs": [str(step_data_dir / "known_blockers.json"), str(step_data_dir / "known_blockers.md")],
        },
        {
            "id": "STEP-008",
            "name": "Continuity pack build",
            "purpose": "Assemble continuity pack folder, manifest, hashes, and zip.",
            "commands": [
                {
                    "script": "continuity_pack_build.py",
                    "args": [
                        "--imperium-root", str(imperium_root),
                        "--task-root", str(task_root),
                        "--run-id", run_id,
                        "--output-pack-dir", str(pack_dir),
                        "--step-data-dir", str(step_data_dir),
                        "--step-receipts-dir", str(step_receipts_dir),
                        "--executor-receipt", str(executor_receipt_path),
                        "--output-json", str(step_data_dir / "pack_build.json"),
                        "--output-md", str(step_data_dir / "pack_build.md"),
                    ],
                    "verdict_json": step_data_dir / "pack_build.json",
                }
            ],
            "fatal": True,
            "outputs": [str(step_data_dir / "pack_build.json"), str(step_data_dir / "pack_build.md"), str(task_root / "CONTINUITY_PACK.zip")],
        },
        {
            "id": "STEP-009",
            "name": "Continuity pack verify",
            "purpose": "Verify pack integrity, manifest/hash consistency, and zip hygiene.",
            "commands": [
                {
                    "script": "continuity_pack_verify.py",
                    "args": [
                        "--task-root", str(task_root),
                        "--pack-dir", str(pack_dir),
                        "--output-json", str(step_data_dir / "pack_verify.json"),
                        "--output-md", str(step_data_dir / "pack_verify.md"),
                    ],
                    "verdict_json": step_data_dir / "pack_verify.json",
                }
            ],
            "fatal": True,
            "outputs": [str(step_data_dir / "pack_verify.json"), str(step_data_dir / "pack_verify.md")],
        },
        {
            "id": "STEP-010",
            "name": "Owner summary",
            "purpose": "Generate owner-facing continuity summary and final response template.",
            "commands": [
                {
                    "script": "continuity_owner_summary.py",
                    "args": [
                        "--task-root", str(task_root),
                        "--pack-dir", str(pack_dir),
                        "--verify-json", str(step_data_dir / "pack_verify.json"),
                        "--metrics-json", str(pack_dir / "METRICS.json"),
                        "--output-json", str(step_data_dir / "owner_summary.json"),
                        "--output-md", str(step_data_dir / "owner_summary.md"),
                    ],
                    "verdict_json": step_data_dir / "owner_summary.json",
                }
            ],
            "fatal": True,
            "outputs": [str(step_data_dir / "owner_summary.json"), str(step_data_dir / "owner_summary.md"), str(task_root / "OWNER_SUMMARY.md")],
        },
    ]

    overall_blocked = False
    overall_partial = False

    total = len(steps)
    for idx, step in enumerate(steps, start=1):
        label = f"[{idx:03d}/{total:03d}]"
        print(f"{label} {step['name']} ... START")
        print(f"  script_group: {', '.join([c['script'] for c in step['commands']])}")
        print(f"  purpose: {step['purpose']}")
        print(f"  outputs: {', '.join(step['outputs'])}")

        started = iso_now()
        cmd_results = []
        rc_list: List[int] = []
        verdicts: List[str] = []

        for c in step["commands"]:
            script_path = tools_root / c["script"]
            cmd = [sys.executable, str(script_path)] + c["args"]
            rc, out_lines, err_lines = run_command_live(cmd, cwd=tools_root)
            rc_list.append(rc)
            verdict = load_verdict(Path(c["verdict_json"]))
            verdicts.append(verdict)
            cmd_results.append(
                {
                    "script": c["script"],
                    "exit_code": rc,
                    "verdict": verdict,
                    "stdout_tail": out_lines[-8:],
                    "stderr_tail": err_lines[-8:],
                }
            )

        ended = iso_now()
        step_verdict = summarize_step_verdict(verdicts, rc_list)
        if step_verdict in {"PARTIAL"}:
            overall_partial = True
        if step_verdict in {"BLOCKED", "FAIL"}:
            overall_blocked = True

        receipt_payload = {
            "task_id": args.task_id,
            "run_id": run_id,
            "step_id": step["id"],
            "script_name": ",".join([c["script"] for c in step["commands"]]),
            "started_at_utc": started,
            "ended_at_utc": ended,
            "exit_code": max(rc_list) if rc_list else 0,
            "verdict": step_verdict,
            "output_files": step["outputs"],
            "notes": {
                "purpose": step["purpose"],
                "commands": cmd_results,
                "no_vm2_contact": True,
                "no_real_e2e": True,
                "no_throne": True,
                "no_watchers": True,
                "no_latest": True,
            },
        }

        step_receipt_path = step_receipts_dir / f"{step['id']}_{step['name'].replace(' ', '_').upper()}.json"
        write_json(step_receipt_path, receipt_payload)

        step_report_lines = [
            f"# {step['id']} {step['name']}",
            "",
            f"started_at_utc: {started}",
            f"ended_at_utc: {ended}",
            f"verdict: {step_verdict}",
            f"exit_code: {receipt_payload['exit_code']}",
            f"purpose: {step['purpose']}",
            "",
            "## Command Results",
        ]
        for res in cmd_results:
            step_report_lines.append(f"- {res['script']} rc={res['exit_code']} verdict={res['verdict']}")
        write_text(step_reports_dir / f"{step['id']}.md", "\n".join(step_report_lines))

        executor_receipt["steps"].append(
            {
                "step_id": step["id"],
                "name": step["name"],
                "verdict": step_verdict,
                "exit_code": receipt_payload["exit_code"],
                "step_receipt": str(step_receipt_path),
            }
        )
        write_json(executor_receipt_path, executor_receipt)

        print(f"{label} {step['name']} ... {step_verdict}")

        if step["fatal"] and step_verdict in {"BLOCKED", "FAIL"}:
            print(f"{label} fatal step failed; executor will stop.")
            break

    # Derive final verdict
    final_verdict = "PASS_AS_CONTINUITY_EXECUTOR_BASE"
    if overall_blocked:
        final_verdict = "BLOCKED"
    elif overall_partial:
        final_verdict = "PARTIAL"

    # Override from owner summary result if present
    owner_summary_json = step_data_dir / "owner_summary.json"
    owner_data, owner_err = read_json_safe(owner_summary_json)
    if owner_err is None and isinstance(owner_data, dict):
        ov = str(owner_data.get("final_verdict", "")).strip()
        if ov:
            final_verdict = ov

    executor_receipt.update(
        {
            "ended_at_utc": iso_now(),
            "status": final_verdict,
            "final_pack_zip": str(task_root / "CONTINUITY_PACK.zip"),
            "final_pack_sidecar": str(task_root / "CONTINUITY_PACK.zip.sha256"),
        }
    )
    write_json(executor_receipt_path, executor_receipt)

    # Copy scripts snapshot
    copy_continuity_scripts(tools_root, task_root / "20_CONTINUITY_SCRIPTS_COPY")

    # Required report files
    impl_report = [
        "# 0016A_IMPLEMENTATION_REPORT",
        "",
        "Implemented continuity subsystem base scripts in 20_CONTINUITY.",
        "Executor mode: manual-visible with live step logs.",
        "No VM2, no E2E, no THRONE, no watchers, no latest logic.",
    ]
    write_text(reports_dir / "0016A_IMPLEMENTATION_REPORT.md", "\n".join(impl_report))

    run_report = [
        "# 0016A_EXECUTOR_RUN_REPORT",
        "",
        f"task_id: {args.task_id}",
        f"run_id: {run_id}",
        f"final_verdict: {final_verdict}",
        "",
        "## Steps",
    ]
    for s in executor_receipt.get("steps", []):
        run_report.append(f"- {s['step_id']} {s['name']} => {s['verdict']} (rc={s['exit_code']})")
    write_text(reports_dir / "0016A_EXECUTOR_RUN_REPORT.md", "\n".join(run_report))

    # Copy specific report aliases
    src_address = step_data_dir / "address_hardening.md"
    if src_address.exists():
        shutil.copy2(src_address, reports_dir / "0016A_ADDRESS_HARDENING_REPORT.md")
    src_verify = step_data_dir / "pack_verify.md"
    if src_verify.exists():
        shutil.copy2(src_verify, reports_dir / "0016A_PACK_VERIFY_REPORT.md")

    inv_lines = [
        "# 0016A_INVENTORY_REPORT",
        "",
        f"artifacts_inventory: {step_data_dir / 'artifacts_inventory.json'}",
        f"manual_proofs_inventory: {step_data_dir / 'manual_proofs_inventory.json'}",
        f"tools_inventory: {step_data_dir / 'tools_inventory.json'}",
        f"tasks_inventory: {step_data_dir / 'tasks_inventory.json'}",
        f"receipts_scan: {step_data_dir / 'receipts_scan.json'}",
        f"ledgers_scan: {step_data_dir / 'ledgers_scan.json'}",
    ]
    write_text(reports_dir / "0016A_INVENTORY_REPORT.md", "\n".join(inv_lines))

    speculum_lines = [
        "# SPECULUM_REVIEW_REQUEST",
        "",
        "Please hard-review TASK-20260509-0016A continuity executor base:",
        "1. Whether executor transparency and live step output are sufficient.",
        "2. Whether OWNER_MANUAL_PROOFS are correctly separated from normal artifacts.",
        "3. Whether address hardening detects dirty/stale path patterns.",
        "4. Whether old/new tasks are inventoried without latest logic.",
        "5. Whether metrics avoid fake-green and reflect blocker reality.",
        "6. Whether pack is suitable for new chat handoff baseline.",
        "7. Whether this can become future Sanctum/MetaOS backend for a button.",
        "8. Whether any local-only secret leakage risk remains.",
        "9. Whether next step should be 0016B or return to 0014F.",
    ]
    write_text(task_root / "SPECULUM_REVIEW_REQUEST.md", "\n".join(speculum_lines))

    # Ensure top-level owner files
    if not (task_root / "OWNER_SUMMARY.md").exists():
        write_text(
            task_root / "OWNER_SUMMARY.md",
            "# OWNER_SUMMARY\n\nContinuity executor finished with no owner summary step output.",
        )

    if not (task_root / "AGENT_FINAL_RESPONSE.txt").exists():
        write_text(
            task_root / "AGENT_FINAL_RESPONSE.txt",
            owner_report_text(
                step=args.task_id,
                bundle=str(task_root / "CONTINUITY_PACK.zip"),
                verdict=final_verdict,
                lines=[
                    "Собран continuity executor и continuity pack.",
                    "Инвентари и блокеры зафиксированы по файловым evidence.",
                    "VM2/E2E/THRONE/watchers/latest не использовались.",
                    "Требуется Speculum review перед следующим шагом.",
                ],
            ),
        )

    # Task-level manifest/hash
    build_task_manifest(task_root, args.task_id)

    print(f"FINAL VERDICT: {final_verdict}")
    print(f"TASK ROOT: {task_root}")
    print(f"CONTINUITY PACK: {task_root / 'CONTINUITY_PACK.zip'}")
    return 0 if final_verdict in {"PASS_AS_CONTINUITY_EXECUTOR_BASE", "PARTIAL"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
