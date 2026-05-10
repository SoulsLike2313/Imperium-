#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path


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


def write_md(path: Path, title: str, body: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {title}", "", f"- generated_at: {body.get('generated_at')}"]
    if "verdict" in body:
        lines.append(f"- verdict: {body.get('verdict')}")
    for key in ["old_pack_path", "new_pack_path", "real_state_path", "ports_registry_path"]:
        if body.get(key):
            lines.append(f"- {key}: {body.get(key)}")
    checks = body.get("checks", [])
    if checks:
        lines.extend(["", "## checks"])
        for c in checks:
            lines.append(f"- {c.get('check')}: {c.get('ok')} ({c.get('detail')})")
    issues = body.get("issues", [])
    if issues:
        lines.extend(["", "## issues"])
        for i in issues:
            lines.append(f"- {i}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def list_packs(packs_root: Path):
    return sorted([x for x in packs_root.glob("CONTINUITY_PACK_*") if x.is_dir()], key=lambda p: p.name)


def resolve_old_pack(root: Path, arg_old):
    if arg_old:
        p = Path(arg_old)
        if p.exists():
            return p
    freeze = root / "ARTIFACTS" / "TASK-20260510-ADMINISTRATUM-CONTINUITY-PACK-QA-PORTS-AND-REBUILD-V0_1" / "00_INPUTS" / "INPUT_FREEZE.json"
    j = read_json(freeze, {})
    sel = j.get("selected_old_pack_path") if isinstance(j, dict) else None
    if sel and Path(sel).exists():
        return Path(sel)
    direct = root / "ORGANS" / "ADMINISTRATUM" / "CONTINUITY" / "PACKS" / "CONTINUITY_PACK_20260510_082210"
    return direct if direct.exists() else None


def pack_required_files_ok(pack_dir: Path):
    req = [
        "CONTINUITY_PACK.json",
        "CONTINUITY_PACK.md",
        "IMPERIUM_ENTRYPOINT_FOR_NEW_CHAT.md",
        "DO_NOT_DO.md",
        "NEXT_ACTIONS.md",
        "HANDOFF_SUFFICIENCY_REPORT.json",
        "PORTS_SNAPSHOT.json",
        "MANIFEST.json",
        "SHA256SUMS.txt",
        "BUILD_RECEIPT.json",
    ]
    missing = [x for x in req if not (pack_dir / x).exists()]
    return len(missing) == 0, missing


def check_pack_vs_real(pack_dir: Path, real_state: dict, ports_registry: dict, old_pack_expected: Path | None):
    pack = read_json(pack_dir / "CONTINUITY_PACK.json", {})
    checks = []
    issues = []

    def add(name, ok, detail):
        checks.append({"check": name, "ok": bool(ok), "detail": detail})
        if not ok:
            issues.append(f"{name}: {detail}")

    play = pack.get("latest_verified_dashboard", {}).get("doctrinarium_playwright_verdict")
    add("mentions_doctrinarium_v0_8_playwright_pass", play == "PASS_PLAYWRIGHT_V0_8_VISUAL_FUNCTIONAL_AUDIT", str(play))

    fin = Path(pack.get("evidence_paths", {}).get("administratum_v0_1_finalization", ""))
    add("mentions_administratum_v0_1_finalization", fin.exists(), str(fin))

    add("includes_ports_registry", Path(pack.get("ports_registry_path", "")).exists(), str(pack.get("ports_registry_path")))
    add("includes_next_action", bool(pack.get("next_actions")), str(pack.get("next_actions")))
    add("includes_do_not_do", bool(pack.get("do_not_do")), str(pack.get("do_not_do")))
    add("includes_limitations", bool(pack.get("limitations")), str(pack.get("limitations")))
    add("includes_evidence_paths", bool(pack.get("evidence_paths")), str(list((pack.get("evidence_paths") or {}).keys())))

    entry = (pack_dir / "IMPERIUM_ENTRYPOINT_FOR_NEW_CHAT.md").read_text(encoding="utf-8", errors="replace") if (pack_dir / "IMPERIUM_ENTRYPOINT_FOR_NEW_CHAT.md").exists() else ""
    add("entrypoint_role_neutral", "Owner will provide role separately." in entry and "Use evidence paths, not chat memory." in entry, entry[:180].replace("\n", " "))

    pack_orgs = {
        str(x.get("organ_id", "")).upper()
        for x in read_json(pack_dir / "PORTS_SNAPSHOT.json", {}).get("ports", [])
        if not str(x.get("organ_id", "")).startswith("_")
    }
    real_orgs = {
        str(x.get("organ_id", "")).upper()
        for x in real_state.get("organs_discovered", [])
        if not str(x.get("organ_id", "")).startswith("_")
    }
    missing_orgs = sorted(list(real_orgs - pack_orgs))
    add("ports_cover_real_organs", len(missing_orgs) == 0, str(missing_orgs))

    reg_orgs = {str(x.get("organ_id", "")).upper() for x in ports_registry.get("ports", [])} if isinstance(ports_registry, dict) else set()
    add("ports_registry_not_empty", len(reg_orgs) > 0, f"count={len(reg_orgs)}")

    if old_pack_expected:
        old_ref = pack.get("old_pack_reference_path") or (pack.get("evidence_paths", {}) or {}).get("old_pack_reference")
        add("references_selected_old_pack", str(old_ref) == str(old_pack_expected), f"expected={old_pack_expected} actual={old_ref}")

    ok_required, missing_required = pack_required_files_ok(pack_dir)
    add("required_new_pack_files_present", ok_required, str(missing_required))

    critical = {
        "mentions_doctrinarium_v0_8_playwright_pass",
        "mentions_administratum_v0_1_finalization",
        "includes_ports_registry",
        "includes_next_action",
        "includes_do_not_do",
        "includes_evidence_paths",
        "entrypoint_role_neutral",
        "required_new_pack_files_present",
    }
    critical_fails = [c for c in checks if (not c["ok"] and c["check"] in critical)]
    if critical_fails:
        verdict = "NEW_PACK_INSUFFICIENT_FOR_RELIABLE_HANDOFF"
    elif issues:
        verdict = "NEW_PACK_PARTIALLY_SUFFICIENT_NEEDS_REPAIR"
    else:
        verdict = "NEW_PACK_SUFFICIENT_FOR_BOOTSTRAP_NEW_CHAT_HANDOFF_WITH_LIMITATIONS"

    return {
        "generated_at": now_iso(),
        "pack_path": str(pack_dir),
        "checks": checks,
        "issues": issues,
        "critical_failures": critical_fails,
        "verdict": verdict,
    }


def old_new_diff(old_dir: Path, new_dir: Path):
    old = read_json(old_dir / "CONTINUITY_PACK.json", {})
    new = read_json(new_dir / "CONTINUITY_PACK.json", {})
    changed = []
    for key in [
        "schema_version",
        "current_completed_point",
        "known_blockers_count",
        "ports_registry_path",
        "old_pack_qa_verdict",
    ]:
        ov, nv = old.get(key), new.get(key)
        if ov != nv:
            changed.append({"field": key, "old": ov, "new": nv})
    old_files = sorted([x.name for x in old_dir.glob("*") if x.is_file()])
    new_files = sorted([x.name for x in new_dir.glob("*") if x.is_file()])
    return {
        "generated_at": now_iso(),
        "old_pack_path": str(old_dir),
        "new_pack_path": str(new_dir),
        "changed_fields": changed,
        "old_file_count": len(old_files),
        "new_file_count": len(new_files),
        "new_files_added": sorted(list(set(new_files) - set(old_files))),
        "files_removed": sorted(list(set(old_files) - set(new_files))),
        "verdict": "PASS_WITH_LIMITATIONS",
    }


def ports_vs_real(real_state: dict, ports_registry: dict):
    real_orgs = {
        str(x.get("organ_id", "")).upper()
        for x in real_state.get("organs_discovered", [])
        if not str(x.get("organ_id", "")).startswith("_")
    }
    reg_orgs = {
        str(x.get("organ_id", "")).upper()
        for x in (ports_registry.get("ports", []) if isinstance(ports_registry, dict) else [])
        if not str(x.get("organ_id", "")).startswith("_")
    }
    missing = sorted(list(real_orgs - reg_orgs))
    extra = sorted(list(reg_orgs - real_orgs))
    issues = []
    if missing:
        issues.append(f"Missing ports for real organs: {missing}")
    if extra:
        issues.append(f"Ports registered for non-discovered organs: {extra}")
    return {
        "generated_at": now_iso(),
        "real_organs_count": len(real_orgs),
        "registry_organs_count": len(reg_orgs),
        "missing_ports_for_real_organs": missing,
        "extra_registry_organs": extra,
        "issues": issues,
        "verdict": "PASS_WITH_LIMITATIONS" if not missing else "REPAIR_REQUIRED_CONTINUITY_MISSING_CRITICAL_STATE",
    }


def save_reports(out_dir: Path, old_new: dict, old_real: dict, new_real: dict, ports_real: dict, final_decision: dict):
    write_json(out_dir / "OLD_PACK_VS_NEW_PACK.json", old_new)
    write_md(out_dir / "OLD_PACK_VS_NEW_PACK.md", "OLD PACK VS NEW PACK", old_new)
    write_json(out_dir / "OLD_PACK_VS_REAL_IMPERIUM.json", old_real)
    write_md(out_dir / "OLD_PACK_VS_REAL_IMPERIUM.md", "OLD PACK VS REAL IMPERIUM", old_real)
    write_json(out_dir / "NEW_PACK_VS_REAL_IMPERIUM.json", new_real)
    write_md(out_dir / "NEW_PACK_VS_REAL_IMPERIUM.md", "NEW PACK VS REAL IMPERIUM", new_real)
    write_json(out_dir / "PORTS_VS_REAL_IMPERIUM.json", ports_real)
    write_md(out_dir / "PORTS_VS_REAL_IMPERIUM.md", "PORTS VS REAL IMPERIUM", ports_real)
    write_json(out_dir / "FINAL_HANDOFF_SUFFICIENCY_DECISION.json", final_decision)
    write_md(out_dir / "FINAL_HANDOFF_SUFFICIENCY_DECISION.md", "FINAL HANDOFF SUFFICIENCY DECISION", final_decision)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=r"E:\IMPERIUM")
    ap.add_argument("--old-pack-path", default=None)
    ap.add_argument("--new-pack-path", default=None)
    ap.add_argument("--real-state-path", default=None)
    ap.add_argument("--ports-registry-path", default=None)
    ap.add_argument("--output-dir", default=None)
    args = ap.parse_args()

    root = Path(args.root)
    admin = root / "ORGANS" / "ADMINISTRATUM"
    packs_root = admin / "CONTINUITY" / "PACKS"
    comparisons_root = admin / "CONTINUITY" / "COMPARISONS"
    comparisons_root.mkdir(parents=True, exist_ok=True)

    packs = list_packs(packs_root)
    if not packs:
        print(json.dumps({"ok": False, "error": "No continuity packs found."}, ensure_ascii=False))
        return 2

    new_pack = Path(args.new_pack_path) if args.new_pack_path else packs[-1]
    old_pack = Path(args.old_pack_path) if args.old_pack_path else resolve_old_pack(root, None)
    if old_pack is None and len(packs) >= 2:
        old_pack = packs[-2]
    if old_pack is not None and old_pack.resolve() == new_pack.resolve() and len(packs) >= 2:
        old_pack = packs[-2]
    if old_pack is None:
        old_pack = new_pack

    real_state_path = Path(args.real_state_path) if args.real_state_path else (
        root / "ARTIFACTS" / "TASK-20260510-ADMINISTRATUM-CONTINUITY-PACK-QA-PORTS-AND-REBUILD-V0_1" / "01_REAL_IMPERIUM_SCAN" / "REAL_IMPERIUM_STATE.json"
    )
    ports_registry_path = Path(args.ports_registry_path) if args.ports_registry_path else (admin / "ADDRESS_REGISTRY" / "CONTINUITY_PORTS.json")

    real_state = read_json(real_state_path, {})
    ports_registry = read_json(ports_registry_path, {})

    old_vs_new = old_new_diff(old_pack, new_pack)
    old_vs_real = check_pack_vs_real(old_pack, real_state, ports_registry, old_pack)
    new_vs_real = check_pack_vs_real(new_pack, real_state, ports_registry, old_pack)
    ports_real = ports_vs_real(real_state, ports_registry)

    if new_vs_real["verdict"] == "NEW_PACK_INSUFFICIENT_FOR_RELIABLE_HANDOFF":
        final_verdict = "NEW_PACK_INSUFFICIENT_FOR_RELIABLE_HANDOFF"
    elif new_vs_real["issues"] or ports_real["verdict"] != "PASS_WITH_LIMITATIONS":
        final_verdict = "NEW_PACK_PARTIALLY_SUFFICIENT_NEEDS_REPAIR"
    else:
        final_verdict = "NEW_PACK_SUFFICIENT_FOR_BOOTSTRAP_NEW_CHAT_HANDOFF_WITH_LIMITATIONS"

    final_decision = {
        "generated_at": now_iso(),
        "old_pack_path": str(old_pack),
        "new_pack_path": str(new_pack),
        "real_state_path": str(real_state_path),
        "ports_registry_path": str(ports_registry_path),
        "old_pack_verdict": old_vs_real["verdict"],
        "new_pack_verdict": new_vs_real["verdict"],
        "ports_vs_real_verdict": ports_real["verdict"],
        "verdict": final_verdict,
        "checks": [
            {"check": "old_pack_evaluated", "ok": True, "detail": str(old_pack)},
            {"check": "new_pack_evaluated", "ok": True, "detail": str(new_pack)},
            {"check": "real_state_loaded", "ok": bool(real_state), "detail": str(real_state_path)},
            {"check": "ports_registry_loaded", "ok": bool(ports_registry), "detail": str(ports_registry_path)},
        ],
        "issues": old_vs_real.get("issues", []) + new_vs_real.get("issues", []) + ports_real.get("issues", []),
        "limitations": [
            "Comparison proves bootstrap handoff quality only.",
            "No canon or full readiness claim is implied.",
        ],
    }

    out_dir = Path(args.output_dir) if args.output_dir else comparisons_root
    out_dir.mkdir(parents=True, exist_ok=True)
    save_reports(out_dir, old_vs_new, old_vs_real, new_vs_real, ports_real, final_decision)

    ts = ts_id()
    summary_json = comparisons_root / f"CONTINUITY_COMPARISON_{ts}.json"
    summary_md = comparisons_root / f"CONTINUITY_COMPARISON_{ts}.md"
    summary = {
        "schema_version": "ADMINISTRATUM_CONTINUITY_COMPARISON_V0_1",
        "generated_at": now_iso(),
        "old_pack_path": str(old_pack),
        "new_pack_path": str(new_pack),
        "real_state_path": str(real_state_path),
        "ports_registry_path": str(ports_registry_path),
        "verdict": final_verdict,
        "old_pack_verdict": old_vs_real.get("verdict"),
        "new_pack_verdict": new_vs_real.get("verdict"),
        "issues_count": len(final_decision.get("issues", [])),
        "issues": final_decision.get("issues", []),
        "outputs": {
            "output_dir": str(out_dir),
            "final_decision_json": str(out_dir / "FINAL_HANDOFF_SUFFICIENCY_DECISION.json"),
        },
    }
    write_json(summary_json, summary)
    write_md(summary_md, "CONTINUITY COMPARISON", summary)

    self_report = read_json(admin / "SELF_REPORT.json", {})
    if isinstance(self_report, dict):
        self_report["latest_comparison_path"] = str(summary_json)
        self_report["last_updated_at"] = now_iso()
        write_json(admin / "SELF_REPORT.json", self_report)

    print(
        json.dumps(
            {
                "ok": True,
                "verdict": final_verdict,
                "old_pack_path": str(old_pack),
                "new_pack_path": str(new_pack),
                "output_dir": str(out_dir),
                "summary_json": str(summary_json),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
