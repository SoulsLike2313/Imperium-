#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR / "lib"))

from common_runtime import (
    add_common_args,
    validate_identity,
    identity_block,
    has_latest_pattern,
    resolve_within_task_root,
    sha256_file,
    write_json,
    write_receipt,
    owner_report,
)

STEP = "TASK-20260508-0014E::artifact_manifest_write.py"


def parse_args():
    p = argparse.ArgumentParser(description="Write artifact manifest for stage outputs")
    add_common_args(p, include_receipt=True, receipt_required=False)
    p.add_argument("--artifact-root", required=True)
    p.add_argument("--manifest-out", required=True)
    p.add_argument("--producer-type", required=False, default="PC_SERVITOR")
    return p.parse_args()


def main():
    args = parse_args()
    errors = validate_identity(args)
    if has_latest_pattern(args.artifact_root) or has_latest_pattern(args.manifest_out):
        errors.append("latest_pattern_path")
    if errors:
        write_receipt(args, status="FAIL", action="ARTIFACT_MANIFEST_WRITE", failure_reason=";".join(errors), extra={"errors": errors})
        owner_report(STEP, "N/A", "FAIL", [
            "Запись manifest отклонена fail-closed.",
            "Identity или path-политика нарушены.",
            "VM2/E2E/THRONE/watchers не использовались.",
            "Исправьте входные параметры.",
        ])
        return 1

    task_root = Path(args.task_root)
    artifact_root = resolve_within_task_root(task_root, Path(args.artifact_root), allow_nonexistent=False)
    manifest_out = resolve_within_task_root(task_root, Path(args.manifest_out))

    if not artifact_root.exists() or not artifact_root.is_dir():
        write_receipt(args, status="FAIL", action="ARTIFACT_MANIFEST_WRITE", failure_reason="artifact_root_missing")
        owner_report(STEP, "N/A", "FAIL", [
            "Artifact root не найден.",
            "Manifest не создан.",
            "VM2/E2E/THRONE/watchers не использовались.",
            "Подготовьте artifacts и повторите.",
        ])
        return 1

    files = [p for p in artifact_root.rglob("*") if p.is_file()]
    entries = []
    for fp in sorted(files):
        rel = fp.relative_to(artifact_root).as_posix()
        if rel.startswith("/") or ".." in rel.split("/"):
            write_receipt(args, status="FAIL", action="ARTIFACT_MANIFEST_WRITE", failure_reason=f"unsafe_rel:{rel}")
            return 1
        entries.append({
            "relative_path": rel,
            "sha256": sha256_file(fp),
            "size_bytes": fp.stat().st_size,
            "producer_actor": args.actor_id,
        })

    manifest = {
        **identity_block(args),
        "producer_type": args.producer_type,
        "artifact_root": artifact_root.relative_to(task_root).as_posix(),
        "artifact_count": len(entries),
        "artifacts": entries,
    }
    write_json(manifest_out, manifest)

    write_receipt(args, status="PASS", action="ARTIFACT_MANIFEST_WRITE", extra={
        "manifest_ref": manifest_out.relative_to(task_root).as_posix(),
        "artifact_count": len(entries),
    })
    owner_report(STEP, "N/A", "PASS", [
        "Manifest stage artifacts создан локально.",
        "Файлы зафиксированы с sha256 и относительными путями.",
        "VM2/E2E/THRONE/watchers не использовались.",
        "Manifest готов к verify шагу.",
    ])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
