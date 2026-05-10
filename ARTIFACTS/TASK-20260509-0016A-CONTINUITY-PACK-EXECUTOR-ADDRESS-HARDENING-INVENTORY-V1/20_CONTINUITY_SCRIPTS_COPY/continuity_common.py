#!/usr/bin/env python3
"""Shared helpers for continuity subsystem scripts."""
from __future__ import annotations

import hashlib
import json
import os
import py_compile
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

TASK_ID_RE = re.compile(r"TASK-[0-9]{8}-[A-Z0-9-]+", re.IGNORECASE)
LATEST_RE = re.compile(r"(latest|newest|most[-_ ]?recent)", re.IGNORECASE)


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_read_text(path: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "cp1251", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except Exception:
            continue
    return path.read_text(errors="ignore")


def read_json_safe(path: Path) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    try:
        return json.loads(safe_read_text(path)), None
    except Exception as exc:
        return None, str(exc)


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    path.write_text(content if content.endswith("\n") else content + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def posix_rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def detect_task_id(text: str) -> Optional[str]:
    m = TASK_ID_RE.search(text)
    return m.group(0).upper() if m else None


def classify_manual_path(path: Path, manual_root: Path) -> bool:
    try:
        path.resolve().relative_to(manual_root.resolve())
        return True
    except Exception:
        return False


def has_latest_pattern(value: str) -> bool:
    return bool(LATEST_RE.search(value or ""))


def find_files(root: Path, pattern: str) -> List[Path]:
    if not root.exists():
        return []
    return sorted([p for p in root.rglob(pattern) if p.is_file()])


def find_dirs(root: Path, name: str) -> List[Path]:
    if not root.exists():
        return []
    return sorted([p for p in root.rglob("*") if p.is_dir() and p.name == name])


def compile_py_files(files: Iterable[Path]) -> Tuple[int, List[Dict[str, str]]]:
    ok = 0
    errors: List[Dict[str, str]] = []
    for file in files:
        try:
            py_compile.compile(str(file), doraise=True)
            ok += 1
        except Exception as exc:
            errors.append({"file": str(file), "error": str(exc)})
    return ok, errors


def remove_generated_caches(root: Path) -> Dict[str, int]:
    pycache_dirs = [p for p in root.rglob("__pycache__") if p.is_dir()]
    pyc_files = [p for p in root.rglob("*.pyc") if p.is_file()]
    pyo_files = [p for p in root.rglob("*.pyo") if p.is_file()]
    for d in pycache_dirs:
        shutil.rmtree(d, ignore_errors=True)
    for f in pyc_files + pyo_files:
        try:
            f.unlink(missing_ok=True)
        except Exception:
            pass
    return {
        "removed_pycache_dirs": len(pycache_dirs),
        "removed_pyc_files": len(pyc_files),
        "removed_pyo_files": len(pyo_files),
    }


def create_sha256s_file(root: Path, out_file: Path, exclude_names: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    exclude = set(exclude_names or [])
    items = []
    lines = []
    for p in sorted([x for x in root.rglob("*") if x.is_file()]):
        rel = p.relative_to(root).as_posix()
        if p.name in exclude:
            continue
        digest = sha256_file(p)
        lines.append(f"{digest}  {rel}")
        items.append({"path": rel, "sha256": digest, "size_bytes": p.stat().st_size})
    write_text(out_file, "\n".join(lines))
    return items


def verify_sha256s_file(root: Path, sha_file: Path) -> Dict[str, Any]:
    verified = 0
    missing = 0
    mismatch = 0
    invalid = 0
    errors: List[str] = []
    for idx, raw in enumerate(safe_read_text(sha_file).splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        if "  " not in line:
            invalid += 1
            errors.append(f"line_{idx}:invalid_format")
            continue
        expected, rel = line.split("  ", 1)
        if "\\" in rel or rel.startswith("/") or rel.startswith("..") or ":" in rel[:3]:
            invalid += 1
            errors.append(f"line_{idx}:unsafe_path:{rel}")
            continue
        p = root / rel.replace("/", os.sep)
        if not p.exists():
            missing += 1
            errors.append(f"line_{idx}:missing:{rel}")
            continue
        got = sha256_file(p)
        if got.lower() != expected.lower():
            mismatch += 1
            errors.append(f"line_{idx}:mismatch:{rel}")
        else:
            verified += 1
    return {
        "verified_count": verified,
        "missing_count": missing,
        "mismatch_count": mismatch,
        "invalid_count": invalid,
        "errors": errors,
    }


def parse_verdict_from_text(content: str) -> Optional[str]:
    m = re.search(r"\b(PASS_AS_CONTINUITY_EXECUTOR_BASE|PASS_AS_LOCAL_RUNTIME_PRIMITIVES|PASS|PARTIAL|BLOCKED|FAIL|CONTINUITY_GREEN|CONTINUITY_YELLOW|CONTINUITY_RED)\b", content)
    return m.group(1) if m else None


def owner_report_text(step: str, bundle: str, verdict: str, lines: List[str]) -> str:
    lines = lines[:4]
    body = [
        "ШАГ:",
        step,
        "",
        "БАНДЛ:",
        bundle,
        "",
        "ВЕРДИКТ:",
        verdict,
        "",
        "КОММЕНТАРИЙ ДЛЯ OWNER:",
    ]
    body.extend(lines)
    return "\n".join(body) + "\n"


def try_parse_json_files(paths: Iterable[Path]) -> Tuple[int, List[str]]:
    ok = 0
    errs: List[str] = []
    for p in paths:
        obj, err = read_json_safe(p)
        if err:
            errs.append(f"{p}: {err}")
        else:
            _ = obj
            ok += 1
    return ok, errs


def path_hygiene_stats(paths: Iterable[str]) -> Dict[str, int]:
    backslash = 0
    abs_count = 0
    traversal = 0
    for p in paths:
        if "\\" in p:
            backslash += 1
        if p.startswith("/") or (len(p) > 1 and p[1] == ":"):
            abs_count += 1
        if "../" in p or p.startswith(".."):
            traversal += 1
    return {
        "backslash_count": backslash,
        "absolute_path_count": abs_count,
        "traversal_count": traversal,
    }
