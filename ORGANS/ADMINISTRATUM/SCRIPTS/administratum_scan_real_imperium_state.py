#!/usr/bin/env python3
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


SKIP_NAMES = {
    "archive",
    "_archive",
    "00_archive",
    "old",
    "deprecated",
    "node_modules",
    "__pycache__",
}


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def read_json(path: Path, default=None):
    if not path.exists():
        return {} if default is None else default
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {} if default is None else default


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def list_recent_files(folder: Path, pattern: str, n: int = 5):
    if not folder.exists():
        return []
    items = sorted([x for x in folder.glob(pattern) if x.is_file()], key=lambda x: x.stat().st_mtime, reverse=True)
    return [str(x) for x in items[:n]]


def discover_organs(root: Path):
    organs_root = root / "ORGANS"
    out = []
    if not organs_root.exists():
        return out

    for organ_dir in sorted([x for x in organs_root.iterdir() if x.is_dir()], key=lambda x: x.name.lower()):
        if organ_dir.name.lower() in SKIP_NAMES:
            continue

        organ_id = organ_dir.name.upper()
        status_path = organ_dir / "ORGAN_STATUS.json"
        contract_path = organ_dir / "ORGAN_CONTRACT.json"
        utility_dir = organ_dir / "UTILITY"
        ports_dir = organ_dir / "PORTS"
        reports_dir = organ_dir / "REPORTS"
        receipts_dir = organ_dir / "RECEIPTS"

        dashboard_exists = False
        if utility_dir.exists():
            reg = utility_dir / "DASHBOARD_REGISTRY.json"
            if reg.exists():
                dashboard_exists = True
            else:
                for d in utility_dir.glob("WEB_DASHBOARD_*"):
                    if d.is_dir():
                        dashboard_exists = True
                        break

        status_json = read_json(status_path, {})
        blockers = status_json.get("blockers")
        if blockers is None:
            blockers = status_json.get("current_blockers")
        if blockers is None:
            blockers = []

        out.append(
            {
                "organ_id": organ_id,
                "path": str(organ_dir),
                "status_file_exists": status_path.exists(),
                "contract_exists": contract_path.exists(),
                "dashboard_exists": dashboard_exists,
                "utility_exists": utility_dir.exists(),
                "ports_exists": ports_dir.exists(),
                "latest_reports": list_recent_files(reports_dir, "*.json", 5) + list_recent_files(reports_dir, "*.md", 5),
                "latest_receipts": list_recent_files(receipts_dir, "*.json", 8),
                "known_blockers": blockers,
            }
        )
    return out


def discover_dashboards(root: Path):
    dashboards = []
    organs_root = root / "ORGANS"
    if not organs_root.exists():
        return dashboards
    for organ_dir in [x for x in organs_root.iterdir() if x.is_dir()]:
        if organ_dir.name.lower() in SKIP_NAMES:
            continue
        utility = organ_dir / "UTILITY"
        reg = utility / "DASHBOARD_REGISTRY.json"
        if reg.exists():
            data = read_json(reg, {})
            if isinstance(data, dict):
                for d in data.get("dashboards", []):
                    dashboards.append(
                        {
                            "organ_id": organ_dir.name.upper(),
                            "dashboard_id": d.get("dashboard_id"),
                            "version": d.get("version"),
                            "status": d.get("status"),
                            "url": d.get("url"),
                            "launcher_path": d.get("launcher_path"),
                            "registry_path": str(reg),
                        }
                    )
    return dashboards


def discover_finalization_receipts(root: Path, n: int = 30):
    artifacts = root / "ARTIFACTS"
    receipts = []
    if not artifacts.exists():
        return receipts

    for task_dir in [x for x in artifacts.iterdir() if x.is_dir()]:
        if task_dir.name.lower() in SKIP_NAMES:
            continue
        # bounded known locations
        candidates = [
            task_dir / "PACKAGE" / "FINALIZATION_RECEIPT_EXTERNAL.json",
            task_dir / "13_PACKAGE" / "FINALIZATION_RECEIPT_EXTERNAL.json",
            task_dir / "15_PACKAGE" / "FINALIZATION_RECEIPT_EXTERNAL.json",
        ]
        for c in candidates:
            if c.exists() and c.is_file():
                data = read_json(c, {})
                receipts.append(
                    {
                        "task_artifact": str(task_dir),
                        "path": str(c),
                        "verdict": data.get("verdict"),
                        "zip_path": data.get("final_zip_path") or data.get("zip_path"),
                        "zip_sha256": data.get("final_zip_sha256") or data.get("zip_sha256"),
                        "created_at": data.get("finalization_time") or data.get("created_at"),
                        "mtime": c.stat().st_mtime,
                    }
                )
    receipts = sorted(receipts, key=lambda x: x.get("mtime", 0), reverse=True)
    for r in receipts:
        r.pop("mtime", None)
    return receipts[:n]


def discover_continuity_packs(root: Path, old_target: str):
    packs_root = root / "ORGANS" / "ADMINISTRATUM" / "CONTINUITY" / "PACKS"
    items = []
    if packs_root.exists():
        for p in sorted([x for x in packs_root.glob("CONTINUITY_PACK_*") if x.is_dir()], key=lambda x: x.name):
            cp = p / "CONTINUITY_PACK.json"
            bi = p / "BUILD_RECEIPT.json"
            verdict = None
            if bi.exists():
                verdict = read_json(bi, {}).get("verdict")
            items.append(
                {
                    "pack_id": p.name,
                    "path": str(p),
                    "has_pack_json": cp.exists(),
                    "has_build_receipt": bi.exists(),
                    "build_verdict": verdict,
                    "manifest_path": str(p / "MANIFEST.json") if (p / "MANIFEST.json").exists() else None,
                    "sha256sums_path": str(p / "SHA256SUMS.txt") if (p / "SHA256SUMS.txt").exists() else None,
                    "mtime": p.stat().st_mtime,
                }
            )
    items = sorted(items, key=lambda x: x["mtime"])
    selected_old = [x for x in items if old_target in x["pack_id"]]
    newest_before_task = items[-1] if items else None
    for x in items:
        x.pop("mtime", None)
    return {
        "packs": items,
        "selected_old_candidates": selected_old,
        "newest_pack_before_this_scan": newest_before_task,
    }


def discover_recent_artifacts(root: Path, n: int = 25):
    artifacts = root / "ARTIFACTS"
    out = []
    if not artifacts.exists():
        return out
    dirs = sorted([x for x in artifacts.iterdir() if x.is_dir()], key=lambda x: x.stat().st_mtime, reverse=True)
    for d in dirs[:n]:
        if d.name.lower() in SKIP_NAMES:
            continue
        final = None
        for c in [
            d / "PACKAGE" / "FINALIZATION_RECEIPT_EXTERNAL.json",
            d / "13_PACKAGE" / "FINALIZATION_RECEIPT_EXTERNAL.json",
            d / "15_PACKAGE" / "FINALIZATION_RECEIPT_EXTERNAL.json",
        ]:
            if c.exists():
                final = str(c)
                break
        owner_summary = None
        for c in [d / "OWNER_SUMMARY", d / "08_OWNER_SUMMARY", d / "09_OWNER_SUMMARY", d / "12_OWNER_SUMMARY", d / "14_OWNER_SUMMARY"]:
            if c.exists():
                mds = list(c.glob("*.md"))
                if mds:
                    owner_summary = str(mds[0])
                    break
        out.append(
            {
                "artifact_folder": str(d),
                "last_modified": dt.datetime.fromtimestamp(d.stat().st_mtime, dt.timezone.utc).isoformat(),
                "finalization_receipt": final,
                "owner_summary": owner_summary,
            }
        )
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=r"E:\IMPERIUM")
    parser.add_argument("--old-pack-target", default="CONTINUITY_PACK_20260510_082210")
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--output-limitations-md", required=True)
    args = parser.parse_args()

    root = Path(args.root)
    admin = root / "ORGANS" / "ADMINISTRATUM"

    organs = discover_organs(root)
    dashboards = discover_dashboards(root)
    finalizations = discover_finalization_receipts(root, 40)
    continuity = discover_continuity_packs(root, args.old_pack_target)
    recent_artifacts = discover_recent_artifacts(root, 35)

    doctr_state_path = root / "ORGANS" / "DOCTRINARIUM" / "STATUS" / "DOCTRINARIUM_STATUS.json"
    doctr_all_gap = root / "ORGANS" / "DOCTRINARIUM" / "REPORTS" / "ALL_ORGANS_GAP_REPORT.json"
    doctr_util_gap = root / "ORGANS" / "DOCTRINARIUM" / "REPORTS" / "ORGAN_UTILITY_GAP_REPORT.json"
    doctr_state = read_json(doctr_state_path, {})
    all_gap_json = read_json(doctr_all_gap, {})
    util_gap_json = read_json(doctr_util_gap, {})

    admin_status = read_json(admin / "ORGAN_STATUS.json", {})
    admin_dashboard_status = read_json(admin / "UTILITY" / "WEB_DASHBOARD_V0_1" / "DASHBOARD_STATUS_V0_1.json", {})
    admin_self_report = read_json(admin / "SELF_REPORT.json", {})
    lex_status = read_json(admin / "LEXICON" / "LANGUAGE_BASE_STATUS.json", {})
    latest_comp = None
    comp_root = admin / "CONTINUITY" / "COMPARISONS"
    if comp_root.exists():
        cmp_files = sorted([x for x in comp_root.glob("CONTINUITY_COMPARISON_*.json") if x.is_file()], key=lambda x: x.name)
        if cmp_files:
            latest_comp = str(cmp_files[-1])

    payload = {
        "schema_version": "REAL_IMPERIUM_STATE_V0_1",
        "generated_at": now_iso(),
        "root": str(root),
        "old_pack_target": args.old_pack_target,
        "organs_discovered": organs,
        "known_dashboards": dashboards,
        "known_finalization_receipts": finalizations,
        "known_continuity_packs": continuity,
        "recent_task_artifacts": recent_artifacts,
        "doctrinarium_state": {
            "status_path": str(doctr_state_path),
            "all_organs_gap_report_path": str(doctr_all_gap),
            "organ_utility_gap_report_path": str(doctr_util_gap),
            "status": doctr_state,
            "all_organs_gap_summary": {
                "verdict": all_gap_json.get("verdict"),
                "total_organs_checked": all_gap_json.get("total_organs_checked"),
                "total_blockers_found": all_gap_json.get("total_blockers_found"),
            },
            "utility_gap_summary": {
                "verdict": util_gap_json.get("verdict"),
                "summary": util_gap_json.get("summary", {}),
            },
            "law_enforcement_status": doctr_state.get("law_registry_status", {}),
            "current_blockers_count": len(doctr_state.get("blockers", [])) if isinstance(doctr_state.get("blockers", []), list) else None,
        },
        "administratum_state": {
            "status": admin_status,
            "dashboard_status": admin_dashboard_status,
            "self_report": admin_self_report,
            "latest_continuity_pack_path": admin_self_report.get("latest_continuity_pack_path"),
            "latest_comparison_path": admin_self_report.get("latest_comparison_path") or latest_comp,
            "generator_scripts": [
                str(admin / "SCRIPTS" / "administratum_build_continuity_pack.py"),
                str(admin / "SCRIPTS" / "administratum_compare_continuity_pack.py"),
            ],
            "language_base_status": lex_status,
        },
        "scan_policies": {
            "no_archive_recursive_scan": True,
            "no_sanctum_changes": True,
            "no_vm2": True,
            "no_throne": True,
            "bounded_scan": True,
        },
    }

    out_json = Path(args.output_json)
    out_md = Path(args.output_md)
    out_lim = Path(args.output_limitations_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_lim.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    md = []
    md.append("# REAL IMPERIUM STATE")
    md.append("")
    md.append(f"- Generated at: {payload['generated_at']}")
    md.append(f"- Old pack target: {args.old_pack_target}")
    md.append(f"- Organs discovered: {len(organs)}")
    md.append(f"- Known dashboards: {len(dashboards)}")
    md.append(f"- Known finalization receipts: {len(finalizations)}")
    md.append(f"- Known continuity packs: {len(continuity['packs'])}")
    md.append("")
    md.append("## Doctrinarium Summary")
    dsum = payload["doctrinarium_state"]["all_organs_gap_summary"]
    md.append(f"- All-organs verdict: {dsum.get('verdict')}")
    md.append(f"- Total organs checked: {dsum.get('total_organs_checked')}")
    md.append(f"- Total blockers: {dsum.get('total_blockers_found')}")
    md.append(f"- Utility verdict: {payload['doctrinarium_state']['utility_gap_summary'].get('verdict')}")
    md.append(f"- Law status: {payload['doctrinarium_state'].get('law_enforcement_status')}")
    md.append("")
    md.append("## Administratum Summary")
    md.append(f"- Status: {admin_status.get('status')}")
    md.append(f"- Dashboard ID: {admin_status.get('current_dashboard_id')}")
    md.append(f"- Latest continuity pack: {payload['administratum_state'].get('latest_continuity_pack_path')}")
    md.append(f"- Latest comparison: {payload['administratum_state'].get('latest_comparison_path')}")
    md.append("")
    md.append("## Old Pack Candidates")
    for c in continuity.get("selected_old_candidates", []):
        md.append(f"- {c.get('path')}")
    out_md.write_text("\n".join(md) + "\n", encoding="utf-8")

    lim = []
    lim.append("# REAL IMPERIUM SCAN LIMITATIONS")
    lim.append("")
    lim.append("- Scan is bounded to known IMPERIUM surfaces and excludes archive-like trees.")
    lim.append("- No recursive archive scan was performed.")
    lim.append("- No Sanctum modifications were made.")
    lim.append("- No VM2/THRONE actions were performed.")
    lim.append("- Heavy binary/deep third-party folders are excluded by design.")
    out_lim.write_text("\n".join(lim) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "ok": True,
                "organs_discovered": len(organs),
                "dashboards": len(dashboards),
                "selected_old_candidates": len(continuity.get("selected_old_candidates", [])),
                "output_json": str(out_json),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
