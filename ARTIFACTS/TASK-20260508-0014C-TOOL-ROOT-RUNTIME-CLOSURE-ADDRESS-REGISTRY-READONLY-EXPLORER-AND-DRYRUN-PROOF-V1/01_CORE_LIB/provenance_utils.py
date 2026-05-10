#!/usr/bin/env python3
"""Provenance utilities for strict origin tracking."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = [
    "task_id",
    "stage_id",
    "run_id",
    "contour_id",
    "producer_type",
    "producer_id",
    "executor_role",
    "creation_mode",
    "created_at_utc",
    "produced_on_host_class",
    "source_bundle_name",
    "source_bundle_sha256",
    "parent_bundle_refs",
    "transfer_method",
    "transfer_actor",
    "manual_touchpoints",
    "authority_level",
    "acceptance_scope",
    "verification_status",
]

ALLOWED_CONTOUR_IDS = {"PC", "VM2", "OWNER_MANUAL"}
ALLOWED_PRODUCER_TYPES = {"PC_SERVITOR", "VM2_WORKER", "OWNER_MANUAL"}
ALLOWED_CREATION_MODES = {"SCRIPTED", "MANUAL", "SEMI_MANUAL"}
ALLOWED_TRANSFER_METHODS = {"LOCAL_CREATE", "SSH_SEND", "SSH_FETCH", "MANUAL_COPY", "MANUAL_UPLOAD", "NONE"}
ALLOWED_AUTHORITY_LEVELS = {
    "WORKING_ARTIFACT",
    "STAGE_OUTPUT",
    "FETCHED_STAGE_BUNDLE",
    "VERIFIED_STAGE_BUNDLE",
    "FINAL_TASK_BUNDLE",
    "REVIEW_REQUEST",
    "BLOCKED_ARTIFACT",
}
ALLOWED_VERIFICATION_STATUS = {
    "UNVERIFIED",
    "HASH_VERIFIED",
    "MANIFEST_VERIFIED",
    "RECEIPT_VERIFIED",
    "BARRIER_PASSED",
    "BARRIER_FAILED",
    "REJECTED",
}
ALLOWED_SOURCE_BUNDLE_SHA256_STATUS = {
    "EMBEDDED",
    "EXTERNAL_HASH_RECORDED_IN_SIDECAR",
    "NOT_APPLICABLE",
}
SHA256_HEX_RE = re.compile(r"^[a-fA-F0-9]{64}$")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def create_provenance_record(**kwargs: Any) -> dict[str, Any]:
    record: dict[str, Any] = {field: kwargs.get(field) for field in REQUIRED_FIELDS}
    for key, value in kwargs.items():
        if key not in record:
            record[key] = value
    if not record.get("created_at_utc"):
        record["created_at_utc"] = utc_now()
    if record.get("parent_bundle_refs") is None:
        record["parent_bundle_refs"] = []
    if record.get("manual_touchpoints") is None:
        record["manual_touchpoints"] = []
    return record


def validate_provenance(record: dict[str, Any], strict_acceptance: bool = True) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in record:
            errors.append(f"missing provenance field: {field}")
            continue
        value = record[field]
        if field == "source_bundle_sha256":
            status = str(record.get("source_bundle_sha256_status", "")).strip()
            if value is None or (isinstance(value, str) and value.strip() == ""):
                if status != "EXTERNAL_HASH_RECORDED_IN_SIDECAR":
                    errors.append("empty provenance field: source_bundle_sha256")
                continue
            normalized = str(value).strip()
            if normalized.upper() == "PENDING":
                errors.append("source_bundle_sha256 cannot be PENDING")
            elif not SHA256_HEX_RE.fullmatch(normalized):
                errors.append("source_bundle_sha256 must be 64-char hex when provided")
            continue
        if value is None or (isinstance(value, str) and value.strip() == ""):
            errors.append(f"empty provenance field: {field}")

    sha_status = record.get("source_bundle_sha256_status")
    if sha_status is not None and sha_status not in ALLOWED_SOURCE_BUNDLE_SHA256_STATUS:
        errors.append("invalid source_bundle_sha256_status")

    if record.get("contour_id") not in ALLOWED_CONTOUR_IDS:
        errors.append("invalid contour_id")
    if record.get("producer_type") not in ALLOWED_PRODUCER_TYPES:
        errors.append("invalid producer_type")
    if record.get("creation_mode") not in ALLOWED_CREATION_MODES:
        errors.append("invalid creation_mode")
    if record.get("transfer_method") not in ALLOWED_TRANSFER_METHODS:
        errors.append("invalid transfer_method")
    if record.get("authority_level") not in ALLOWED_AUTHORITY_LEVELS:
        errors.append("invalid authority_level")
    if record.get("verification_status") not in ALLOWED_VERIFICATION_STATUS:
        errors.append("invalid verification_status")

    if strict_acceptance and record.get("producer_type") == "UNKNOWN":
        errors.append("UNKNOWN producer_type is forbidden for accepted artifacts")

    if record.get("producer_type") == "OWNER_MANUAL" and record.get("creation_mode") == "SCRIPTED":
        errors.append("OWNER_MANUAL artifacts cannot declare SCRIPTED creation_mode")

    if record.get("contour_id") == "VM2" and record.get("authority_level") == "FINAL_TASK_BUNDLE":
        errors.append("VM2 cannot claim FINAL_TASK_BUNDLE authority")

    return errors


def write_provenance(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2), encoding="utf-8")


def read_provenance(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def origin_index_key(record: dict[str, Any], artifact_sha256: str) -> str:
    return "|".join(
        [
            str(record.get("task_id", "")),
            str(record.get("stage_id", "")),
            str(record.get("run_id", "")),
            str(record.get("contour_id", "")),
            str(record.get("producer_type", "")),
            str(record.get("producer_id", "")),
            artifact_sha256.lower().strip(),
        ]
    )


def _origin_base_key(record: dict[str, Any]) -> str:
    return "|".join(
        [
            str(record.get("task_id", "")),
            str(record.get("stage_id", "")),
            str(record.get("run_id", "")),
            str(record.get("contour_id", "")),
            str(record.get("producer_type", "")),
            str(record.get("producer_id", "")),
        ]
    )


def update_origin_index(
    index_path: Path,
    record: dict[str, Any],
    artifact_name: str,
    artifact_path: str,
    artifact_sha256: str,
    provenance_ref: str,
    receipt_ref: str,
) -> dict[str, Any]:
    index_path.parent.mkdir(parents=True, exist_ok=True)
    if index_path.exists():
        data = json.loads(index_path.read_text(encoding="utf-8"))
    else:
        data = {"index_version": "ORIGIN_INDEX_SCHEMA_V1", "items": []}

    if "items" not in data or not isinstance(data["items"], list):
        data["items"] = []

    base_key = _origin_base_key(record)
    full_key = origin_index_key(record, artifact_sha256)
    status = "UNIQUE"

    same_base = [item for item in data["items"] if item.get("base_key") == base_key]
    for item in same_base:
        existing_sha = str(item.get("artifact_sha256", "")).lower()
        if existing_sha == artifact_sha256.lower().strip():
            status = "DUPLICATE_SAME_HASH"
        else:
            status = "CONFLICT_DIFFERENT_HASH"
            break

    new_item = {
        "origin_key": full_key,
        "base_key": base_key,
        "task_id": record.get("task_id"),
        "stage_id": record.get("stage_id"),
        "run_id": record.get("run_id"),
        "contour_id": record.get("contour_id"),
        "producer_type": record.get("producer_type"),
        "producer_id": record.get("producer_id"),
        "artifact_name": artifact_name,
        "artifact_path": artifact_path,
        "artifact_sha256": artifact_sha256.lower().strip(),
        "provenance_ref": provenance_ref,
        "receipt_ref": receipt_ref,
        "origin_status": status,
        "updated_at_utc": utc_now(),
    }
    data["items"].append(new_item)
    index_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return new_item
