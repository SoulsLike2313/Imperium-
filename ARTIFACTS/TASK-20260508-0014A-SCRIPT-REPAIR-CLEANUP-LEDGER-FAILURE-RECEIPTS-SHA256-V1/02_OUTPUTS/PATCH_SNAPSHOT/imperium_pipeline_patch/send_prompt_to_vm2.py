#!/usr/bin/env python3
"""Dispatch a prompt package to VM2 with strict identity, provenance, and ledger events."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from lib.id_validation import (  # noqa: E402
    validate_contour_id,
    validate_producer_id,
    validate_producer_type,
    validate_run_id,
    validate_stage_id,
    validate_task_id,
)
from lib.ledger_utils import append_event  # noqa: E402
from lib.owner_report import print_owner_report, write_owner_report  # noqa: E402
from lib.path_safety import assert_no_latest_pattern, assert_safe_shareable_path  # noqa: E402
from lib.provenance_utils import create_provenance_record, update_origin_index, validate_provenance, write_provenance  # noqa: E402
from lib.sha256_utils import file_sha256  # noqa: E402


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_route_config(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Route config not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _safe_append_stage_failed(
    ledger_path: Path,
    task_id: str,
    stage_id: str,
    run_id: str,
    contour_id: str,
    producer_type: str,
    producer_id: str,
    artifact_ref: str,
    receipt_ref: str,
    notes: str,
) -> None:
    try:
        append_event(
            ledger_path,
            {
                "task_id": task_id,
                "stage_id": stage_id,
                "run_id": run_id,
                "contour_id": contour_id,
                "producer_type": producer_type,
                "producer_id": producer_id,
                "event_type": "STAGE_FAILED",
                "status": "FAIL",
                "artifact_ref": artifact_ref,
                "artifact_sha256": "",
                "previous_event_ref": "",
                "timestamp_utc": "",
                "receipt_ref": receipt_ref,
                "notes": notes,
            },
        )
    except Exception:
        return


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Send prompt package to VM2.")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--stage-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--contour-id", required=True)
    parser.add_argument("--producer-type", required=True)
    parser.add_argument("--producer-id", required=True)
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--output-receipt", required=True)
    parser.add_argument("--ledger-path", required=True)
    parser.add_argument("--provenance-output", required=True)
    parser.add_argument("--origin-index-path", required=True)
    parser.add_argument("--config", required=True, help="Local VM2 route config JSON")
    parser.add_argument("--owner-report-output", default="")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    receipt_path = Path(args.output_receipt).resolve()
    ledger_path = Path(args.ledger_path).resolve()
    provenance_path = Path(args.provenance_output).resolve()

    bundle_ref = "N/A"
    verdict = "FAIL"
    failure_reason = ""
    command_log: list[str] = []

    # Keep raw values for failure receipts.
    task_id_raw = args.task_id.strip()
    stage_id_raw = args.stage_id.strip()
    run_id_raw = args.run_id.strip()
    contour_id_raw = args.contour_id.strip()
    producer_type_raw = args.producer_type.strip()
    producer_id_raw = args.producer_id.strip()
    remote_prompt_path = ""
    prompt_sha = ""

    try:
        task_id = validate_task_id(task_id_raw)
        stage_id = validate_stage_id(stage_id_raw)
        run_id = validate_run_id(run_id_raw)
        contour_id = validate_contour_id(contour_id_raw)
        producer_type = validate_producer_type(producer_type_raw)
        producer_id = validate_producer_id(producer_id_raw)

        if contour_id != "VM2":
            raise ValueError("send_prompt_to_vm2.py requires --contour-id VM2")
        if producer_type != "PC_SERVITOR":
            raise ValueError("send_prompt_to_vm2.py requires --producer-type PC_SERVITOR")

        prompt_file = Path(args.prompt_file).resolve()
        assert_no_latest_pattern(str(prompt_file), "prompt-file")
        assert_safe_shareable_path(prompt_file, "prompt-file")
        if not prompt_file.exists() or not prompt_file.is_file():
            raise FileNotFoundError(f"Prompt file does not exist: {prompt_file}")

        prompt_sha = file_sha256(prompt_file)
        route = _load_route_config(Path(args.config).resolve())
        remote_worker_root = str(route.get("remote_worker_root", "")).strip()
        user_host = str(route.get("user_host", "")).strip()
        port = str(route.get("port", "")).strip()
        key_path = str(route.get("key_path", "")).strip()

        if not remote_worker_root or not user_host or not port or not key_path:
            raise ValueError("Route config missing required keys: remote_worker_root/user_host/port/key_path")

        assert_no_latest_pattern(remote_worker_root, "remote_worker_root")
        remote_task_dir = f"{remote_worker_root}/01_INBOX/tasks/{task_id}/{stage_id}/{run_id}"
        remote_prompt_path = f"{remote_task_dir}/PROMPT.md"
        bundle_ref = remote_prompt_path

        dispatch_ok = True
        if not args.dry_run:
            mkdir_cmd = ["ssh", "-i", key_path, "-p", port, user_host, f"mkdir -p '{remote_task_dir}'"]
            command_log.append("ssh mkdir -p <remote_task_dir>")
            mkdir_result = _run(mkdir_cmd)
            if mkdir_result.returncode != 0:
                dispatch_ok = False
                failure_reason = (mkdir_result.stderr or "remote mkdir failed").strip()

            if dispatch_ok:
                scp_cmd = ["scp", "-i", key_path, "-P", port, str(prompt_file), f"{user_host}:{remote_prompt_path}"]
                command_log.append("scp <prompt> to remote path")
                scp_result = _run(scp_cmd)
                if scp_result.returncode != 0:
                    dispatch_ok = False
                    failure_reason = (scp_result.stderr or "scp dispatch failed").strip()
        else:
            dispatch_ok = True
            command_log.append("dry-run enabled; no SSH/SCP command executed")

        verification_status = "RECEIPT_VERIFIED" if dispatch_ok else "REJECTED"
        provenance = create_provenance_record(
            task_id=task_id,
            stage_id=stage_id,
            run_id=run_id,
            contour_id="VM2",
            producer_type="PC_SERVITOR",
            producer_id=producer_id,
            executor_role="dispatch_operator",
            creation_mode="SCRIPTED",
            produced_on_host_class="PC",
            source_bundle_name=prompt_file.name,
            source_bundle_sha256=prompt_sha,
            parent_bundle_refs=[],
            transfer_method="SSH_SEND" if not args.dry_run else "NONE",
            transfer_actor=producer_id,
            manual_touchpoints=[],
            authority_level="WORKING_ARTIFACT",
            acceptance_scope="dispatch_pre_stage_execution",
            verification_status=verification_status,
        )
        prov_errors = validate_provenance(provenance, strict_acceptance=True)
        if prov_errors:
            raise ValueError("Provenance validation failed: " + "; ".join(prov_errors))
        write_provenance(provenance_path, provenance)

        receipt_status = "PASS" if dispatch_ok else "FAIL"
        receipt_payload = {
            "task_id": task_id,
            "stage_id": stage_id,
            "run_id": run_id,
            "contour_id": "VM2",
            "producer_type": "PC_SERVITOR",
            "producer_id": producer_id,
            "status": receipt_status,
            "failure_reason": "" if dispatch_ok else failure_reason,
            "timestamp_utc": _utc_now(),
            "prompt_file": str(prompt_file),
            "prompt_sha256": prompt_sha,
            "remote_prompt_path": remote_prompt_path,
            "dispatch_mode": "DRY_RUN" if args.dry_run else "SSH_SEND",
            "commands": command_log,
            "deleted_anything": False,
            "moved_anything": False,
            "touched_throne": False,
            "touched_vm2": not args.dry_run,
            "touched_vm3": False,
            "autosync_used": False,
            "latest_logic_used": False,
            "provenance_ref": str(provenance_path),
            "verdict": receipt_status,
        }
        _write_json(receipt_path, receipt_payload)

        origin_item = update_origin_index(
            Path(args.origin_index_path).resolve(),
            provenance,
            artifact_name=prompt_file.name,
            artifact_path=str(prompt_file),
            artifact_sha256=prompt_sha,
            provenance_ref=str(provenance_path),
            receipt_ref=str(receipt_path),
        )

        event_type = "STAGE_DISPATCHED" if dispatch_ok else "STAGE_FAILED"
        append_event(
            ledger_path,
            {
                "task_id": task_id,
                "stage_id": stage_id,
                "run_id": run_id,
                "contour_id": "VM2",
                "producer_type": "PC_SERVITOR",
                "producer_id": producer_id,
                "event_type": event_type,
                "status": receipt_status,
                "artifact_ref": str(prompt_file),
                "artifact_sha256": prompt_sha,
                "previous_event_ref": "",
                "timestamp_utc": "",
                "receipt_ref": str(receipt_path),
                "notes": f"origin_status={origin_item.get('origin_status')}; dry_run={args.dry_run}",
            },
        )

        verdict = receipt_status

    except Exception as exc:  # pylint: disable=broad-except
        failure_reason = str(exc)
        verdict = "FAIL"
        _write_json(
            receipt_path,
            {
                "task_id": task_id_raw,
                "stage_id": stage_id_raw,
                "run_id": run_id_raw,
                "contour_id": contour_id_raw,
                "producer_type": producer_type_raw,
                "producer_id": producer_id_raw,
                "status": "FAIL",
                "failure_reason": failure_reason,
                "timestamp_utc": _utc_now(),
                "provenance_ref": str(provenance_path) if provenance_path.exists() else "",
                "deleted_anything": False,
                "moved_anything": False,
                "touched_throne": False,
                "touched_vm2": False,
                "touched_vm3": False,
                "autosync_used": False,
                "latest_logic_used": False,
                "verdict": "FAIL",
            },
        )
        _safe_append_stage_failed(
            ledger_path=ledger_path,
            task_id=task_id_raw,
            stage_id=stage_id_raw,
            run_id=run_id_raw,
            contour_id=contour_id_raw,
            producer_type=producer_type_raw,
            producer_id=producer_id_raw,
            artifact_ref=args.prompt_file,
            receipt_ref=str(receipt_path),
            notes=f"dispatch failure: {failure_reason}",
        )
        print(f"ERROR: {failure_reason}", file=sys.stderr)

    comment_lines = [
        "Выполнен dispatch wrapper с обязательными TASK/STAGE/RUN и provenance проверками.",
        "На ошибках формируется FAIL receipt и пишется STAGE_FAILED событие в append-only ledger.",
        "E2E не запускался, THRONE transfer и watchers не использовались.",
        "Следующий шаг: после устранения входной ошибки повторить dispatch тем же идентификаторным набором.",
    ]
    step = f"{task_id_raw}/{stage_id_raw}/send_prompt_to_vm2.py"
    print_owner_report(step, bundle_ref, verdict, comment_lines)
    if args.owner_report_output:
        write_owner_report(Path(args.owner_report_output).resolve(), step, bundle_ref, verdict, comment_lines)

    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
