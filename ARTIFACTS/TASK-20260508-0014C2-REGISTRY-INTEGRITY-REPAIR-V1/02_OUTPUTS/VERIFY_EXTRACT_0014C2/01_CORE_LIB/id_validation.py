#!/usr/bin/env python3
"""Identity and enum validation helpers for IMPERIUM pipeline scripts."""

from __future__ import annotations

import re
from typing import Iterable

TASK_ID_RE = re.compile(r"^TASK-\d{8}-\d{4}[A-Z0-9-]*-[A-Z0-9-]+$")
STAGE_ID_RE = re.compile(r"^STAGE-[A-Z0-9][A-Z0-9-]*$")
RUN_ID_RE = re.compile(r"^RUN-\d{8}-\d{4,}$")
PRODUCER_ID_RE = re.compile(r"^[A-Za-z0-9_.:-]{3,128}$")

ALLOWED_CONTOUR_IDS = {"PC", "VM2", "OWNER_MANUAL"}
ALLOWED_PRODUCER_TYPES = {"PC_SERVITOR", "VM2_WORKER", "OWNER_MANUAL"}
ALLOWED_EVENT_TYPES = {
    "TASK_CREATED",
    "STAGE_DECLARED",
    "STAGE_DISPATCHED",
    "STAGE_STARTED",
    "STAGE_PROGRESS",
    "STAGE_COMPLETED",
    "STAGE_FAILED",
    "BUNDLE_CREATED",
    "BUNDLE_FETCHED",
    "HASH_VERIFIED",
    "MANIFEST_VERIFIED",
    "RECEIPT_VERIFIED",
    "BARRIER_PASS",
    "BARRIER_FAIL",
    "BARRIER_WAITING",
    "BARRIER_CONFLICT",
    "ORIGIN_CONFLICT",
    "FINAL_BUNDLE_CREATED",
    "SPECULUM_REVIEW_REQUESTED",
}


def _ensure_nonempty(value: str, field_name: str) -> str:
    if value is None or str(value).strip() == "":
        raise ValueError(f"{field_name} is required")
    return str(value).strip()


def validate_task_id(task_id: str) -> str:
    task_id = _ensure_nonempty(task_id, "task_id")
    if not TASK_ID_RE.fullmatch(task_id):
        raise ValueError(f"Invalid TASK_ID format: {task_id}")
    return task_id


def validate_stage_id(stage_id: str) -> str:
    stage_id = _ensure_nonempty(stage_id, "stage_id")
    if not STAGE_ID_RE.fullmatch(stage_id):
        raise ValueError(f"Invalid STAGE_ID format: {stage_id}")
    return stage_id


def validate_run_id(run_id: str) -> str:
    run_id = _ensure_nonempty(run_id, "run_id")
    if not RUN_ID_RE.fullmatch(run_id):
        raise ValueError(f"Invalid RUN_ID format: {run_id}")
    return run_id


def validate_contour_id(contour_id: str) -> str:
    contour_id = _ensure_nonempty(contour_id, "contour_id")
    if contour_id not in ALLOWED_CONTOUR_IDS:
        raise ValueError(f"Invalid CONTOUR_ID: {contour_id}")
    return contour_id


def validate_producer_type(producer_type: str) -> str:
    producer_type = _ensure_nonempty(producer_type, "producer_type")
    if producer_type not in ALLOWED_PRODUCER_TYPES:
        raise ValueError(f"Invalid producer_type: {producer_type}")
    return producer_type


def validate_producer_id(producer_id: str) -> str:
    producer_id = _ensure_nonempty(producer_id, "producer_id")
    if not PRODUCER_ID_RE.fullmatch(producer_id):
        raise ValueError(f"Invalid producer_id format: {producer_id}")
    return producer_id


def validate_event_type(event_type: str) -> str:
    event_type = _ensure_nonempty(event_type, "event_type")
    if event_type not in ALLOWED_EVENT_TYPES:
        raise ValueError(f"Invalid event_type: {event_type}")
    return event_type


def ensure_required(values: dict, required_fields: Iterable[str]) -> None:
    missing = [field for field in required_fields if not values.get(field)]
    if missing:
        raise ValueError("Missing required fields: " + ", ".join(missing))
