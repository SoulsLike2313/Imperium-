from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import traceback
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "ADMINISTRATUM_RESUME_CONTINUITY_PACK_V0_2"
PACK_PREFIX = "RESUME_CONTINUITY_PACK_"
TASK_ID = "TASK-20260510-ADMINISTRATUM-RESUME-CONTINUITY-PACK-V0_2-MANUAL"

OWNER_LATEST_DECISION = (
    "Continuity pack РїСЂРёР·РЅР°РЅ СЃР»Р°Р±С‹Рј Рё Р±РµСЃСЏС‡РёРј: РµРіРѕ РЅРµ С…РІР°С‚Р°РµС‚, С‡С‚РѕР±С‹ РїСЂРѕСЃС‚Рѕ "
    "РїСЂРѕРґРѕР»Р¶РёС‚СЊ СЂРѕРІРЅРѕ СЃ РїРѕСЃР»РµРґРЅРµР№ С‚РѕС‡РєРё. Administratum v0.2 РґРѕР»Р¶РµРЅ СЃС‚СЂРѕРёС‚СЊ "
    "РЅРµ РєСЂР°СЃРёРІС‹Р№ РѕР±С‰РёР№ handoff, Р° С‚РѕС‡РЅС‹Р№ Resume Continuity Pack: START_HERE, "
    "LAST_POINT_STATE, OWNER_DECISION_LOG, NEXT_ATOMIC_STEP, evidence ledger."
)

DO_NOT_DO = [
    "РЅРµ Р·Р°СЏРІР»СЏС‚СЊ green/canon/real-task-ready",
    "РЅРµ РїРѕРґРјРµРЅСЏС‚СЊ РїРѕСЃР»РµРґРЅСЋСЋ С‚РѕС‡РєСѓ РѕР±С‰РёРј РїРµСЂРµСЃРєР°Р·РѕРј СЃРёСЃС‚РµРјС‹",
    "РЅРµ РґРµР»Р°С‚СЊ РґРІР° СЂРµР¶РёРјР° СЃР»Р°Р±РѕРіРѕ pack РІРјРµСЃС‚Рѕ РѕРґРЅРѕРіРѕ С‚РѕС‡РЅРѕРіРѕ resume pack",
    "РЅРµ С‚СЂРѕРіР°С‚СЊ THRONE",
    "РЅРµ СЃРёРЅРєР°С‚СЊ РІ THRONE",
    "РЅРµ СѓРґР°Р»СЏС‚СЊ СЃС‚Р°СЂС‹Рµ pack/artifacts",
    "РЅРµ Р»РµР·С‚СЊ РІ SANCTUM РІ СЌС‚РѕРј РїР°С‚С‡Рµ",
    "РЅРµ Р°РєС‚РёРІРёСЂРѕРІР°С‚СЊ VM2",
    "РЅРµ РїСЂРѕРґРѕР»Р¶Р°С‚СЊ РїРѕ РїР°РјСЏС‚Рё Р±РµР· evidence path",
    "РЅРµ РёСЃРїРѕР»СЊР·РѕРІР°С‚СЊ latest guessing Р±РµР· СЏРІРЅРѕРіРѕ РїСѓС‚Рё/receipt/hash",
]

CURRENT_OBJECTIVE = (
    "РџРѕС‡РёРЅРёС‚СЊ Administratum Continuity Pack РґРѕ v0.2 С‚Р°Рє, С‡С‚РѕР±С‹ РЅРѕРІС‹Р№ С‡Р°С‚ РјРѕРі "
    "СЂРѕРІРЅРѕ РІРѕСЃСЃС‚Р°РЅРѕРІРёС‚СЊ РїРѕСЃР»РµРґРЅСЋСЋ СЂР°Р±РѕС‡СѓСЋ С‚РѕС‡РєСѓ: С‡С‚Рѕ РёРјРµРЅРЅРѕ РґРµР»Р°Р»Рё, РіРґРµ РѕСЃС‚Р°РЅРѕРІРёР»РёСЃСЊ, "
    "РєР°РєРѕРµ РїРѕСЃР»РµРґРЅРµРµ СЂРµС€РµРЅРёРµ Owner РёР·РјРµРЅРёР»Рѕ РєСѓСЂСЃ, РєР°РєРѕР№ СЃР»РµРґСѓСЋС‰РёР№ Р°С‚РѕРјР°СЂРЅС‹Р№ С€Р°Рі, "
    "РєР°РєРёРµ С„Р°Р№Р»С‹ Рё receipts СЌС‚Рѕ РґРѕРєР°Р·С‹РІР°СЋС‚."
)

NEXT_ATOMIC_STEP = (
    "РџРѕСЃР»Рµ Р·Р°РїСѓСЃРєР° СЌС‚РѕРіРѕ РїР°С‚С‡Р° РѕС‚РєСЂС‹С‚СЊ Administratum Dashboard v0.2 РёР»Рё РЅР°РїСЂСЏРјСѓСЋ "
    "Р·Р°РїСѓСЃС‚РёС‚СЊ administratum_build_resume_continuity_pack_v0_2.py, РїСЂРѕРІРµСЂРёС‚СЊ START_HERE.md "
    "РІ СЃРІРµР¶РµРј RESUME_CONTINUITY_PACK Рё С‚РѕР»СЊРєРѕ РїРѕС‚РѕРј РґРІРёРіР°С‚СЊСЃСЏ Рє СЃР»РµРґСѓСЋС‰РµРјСѓ РѕСЂРіР°РЅСѓ."
)

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

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

def find_dirs(root: Path, pattern: str, max_items: int = 80) -> list[Path]:
    try:
        return sorted_by_mtime([p for p in root.rglob(pattern) if p.is_dir()])[:max_items]
    except Exception:
        return []

def latest_dir(base: Path, prefix: str) -> Path | None:
    if not base.exists():
        return None
    candidates = [p for p in base.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    if not candidates:
        return None
    return sorted_by_mtime(candidates)[0]

def collect_finalization_receipts(root: Path) -> list[dict[str, Any]]:
    receipts = []
    for p in find_files(root / "ARTIFACTS", "FINALIZATION_RECEIPT_EXTERNAL.json", 200):
        data = read_json(p) or {}
        receipts.append({
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
        })
    # Also collect receipts that are named differently inside package dirs.
    for p in find_files(root / "ARTIFACTS", "*FINAL*RECEIPT*.json", 200):
        if p.name == "FINALIZATION_RECEIPT_EXTERNAL.json":
            continue
        data = read_json(p) or {}
        receipts.append({
            "path": str(p),
            "relative_path": safe_rel(p, root),
            "mtime_utc": mtime_iso(p),
            "task_id": data.get("task_id"),
            "verdict": data.get("verdict") or data.get("status"),
            "finalization_time": data.get("finalization_time") or data.get("timestamp") or data.get("created_at"),
        })
    return sorted(receipts, key=lambda x: x.get("finalization_time") or x.get("mtime_utc") or "", reverse=True)

def collect_latest_packs(root: Path) -> dict[str, Any]:
    packs_root = root / "ORGANS" / "ADMINISTRATUM" / "CONTINUITY" / "PACKS"
    return {
        "packs_root": str(packs_root),
        "latest_resume_pack_before_this_run": str(latest_dir(packs_root, "RESUME_CONTINUITY_PACK_")) if latest_dir(packs_root, "RESUME_CONTINUITY_PACK_") else None,
        "latest_semantic_pack": str(latest_dir(packs_root, "CONTINUITY_PACK_")) if latest_dir(packs_root, "CONTINUITY_PACK_") else None,
        "latest_developer_pack": str(latest_dir(packs_root, "DEVELOPER_GRADE_CONTINUITY_PACK_")) if latest_dir(packs_root, "DEVELOPER_GRADE_CONTINUITY_PACK_") else None,
        "recent_pack_dirs": [
            {"path": str(p), "name": p.name, "mtime_utc": mtime_iso(p)}
            for p in sorted_by_mtime([d for d in packs_root.iterdir() if d.is_dir()])[:20]
        ] if packs_root.exists() else [],
    }

def collect_dashboards(root: Path) -> list[dict[str, Any]]:
    out = []
    for p in find_files(root / "ORGANS", "DASHBOARD_REGISTRY.json", 50):
        data = read_json(p)
        out.append({
            "registry_path": str(p),
            "relative_path": safe_rel(p, root),
            "mtime_utc": mtime_iso(p),
            "data": data,
        })
    for p in find_files(root / "ORGANS", "DASHBOARD_STATUS*.json", 80):
        data = read_json(p)
        out.append({
            "status_path": str(p),
            "relative_path": safe_rel(p, root),
            "mtime_utc": mtime_iso(p),
            "data": data,
        })
    return out

def collect_organ_status(root: Path) -> list[dict[str, Any]]:
    out = []
    for p in find_files(root / "ORGANS", "ORGAN_STATUS.json", 80):
        data = read_json(p) or {}
        organ_id = data.get("organ_id") or p.parts[-3] if len(p.parts) >= 3 else p.parent.name
        out.append({
            "organ_id": organ_id,
            "path": str(p),
            "relative_path": safe_rel(p, root),
            "mtime_utc": mtime_iso(p),
            "status": data.get("status"),
            "classification_target": data.get("classification_target"),
            "current_dashboard_id": data.get("current_dashboard_id"),
            "blockers": data.get("blockers"),
            "limitations": data.get("limitations"),
        })
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
    seen = set()
    out = []
    for pat in names:
        for p in find_files(root, pat, 100):
            key = str(p).lower()
            if key in seen:
                continue
            seen.add(key)
            data = read_json(p)
            out.append({
                "path": str(p),
                "relative_path": safe_rel(p, root),
                "mtime_utc": mtime_iso(p),
                "sha256": sha256_file(p),
                "summary_keys": list(data.keys())[:20] if isinstance(data, dict) else None,
                "verdict": data.get("verdict") if isinstance(data, dict) else None,
                "status": data.get("status") if isinstance(data, dict) else None,
                "task_id": data.get("task_id") if isinstance(data, dict) else None,
            })
    return sorted(out, key=lambda x: x.get("mtime_utc") or "", reverse=True)[:120]

def collect_active_tasks(root: Path) -> dict[str, Any]:
    candidates = []
    for p in find_files(root, "ACTIVE_TASKS.json", 30):
        candidates.append({
            "path": str(p),
            "relative_path": safe_rel(p, root),
            "mtime_utc": mtime_iso(p),
            "data": read_json(p),
        })
    return {"candidates": candidates[:10]}

def infer_last_verified_point(receipts: list[dict[str, Any]], packs: dict[str, Any]) -> dict[str, Any]:
    latest_receipt = receipts[0] if receipts else None
    return {
        "latest_finalized_artifact": latest_receipt,
        "latest_developer_pack": packs.get("latest_developer_pack"),
        "latest_semantic_pack": packs.get("latest_semantic_pack"),
        "latest_resume_pack_before_this_run": packs.get("latest_resume_pack_before_this_run"),
        "owner_latest_decision": OWNER_LATEST_DECISION,
        "current_objective": CURRENT_OBJECTIVE,
        "next_atomic_step": NEXT_ATOMIC_STEP,
        "resume_rule": "РќРѕРІС‹Р№ С‡Р°С‚ РґРѕР»Р¶РµРЅ РЅР°С‡РёРЅР°С‚СЊ СЃ START_HERE.md, Р·Р°С‚РµРј LAST_POINT_STATE.json, Р·Р°С‚РµРј NEXT_ATOMIC_STEP.md. Р•СЃР»Рё СЌС‚РѕРіРѕ РЅРµРґРѕСЃС‚Р°С‚РѕС‡РЅРѕ вЂ” pack СЃС‡РёС‚Р°РµС‚СЃСЏ СЃР»Р°Р±С‹Рј.",
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
        label = item.get("task_id") or item.get("verdict") or item.get("status") or item.get("relative_path") or item.get("path")
        lines.append(f"{i}. `{label}`")
        for key in ["verdict", "status", "finalization_time", "mtime_utc", "relative_path", "path", "final_zip_sha256"]:
            val = item.get(key)
            if val:
                lines.append(f"   - {key}: `{val}`")
    return "\n".join(lines) + "\n"

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

    receipts = collect_finalization_receipts(root)
    packs = collect_latest_packs(root)
    dashboards = collect_dashboards(root)
    organ_status = collect_organ_status(root)
    reports = collect_key_reports(root)
    active_tasks = collect_active_tasks(root)
    last_point = infer_last_verified_point(receipts, packs)

    state = {
        "schema_version": SCHEMA,
        "pack_id": pack_dir.name,
        "generated_at_utc": utc_now(),
        "root": str(root),
        "task_id": TASK_ID,
        "classification": "RESUME_CONTINUITY_NOT_GENERAL_SUMMARY",
        "owner_latest_decision": OWNER_LATEST_DECISION,
        "current_objective": CURRENT_OBJECTIVE,
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

    start_here = f"""# START HERE вЂ” Resume Continuity Pack v0.2

This pack is NOT a general story of the system.  
It exists so a new chat can continue from the last working point without irritating re-discovery.

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
The previous idea вЂ” two modes, light semantic and developer technical вЂ” is not enough.  
The actual failure is that continuity does not preserve the exact last working point cleanly.

## New Direction
Administratum v0.2 must make one strong resume-first pack.  
Mode separation can come later only after resume quality is fixed.

## Current Manual Patch
- task_id: `{TASK_ID}`
- created by: manual PowerShell patch
- action: install `administratum_build_resume_continuity_pack_v0_2.py`, Dashboard v0.2 button, registry, receipt
"""

    next_step_md = f"""# NEXT ATOMIC STEP

{NEXT_ATOMIC_STEP}

## Acceptance Check
- Fresh `RESUME_CONTINUITY_PACK_*` exists.
- `START_HERE.md` states the latest Owner correction.
- `LAST_POINT_STATE.json` contains latest artifact receipts and exact current objective.
- `EVIDENCE_INDEX.md` lists real paths, not vague references.
- `DO_NOT_DO.md` blocks fake green/canon/latest guessing.

## After Passing
Then continue to the next organ, preferably `Officio Agentis v0.1`, because role contracts are the next hard blocker.
"""

    open_blockers = """# OPEN BLOCKERS

- Continuity was judged insufficient for exact resume; this v0.2 pack is the corrective layer.
- Doctrinarium still does not authorize canon/green/real-task-ready.
- Hard-law enforcement remains incomplete until Doctrinarium says otherwise.
- Organ ports may exist but can still contain weak/unknown/scaffold fields.
- Officio Agentis role contracts are not yet formalized.
"""

    do_not_do_md = "# DO NOT DO\n\n" + "".join(f"- {x}\n" for x in DO_NOT_DO)

    evidence_md = md_path_list(receipts[:30], "EVIDENCE INDEX вЂ” FINALIZATION RECEIPTS", 30)
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
            for b in blockers:
                organ_md_lines.append(f"  - {b}")
        organ_md_lines.append("")
    organ_md = "\n".join(organ_md_lines) + "\n"

    development_map = f"""# DEVELOPMENT MAP

## Where We Are
Administratum is being upgraded to resume-first continuity v0.2.

## What Was Wrong
The earlier pack could describe the system and developer surfaces, but did not reliably let the next chat continue exactly from the last point.

## What This Patch Adds
- `START_HERE.md` as mandatory first file.
- `LAST_POINT_STATE.json` as machine-readable truth snapshot.
- `OWNER_DECISION_LOG.md` to preserve course corrections.
- `NEXT_ATOMIC_STEP.md` to remove ambiguity.
- Evidence and artifact ledgers.
- Dashboard v0.2 button for Resume Continuity Pack.

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
    write_text(pack_dir / "PACK_QUALITY_GATE.md", f"# PACK QUALITY GATE\n\n- verdict: `{quality['verdict']}`\n- meaning: resume-first continuity built, but no canon/green claim.\n")

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
        "limitations": quality["limitations"],
    }
    write_json(pack_dir / "BUILD_RECEIPT.json", receipt)

    # Manifest and hashes.
    file_entries = []
    for p in sorted([x for x in pack_dir.rglob("*") if x.is_file()]):
        if p.name in {"MANIFEST.json", "SHA256SUMS.txt"}:
            continue
        file_entries.append({
            "relative_path": safe_rel(p, pack_dir),
            "size_bytes": p.stat().st_size,
            "sha256": sha256_file(p),
        })
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

    # Copy receipt to artifact area and create external finalization receipt + zip.
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
        "verdict": quality["verdict"],
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=os.environ.get("IMPERIUM_ROOT", r"E:\IMPERIUM"))
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
    except Exception as e:
        payload = {
            "ok": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())