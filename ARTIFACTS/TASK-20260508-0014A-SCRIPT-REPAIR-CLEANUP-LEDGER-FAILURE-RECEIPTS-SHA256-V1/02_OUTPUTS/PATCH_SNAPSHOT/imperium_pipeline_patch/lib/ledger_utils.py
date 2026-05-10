#!/usr/bin/env python3
"""Append-only JSONL ledger utilities."""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .id_validation import (
    validate_contour_id,
    validate_event_type,
    validate_producer_id,
    validate_producer_type,
    validate_run_id,
    validate_stage_id,
    validate_task_id,
)

REQUIRED_EVENT_FIELDS = [
    "task_id",
    "stage_id",
    "run_id",
    "contour_id",
    "producer_type",
    "producer_id",
    "event_type",
    "status",
    "artifact_ref",
    "artifact_sha256",
    "previous_event_ref",
    "timestamp_utc",
    "receipt_ref",
    "notes",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


_ISO_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def _normalize_timestamp_utc(value: Any) -> str:
    if value is None:
        return _utc_now()
    text = str(value).strip()
    if not text:
        return _utc_now()
    if _ISO_UTC_RE.fullmatch(text):
        return text

    candidate = text.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise ValueError(f"Invalid timestamp_utc format: {value}") from exc

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    parsed_utc = parsed.astimezone(timezone.utc)
    return parsed_utc.strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_lines(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Malformed ledger JSONL at line {index}: {exc}") from exc
    return events


def append_event(ledger_path: Path, event: dict[str, Any]) -> dict[str, Any]:
    validate_task_id(event.get("task_id", ""))
    validate_stage_id(event.get("stage_id", ""))
    validate_run_id(event.get("run_id", ""))
    validate_contour_id(event.get("contour_id", ""))
    validate_producer_type(event.get("producer_type", ""))
    validate_producer_id(event.get("producer_id", ""))
    validate_event_type(event.get("event_type", ""))

    existing = _read_lines(ledger_path)
    previous_event_ref = existing[-1].get("event_id", "") if existing else "NONE"

    output_event = dict(event)
    output_event.setdefault("event_id", f"EVT-{uuid.uuid4()}")
    output_event["timestamp_utc"] = _normalize_timestamp_utc(output_event.get("timestamp_utc"))
    output_event.setdefault("artifact_ref", "")
    output_event.setdefault("artifact_sha256", "")
    output_event.setdefault("receipt_ref", "")
    output_event.setdefault("notes", "")
    output_event["previous_event_ref"] = output_event.get("previous_event_ref") or previous_event_ref

    for field in REQUIRED_EVENT_FIELDS:
        if field not in output_event:
            raise ValueError(f"Missing required ledger field: {field}")

    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(output_event, ensure_ascii=False) + "\n")
    return output_event


def read_ledger(ledger_path: Path) -> list[dict[str, Any]]:
    return _read_lines(ledger_path)


def summarize_task_state(ledger_path: Path, task_id: str) -> dict[str, Any]:
    validate_task_id(task_id)
    events = [event for event in _read_lines(ledger_path) if event.get("task_id") == task_id]
    by_stage: dict[str, dict[str, Any]] = {}
    active_runs: list[str] = []
    failed_runs: list[str] = []
    conflicts: list[str] = []
    barrier_events: list[str] = []
    final_bundle_created = False

    for event in events:
        stage = event.get("stage_id", "")
        by_stage[stage] = event
        status = str(event.get("status", "")).upper()
        run_id = str(event.get("run_id", ""))
        event_type = str(event.get("event_type", ""))

        if status in {"RUNNING", "DISPATCHED", "STARTED", "PROGRESS"}:
            if run_id not in active_runs:
                active_runs.append(run_id)
        if status in {"FAIL", "FAILED", "BLOCKED"} or event_type == "STAGE_FAILED":
            if run_id not in failed_runs:
                failed_runs.append(run_id)
        if event_type in {"BARRIER_CONFLICT", "ORIGIN_CONFLICT"}:
            conflicts.append(event.get("event_id", ""))
        if event_type.startswith("BARRIER_"):
            barrier_events.append(event_type)
        if event_type == "FINAL_BUNDLE_CREATED":
            final_bundle_created = True

    overall = "WAITING"
    if conflicts:
        overall = "CONFLICT"
    elif failed_runs:
        overall = "FAIL"
    elif final_bundle_created:
        overall = "COMPLETED"
    elif active_runs:
        overall = "RUNNING"
    elif events:
        overall = "WAITING"
    else:
        overall = "BLOCKED"

    return {
        "task_id": task_id,
        "overall_status": overall,
        "event_count": len(events),
        "stages_found": sorted([stage for stage in by_stage.keys() if stage]),
        "latest_event_per_stage": by_stage,
        "active_runs": active_runs,
        "failed_runs": failed_runs,
        "conflicts": conflicts,
        "barrier_events": barrier_events,
        "final_bundle_created": final_bundle_created,
    }
