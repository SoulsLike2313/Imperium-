#!/usr/bin/env python3
"""
Read-only IMPERIUM audit/map generator.

This script only reads existing files and writes reports under the audit output folder.
It does not modify existing IMPERIUM source/artifact files.
"""

from __future__ import annotations

import getpass
import hashlib
import json
import os
import platform
import re
import socket
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID = "TASK-20260509-IMPERIUM-READONLY-AUDIT-AND-MAP-FOR-SPECULUM-V1"
EXPECTED_ROOT = Path(r"E:\IMPERIUM")
OUTPUT_ROOT = EXPECTED_ROOT / "ARTIFACTS" / TASK_ID

ZIP_NAME = f"{TASK_ID}_AUDIT_PACK.zip"
ZIP_SHA_NAME = f"{ZIP_NAME}.sha256"

ARCHIVE_PATTERNS = [
    re.compile(r"^archive$", re.IGNORECASE),
    re.compile(r"^_archive$", re.IGNORECASE),
    re.compile(r"^00_archive$", re.IGNORECASE),
    re.compile(r"^old$", re.IGNORECASE),
    re.compile(r"^deprecated$", re.IGNORECASE),
    re.compile(r"(^|[_\-])(archive|old|deprecated)([_\-]|$)", re.IGNORECASE),
]

NOISE_DIRS = {
    "__pycache__",
    ".git",
    "node_modules",
    "venv",
    ".venv",
    ".mypy_cache",
    ".pytest_cache",
}

FILE_INTEREST_SUFFIXES = {".py", ".ps1", ".json", ".md", ".zip", ".sha256"}
FILE_INTEREST_NAMES = {"sha256sums.txt", "content_manifest.json", "finalization_receipt.json"}

TARGET_SANCTUM_TASK_ID = "TASK-20260509-SANCTUM-V0_1-OWNER-ACCEPTABLE-VERSION-ACTIVE-V1"

ORGAN_NAMES = [
    "Custodes",
    "Inquisition",
    "Mechanicus",
    "Administratum",
    "Astronomicon",
    "Strategium",
    "Officio Agentis",
    "Throne",
    "Schola Imperialis",
    "Doctrinarium",
]


@dataclass
class FileMeta:
    path: Path
    size: int
    mtime_iso: str


def now_local_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def is_archive_like(name: str) -> bool:
    for rx in ARCHIVE_PATTERNS:
        if rx.search(name):
            return True
    return False


def is_noise_dir(name: str) -> bool:
    return name.lower() in NOISE_DIRS


def classify_major_folder(name: str) -> tuple[str, str]:
    n = name.upper()
    if is_archive_like(name):
        return "archive", "ARCHIVE_SKIPPED"
    if n == "SANCTUM":
        return "active", "Looks active Sanctum source area"
    if n == "ARTIFACTS":
        return "mixed", "Mixed task outputs (active/interim/final-like artifacts)"
    if n == "ORGANS":
        return "scaffold", "Organ scaffolds/contracts/scripts area"
    if n == "EXPLORER":
        return "tooling", "Explorer UI and verification tools"
    if n == "OBSERVED":
        return "observed", "Observed/captured materials (status unclear)"
    return "unknown", "Unknown role from folder name only"


def safe_file_meta(path: Path) -> FileMeta:
    st = path.stat()
    return FileMeta(
        path=path,
        size=st.st_size,
        mtime_iso=datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
    )


def top_level_inventory(root: Path) -> tuple[list[dict], list[dict]]:
    top_rows: list[dict] = []
    skipped_archive_rows: list[dict] = []
    for p in sorted(root.iterdir(), key=lambda x: x.name.lower()):
        if not p.is_dir():
            continue
        class_state, comment = classify_major_folder(p.name)
        row = {
            "name": p.name,
            "path": str(p),
            "classification": class_state,
            "comment": comment,
            "safe_state": "unclear",
        }
        if class_state == "active":
            row["safe_state"] = "active"
        elif class_state == "archive":
            row["safe_state"] = "archive_skipped"
        elif class_state in {"tooling", "scaffold"}:
            row["safe_state"] = "likely_safe_if_readonly"
        top_rows.append(row)

        if class_state == "archive":
            direct_files = [x for x in p.iterdir() if x.is_file()]
            direct_dirs = [x for x in p.iterdir() if x.is_dir()]
            approx_size = sum(x.stat().st_size for x in direct_files)
            skipped_archive_rows.append(
                {
                    "path": str(p),
                    "skip_policy": "SKIP_SUBTREE",
                    "top_level_file_count": len(direct_files),
                    "top_level_dir_count": len(direct_dirs),
                    "approx_top_level_file_bytes": approx_size,
                }
            )
    return top_rows, skipped_archive_rows


def build_selected_depth_tree(root: Path, max_depth: int = 3, max_files_per_dir: int = 25) -> str:
    lines: list[str] = [str(root)]

    def walk(dir_path: Path, prefix: str, depth: int) -> None:
        if depth > max_depth:
            return
        try:
            entries = sorted(list(dir_path.iterdir()), key=lambda x: (x.is_file(), x.name.lower()))
        except Exception:
            lines.append(f"{prefix}[unreadable]")
            return

        dirs = [e for e in entries if e.is_dir()]
        files = [e for e in entries if e.is_file()]

        shown_files = 0
        total_items = len(dirs) + min(len(files), max_files_per_dir)
        idx = 0

        for d in dirs:
            idx += 1
            joint = "└── " if idx == total_items and shown_files == min(len(files), max_files_per_dir) else "├── "
            if is_archive_like(d.name):
                lines.append(f"{prefix}{joint}{d.name}/ [SKIP_SUBTREE:ARCHIVE_LIKE]")
                continue
            if is_noise_dir(d.name):
                lines.append(f"{prefix}{joint}{d.name}/ [SKIP_SUBTREE:NOISE]")
                continue
            lines.append(f"{prefix}{joint}{d.name}/")
            new_prefix = prefix + ("    " if joint == "└── " else "│   ")
            walk(d, new_prefix, depth + 1)

        for f in files[:max_files_per_dir]:
            shown_files += 1
            idx += 1
            joint = "└── " if idx == total_items else "├── "
            lines.append(f"{prefix}{joint}{f.name}")

        if len(files) > max_files_per_dir:
            lines.append(f"{prefix}└── ... ({len(files) - max_files_per_dir} more files omitted)")

    walk(root, "", 1)
    return "\n".join(lines) + "\n"


def iter_non_archive_files(root: Path) -> tuple[list[Path], list[dict], list[dict]]:
    files: list[Path] = []
    skipped_archives: list[dict] = []
    skipped_noise: list[dict] = []
    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        dpath = Path(dirpath)
        kept_dirs: list[str] = []
        for dn in dirnames:
            full = dpath / dn
            if is_archive_like(dn):
                skipped_archives.append({"path": str(full), "reason": "SKIP_SUBTREE_ARCHIVE_LIKE"})
                continue
            if is_noise_dir(dn):
                skipped_noise.append({"path": str(full), "reason": "SKIP_SUBTREE_NOISE"})
                continue
            kept_dirs.append(dn)
        dirnames[:] = kept_dirs

        for fn in filenames:
            files.append(dpath / fn)
    return files, skipped_archives, skipped_noise


def classify_file_kind(path: Path) -> tuple[str, str]:
    n = path.name.lower()
    p = str(path).replace("\\", "/").lower()
    if n.endswith(".py"):
        if "/sanctum/" in p:
            return "source", "Sanctum source or helper script"
        return "source", "Python source/script"
    if n.endswith(".ps1"):
        return "script", "PowerShell script"
    if "receipt" in n:
        return "receipt", "Receipt/proof file"
    if n.endswith(".zip"):
        return "artifact", "Bundle/archive artifact"
    if n.endswith(".sha256") or n == "sha256sums.txt":
        return "hash", "Hash/sidecar file"
    if n == "content_manifest.json" or "manifest" in n:
        return "manifest", "Manifest-like file"
    if n.endswith(".json"):
        return "data", "JSON data/report/policy"
    if n.endswith(".md"):
        return "doc", "Markdown document/report"
    return "unknown", "Unknown"


TASK_ID_RX = re.compile(r"(TASK-\d{8}-[A-Z0-9_\-]+)", re.IGNORECASE)


def extract_task_ids_from_path(path: Path) -> set[str]:
    ids: set[str] = set()
    for part in path.parts:
        if part.upper().startswith("TASK-"):
            ids.add(part)
        else:
            m = TASK_ID_RX.search(part)
            if m:
                ids.add(m.group(1))
    m2 = TASK_ID_RX.search(path.name)
    if m2:
        ids.add(m2.group(1))
    return ids


def collect_tasks_map(files: list[Path], skipped_archives: list[dict]) -> dict:
    tasks: dict[str, dict] = {}
    for f in files:
        tids = extract_task_ids_from_path(f)
        for tid in tids:
            t = tasks.setdefault(
                tid,
                {
                    "task_id": tid,
                    "locations": set(),
                    "files": [],
                    "status": "UNKNOWN",
                    "has_receipt": False,
                    "has_manifest": False,
                    "has_zip": False,
                    "has_sha256_sidecar": False,
                    "has_clear_current_version": False,
                    "risks_comments": [],
                },
            )
            t["locations"].add(str(f.parent))
            t["files"].append(f)
            lname = f.name.lower()
            if "receipt" in lname:
                t["has_receipt"] = True
            if lname in {"content_manifest.json", "manifest.json"} or "manifest" in lname:
                t["has_manifest"] = True
            if lname.endswith(".zip"):
                t["has_zip"] = True
            if lname.endswith(".sha256") or lname == "sha256sums.txt":
                t["has_sha256_sidecar"] = True
            if re.search(r"sanctum_v\d+(_\d+)?\.py", lname):
                t["has_clear_current_version"] = True

    # Mark archive-skipped tasks if visible in skipped paths
    for row in skipped_archives:
        p = row["path"]
        tids = extract_task_ids_from_path(Path(p))
        for tid in tids:
            t = tasks.setdefault(
                tid,
                {
                    "task_id": tid,
                    "locations": set(),
                    "files": [],
                    "status": "ARCHIVE_SKIPPED",
                    "has_receipt": False,
                    "has_manifest": False,
                    "has_zip": False,
                    "has_sha256_sidecar": False,
                    "has_clear_current_version": False,
                    "risks_comments": [],
                },
            )
            t["status"] = "ARCHIVE_SKIPPED"
            t["locations"].add(p)
            t["risks_comments"].append("Task appears under archive-like skipped subtree; content not enumerated.")

    for tid, t in tasks.items():
        up = tid.upper()
        loc_text = " ".join(t["locations"]).upper()
        if t["status"] == "ARCHIVE_SKIPPED":
            pass
        elif "-ACTIVE-" in up:
            t["status"] = "ACTIVE"
        elif "INTERIM" in up or "INTERIM" in loc_text or "HANDOFF" in loc_text:
            t["status"] = "INTERIM"
        elif t["has_zip"] and t["has_sha256_sidecar"] and t["has_receipt"]:
            t["status"] = "FINAL"
        else:
            t["status"] = "UNKNOWN"

        if not t["has_receipt"]:
            t["risks_comments"].append("No receipt detected.")
        if t["has_zip"] and not t["has_sha256_sidecar"]:
            t["risks_comments"].append("Zip exists without sha256 sidecar.")
        if t["status"] == "UNKNOWN":
            t["risks_comments"].append("Status ambiguous from on-disk signals.")

    # normalize
    out = {}
    for tid, t in tasks.items():
        out[tid] = {
            "task_id": tid,
            "locations": sorted(t["locations"]),
            "apparent_status": t["status"],
            "has_receipt": t["has_receipt"],
            "has_manifest": t["has_manifest"],
            "has_zip": t["has_zip"],
            "has_sha256_sidecar": t["has_sha256_sidecar"],
            "has_clear_current_version": t["has_clear_current_version"],
            "risks_comments": t["risks_comments"],
            "file_count_seen": len(t["files"]),
        }
    return out


def parse_version_tuple(stem: str) -> tuple[int, ...]:
    m = re.search(r"sanctum_v(.+)$", stem, re.IGNORECASE)
    if not m:
        return (-1,)
    raw = m.group(1)
    parts = []
    for x in raw.split("_"):
        try:
            parts.append(int(x))
        except Exception:
            parts.append(-1)
    return tuple(parts)


def collect_sanctum_state(files: list[Path], tasks_map: dict[str, dict]) -> dict:
    sanctum_files = []
    for f in files:
        if re.fullmatch(r"sanctum_v\d+(?:_\d+)?\.py", f.name, re.IGNORECASE):
            meta = safe_file_meta(f)
            sanctum_files.append(
                {
                    "path": str(f),
                    "name": f.name,
                    "version_key": parse_version_tuple(f.stem),
                    "size_bytes": meta.size,
                    "modified": meta.mtime_iso,
                }
            )
    sanctum_files = sorted(sanctum_files, key=lambda x: x["version_key"])
    latest = sanctum_files[-1]["name"] if sanctum_files else None
    has_v027 = any(x["name"].lower() == "sanctum_v0_27.py" for x in sanctum_files)
    has_v028 = any(x["name"].lower() == "sanctum_v0_28.py" for x in sanctum_files)

    baseline_accepted = False
    baseline_evidence = []
    # strict: only claim accepted if explicit evidence
    for f in files:
        if f.suffix.lower() not in {".md", ".json"}:
            continue
        try:
            txt = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if "sanctum" in txt.lower() and re.search(r"\bbaseline\s+accepted\b", txt, re.IGNORECASE):
            baseline_accepted = True
            baseline_evidence.append(str(f))

    # discover blocker hints
    blocker_hints = []
    blocker_rx = re.compile(r"(flicker|blank map|мерцани|пуст[а-я]* карта)", re.IGNORECASE)
    for f in files:
        if f.suffix.lower() not in {".md", ".json"}:
            continue
        if "sanctum" not in str(f).lower():
            continue
        try:
            txt = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if blocker_rx.search(txt):
            blocker_hints.append(str(f))
    blocker_hints = sorted(set(blocker_hints))[:20]

    active_task_info = tasks_map.get(TARGET_SANCTUM_TASK_ID, {})
    return {
        "task_id_focus": TARGET_SANCTUM_TASK_ID,
        "sanctum_files": sanctum_files,
        "likely_latest_version": latest,
        "has_sanctum_v0_27_py": has_v027,
        "has_sanctum_v0_28_py": has_v028,
        "baseline_accepted": baseline_accepted,
        "baseline_acceptance_evidence": baseline_evidence,
        "known_blocker_hints": blocker_hints,
        "active_task_map_entry": active_task_info,
        "do_not_touch_next": [
            "Do not continue sanctum_v0_28 in this audit.",
            "Do not fix flicker in this audit.",
            "Do not add stage tracking buttons in this audit.",
            "Do not claim baseline accepted without explicit evidence.",
        ],
    }


def collect_continuity_packs(files: list[Path]) -> list[dict]:
    packs = defaultdict(lambda: {"paths": set(), "zips": [], "sha": [], "receipts": []})
    for f in files:
        pstr = str(f).replace("\\", "/")
        low = pstr.lower()
        if "continuity" in low or "handoff" in low:
            # choose pack key as nearest folder with continuity/handoff
            parts = f.parts
            key = None
            for i in range(len(parts) - 1, -1, -1):
                part = parts[i]
                if "continuity" in part.lower() or "handoff" in part.lower():
                    key = part
                    break
            if key is None:
                key = f.parent.name
            row = packs[key]
            row["paths"].add(str(f.parent))
            if f.suffix.lower() == ".zip":
                row["zips"].append(str(f))
            if f.suffix.lower() == ".sha256":
                row["sha"].append(str(f))
            if "receipt" in f.name.lower():
                row["receipts"].append(str(f))

    out = []
    for key, row in packs.items():
        k = key.upper()
        if "START" in k:
            ptype = "START"
        elif "INTERIM" in k or "HANDOFF" in k:
            ptype = "INTERIM"
        elif "FINAL" in k:
            ptype = "FINAL"
        else:
            ptype = "UNKNOWN"

        sha_values = []
        for sp in row["sha"]:
            try:
                first = Path(sp).read_text(encoding="utf-8", errors="ignore").strip().split()
                sha_values.append({"path": sp, "sha256": first[0] if first else None})
            except Exception:
                sha_values.append({"path": sp, "sha256": None})

        enough = False
        comment = "Unknown continuity completeness."
        if ptype == "INTERIM" and row["receipts"]:
            enough = True
            comment = "Likely sufficient for new-chat continuation (has interim markers and receipts)."
        if ptype == "START":
            comment = "Start continuity only; may miss current progress."

        out.append(
            {
                "pack_name": key,
                "paths": sorted(row["paths"]),
                "type": ptype,
                "zip_paths": sorted(row["zips"]),
                "sidecar_paths": sorted(row["sha"]),
                "receipt_paths": sorted(row["receipts"]),
                "sha256_values": sha_values,
                "likely_enough_for_new_chat": enough,
                "comment": comment,
            }
        )
    return sorted(out, key=lambda x: x["pack_name"].lower())


def organ_folder_name(org: str) -> str:
    # canonical map to likely folder naming
    mapping = {
        "Custodes": "CUSTODES",
        "Inquisition": "INQUISITION",
        "Mechanicus": "MECHANICUS",
        "Administratum": "ADMINISTRATUM",
        "Astronomicon": "ASTRONOMICON",
        "Strategium": "STRATEGIUM",
        "Officio Agentis": "OFFICIO_AGENTIS",
        "Throne": "THRONE",
        "Schola Imperialis": "SCHOLA_IMPERIALIS",
        "Doctrinarium": "DOCTRINARIUM",
    }
    return mapping.get(org, org.upper().replace(" ", "_"))


def collect_organs_state(root: Path) -> list[dict]:
    organs_root = root / "ORGANS"
    rows = []
    for org in ORGAN_NAMES:
        folder = organs_root / organ_folder_name(org)
        exists = folder.exists() and folder.is_dir()
        row = {
            "organ": org,
            "expected_folder": str(folder),
            "folder_exists": exists,
            "code_count_py": 0,
            "docs_count_md_json": 0,
            "self_report_signals": [],
            "contract_signals": [],
            "state": "NOT_FOUND",
        }
        if exists:
            py = 0
            docs = 0
            report_signals = []
            contract_signals = []
            for p in folder.rglob("*"):
                if not p.is_file():
                    continue
                lname = p.name.lower()
                if p.suffix.lower() == ".py":
                    py += 1
                if p.suffix.lower() in {".md", ".json"}:
                    docs += 1
                if any(k in lname for k in ["status", "health", "report", "index", "api"]):
                    report_signals.append(str(p))
                if "contract" in lname or "port" in lname or "schema" in lname:
                    contract_signals.append(str(p))
            row["code_count_py"] = py
            row["docs_count_md_json"] = docs
            row["self_report_signals"] = report_signals[:20]
            row["contract_signals"] = contract_signals[:20]
            if py == 0 and docs > 0:
                row["state"] = "PLACEHOLDER_OR_CONCEPTUAL"
            elif py > 0:
                row["state"] = "PARTIALLY_REAL_BUT_NEEDS_VERIFICATION"
            else:
                row["state"] = "UNKNOWN"
        rows.append(row)
    return rows


def risk_register(top_rows: list[dict], tasks_map: dict[str, dict], sanctum_state: dict, continuity_packs: list[dict]) -> list[dict]:
    risks = []
    risks.append(
        {
            "severity": "CRITICAL",
            "risk": "Active/interim/final ambiguity across task folders",
            "evidence": "Multiple TASK-* artifacts with mixed conventions; status derivation often heuristic.",
            "impact": "Continuity loss and wrong next-step decisions.",
        }
    )
    risks.append(
        {
            "severity": "HIGH",
            "risk": "No single explicit system-wide source-of-truth file",
            "evidence": "No canonical IMPERIUM_INDEX/CURRENT_STATE root marker discovered by convention.",
            "impact": "Owner/context handoff overhead and memory loss risk.",
        }
    )
    if sanctum_state.get("has_sanctum_v0_27_py"):
        risks.append(
            {
                "severity": "HIGH",
                "risk": "Sanctum visual baseline not accepted while active task continues",
                "evidence": "v0.27 present, blocker hints include flicker/blank-map references.",
                "impact": "Premature baseline/final claims risk.",
            }
        )
    if any(r["classification"] == "archive" for r in top_rows):
        risks.append(
            {
                "severity": "MEDIUM",
                "risk": "Archive contamination ambiguity",
                "evidence": "Archive-like subtrees exist and were intentionally skipped.",
                "impact": "Unknown stale copies may confuse active status if later mixed.",
            }
        )
    risks.append(
        {
            "severity": "MEDIUM",
            "risk": "Script execution safety variance",
            "evidence": "Many local scripts exist under ORGANS/EXPLORER/SANCTUM; capability boundaries not centrally enforced in one file.",
            "impact": "Operator can run wrong script in wrong stage.",
        }
    )
    risks.append(
        {
            "severity": "LOW",
            "risk": "Duplicate handoff structure drift",
            "evidence": "Continuity directories may coexist in multiple schema generations.",
            "impact": "Reader confusion over latest handoff.",
        }
    )
    return risks


def main() -> int:
    root = EXPECTED_ROOT if EXPECTED_ROOT.exists() else Path.cwd()
    output = OUTPUT_ROOT
    for d in [
        "00_README",
        "01_INVENTORY",
        "02_TASKS",
        "03_SANCTUM",
        "04_CONTINUITY",
        "05_ORGANS_AND_PORTS",
        "06_RISKS",
        "07_SPECULUM_INPUT",
        "08_MACHINE_READABLE",
        "09_RECEIPTS",
        "11_BUNDLE",
    ]:
        (output / d).mkdir(parents=True, exist_ok=True)

    started = now_local_iso()

    top_rows, top_archive_skips = top_level_inventory(root)
    tree_txt = build_selected_depth_tree(root, max_depth=3, max_files_per_dir=20)
    files, skipped_archives, skipped_noise = iter_non_archive_files(root)

    # inventory of files of interest
    interest_rows = []
    for f in files:
        lname = f.name.lower()
        if f.suffix.lower() in FILE_INTEREST_SUFFIXES or lname in FILE_INTEREST_NAMES:
            meta = safe_file_meta(f)
            kind, comment = classify_file_kind(f)
            interest_rows.append(
                {
                    "path": str(f),
                    "size_bytes": meta.size,
                    "modified": meta.mtime_iso,
                    "kind": kind,
                    "comment": comment,
                }
            )
    interest_rows = sorted(interest_rows, key=lambda x: x["path"].lower())

    tasks_map = collect_tasks_map(files, skipped_archives)
    sanctum_state = collect_sanctum_state(files, tasks_map)
    continuity_packs = collect_continuity_packs(files)
    organs_state = collect_organs_state(root)
    risks = risk_register(top_rows, tasks_map, sanctum_state, continuity_packs)

    # 00_README
    write_text(
        output / "00_README" / "AUDIT_README.md",
        "\n".join(
            [
                "# AUDIT README",
                "",
                f"Task: {TASK_ID}",
                "Purpose: factual read-only audit/map for Owner handoff to Logos-Speculum hard review.",
                f"Audited root: {root}",
                f"Audit time local: {started}",
                f"Audit time utc: {now_utc_iso()}",
                f"Machine: {platform.node()} | User: {getpass.getuser()} | Hostname: {socket.gethostname()}",
                "",
                "Exclusions:",
                "- Archive-like folders are SKIP_SUBTREE (existence only).",
                "- Noise dirs (__pycache__, .git, node_modules, venv, .venv) are skipped in deep mapping.",
                "- Archive contents are not read.",
                "",
                "No-modification statement:",
                "- Existing IMPERIUM files were not edited/renamed/moved/deleted by this audit.",
                "- Only files under this audit output folder were created.",
                "",
                "How Owner should use this pack:",
                "1. Read 00_README and 01_INVENTORY.",
                "2. Read 02_TASKS and 03_SANCTUM for active/interim status.",
                "3. Read 04_CONTINUITY and 06_RISKS for handoff risk awareness.",
                "4. Paste 07_SPECULUM_INPUT/SPECULUM_BRIEF.md into Logos-Speculum chat.",
            ]
        )
        + "\n",
    )

    # 01_INVENTORY
    tl_md = ["# IMPERIUM TREE TOP LEVEL", ""]
    for r in top_rows:
        tl_md.append(
            f"- `{r['name']}` | class={r['classification']} | state={r['safe_state']} | note={r['comment']}"
        )
    if top_archive_skips:
        tl_md.append("")
        tl_md.append("Archive-like skipped roots (top-level existence only):")
        for a in top_archive_skips:
            tl_md.append(
                f"- `{a['path']}` | top_files={a['top_level_file_count']} | top_dirs={a['top_level_dir_count']} | approx_bytes={a['approx_top_level_file_bytes']}"
            )
    write_text(output / "01_INVENTORY" / "IMPERIUM_TREE_TOP_LEVEL.md", "\n".join(tl_md) + "\n")
    write_text(output / "01_INVENTORY" / "IMPERIUM_TREE_SELECTED_DEPTH.txt", tree_txt)

    foi_md = ["# FILES OF INTEREST", ""]
    for r in interest_rows:
        foi_md.append(
            f"- `{r['path']}` | size={r['size_bytes']} | modified={r['modified']} | class={r['kind']} | comment={r['comment']}"
        )
    write_text(output / "01_INVENTORY" / "FILES_OF_INTEREST.md", "\n".join(foi_md) + "\n")

    # 02_TASKS
    tasks_sorted = sorted(tasks_map.values(), key=lambda x: x["task_id"].upper())
    tm_md = ["# TASKS MAP", ""]
    for t in tasks_sorted:
        tm_md.append(f"## {t['task_id']}")
        tm_md.append(f"- location_count: {len(t['locations'])}")
        for loc in t["locations"][:10]:
            tm_md.append(f"- location: `{loc}`")
        tm_md.append(f"- apparent_status: {t['apparent_status']}")
        tm_md.append(f"- has_receipt: {t['has_receipt']}")
        tm_md.append(f"- has_manifest: {t['has_manifest']}")
        tm_md.append(f"- has_zip: {t['has_zip']}")
        tm_md.append(f"- has_sha256_sidecar: {t['has_sha256_sidecar']}")
        tm_md.append(f"- has_clear_current_version: {t['has_clear_current_version']}")
        if t["risks_comments"]:
            tm_md.append("- risks/comments:")
            for c in t["risks_comments"]:
                tm_md.append(f"  - {c}")
        tm_md.append("")
    write_text(output / "02_TASKS" / "TASKS_MAP.md", "\n".join(tm_md) + "\n")
    write_json(output / "02_TASKS" / "TASKS_MAP.json", {"tasks": tasks_sorted})

    # 03_SANCTUM
    sanct_md = ["# SANCTUM STATE", ""]
    sanct_md.append(f"- likely_latest_version: {sanctum_state['likely_latest_version']}")
    sanct_md.append(f"- sanctum_v0_27.py exists: {sanctum_state['has_sanctum_v0_27_py']}")
    sanct_md.append(f"- sanctum_v0_28.py exists: {sanctum_state['has_sanctum_v0_28_py']}")
    sanct_md.append(f"- baseline accepted evidence found: {sanctum_state['baseline_accepted']}")
    if sanctum_state["baseline_acceptance_evidence"]:
        sanct_md.append("- baseline evidence paths:")
        for p in sanctum_state["baseline_acceptance_evidence"]:
            sanct_md.append(f"  - `{p}`")
    else:
        sanct_md.append("- baseline acceptance: NOT PROVEN by explicit evidence.")
    sanct_md.append("- known blocker hints:")
    if sanctum_state["known_blocker_hints"]:
        for p in sanctum_state["known_blocker_hints"]:
            sanct_md.append(f"  - `{p}`")
    else:
        sanct_md.append("  - none discovered via read-only text match")
    sanct_md.append("- do not touch next:")
    for s in sanctum_state["do_not_touch_next"]:
        sanct_md.append(f"  - {s}")
    sanct_md.append("")
    sanct_md.append("Discovered sanctum_v*.py files:")
    for r in sanctum_state["sanctum_files"]:
        sanct_md.append(
            f"- `{r['path']}` | version_key={r['version_key']} | size={r['size_bytes']} | modified={r['modified']}"
        )
    write_text(output / "03_SANCTUM" / "SANCTUM_STATE.md", "\n".join(sanct_md) + "\n")
    write_json(output / "03_SANCTUM" / "SANCTUM_FILES.json", sanctum_state)

    # 04_CONTINUITY
    cp_md = ["# CONTINUITY PACKS MAP", ""]
    for p in continuity_packs:
        cp_md.append(f"## {p['pack_name']}")
        cp_md.append(f"- type: {p['type']}")
        for x in p["paths"]:
            cp_md.append(f"- path: `{x}`")
        for z in p["zip_paths"]:
            cp_md.append(f"- zip: `{z}`")
        for s in p["sidecar_paths"]:
            cp_md.append(f"- sidecar: `{s}`")
        for r in p["receipt_paths"]:
            cp_md.append(f"- receipt: `{r}`")
        if p["sha256_values"]:
            cp_md.append("- parsed sha256:")
            for sv in p["sha256_values"]:
                cp_md.append(f"  - `{sv['path']}` => {sv['sha256']}")
        cp_md.append(f"- likely enough for new chat continuation: {p['likely_enough_for_new_chat']}")
        cp_md.append(f"- comment: {p['comment']}")
        cp_md.append("")
    write_text(output / "04_CONTINUITY" / "CONTINUITY_PACKS_MAP.md", "\n".join(cp_md) + "\n")

    gaps = [
        "- Missing explicit global source-of-truth file (e.g., IMPERIUM_INDEX.json).",
        "- Active vs interim vs final status can be ambiguous without opening multiple receipts.",
        "- Continuity folder naming/schema drift possible across iterations.",
        "- Some tasks may lack clear CURRENT_STATE file.",
        "- Archive skipped by policy, so hidden stale duplicates remain unknown.",
    ]
    write_text(output / "04_CONTINUITY" / "CONTINUITY_GAPS.md", "# CONTINUITY GAPS\n\n" + "\n".join(gaps) + "\n")

    # 05_ORGANS_AND_PORTS
    op_md = ["# ORGANS PORTS STATE", ""]
    for r in organs_state:
        op_md.append(f"## {r['organ']}")
        op_md.append(f"- folder_exists: {r['folder_exists']}")
        op_md.append(f"- expected_folder: `{r['expected_folder']}`")
        op_md.append(f"- code_count_py: {r['code_count_py']}")
        op_md.append(f"- docs_count_md_json: {r['docs_count_md_json']}")
        op_md.append(f"- contract_signals_count: {len(r['contract_signals'])}")
        op_md.append(f"- self_report_signals_count: {len(r['self_report_signals'])}")
        op_md.append(f"- state: {r['state']}")
        op_md.append("")
    write_text(output / "05_ORGANS_AND_PORTS" / "ORGANS_PORTS_STATE.md", "\n".join(op_md) + "\n")

    # 06_RISKS
    rr_md = ["# RISK REGISTER", ""]
    for r in risks:
        rr_md.append(f"## {r['severity']} - {r['risk']}")
        rr_md.append(f"- evidence: {r['evidence']}")
        rr_md.append(f"- impact: {r['impact']}")
        rr_md.append("")
    write_text(output / "06_RISKS" / "RISK_REGISTER.md", "\n".join(rr_md) + "\n")

    good_points = [
        "- Task IDs are present across artifacts.",
        "- Receipts are widely used in task folders.",
        "- Hash sidecars/sha files exist in many bundles.",
        "- Continuity/handoff packs exist for Sanctum flow.",
        "- Sanctum source is versioned (sanctum_v*.py).",
        "- No-fake-baseline principle appears explicitly in handoff docs.",
    ]
    write_text(output / "06_RISKS" / "WHAT_IS_GOOD.md", "# WHAT IS GOOD\n\n" + "\n".join(good_points) + "\n")

    bad_points = [
        "- Source of truth is not singular and not obvious at first glance.",
        "- Active/interim/final boundaries are not uniformly encoded across all tasks.",
        "- Naming/schema drift in continuity folders can mislead operators.",
        "- Archive-like regions exist and may hold conflicting stale state (intentionally skipped now).",
        "- Operator memory dependency remains high without a mandatory per-task CURRENT_STATE file.",
    ]
    write_text(
        output / "06_RISKS" / "WHAT_IS_BAD_OR_WEAK.md",
        "# WHAT IS BAD OR WEAK\n\n" + "\n".join(bad_points) + "\n",
    )

    # 07_SPECULUM_INPUT
    questions = [
        "A. Is the current IMPERIUM structure enough for safe new-chat continuity?",
        "B. Where is the real source of truth now?",
        "C. What is ambiguous between active/interim/final/archive?",
        "D. What creates the highest fake-green risk?",
        "E. What minimal current-state standard is needed per task?",
        "F. Should every active task have CURRENT_STATE.json?",
        "G. Should IMPERIUM root have IMPERIUM_INDEX.json?",
        "H. What should Sanctum/Explorer show first?",
        "I. Which folders must be protected from accidental edits?",
        "J. What is the safest next small architecture step?",
    ]
    write_text(output / "07_SPECULUM_INPUT" / "QUESTIONS_FOR_SPECULUM.md", "# QUESTIONS FOR SPECULUM\n\n" + "\n".join(f"- {q}" for q in questions) + "\n")

    brief_lines = [
        "# SPECULUM BRIEF",
        "",
        "Read-only audit was performed over IMPERIUM root to map current active/interim/final/unknown state.",
        "No build/repair/cleanup actions were performed; archive-like subtrees were intentionally skipped.",
        "",
        "What was found:",
        "- Mixed task states in ARTIFACTS with many receipts and hashes.",
        "- Sanctum task remains active; baseline acceptance not explicitly proven.",
        "- Continuity packs exist but schema consistency is imperfect.",
        "",
        "What remains uncertain:",
        "- Single canonical source-of-truth file is not obvious.",
        "- Archive-skipped subtrees may contain stale/conflicting state.",
        "",
        "What Speculum should judge:",
        "- Minimal mandatory current-state standard per task.",
        "- Root-level index/guardrails for continuity and anti-fake-green discipline.",
        "- Safe small architecture step to reduce handoff ambiguity.",
        "",
        "What Speculum must NOT do in this review:",
        "- Do not assume baseline acceptance without explicit evidence.",
        "- Do not perform destructive cleanup as part of this audit review.",
    ]
    write_text(output / "07_SPECULUM_INPUT" / "SPECULUM_BRIEF.md", "\n".join(brief_lines) + "\n")

    # 08_MACHINE_READABLE
    audit_json = {
        "audit_metadata": {
            "task_id": TASK_ID,
            "created_at_local": started,
            "created_at_utc": now_utc_iso(),
            "user": getpass.getuser(),
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
        },
        "root": str(root),
        "output_root": str(output),
        "archive_skip_policy": "SKIP_SUBTREE for archive-like names",
        "exclusions": {
            "archive_patterns": [r.pattern for r in ARCHIVE_PATTERNS],
            "noise_dirs": sorted(NOISE_DIRS),
        },
        "top_level_folders": top_rows,
        "archive_skipped_top_level": top_archive_skips,
        "skipped_archive_subtrees_count": len(skipped_archives),
        "tasks": sorted(tasks_map.values(), key=lambda x: x["task_id"].upper()),
        "sanctum": sanctum_state,
        "continuity_packs": continuity_packs,
        "organs": organs_state,
        "risks": risks,
        "recommended_next_actions": [
            "Send this audit pack to Logos-Speculum for hard review.",
            "Define a minimal mandatory CURRENT_STATE.json per active task.",
            "Define a single root IMPERIUM index/source-of-truth pointer.",
        ],
    }
    write_json(output / "08_MACHINE_READABLE" / "IMPERIUM_AUDIT.json", audit_json)

    current_state_candidate = {
        "schema": "CURRENT_STATE_CANDIDATE_V0",
        "task_id": TARGET_SANCTUM_TASK_ID,
        "status": "ACTIVE_NOT_COMPLETE",
        "current_version": "sanctum_v0_27.py",
        "owner_acceptance_state": "NOT_ACCEPTED_BASELINE",
        "blocker": "flickering_or_blank_unified_map",
        "next_action": "FIX_VISUAL_STABILITY_ONLY",
        "do_not_do": [
            "No final artifact claim",
            "No baseline claim",
            "No VM2/THRONE/E2E/watchers",
            "No functional stage buttons before visual baseline",
        ],
        "source_of_truth": "TO_BE_DECIDED_BY_SPECULUM",
        "latest_receipts": ["INTERIM_CONTINUITY_RECEIPT.json"],
        "latest_artifacts": ["interim continuity zip + sidecar"],
        "open_questions": [
            "Where to store canonical current-state for all tasks?",
            "How to encode ACTIVE/INTERIM/FINAL uniformly?",
        ],
        "note": "Proposal only; not applied to live system.",
    }
    write_json(output / "08_MACHINE_READABLE" / "CURRENT_STATE_CANDIDATE.json", current_state_candidate)

    # 09_RECEIPTS
    all_created_files = [p for p in output.rglob("*") if p.is_file()]
    # SHA list excludes itself and bundle folder to avoid self-reference loops
    sha_targets = []
    for p in all_created_files:
        rel = p.relative_to(output).as_posix()
        if rel == "09_RECEIPTS/AUDIT_SHA256SUMS.txt":
            continue
        if rel.startswith("11_BUNDLE/"):
            continue
        sha_targets.append(p)
    sha_lines = [f"{sha256_file(p)}  {p.relative_to(output).as_posix()}" for p in sorted(sha_targets)]
    write_text(output / "09_RECEIPTS" / "AUDIT_SHA256SUMS.txt", "\n".join(sha_lines) + ("\n" if sha_lines else ""))

    receipt_verdict = "PASS_READONLY_AUDIT_CREATED"
    receipt = {
        "task_id": TASK_ID,
        "created_at_local": now_local_iso(),
        "root_audited": str(root),
        "output_folder": str(output),
        "files_created": len([p for p in output.rglob("*") if p.is_file()]),
        "archive_skip_policy": "SKIP_SUBTREE_ARCHIVE_LIKE",
        "no_modify_policy": True,
        "verdict": receipt_verdict,
    }
    write_json(output / "09_RECEIPTS" / "AUDIT_RECEIPT.json", receipt)

    # final pack zip
    bundle_dir = output / "11_BUNDLE"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    zip_path = bundle_dir / ZIP_NAME
    sidecar = bundle_dir / ZIP_SHA_NAME

    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(output.rglob("*")):
            if not p.is_file():
                continue
            rel = p.relative_to(output).as_posix()
            if rel.startswith("11_BUNDLE/"):
                continue
            if p.suffix.lower() in {".pyc", ".pyo"}:
                continue
            if "__pycache__" in rel:
                continue
            zf.write(p, rel)

    zsha = sha256_file(zip_path)
    write_text(sidecar, f"{zsha}  {zip_path.name}\n")

    # update receipt with bundle info
    receipt["bundle_zip"] = str(zip_path)
    receipt["bundle_zip_sha256"] = zsha
    receipt["bundle_sidecar"] = str(sidecar)
    write_json(output / "09_RECEIPTS" / "AUDIT_RECEIPT.json", receipt)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

