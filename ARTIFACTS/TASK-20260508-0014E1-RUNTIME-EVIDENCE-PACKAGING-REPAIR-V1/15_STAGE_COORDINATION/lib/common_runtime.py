#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ALLOWED_CONTOURS = {"PC", "VM2", "OWNER_MANUAL", "LOCAL_TEST"}
LATEST_RE = re.compile(r"(latest|newest|most[-_ ]?recent)", re.IGNORECASE)
ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9._-]*$")


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def has_latest_pattern(value: str) -> bool:
    return bool(LATEST_RE.search(value or ""))


def canonical_json_bytes(data: Dict[str, Any]) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def resolve_within_task_root(task_root: Path, target: Path, allow_nonexistent: bool = True) -> Path:
    root = task_root.resolve()
    candidate = target
    if not candidate.is_absolute():
        candidate = (root / candidate)
    if allow_nonexistent:
        resolved_parent = candidate.parent.resolve()
        if resolved_parent != root and root not in resolved_parent.parents:
            raise ValueError(f"Path outside task root: {target}")
        return candidate
    resolved = candidate.resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"Path outside task root: {target}")
    return resolved


def add_common_args(parser: argparse.ArgumentParser, include_receipt: bool = True, receipt_required: bool = False) -> None:
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--stage-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--contour-id", required=True)
    parser.add_argument("--actor-id", required=True)
    parser.add_argument("--tool-id", required=True)
    parser.add_argument("--task-root", required=True)
    if include_receipt:
        parser.add_argument("--receipt-out", required=receipt_required)
    parser.add_argument("--fail-closed", action="store_true")
    parser.add_argument("--no-throne", action="store_true")
    parser.add_argument("--no-autosync", action="store_true")
    parser.add_argument("--no-delete", action="store_true")


def validate_identity(args: argparse.Namespace) -> List[str]:
    errors: List[str] = []
    values = {
        "task_id": args.task_id,
        "stage_id": args.stage_id,
        "run_id": args.run_id,
        "contour_id": args.contour_id,
        "actor_id": args.actor_id,
        "tool_id": args.tool_id,
    }
    for key, value in values.items():
        if not value:
            errors.append(f"missing_{key}")
            continue
        if ".." in value:
            errors.append(f"path_traversal_{key}")
        if has_latest_pattern(value):
            errors.append(f"latest_pattern_{key}")
        if key != "contour_id" and not ID_RE.match(value):
            errors.append(f"invalid_format_{key}")

    if args.contour_id and args.contour_id not in ALLOWED_CONTOURS:
        errors.append("invalid_contour_id")

    try:
        root = Path(args.task_root)
        if has_latest_pattern(str(root)):
            errors.append("latest_pattern_task_root")
        if not root.exists():
            errors.append("task_root_not_exists")
    except Exception:
        errors.append("invalid_task_root")

    if not args.no_throne:
        errors.append("no_throne_flag_required")
    if not args.no_autosync:
        errors.append("no_autosync_flag_required")
    if not args.no_delete:
        errors.append("no_delete_flag_required")

    return errors


def identity_block(args: argparse.Namespace) -> Dict[str, str]:
    return {
        "task_id": args.task_id,
        "stage_id": args.stage_id,
        "run_id": args.run_id,
        "contour_id": args.contour_id,
        "actor_id": args.actor_id,
        "tool_id": args.tool_id,
        "timestamp_utc": now_utc(),
    }


def write_receipt(args: argparse.Namespace, status: str, action: str, failure_reason: Optional[str] = None, extra: Optional[Dict[str, Any]] = None, receipt_path: Optional[Path] = None) -> Optional[Path]:
    rec_arg = getattr(args, "receipt_out", None)
    target = receipt_path or (Path(rec_arg) if rec_arg else None)
    if target is None:
        return None
    task_root = Path(args.task_root)
    target = resolve_within_task_root(task_root, target)
    payload: Dict[str, Any] = {
        **identity_block(args),
        "action": action,
        "status": status,
        "failure_reason": failure_reason,
        "no_vm2_contact": True,
        "no_real_e2e": True,
        "no_throne": True,
        "no_watchers": True,
        "no_latest": True,
    }
    if extra:
        payload.update(extra)
    write_json(target, payload)
    return target


def owner_report(step: str, bundle: str, verdict: str, lines: List[str]) -> None:
    print("ШАГ:")
    print(step)
    print("")
    print("БАНДЛ:")
    print(bundle)
    print("")
    print("ВЕРДИКТ:")
    print(verdict)
    print("")
    print("КОММЕНТАРИЙ ДЛЯ OWNER:")
    for ln in lines[:4]:
        print(ln)


def build_event(args: argparse.Namespace, event_type: str, status: str, evidence_refs: Optional[List[str]] = None, extra: Optional[Dict[str, Any]] = None, previous_event_hash: Optional[str] = None) -> Dict[str, Any]:
    event: Dict[str, Any] = {
        "event_id": f"EVT-{uuid.uuid4()}",
        **identity_block(args),
        "event_type": event_type,
        "status": status,
        "evidence_refs": evidence_refs or [],
        "previous_event_hash": previous_event_hash,
    }
    if extra:
        event.update(extra)
    to_hash = dict(event)
    event_hash = sha256_bytes(canonical_json_bytes(to_hash))
    event["event_hash"] = event_hash
    return event


def read_ledger_events(ledger_path: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
    events: List[Dict[str, Any]] = []
    errors: List[str] = []
    if not ledger_path.exists():
        return events, errors
    for idx, line in enumerate(ledger_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except Exception as exc:
            errors.append(f"invalid_json_line_{idx}:{exc}")
    return events, errors


def append_ledger_event(args: argparse.Namespace, ledger_path: Path, event_type: str, status: str, evidence_refs: Optional[List[str]] = None, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    task_root = Path(args.task_root)
    ledger_path = resolve_within_task_root(task_root, ledger_path)
    events, errors = read_ledger_events(ledger_path)
    if errors:
        raise ValueError("ledger_parse_error:" + ";".join(errors))
    previous_hash = events[-1].get("event_hash") if events else None
    event = build_event(args, event_type=event_type, status=status, evidence_refs=evidence_refs, extra=extra, previous_event_hash=previous_hash)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    return event


def verify_event_hash(event: Dict[str, Any]) -> bool:
    given = event.get("event_hash")
    if not given:
        return False
    probe = dict(event)
    probe.pop("event_hash", None)
    expected = sha256_bytes(canonical_json_bytes(probe))
    return expected == given


def ensure_file_exists(path: Path, name: str) -> None:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"{name}_missing:{path}")


def load_signal_and_verify(signal_path: Path) -> Dict[str, Any]:
    signal = read_json(signal_path)
    signal_hash = signal.get("signal_hash")
    if not signal_hash:
        raise ValueError("signal_hash_missing")
    probe = dict(signal)
    probe.pop("signal_hash", None)
    expected = sha256_bytes(canonical_json_bytes(probe))
    if expected != signal_hash:
        raise ValueError("signal_hash_mismatch")
    return signal


def write_failure_and_report(args: argparse.Namespace, step: str, reason: str, bundle: str = "N/A", receipt_path: Optional[Path] = None, action: str = "runtime_action", extra: Optional[Dict[str, Any]] = None, verdict: str = "FAIL") -> int:
    try:
        write_receipt(args, status="FAIL", action=action, failure_reason=reason, extra=extra, receipt_path=receipt_path)
    except Exception:
        pass
    owner_report(step, bundle, verdict, [
        f"Выполнена локальная проверка для {step}.",
        f"Операция остановлена: {reason}.",
        "VM2/E2E/THRONE/watchers не использовались.",
        "Требуется исправление входных данных или контракта.",
    ])
    return 1
