#!/usr/bin/env python3
"""Fetch an exact VM2 stage bundle with strict identity/provenance verification."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TOOLS_ROOT = SCRIPT_DIR.parent
CORE_LIB_DIR = TOOLS_ROOT / "01_CORE_LIB"
if str(CORE_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_LIB_DIR))

from id_validation import (  # noqa: E402
    validate_contour_id,
    validate_producer_id,
    validate_producer_type,
    validate_run_id,
    validate_stage_id,
    validate_task_id,
)
from ledger_utils import append_event  # noqa: E402
from owner_report import print_owner_report, write_owner_report  # noqa: E402
from path_safety import assert_no_latest_pattern, assert_safe_shareable_path  # noqa: E402
from provenance_utils import create_provenance_record, update_origin_index, validate_provenance, write_provenance  # noqa: E402
from sha256_utils import file_sha256, parse_sha256_file  # noqa: E402


REQUIRED_BUNDLE_HINTS = ["manifest", "receipt", "provenance"]


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


def _load_route_config(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Route config not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _bundle_has_required_files(bundle_path: Path) -> tuple[bool, list[str]]:
    missing: list[str] = []
    with zipfile.ZipFile(bundle_path, "r") as archive:
        names = [name.lower() for name in archive.namelist()]
    for hint in REQUIRED_BUNDLE_HINTS:
        if not any(hint in name for name in names):
            missing.append(hint)
    return len(missing) == 0, missing


def _extract_first_json_by_hint(bundle_path: Path, hint: str) -> dict | None:
    with zipfile.ZipFile(bundle_path, "r") as archive:
        for name in archive.namelist():
            lname = name.lower()
            if hint in lname and lname.endswith(".json"):
                try:
                    return json.loads(archive.read(name).decode("utf-8"))
                except Exception:
                    return None
    return None


def _safe_append_stage_failed(
    ledger_path: Path,
    task_id: str,
    stage_id: str,
    run_id: str,
    contour_id: str,
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
                "producer_type": "PC_SERVITOR",
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
    parser = argparse.ArgumentParser(description="Fetch exact VM2 stage bundle by identity.")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--stage-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--contour-id", required=True)
    parser.add_argument("--expected-producer-type", required=True)
    parser.add_argument("--remote-bundle-path", required=True)
    parser.add_argument("--remote-sha256-path", required=True)
    parser.add_argument("--local-output-dir", required=True)
    parser.add_argument("--output-receipt", required=True)
    parser.add_argument("--ledger-path", required=True)
    parser.add_argument("--provenance-output", required=True)
    parser.add_argument("--origin-index-path", required=True)
    parser.add_argument("--producer-id", required=True, help="PC producer id for fetch action")
    parser.add_argument("--config", required=True)
    parser.add_argument("--owner-report-output", default="")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    receipt_path = Path(args.output_receipt).resolve()
    ledger_path = Path(args.ledger_path).resolve()
    provenance_path = Path(args.provenance_output).resolve()

    verdict = "FAIL"
    bundle_ref = "N/A"

    # Raw values for failure evidence.
    task_id_raw = args.task_id.strip()
    stage_id_raw = args.stage_id.strip()
    run_id_raw = args.run_id.strip()
    contour_id_raw = args.contour_id.strip()
    expected_producer_type_raw = args.expected_producer_type.strip()
    producer_id_raw = args.producer_id.strip()
    failure_reason = ""

    try:
        task_id = validate_task_id(task_id_raw)
        stage_id = validate_stage_id(stage_id_raw)
        run_id = validate_run_id(run_id_raw)
        contour_id = validate_contour_id(contour_id_raw)
        if contour_id != "VM2":
            raise ValueError("fetch_vm2_stage_bundle.py requires --contour-id VM2")

        expected_producer_type = validate_producer_type(expected_producer_type_raw)
        if expected_producer_type != "VM2_WORKER":
            raise ValueError("Expected producer type must be VM2_WORKER")
        producer_id = validate_producer_id(producer_id_raw)

        remote_bundle_path = args.remote_bundle_path.strip()
        remote_sha_path = args.remote_sha256_path.strip()
        assert_no_latest_pattern(remote_bundle_path, "remote-bundle-path")
        assert_no_latest_pattern(remote_sha_path, "remote-sha256-path")

        local_output_dir = Path(args.local_output_dir).resolve()
        local_output_dir.mkdir(parents=True, exist_ok=True)
        assert_safe_shareable_path(local_output_dir, "local-output-dir")

        route = _load_route_config(Path(args.config).resolve())
        key_path = str(route.get("key_path", "")).strip()
        port = str(route.get("port", "")).strip()
        user_host = str(route.get("user_host", "")).strip()
        if not key_path or not port or not user_host:
            raise ValueError("Route config missing key_path/port/user_host")

        local_bundle = local_output_dir / Path(remote_bundle_path).name
        local_sha = local_output_dir / Path(remote_sha_path).name
        bundle_ref = str(local_bundle)

        command_log: list[str] = []
        checks_passed = {
            "remote_sha_exists": False,
            "local_sha_match": False,
            "bundle_exists": False,
            "manifest_exists": False,
            "receipt_exists": False,
            "provenance_exists": False,
            "identity_match": False,
            "producer_type_match": False,
            "no_policy_violation": True,
        }

        if not args.dry_run:
            check_cmd = ["ssh", "-i", key_path, "-p", port, user_host, f"test -f '{remote_bundle_path}' && test -f '{remote_sha_path}'"]
            command_log.append("ssh test remote bundle + sha256 existence")
            check_result = _run(check_cmd)
            if check_result.returncode != 0:
                raise RuntimeError("Remote bundle/sha256 does not exist")
            checks_passed["remote_sha_exists"] = True

            get_bundle = ["scp", "-i", key_path, "-P", port, f"{user_host}:{remote_bundle_path}", str(local_bundle)]
            get_sha = ["scp", "-i", key_path, "-P", port, f"{user_host}:{remote_sha_path}", str(local_sha)]
            command_log.append("scp remote bundle")
            if _run(get_bundle).returncode != 0:
                raise RuntimeError("Bundle scp failed")
            command_log.append("scp remote sha256 file")
            if _run(get_sha).returncode != 0:
                raise RuntimeError("SHA256 scp failed")
        else:
            command_log.append("dry-run enabled; no SSH/SCP command executed")

        checks_passed["bundle_exists"] = local_bundle.exists()
        if not checks_passed["bundle_exists"]:
            raise RuntimeError("Fetched bundle is missing locally")
        if not local_sha.exists():
            raise RuntimeError("Fetched sha256 file is missing locally")

        sha_entries = parse_sha256_file(local_sha)
        expected_sha = sha_entries[0][0] if sha_entries else ""
        actual_sha = file_sha256(local_bundle)
        checks_passed["local_sha_match"] = bool(expected_sha and expected_sha == actual_sha)
        if not checks_passed["local_sha_match"]:
            raise RuntimeError("Local bundle sha256 does not match expected remote sha256")

        has_required, missing_hints = _bundle_has_required_files(local_bundle)
        checks_passed["manifest_exists"] = "manifest" not in missing_hints
        checks_passed["receipt_exists"] = "receipt" not in missing_hints
        checks_passed["provenance_exists"] = "provenance" not in missing_hints
        if not has_required:
            raise RuntimeError("Bundle missing required internal evidence: " + ", ".join(missing_hints))

        embedded_provenance = _extract_first_json_by_hint(local_bundle, "provenance")
        if not embedded_provenance:
            raise RuntimeError("Unable to parse embedded provenance JSON from bundle")
        prov_errors = validate_provenance(embedded_provenance, strict_acceptance=True)
        if prov_errors:
            raise RuntimeError("Embedded provenance invalid: " + "; ".join(prov_errors))

        checks_passed["identity_match"] = (
            embedded_provenance.get("task_id") == task_id
            and embedded_provenance.get("stage_id") == stage_id
            and embedded_provenance.get("run_id") == run_id
            and embedded_provenance.get("contour_id") == contour_id
        )
        checks_passed["producer_type_match"] = embedded_provenance.get("producer_type") == expected_producer_type

        if not checks_passed["identity_match"]:
            raise RuntimeError("Embedded provenance identity mismatch against requested TASK/STAGE/RUN/CONTOUR")
        if not checks_passed["producer_type_match"]:
            raise RuntimeError("Embedded provenance producer_type mismatch")

        if embedded_provenance.get("authority_level") == "FINAL_TASK_BUNDLE" and contour_id == "VM2":
            raise RuntimeError("VM2 bundle cannot claim FINAL_TASK_BUNDLE authority")

        fetch_provenance = create_provenance_record(
            task_id=task_id,
            stage_id=stage_id,
            run_id=run_id,
            contour_id="PC",
            producer_type="PC_SERVITOR",
            producer_id=producer_id,
            executor_role="fetch_operator",
            creation_mode="SCRIPTED",
            produced_on_host_class="PC",
            source_bundle_name=local_bundle.name,
            source_bundle_sha256=actual_sha,
            parent_bundle_refs=[str(local_bundle)],
            transfer_method="SSH_FETCH" if not args.dry_run else "NONE",
            transfer_actor=producer_id,
            manual_touchpoints=[],
            authority_level="FETCHED_STAGE_BUNDLE",
            acceptance_scope="fetch_and_verify",
            verification_status="RECEIPT_VERIFIED",
        )
        prov_errors = validate_provenance(fetch_provenance, strict_acceptance=True)
        if prov_errors:
            raise RuntimeError("Fetch provenance invalid: " + "; ".join(prov_errors))
        write_provenance(provenance_path, fetch_provenance)

        origin_item = update_origin_index(
            Path(args.origin_index_path).resolve(),
            fetch_provenance,
            artifact_name=local_bundle.name,
            artifact_path=str(local_bundle),
            artifact_sha256=actual_sha,
            provenance_ref=str(provenance_path),
            receipt_ref=str(receipt_path),
        )

        append_event(
            ledger_path,
            {
                "task_id": task_id,
                "stage_id": stage_id,
                "run_id": run_id,
                "contour_id": contour_id,
                "producer_type": "PC_SERVITOR",
                "producer_id": producer_id,
                "event_type": "BUNDLE_FETCHED",
                "status": "PASS",
                "artifact_ref": str(local_bundle),
                "artifact_sha256": actual_sha,
                "previous_event_ref": "",
                "timestamp_utc": "",
                "receipt_ref": str(receipt_path),
                "notes": f"origin_status={origin_item.get('origin_status')}",
            },
        )
        append_event(
            ledger_path,
            {
                "task_id": task_id,
                "stage_id": stage_id,
                "run_id": run_id,
                "contour_id": contour_id,
                "producer_type": "PC_SERVITOR",
                "producer_id": producer_id,
                "event_type": "HASH_VERIFIED",
                "status": "PASS",
                "artifact_ref": str(local_bundle),
                "artifact_sha256": actual_sha,
                "previous_event_ref": "",
                "timestamp_utc": "",
                "receipt_ref": str(receipt_path),
                "notes": "sha256 matched expected remote value",
            },
        )
        append_event(
            ledger_path,
            {
                "task_id": task_id,
                "stage_id": stage_id,
                "run_id": run_id,
                "contour_id": contour_id,
                "producer_type": "PC_SERVITOR",
                "producer_id": producer_id,
                "event_type": "MANIFEST_VERIFIED",
                "status": "PASS",
                "artifact_ref": str(local_bundle),
                "artifact_sha256": actual_sha,
                "previous_event_ref": "",
                "timestamp_utc": "",
                "receipt_ref": str(receipt_path),
                "notes": "bundle contains manifest marker",
            },
        )
        append_event(
            ledger_path,
            {
                "task_id": task_id,
                "stage_id": stage_id,
                "run_id": run_id,
                "contour_id": contour_id,
                "producer_type": "PC_SERVITOR",
                "producer_id": producer_id,
                "event_type": "RECEIPT_VERIFIED",
                "status": "PASS",
                "artifact_ref": str(local_bundle),
                "artifact_sha256": actual_sha,
                "previous_event_ref": "",
                "timestamp_utc": "",
                "receipt_ref": str(receipt_path),
                "notes": "bundle contains receipt and provenance markers",
            },
        )

        _write_json(
            receipt_path,
            {
                "task_id": task_id,
                "stage_id": stage_id,
                "run_id": run_id,
                "contour_id": contour_id,
                "expected_producer_type": expected_producer_type,
                "actual_embedded_producer_type": embedded_provenance.get("producer_type"),
                "status": "PASS",
                "failure_reason": "",
                "timestamp_utc": _utc_now(),
                "local_bundle_path": str(local_bundle),
                "local_sha256_path": str(local_sha),
                "expected_sha256": expected_sha,
                "actual_sha256": actual_sha,
                "checks_passed": checks_passed,
                "commands": command_log,
                "deleted_anything": False,
                "moved_anything": False,
                "touched_throne": False,
                "touched_vm2": not args.dry_run,
                "touched_vm3": False,
                "autosync_used": False,
                "latest_logic_used": False,
                "provenance_ref": str(provenance_path),
                "verdict": "PASS",
            },
        )

        verdict = "PASS"

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
                "expected_producer_type": expected_producer_type_raw,
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
            producer_id=producer_id_raw,
            artifact_ref=args.remote_bundle_path,
            receipt_ref=str(receipt_path),
            notes=f"fetch failure: {failure_reason}",
        )
        print(f"ERROR: {failure_reason}", file=sys.stderr)

    comments = [
        "Выполнен fetch wrapper с обязательными identity, producer и provenance проверками.",
        "На ошибках формируется FAIL receipt и пишется STAGE_FAILED событие в append-only ledger.",
        "Реальный E2E запуск в этой задаче не выполнялся, THRONE и watchers не затрагивались.",
        "Следующий шаг: устранить причину отказа и повторить fetch по тем же TASK/STAGE/RUN/CONTOUR.",
    ]
    step = f"{task_id_raw}/{stage_id_raw}/fetch_vm2_stage_bundle.py"
    print_owner_report(step, bundle_ref, verdict, comments)
    if args.owner_report_output:
        write_owner_report(Path(args.owner_report_output).resolve(), step, bundle_ref, verdict, comments)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
