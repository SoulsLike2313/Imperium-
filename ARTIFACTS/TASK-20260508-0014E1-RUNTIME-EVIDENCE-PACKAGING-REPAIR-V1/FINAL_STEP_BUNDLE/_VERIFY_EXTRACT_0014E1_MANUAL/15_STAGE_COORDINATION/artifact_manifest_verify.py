#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR / "lib"))

from common_runtime import (
    add_common_args,
    validate_identity,
    resolve_within_task_root,
    read_json,
    sha256_file,
    write_json,
    write_receipt,
    owner_report,
)

STEP = "TASK-20260508-0014E::artifact_manifest_verify.py"


def parse_args():
    p = argparse.ArgumentParser(description="Verify artifact manifest integrity")
    add_common_args(p, include_receipt=True, receipt_required=False)
    p.add_argument("--manifest-path", required=True)
    p.add_argument("--compare-manifest", required=False)
    p.add_argument("--verify-out", required=False)
    return p.parse_args()


def main():
    args = parse_args()
    errors = validate_identity(args)
    if errors:
        write_receipt(args, status="FAIL", action="ARTIFACT_MANIFEST_VERIFY", failure_reason=";".join(errors), extra={"errors": errors})
        owner_report(STEP, "N/A", "FAIL", [
            "Проверка manifest остановлена fail-closed.",
            "Identity невалиден.",
            "VM2/E2E/THRONE/watchers не использовались.",
            "Исправьте identity и повторите.",
        ])
        return 1

    task_root = Path(args.task_root)
    manifest_path = resolve_within_task_root(task_root, Path(args.manifest_path), allow_nonexistent=False)
    manifest = read_json(manifest_path)

    status = "PASS"
    issues = []

    for k in ["task_id", "stage_id", "run_id", "contour_id", "actor_id", "tool_id"]:
        if k not in manifest:
            issues.append(f"missing_manifest_identity:{k}")
    for k in ["task_id", "stage_id", "run_id", "contour_id"]:
        if manifest.get(k) != getattr(args, k):
            issues.append(f"identity_mismatch:{k}")

    artifact_root_rel = manifest.get("artifact_root")
    if not artifact_root_rel:
        issues.append("missing_artifact_root")
    else:
        artifact_root = resolve_within_task_root(task_root, Path(artifact_root_rel), allow_nonexistent=False)
        for item in manifest.get("artifacts", []):
            rel = item.get("relative_path")
            expected = item.get("sha256")
            if not rel or not expected:
                issues.append(f"invalid_entry:{rel}")
                continue
            fp = artifact_root / rel
            if not fp.exists() or not fp.is_file():
                issues.append(f"missing_artifact:{rel}")
                continue
            actual = sha256_file(fp)
            if actual != expected:
                issues.append(f"sha_mismatch:{rel}")

    compare_conflicts = []
    if args.compare_manifest:
        compare_path = resolve_within_task_root(task_root, Path(args.compare_manifest), allow_nonexistent=False)
        other = read_json(compare_path)
        same_identity = (
            other.get("task_id") == manifest.get("task_id") and
            other.get("stage_id") == manifest.get("stage_id") and
            other.get("run_id") == manifest.get("run_id") and
            other.get("contour_id") == manifest.get("contour_id")
        )
        if same_identity:
            m1 = {x.get("relative_path"): x.get("sha256") for x in manifest.get("artifacts", [])}
            m2 = {x.get("relative_path"): x.get("sha256") for x in other.get("artifacts", [])}
            for k in sorted(set(m1.keys()) & set(m2.keys())):
                if m1[k] != m2[k]:
                    compare_conflicts.append(f"conflict_same_identity_different_hash:{k}")

    if compare_conflicts:
        status = "CONFLICT"
    elif issues:
        status = "FAIL"

    out = {
        "task_id": args.task_id,
        "stage_id": args.stage_id,
        "run_id": args.run_id,
        "contour_id": args.contour_id,
        "status": status,
        "issues": issues,
        "conflicts": compare_conflicts,
    }

    if args.verify_out:
        verify_out = resolve_within_task_root(task_root, Path(args.verify_out))
        write_json(verify_out, out)

    write_receipt(args, status=status, action="ARTIFACT_MANIFEST_VERIFY", failure_reason=";".join(issues + compare_conflicts) if status != "PASS" else None, extra=out)
    owner_report(STEP, "N/A", status, [
        "Проверка artifact manifest выполнена локально.",
        f"Результат: {status}.",
        "VM2/E2E/THRONE/watchers не использовались.",
        "Готово для дальнейшей gate/evidence логики.",
    ])
    return 0 if status == "PASS" else (2 if status == "CONFLICT" else 1)


if __name__ == "__main__":
    raise SystemExit(main())
