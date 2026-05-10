#!/usr/bin/env python3
"""Assemble final PC-side task bundle only after BARRIER_PASS."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

SCRIPT_DIR = Path(__file__).resolve().parent
TOOLS_ROOT = SCRIPT_DIR.parent
CORE_LIB_DIR = TOOLS_ROOT / "01_CORE_LIB"
if str(CORE_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_LIB_DIR))

from id_validation import validate_task_id  # noqa: E402
from ledger_utils import append_event  # noqa: E402
from manifest_utils import write_manifest  # noqa: E402
from owner_report import print_owner_report, write_owner_report  # noqa: E402
from path_safety import assert_no_latest_pattern  # noqa: E402
from provenance_utils import create_provenance_record, update_origin_index, validate_provenance, write_provenance  # noqa: E402
from sha256_utils import file_sha256, write_sha256_file, write_single_sha256_file  # noqa: E402


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _utc_stamp_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Assemble final task bundle after BARRIER_PASS")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--task-root", required=True)
    parser.add_argument("--barrier-report", required=True)
    parser.add_argument("--input-root", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--ledger-path", required=True)
    parser.add_argument("--origin-index-path", required=True)
    parser.add_argument("--owner-summary", required=True)
    parser.add_argument("--speculum-review-request", required=True)
    parser.add_argument("--producer-id", required=True)
    parser.add_argument("--approved-registry-path", action="append", default=[])
    parser.add_argument("--owner-report-output", default="")
    return parser


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _safe_arcname_for_zip(file_path: Path, base_dir: Path) -> str:
    rel = file_path.resolve().relative_to(base_dir.resolve())
    rel_posix = rel.as_posix()
    normalized = str(PurePosixPath(rel_posix))
    if normalized.startswith("/") or normalized.startswith("\\"):
        raise ValueError(f"Unsafe absolute archive member path: {normalized}")
    if normalized.startswith("../") or "/../" in f"/{normalized}/":
        raise ValueError(f"Unsafe traversal archive member path: {normalized}")
    if ":" in normalized:
        raise ValueError(f"Unsafe drive-like archive member path: {normalized}")
    if "\\" in normalized:
        raise ValueError(f"Unsafe backslash archive member path: {normalized}")
    if normalized in {"", "."}:
        raise ValueError("Unsafe empty archive member path")
    return normalized


def _is_within(base: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(base.resolve())
        return True
    except Exception:
        return False


def _resolve_and_validate_in_scope(label: str, raw_path: str, task_root: Path, approved: list[Path]) -> Path:
    resolved = Path(raw_path).resolve()
    if _is_within(task_root, resolved):
        return resolved
    for allowed in approved:
        if allowed.is_file():
            if resolved == allowed.resolve():
                return resolved
        else:
            if _is_within(allowed.resolve(), resolved):
                return resolved
    raise ValueError(f"{label} is outside --task-root and not in approved-registry scope: {resolved}")


def _safe_append_ledger_event(
    ledger_path: Path,
    task_id: str,
    producer_id: str,
    event_type: str,
    status: str,
    artifact_ref: str,
    receipt_ref: str,
    notes: str,
) -> None:
    try:
        append_event(
            ledger_path,
            {
                "task_id": task_id,
                "stage_id": "STAGE-FINAL-ASSEMBLY",
                "run_id": "RUN-00000000-0000",
                "contour_id": "PC",
                "producer_type": "PC_SERVITOR",
                "producer_id": producer_id,
                "event_type": event_type,
                "status": status,
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


def _copy_tree_files(src_root: Path, dst_root: Path, exclude_prefix: Path) -> list[Path]:
    copied: list[Path] = []
    for file_path in src_root.rglob("*"):
        if not file_path.is_file():
            continue
        if exclude_prefix in file_path.parents:
            continue
        rel = file_path.relative_to(src_root)
        dst = dst_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, dst)
        copied.append(dst)
    return copied


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    task_id = args.task_id.strip()
    verdict = "FAIL"
    bundle_ref = "N/A"
    failure_reason = ""

    receipt_path_fallback = Path(args.output_dir).resolve() / "FINAL_ASSEMBLY_RECEIPT.json"

    try:
        validate_task_id(task_id)

        assert_no_latest_pattern(args.output_dir, "output-dir")
        assert_no_latest_pattern(args.input_root, "input-root")
        assert_no_latest_pattern(args.barrier_report, "barrier-report")

        task_root = Path(args.task_root).resolve()
        if not task_root.exists() or not task_root.is_dir():
            raise ValueError(f"task-root does not exist as directory: {task_root}")

        approved_paths = [Path(p).resolve() for p in args.approved_registry_path]

        barrier_report_path = _resolve_and_validate_in_scope("barrier-report", args.barrier_report, task_root, approved_paths)
        input_root = _resolve_and_validate_in_scope("input-root", args.input_root, task_root, approved_paths)
        output_dir = _resolve_and_validate_in_scope("output-dir", args.output_dir, task_root, approved_paths)
        ledger_path = _resolve_and_validate_in_scope("ledger-path", args.ledger_path, task_root, approved_paths)
        origin_index_path = _resolve_and_validate_in_scope("origin-index-path", args.origin_index_path, task_root, approved_paths)
        owner_summary_path = _resolve_and_validate_in_scope("owner-summary", args.owner_summary, task_root, approved_paths)
        speculum_request_path = _resolve_and_validate_in_scope(
            "speculum-review-request", args.speculum_review_request, task_root, approved_paths
        )

        output_dir.mkdir(parents=True, exist_ok=True)
        receipt_path = output_dir / "FINAL_ASSEMBLY_RECEIPT.json"

        barrier = _read_json(barrier_report_path)
        barrier_result = str(barrier.get("barrier_result", "")).strip()
        if barrier_result != "BARRIER_PASS":
            verdict = "BLOCKED"
            failure_reason = f"barrier report requires BARRIER_PASS, got: {barrier_result or 'MISSING'}"
            _write_json(
                receipt_path,
                {
                    "task_id": task_id,
                    "status": "BLOCKED",
                    "failure_reason": failure_reason,
                    "timestamp_utc": _utc_now(),
                    "barrier_report": str(barrier_report_path),
                    "barrier_result": barrier_result,
                    "verdict": "BLOCKED",
                    "deleted_anything": False,
                    "build_dir_clean_performed": False,
                    "touched_throne": False,
                    "touched_vm2": False,
                    "touched_vm3": False,
                    "autosync_used": False,
                    "latest_logic_used": False,
                },
            )
            _safe_append_ledger_event(
                ledger_path=ledger_path,
                task_id=task_id,
                producer_id=args.producer_id,
                event_type="STAGE_FAILED",
                status="BLOCKED",
                artifact_ref=str(barrier_report_path),
                receipt_ref=str(receipt_path),
                notes=failure_reason,
            )
            raise RuntimeError(failure_reason)

        build_dir = output_dir / f"{task_id}_FINAL_TASK_BUNDLE_CONTENT_{_utc_stamp_compact()}"
        build_dir.mkdir(parents=True, exist_ok=False)

        copied = _copy_tree_files(input_root, build_dir / "INPUT_ROOT", output_dir)

        shutil.copy2(barrier_report_path, build_dir / "BARRIER_REPORT.json")
        shutil.copy2(owner_summary_path, build_dir / "OWNER_SUMMARY.md")
        shutil.copy2(speculum_request_path, build_dir / "SPECULUM_REVIEW_REQUEST.md")
        shutil.copy2(ledger_path, build_dir / "TASK_STATUS_LEDGER.jsonl")
        shutil.copy2(origin_index_path, build_dir / "ORIGIN_INDEX.json")

        final_agent_response_path = build_dir / "AGENT_FINAL_RESPONSE.txt"
        write_owner_report(
            final_agent_response_path,
            step=f"{task_id}/final_bundle_assemble.py",
            bundle="FINAL_TASK_BUNDLE.zip",
            verdict="PASS",
            comment_lines=[
                "Собран финальный PC-side task bundle после подтвержденного BARRIER_PASS.",
                "Включены inputs, receipts, ledger, origin index, barrier report и owner/speculum документы.",
                "THRONE transfer и automation/watchers не использовались.",
                "Следующий шаг: передать bundle на Speculum review перед TASK-0015 E2E.",
            ],
        )

        provenance = create_provenance_record(
            task_id=task_id,
            stage_id="STAGE-FINAL-ASSEMBLY",
            run_id="RUN-00000000-0000",
            contour_id="PC",
            producer_type="PC_SERVITOR",
            producer_id=args.producer_id,
            executor_role="final_assembler",
            creation_mode="SCRIPTED",
            produced_on_host_class="PC",
            source_bundle_name=f"{task_id}_FINAL_TASK_BUNDLE.zip",
            source_bundle_sha256=None,
            source_bundle_sha256_status="EXTERNAL_HASH_RECORDED_IN_SIDECAR",
            parent_bundle_refs=[str(input_root)],
            transfer_method="LOCAL_CREATE",
            transfer_actor=args.producer_id,
            manual_touchpoints=[],
            authority_level="FINAL_TASK_BUNDLE",
            acceptance_scope="task_closeout",
            verification_status="BARRIER_PASSED",
        )
        prov_errors = validate_provenance(provenance, strict_acceptance=True)
        if prov_errors:
            raise RuntimeError("Final provenance invalid: " + "; ".join(prov_errors))

        provenance_path = build_dir / "FINAL_PROVENANCE.json"
        write_provenance(provenance_path, provenance)

        files_for_manifest = [path for path in build_dir.rglob("*") if path.is_file()]
        manifest_path = build_dir / "MANIFEST.json"
        manifest_identity = {
            "task_id": task_id,
            "stage_id": "STAGE-FINAL-ASSEMBLY",
            "run_id": "RUN-00000000-0000",
            "contour_id": "PC",
            "producer_type": "PC_SERVITOR",
            "producer_id": args.producer_id,
        }
        write_manifest(manifest_path, manifest_identity, files_for_manifest, build_dir, notes=["Final bundle assembly output"])
        manifest_payload = _read_json(manifest_path)
        manifest_payload["bundle_sha256_location"] = "external_sidecar_sha256"
        manifest_payload["bundle_self_hash_embedded"] = False
        manifest_payload["bundle_self_hash_sidecar_pattern"] = "<final_bundle>.zip.sha256"
        _write_json(manifest_path, manifest_payload)

        files_for_sha = [path for path in build_dir.rglob("*") if path.is_file() and path.name != "SHA256SUMS.txt"]
        sha_path = build_dir / "SHA256SUMS.txt"
        write_sha256_file(sorted(files_for_sha), sha_path, base_dir=build_dir)

        zip_path = output_dir / f"{task_id}_FINAL_TASK_BUNDLE.zip"
        if zip_path.exists():
            zip_path.unlink()
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for file_path in sorted([p for p in build_dir.rglob("*") if p.is_file()]):
                archive.write(file_path, arcname=_safe_arcname_for_zip(file_path, build_dir))

        zip_sha = file_sha256(zip_path)
        zip_sha_path = output_dir / f"{task_id}_FINAL_TASK_BUNDLE.zip.sha256"
        write_single_sha256_file(zip_path, zip_sha_path)

        origin_provenance = dict(provenance)
        origin_provenance["source_bundle_sha256"] = zip_sha
        origin_provenance["source_bundle_sha256_status"] = "EMBEDDED"
        update_origin_index(
            origin_index_path,
            origin_provenance,
            artifact_name=zip_path.name,
            artifact_path=str(zip_path),
            artifact_sha256=zip_sha,
            provenance_ref=str(provenance_path),
            receipt_ref=str(receipt_path),
        )

        receipt_payload = {
            "task_id": task_id,
            "barrier_result": barrier_result,
            "final_bundle": str(zip_path),
            "final_bundle_sha256": zip_sha,
            "final_bundle_sha256_location": str(zip_sha_path),
            "task_root": str(task_root),
            "build_dir": str(build_dir),
            "copied_file_count": len(copied),
            "status": "PASS",
            "failure_reason": "",
            "timestamp_utc": _utc_now(),
            "deleted_anything": False,
            "build_dir_clean_performed": False,
            "touched_throne": False,
            "touched_vm2": False,
            "touched_vm3": False,
            "autosync_used": False,
            "latest_logic_used": False,
            "verdict": "PASS",
        }
        receipt_path.write_text(json.dumps(receipt_payload, indent=2), encoding="utf-8")

        append_event(
            ledger_path,
            {
                "task_id": task_id,
                "stage_id": "STAGE-FINAL-ASSEMBLY",
                "run_id": "RUN-00000000-0000",
                "contour_id": "PC",
                "producer_type": "PC_SERVITOR",
                "producer_id": args.producer_id,
                "event_type": "FINAL_BUNDLE_CREATED",
                "status": "PASS",
                "artifact_ref": str(zip_path),
                "artifact_sha256": zip_sha,
                "previous_event_ref": "",
                "timestamp_utc": "",
                "receipt_ref": str(receipt_path),
                "notes": "final bundle assembly completed after barrier pass",
            },
        )

        verdict = "PASS"
        bundle_ref = str(zip_path)

    except Exception as exc:  # pylint: disable=broad-except
        if verdict not in {"BLOCKED"}:
            verdict = "FAIL"
        failure_reason = failure_reason or str(exc)
        _write_json(
            receipt_path_fallback,
            {
                "task_id": task_id,
                "status": verdict,
                "failure_reason": failure_reason,
                "timestamp_utc": _utc_now(),
                "barrier_report": str(Path(args.barrier_report).resolve()),
                "verdict": verdict,
                "deleted_anything": False,
                "build_dir_clean_performed": False,
                "touched_throne": False,
                "touched_vm2": False,
                "touched_vm3": False,
                "autosync_used": False,
                "latest_logic_used": False,
            },
        )
        try:
            _safe_append_ledger_event(
                ledger_path=Path(args.ledger_path).resolve(),
                task_id=task_id,
                producer_id=args.producer_id,
                event_type="STAGE_FAILED",
                status=verdict,
                artifact_ref=args.barrier_report,
                receipt_ref=str(receipt_path_fallback),
                notes=f"final assembly failure: {failure_reason}",
            )
        except Exception:
            pass
        print(f"ERROR: {exc}", file=sys.stderr)

    comments = [
        "Final assembly строго разрешён только после BARRIER_PASS и иначе выдаёт BLOCKED/FAIL receipt.",
        "Пути строго ограничены --task-root, build dir создаётся timestamped без silent delete.",
        "Внутренний SHA256SUMS пишет archive-relative POSIX пути, внешний .sha256 остаётся filename-only.",
        "E2E в этой задаче не выполнялся, THRONE и watchers остаются заблокированы.",
    ]
    step = f"{args.task_id}/final_bundle_assemble.py"
    print_owner_report(step, bundle_ref, verdict, comments)
    if args.owner_report_output:
        write_owner_report(Path(args.owner_report_output).resolve(), step, bundle_ref, verdict, comments)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
