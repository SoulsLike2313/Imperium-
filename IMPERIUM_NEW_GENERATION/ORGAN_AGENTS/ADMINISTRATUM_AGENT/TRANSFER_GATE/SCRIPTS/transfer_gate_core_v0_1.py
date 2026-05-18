#!/usr/bin/env python3
"""Administratum Transfer Gate V0.1 core logic."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

DEFAULT_TRANSFER_ROOT = Path(
    os.environ.get(
        "ADMINISTRATUM_TRANSFER_ROOT",
        "/home/vboxuser2/IMPERIUM_CONTEXT/LOCAL/ADMINISTRATUM_TRANSFER",
    )
)
EXPECTED_PROMPT_PACK_FILES = {
    "TASK_PACK.md",
    "task_pack.json",
    "START_PROMPT.txt",
    "MANIFEST.json",
    "SHA256SUMS.txt",
}
EXPECTED_RESPONSE_FILES = {
    "FINAL_REPORT.md",
    "final_report.json",
    "MANIFEST.json",
    "SHA256SUMS.txt",
}
OWNER_TRIGGER_PHRASE = "Пиши промт"
LEDGER_NAME = "transfer_ledger_v0_1.jsonl"


class TransferGateError(RuntimeError):
    """Raised when a transfer gate operation cannot be completed."""


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def append_jsonl(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(data, ensure_ascii=False) + "\n")


def ensure_transfer_dirs(runtime_root: Path = DEFAULT_TRANSFER_ROOT) -> Dict[str, Path]:
    root = runtime_root.expanduser().resolve()
    dirs = {
        "root": root,
        "inbox_pc_to_vm2": root / "INBOX" / "PC_TO_VM2",
        "outbox_vm2_to_pc": root / "OUTBOX" / "VM2_TO_PC",
        "received_vm2": root / "RECEIVED" / "VM2",
        "ledger": root / "LEDGER",
        "ledger_receipts": root / "LEDGER" / "RECEIPTS",
        "quarantine": root / "QUARANTINE",
    }
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return dirs


def parse_sha256sums(text: str) -> Dict[str, str]:
    sums: Dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split()
        if len(parts) < 2:
            continue
        digest = parts[0].strip()
        name = " ".join(parts[1:]).strip().lstrip("*")
        if len(digest) == 64:
            sums[name.replace("\\", "/")] = digest.lower()
    return sums


def _zip_names(zip_obj: zipfile.ZipFile) -> List[str]:
    return sorted(name for name in zip_obj.namelist() if not name.endswith("/"))


def _zip_read_json(zip_obj: zipfile.ZipFile, name: str) -> Dict[str, Any]:
    with zip_obj.open(name, "r") as handle:
        raw = handle.read()
    parsed = json.loads(raw.decode("utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError(f"{name} must be a JSON object")
    return parsed


def _zip_member_sha256(zip_obj: zipfile.ZipFile, name: str) -> str:
    with zip_obj.open(name, "r") as handle:
        return sha256_bytes(handle.read())


def _check_zip_hashes(
    zip_obj: zipfile.ZipFile,
    *,
    required_names: Iterable[str],
    errors: List[str],
    warnings: List[str],
) -> Dict[str, str]:
    try:
        sums_text = zip_obj.read("SHA256SUMS.txt").decode("utf-8")
    except Exception as exc:
        errors.append(f"sha256sums_unreadable: {exc}")
        return {}
    declared = parse_sha256sums(sums_text)
    for name in sorted(required_names):
        if name == "SHA256SUMS.txt":
            continue
        expected = declared.get(name)
        if not expected:
            errors.append(f"missing_sha256sum_entry:{name}")
            continue
        actual = _zip_member_sha256(zip_obj, name)
        if actual != expected.lower():
            errors.append(f"sha256_mismatch:{name}")
    return declared


def _check_manifest_hashes(
    zip_obj: zipfile.ZipFile,
    manifest: Dict[str, Any],
    *,
    errors: List[str],
    warnings: List[str],
) -> None:
    files = manifest.get("files")
    if not isinstance(files, list):
        warnings.append("manifest_files_missing_or_not_list")
        return
    for item in files:
        if not isinstance(item, dict):
            warnings.append("manifest_file_record_not_object")
            continue
        name = str(item.get("path", "")).replace("\\", "/")
        declared_sha = item.get("sha256")
        declared_size = item.get("size_bytes")
        if not name:
            warnings.append("manifest_file_record_missing_path")
            continue
        if name not in zip_obj.namelist():
            errors.append(f"manifest_file_missing_from_zip:{name}")
            continue
        info = zip_obj.getinfo(name)
        if isinstance(declared_size, int) and declared_size != info.file_size:
            if name == "MANIFEST.json":
                warnings.append(f"manifest_self_size_mismatch:{name}")
            else:
                errors.append(f"manifest_size_mismatch:{name}")
        if isinstance(declared_sha, str) and declared_sha:
            actual = _zip_member_sha256(zip_obj, name)
            if actual != declared_sha.lower():
                errors.append(f"manifest_sha256_mismatch:{name}")


def _result_verdict(errors: Sequence[str], warnings: Sequence[str]) -> str:
    if errors:
        return "BLOCKED"
    if warnings:
        return "PASS_WITH_WARNINGS"
    return "PASS"


def verify_prompt_pack(pack_zip: Path, runtime_root: Path = DEFAULT_TRANSFER_ROOT) -> Dict[str, Any]:
    pack_path = pack_zip.expanduser().resolve()
    errors: List[str] = []
    warnings: List[str] = []
    manifest: Dict[str, Any] = {}
    task_pack: Dict[str, Any] = {}
    names: List[str] = []
    declared_hashes: Dict[str, str] = {}
    task_id = ""
    required_starting_head = ""

    if not pack_path.exists():
        errors.append("prompt_pack_zip_not_found")
    elif not zipfile.is_zipfile(pack_path):
        errors.append("prompt_pack_not_a_zip")
    else:
        with zipfile.ZipFile(pack_path, "r") as zip_obj:
            names = _zip_names(zip_obj)
            missing = sorted(EXPECTED_PROMPT_PACK_FILES - set(names))
            if missing:
                errors.extend(f"missing_required_file:{name}" for name in missing)
            extras = sorted(set(names) - EXPECTED_PROMPT_PACK_FILES)
            if extras:
                warnings.append(f"extra_files_present:{','.join(extras)}")
            if not missing:
                declared_hashes = _check_zip_hashes(
                    zip_obj,
                    required_names=EXPECTED_PROMPT_PACK_FILES,
                    errors=errors,
                    warnings=warnings,
                )
            try:
                manifest = _zip_read_json(zip_obj, "MANIFEST.json")
                _check_manifest_hashes(zip_obj, manifest, errors=errors, warnings=warnings)
            except Exception as exc:
                errors.append(f"manifest_json_unreadable:{exc}")
            try:
                task_pack = _zip_read_json(zip_obj, "task_pack.json")
                task_id = str(task_pack.get("task_id", "")).strip()
                required_starting_head = str(task_pack.get("required_starting_head", "")).strip()
                gate = task_pack.get("creation_gate")
                if not isinstance(gate, dict):
                    warnings.append("creation_gate_missing")
                else:
                    phrase = gate.get("owner_trigger_phrase_exact")
                    verified = gate.get("trigger_phrase_verified_by_logos")
                    if phrase != OWNER_TRIGGER_PHRASE:
                        warnings.append("owner_trigger_phrase_not_exact")
                    if verified is not True:
                        warnings.append("trigger_phrase_not_verified_by_logos")
            except Exception as exc:
                errors.append(f"task_pack_json_unreadable:{exc}")
            if not task_id:
                warnings.append("task_id_missing_or_empty")

    ensure_transfer_dirs(runtime_root)
    payload_sha = sha256_file(pack_path) if pack_path.exists() else ""
    return {
        "report_type": "ADMINISTRATUM_TRANSFER_PROMPT_PACK_VERIFICATION_V0_1",
        "verified_at_utc": now_utc(),
        "pack_zip": str(pack_path),
        "payload_sha256": payload_sha,
        "required_files": sorted(EXPECTED_PROMPT_PACK_FILES),
        "zip_files": names,
        "sha256_entries": declared_hashes,
        "manifest_task_id": str(manifest.get("task_id", "")),
        "task_id": task_id or str(manifest.get("task_id", "")),
        "required_starting_head": required_starting_head or str(manifest.get("required_starting_head", "")),
        "target_actor": str(task_pack.get("target_actor", manifest.get("target_actor", ""))) if task_pack else "",
        "creation_gate": task_pack.get("creation_gate", {}) if task_pack else {},
        "warnings": warnings,
        "errors": errors,
        "verdict": _result_verdict(errors, warnings),
    }


def _make_ids(task_id: str, step_name: str, payload_sha256: str) -> Tuple[str, str]:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    transfer_hash = hashlib.sha256(f"{task_id}|{step_name}|{payload_sha256}|{stamp}".encode("utf-8")).hexdigest()[:10]
    corr_hash = hashlib.sha256(f"{task_id}|{payload_sha256}".encode("utf-8")).hexdigest()[:12]
    return f"TRANSFER-{stamp}-{transfer_hash}", f"CORR-{corr_hash}"


def _quarantine_copy(source: Path, runtime_root: Path, task_id: str, reason: str) -> str:
    dirs = ensure_transfer_dirs(runtime_root)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_task = task_id or "UNKNOWN_TASK"
    target_dir = dirs["quarantine"] / safe_task
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{stamp}__{reason}__{source.name}"
    shutil.copy2(source, target)
    return str(target)


def send_vm2_prompt_pack(
    pack_zip: Path,
    *,
    step_name: str,
    source_head: str,
    runtime_root: Path = DEFAULT_TRANSFER_ROOT,
    operator: str = "OWNER",
) -> Dict[str, Any]:
    dirs = ensure_transfer_dirs(runtime_root)
    verification = verify_prompt_pack(pack_zip, runtime_root)
    task_id = str(verification.get("task_id") or "UNKNOWN_TASK")
    if verification["verdict"] == "BLOCKED":
        quarantine_path = ""
        pack_path = pack_zip.expanduser().resolve()
        if pack_path.exists():
            quarantine_path = _quarantine_copy(pack_path, runtime_root, task_id, "invalid_prompt_pack")
        result = {
            "report_type": "ADMINISTRATUM_TRANSFER_SEND_VM2_V0_1",
            "created_at_utc": now_utc(),
            "task_id": task_id,
            "step_name": step_name,
            "verification": verification,
            "quarantine_path": quarantine_path,
            "verdict": "BLOCKED_INVALID_PROMPT_PACK",
        }
        append_jsonl(dirs["ledger"] / LEDGER_NAME, result)
        return result

    transfer_id, correlation_id = _make_ids(task_id, step_name, str(verification.get("payload_sha256", "")))
    received_dir = dirs["received_vm2"] / task_id
    received_dir.mkdir(parents=True, exist_ok=True)
    source_zip = pack_zip.expanduser().resolve()
    target_zip = received_dir / source_zip.name
    shutil.copy2(source_zip, target_zip)
    receipt = {
        "receipt_type": "ADMINISTRATUM_TRANSFER_RECEIPT_V0_1",
        "transfer_id": transfer_id,
        "correlation_id": correlation_id,
        "source_actor": "LOGOS_PRIME",
        "operator": operator,
        "gateway": "ADMINISTRATUM_AGENT",
        "target_actor": "VM2_SERVITOR",
        "route": "PC_TO_VM2",
        "step_name": step_name,
        "task_id": task_id,
        "payload_sha256": str(verification.get("payload_sha256", "")),
        "source_head": source_head,
        "signed_at_utc": now_utc(),
        "source_zip": str(source_zip),
        "received_zip": str(target_zip),
        "verification_verdict": verification["verdict"],
        "warnings": list(verification.get("warnings", [])),
        "verdict": "SIGNED_FOR_MANUAL_VM2_TRANSFER",
    }
    receipt_path = dirs["ledger_receipts"] / f"{transfer_id}_receipt.json"
    received_receipt_path = received_dir / f"{transfer_id}_receipt.json"
    write_json(receipt_path, receipt)
    write_json(received_receipt_path, receipt)
    ledger_entry = {
        "event": "PROMPT_PACK_SIGNED_FOR_VM2",
        "recorded_at_utc": now_utc(),
        "transfer_id": transfer_id,
        "correlation_id": correlation_id,
        "task_id": task_id,
        "step_name": step_name,
        "payload_sha256": receipt["payload_sha256"],
        "received_zip": str(target_zip),
        "receipt_path": str(receipt_path),
        "verdict": receipt["verdict"],
    }
    append_jsonl(dirs["ledger"] / LEDGER_NAME, ledger_entry)
    return {
        "report_type": "ADMINISTRATUM_TRANSFER_SEND_VM2_V0_1",
        "created_at_utc": now_utc(),
        "task_id": task_id,
        "transfer_id": transfer_id,
        "correlation_id": correlation_id,
        "step_name": step_name,
        "received_zip": str(target_zip),
        "receipt_path": str(receipt_path),
        "received_receipt_path": str(received_receipt_path),
        "ledger_path": str(dirs["ledger"] / LEDGER_NAME),
        "verification": verification,
        "warnings": list(verification.get("warnings", [])),
        "verdict": receipt["verdict"],
    }


def _metadata_correlation(metadata: Dict[str, Any]) -> str:
    direct = metadata.get("correlation_id")
    if isinstance(direct, str) and direct:
        return direct
    transfer = metadata.get("transfer")
    if isinstance(transfer, dict):
        nested = transfer.get("correlation_id")
        if isinstance(nested, str):
            return nested
    return ""


def verify_response_bundle(
    response_zip: Path,
    *,
    task_id: str,
    expected_filename: str,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    path = response_zip.expanduser().resolve()
    errors: List[str] = []
    warnings: List[str] = []
    names: List[str] = []
    metadata: Dict[str, Any] = {}
    declared_hashes: Dict[str, str] = {}

    if path.name != expected_filename:
        errors.append("response_filename_not_exact")
    if not path.exists():
        errors.append("response_bundle_not_found")
    elif not zipfile.is_zipfile(path):
        errors.append("response_bundle_not_a_zip")
    else:
        with zipfile.ZipFile(path, "r") as zip_obj:
            names = _zip_names(zip_obj)
            missing = sorted(EXPECTED_RESPONSE_FILES - set(names))
            if missing:
                errors.extend(f"missing_response_file:{name}" for name in missing)
            if "SHA256SUMS.txt" in names:
                declared_hashes = _check_zip_hashes(
                    zip_obj,
                    required_names=[name for name in EXPECTED_RESPONSE_FILES if name in names],
                    errors=errors,
                    warnings=warnings,
                )
            else:
                errors.append("response_sha256sums_missing")
            try:
                metadata = _zip_read_json(zip_obj, "final_report.json")
            except Exception as exc:
                errors.append(f"final_report_json_unreadable:{exc}")
            try:
                manifest = _zip_read_json(zip_obj, "MANIFEST.json")
                _check_manifest_hashes(zip_obj, manifest, errors=errors, warnings=warnings)
            except Exception as exc:
                errors.append(f"response_manifest_json_unreadable:{exc}")

    metadata_task_id = str(metadata.get("task_id", ""))
    metadata_correlation_id = _metadata_correlation(metadata)
    if metadata_task_id and metadata_task_id != task_id:
        errors.append("response_task_id_mismatch")
    if not metadata_task_id:
        errors.append("response_task_id_missing")
    if correlation_id and metadata_correlation_id != correlation_id:
        errors.append("response_correlation_id_mismatch")

    return {
        "report_type": "ADMINISTRATUM_TRANSFER_RESPONSE_BUNDLE_VERIFICATION_V0_1",
        "verified_at_utc": now_utc(),
        "response_zip": str(path),
        "expected_filename": expected_filename,
        "task_id": task_id,
        "metadata_task_id": metadata_task_id,
        "expected_correlation_id": correlation_id or "",
        "metadata_correlation_id": metadata_correlation_id,
        "payload_sha256": sha256_file(path) if path.exists() else "",
        "zip_files": names,
        "sha256_entries": declared_hashes,
        "warnings": warnings,
        "errors": errors,
        "verdict": _result_verdict(errors, warnings),
    }


def fetch_vm2_response_bundle(
    *,
    task_id: str,
    expected_filename: Optional[str] = None,
    correlation_id: Optional[str] = None,
    runtime_root: Path = DEFAULT_TRANSFER_ROOT,
    quarantine_on_mismatch: bool = True,
) -> Dict[str, Any]:
    dirs = ensure_transfer_dirs(runtime_root)
    filename = expected_filename or f"{task_id}__VM2_RESPONSE_BUNDLE.zip"
    response_path = dirs["outbox_vm2_to_pc"] / task_id / filename
    verification = verify_response_bundle(
        response_path,
        task_id=task_id,
        expected_filename=filename,
        correlation_id=correlation_id,
    )
    quarantine_path = ""
    if verification["verdict"] == "BLOCKED" and response_path.exists() and quarantine_on_mismatch:
        quarantine_path = _quarantine_copy(response_path, runtime_root, task_id, "response_mismatch")
    event = {
        "event": "VM2_RESPONSE_FETCH",
        "recorded_at_utc": now_utc(),
        "task_id": task_id,
        "expected_filename": filename,
        "response_zip": str(response_path),
        "correlation_id": correlation_id or "",
        "verification_verdict": verification["verdict"],
        "quarantine_path": quarantine_path,
        "verdict": "FETCHED_VERIFIED" if verification["verdict"] != "BLOCKED" else "BLOCKED_RESPONSE_MISMATCH",
    }
    receipt_name = f"FETCH-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{task_id}_receipt.json"
    receipt_path = dirs["ledger_receipts"] / receipt_name
    write_json(receipt_path, {"receipt_type": "ADMINISTRATUM_TRANSFER_FETCH_RECEIPT_V0_1", **event, "verification": verification})
    append_jsonl(dirs["ledger"] / LEDGER_NAME, event)
    return {
        "report_type": "ADMINISTRATUM_TRANSFER_FETCH_VM2_V0_1",
        "created_at_utc": now_utc(),
        "task_id": task_id,
        "expected_filename": filename,
        "response_zip": str(response_path),
        "receipt_path": str(receipt_path),
        "ledger_path": str(dirs["ledger"] / LEDGER_NAME),
        "quarantine_path": quarantine_path,
        "verification": verification,
        "warnings": list(verification.get("warnings", [])),
        "errors": list(verification.get("errors", [])),
        "verdict": event["verdict"],
    }


def transfer_status(runtime_root: Path = DEFAULT_TRANSFER_ROOT, *, ledger_tail: int = 5) -> Dict[str, Any]:
    dirs = ensure_transfer_dirs(runtime_root)
    ledger_path = dirs["ledger"] / LEDGER_NAME
    lines: List[str] = []
    if ledger_path.exists():
        lines = [line for line in ledger_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    latest: List[Dict[str, Any]] = []
    for raw in lines[-ledger_tail:]:
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                latest.append(parsed)
        except Exception:
            latest.append({"unparsed": raw[:200]})
    folder_counts = {
        key: sum(1 for _ in path.rglob("*") if _.is_file())
        for key, path in dirs.items()
        if key != "root"
    }
    return {
        "report_type": "ADMINISTRATUM_TRANSFER_STATUS_V0_1",
        "generated_at_utc": now_utc(),
        "runtime_root": str(dirs["root"]),
        "required_dirs": {key: str(path) for key, path in dirs.items() if key != "root"},
        "folder_file_counts": folder_counts,
        "ledger_path": str(ledger_path),
        "ledger_entries": len(lines),
        "latest_ledger_entries": latest,
        "verdict": "PASS",
    }
