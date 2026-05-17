#!/usr/bin/env python3
"""Read-only repository reconnaissance runner for IMPERIUM bootstrap v0.1."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SKIP_DIR_NAMES = {
    ".git",
    "__pycache__",
    "node_modules",
    "venv",
    ".venv",
    "dist",
    "build",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
}

SCRIPT_EXTENSIONS = {".py", ".ps1", ".sh", ".bat"}
TEXT_SCAN_EXTENSIONS = {
    ".py",
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".ini",
    ".cfg",
    ".ps1",
    ".sh",
    ".bat",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".css",
    ".html",
    ".xml",
}

RUNTIME_CANDIDATE_TOKENS = {
    "runtime",
    "artifact",
    "artifacts",
    "cache",
    "temp",
    "tmp",
    "inbox",
    "outbox",
}

MARKER_RE = re.compile(r"\b(TODO|FIXME|PLACEHOLDER)\b", re.IGNORECASE)
MAX_CANDIDATE_ITEMS = 300
MAX_MARKERS = 500
MAX_TEXT_FILE_BYTES = 2 * 1024 * 1024
LARGE_FILE_BYTES = 10 * 1024 * 1024


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _to_posix(path: Path) -> str:
    return path.as_posix()


def _safe_rel(path: Path, root: Path) -> str:
    return _to_posix(path.relative_to(root))


def _run_git(repo_root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return ""
    return proc.stdout.strip()


def _git_status_summary(repo_root: Path) -> dict[str, Any]:
    status_lines = _run_git(repo_root, "status", "--short").splitlines()
    status_lines = [line for line in status_lines if line.strip()]
    return {
        "is_clean": len(status_lines) == 0,
        "line_count": len(status_lines),
        "sample": status_lines[:80],
    }


def _extract_registered_paths(payload: Any) -> set[str]:
    result: set[str] = set()

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                key_l = str(key).lower()
                if key_l in {"path", "script_path", "file", "file_path", "script"} and isinstance(value, str):
                    normalized = value.replace("\\", "/").lstrip("./")
                    if normalized:
                        result.add(normalized)
                visit(value)
        elif isinstance(node, list):
            for item in node:
                visit(item)

    visit(payload)
    return result


def _scan_markers(file_path: Path) -> list[dict[str, Any]]:
    if file_path.suffix.lower() not in TEXT_SCAN_EXTENSIONS:
        return []
    try:
        if file_path.stat().st_size > MAX_TEXT_FILE_BYTES:
            return []
    except OSError:
        return []

    findings: list[dict[str, Any]] = []
    try:
        with file_path.open("r", encoding="utf-8", errors="ignore") as handle:
            for idx, line in enumerate(handle, start=1):
                match = MARKER_RE.search(line)
                if not match:
                    continue
                findings.append(
                    {
                        "line": idx,
                        "marker": match.group(1).upper(),
                        "preview": line.strip()[:180],
                    }
                )
                if len(findings) >= 3:
                    break
    except OSError:
        return []
    return findings


def gather_recon(repo_root: Path) -> dict[str, Any]:
    files_by_top_level_zone: Counter[str] = Counter()
    extension_counts: Counter[str] = Counter()
    top_level_dir_counts: Counter[str] = Counter()
    basename_map: dict[str, list[str]] = defaultdict(list)
    python_script_candidates: list[str] = []
    markdown_doctrine_doc_candidates: list[str] = []
    json_contract_candidates: list[str] = []
    runtime_output_cache_candidate_paths: list[str] = []
    large_file_candidates: list[dict[str, Any]] = []
    marker_candidates: list[dict[str, Any]] = []

    total_files = 0
    total_dirs = 0

    for root, dirs, files in os.walk(repo_root, topdown=True):
        dirs[:] = [d for d in dirs if d not in SKIP_DIR_NAMES]
        current_root = Path(root)

        for child_dir in dirs:
            total_dirs += 1
            child_path = current_root / child_dir
            rel_dir = _safe_rel(child_path, repo_root)
            top = rel_dir.split("/", 1)[0]
            top_level_dir_counts[top] += 1
            rel_dir_l = rel_dir.lower()
            if any(token in rel_dir_l for token in RUNTIME_CANDIDATE_TOKENS):
                if len(runtime_output_cache_candidate_paths) < MAX_CANDIDATE_ITEMS:
                    runtime_output_cache_candidate_paths.append(rel_dir)

        for filename in files:
            total_files += 1
            file_path = current_root / filename
            rel_path = _safe_rel(file_path, repo_root)
            rel_path_l = rel_path.lower()
            parts = rel_path.split("/")
            top = parts[0] if parts else "."
            files_by_top_level_zone[top] += 1

            suffix = file_path.suffix.lower() if file_path.suffix else "<no_ext>"
            extension_counts[suffix] += 1
            basename_map[file_path.name.lower()].append(rel_path)

            if suffix in SCRIPT_EXTENSIONS and len(python_script_candidates) < MAX_CANDIDATE_ITEMS:
                python_script_candidates.append(rel_path)

            if suffix == ".md" and ("doctrinarium" in rel_path_l or "doctrine" in rel_path_l or "gate" in rel_path_l):
                if len(markdown_doctrine_doc_candidates) < MAX_CANDIDATE_ITEMS:
                    markdown_doctrine_doc_candidates.append(rel_path)

            if suffix == ".json" and any(token in rel_path_l for token in ("schemas/", "registry/", "contract", "schema")):
                if len(json_contract_candidates) < MAX_CANDIDATE_ITEMS:
                    json_contract_candidates.append(rel_path)

            if any(token in rel_path_l for token in RUNTIME_CANDIDATE_TOKENS):
                if len(runtime_output_cache_candidate_paths) < MAX_CANDIDATE_ITEMS:
                    runtime_output_cache_candidate_paths.append(rel_path)

            try:
                size = file_path.stat().st_size
            except OSError:
                size = -1

            if size >= LARGE_FILE_BYTES and len(large_file_candidates) < MAX_CANDIDATE_ITEMS:
                large_file_candidates.append(
                    {
                        "path": rel_path,
                        "size_bytes": size,
                        "size_mb": round(size / (1024 * 1024), 2),
                    }
                )

            if len(marker_candidates) < MAX_MARKERS:
                file_markers = _scan_markers(file_path)
                for finding in file_markers:
                    marker_candidates.append(
                        {
                            "path": rel_path,
                            "line": finding["line"],
                            "marker": finding["marker"],
                            "preview": finding["preview"],
                        }
                    )
                    if len(marker_candidates) >= MAX_MARKERS:
                        break

    duplicate_basename_candidates = []
    for base_name, paths in basename_map.items():
        if len(paths) > 1:
            duplicate_basename_candidates.append(
                {
                    "basename": base_name,
                    "count": len(paths),
                    "sample_paths": sorted(paths)[:8],
                }
            )
    duplicate_basename_candidates.sort(key=lambda x: x["count"], reverse=True)
    duplicate_basename_candidates = duplicate_basename_candidates[:MAX_CANDIDATE_ITEMS]

    script_candidates_all = [p for p in python_script_candidates if Path(p).suffix.lower() in SCRIPT_EXTENSIONS]

    registry_path = repo_root / "REGISTRY" / "SCRIPT_REGISTRY.json"
    registered_paths: set[str] = set()
    risk_notes: list[str] = []
    if registry_path.exists():
        try:
            payload = json.loads(registry_path.read_text(encoding="utf-8"))
            registered_paths = _extract_registered_paths(payload)
        except Exception as exc:  # noqa: BLE001
            risk_notes.append(f"Could not parse REGISTRY/SCRIPT_REGISTRY.json: {exc}")
    else:
        risk_notes.append("REGISTRY/SCRIPT_REGISTRY.json was not found; unregistered script scan is partial.")

    normalized_registered = {p.replace("\\", "/").lstrip("./") for p in registered_paths}
    unregistered_script_candidates = [
        path for path in script_candidates_all if path.replace("\\", "/").lstrip("./") not in normalized_registered
    ][:MAX_CANDIDATE_ITEMS]

    imperium_test_version_files = files_by_top_level_zone.get("IMPERIUM_TEST_VERSION", 0)
    imperium_test_version_dirs = top_level_dir_counts.get("IMPERIUM_TEST_VERSION", 0)
    organs_files = files_by_top_level_zone.get("ORGANS", 0)
    organs_dirs = top_level_dir_counts.get("ORGANS", 0)

    itv_subzone_files: Counter[str] = Counter()
    organs_subzone_files: Counter[str] = Counter()
    for path, count in files_by_top_level_zone.items():
        if path == "IMPERIUM_TEST_VERSION":
            continue
        # Subzone details are collected below from explicit candidate lists.
        _ = count

    for rel_path in python_script_candidates:
        parts = rel_path.split("/")
        if len(parts) > 1 and parts[0] == "IMPERIUM_TEST_VERSION":
            itv_subzone_files[parts[1]] += 1
        if len(parts) > 1 and parts[0] == "ORGANS":
            organs_subzone_files[parts[1]] += 1

    for rel_path in markdown_doctrine_doc_candidates + json_contract_candidates:
        parts = rel_path.split("/")
        if len(parts) > 1 and parts[0] == "IMPERIUM_TEST_VERSION":
            itv_subzone_files[parts[1]] += 1
        if len(parts) > 1 and parts[0] == "ORGANS":
            organs_subzone_files[parts[1]] += 1

    if not itv_subzone_files:
        itv_subzone_files["(no sampled subzones)"] = 0
    if not organs_subzone_files:
        organs_subzone_files["(no sampled subzones)"] = 0

    cleanup_candidates = {
        "verdict": "CANDIDATE_ONLY_NO_DELETE",
        "runtime_output_cache_candidate_paths": runtime_output_cache_candidate_paths[:120],
        "large_file_candidates": large_file_candidates[:80],
        "duplicate_basename_candidates": duplicate_basename_candidates[:80],
        "marker_candidates_count": len(marker_candidates),
    }

    recon_data: dict[str, Any] = {
        "generated_at": _utc_now(),
        "repo_root": str(repo_root),
        "git_head": _run_git(repo_root, "rev-parse", "HEAD"),
        "git_branch": _run_git(repo_root, "rev-parse", "--abbrev-ref", "HEAD"),
        "git_status_summary": _git_status_summary(repo_root),
        "total_files": total_files,
        "total_dirs": total_dirs,
        "files_by_top_level_zone": dict(files_by_top_level_zone.most_common()),
        "extension_counts": dict(extension_counts.most_common()),
        "python_script_candidates": python_script_candidates[:MAX_CANDIDATE_ITEMS],
        "markdown_doctrine_doc_candidates": markdown_doctrine_doc_candidates[:MAX_CANDIDATE_ITEMS],
        "json_contract_candidates": json_contract_candidates[:MAX_CANDIDATE_ITEMS],
        "IMPERIUM_TEST_VERSION_summary": {
            "files": imperium_test_version_files,
            "dirs": imperium_test_version_dirs,
            "sampled_subzone_signal": dict(itv_subzone_files.most_common(20)),
        },
        "main_ORGANS_summary": {
            "files": organs_files,
            "dirs": organs_dirs,
            "sampled_subzone_signal": dict(organs_subzone_files.most_common(20)),
        },
        "runtime_output_cache_candidate_paths": runtime_output_cache_candidate_paths[:MAX_CANDIDATE_ITEMS],
        "large_file_candidates": large_file_candidates[:MAX_CANDIDATE_ITEMS],
        "duplicate_basename_candidates": duplicate_basename_candidates[:MAX_CANDIDATE_ITEMS],
        "TODO_FIXME_PLACEHOLDER_marker_candidates": marker_candidates[:MAX_MARKERS],
        "unregistered_script_candidates_if_possible": {
            "registry_source": "REGISTRY/SCRIPT_REGISTRY.json",
            "registered_path_count_detected": len(normalized_registered),
            "candidate_count": len(unregistered_script_candidates),
            "sample": unregistered_script_candidates[:MAX_CANDIDATE_ITEMS],
        },
        "cleanup_candidates": cleanup_candidates,
        "risk_notes": risk_notes
        + [
            "Skipped heavy/noisy directories: " + ", ".join(sorted(SKIP_DIR_NAMES)),
            "Read-only reconnaissance; no delete/move/rename/write outside report outputs.",
        ],
        "next_recommended_gated_task": (
            "TASK-20260517-UNQUISITION-EXTEREMINATUS-RECON-REVIEW-AND-REGISTRATION-GATE-V0_1"
        ),
    }
    return recon_data


def build_markdown_report(data: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# IMPERIUM Repo Recon Report V0.1")
    lines.append("")
    lines.append(f"- generated_at: `{data['generated_at']}`")
    lines.append(f"- repo_root: `{data['repo_root']}`")
    lines.append(f"- git_head: `{data['git_head']}`")
    lines.append(f"- git_branch: `{data['git_branch']}`")
    lines.append(
        f"- git_status_summary: clean={data['git_status_summary']['is_clean']}, "
        f"lines={data['git_status_summary']['line_count']}"
    )
    lines.append(f"- total_files: `{data['total_files']}`")
    lines.append(f"- total_dirs: `{data['total_dirs']}`")
    lines.append("")

    lines.append("## Files By Top-Level Zone")
    for zone, count in list(data["files_by_top_level_zone"].items())[:20]:
        lines.append(f"- {zone}: {count}")
    lines.append("")

    lines.append("## Extension Counts")
    for ext, count in list(data["extension_counts"].items())[:25]:
        lines.append(f"- {ext}: {count}")
    lines.append("")

    lines.append("## IMPERIUM_TEST_VERSION Summary")
    itv = data["IMPERIUM_TEST_VERSION_summary"]
    lines.append(f"- files: {itv['files']}")
    lines.append(f"- dirs: {itv['dirs']}")
    for subzone, signal in list(itv["sampled_subzone_signal"].items())[:15]:
        lines.append(f"- sampled_subzone_signal::{subzone}: {signal}")
    lines.append("")

    lines.append("## Main ORGANS Summary")
    organs = data["main_ORGANS_summary"]
    lines.append(f"- files: {organs['files']}")
    lines.append(f"- dirs: {organs['dirs']}")
    for subzone, signal in list(organs["sampled_subzone_signal"].items())[:15]:
        lines.append(f"- sampled_subzone_signal::{subzone}: {signal}")
    lines.append("")

    lines.append("## Candidate Buckets")
    lines.append(f"- python_script_candidates: {len(data['python_script_candidates'])}")
    lines.append(f"- markdown_doctrine_doc_candidates: {len(data['markdown_doctrine_doc_candidates'])}")
    lines.append(f"- json_contract_candidates: {len(data['json_contract_candidates'])}")
    lines.append(f"- runtime/output/cache candidate paths: {len(data['runtime_output_cache_candidate_paths'])}")
    lines.append(f"- large file candidates: {len(data['large_file_candidates'])}")
    lines.append(f"- duplicate basename candidates: {len(data['duplicate_basename_candidates'])}")
    lines.append(f"- TODO/FIXME/PLACEHOLDER marker candidates: {len(data['TODO_FIXME_PLACEHOLDER_marker_candidates'])}")
    lines.append(
        "- unregistered script candidates: "
        f"{data['unregistered_script_candidates_if_possible']['candidate_count']}"
    )
    lines.append("")

    lines.append("## Cleanup Candidates Verdict")
    lines.append("- CANDIDATE_ONLY_NO_DELETE")
    lines.append("")

    lines.append("## Risk Notes")
    for note in data["risk_notes"]:
        lines.append(f"- {note}")
    lines.append("")

    lines.append("## Next Recommended Gated Task")
    lines.append(f"- {data['next_recommended_gated_task']}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    repo_root = Path.cwd()
    if not (repo_root / ".git").exists():
        print("ERROR: run from repository root (missing .git in current directory).", file=sys.stderr)
        return 2

    report_dir = repo_root / "ORGANS" / "ADMINISTRATUM" / "REPORTS"
    report_dir.mkdir(parents=True, exist_ok=True)
    json_path = report_dir / "repo_recon_report_v0_1.json"
    md_path = report_dir / "repo_recon_report_v0_1.md"

    data = gather_recon(repo_root)
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(build_markdown_report(data), encoding="utf-8")

    print(str(json_path))
    print(str(md_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
