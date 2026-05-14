#!/usr/bin/env python3
"""Build a task evidence bundle from Administratum session records."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from administratum_lifecycle_common_v0_1 import (
    REPO_ROOT,
    append_jsonl,
    ensure_external_path,
    read_json,
    session_dir,
    sha256_file,
    to_repo_rel,
    utc_now,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--bundle-root", default=r"E:/IMPERIUM_CONTEXT/LOCAL/TASK_BUNDLES")
    parser.add_argument("--allow-stopped", action="store_true")
    return parser.parse_args()


def normalize_source(path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = REPO_ROOT / path_value
    return path


def copy_artifact(source: Path, bundle_dir: Path, counter: int) -> tuple[Path, str]:
    if source.is_absolute():
        try:
            rel = source.relative_to(REPO_ROOT)
            dest = bundle_dir / "repo_artifacts" / rel
        except Exception:
            dest = bundle_dir / "external_artifacts" / f"{counter:04d}_{source.name}"
    else:
        dest = bundle_dir / "repo_artifacts" / source
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    return dest, sha256_file(dest)


def main() -> int:
    args = parse_args()
    now = utc_now()

    task_session_dir = session_dir(args.task_id)
    task_session_path = task_session_dir / "task_session.json"
    events_path = task_session_dir / "events.jsonl"
    stage_reports_dir = task_session_dir / "stage_reports"
    manifest_path_in_session = task_session_dir / "bundle_manifest.json"

    if not task_session_path.exists():
        print(json.dumps({"status": "FAIL", "reason": "task session not found"}, ensure_ascii=True))
        return 1

    bundle_root = Path(args.bundle_root)
    if not bundle_root.is_absolute():
        print(json.dumps({"status": "FAIL", "reason": "bundle_root must be absolute"}, ensure_ascii=True))
        return 1
    if not ensure_external_path(bundle_root):
        print(json.dumps({"status": "FAIL", "reason": "bundle_root must be outside repo"}, ensure_ascii=True))
        return 1

    session = read_json(task_session_path)
    task_status = str(session.get("status", ""))
    if task_status in {"STOPPED", "STOPPED_PENDING_OWNER_APPROVAL"} and not args.allow_stopped:
        print(json.dumps({"status": "FAIL", "reason": "cannot bundle stopped task without --allow-stopped"}, ensure_ascii=True))
        return 1

    bundle_task_dir = bundle_root / args.task_id
    bundle_task_dir.mkdir(parents=True, exist_ok=True)

    artifact_sources: list[Path] = []
    for core_name in ["task_session.json", "events.jsonl", "final_verdict.json", "stop_record.json"]:
        p = task_session_dir / core_name
        if p.exists():
            artifact_sources.append(p)

    if stage_reports_dir.exists():
        for stage_file in sorted(stage_reports_dir.glob("*.json")):
            artifact_sources.append(stage_file)
            stage_payload = read_json(stage_file)
            for ev in stage_payload.get("evidence_paths", []):
                src = normalize_source(str(ev))
                if src.exists() and src.is_file():
                    artifact_sources.append(src)

    unique_sources: list[Path] = []
    seen = set()
    for src in artifact_sources:
        key = str(src.resolve(strict=False)).lower()
        if key not in seen:
            unique_sources.append(src)
            seen.add(key)

    artifacts: list[dict[str, str]] = []
    for idx, source in enumerate(unique_sources, start=1):
        if not source.exists() or not source.is_file():
            continue
        dest, digest = copy_artifact(source, bundle_task_dir, idx)
        artifacts.append(
            {
                "source_path": to_repo_rel(source),
                "dest_path": str(dest).replace("\\", "/"),
                "sha256": digest,
            }
        )

    manifest_payload = {
        "schema_version": "administratum_task_bundle_manifest_v0_1",
        "task_id": args.task_id,
        "status": "BUNDLED",
        "bundle_root": str(bundle_root).replace("\\", "/"),
        "bundle_task_dir": str(bundle_task_dir).replace("\\", "/"),
        "created_utc": now,
        "artifacts": artifacts,
    }
    manifest_path_in_bundle = bundle_task_dir / "bundle_manifest.json"
    write_json(manifest_path_in_bundle, manifest_payload)
    write_json(manifest_path_in_session, manifest_payload)

    session["status"] = "BUNDLED"
    session["updated_utc"] = now
    write_json(task_session_path, session)

    append_jsonl(
        events_path,
        {
            "timestamp_utc": now,
            "event_type": "TASK_BUNDLED",
            "task_id": args.task_id,
            "status": "BUNDLED",
            "bundle_manifest_path": str(manifest_path_in_bundle).replace("\\", "/"),
        },
    )

    payload = {
        "status": "PASS",
        "task_id": args.task_id,
        "task_status": "BUNDLED",
        "bundle_task_dir": str(bundle_task_dir).replace("\\", "/"),
        "bundle_manifest_path": str(manifest_path_in_bundle).replace("\\", "/"),
        "artifact_count": len(artifacts),
    }
    print(json.dumps(payload, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
