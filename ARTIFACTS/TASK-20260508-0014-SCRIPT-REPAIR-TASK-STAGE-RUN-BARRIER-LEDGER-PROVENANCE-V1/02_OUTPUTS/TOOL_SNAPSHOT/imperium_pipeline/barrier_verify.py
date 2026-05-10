#!/usr/bin/env python3
"""Barrier verification reducer for IMPERIUM task evidence."""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from lib.id_validation import validate_task_id  # noqa: E402
from lib.ledger_utils import append_event, read_ledger  # noqa: E402
from lib.owner_report import print_owner_report, write_owner_report  # noqa: E402
from lib.path_safety import assert_no_latest_pattern  # noqa: E402
from lib.provenance_utils import read_provenance, validate_provenance  # noqa: E402
from lib.sha256_utils import parse_sha256_file  # noqa: E402


def _load_expected_stages(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]

    if isinstance(data, list):
        if all(isinstance(item, str) for item in data):
            return [item for item in data if item]
        stage_ids = []
        for item in data:
            if isinstance(item, dict) and item.get("stage_id"):
                stage_ids.append(str(item["stage_id"]))
        return stage_ids

    if isinstance(data, dict):
        if isinstance(data.get("stages"), list):
            stages = data["stages"]
            stage_ids = []
            for item in stages:
                if isinstance(item, str):
                    stage_ids.append(item)
                elif isinstance(item, dict) and item.get("stage_id"):
                    stage_ids.append(str(item["stage_id"]))
            return stage_ids
    raise ValueError("Unable to parse expected stage map")


def _extract_internal_file(bundle_path: Path, name_hint: str, output_path: Path) -> Path | None:
    with zipfile.ZipFile(bundle_path, "r") as archive:
        for member in archive.namelist():
            if name_hint.lower() in member.lower() and not member.endswith("/"):
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_bytes(archive.read(member))
                return output_path
    return None


def _bundle_has_name_hint(bundle_path: Path, hint: str) -> bool:
    with zipfile.ZipFile(bundle_path, "r") as archive:
        return any(hint.lower() in name.lower() for name in archive.namelist())


def _load_origin_index(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Origin index not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Barrier verification for IMPERIUM bundles")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--expected-stage-map", required=True)
    parser.add_argument("--bundle-path", required=True)
    parser.add_argument("--manifest-path", default="")
    parser.add_argument("--sha256s-path", default="")
    parser.add_argument("--ledger-path", required=True)
    parser.add_argument("--origin-index-path", required=True)
    parser.add_argument("--output-report", required=True)
    parser.add_argument("--output-receipt", required=True)
    parser.add_argument("--producer-id", required=True)
    parser.add_argument("--owner-report-output", default="")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    task_id = args.task_id
    verdict = "FAIL"
    barrier_result = "BARRIER_FAIL"
    reasons_fail: list[str] = []
    reasons_waiting: list[str] = []
    reasons_conflict: list[str] = []

    bundle_ref = str(Path(args.bundle_path).resolve())

    try:
        validate_task_id(task_id)
        assert_no_latest_pattern(args.bundle_path, "bundle-path")
        assert_no_latest_pattern(args.expected_stage_map, "expected-stage-map")

        bundle_path = Path(args.bundle_path).resolve()
        if not bundle_path.exists() or not bundle_path.is_file():
            raise FileNotFoundError(f"Bundle not found: {bundle_path}")

        expected_stages = _load_expected_stages(Path(args.expected_stage_map).resolve())
        if not expected_stages:
            reasons_fail.append("expected stage map has no stages")

        manifest_path = Path(args.manifest_path).resolve() if args.manifest_path else None
        sha_path = Path(args.sha256s_path).resolve() if args.sha256s_path else None

        work_dir = Path(args.output_report).resolve().parent
        if manifest_path is None:
            manifest_path = _extract_internal_file(bundle_path, "manifest.json", work_dir / "_internal_manifest.json")
        if sha_path is None:
            sha_path = _extract_internal_file(bundle_path, "sha256s.txt", work_dir / "_internal_sha256s.txt")

        if manifest_path is None or not manifest_path.exists():
            reasons_fail.append("missing manifest")
        if sha_path is None or not sha_path.exists():
            reasons_fail.append("missing sha256s")

        if sha_path and sha_path.exists():
            try:
                sha_entries = parse_sha256_file(sha_path)
                if not sha_entries:
                    reasons_fail.append("sha256s is empty")
            except Exception as exc:
                reasons_fail.append(f"invalid sha256 file: {exc}")

        has_receipt = _bundle_has_name_hint(bundle_path, "receipt")
        has_provenance = _bundle_has_name_hint(bundle_path, "provenance")
        if not has_receipt:
            reasons_fail.append("missing receipt")
        if not has_provenance:
            reasons_fail.append("missing provenance")

        # Try provenance JSON from external path first then internal extract.
        provenance_candidate = None
        if has_provenance:
            internal_prov = _extract_internal_file(bundle_path, "provenance", work_dir / "_internal_provenance.json")
            if internal_prov and internal_prov.exists():
                try:
                    provenance_candidate = _read_json(internal_prov)
                except Exception:
                    provenance_candidate = None

        if provenance_candidate is None:
            reasons_fail.append("receipt without parseable provenance")
        else:
            prov_errors = validate_provenance(provenance_candidate, strict_acceptance=True)
            if prov_errors:
                reasons_fail.append("provenance invalid: " + "; ".join(prov_errors))
            else:
                if provenance_candidate.get("task_id") != task_id:
                    reasons_fail.append("provenance task_id mismatch")
                if provenance_candidate.get("contour_id") in {"", None}:
                    reasons_fail.append("missing CONTOUR_ID in provenance")
                if provenance_candidate.get("producer_type") in {"", None, "UNKNOWN"}:
                    reasons_fail.append("unknown or missing producer_type")
                if provenance_candidate.get("producer_id") in {"", None}:
                    reasons_fail.append("missing producer_id")
                if provenance_candidate.get("authority_level") == "FINAL_TASK_BUNDLE" and provenance_candidate.get("contour_id") == "VM2":
                    reasons_fail.append("bundle claiming final authority from VM2")

        if _bundle_has_name_hint(bundle_path, "latest"):
            reasons_fail.append("latest-fetch evidence")

        ledger_path = Path(args.ledger_path).resolve()
        ledger_events = read_ledger(ledger_path)
        task_events = [event for event in ledger_events if event.get("task_id") == task_id]
        if not task_events:
            reasons_waiting.append("no task events in ledger")

        stage_coverage = {stage_id: False for stage_id in expected_stages}
        for event in task_events:
            stage = event.get("stage_id")
            event_type = event.get("event_type")
            if stage in stage_coverage and event_type in {"STAGE_COMPLETED", "BUNDLE_FETCHED", "RECEIPT_VERIFIED"}:
                stage_coverage[stage] = True
            if event_type in {"BARRIER_CONFLICT", "ORIGIN_CONFLICT"}:
                reasons_conflict.append(f"ledger conflict event: {event_type}")

        for stage_id, covered in stage_coverage.items():
            if not covered:
                reasons_waiting.append(f"stage evidence missing: {stage_id}")

        origin_index = _load_origin_index(Path(args.origin_index_path).resolve())
        items = origin_index.get("items", []) if isinstance(origin_index, dict) else []
        matching_items = [item for item in items if item.get("task_id") == task_id]
        if not matching_items:
            reasons_waiting.append("no origin index items for task")
        for item in matching_items:
            if item.get("origin_status") == "CONFLICT_DIFFERENT_HASH":
                reasons_conflict.append("origin index conflict detected")

        for event in task_events:
            notes = str(event.get("notes", "")).lower()
            if "throne" in notes and "no" not in notes:
                reasons_fail.append("THRONE transfer claim")
            if "autosync" in notes and "no" not in notes:
                reasons_fail.append("auto-sync claim")

        if reasons_conflict:
            barrier_result = "BARRIER_CONFLICT"
            verdict = "CONFLICT"
        elif reasons_fail:
            barrier_result = "BARRIER_FAIL"
            verdict = "FAIL"
        elif reasons_waiting:
            barrier_result = "BARRIER_WAITING"
            verdict = "WAITING"
        else:
            barrier_result = "BARRIER_PASS"
            verdict = "PASS"

        report_payload = {
            "task_id": task_id,
            "barrier_result": barrier_result,
            "verdict": verdict,
            "reasons_fail": reasons_fail,
            "reasons_waiting": reasons_waiting,
            "reasons_conflict": reasons_conflict,
            "expected_stages": expected_stages,
            "bundle_path": str(bundle_path),
            "ledger_path": str(ledger_path),
            "origin_index_path": str(Path(args.origin_index_path).resolve()),
        }
        Path(args.output_report).resolve().write_text(json.dumps(report_payload, indent=2), encoding="utf-8")

        receipt_payload = {
            "task_id": task_id,
            "script": "barrier_verify.py",
            "barrier_result": barrier_result,
            "verdict": verdict,
            "deleted_anything": False,
            "touched_throne": False,
            "touched_vm2": False,
            "touched_vm3": False,
            "autosync_used": False,
            "latest_logic_used": False,
        }
        Path(args.output_receipt).resolve().write_text(json.dumps(receipt_payload, indent=2), encoding="utf-8")

        append_event(
            Path(args.ledger_path).resolve(),
            {
                "task_id": task_id,
                "stage_id": "STAGE-BARRIER",
                "run_id": "RUN-00000000-0000",
                "contour_id": "PC",
                "producer_type": "PC_SERVITOR",
                "producer_id": args.producer_id,
                "event_type": barrier_result,
                "status": verdict,
                "artifact_ref": str(Path(args.output_report).resolve()),
                "artifact_sha256": "",
                "previous_event_ref": "",
                "timestamp_utc": "",
                "receipt_ref": str(Path(args.output_receipt).resolve()),
                "notes": "barrier reducer result",
            },
        )

    except Exception as exc:  # pylint: disable=broad-except
        barrier_result = "BARRIER_FAIL"
        verdict = "FAIL"
        reasons_fail.append(str(exc))
        report_payload = {
            "task_id": task_id,
            "barrier_result": barrier_result,
            "verdict": verdict,
            "reasons_fail": reasons_fail,
            "reasons_waiting": reasons_waiting,
            "reasons_conflict": reasons_conflict,
        }
        Path(args.output_report).resolve().write_text(json.dumps(report_payload, indent=2), encoding="utf-8")
        Path(args.output_receipt).resolve().write_text(
            json.dumps({"task_id": task_id, "script": "barrier_verify.py", "barrier_result": barrier_result, "verdict": verdict}, indent=2),
            encoding="utf-8",
        )
        try:
            append_event(
                Path(args.ledger_path).resolve(),
                {
                    "task_id": task_id,
                    "stage_id": "STAGE-BARRIER",
                    "run_id": "RUN-00000000-0000",
                    "contour_id": "PC",
                    "producer_type": "PC_SERVITOR",
                    "producer_id": args.producer_id,
                    "event_type": "BARRIER_FAIL",
                    "status": "FAIL",
                    "artifact_ref": str(Path(args.output_report).resolve()),
                    "artifact_sha256": "",
                    "previous_event_ref": "",
                    "timestamp_utc": "",
                    "receipt_ref": str(Path(args.output_receipt).resolve()),
                    "notes": str(exc),
                },
            )
        except Exception:
            pass
        print(f"ERROR: {exc}", file=sys.stderr)

    comments = [
        "Barrier reducer выполнил проверку identity/integrity/provenance/origin/ledger по заданному task scope.",
        "Результат строго ограничен enum: BARRIER_PASS/BARRIER_FAIL/BARRIER_WAITING/BARRIER_CONFLICT.",
        "E2E и внешние контуры не запускались, THRONE и автоматизация не затрагивались.",
        "Следующий шаг: при BARRIER_PASS выполнить final_bundle_assemble.py, иначе закрыть причины FAIL/WAITING/CONFLICT.",
    ]
    step = f"{args.task_id}/barrier_verify.py"
    print_owner_report(step, str(Path(args.output_report).resolve()), verdict, comments)
    if args.owner_report_output:
        write_owner_report(Path(args.owner_report_output).resolve(), step, str(Path(args.output_report).resolve()), verdict, comments)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
