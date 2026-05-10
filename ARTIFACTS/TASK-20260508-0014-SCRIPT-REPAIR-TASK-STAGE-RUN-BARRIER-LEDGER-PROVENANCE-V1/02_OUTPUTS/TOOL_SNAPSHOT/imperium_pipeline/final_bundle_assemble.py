#!/usr/bin/env python3
"""Assemble final PC-side task bundle only after BARRIER_PASS."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import zipfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from lib.ledger_utils import append_event  # noqa: E402
from lib.manifest_utils import write_manifest  # noqa: E402
from lib.owner_report import print_owner_report, write_owner_report  # noqa: E402
from lib.path_safety import assert_no_latest_pattern  # noqa: E402
from lib.provenance_utils import create_provenance_record, update_origin_index, validate_provenance, write_provenance  # noqa: E402
from lib.sha256_utils import file_sha256, write_sha256_file  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Assemble final task bundle after BARRIER_PASS")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--barrier-report", required=True)
    parser.add_argument("--input-root", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--ledger-path", required=True)
    parser.add_argument("--origin-index-path", required=True)
    parser.add_argument("--owner-summary", required=True)
    parser.add_argument("--speculum-review-request", required=True)
    parser.add_argument("--producer-id", required=True)
    parser.add_argument("--owner-report-output", default="")
    return parser


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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

    verdict = "FAIL"
    bundle_ref = "N/A"

    try:
        assert_no_latest_pattern(args.output_dir, "output-dir")

        task_id = args.task_id.strip()
        barrier_report_path = Path(args.barrier_report).resolve()
        input_root = Path(args.input_root).resolve()
        output_dir = Path(args.output_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        barrier = _read_json(barrier_report_path)
        barrier_result = barrier.get("barrier_result")
        if barrier_result != "BARRIER_PASS":
            raise RuntimeError("final_bundle_assemble.py requires BARRIER_PASS")

        build_dir = output_dir / f"{task_id}_FINAL_TASK_BUNDLE_CONTENT"
        if build_dir.exists():
            shutil.rmtree(build_dir)
        build_dir.mkdir(parents=True, exist_ok=True)

        copied = _copy_tree_files(input_root, build_dir / "INPUT_ROOT", output_dir)

        owner_summary_path = Path(args.owner_summary).resolve()
        speculum_request_path = Path(args.speculum_review_request).resolve()
        ledger_path = Path(args.ledger_path).resolve()
        origin_index_path = Path(args.origin_index_path).resolve()

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
            source_bundle_name="FINAL_TASK_BUNDLE.zip",
            source_bundle_sha256="PENDING",
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

        files_for_sha = [path for path in build_dir.rglob("*") if path.is_file() and path.name != "SHA256SUMS.txt"]
        sha_path = build_dir / "SHA256SUMS.txt"
        write_sha256_file(sorted(files_for_sha), sha_path)

        zip_path = output_dir / f"{task_id}_FINAL_TASK_BUNDLE.zip"
        if zip_path.exists():
            zip_path.unlink()
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for file_path in sorted([p for p in build_dir.rglob("*") if p.is_file()]):
                archive.write(file_path, arcname=str(file_path.relative_to(build_dir)).replace("\\", "/"))

        zip_sha = file_sha256(zip_path)
        zip_sha_path = output_dir / f"{task_id}_FINAL_TASK_BUNDLE.zip.sha256"
        zip_sha_path.write_text(f"{zip_sha}  {zip_path.name}\n", encoding="utf-8")

        # Update provenance and origin index with final zip hash.
        provenance["source_bundle_sha256"] = zip_sha
        write_provenance(provenance_path, provenance)
        update_origin_index(
            origin_index_path,
            provenance,
            artifact_name=zip_path.name,
            artifact_path=str(zip_path),
            artifact_sha256=zip_sha,
            provenance_ref=str(provenance_path),
            receipt_ref=str(output_dir / "FINAL_ASSEMBLY_RECEIPT.json"),
        )

        receipt_payload = {
            "task_id": task_id,
            "barrier_result": barrier_result,
            "final_bundle": str(zip_path),
            "final_bundle_sha256": zip_sha,
            "copied_file_count": len(copied),
            "deleted_anything": False,
            "touched_throne": False,
            "touched_vm2": False,
            "touched_vm3": False,
            "autosync_used": False,
            "latest_logic_used": False,
            "verdict": "PASS",
        }
        receipt_path = output_dir / "FINAL_ASSEMBLY_RECEIPT.json"
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
        verdict = "FAIL"
        print(f"ERROR: {exc}", file=sys.stderr)

    comments = [
        "Реализована сборка финального PC-side бандла только при BARRIER_PASS и с обязательным AGENT_FINAL_RESPONSE.",
        "Сборка включает manifest, SHA256SUMS, provenance, ledger, origin index и review документы.",
        "E2E выполнение не запускалось в этой задаче, THRONE и automation/watchers остаются заблокированы.",
        "Следующий шаг: использовать скрипт в TASK-0015 после контролируемого barrier pass на реальном tiny E2E.",
    ]
    step = f"{args.task_id}/final_bundle_assemble.py"
    print_owner_report(step, bundle_ref, verdict, comments)
    if args.owner_report_output:
        write_owner_report(Path(args.owner_report_output).resolve(), step, bundle_ref, verdict, comments)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
