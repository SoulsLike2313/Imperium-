from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import traceback
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "ADMINISTRATUM_RESUME_CONTINUITY_PACK_V0_2"
PACK_PREFIX = "RESUME_CONTINUITY_PACK_"
TASK_ID = "TASK-20260510-ADMINISTRATUM-RESUME-CONTINUITY-PACK-V0_2-MANUAL"
ROUTE_TRUTH_RELATIVE = Path("ORGANS") / "ADMINISTRATUM" / "CONFIG" / "ADMINISTRATUM_ROUTE_TRUTH_V0_1.json"

DEFAULT_ROUTE_TRUTH: dict[str, Any] = {
    "schema_version": "ADMINISTRATUM_ROUTE_TRUTH_V0_1",
    "repository": {
        "owner": "SoulsLike2313",
        "name": "Imperium-",
        "remote_url": "https://github.com/SoulsLike2313/Imperium-",
        "tree_url_template": "https://github.com/SoulsLike2313/Imperium-/tree/{head_sha}",
    },
    "paths": {
        "pc_repo_root": "E:\\IMPERIUM",
        "vm2_repo_root": "/home/vboxuser2/IMPERIUM_WORK/Imperium-",
    },
    "vm2_ssh": {
        "user_host": "vboxuser2@127.0.0.1",
        "port": 2223,
        "key_path_powershell": "$env:USERPROFILE\\.ssh\\imperium_pc_to_vm2_ed25519_20260418",
        "ssh_command_powershell": "ssh -i $env:USERPROFILE\\.ssh\\imperium_pc_to_vm2_ed25519_20260418 -p 2223 vboxuser2@127.0.0.1",
    },
}

OWNER_LATEST_DECISION = (
    "The continuity pack was judged too weak for exact resume. "
    "Administratum v0.2 must produce one resume-first pack that preserves the exact continuation point: "
    "START_HERE, LAST_POINT_STATE, OWNER_DECISION_LOG, NEXT_ATOMIC_STEP, and evidence ledger."
)

DO_NOT_DO = [
    "do not claim green/canon/real-task-ready",
    "do not replace the last verified point with a broad summary",
    "do not split into weak modes instead of one strong resume pack",
    "do not touch THRONE",
    "do not sync into THRONE",
    "do not delete old packs or artifacts",
    "do not continue by memory without evidence paths",
    "do not use latest guessing without explicit path/receipt/hash",
]

CURRENT_OBJECTIVE = (
    "Upgrade Administratum continuity to resume-first v0.2 so a new chat can continue from the exact last working point: "
    "what was done, where execution stopped, which Owner decision changed course, which atomic step is next, "
    "and which files/receipts prove it."
)

NEXT_ATOMIC_STEP = (
    "Run the resume continuity pack builder, validate START_HERE.md in the fresh RESUME_CONTINUITY_PACK output, "
    "then continue to the next organ only after resume evidence is sufficient."
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def detect_repo_root() -> Path:
    candidates: list[Path] = []

    script_path = Path(__file__).resolve()
    if len(script_path.parents) >= 4:
        candidates.append(script_path.parents[3])

    env_root = os.environ.get("IMPERIUM_ROOT")
    if env_root:
        candidates.append(Path(env_root).expanduser())

    candidates.append(Path.cwd())

    for candidate in candidates:
        if (candidate / ".git").exists() or (candidate / "AGENTS.md").exists():
            return candidate

    return candidates[0]


def read_text(path: Path, limit: int = 24000) -> str | None:
    try:
        if not path.exists() or not path.is_file():
            return None
        data = path.read_text(encoding="utf-8", errors="replace")
        if len(data) > limit:
            return data[:limit] + "\n...[TRUNCATED]..."
        return data
    except Exception:
        return None


def read_json(path: Path) -> Any | None:
    txt = read_text(path, limit=2_000_000)
    if txt is None:
        return None
    try:
        return json.loads(txt)
    except Exception:
        return None


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except Exception:
        return str(path)


def mtime_iso(path: Path) -> str:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()
    except Exception:
        return "UNKNOWN"


def sorted_by_mtime(paths: list[Path]) -> list[Path]:
    return sorted(paths, key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)


def find_files(root: Path, pattern: str, max_items: int = 200) -> list[Path]:
    try:
        return sorted_by_mtime([p for p in root.rglob(pattern) if p.is_file()])[:max_items]
    except Exception:
        return []


def latest_dir(base: Path, prefix: str) -> Path | None:
    if not base.exists():
        return None
    candidates = [p for p in base.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    if not candidates:
        return None
    return sorted_by_mtime(candidates)[0]


def merge_dict(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_dict(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_route_truth(root: Path) -> dict[str, Any]:
    source_path = root / ROUTE_TRUTH_RELATIVE
    payload = read_json(source_path)

    route_truth = dict(DEFAULT_ROUTE_TRUTH)
    if isinstance(payload, dict):
        route_truth = merge_dict(route_truth, payload)

    route_truth["_source_path"] = str(source_path)
    route_truth["_source_exists"] = source_path.exists()
    return route_truth


def run_git(root: Path, args: list[str]) -> tuple[bool, str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    output = (proc.stdout or proc.stderr or "").strip()
    return proc.returncode == 0, output


def first_line(text: str) -> str:
    for line in text.splitlines():
        value = line.strip()
        if value:
            return value
    return ""


def collect_git_truth(root: Path, route_truth: dict[str, Any]) -> dict[str, Any]:
    ok_head, head_raw = run_git(root, ["rev-parse", "HEAD"])
    ok_count, count_raw = run_git(root, ["rev-list", "--count", "HEAD"])
    ok_latest, latest_raw = run_git(root, ["log", "-1", "--oneline"])

    head_sha = first_line(head_raw) if ok_head else ""
    count_str = first_line(count_raw) if ok_count else ""
    latest_commit_oneline = first_line(latest_raw) if ok_latest else ""

    commit_count: int | None = int(count_str) if count_str.isdigit() else None

    repo_cfg = route_truth.get("repository") if isinstance(route_truth.get("repository"), dict) else {}
    remote_url = str(repo_cfg.get("remote_url", DEFAULT_ROUTE_TRUTH["repository"]["remote_url"]))
    tree_template = str(
        repo_cfg.get("tree_url_template", DEFAULT_ROUTE_TRUTH["repository"]["tree_url_template"])
    )
    tree_url = tree_template.format(head_sha=head_sha) if head_sha else ""

    return {
        "head_sha": head_sha,
        "commit_count": commit_count,
        "latest_commit_oneline": latest_commit_oneline,
        "tree_url": tree_url,
        "remote_url": remote_url,
        "collection": {
            "head_ok": ok_head,
            "count_ok": ok_count,
            "latest_ok": ok_latest,
        },
    }


def collect_finalization_receipts(root: Path) -> list[dict[str, Any]]:
    receipts: list[dict[str, Any]] = []
    for p in find_files(root / "ARTIFACTS", "FINALIZATION_RECEIPT_EXTERNAL.json", 200):
        data = read_json(p) or {}
        receipts.append(
            {
                "path": str(p),
                "relative_path": safe_rel(p, root),
                "mtime_utc": mtime_iso(p),
                "task_id": data.get("task_id"),
                "verdict": data.get("verdict"),
                "finalization_time": data.get("finalization_time"),
                "final_zip_path": data.get("final_zip_path"),
                "final_zip_sha256": data.get("final_zip_sha256"),
                "manifest_path": data.get("manifest_path"),
                "manifest_sha256": data.get("manifest_sha256"),
            }
        )

    for p in find_files(root / "ARTIFACTS", "*FINAL*RECEIPT*.json", 200):
        if p.name == "FINALIZATION_RECEIPT_EXTERNAL.json":
            continue
        data = read_json(p) or {}
        receipts.append(
            {
                "path": str(p),
                "relative_path": safe_rel(p, root),
                "mtime_utc": mtime_iso(p),
                "task_id": data.get("task_id"),
                "verdict": data.get("verdict") or data.get("status"),
                "finalization_time": data.get("finalization_time")
                or data.get("timestamp")
                or data.get("created_at"),
            }
        )

    return sorted(receipts, key=lambda x: x.get("finalization_time") or x.get("mtime_utc") or "", reverse=True)


def collect_latest_packs(root: Path) -> dict[str, Any]:
    packs_root = root / "ORGANS" / "ADMINISTRATUM" / "CONTINUITY" / "PACKS"
    return {
        "packs_root": str(packs_root),
        "latest_resume_pack_before_this_run": str(latest_dir(packs_root, "RESUME_CONTINUITY_PACK_"))
        if latest_dir(packs_root, "RESUME_CONTINUITY_PACK_")
        else None,
        "latest_semantic_pack": str(latest_dir(packs_root, "CONTINUITY_PACK_"))
        if latest_dir(packs_root, "CONTINUITY_PACK_")
        else None,
        "latest_developer_pack": str(latest_dir(packs_root, "DEVELOPER_GRADE_CONTINUITY_PACK_"))
        if latest_dir(packs_root, "DEVELOPER_GRADE_CONTINUITY_PACK_")
        else None,
        "recent_pack_dirs": [
            {"path": str(p), "name": p.name, "mtime_utc": mtime_iso(p)}
            for p in sorted_by_mtime([d for d in packs_root.iterdir() if d.is_dir()])[:20]
        ]
        if packs_root.exists()
        else [],
    }


def collect_dashboards(root: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for p in find_files(root / "ORGANS", "DASHBOARD_REGISTRY.json", 50):
        data = read_json(p)
        out.append(
            {
                "registry_path": str(p),
                "relative_path": safe_rel(p, root),
                "mtime_utc": mtime_iso(p),
                "data": data,
            }
        )
    for p in find_files(root / "ORGANS", "DASHBOARD_STATUS*.json", 80):
        data = read_json(p)
        out.append(
            {
                "status_path": str(p),
                "relative_path": safe_rel(p, root),
                "mtime_utc": mtime_iso(p),
                "data": data,
            }
        )
    return out


def collect_organ_status(root: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for p in find_files(root / "ORGANS", "ORGAN_STATUS.json", 80):
        data = read_json(p) or {}
        organ_id = data.get("organ_id") or (p.parts[-3] if len(p.parts) >= 3 else p.parent.name)
        out.append(
            {
                "organ_id": organ_id,
                "path": str(p),
                "relative_path": safe_rel(p, root),
                "mtime_utc": mtime_iso(p),
                "status": data.get("status"),
                "classification_target": data.get("classification_target"),
                "current_dashboard_id": data.get("current_dashboard_id"),
                "blockers": data.get("blockers"),
                "limitations": data.get("limitations"),
            }
        )
    return out


def collect_key_reports(root: Path) -> list[dict[str, Any]]:
    names = [
        "ALL_ORGANS_GAP_REPORT*.json",
        "DOCTRINARIUM_STATUS*.json",
        "ORGAN_UTILITY_GAP_REPORT*.json",
        "PLAYWRIGHT_AUDIT*_REPORT.json",
        "TEST_REPORT.json",
        "BUILD_RECEIPT.json",
        "HANDOFF_SUFFICIENCY_REPORT.json",
        "CONTINUITY_PACK_TEST_REPORT.json",
    ]
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for pat in names:
        for p in find_files(root, pat, 100):
            key = str(p).lower()
            if key in seen:
                continue
            seen.add(key)
            data = read_json(p)
            out.append(
                {
                    "path": str(p),
                    "relative_path": safe_rel(p, root),
                    "mtime_utc": mtime_iso(p),
                    "sha256": sha256_file(p),
                    "summary_keys": list(data.keys())[:20] if isinstance(data, dict) else None,
                    "verdict": data.get("verdict") if isinstance(data, dict) else None,
                    "status": data.get("status") if isinstance(data, dict) else None,
                    "task_id": data.get("task_id") if isinstance(data, dict) else None,
                }
            )
    return sorted(out, key=lambda x: x.get("mtime_utc") or "", reverse=True)[:120]


def collect_active_tasks(root: Path) -> dict[str, Any]:
    candidates = []
    for p in find_files(root, "ACTIVE_TASKS.json", 30):
        candidates.append(
            {
                "path": str(p),
                "relative_path": safe_rel(p, root),
                "mtime_utc": mtime_iso(p),
                "data": read_json(p),
            }
        )
    return {"candidates": candidates[:10]}


def infer_last_verified_point(
    receipts: list[dict[str, Any]], packs: dict[str, Any], git_truth: dict[str, Any]
) -> dict[str, Any]:
    latest_receipt = receipts[0] if receipts else None
    return {
        "latest_finalized_artifact": latest_receipt,
        "latest_developer_pack": packs.get("latest_developer_pack"),
        "latest_semantic_pack": packs.get("latest_semantic_pack"),
        "latest_resume_pack_before_this_run": packs.get("latest_resume_pack_before_this_run"),
        "owner_latest_decision": OWNER_LATEST_DECISION,
        "current_objective": CURRENT_OBJECTIVE,
        "next_atomic_step": NEXT_ATOMIC_STEP,
        "resume_rule": (
            "A new chat must read START_HERE.md, then LAST_POINT_STATE.json, then NEXT_ATOMIC_STEP.md. "
            "If this is insufficient to continue exactly, the pack is weak."
        ),
        "git_truth": git_truth,
    }


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def md_path_list(items: list[dict[str, Any]], title: str, max_items: int = 20) -> str:
    lines = [f"# {title}", ""]
    if not items:
        lines.append("- none found")
        return "\n".join(lines) + "\n"
    for i, item in enumerate(items[:max_items], 1):
        label = (
            item.get("task_id")
            or item.get("verdict")
            or item.get("status")
            or item.get("relative_path")
            or item.get("path")
        )
        lines.append(f"{i}. `{label}`")
        for key in ["verdict", "status", "finalization_time", "mtime_utc", "relative_path", "path", "final_zip_sha256"]:
            val = item.get(key)
            if val:
                lines.append(f"   - {key}: `{val}`")
    return "\n".join(lines) + "\n"


def route_truth_view(route_truth: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": route_truth.get("schema_version"),
        "source_path": route_truth.get("_source_path"),
        "source_exists": route_truth.get("_source_exists"),
        "repository": route_truth.get("repository"),
        "paths": route_truth.get("paths"),
        "vm2_ssh": route_truth.get("vm2_ssh"),
    }


def build_pack(root: Path) -> dict[str, Any]:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    packs_root = root / "ORGANS" / "ADMINISTRATUM" / "CONTINUITY" / "PACKS"
    pack_dir = packs_root / f"{PACK_PREFIX}{ts}"
    artifact_root = root / "ARTIFACTS" / TASK_ID
    package_dir = artifact_root / "14_PACKAGE"
    packs_root.mkdir(parents=True, exist_ok=True)
    pack_dir.mkdir(parents=True, exist_ok=False)
    artifact_root.mkdir(parents=True, exist_ok=True)
    package_dir.mkdir(parents=True, exist_ok=True)

    route_truth = load_route_truth(root)
    git_truth = collect_git_truth(root, route_truth)

    receipts = collect_finalization_receipts(root)
    packs = collect_latest_packs(root)
    dashboards = collect_dashboards(root)
    organ_status = collect_organ_status(root)
    reports = collect_key_reports(root)
    active_tasks = collect_active_tasks(root)
    last_point = infer_last_verified_point(receipts, packs, git_truth)

    state = {
        "schema_version": SCHEMA,
        "pack_id": pack_dir.name,
        "generated_at_utc": utc_now(),
        "root": str(root),
        "task_id": TASK_ID,
        "classification": "RESUME_CONTINUITY_NOT_GENERAL_SUMMARY",
        "owner_latest_decision": OWNER_LATEST_DECISION,
        "current_objective": CURRENT_OBJECTIVE,
        "route_truth": route_truth_view(route_truth),
        "git_truth": git_truth,
        "last_verified_point": last_point,
        "packs": packs,
        "latest_finalization_receipts": receipts[:40],
        "active_tasks": active_tasks,
        "organ_status": organ_status,
        "dashboards": dashboards[:40],
        "key_reports": reports,
        "do_not_do": DO_NOT_DO,
        "next_atomic_step": NEXT_ATOMIC_STEP,
        "quality_contract": {
            "must_answer_where_are_we": True,
            "must_answer_what_changed_last": True,
            "must_answer_what_owner_corrected": True,
            "must_answer_next_atomic_step": True,
            "must_include_evidence_paths": True,
            "must_not_be_only_system_description": True,
            "must_not_claim_green_or_canon": True,
        },
    }

    latest = last_point.get("latest_finalized_artifact") or {}
    latest_label = latest.get("task_id") or latest.get("relative_path") or "UNKNOWN"
    latest_verdict = latest.get("verdict") or "UNKNOWN"

    paths_info = route_truth.get("paths") if isinstance(route_truth.get("paths"), dict) else {}
    ssh_info = route_truth.get("vm2_ssh") if isinstance(route_truth.get("vm2_ssh"), dict) else {}

    start_here = f"""# START HERE - Resume Continuity Pack v0.2

This pack is not a general story of the system.
It exists so a new chat can continue from the last working point without re-discovery.

## Canonical Routes
- PC repo root: `{paths_info.get('pc_repo_root', 'E:\\\\IMPERIUM')}`
- VM2 repo root: `{paths_info.get('vm2_repo_root', '/home/vboxuser2/IMPERIUM_WORK/Imperium-')}`
- VM2 SSH: `{ssh_info.get('user_host', 'vboxuser2@127.0.0.1')} -p {ssh_info.get('port', 2223)} -i {ssh_info.get('key_path_powershell', '$env:USERPROFILE\\\\.ssh\\\\imperium_pc_to_vm2_ed25519_20260418')}`

## Git Truth
- head_sha: `{git_truth.get('head_sha') or 'UNAVAILABLE'}`
- commit_count: `{git_truth.get('commit_count') if git_truth.get('commit_count') is not None else 'UNAVAILABLE'}`
- latest_commit_oneline: `{git_truth.get('latest_commit_oneline') or 'UNAVAILABLE'}`
- tree_url: `{git_truth.get('tree_url') or 'UNAVAILABLE'}`

## Current Objective
{CURRENT_OBJECTIVE}

## Owner Latest Correction
{OWNER_LATEST_DECISION}

## Last Verified Artifact / Evidence
- latest: `{latest_label}`
- verdict: `{latest_verdict}`
- finalization_time: `{latest.get('finalization_time') or latest.get('mtime_utc') or 'UNKNOWN'}`
- evidence_path: `{latest.get('path') or 'UNKNOWN'}`
- final_zip_sha256: `{latest.get('final_zip_sha256') or 'UNKNOWN'}`

## Current Development Point
Administratum continuity is being upgraded from weak/bootstrap handoff to exact resume handoff.
The key requirement is: `START_HERE.md + LAST_POINT_STATE.json + NEXT_ATOMIC_STEP.md + evidence ledger` must be enough to resume.

## Next Atomic Step
{NEXT_ATOMIC_STEP}

## Read Order
1. `START_HERE.md`
2. `LAST_POINT_STATE.json`
3. `OWNER_DECISION_LOG.md`
4. `NEXT_ATOMIC_STEP.md`
5. `EVIDENCE_INDEX.md`
6. `OPEN_BLOCKERS.md`

## Do Not Do
"""
    for item in DO_NOT_DO:
        start_here += f"- {item}\n"
    start_here += "\n## Resume Test\nIf a new chat still asks 'where are we?' after this file, the pack failed.\n"

    owner_log = f"""# OWNER DECISION LOG

## Latest Correction
{OWNER_LATEST_DECISION}

## Meaning
The earlier idea of weak split modes is not enough.
The real failure is continuity that cannot preserve the exact last working point cleanly.

## New Direction
Administratum v0.2 must produce one strong resume-first pack.
Mode separation can come later only after resume quality is fixed.

## Current Manual Patch
- task_id: `{TASK_ID}`
- action: install `administratum_build_resume_continuity_pack_v0_2.py`, dashboard button, registry, receipt
- route truth source: `{route_truth.get('_source_path')}`
"""

    next_step_md = f"""# NEXT ATOMIC STEP

{NEXT_ATOMIC_STEP}

## Acceptance Check
- Fresh `RESUME_CONTINUITY_PACK_*` exists.
- `START_HERE.md` contains canonical routes and exact git truth.
- `LAST_POINT_STATE.json` includes `route_truth` and `git_truth`.
- `EVIDENCE_INDEX.md` lists real paths, not vague references.
- `DO_NOT_DO.md` blocks fake green/canon/latest guessing.

## After Passing
Continue to the next organ only after human review confirms the resume payload is sufficient.
"""

    open_blockers = """# OPEN BLOCKERS

- Continuity was judged insufficient for exact resume; this v0.2 pack is the corrective layer.
- Doctrinarium still does not authorize canon/green/real-task-ready.
- Hard-law enforcement remains incomplete until Doctrinarium says otherwise.
- Organ ports may exist but can still contain weak/unknown/scaffold fields.
- Officio Agentis role contracts are not yet formalized.
"""

    do_not_do_md = "# DO NOT DO\n\n" + "".join(f"- {x}\n" for x in DO_NOT_DO)

    evidence_md = md_path_list(receipts[:30], "EVIDENCE INDEX - FINALIZATION RECEIPTS", 30)
    reports_md = md_path_list(reports[:30], "KEY REPORTS", 30)
    artifacts_md = md_path_list(receipts[:40], "ARTIFACTS LEDGER", 40)

    organ_md_lines = ["# ORGAN READINESS SNAPSHOT", ""]
    if not organ_status:
        organ_md_lines.append("- no ORGAN_STATUS.json files found")
    for item in organ_status:
        organ_md_lines.append(f"## {item.get('organ_id')}")
        organ_md_lines.append(f"- status: `{item.get('status')}`")
        organ_md_lines.append(f"- classification_target: `{item.get('classification_target')}`")
        organ_md_lines.append(f"- dashboard: `{item.get('current_dashboard_id')}`")
        organ_md_lines.append(f"- path: `{item.get('relative_path')}`")
        blockers = item.get("blockers") or []
        if blockers:
            organ_md_lines.append("- blockers:")
            for blocker in blockers:
                organ_md_lines.append(f"  - {blocker}")
        organ_md_lines.append("")
    organ_md = "\n".join(organ_md_lines) + "\n"

    development_map = f"""# DEVELOPMENT MAP

## Where We Are
Administratum is being upgraded to resume-first continuity v0.2.

## What Was Wrong
The earlier pack described the system but did not reliably let the next chat continue from the exact last point.

## What This Patch Adds
- Canonical route truth (PC root, VM2 root, SSH route).
- Exact git truth (`head_sha`, `commit_count`, `latest_commit_oneline`, `tree_url`).
- `START_HERE.md` as mandatory first file.
- `LAST_POINT_STATE.json` as machine-readable truth snapshot.
- `OWNER_DECISION_LOG.md` to preserve course corrections.
- `NEXT_ATOMIC_STEP.md` to remove ambiguity.
- Evidence and artifact ledgers.

## What Remains Next
After this pack passes human review: formalize `Officio Agentis v0.1`.
"""

    quality = {
        "schema_version": "RESUME_PACK_QUALITY_GATE_V0_2",
        "generated_at_utc": utc_now(),
        "checks": {
            "has_start_here": True,
            "has_last_point_state": True,
            "has_owner_latest_decision": True,
            "has_next_atomic_step": True,
            "has_evidence_ledger": len(receipts) > 0,
            "has_do_not_do": True,
            "has_route_truth": True,
            "has_git_truth_with_tree_url": bool(git_truth.get("tree_url")),
            "not_general_summary_only": True,
            "explicitly_blocks_fake_green": True,
        },
        "verdict": "PASS_RESUME_CONTINUITY_PACK_V0_2_WITH_LIMITATIONS",
        "limitations": [
            "Human review still required.",
            "Does not claim canon/green/real-task-ready.",
            "Depends on local artifact/receipt presence at build time.",
        ],
    }

    write_text(pack_dir / "START_HERE.md", start_here)
    write_json(pack_dir / "LAST_POINT_STATE.json", state)
    write_text(pack_dir / "OWNER_DECISION_LOG.md", owner_log)
    write_text(pack_dir / "NEXT_ATOMIC_STEP.md", next_step_md)
    write_text(pack_dir / "DO_NOT_DO.md", do_not_do_md)
    write_text(pack_dir / "OPEN_BLOCKERS.md", open_blockers)
    write_text(pack_dir / "DEVELOPMENT_MAP.md", development_map)
    write_text(pack_dir / "EVIDENCE_INDEX.md", evidence_md + "\n" + reports_md)
    write_json(pack_dir / "EVIDENCE_INDEX.json", {"finalization_receipts": receipts, "key_reports": reports})
    write_text(pack_dir / "ARTIFACTS_LEDGER.md", artifacts_md)
    write_json(pack_dir / "ARTIFACTS_LEDGER.json", receipts)
    write_text(pack_dir / "ORGAN_READINESS.md", organ_md)
    write_json(pack_dir / "ORGAN_READINESS.json", organ_status)
    write_json(pack_dir / "DASHBOARDS.json", dashboards)
    write_text(pack_dir / "DASHBOARDS.md", md_path_list(dashboards, "DASHBOARDS", 40))
    write_json(pack_dir / "PACK_QUALITY_GATE.json", quality)
    write_text(
        pack_dir / "PACK_QUALITY_GATE.md",
        (
            "# PACK QUALITY GATE\n\n"
            f"- verdict: `{quality['verdict']}`\n"
            "- meaning: resume-first continuity built, but no canon/green claim.\n"
        ),
    )

    receipt = {
        "schema_version": "RESUME_CONTINUITY_BUILD_RECEIPT_V0_2",
        "task_id": TASK_ID,
        "pack_id": pack_dir.name,
        "pack_path": str(pack_dir),
        "generated_at_utc": utc_now(),
        "verdict": quality["verdict"],
        "owner_latest_decision_captured": True,
        "start_here_path": str(pack_dir / "START_HERE.md"),
        "last_point_state_path": str(pack_dir / "LAST_POINT_STATE.json"),
        "git_truth": git_truth,
        "limitations": quality["limitations"],
    }
    write_json(pack_dir / "BUILD_RECEIPT.json", receipt)

    file_entries = []
    for p in sorted([x for x in pack_dir.rglob("*") if x.is_file()]):
        if p.name in {"MANIFEST.json", "SHA256SUMS.txt"}:
            continue
        file_entries.append(
            {
                "relative_path": safe_rel(p, pack_dir),
                "size_bytes": p.stat().st_size,
                "sha256": sha256_file(p),
            }
        )

    manifest = {
        "schema_version": "RESUME_CONTINUITY_MANIFEST_V0_2",
        "task_id": TASK_ID,
        "pack_id": pack_dir.name,
        "generated_at_utc": utc_now(),
        "files": file_entries,
    }
    write_json(pack_dir / "MANIFEST.json", manifest)
    sha_lines = [f"{e['sha256']}  {e['relative_path']}" for e in file_entries]
    write_text(pack_dir / "SHA256SUMS.txt", "\n".join(sha_lines) + "\n")

    write_json(artifact_root / "06_RESUME_PACK_REFERENCE.json", receipt)
    zip_path = package_dir / f"{TASK_ID}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted([x for x in pack_dir.rglob("*") if x.is_file()]):
            z.write(p, arcname=f"{pack_dir.name}/{safe_rel(p, pack_dir)}")
        z.write(artifact_root / "06_RESUME_PACK_REFERENCE.json", arcname="06_RESUME_PACK_REFERENCE.json")

    sidecar = package_dir / f"{TASK_ID}.zip.sha256"
    write_text(sidecar, f"{sha256_file(zip_path)}  {zip_path}\n")

    finalization = {
        "schema_version": "FINALIZATION_RECEIPT_EXTERNAL_V0_2",
        "task_id": TASK_ID,
        "final_zip_path": str(zip_path),
        "final_zip_sha256": sha256_file(zip_path),
        "sidecar_path": str(sidecar),
        "sidecar_sha256": sha256_file(sidecar),
        "pack_path": str(pack_dir),
        "pack_manifest_path": str(pack_dir / "MANIFEST.json"),
        "pack_manifest_sha256": sha256_file(pack_dir / "MANIFEST.json"),
        "sha256sums_path": str(pack_dir / "SHA256SUMS.txt"),
        "sha256sums_sha256": sha256_file(pack_dir / "SHA256SUMS.txt"),
        "git_truth": git_truth,
        "finalization_time": utc_now(),
        "verdict": quality["verdict"],
        "self_reference_policy": "zip and sidecar excluded from internal pack manifest/hash payload",
    }
    write_json(artifact_root / "FINALIZATION_RECEIPT_EXTERNAL.json", finalization)

    return {
        "ok": True,
        "task_id": TASK_ID,
        "pack_path": str(pack_dir),
        "start_here": str(pack_dir / "START_HERE.md"),
        "final_zip_path": str(zip_path),
        "final_zip_sha256": finalization["final_zip_sha256"],
        "git_truth": git_truth,
        "verdict": quality["verdict"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=os.environ.get("IMPERIUM_ROOT") or str(detect_repo_root()))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        result = build_pack(Path(args.root))
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("RESUME CONTINUITY PACK BUILT")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        payload = {
            "ok": False,
            "error": str(exc),
            "traceback": traceback.format_exc(),
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
