#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

SKIP = {"archive", "_archive", "00_archive", "old", "deprecated", "node_modules", "__pycache__"}
REQ_PORT_FILES = [
    "CONTINUITY_PORT.json",
    "CONTINUITY_SELF_REPORT.json",
    "LATEST_REPORTS_INDEX.json",
    "LATEST_RECEIPTS_INDEX.json",
    "DASHBOARD_PORT.json",
    "BLOCKERS_PORT.json",
]
REQ_PACK_FILES = [
    "CONTINUITY_PACK.json",
    "CONTINUITY_PACK.md",
    "CURRENT_STATE_SUMMARY.md",
    "ENTRYPOINT_FOR_NEW_CHAT.md",
    "IMPERIUM_ENTRYPOINT_FOR_NEW_CHAT.md",
    "LOGOS_HANDOFF_CORE.md",
    "SYSTEM_CHRONOLOGY.md",
    "ACTIVE_TASKS.json",
    "ACTIVE_TASKS.md",
    "NEXT_ACTIONS.md",
    "DO_NOT_DO.md",
    "BLOCKERS.md",
    "ORGAN_SNAPSHOT.json",
    "ORGAN_SNAPSHOT.md",
    "DASHBOARD_SNAPSHOT.json",
    "LAW_AND_DOCTRINE_SNAPSHOT.json",
    "ADDRESS_MAP.json",
    "ADDRESS_MAP.md",
    "ARTIFACT_INDEX.json",
    "RECENT_ARTIFACTS.md",
    "LATEST_RECEIPTS_INDEX.json",
    "CONTINUITY_DIFF_FROM_PREVIOUS.json",
    "CONTINUITY_DIFF_FROM_PREVIOUS.md",
    "PORTS_SNAPSHOT.json",
    "PORTS_SNAPSHOT.md",
    "PORT_MISSING_REPORT.json",
    "PORT_MISSING_REPORT.md",
    "PORT_STALENESS_REPORT.json",
    "PORT_STALENESS_REPORT.md",
    "HANDOFF_SUFFICIENCY_REPORT.json",
    "HANDOFF_SUFFICIENCY_REPORT.md",
    "MANIFEST.json",
    "SHA256SUMS.txt",
    "BUILD_RECEIPT.json",
]


def now_iso():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def ts_id():
    return dt.datetime.now().strftime("%Y%m%d_%H%M%S")


def read_json(path: Path, default=None):
    if not path.exists():
        return {} if default is None else default
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {} if default is None else default


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sha256_file(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_iso(s):
    if not isinstance(s, str) or not s.strip():
        return None
    t = s.strip()
    if t.endswith("Z"):
        t = t[:-1] + "+00:00"
    try:
        d = dt.datetime.fromisoformat(t)
        if d.tzinfo is None:
            d = d.replace(tzinfo=dt.timezone.utc)
        return d
    except Exception:
        return None


def is_skip_dir(p: Path):
    return p.name.lower() in SKIP


def list_packs(packs_root: Path):
    return sorted([x for x in packs_root.glob("CONTINUITY_PACK_*") if x.is_dir()], key=lambda p: p.name)


def find_latest_file(root: Path, pattern: str):
    if not root.exists():
        return None
    files = sorted([x for x in root.glob(pattern) if x.is_file()], key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def collect_dashboards(root: Path):
    out = []
    organs = root / "ORGANS"
    if not organs.exists():
        return {"schema_version": "ADMINISTRATUM_DASHBOARD_SNAPSHOT_V0_1", "generated_at": now_iso(), "dashboards": []}
    for organ in sorted([x for x in organs.iterdir() if x.is_dir()], key=lambda p: p.name.lower()):
        if is_skip_dir(organ) or organ.name.upper() == "SANCTUM":
            continue
        utility = organ / "UTILITY"
        reg_path = utility / "DASHBOARD_REGISTRY.json"
        if reg_path.exists():
            reg = read_json(reg_path, {})
            out.append(
                {
                    "organ_id": organ.name.upper(),
                    "dashboard_id": reg.get("current_dashboard_id") or reg.get("dashboard_id"),
                    "version": reg.get("version") or reg.get("dashboard_version"),
                    "status": reg.get("status"),
                    "url": reg.get("url") or reg.get("dashboard_url"),
                    "launcher_path": reg.get("launcher_path"),
                    "registry_path": str(reg_path),
                }
            )
            continue
        if utility.exists():
            web_dirs = sorted([x for x in utility.glob("WEB_DASHBOARD_*") if x.is_dir()], key=lambda p: p.name)
            if web_dirs:
                out.append(
                    {
                        "organ_id": organ.name.upper(),
                        "dashboard_id": web_dirs[-1].name,
                        "version": None,
                        "status": "DASHBOARD_DIR_ONLY",
                        "url": None,
                        "launcher_path": None,
                        "registry_path": None,
                    }
                )
    return {
        "schema_version": "ADMINISTRATUM_DASHBOARD_SNAPSHOT_V0_1",
        "generated_at": now_iso(),
        "dashboards": out,
        "summary": {"total_dashboards": len(out)},
    }


def collect_artifacts(root: Path, limit=30):
    items = []
    art_root = root / "ARTIFACTS"
    if art_root.exists():
        dirs = sorted([x for x in art_root.iterdir() if x.is_dir() and not is_skip_dir(x)], key=lambda p: p.stat().st_mtime, reverse=True)
        for d in dirs[:limit]:
            fin = None
            for p in [
                d / "PACKAGE" / "FINALIZATION_RECEIPT_EXTERNAL.json",
                d / "13_PACKAGE" / "FINALIZATION_RECEIPT_EXTERNAL.json",
                d / "15_PACKAGE" / "FINALIZATION_RECEIPT_EXTERNAL.json",
                d / "12_PACKAGE" / "FINALIZATION_RECEIPT_EXTERNAL.json",
            ]:
                if p.exists():
                    fin = p
                    break
            items.append(
                {
                    "artifact_dir": str(d),
                    "last_modified": dt.datetime.fromtimestamp(d.stat().st_mtime, dt.timezone.utc).isoformat(),
                    "finalization_receipt_path": str(fin) if fin else None,
                }
            )
    return {"schema_version": "ADMINISTRATUM_ARTIFACT_INDEX_V0_1", "generated_at": now_iso(), "items": items}


def active_tasks(artifact_index):
    tasks = []
    for item in artifact_index.get("items", []):
        d = Path(item.get("artifact_dir", ""))
        if d.name.startswith("TASK-"):
            recipe = d / "00_INPUTS" / "TASK_RECIPE.json"
            rj = read_json(recipe, {}) if recipe.exists() else {}
            tasks.append(
                {
                    "task_id": rj.get("task_id") or d.name,
                    "task_name": rj.get("task_name"),
                    "artifact_path": str(d),
                    "has_finalization": bool(item.get("finalization_receipt_path")),
                    "finalization_receipt_path": item.get("finalization_receipt_path"),
                }
            )
    return {"schema_version": "ADMINISTRATUM_ACTIVE_TASKS_V0_1", "generated_at": now_iso(), "tasks": tasks}


def fallback_port(organ_dir: Path, reason: str):
    status = read_json(organ_dir / "ORGAN_STATUS.json", {})
    contract = read_json(organ_dir / "ORGAN_CONTRACT.json", {})
    latest_report = find_latest_file(organ_dir / "REPORTS", "*.json") or find_latest_file(organ_dir / "REPORTS", "*.md")
    latest_receipt = find_latest_file(organ_dir / "RECEIPTS", "*.json")
    return {
        "schema_version": "CONTINUITY_PORT_FALLBACK_V0_1",
        "organ_id": organ_dir.name.upper(),
        "port_status": "PORT_MISSING_FALLBACK_USED",
        "status": status.get("status") or contract.get("status") or "UNKNOWN",
        "owner_approval_state": status.get("owner_approval_state", "UNKNOWN"),
        "source_paths": [str(organ_dir)],
        "latest_known_reports": [str(latest_report)] if latest_report else [],
        "latest_known_receipts": [str(latest_receipt)] if latest_receipt else [],
        "dashboard_refs": [str(organ_dir / "UTILITY")] if (organ_dir / "UTILITY").exists() else [],
        "blockers": status.get("blockers") or status.get("current_blockers") or [],
        "limitations": ["Fallback scan used because continuity port is missing."],
        "next_actions": ["Create or refresh PORTS files for this organ."],
        "do_not_claim": ["organ readiness", "canon readiness", "continuity green"],
        "evidence_level": "FALLBACK_SCAN",
        "stale_if_older_than_hours": 24,
        "last_verified_at": now_iso(),
        "fallback_reason": reason,
    }


def parse_port(organ_id: str, port_dir: Path):
    cp = read_json(port_dir / "CONTINUITY_PORT.json", {})
    reports = read_json(port_dir / "LATEST_REPORTS_INDEX.json", {})
    receipts = read_json(port_dir / "LATEST_RECEIPTS_INDEX.json", {})
    dash = read_json(port_dir / "DASHBOARD_PORT.json", {})
    blk = read_json(port_dir / "BLOCKERS_PORT.json", {})
    missing = [name for name in REQ_PORT_FILES if not (port_dir / name).exists()]
    stale_hours = cp.get("stale_if_older_than_hours", 72)
    try:
        stale_hours = int(stale_hours)
    except Exception:
        stale_hours = 72
    t = parse_iso(cp.get("last_verified_at") or cp.get("generated_at"))
    age_h = None
    stale = False
    if t:
        age_h = (dt.datetime.now(dt.timezone.utc) - t).total_seconds() / 3600.0
        stale = age_h > stale_hours
    raw_do_not_claim = cp.get("do_not_claim") or blk.get("do_not_claim") or []
    safe_do_not_claim = []
    for item in raw_do_not_claim:
        if isinstance(item, str):
            text = item.strip().lower().replace("_", " ")
            if text:
                safe_do_not_claim.append(text)
    if not safe_do_not_claim:
        safe_do_not_claim = ["no fake green", "no canon claim", "no full readiness claim"]
    data = {
        "schema_version": cp.get("schema_version", "CONTINUITY_PORT_BUNDLE_V0_1"),
        "organ_id": organ_id,
        "port_status": "PORT_READY" if not missing else "PORT_PARTIAL",
        "status": cp.get("status", "UNKNOWN"),
        "owner_approval_state": cp.get("owner_approval_state", "UNKNOWN"),
        "source_paths": cp.get("source_paths") or [str(port_dir.parent)],
        "latest_known_reports": cp.get("latest_known_reports") or reports.get("latest_known_reports") or [],
        "latest_known_receipts": cp.get("latest_known_receipts") or receipts.get("latest_known_receipts") or [],
        "dashboard_refs": cp.get("dashboard_refs") or dash.get("dashboard_refs") or [],
        "blockers": cp.get("blockers") or blk.get("blockers") or [],
        "limitations": cp.get("limitations") or blk.get("limitations") or [],
        "next_actions": cp.get("next_actions") or blk.get("next_actions") or [],
        "do_not_claim": safe_do_not_claim,
        "evidence_level": cp.get("evidence_level", "PORT_DECLARED"),
        "stale_if_older_than_hours": stale_hours,
        "last_verified_at": cp.get("last_verified_at") or cp.get("generated_at"),
        "port_dir": str(port_dir),
        "missing_port_files": missing,
        "is_stale": stale,
        "age_hours": age_h,
    }
    stale_rec = None
    if stale:
        stale_rec = {
            "organ_id": organ_id,
            "port_dir": str(port_dir),
            "age_hours": age_h,
            "stale_if_older_than_hours": stale_hours,
            "last_verified_at": data.get("last_verified_at"),
            "reason": "PORT_STALE",
        }
    return data, missing, stale_rec


def collect_ports(root: Path, reg_path: Path):
    reg = read_json(reg_path, {})
    reg_map = {}
    for p in reg.get("ports", []) if isinstance(reg, dict) else []:
        oid = str(p.get("organ_id", "")).upper().strip()
        if oid:
            reg_map[oid] = p
    snapshot, missing, stale, warnings = [], [], [], []
    organs = root / "ORGANS"
    if not organs.exists():
        return {"registry": reg, "snapshot": [], "missing": [{"organ_id": "ALL", "reason": "ORGANS_ROOT_MISSING"}], "stale": [], "warnings": []}
    for organ in sorted(
        [x for x in organs.iterdir() if x.is_dir() and not is_skip_dir(x) and x.name.upper() != "SANCTUM" and not x.name.startswith("_")],
        key=lambda p: p.name.upper(),
    ):
        oid = organ.name.upper()
        reg_item = reg_map.get(oid)
        port_dir = Path(reg_item["ports_path"]) if reg_item and reg_item.get("ports_path") else (organ / "PORTS")
        if (port_dir / "CONTINUITY_PORT.json").exists():
            rec, miss, st = parse_port(oid, port_dir)
            snapshot.append(rec)
            if miss:
                missing.append({"organ_id": oid, "reason": "PORT_FILES_MISSING", "missing_files": miss, "path": str(port_dir)})
            if st:
                stale.append(st)
        else:
            reason = "PORT_NOT_REGISTERED" if reg_item is None else "PORT_REGISTERED_BUT_CONTINUITY_PORT_MISSING"
            rec = fallback_port(organ, reason)
            snapshot.append(rec)
            missing.append({"organ_id": oid, "reason": reason, "path": str(port_dir)})
            warnings.append(f"PORT_MISSING_FALLBACK_USED for {oid}")
    return {"registry": reg, "snapshot": snapshot, "missing": missing, "stale": stale, "warnings": sorted(set(warnings))}


def law_and_doctrine(root: Path):
    doc = root / "ORGANS" / "DOCTRINARIUM"
    status = read_json(doc / "STATUS" / "DOCTRINARIUM_STATUS.json", {})
    doctrine_index = read_json(doc / "DOCTRINE" / "DOCTRINE_INDEX.json", {})
    laws = read_json(doc / "LAWS" / "MANDATORY_LAWS.json", {})
    gaps = read_json(doc / "REPORTS" / "ALL_ORGANS_GAP_REPORT.json", {})
    util_gaps = read_json(doc / "REPORTS" / "ORGAN_UTILITY_GAP_REPORT.json", {})
    return {
        "schema_version": "LAW_AND_DOCTRINE_SNAPSHOT_V0_1",
        "generated_at": now_iso(),
        "status": status,
        "doctrine_index": doctrine_index,
        "law_registry_summary": {
            "total_laws": len(laws.get("laws", [])) if isinstance(laws, dict) else 0,
            "not_fully_enforced": [x.get("law_id") for x in (laws.get("laws", []) if isinstance(laws, dict) else []) if x.get("enforcement_status") != "LAW_ENFORCED"],
        },
        "gap_summary": {
            "total_organs_checked": gaps.get("total_organs_checked"),
            "total_blockers_found": gaps.get("total_blockers_found"),
            "utility_blocking_failures": util_gaps.get("summary", {}).get("blocking_utility_failures") if isinstance(util_gaps, dict) else None,
        },
    }


def chronology(root: Path):
    pts = [
        (
            "Doctrinarium dashboard v0.8 handoff finalized",
            root / "ARTIFACTS" / "MANUAL-DOCTRINARIUM-DASHBOARD-V0_8-TECHNICAL-HANDOFF" / "PACKAGE" / "FINALIZATION_RECEIPT_EXTERNAL.json",
        ),
        (
            "Doctrinarium dashboard v0.8 Playwright audit",
            root / "ARTIFACTS" / "MANUAL-DOCTRINARIUM-DASHBOARD-V0_8-TECHNICAL-HANDOFF" / "PLAYWRIGHT_AUDIT" / "PLAYWRIGHT_AUDIT_V0_8_REPORT.json",
        ),
        (
            "Administratum dashboard and continuity task finalized",
            root / "ARTIFACTS" / "TASK-20260509-ADMINISTRATUM-ORGAN-DASHBOARD-AND-CONTINUITY-PACK-V0_1" / "13_PACKAGE" / "FINALIZATION_RECEIPT_EXTERNAL.json",
        ),
        (
            "Continuity QA/ports/rebuild task started",
            root / "ARTIFACTS" / "TASK-20260510-ADMINISTRATUM-CONTINUITY-PACK-QA-PORTS-AND-REBUILD-V0_1" / "00_INPUTS" / "TASK_RECIPE.json",
        ),
    ]
    out = []
    for label, p in pts:
        t = None
        if p.exists():
            j = read_json(p, {})
            t = j.get("created_at") or j.get("finalization_time") or j.get("generated_at")
            if not t:
                t = dt.datetime.fromtimestamp(p.stat().st_mtime, dt.timezone.utc).isoformat()
        out.append({"step": label, "timestamp": t, "evidence_path": str(p), "exists": p.exists()})
    return out


def resolve_old_pack(root: Path, arg_old):
    if arg_old:
        p = Path(arg_old)
        if p.exists():
            return p
    freeze = root / "ARTIFACTS" / "TASK-20260510-ADMINISTRATUM-CONTINUITY-PACK-QA-PORTS-AND-REBUILD-V0_1" / "00_INPUTS" / "INPUT_FREEZE.json"
    f = read_json(freeze, {})
    sel = f.get("selected_old_pack_path") if isinstance(f, dict) else None
    if sel:
        p = Path(sel)
        if p.exists():
            return p
    direct = root / "ORGANS" / "ADMINISTRATUM" / "CONTINUITY" / "PACKS" / "CONTINUITY_PACK_20260510_082210"
    return direct if direct.exists() else None


def entry_text(point, next_step):
    return (
        "This is the latest IMPERIUM continuity state.\n"
        "Owner will provide role separately.\n"
        "Use evidence paths, not chat memory.\n"
        f"Current verified point is: {point}\n"
        f"Latest completed work is: {point}\n"
        f"Next recommended step is: {next_step}\n"
        "Do not claim green or canon.\n"
        "If uncertain, ask for the latest continuity pack or run Administratum continuity build.\n"
    )


def handoff_checks(pack, pack_dir: Path, old_pack, ports_data):
    checks = []

    def add(name, ok, detail):
        checks.append({"check": name, "ok": bool(ok), "detail": detail})

    add(
        "includes_doctrinarium_v0_8_playwright_pass",
        pack.get("latest_verified_dashboard", {}).get("doctrinarium_playwright_verdict") == "PASS_PLAYWRIGHT_V0_8_VISUAL_FUNCTIONAL_AUDIT",
        str(pack.get("latest_verified_dashboard", {}).get("doctrinarium_playwright_verdict")),
    )
    fin = Path(pack.get("evidence_paths", {}).get("administratum_v0_1_finalization", ""))
    add("includes_administratum_v0_1_finalization", fin.exists(), str(fin))
    add("includes_ports_registry", bool(pack.get("ports_registry_path")), str(pack.get("ports_registry_path")))
    add("includes_next_action", bool(pack.get("next_actions")), str(pack.get("next_actions")))
    add("includes_do_not_do", bool(pack.get("do_not_do")), str(pack.get("do_not_do")))
    add("includes_role_neutral_entrypoint", (pack_dir / "IMPERIUM_ENTRYPOINT_FOR_NEW_CHAT.md").exists(), str(pack_dir / "IMPERIUM_ENTRYPOINT_FOR_NEW_CHAT.md"))
    add("references_old_pack", bool(old_pack and old_pack.exists()), str(old_pack) if old_pack else "none")
    checkable_required = {
        "CONTINUITY_PACK.json",
        "CONTINUITY_PACK.md",
        "CURRENT_STATE_SUMMARY.md",
        "ENTRYPOINT_FOR_NEW_CHAT.md",
        "IMPERIUM_ENTRYPOINT_FOR_NEW_CHAT.md",
        "LOGOS_HANDOFF_CORE.md",
        "SYSTEM_CHRONOLOGY.md",
        "ACTIVE_TASKS.json",
        "ACTIVE_TASKS.md",
        "NEXT_ACTIONS.md",
        "DO_NOT_DO.md",
        "BLOCKERS.md",
        "ORGAN_SNAPSHOT.json",
        "ORGAN_SNAPSHOT.md",
        "DASHBOARD_SNAPSHOT.json",
        "LAW_AND_DOCTRINE_SNAPSHOT.json",
        "ADDRESS_MAP.json",
        "ADDRESS_MAP.md",
        "ARTIFACT_INDEX.json",
        "RECENT_ARTIFACTS.md",
        "LATEST_RECEIPTS_INDEX.json",
        "CONTINUITY_DIFF_FROM_PREVIOUS.json",
        "CONTINUITY_DIFF_FROM_PREVIOUS.md",
        "PORTS_SNAPSHOT.json",
        "PORTS_SNAPSHOT.md",
        "PORT_MISSING_REPORT.json",
        "PORT_MISSING_REPORT.md",
        "PORT_STALENESS_REPORT.json",
        "PORT_STALENESS_REPORT.md",
    }
    add("required_files_written", all((pack_dir / x).exists() for x in checkable_required), "required file set")

    critical = {"includes_doctrinarium_v0_8_playwright_pass", "includes_administratum_v0_1_finalization", "includes_ports_registry", "includes_next_action", "includes_do_not_do", "includes_role_neutral_entrypoint", "required_files_written"}
    failed = [x for x in checks if not x["ok"] and x["check"] in critical]
    if failed:
        verdict = "NEW_PACK_INSUFFICIENT_FOR_RELIABLE_HANDOFF"
    elif ports_data.get("missing") or ports_data.get("stale"):
        verdict = "NEW_PACK_PARTIALLY_SUFFICIENT_NEEDS_REPAIR"
    else:
        verdict = "NEW_PACK_SUFFICIENT_FOR_BOOTSTRAP_NEW_CHAT_HANDOFF_WITH_LIMITATIONS"
    return {
        "schema_version": "HANDOFF_SUFFICIENCY_REPORT_V0_1",
        "generated_at": now_iso(),
        "checks": checks,
        "critical_failures": failed,
        "ports_missing_count": len(ports_data.get("missing", [])),
        "ports_stale_count": len(ports_data.get("stale", [])),
        "verdict": verdict,
        "limitations": [
            "Bootstrap continuity context only.",
            "No canon or real-task readiness claim is permitted.",
        ],
    }


def write_manifest_hashes(pack_dir: Path):
    data_files = []
    for p in sorted(pack_dir.rglob("*")):
        if not p.is_file():
            continue
        if p.name == "SHA256SUMS.txt":
            continue
        if p.suffix.lower() in {".pyc", ".pyo"}:
            continue
        if "__pycache__" in p.parts:
            continue
        data_files.append(p)
    manifest = {
        "schema_version": "CONTINUITY_PACK_MANIFEST_V0_1",
        "generated_at": now_iso(),
        "pack_root": str(pack_dir),
        "files": [{"path": str(p), "relative_path": str(p.relative_to(pack_dir)), "size": p.stat().st_size} for p in data_files],
    }
    manifest_path = pack_dir / "MANIFEST.json"
    write_json(manifest_path, manifest)
    hash_targets = sorted([p for p in pack_dir.rglob("*") if p.is_file() and p.name != "SHA256SUMS.txt" and "__pycache__" not in p.parts and p.suffix.lower() not in {".pyc", ".pyo"}], key=lambda x: str(x).lower())
    lines = [f"{sha256_file(p)}  {p}" for p in hash_targets]
    sha_path = pack_dir / "SHA256SUMS.txt"
    write_text(sha_path, "\n".join(lines) + "\n")
    return manifest_path, sha_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=r"E:\IMPERIUM")
    ap.add_argument("--trigger", default="manual_cli")
    ap.add_argument("--run-id", default=f"RUN-{ts_id()}")
    ap.add_argument("--old-pack-path", default=None)
    args = ap.parse_args()

    root = Path(args.root)
    admin = root / "ORGANS" / "ADMINISTRATUM"
    packs_root = admin / "CONTINUITY" / "PACKS"
    packs_root.mkdir(parents=True, exist_ok=True)

    script_path = Path(__file__).resolve()
    script_sha = sha256_file(script_path)
    prev_pack = list_packs(packs_root)
    previous = prev_pack[-1] if prev_pack else None

    pack_id = f"CONTINUITY_PACK_{ts_id()}"
    pack_dir = packs_root / pack_id
    if pack_dir.exists():
        pack_id = pack_id + "_R"
        pack_dir = packs_root / pack_id
    pack_dir.mkdir(parents=True, exist_ok=False)

    ports_registry = admin / "ADDRESS_REGISTRY" / "CONTINUITY_PORTS.json"
    ports_data = collect_ports(root, ports_registry)
    dashboards = collect_dashboards(root)
    artifacts = collect_artifacts(root)
    tasks = active_tasks(artifacts)
    doctrine = law_and_doctrine(root)
    chrono = chronology(root)
    old_pack = resolve_old_pack(root, args.old_pack_path)
    old_pack_qa = read_json(root / "ARTIFACTS" / "TASK-20260510-ADMINISTRATUM-CONTINUITY-PACK-QA-PORTS-AND-REBUILD-V0_1" / "03_OLD_PACK_VS_REALITY_QA" / "OLD_PACK_VS_REALITY_QA.json", {})
    admin_status = read_json(admin / "ORGAN_STATUS.json", {})
    admin_self = read_json(admin / "SELF_REPORT.json", {})

    blockers = []
    for rec in ports_data.get("snapshot", []):
        for b in rec.get("blockers", []) or []:
            if isinstance(b, str) and b.strip():
                blockers.append(f"{rec.get('organ_id')}: {b}")
    for b in doctrine.get("status", {}).get("blockers", []) or []:
        if isinstance(b, str):
            blockers.append(f"DOCTRINARIUM: {b}")
    blockers = sorted(set(blockers))

    next_actions = [
        "Review new continuity comparison and close top missing or stale port items.",
        "Update weak organ ports from UNKNOWN to evidence-backed values.",
        "Run Doctrinarium validators after organ-side hardening.",
        "Keep continuity handoff in bootstrap limitations mode.",
    ]
    do_not_do = [
        "no fake green",
        "no canon claim",
        "no archive scan",
        "no sanctum changes",
        "no vm2 activation",
        "no throne contact",
        "no delete",
        "no latest guessing",
    ]
    current_point = "Ports-first continuity collection integrated and new continuity pack generated."
    evidence = {
        "doctrinarium_handoff_finalization": str(root / "ARTIFACTS" / "MANUAL-DOCTRINARIUM-DASHBOARD-V0_8-TECHNICAL-HANDOFF" / "PACKAGE" / "FINALIZATION_RECEIPT_EXTERNAL.json"),
        "doctrinarium_handoff_zip": str(root / "ARTIFACTS" / "MANUAL-DOCTRINARIUM-DASHBOARD-V0_8-TECHNICAL-HANDOFF" / "PACKAGE" / "MANUAL-DOCTRINARIUM-DASHBOARD-V0_8-TECHNICAL-HANDOFF.zip"),
        "doctrinarium_playwright_report": str(root / "ARTIFACTS" / "MANUAL-DOCTRINARIUM-DASHBOARD-V0_8-TECHNICAL-HANDOFF" / "PLAYWRIGHT_AUDIT" / "PLAYWRIGHT_AUDIT_V0_8_REPORT.json"),
        "administratum_v0_1_finalization": str(root / "ARTIFACTS" / "TASK-20260509-ADMINISTRATUM-ORGAN-DASHBOARD-AND-CONTINUITY-PACK-V0_1" / "13_PACKAGE" / "FINALIZATION_RECEIPT_EXTERNAL.json"),
        "ports_registry": str(ports_registry),
        "old_pack_reference": str(old_pack) if old_pack else None,
        "old_pack_qa": str(root / "ARTIFACTS" / "TASK-20260510-ADMINISTRATUM-CONTINUITY-PACK-QA-PORTS-AND-REBUILD-V0_1" / "03_OLD_PACK_VS_REALITY_QA" / "OLD_PACK_VS_REALITY_QA.json"),
    }
    pack = {
        "schema_version": "ADMINISTRATUM_CONTINUITY_PACK_PORTS_V0_1",
        "pack_id": pack_id,
        "generated_at": now_iso(),
        "trigger": args.trigger,
        "run_id": args.run_id,
        "source_root": str(root),
        "generator_script_path": str(script_path),
        "generator_script_sha256": script_sha,
        "previous_pack_path": str(previous) if previous else None,
        "old_pack_reference_path": str(old_pack) if old_pack else None,
        "ports_registry_path": str(ports_registry),
        "ports_first_rule": "CONTINUITY_PORTS_FIRST",
        "fallback_rule": "PORT_MISSING_FALLBACK_USED",
        "port_collection_summary": {
            "total_organs": len(ports_data.get("snapshot", [])),
            "missing_ports": len(ports_data.get("missing", [])),
            "stale_ports": len(ports_data.get("stale", [])),
            "fallback_warnings": ports_data.get("warnings", []),
        },
        "active_task": "TASK-20260510-ADMINISTRATUM-CONTINUITY-PACK-QA-PORTS-AND-REBUILD-V0_1",
        "current_completed_point": current_point,
        "latest_verified_dashboard": {
            "doctrinarium_dashboard_id": "DOCTRINARIUM_WEB_DASHBOARD_V0_8",
            "doctrinarium_playwright_verdict": read_json(root / "ARTIFACTS" / "MANUAL-DOCTRINARIUM-DASHBOARD-V0_8-TECHNICAL-HANDOFF" / "PLAYWRIGHT_AUDIT" / "PLAYWRIGHT_AUDIT_V0_8_REPORT.json", {}).get("verdict"),
            "administratum_dashboard_id": admin_status.get("current_dashboard_id"),
            "known_dashboards_count": len(dashboards.get("dashboards", [])),
        },
        "latest_doctrinarium_state": doctrine.get("status", {}),
        "latest_administratum_state": admin_status,
        "known_blockers_count": len(blockers),
        "known_blockers": blockers,
        "old_pack_qa_verdict": old_pack_qa.get("verdict"),
        "evidence_paths": evidence,
        "next_actions": next_actions,
        "do_not_do": do_not_do,
        "limitations": [
            "Continuity pack remains bootstrap evidence context only.",
            "Ports exist but several organs still expose weak or unknown fields.",
            "No canon or real-task readiness claim is allowed from this pack alone.",
        ],
    }

    write_json(pack_dir / "CONTINUITY_PACK.json", pack)
    write_text(pack_dir / "CONTINUITY_PACK.md", "\n".join(["# CONTINUITY PACK", "", f"- Pack ID: {pack_id}", f"- Previous pack: {pack['previous_pack_path']}", f"- Old pack reference: {pack['old_pack_reference_path']}", f"- Active task: {pack['active_task']}", f"- Current completed point: {current_point}", f"- Missing ports: {pack['port_collection_summary']['missing_ports']}", f"- Stale ports: {pack['port_collection_summary']['stale_ports']}", "", "## Next Actions"] + [f"- {x}" for x in next_actions] + ["", "## Limitations"] + [f"- {x}" for x in pack["limitations"]]) + "\n")
    write_text(pack_dir / "CURRENT_STATE_SUMMARY.md", "\n".join(["# CURRENT STATE SUMMARY", "", f"- Active task: {pack['active_task']}", f"- Completed point: {current_point}", f"- Old pack QA verdict: {old_pack_qa.get('verdict')}", f"- Ports missing: {len(ports_data.get('missing', []))}", f"- Ports stale: {len(ports_data.get('stale', []))}", "", "Use evidence paths in CONTINUITY_PACK.json for verification."]) + "\n")
    ent = entry_text(current_point, next_actions[0])
    write_text(pack_dir / "ENTRYPOINT_FOR_NEW_CHAT.md", ent)
    write_text(pack_dir / "IMPERIUM_ENTRYPOINT_FOR_NEW_CHAT.md", ent)
    write_text(pack_dir / "LOGOS_HANDOFF_CORE.md", "# LOGOS HANDOFF CORE\n\n- Owner will provide role separately.\n- Use continuity evidence paths rather than chat memory.\n- Validate blockers and next action before executing new tasks.\n- Keep bootstrap limitations visible.\n")
    write_text(pack_dir / "SYSTEM_CHRONOLOGY.md", "\n".join(["# SYSTEM CHRONOLOGY", ""] + [f"- {x['step']} | timestamp={x.get('timestamp')} | exists={x.get('exists')} | evidence={x['evidence_path']}" for x in chrono]) + "\n")

    write_json(pack_dir / "ACTIVE_TASKS.json", tasks)
    write_text(pack_dir / "ACTIVE_TASKS.md", "\n".join(["# ACTIVE TASKS", ""] + [f"- {x.get('task_id')} | finalized={x.get('has_finalization')} | artifact={x.get('artifact_path')}" for x in tasks.get("tasks", [])]) + "\n")
    write_text(pack_dir / "NEXT_ACTIONS.md", "# NEXT ACTIONS\n\n" + "\n".join([f"- {x}" for x in next_actions]) + "\n")
    write_text(pack_dir / "DO_NOT_DO.md", "# DO NOT DO\n\n" + "\n".join([f"- {x}" for x in do_not_do]) + "\n")
    write_text(pack_dir / "BLOCKERS.md", "# BLOCKERS\n\n" + ("\n".join([f"- {x}" for x in blockers]) if blockers else "- none") + "\n")

    organ_snap = {
        "schema_version": "ORGAN_SNAPSHOT_V0_1",
        "generated_at": now_iso(),
        "organs": ports_data.get("snapshot", []),
        "summary": {
            "total_organs": len(ports_data.get("snapshot", [])),
            "missing_ports": len(ports_data.get("missing", [])),
            "stale_ports": len(ports_data.get("stale", [])),
        },
    }
    write_json(pack_dir / "ORGAN_SNAPSHOT.json", organ_snap)
    write_text(pack_dir / "ORGAN_SNAPSHOT.md", "\n".join(["# ORGAN SNAPSHOT", "", f"- Total organs: {organ_snap['summary']['total_organs']}", f"- Missing ports: {organ_snap['summary']['missing_ports']}", f"- Stale ports: {organ_snap['summary']['stale_ports']}", "", "## Organs"] + [f"- {x.get('organ_id')}: status={x.get('status')} port_status={x.get('port_status')} evidence={x.get('evidence_level')}" for x in ports_data.get("snapshot", [])]) + "\n")
    write_json(pack_dir / "DASHBOARD_SNAPSHOT.json", dashboards)
    write_json(pack_dir / "LAW_AND_DOCTRINE_SNAPSHOT.json", doctrine)

    addr = {
        "schema_version": "ADDRESS_MAP_V0_1",
        "generated_at": now_iso(),
        "ports_registry_path": str(ports_registry),
        "ports": [
            {
                "organ_id": x.get("organ_id"),
                "port_dir": x.get("port_dir"),
                "source_paths": x.get("source_paths"),
                "latest_known_reports": x.get("latest_known_reports"),
                "latest_known_receipts": x.get("latest_known_receipts"),
            }
            for x in ports_data.get("snapshot", [])
        ],
    }
    write_json(pack_dir / "ADDRESS_MAP.json", addr)
    write_text(pack_dir / "ADDRESS_MAP.md", "\n".join(["# ADDRESS MAP", "", f"- Registry: {ports_registry}", "", "## Organs"] + [f"- {x.get('organ_id')}: port={x.get('port_dir')}" for x in addr["ports"]]) + "\n")
    write_json(pack_dir / "ARTIFACT_INDEX.json", artifacts)
    write_text(pack_dir / "RECENT_ARTIFACTS.md", "\n".join(["# RECENT ARTIFACTS", ""] + [f"- {x.get('artifact_dir')} | finalization={x.get('finalization_receipt_path')}" for x in artifacts.get("items", [])]) + "\n")

    latest_receipts = {"schema_version": "LATEST_RECEIPTS_INDEX_V0_1", "generated_at": now_iso(), "items": []}
    for x in ports_data.get("snapshot", []):
        for p in x.get("latest_known_receipts", []):
            latest_receipts["items"].append({"organ_id": x.get("organ_id"), "receipt_path": p, "exists": Path(p).exists()})
    for k in ["doctrinarium_handoff_finalization", "administratum_v0_1_finalization"]:
        p = evidence.get(k)
        if p:
            latest_receipts["items"].append({"organ_id": "SYSTEM", "receipt_path": p, "exists": Path(p).exists(), "label": k})
    write_json(pack_dir / "LATEST_RECEIPTS_INDEX.json", latest_receipts)

    prev_json = read_json(previous / "CONTINUITY_PACK.json", {}) if previous else {}
    diff_changes = []
    for k in ["active_task", "current_completed_point", "known_blockers_count", "ports_registry_path"]:
        o, n = prev_json.get(k), pack.get(k)
        if o != n:
            diff_changes.append({"field": k, "old": o, "new": n})
    diff_changes.append({"field": "ports_missing_count", "old": prev_json.get("port_collection_summary", {}).get("missing_ports") if isinstance(prev_json, dict) else None, "new": pack.get("port_collection_summary", {}).get("missing_ports")})
    diff = {
        "schema_version": "CONTINUITY_DIFF_FROM_PREVIOUS_V0_1",
        "generated_at": now_iso(),
        "previous_pack_path": str(previous) if previous else None,
        "current_pack_path": str(pack_dir),
        "changes": diff_changes,
        "has_changes": bool(diff_changes),
    }
    write_json(pack_dir / "CONTINUITY_DIFF_FROM_PREVIOUS.json", diff)
    write_text(pack_dir / "CONTINUITY_DIFF_FROM_PREVIOUS.md", "\n".join(["# CONTINUITY DIFF FROM PREVIOUS", "", f"- Previous pack: {diff['previous_pack_path']}", f"- Has changes: {diff['has_changes']}", "", "## Changes"] + [f"- {x['field']}: old={x['old']} | new={x['new']}" for x in diff_changes]) + "\n")

    ports_snap = {
        "schema_version": "PORTS_SNAPSHOT_V0_1",
        "generated_at": now_iso(),
        "registry_path": str(ports_registry),
        "ports": ports_data.get("snapshot", []),
        "summary": {
            "total_ports": len(ports_data.get("snapshot", [])),
            "missing_count": len(ports_data.get("missing", [])),
            "stale_count": len(ports_data.get("stale", [])),
            "fallback_warnings": ports_data.get("warnings", []),
        },
    }
    write_json(pack_dir / "PORTS_SNAPSHOT.json", ports_snap)
    write_text(pack_dir / "PORTS_SNAPSHOT.md", "\n".join(["# PORTS SNAPSHOT", "", f"- Total ports: {ports_snap['summary']['total_ports']}", f"- Missing count: {ports_snap['summary']['missing_count']}", f"- Stale count: {ports_snap['summary']['stale_count']}", "", "## Warnings"] + ([f"- {x}" for x in ports_data.get("warnings", [])] if ports_data.get("warnings") else ["- none"])) + "\n")
    miss_rep = {"schema_version": "PORT_MISSING_REPORT_V0_1", "generated_at": now_iso(), "items": ports_data.get("missing", []), "count": len(ports_data.get("missing", []))}
    write_json(pack_dir / "PORT_MISSING_REPORT.json", miss_rep)
    write_text(pack_dir / "PORT_MISSING_REPORT.md", "\n".join(["# PORT MISSING REPORT", "", f"- Missing items: {miss_rep['count']}"] + [f"- {x.get('organ_id')}: {x.get('reason')} | {x.get('path')}" for x in miss_rep["items"]]) + "\n")
    stale_rep = {"schema_version": "PORT_STALENESS_REPORT_V0_1", "generated_at": now_iso(), "items": ports_data.get("stale", []), "count": len(ports_data.get("stale", []))}
    write_json(pack_dir / "PORT_STALENESS_REPORT.json", stale_rep)
    write_text(pack_dir / "PORT_STALENESS_REPORT.md", "\n".join(["# PORT STALENESS REPORT", "", f"- Stale items: {stale_rep['count']}"] + [f"- {x.get('organ_id')}: age_hours={x.get('age_hours')} threshold={x.get('stale_if_older_than_hours')}" for x in stale_rep["items"]]) + "\n")

    handoff = handoff_checks(pack, pack_dir, old_pack, ports_data)
    write_json(pack_dir / "HANDOFF_SUFFICIENCY_REPORT.json", handoff)
    write_text(pack_dir / "HANDOFF_SUFFICIENCY_REPORT.md", "\n".join(["# HANDOFF SUFFICIENCY REPORT", "", f"- Verdict: {handoff['verdict']}", "", "## Checks"] + [f"- {x['check']}: {x['ok']} ({x['detail']})" for x in handoff["checks"]] + (["", "## Critical Failures"] + [f"- {x['check']}: {x['detail']}" for x in handoff.get("critical_failures", [])] if handoff.get("critical_failures") else [])) + "\n")

    build_receipt = {
        "schema_version": "ADMINISTRATUM_CONTINUITY_BUILD_RECEIPT_V0_1",
        "pack_id": pack_id,
        "generated_at": now_iso(),
        "run_id": args.run_id,
        "trigger": args.trigger,
        "script_path": str(script_path),
        "script_sha256": script_sha,
        "ports_registry_path": str(ports_registry),
        "old_pack_reference_path": str(old_pack) if old_pack else None,
        "previous_pack_path": str(previous) if previous else None,
        "verdict": "PASS_WITH_LIMITATIONS" if handoff["verdict"] != "NEW_PACK_INSUFFICIENT_FOR_RELIABLE_HANDOFF" else "REPAIR_REQUIRED_CONTINUITY_MISSING_CRITICAL_STATE",
        "blockers": [x.get("check") for x in handoff.get("critical_failures", [])],
        "warnings": ports_data.get("warnings", []),
        "limitations": handoff.get("limitations", []),
        "next_action": next_actions[0],
        "no_archive_scan_observed": True,
        "no_sanctum_claim_observed": True,
        "no_vm2_observed": True,
        "no_throne_observed": True,
        "no_delete_policy_observed": True,
    }
    write_json(pack_dir / "BUILD_RECEIPT.json", build_receipt)
    manifest_path, sha_path = write_manifest_hashes(pack_dir)

    if isinstance(admin_self, dict):
        admin_self["latest_continuity_pack_path"] = str(pack_dir)
        admin_self["latest_build_receipt_path"] = str(pack_dir / "BUILD_RECEIPT.json")
        admin_self["last_updated_at"] = now_iso()
        write_json(admin / "SELF_REPORT.json", admin_self)

    print(
        json.dumps(
            {
                "ok": True,
                "pack_id": pack_id,
                "pack_path": str(pack_dir),
                "build_receipt_path": str(pack_dir / "BUILD_RECEIPT.json"),
                "manifest_path": str(manifest_path),
                "sha256sums_path": str(sha_path),
                "handoff_sufficiency_verdict": handoff.get("verdict"),
                "ports_missing_count": len(ports_data.get("missing", [])),
                "ports_stale_count": len(ports_data.get("stale", [])),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
