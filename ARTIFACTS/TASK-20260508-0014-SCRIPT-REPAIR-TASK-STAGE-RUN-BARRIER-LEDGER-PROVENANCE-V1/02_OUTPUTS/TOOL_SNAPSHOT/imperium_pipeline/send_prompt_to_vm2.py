#!/usr/bin/env python3
"""Dispatch a prompt package to VM2 with strict identity, provenance, and ledger events."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
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


def _load_route_config(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Route config not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


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

    verdict = "FAIL"
    comment_lines = []
    bundle_ref = "N/A"

    try:
        task_id = validate_task_id(args.task_id)
        stage_id = validate_stage_id(args.stage_id)
        run_id = validate_run_id(args.run_id)
        contour_id = validate_contour_id(args.contour_id)
        producer_type = validate_producer_type(args.producer_type)
        producer_id = validate_producer_id(args.producer_id)

        if contour_id != "VM2":
            raise ValueError("send_prompt_to_vm2.py requires --contour-id VM2")
        if producer_type != "PC_SERVITOR":
            raise ValueError("send_prompt_to_vm2.py requires --producer-type PC_SERVITOR")

        prompt_file = Path(args.prompt_file).resolve()
        assert_no_latest_pattern(str(prompt_file), "prompt-file")
        assert_safe_shareable_path(prompt_file, "prompt-file")
        if not prompt_file.exists() or not prompt_file.is_file():
            raise FileNotFoundError(f"Prompt file does not exist: {prompt_file}")

        receipt_path = Path(args.output_receipt).resolve()
        ledger_path = Path(args.ledger_path).resolve()
        provenance_path = Path(args.provenance_output).resolve()
        origin_index_path = Path(args.origin_index_path).resolve()
        route_config_path = Path(args.config).resolve()

        prompt_sha = file_sha256(prompt_file)
        route = _load_route_config(route_config_path)
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

        command_log = []
        dispatch_ok = True

        if not args.dry_run:
            mkdir_cmd = ["ssh", "-i", key_path, "-p", port, user_host, f"mkdir -p '{remote_task_dir}'"]
            command_log.append("ssh mkdir -p <remote_task_dir>")
            mkdir_result = _run(mkdir_cmd)
            if mkdir_result.returncode != 0:
                dispatch_ok = False
                command_log.append(f"mkdir stderr: {mkdir_result.stderr.strip()}")

            if dispatch_ok:
                scp_cmd = ["scp", "-i", key_path, "-P", port, str(prompt_file), f"{user_host}:{remote_prompt_path}"]
                command_log.append("scp <prompt> to remote path")
                scp_result = _run(scp_cmd)
                if scp_result.returncode != 0:
                    dispatch_ok = False
                    command_log.append(f"scp stderr: {scp_result.stderr.strip()}")
        else:
            dispatch_ok = True
            command_log.append("dry-run enabled; no SSH/SCP command executed")

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
            verification_status="RECEIPT_VERIFIED" if dispatch_ok else "REJECTED",
        )
        prov_errors = validate_provenance(provenance, strict_acceptance=True)
        if prov_errors:
            raise ValueError("Provenance validation failed: " + "; ".join(prov_errors))
        write_provenance(provenance_path, provenance)

        receipt_payload = {
            "task_id": task_id,
            "stage_id": stage_id,
            "run_id": run_id,
            "contour_id": "VM2",
            "producer_type": "PC_SERVITOR",
            "producer_id": producer_id,
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
            "verdict": "PASS" if dispatch_ok else "FAIL",
        }
        _write_json(receipt_path, receipt_payload)

        origin_item = update_origin_index(
            origin_index_path,
            provenance,
            artifact_name=prompt_file.name,
            artifact_path=str(prompt_file),
            artifact_sha256=prompt_sha,
            provenance_ref=str(provenance_path),
            receipt_ref=str(receipt_path),
        )

        event_type = "STAGE_DISPATCHED" if dispatch_ok else "STAGE_FAILED"
        status = "PASS" if dispatch_ok else "FAIL"
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
                "status": status,
                "artifact_ref": str(prompt_file),
                "artifact_sha256": prompt_sha,
                "previous_event_ref": "",
                "timestamp_utc": "",
                "receipt_ref": str(receipt_path),
                "notes": f"origin_status={origin_item.get('origin_status')}; dry_run={args.dry_run}",
            },
        )

        verdict = "PASS" if dispatch_ok else "FAIL"
        comment_lines = [
            "Подготовлена и проверена отправка prompt-пакета с обязательными TASK/STAGE/RUN и provenance полями.",
            "Сформированы DISPATCH_RECEIPT, provenance record и append-only ledger event для dispatch/fail.",
            "E2E не выполнялся в рамках этой задачи, THRONE и автоматизация остаются заблокированы.",
            "Следующий шаг: использовать repaired fetch/barrier/final scripts в TASK-0015 при контролируемом tiny E2E.",
        ]

    except Exception as exc:  # pylint: disable=broad-except
        verdict = "FAIL"
        comment_lines = [
            "Скрипт dispatch завершился ошибкой на этапе строгой валидации или подготовки отправки.",
            "Обязательные identity/provenance/ledger требования не были полностью выполнены.",
            "THRONE не затрагивался, E2E запуск не выполнялся.",
            "Следующий шаг: исправить входные параметры и повторить dispatch с тем же TASK/STAGE/RUN.",
        ]
        print(f"ERROR: {exc}", file=sys.stderr)

    step = f"{args.task_id}/{args.stage_id}/send_prompt_to_vm2.py"
    report_text = print_owner_report(step, bundle_ref, verdict, comment_lines)
    if args.owner_report_output:
        write_owner_report(Path(args.owner_report_output).resolve(), step, bundle_ref, verdict, comment_lines)

    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
