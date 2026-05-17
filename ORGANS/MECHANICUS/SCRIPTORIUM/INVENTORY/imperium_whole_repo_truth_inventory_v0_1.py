from __future__ import annotations

import json
import os
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

TASK_ID = "TASK-IMPERIUM-WHOLE-REPO-TRUTH-INVENTORY-V0_1"
INVENTORY_ID = "IMPERIUM-WHOLE-REPO-TRUTH-INVENTORY-V0_1"
NEXT_DEFAULT_TASK = "TASK-MECHANICUS-SCRIPTORIUM-TEST-VERSION-TOOL-ABSORPTION-MAP-V0_1"
NEXT_ALT_TASK = "TASK-SECOND-BRAIN-V07-RUNTIME-AUDIT-STATIC-ASSET-ROUTE-FIX"

MAX_TOP_EXTENSIONS = 50
MAX_LARGE_FILES = 50
MAX_ZONE_KEY_SUBZONES = 8
MAX_CANDIDATE_ROWS = 80
MAX_PRIORITY_CANDIDATES = 25
MAX_TYPE_SAFETY_CANDIDATES = 30

SIZE_LARGE_KB = 1024.0
SIZE_VERY_LARGE_KB = 10240.0

CANDIDATE_EXTENSIONS = {".py", ".ps1", ".js", ".ts", ".sh", ".bat", ".cmd"}
CANDIDATE_HINT_SEGMENTS = {
    "tools",
    "scripts",
    "scriptorium",
    "gate_runners",
    "imperium_test_version",
}

REPORT_BUDGET = {
    "max_report_json_lines": 2000,
    "max_report_md_lines": 1200,
    "max_report_json_kb": 500,
    "max_report_md_kb": 500,
    "max_top_lists": 50,
}


@dataclass
class ZoneClassification:
    path: str
    category: str
    confidence: str
    reason: str
    recommended_action: str
    warnings: list[str]


@dataclass
class FileMeta:
    rel_posix: str
    top_zone: str
    ext: str
    size_kb: float
    tracked_status: str


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True, stderr=subprocess.DEVNULL).strip()


def run_git_lines(*args: str) -> list[str]:
    output = run_git(*args)
    if not output:
        return []
    return [line for line in output.splitlines() if line.strip()]


def classify_top_zone(name: str) -> ZoneClassification:
    n = name.lower()
    if name == "ORGANS":
        return ZoneClassification(
            path=name,
            category="ORGAN",
            confidence="HIGH",
            reason="Primary organ body path.",
            recommended_action="INVENTORY_ONLY",
            warnings=[],
        )
    if name in {"src"}:
        return ZoneClassification(name, "SOURCE_CODE", "HIGH", "Conventional source-code zone.", "REVIEW_REQUIRED", [])
    if name in {"tests"}:
        return ZoneClassification(name, "TESTS", "HIGH", "Conventional tests zone.", "INVENTORY_ONLY", [])
    if name in {"IMPERIUM_TEST_VERSION"}:
        return ZoneClassification(
            name,
            "TEST_VERSION",
            "HIGH",
            "Explicit test/experimental technology zone.",
            "REVIEW_REQUIRED",
            ["Do not edit in this task; candidate absorption source."],
        )
    if name in {"RUNTIME", "MEMORY_ZONES", ".imperium_runtime", "INBOX", "OUTBOX"}:
        return ZoneClassification(
            name,
            "RUNTIME_OR_LOCAL",
            "HIGH",
            "Likely runtime/local/generated operations zone.",
            "IGNORE_FOR_NOW",
            ["Treat as non-canon source for implementation claims."],
        )
    if name in {"ARTIFACTS", "ASSETS", "CURRENT_STATE"}:
        return ZoneClassification(
            name,
            "ASSET_OR_ARTIFACT",
            "HIGH",
            "Artifact/asset-heavy zone.",
            "INVENTORY_ONLY",
            ["Avoid mass cleanup without owner gate."],
        )
    if name in {"KILO_TEST", ".kilo"}:
        return ZoneClassification(
            name,
            "NEGATIVE_SAMPLE",
            "MEDIUM",
            "Test harness/negative or isolated zone by naming.",
            "NEGATIVE_SAMPLE_REVIEW",
            ["Keep outside canon merge without explicit absorption decision."],
        )
    if name in {"SANCTUM"}:
        return ZoneClassification(
            name,
            "RUNTIME_OR_LOCAL",
            "MEDIUM",
            "Root SANCTUM path is restricted in current task contracts.",
            "REVIEW_REQUIRED",
            ["Current task forbids modifications in root SANCTUM/."],
        )
    if name in {"TOOLS", "scripts"}:
        return ZoneClassification(
            name,
            "SCRIPT_TOOLING",
            "HIGH",
            "Named tooling/script execution zone.",
            "ABSORB_CANDIDATE",
            ["Read-only in this task; important for future absorption map."],
        )
    if name.startswith("."):
        return ZoneClassification(
            name,
            "ADVISORY",
            "LOW",
            "Dot-prefixed auxiliary/config zone.",
            "INVENTORY_ONLY",
            ["Category may require manual follow-up."],
        )
    return ZoneClassification(
        name,
        "UNKNOWN",
        "LOW",
        "No deterministic rule matched by top-level name alone.",
        "REVIEW_REQUIRED",
        ["Manual classification follow-up recommended."],
    )


def is_binary_extension(ext: str) -> bool:
    return ext in {
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".bmp",
        ".ico",
        ".pdf",
        ".zip",
        ".7z",
        ".rar",
        ".exe",
        ".dll",
        ".so",
        ".dylib",
        ".class",
        ".jar",
        ".pyd",
        ".woff",
        ".woff2",
        ".ttf",
        ".otf",
        ".mp4",
        ".mp3",
    }


def likely_family(meta: FileMeta) -> str:
    p = meta.rel_posix.lower()
    if "gate_runner" in p or "gate_runners" in p:
        return "GATE_RUNNER"
    if "inventory" in p:
        return "INVENTORY_TOOL"
    if "report" in p:
        return "REPORTING_TOOL"
    if "audit" in p:
        return "AUDIT_TOOL"
    if meta.ext == ".ps1":
        return "POWERSHELL_TOOL"
    if meta.ext in {".sh", ".bat", ".cmd"}:
        return "SHELL_HELPER"
    if meta.ext in {".js", ".ts"}:
        return "JS_TS_TOOL"
    if meta.ext == ".py":
        return "PYTHON_TOOL"
    return "UNKNOWN_TOOL"


def recommended_action(meta: FileMeta, zone_category: str) -> tuple[str, str, str]:
    p = meta.rel_posix.lower()
    fam = likely_family(meta)
    if meta.top_zone.lower() in {"kilo_test", ".kilo"}:
        return "NEGATIVE_SAMPLE_REVIEW", "MEDIUM", "Candidate lives in negative/test harness zone."
    if zone_category == "TEST_VERSION":
        if meta.ext == ".py":
            return "TYPE_HARDEN_REQUIRED", "MEDIUM", "Python candidate in test-version zone should be hardened before reuse."
        return "ABSORB_CANDIDATE", "MEDIUM", "Candidate in test-version zone may be useful for controlled absorption."
    if fam in {"GATE_RUNNER", "AUDIT_TOOL", "REPORTING_TOOL"} and meta.ext == ".py":
        return "TYPE_HARDEN_REQUIRED", "HIGH", "Gate/audit/reporting Python tool should have strict safety review."
    if zone_category in {"RUNTIME_OR_LOCAL", "ASSET_OR_ARTIFACT"}:
        return "IGNORE_FOR_NOW", "MEDIUM", "Runtime/artifact zone candidate is not primary absorption target now."
    if zone_category in {"SOURCE_CODE", "ORGAN", "SCRIPT_TOOLING"}:
        return "ABSORB_CANDIDATE", "MEDIUM", "Looks reusable under Scriptorium absorption discipline."
    return "REVIEW_REQUIRED", "LOW", "Insufficient confidence for direct action; manual triage required."


def main() -> int:
    repo_root = Path.cwd().resolve()
    script_path = Path(__file__).resolve()
    expected_root = script_path.parents[4]
    if repo_root != expected_root:
        raise SystemExit(
            f"STOP: run this script from repository root. cwd={repo_root} expected={expected_root}"
        )

    generated_at = utc_now_iso()
    current_head = run_git("rev-parse", "HEAD")
    branch = run_git("rev-parse", "--abbrev-ref", "HEAD")
    status_lines = run_git_lines("status", "--short")
    tracked_files = run_git_lines("ls-files")
    tracked_set = set(tracked_files)
    untracked_set = {
        line[3:].strip().replace("\\", "/")
        for line in status_lines
        if line.startswith("?? ")
    }

    top_level_entries = sorted(
        [p for p in repo_root.iterdir() if p.name != ".git"],
        key=lambda x: x.name.lower(),
    )

    zone_map: dict[str, dict[str, object]] = {}
    top_level_zones: list[dict[str, object]] = []
    uncertain_zones: list[str] = []

    for entry in top_level_entries:
        cls = classify_top_zone(entry.name)
        zone_map[entry.name] = {
            "classification": cls,
            "file_count": 0,
            "total_kb": 0.0,
            "subzone_counter": Counter(),
            "extensions": Counter(),
        }
        if cls.category in {"UNKNOWN", "REVIEW_REQUIRED"}:
            uncertain_zones.append(entry.name)
        top_level_zones.append(
            {
                "path": entry.name,
                "category": cls.category,
                "confidence": cls.confidence,
                "reason": cls.reason,
                "recommended_action": cls.recommended_action,
                "warnings": cls.warnings,
            }
        )

    extension_counter: Counter[str] = Counter()
    large_candidates: list[dict[str, object]] = []
    candidate_metas: list[FileMeta] = []
    directory_count_estimate = 0
    skipped_binary_ext_count = 0

    for dirpath, dirnames, filenames in os.walk(repo_root):
        current = Path(dirpath)
        if current.name == ".git":
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d != ".git"]
        directory_count_estimate += len(dirnames)
        rel_dir = current.relative_to(repo_root)
        top_zone = rel_dir.parts[0] if rel_dir.parts else "."
        if top_zone not in zone_map:
            cls = classify_top_zone(top_zone)
            zone_map[top_zone] = {
                "classification": cls,
                "file_count": 0,
                "total_kb": 0.0,
                "subzone_counter": Counter(),
                "extensions": Counter(),
            }
            if cls.category in {"UNKNOWN", "REVIEW_REQUIRED"}:
                uncertain_zones.append(top_zone)
        zone_info = zone_map[top_zone]

        for fn in filenames:
            fp = current / fn
            rel_posix = fp.relative_to(repo_root).as_posix()
            ext = fp.suffix.lower()
            try:
                size_kb = round(fp.stat().st_size / 1024.0, 2)
            except OSError:
                continue

            extension_counter[ext or "<no_ext>"] += 1
            zone_info["file_count"] = int(zone_info["file_count"]) + 1
            zone_info["total_kb"] = float(zone_info["total_kb"]) + size_kb
            zone_info["extensions"][ext or "<no_ext>"] += 1
            if len(rel_posix.split("/")) > 1:
                zone_info["subzone_counter"][rel_posix.split("/")[1]] += 1

            if size_kb >= SIZE_LARGE_KB:
                large_candidates.append({"path": rel_posix, "size_kb": size_kb, "top_zone": top_zone})

            if is_binary_extension(ext):
                skipped_binary_ext_count += 1
                continue

            low_parts = {part.lower() for part in rel_posix.split("/")}
            if ext in CANDIDATE_EXTENSIONS or (low_parts & CANDIDATE_HINT_SEGMENTS):
                tracked_status = "TRACKED" if rel_posix in tracked_set else ("UNTRACKED" if rel_posix in untracked_set else "UNKNOWN")
                candidate_metas.append(
                    FileMeta(
                        rel_posix=rel_posix,
                        top_zone=top_zone,
                        ext=ext or "<no_ext>",
                        size_kb=size_kb,
                        tracked_status=tracked_status,
                    )
                )

    top_extensions = extension_counter.most_common(MAX_TOP_EXTENSIONS)
    ext_omitted_count = max(0, len(extension_counter) - len(top_extensions))

    large_candidates_sorted = sorted(large_candidates, key=lambda x: float(x["size_kb"]), reverse=True)
    large_top = large_candidates_sorted[:MAX_LARGE_FILES]
    large_omitted_count = max(0, len(large_candidates_sorted) - len(large_top))

    zones_output: list[dict[str, object]] = []
    for zone_name in sorted(zone_map.keys(), key=str.lower):
        info = zone_map[zone_name]
        cls: ZoneClassification = info["classification"]
        subzones = [name for name, _count in info["subzone_counter"].most_common(MAX_ZONE_KEY_SUBZONES)]
        zones_output.append(
            {
                "path": zone_name,
                "category": cls.category,
                "confidence": cls.confidence,
                "reason": cls.reason,
                "file_count_estimate": int(info["file_count"]),
                "key_subzones": subzones,
                "warnings": cls.warnings,
                "recommended_action": cls.recommended_action,
            }
        )

    zone_summaries_counter: Counter[str] = Counter(z["category"] for z in zones_output)
    zone_summaries = [{"category": k, "zone_count": v} for k, v in sorted(zone_summaries_counter.items())]

    zone_category_by_name = {z["path"]: z["category"] for z in zones_output}
    candidate_rows: list[dict[str, object]] = []
    family_counter: Counter[str] = Counter()
    action_counter: Counter[str] = Counter()

    for meta in candidate_metas:
        fam = likely_family(meta)
        cat = zone_category_by_name.get(meta.top_zone, "UNKNOWN")
        action, confidence, reason = recommended_action(meta, cat)
        family_counter[fam] += 1
        action_counter[action] += 1
        candidate_rows.append(
            {
                "path": meta.rel_posix,
                "extension": meta.ext,
                "likely_family": fam,
                "source_zone": meta.top_zone,
                "tracked_status": meta.tracked_status,
                "size_kb": meta.size_kb,
                "recommended_action": action,
                "confidence": confidence,
                "reason": reason,
            }
        )

    candidate_rows = sorted(
        candidate_rows,
        key=lambda row: (
            {"TYPE_HARDEN_REQUIRED": 0, "ABSORB_CANDIDATE": 1, "REVIEW_REQUIRED": 2, "INVENTORY_ONLY": 3, "NEGATIVE_SAMPLE_REVIEW": 4, "IGNORE_FOR_NOW": 5}.get(
                str(row["recommended_action"]), 6
            ),
            -float(row["size_kb"]),
            str(row["path"]),
        ),
    )
    candidate_count_total = len(candidate_rows)
    candidate_rows_compact = candidate_rows[:MAX_CANDIDATE_ROWS]
    candidate_omitted_count = max(0, candidate_count_total - len(candidate_rows_compact))

    priority_absorption = [
        row["path"]
        for row in candidate_rows
        if row["recommended_action"] in {"ABSORB_CANDIDATE", "TYPE_HARDEN_REQUIRED"}
    ][:MAX_PRIORITY_CANDIDATES]
    type_safety_candidates = [
        row["path"] for row in candidate_rows if row["extension"] == ".py" and row["recommended_action"] == "TYPE_HARDEN_REQUIRED"
    ][:MAX_TYPE_SAFETY_CANDIDATES]

    # Known blockers/warnings from current repository context.
    blockers = [
        {
            "id": "BR-RT-STATIC-ASSET-ROUTE",
            "summary": "Second Brain full runtime audit baseline still blocked by required static asset route truth gap.",
            "evidence_path": "ORGANS/ADMINISTRATUM/GATE_RECEIPTS/GATE_RECEIPT_TASK_SECOND_BRAIN_V07_FULL_RUNTIME_PERFORMANCE_AUDIT_RUNNER_V0_1.json",
        }
    ]
    warnings = [
        {
            "id": "WRN-VERIFY-REPO-NOISE",
            "summary": "Repository-level verification still reports warning flood/noise and known legacy blocker classes.",
            "evidence_path": "scripts/verify_repo.py",
        },
        {
            "id": "WRN-TYPE-SAFETY-PARTIAL",
            "summary": "Python type safety policy exists but strict maturity rollout remains partial.",
            "evidence_path": "ORGANS/MECHANICUS/SCRIPTORIUM/PYTHON_TYPE_SAFETY/SCRIPT_TYPE_SAFETY_POLICY_V0_1.md",
        },
    ]
    unknowns = [
        {
            "id": "UNK-ZONE-CLASSIFICATION",
            "summary": "Some top-level zones remain low-confidence UNKNOWN/REVIEW_REQUIRED by metadata-only rules.",
            "count": len(uncertain_zones),
        }
    ]

    runtime_more_urgent = True
    priority_fixes = [
        NEXT_ALT_TASK,
        NEXT_DEFAULT_TASK,
        "TASK-IMPERIUM-CONTROL-CENTER-DATA-SPINE-CONTRACT-V0_1",
    ]
    next_recommended_task = NEXT_ALT_TASK if runtime_more_urgent else NEXT_DEFAULT_TASK

    inventory_json = {
        "inventory_id": INVENTORY_ID,
        "generated_at": generated_at,
        "current_head": current_head,
        "repo_root": str(repo_root),
        "branch": branch,
        "git_status_before_inventory": status_lines,
        "tracked_file_count": len(tracked_set),
        "untracked_file_count": len(untracked_set),
        "directory_count_estimate": directory_count_estimate,
        "top_level_zones": top_level_zones,
        "zone_summaries": zone_summaries,
        "extension_summary": {
            "top_extensions": [{"extension": ext, "count": cnt} for ext, cnt in top_extensions],
            "omitted_count": ext_omitted_count,
        },
        "large_file_candidates": {
            "threshold_kb": SIZE_LARGE_KB,
            "top_files": large_top,
            "omitted_count": large_omitted_count,
        },
        "report_budget": REPORT_BUDGET,
        "omitted_details": {
            "extension_summary_omitted_count": ext_omitted_count,
            "large_file_omitted_count": large_omitted_count,
            "script_candidate_omitted_count": candidate_omitted_count,
        },
        "limitations": [
            "Metadata-only scan: no deep content copy and no binary parsing.",
            "No script execution performed for discovered files.",
            "Classification is heuristic and may mark UNKNOWN/REVIEW_REQUIRED honestly.",
            f"Binary-extension candidate checks skipped for {skipped_binary_ext_count} files.",
        ],
        "verdict": "PASS_METADATA_TRUTH_BASELINE",
        "next_recommended_task": next_recommended_task,
    }

    zone_class_json = {
        "generated_at": generated_at,
        "current_head": current_head,
        "zones": zones_output,
        "classification_rules": {
            "top_level_name_rules": "Deterministic mappings for ORGANS, IMPERIUM_TEST_VERSION, runtime/artifact/test/source zones.",
            "fallback_rule": "UNKNOWN/REVIEW_REQUIRED when name-only confidence is low.",
            "scan_depth": "Whole-repo metadata walk with compact subzone summaries.",
        },
        "uncertain_zones": sorted(set(uncertain_zones)),
        "recommended_followups": [
            NEXT_DEFAULT_TASK,
            NEXT_ALT_TASK,
            "TASK-IMPERIUM-CONTROL-CENTER-DATA-SPINE-CONTRACT-V0_1",
        ],
        "verdict": "PASS_WITH_REVIEW_REQUIRED_ZONES",
    }

    blocker_map_json = {
        "generated_at": generated_at,
        "current_head": current_head,
        "blockers": blockers,
        "warnings": warnings,
        "unknowns": unknowns,
        "risk_summary": {
            "blocker_count": len(blockers),
            "warning_count": len(warnings),
            "unknown_count": len(unknowns),
        },
        "priority_fixes": priority_fixes,
        "next_recommended_task": next_recommended_task,
        "verdict": "PASS_BLOCKER_WARNING_MAP_CREATED",
    }

    candidate_json = {
        "generated_at": generated_at,
        "current_head": current_head,
        "candidate_count": candidate_count_total,
        "candidates": candidate_rows_compact,
        "family_summary": [{"family": fam, "count": cnt} for fam, cnt in family_counter.most_common()],
        "priority_absorption_candidates": priority_absorption,
        "type_safety_candidates": type_safety_candidates,
        "limitations": [
            "Candidates are metadata-derived and not executed.",
            "Compact candidate list may omit lower-priority rows.",
        ],
        "next_recommended_task": next_recommended_task,
        "verdict": "PASS_CANDIDATE_INVENTORY_CREATED",
    }

    admin_inventory_dir = repo_root / "ORGANS/ADMINISTRATUM/INVENTORY"
    scriptorium_inventory_dir = repo_root / "ORGANS/MECHANICUS/SCRIPTORIUM/INVENTORY"
    admin_inventory_dir.mkdir(parents=True, exist_ok=True)
    scriptorium_inventory_dir.mkdir(parents=True, exist_ok=True)

    (admin_inventory_dir / "WHOLE_REPO_TRUTH_INVENTORY_V0_1.json").write_text(
        json.dumps(inventory_json, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (admin_inventory_dir / "WHOLE_REPO_ZONE_CLASSIFICATION_V0_1.json").write_text(
        json.dumps(zone_class_json, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (admin_inventory_dir / "WHOLE_REPO_BLOCKER_WARNING_MAP_V0_1.json").write_text(
        json.dumps(blocker_map_json, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (scriptorium_inventory_dir / "SCRIPT_TOOL_CANDIDATE_INVENTORY_V0_1.json").write_text(
        json.dumps(candidate_json, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    inventory_md_lines = [
        "# WHOLE REPO TRUTH INVENTORY V0.1",
        "",
        f"- task_id: `{TASK_ID}`",
        f"- generated_at: `{generated_at}`",
        f"- current_head: `{current_head}`",
        f"- repo_root: `{repo_root}`",
        f"- tracked_file_count: `{len(tracked_set)}`",
        f"- untracked_file_count: `{len(untracked_set)}`",
        f"- directory_count_estimate: `{directory_count_estimate}`",
        "",
        "## What Was Inspected",
        "- Whole repository metadata (paths, sizes, extensions, top-level zones, candidate script/tool signals).",
        "",
        "## What Was Not Inspected",
        "- No deep content dump.",
        "- No binary parsing/OCR.",
        "- No execution of discovered scripts/tools.",
        "",
        "## Major Zone Summary",
        "| Category | Zone count |",
        "|---|---:|",
    ]
    for row in zone_summaries:
        inventory_md_lines.append(f"| {row['category']} | {row['zone_count']} |")
    inventory_md_lines.extend(
        [
            "",
            "## Key Warnings",
            f"- Blockers: `{len(blockers)}`; warnings: `{len(warnings)}`; unknown groups: `{len(unknowns)}`.",
            f"- Runtime route truth remains a blocker for full runtime baseline (`{NEXT_ALT_TASK}`).",
            "",
            "## What Should Not Be Touched Yet",
            "- Runtime/local/generated zones and restricted roots should remain untouched in inventory-only tasks.",
            "- Test-version code should be absorbed only through Scriptorium mapping and gate discipline.",
            "",
            "## Next Recommended Task",
            f"- `{next_recommended_task}`",
        ]
    )
    (admin_inventory_dir / "WHOLE_REPO_TRUTH_INVENTORY_V0_1.md").write_text(
        "\n".join(inventory_md_lines).rstrip() + "\n", encoding="utf-8"
    )

    zone_md_lines = [
        "# WHOLE REPO ZONE CLASSIFICATION V0.1",
        "",
        f"- generated_at: `{generated_at}`",
        f"- current_head: `{current_head}`",
        "",
        "| Zone | Category | Confidence | File count est. | Recommended action | Warning count |",
        "|---|---|---|---:|---|---:|",
    ]
    for row in zones_output:
        zone_md_lines.append(
            f"| `{row['path']}` | {row['category']} | {row['confidence']} | {row['file_count_estimate']} | {row['recommended_action']} | {len(row['warnings'])} |"
        )
    zone_md_lines.extend(
        [
            "",
            "## Uncertain Zones",
            f"- count: `{len(set(uncertain_zones))}`",
            "- " + (", ".join(sorted(set(uncertain_zones))) if uncertain_zones else "none"),
        ]
    )
    (admin_inventory_dir / "WHOLE_REPO_ZONE_CLASSIFICATION_V0_1.md").write_text(
        "\n".join(zone_md_lines).rstrip() + "\n", encoding="utf-8"
    )

    blocker_md_lines = [
        "# WHOLE REPO BLOCKER WARNING MAP V0.1",
        "",
        f"- generated_at: `{generated_at}`",
        f"- current_head: `{current_head}`",
        "",
        "## Blockers",
    ]
    for b in blockers:
        blocker_md_lines.append(f"- `{b['id']}`: {b['summary']} (`{b['evidence_path']}`)")
    blocker_md_lines.append("")
    blocker_md_lines.append("## Warnings")
    for w in warnings:
        blocker_md_lines.append(f"- `{w['id']}`: {w['summary']} (`{w['evidence_path']}`)")
    blocker_md_lines.extend(
        [
            "",
            "## Unknowns",
        ]
    )
    for u in unknowns:
        blocker_md_lines.append(f"- `{u['id']}`: {u['summary']} (count=`{u['count']}`)")
    blocker_md_lines.extend(
        [
            "",
            "## Priority Fixes",
            f"1. `{priority_fixes[0]}`",
            f"2. `{priority_fixes[1]}`",
            f"3. `{priority_fixes[2]}`",
            "",
            f"## Next Recommended Task\n- `{next_recommended_task}`",
        ]
    )
    (admin_inventory_dir / "WHOLE_REPO_BLOCKER_WARNING_MAP_V0_1.md").write_text(
        "\n".join(blocker_md_lines).rstrip() + "\n", encoding="utf-8"
    )

    family_summary_rows = candidate_json["family_summary"]
    candidate_md_lines = [
        "# SCRIPT TOOL CANDIDATE INVENTORY V0.1",
        "",
        f"- generated_at: `{generated_at}`",
        f"- current_head: `{current_head}`",
        f"- candidate_count_total: `{candidate_count_total}`",
        f"- candidate_rows_included: `{len(candidate_rows_compact)}`",
        f"- candidate_rows_omitted: `{candidate_omitted_count}`",
        "",
        "## Family Summary",
        "| Family | Count |",
        "|---|---:|",
    ]
    for row in family_summary_rows[:MAX_TOP_EXTENSIONS]:
        candidate_md_lines.append(f"| {row['family']} | {row['count']} |")
    candidate_md_lines.extend(
        [
            "",
            "## Priority Absorption Candidates (sample)",
        ]
    )
    for p in priority_absorption[:30]:
        candidate_md_lines.append(f"- `{p}`")
    candidate_md_lines.extend(
        [
            "",
            "## Type Safety Candidates (sample)",
        ]
    )
    for p in type_safety_candidates[:30]:
        candidate_md_lines.append(f"- `{p}`")
    candidate_md_lines.append("")
    candidate_md_lines.append(f"## Next Recommended Task\n- `{next_recommended_task}`")
    (scriptorium_inventory_dir / "SCRIPT_TOOL_CANDIDATE_INVENTORY_V0_1.md").write_text(
        "\n".join(candidate_md_lines).rstrip() + "\n", encoding="utf-8"
    )

    print("INVENTORY_JSON", admin_inventory_dir / "WHOLE_REPO_TRUTH_INVENTORY_V0_1.json")
    print("ZONE_JSON", admin_inventory_dir / "WHOLE_REPO_ZONE_CLASSIFICATION_V0_1.json")
    print("BLOCKER_JSON", admin_inventory_dir / "WHOLE_REPO_BLOCKER_WARNING_MAP_V0_1.json")
    print("CANDIDATE_JSON", scriptorium_inventory_dir / "SCRIPT_TOOL_CANDIDATE_INVENTORY_V0_1.json")
    print("NEXT_RECOMMENDED_TASK", next_recommended_task)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
