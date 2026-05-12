#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Iterable

REQUIRED_TOP_LEVEL = {"repo", "evidence", "MANIFEST.json", "RECEIPT.json", "VERDICT.md"}
FORBIDDEN_PATH_MARKERS = {
    "THRONE/",
    ".git/",
    ".ssh/",
    "id_rsa",
    "id_ed25519",
    "PRIVATE_KEY",
    "BEGIN OPENSSH PRIVATE KEY",
    "BEGIN RSA PRIVATE KEY",
}
FORBIDDEN_CLAIMS = {"CLEAR", "OPERATIONAL", "SYSTEM_READY"}
BUNDLE_OK_STATES = {
    "BUNDLE_VERIFIED",
    "BUNDLE_APPLIED_TO_WORKTREE",
    "PC_CHECKS_PASSED",
}
BUNDLE_WARN_STATES = {
    "PC_CHECKS_FAILED",
    "BUNDLE_QUARANTINED",
}
BUNDLE_BAD_STATES = {
    "BUNDLE_REJECTED",
    "BLOCKED",
}


class Color:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    BOLD = "\033[1m"


def supports_color() -> bool:
    return sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def paint(text: str, color_code: str, enabled: bool) -> str:
    if not enabled:
        return text
    return f"{color_code}{text}{Color.RESET}"


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel_to(base: Path, child: Path) -> str:
    return child.resolve().relative_to(base.resolve()).as_posix()


def normalize_rel_path(path: str) -> str:
    return path.replace("\\", "/").strip()


def load_json(path: Path, blockers: list[str], label: str) -> dict[str, Any] | None:
    if not path.exists():
        blockers.append(f"missing_file:{label}:{path.as_posix()}")
        return None
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        blockers.append(f"invalid_json:{label}:{type(exc).__name__}:{path.as_posix()}")
        return None
    if not isinstance(obj, dict):
        blockers.append(f"invalid_json_type:{label}:{path.as_posix()}")
        return None
    return obj


def check_required_top_level(bundle_dir: Path, blockers: list[str]) -> dict[str, bool]:
    found: dict[str, bool] = {}
    for item in REQUIRED_TOP_LEVEL:
        found[item] = (bundle_dir / item).exists()
        if not found[item]:
            blockers.append(f"missing_required_member:{item}")
    return found


def has_forbidden_marker(path_str: str) -> bool:
    normalized = normalize_rel_path(path_str)
    upper = normalized.upper()
    for marker in FORBIDDEN_PATH_MARKERS:
        m = marker.upper()
        if m in upper:
            return True
    return False


def as_file_entries(value: Any, blockers: list[str], field_name: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    if not isinstance(value, list):
        blockers.append(f"manifest_field_not_list:{field_name}")
        return entries
    for idx, item in enumerate(value):
        if not isinstance(item, dict):
            blockers.append(f"manifest_field_item_not_object:{field_name}:{idx}")
            continue
        path_value = item.get("path")
        if not isinstance(path_value, str) or not path_value.strip():
            blockers.append(f"manifest_field_item_missing_path:{field_name}:{idx}")
            continue
        sha_value = item.get("sha256")
        if sha_value is not None and not (isinstance(sha_value, str) and len(sha_value) == 64):
            blockers.append(f"manifest_field_item_invalid_sha256:{field_name}:{idx}")
        entries.append({"path": normalize_rel_path(path_value), "sha256": str(sha_value) if sha_value else ""})
    return entries


def verify_file_list(
    bundle_dir: Path,
    entries: Iterable[dict[str, str]],
    expected_prefix: str,
    blockers: list[str],
    warnings: list[str],
    field_name: str,
) -> list[str]:
    verified_paths: list[str] = []
    normalized_prefix = expected_prefix.strip().strip("/")
    prefix = f"{normalized_prefix}/" if normalized_prefix else ""
    for entry in entries:
        rel_path = entry["path"]
        if has_forbidden_marker(rel_path):
            blockers.append(f"forbidden_path_marker:{field_name}:{rel_path}")
        if prefix and not rel_path.startswith(prefix):
            rel_path = prefix + rel_path.lstrip("/")
        target = bundle_dir / rel_path
        verified_paths.append(rel_path)
        if not target.exists() or not target.is_file():
            blockers.append(f"missing_listed_file:{field_name}:{rel_path}")
            continue
        expected_sha = entry.get("sha256", "")
        if expected_sha:
            actual_sha = sha256_file(target)
            if actual_sha != expected_sha:
                blockers.append(f"sha256_mismatch:{field_name}:{rel_path}")
        else:
            warnings.append(f"sha256_missing_optional:{field_name}:{rel_path}")
    return verified_paths


def check_manifest_fields(manifest: dict[str, Any], blockers: list[str]) -> None:
    required = [
        "schema_version",
        "bundle_id",
        "task_id",
        "stage_id",
        "run_id",
        "builder",
        "created_at_utc",
        "source_git_truth",
        "target_git_truth",
        "route_truth_ref",
        "repo_files",
        "evidence_files",
        "receipt_files",
        "sha256",
        "scope",
        "checks",
        "declared_verdict",
        "no_fake_green_statement",
    ]
    for key in required:
        if key not in manifest:
            blockers.append(f"manifest_missing_field:{key}")


def check_forbidden_claims(manifest: dict[str, Any], verdict_text: str, blockers: list[str]) -> None:
    source_blob = json.dumps(manifest, ensure_ascii=False).upper()
    verdict_blob = verdict_text.upper()
    for claim in FORBIDDEN_CLAIMS:
        if claim in source_blob or claim in verdict_blob:
            blockers.append(f"forbidden_claim_detected:{claim}")


def verify_source_git_truth(manifest: dict[str, Any], blockers: list[str]) -> dict[str, Any]:
    out: dict[str, Any] = {"present": False, "head": "", "commit_count": None, "tree_url": ""}
    sgt = manifest.get("source_git_truth")
    if not isinstance(sgt, dict):
        blockers.append("source_git_truth_missing_or_invalid")
        return out
    out["present"] = True
    head = sgt.get("head")
    commit_count = sgt.get("commit_count")
    tree_url = sgt.get("tree_url")
    if not isinstance(head, str) or len(head) != 40:
        blockers.append("source_git_truth_head_invalid")
    if not isinstance(tree_url, str) or not tree_url.strip():
        blockers.append("source_git_truth_tree_url_missing")
    if not isinstance(commit_count, (int, str)):
        blockers.append("source_git_truth_commit_count_invalid")
    out["head"] = head if isinstance(head, str) else ""
    out["commit_count"] = commit_count
    out["tree_url"] = tree_url if isinstance(tree_url, str) else ""
    return out


def verify_sha256_file(bundle_path: Path, sha_file: Path, blockers: list[str]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "sha_file": str(sha_file),
        "present": sha_file.exists(),
        "expected": None,
        "actual": None,
        "verified": False,
    }
    if not sha_file.exists():
        return result
    content = sha_file.read_text(encoding="utf-8", errors="replace").strip()
    expected = content.split()[0] if content else ""
    actual = sha256_file(bundle_path)
    result["expected"] = expected
    result["actual"] = actual
    if not expected:
        blockers.append("sha256_file_empty")
        return result
    if expected != actual:
        blockers.append("bundle_zip_sha256_mismatch")
        return result
    result["verified"] = True
    return result


def verify_manifest_sha_map(bundle_dir: Path, manifest: dict[str, Any], blockers: list[str], warnings: list[str]) -> None:
    sha_map = manifest.get("sha256")
    if not isinstance(sha_map, dict):
        blockers.append("manifest_sha256_not_object")
        return
    for rel, expected in sha_map.items():
        if not isinstance(rel, str) or not rel.strip():
            blockers.append("manifest_sha256_invalid_path_key")
            continue
        if not isinstance(expected, str) or len(expected) != 64:
            blockers.append(f"manifest_sha256_invalid_hash:{rel}")
            continue
        rel_norm = normalize_rel_path(rel)
        target = bundle_dir / rel_norm
        if not target.exists() or not target.is_file():
            blockers.append(f"manifest_sha256_file_missing:{rel_norm}")
            continue
        actual = sha256_file(target)
        if actual != expected:
            blockers.append(f"manifest_sha256_mismatch:{rel_norm}")
    if not sha_map:
        warnings.append("manifest_sha256_map_empty")


def inspect_member_paths(bundle_dir: Path, blockers: list[str]) -> None:
    for file_path in bundle_dir.rglob("*"):
        if not file_path.is_file():
            continue
        rel_path = rel_to(bundle_dir, file_path)
        if has_forbidden_marker(rel_path):
            blockers.append(f"forbidden_path_in_bundle:{rel_path}")


def bundle_state_to_verdict(manifest: dict[str, Any], blockers: list[str], warnings: list[str]) -> tuple[str, bool, bool]:
    can_apply = False
    can_commit = False
    declared = str(manifest.get("declared_verdict", "")).upper()
    if blockers:
        return "BLOCKED", False, False
    if warnings:
        if declared in {"PASS", "PASS_WITH_WARNINGS"}:
            return "PASS_WITH_WARNINGS", True, True
        return "NEEDS_OWNER_DECISION", True, False
    if declared in {"PASS", "PASS_WITH_WARNINGS"}:
        return "PASS", True, True
    if declared in BUNDLE_WARN_STATES:
        return "NEEDS_OWNER_DECISION", True, False
    if declared in BUNDLE_BAD_STATES:
        return "CANNOT_COMMIT", False, False
    if declared in BUNDLE_OK_STATES:
        return "PASS", True, True
    return "PASS", True, True


def verify_bundle_dir(bundle_dir: Path, bundle_path: Path, repo_root: Path | None, sha_info: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    top_level_presence = check_required_top_level(bundle_dir, blockers)

    manifest_path = bundle_dir / "MANIFEST.json"
    receipt_path = bundle_dir / "RECEIPT.json"
    verdict_md_path = bundle_dir / "VERDICT.md"

    manifest = load_json(manifest_path, blockers, "manifest")
    _ = load_json(receipt_path, blockers, "receipt")

    verdict_text = ""
    if verdict_md_path.exists():
        verdict_text = verdict_md_path.read_text(encoding="utf-8", errors="replace")
    else:
        blockers.append("missing_file:verdict_md")

    repo_files_verified: list[str] = []
    evidence_files_verified: list[str] = []
    receipt_files_verified: list[str] = []
    source_git_truth_summary: dict[str, Any] = {}

    if manifest is not None:
        check_manifest_fields(manifest, blockers)
        check_forbidden_claims(manifest, verdict_text, blockers)
        source_git_truth_summary = verify_source_git_truth(manifest, blockers)

        scope = manifest.get("scope")
        if not isinstance(scope, dict):
            blockers.append("manifest_scope_missing_or_invalid")
        else:
            forbidden = scope.get("forbidden_paths_touched")
            if isinstance(forbidden, list) and forbidden:
                blockers.append("manifest_reports_forbidden_paths_touched")

        repo_entries = as_file_entries(manifest.get("repo_files"), blockers, "repo_files")
        evidence_entries = as_file_entries(manifest.get("evidence_files"), blockers, "evidence_files")
        receipt_entries = as_file_entries(manifest.get("receipt_files"), blockers, "receipt_files")

        repo_files_verified = verify_file_list(
            bundle_dir, repo_entries, "repo", blockers, warnings, "repo_files"
        )
        evidence_files_verified = verify_file_list(
            bundle_dir, evidence_entries, "evidence", blockers, warnings, "evidence_files"
        )
        receipt_files_verified = verify_file_list(
            bundle_dir, receipt_entries, "", blockers, warnings, "receipt_files"
        )

        verify_manifest_sha_map(bundle_dir, manifest, blockers, warnings)

    inspect_member_paths(bundle_dir, blockers)

    verdict, can_apply, can_commit = bundle_state_to_verdict(manifest or {}, blockers, warnings)

    checks = {
        "required_top_level": top_level_presence,
        "zip_sha256": sha_info,
        "source_git_truth": source_git_truth_summary,
        "forbidden_path_scan": "PASS" if not any(x.startswith("forbidden_") for x in blockers) else "FAIL",
        "repo_root": str(repo_root.resolve()) if repo_root else None,
    }

    return {
        "schema_version": "imperium.worker_bundle_verification_report.v0_1",
        "checked_at_utc": now_utc(),
        "bundle_path": str(bundle_path),
        "bundle_dir": str(bundle_dir),
        "verdict": verdict,
        "checks": checks,
        "warnings": warnings,
        "blockers": blockers,
        "repo_files": repo_files_verified,
        "evidence_files": evidence_files_verified,
        "receipt_files": receipt_files_verified,
        "can_apply_to_worktree": can_apply,
        "can_commit": can_commit,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def print_human(report: dict[str, Any], color: bool) -> None:
    blockers = report.get("blockers", [])
    warnings = report.get("warnings", [])
    verdict = str(report.get("verdict", "UNKNOWN"))

    def status_text(ok: bool, warn: bool = False) -> str:
        if ok and not warn:
            return paint("PASS", Color.GREEN, color)
        if ok and warn:
            return paint("WARN", Color.YELLOW, color)
        return paint("FAIL", Color.RED, color)

    print(paint("=== IMPERIUM BUNDLE VERIFY ===", Color.BOLD, color))
    print("BUNDLE")
    print(f"  path: {paint(report.get('bundle_path', ''), Color.CYAN, color)}")
    print("SHA256")
    zip_sha = report.get("checks", {}).get("zip_sha256", {})
    if zip_sha.get("present"):
        print(f"  sibling .sha256: {status_text(bool(zip_sha.get('verified')), False)}")
    else:
        print(f"  sibling .sha256: {status_text(True, True)} (not provided)")

    print("MANIFEST")
    top = report.get("checks", {}).get("required_top_level", {})
    missing = [k for k, v in top.items() if not v]
    print(f"  top-level required members: {status_text(not missing)}")

    print("GIT TRUTH")
    sgt = report.get("checks", {}).get("source_git_truth", {})
    git_ok = bool(sgt.get("present") and sgt.get("head") and sgt.get("tree_url"))
    print(f"  source_git_truth: {status_text(git_ok)}")

    print("SCOPE")
    forbidden_scan = report.get("checks", {}).get("forbidden_path_scan") == "PASS"
    print(f"  forbidden path scan: {status_text(forbidden_scan)}")

    print("EVIDENCE")
    evidence_count = len(report.get("evidence_files", []))
    print(f"  evidence files verified: {evidence_count}")

    print("RECEIPTS")
    receipts_count = len(report.get("receipt_files", []))
    print(f"  receipt files verified: {receipts_count}")

    print("FINAL VERDICT")
    if blockers:
        verdict_colored = paint(verdict, Color.RED, color)
    elif warnings:
        verdict_colored = paint(verdict, Color.YELLOW, color)
    else:
        verdict_colored = paint(verdict, Color.GREEN, color)
    print(f"  verdict: {verdict_colored}")
    print(f"  blockers: {len(blockers)}")
    print(f"  warnings: {len(warnings)}")


def verify_zip_bundle(bundle_path: Path, repo_root: Path | None, runtime_root: Path) -> dict[str, Any]:
    blockers: list[str] = []
    if not bundle_path.exists():
        return {
            "schema_version": "imperium.worker_bundle_verification_report.v0_1",
            "checked_at_utc": now_utc(),
            "bundle_path": str(bundle_path),
            "verdict": "BLOCKED",
            "checks": {},
            "warnings": [],
            "blockers": ["bundle_path_not_found"],
            "repo_files": [],
            "evidence_files": [],
            "receipt_files": [],
            "can_apply_to_worktree": False,
            "can_commit": False,
        }

    sha_file = bundle_path.with_suffix(bundle_path.suffix + ".sha256")
    sha_info = verify_sha256_file(bundle_path, sha_file, blockers)

    temp_parent = runtime_root / "bundle_verify_tmp"
    temp_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="bundle_verify_", dir=str(temp_parent)) as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        try:
            with zipfile.ZipFile(bundle_path, "r") as zf:
                zf.extractall(tmp_dir)
        except zipfile.BadZipFile:
            blockers.append("invalid_zip_file")
            return {
                "schema_version": "imperium.worker_bundle_verification_report.v0_1",
                "checked_at_utc": now_utc(),
                "bundle_path": str(bundle_path),
                "verdict": "BLOCKED",
                "checks": {"zip_sha256": sha_info},
                "warnings": [],
                "blockers": blockers,
                "repo_files": [],
                "evidence_files": [],
                "receipt_files": [],
                "can_apply_to_worktree": False,
                "can_commit": False,
            }

        bundle_dir = tmp_dir
        children = [p for p in tmp_dir.iterdir() if p.name != "__MACOSX"]
        if len(children) == 1 and children[0].is_dir():
            bundle_dir = children[0]

        report = verify_bundle_dir(bundle_dir, bundle_path, repo_root, sha_info)
        if blockers:
            report["blockers"] = blockers + report.get("blockers", [])
            report["verdict"] = "BLOCKED"
            report["can_apply_to_worktree"] = False
            report["can_commit"] = False
        return report


def verify_directory_bundle(bundle_dir: Path, repo_root: Path | None) -> dict[str, Any]:
    sha_info = {
        "sha_file": None,
        "present": False,
        "expected": None,
        "actual": None,
        "verified": False,
    }
    return verify_bundle_dir(bundle_dir, bundle_dir, repo_root, sha_info)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify IMPERIUM worker bundle structure and provenance.")
    parser.add_argument("--bundle", required=True, help="Path to bundle zip or extracted bundle directory")
    parser.add_argument("--repo-root", default=None, help="Repository root for contextual checks")
    parser.add_argument("--json-out", default=None, help="Write JSON report to this path")
    parser.add_argument("--human", action="store_true", help="Print human-readable report")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])

    bundle_path = Path(args.bundle).expanduser().resolve()
    repo_root = Path(args.repo_root).expanduser().resolve() if args.repo_root else None

    if repo_root is not None:
        runtime_root = repo_root / ".imperium_runtime" / "bundle_verification"
    else:
        runtime_root = Path.cwd() / ".imperium_runtime" / "bundle_verification"
    runtime_root.mkdir(parents=True, exist_ok=True)

    if bundle_path.is_file() and bundle_path.suffix.lower() == ".zip":
        report = verify_zip_bundle(bundle_path, repo_root, runtime_root)
    elif bundle_path.is_dir():
        report = verify_directory_bundle(bundle_path, repo_root)
    else:
        report = {
            "schema_version": "imperium.worker_bundle_verification_report.v0_1",
            "checked_at_utc": now_utc(),
            "bundle_path": str(bundle_path),
            "verdict": "BLOCKED",
            "checks": {},
            "warnings": [],
            "blockers": ["bundle_path_not_zip_or_directory"],
            "repo_files": [],
            "evidence_files": [],
            "receipt_files": [],
            "can_apply_to_worktree": False,
            "can_commit": False,
        }

    if args.json_out:
        out_path = Path(args.json_out).expanduser().resolve()
        write_json(out_path, report)

    if args.human:
        print_human(report, supports_color())
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))

    return 0 if not report.get("blockers") else 2


if __name__ == "__main__":
    raise SystemExit(main())
