#!/usr/bin/env python3
import argparse
import datetime as dt
import json
from pathlib import Path


FORBIDDEN_CLAIMS = [
    "CONTINUITY_GREEN",
    "CANON_V0_1",
    "SANCTUM_READY",
    "ALL_ORGANS_READY",
    "REAL_TASK_EXECUTION_READY",
]


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def read_json(path: Path, default=None):
    if not path.exists():
        return {} if default is None else default
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {} if default is None else default


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8-sig", errors="replace")
    except Exception:
        return ""


def contains_token(value: str, token: str) -> bool:
    return token.lower() in (value or "").lower()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--old-pack-path", required=True)
    parser.add_argument("--real-state-json", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--missing-md", required=True)
    parser.add_argument("--stale-md", required=True)
    parser.add_argument("--contradiction-md", required=True)
    parser.add_argument("--handoff-md", required=True)
    args = parser.parse_args()

    old_pack = Path(args.old_pack_path)
    real = read_json(Path(args.real_state_json), {})

    cp_json = read_json(old_pack / "CONTINUITY_PACK.json", {})
    cp_md = read_text(old_pack / "CONTINUITY_PACK.md")
    entry_text = read_text(old_pack / "ENTRYPOINT_FOR_NEW_CHAT.md")
    next_actions_text = read_text(old_pack / "NEXT_ACTIONS.md")
    do_not_do_text = read_text(old_pack / "DO_NOT_DO.md")
    blockers_text = read_text(old_pack / "BLOCKERS.md")
    org_snapshot = read_json(old_pack / "ORGAN_SNAPSHOT.json", {})
    dashboard_snapshot = read_json(old_pack / "DASHBOARD_SNAPSHOT.json", {})
    law_snapshot = read_json(old_pack / "LAW_AND_DOCTRINE_SNAPSHOT.json", {})
    artifacts_index = read_json(old_pack / "ARTIFACT_INDEX.json", {})
    receipts_index = read_json(old_pack / "LATEST_RECEIPTS_INDEX.json", {})
    diff_json = read_json(old_pack / "CONTINUITY_DIFF_FROM_PREVIOUS.json", {})

    known_dashboards = real.get("known_dashboards", [])
    known_finalizations = real.get("known_finalization_receipts", [])
    doctr = real.get("doctrinarium_state", {})
    admin_state = real.get("administratum_state", {})

    checks = []
    missing = []
    stale = []
    contradictions = []
    warnings = []

    def add(name: str, ok: bool, detail: str):
        checks.append({"check": name, "ok": bool(ok), "detail": detail})
        if not ok:
            missing.append(f"{name}: {detail}")

    # 1-2 Doctrinarium dashboard & playwright
    dashboard_id = cp_json.get("latest_verified_dashboard", {}).get("doctrinarium_dashboard_id")
    playwright_verdict = cp_json.get("latest_verified_dashboard", {}).get("playwright_verdict")
    add("mentions_doctrinarium_dashboard_v0_8", dashboard_id == "DOCTRINARIUM_WEB_DASHBOARD_V0_8", str(dashboard_id))
    add(
        "mentions_playwright_pass_for_doctrinarium_v0_8",
        playwright_verdict == "PASS_PLAYWRIGHT_V0_8_VISUAL_FUNCTIONAL_AUDIT",
        str(playwright_verdict),
    )

    # 3 Administratum task finalization
    has_admin_finalization = any(
        "TASK-20260509-ADMINISTRATUM-ORGAN-DASHBOARD-AND-CONTINUITY-PACK-V0_1" in str(x.get("task_artifact", ""))
        for x in known_finalizations
    )
    cp_evidence = cp_json.get("evidence_paths", {})
    add(
        "mentions_administratum_task_finalization",
        has_admin_finalization and any("ADMINISTRATUM-ORGAN-DASHBOARD-AND-CONTINUITY-PACK-V0_1" in str(v) for v in cp_evidence.values()),
        str(cp_evidence),
    )

    # 4-6 Admin dashboard, button test, latest comparison
    add("mentions_administratum_dashboard_v0_1", "ADMINISTRATUM_WEB_DASHBOARD_V0_1" in json.dumps(dashboard_snapshot), "dashboard snapshot scan")
    has_button_test = any("06_button_test_receipt.json" in str(x.get("path", "")) for x in receipts_index.get("receipts", []))
    add("mentions_build_continuity_pack_button_test", has_button_test, "receipts index button test path presence")
    add(
        "mentions_latest_known_continuity_comparison",
        bool(cp_json.get("latest_administratum_state")) and bool(admin_state.get("latest_comparison_path")),
        f"pack_has_latest_admin_state={bool(cp_json.get('latest_administratum_state'))}, real_latest={admin_state.get('latest_comparison_path')}",
    )

    # 7 Doctrinarium gaps after Administratum
    real_gap_summary = doctr.get("all_organs_gap_summary", {})
    old_org_summary = org_snapshot.get("summary", {})
    ok_gap_ref = (
        old_org_summary.get("total_organs") == real_gap_summary.get("total_organs_checked")
        and old_org_summary.get("total_blockers") == real_gap_summary.get("total_blockers_found")
    )
    add(
        "mentions_current_doctrinarium_gaps_after_administratum",
        ok_gap_ref,
        f"old={old_org_summary}, real={real_gap_summary}",
    )

    # 8 next action currency
    next_actions = cp_json.get("next_actions", [])
    add("contains_current_next_action", isinstance(next_actions, list) and len(next_actions) > 0, str(next_actions))

    # 9 in-progress contradiction
    current_point = str(cp_json.get("current_completed_point", ""))
    if contains_token(current_point, "in progress") and has_admin_finalization:
        contradictions.append("Pack says 'in progress' while Administratum v0_1 finalization receipt exists.")
    add("no_in_progress_finalization_conflict", len(contradictions) == 0, current_point)

    # 10 count/list contradictions
    if old_org_summary.get("total_organs") and real_gap_summary.get("total_organs_checked"):
        if old_org_summary.get("total_organs") != real_gap_summary.get("total_organs_checked"):
            contradictions.append("Organ count mismatch between old pack snapshot and real Doctrinarium gap report.")
    add("no_count_list_contradictions", len([x for x in contradictions if "count" in x.lower() or "mismatch" in x.lower()]) == 0, str(contradictions))

    # 11 diff quality
    if diff_json.get("status") == "FIRST_PACK_NO_PREVIOUS" and len(real.get("known_continuity_packs", {}).get("packs", [])) > 1:
        stale.append("Old pack diff says FIRST_PACK_NO_PREVIOUS while multiple packs exist in real state.")
    add("diff_not_empty_when_real_changes_exist", len(stale) == 0, str(stale))

    # 12 role-neutral entrypoint
    role_neutral = "Owner will provide role separately" in entry_text
    add("entrypoint_role_neutral_enough", role_neutral, entry_text[:240])

    # 13 no fake green
    serialized = json.dumps(cp_json, ensure_ascii=False)
    bad_claims = [c for c in FORBIDDEN_CLAIMS if c in serialized]
    # Allow forbidden words inside do-not-do section only
    if bad_claims and not all(c in json.dumps(cp_json.get("forbidden_claims", []), ensure_ascii=False) for c in bad_claims):
        warnings.append(f"Potential forbidden claim tokens in payload: {bad_claims}")
    add("avoids_fake_green_claims", len(warnings) == 0, str(warnings))

    # 14 evidence paths
    evidence_paths = cp_json.get("evidence_paths", {})
    add("contains_evidence_paths", isinstance(evidence_paths, dict) and len(evidence_paths) > 0, str(list(evidence_paths.keys())))

    # 15 limitations
    limits = cp_json.get("limitations", [])
    add("contains_limitations", isinstance(limits, list) and len(limits) > 0, str(limits))

    # 16 do-not-do
    add("contains_do_not_do", "no fake green" in do_not_do_text.lower(), do_not_do_text[:220])

    # 17 dashboards coverage
    pack_dash_json = json.dumps(dashboard_snapshot, ensure_ascii=False)
    dashboards_ok = True
    for d in known_dashboards:
        did = d.get("dashboard_id")
        if did and did not in pack_dash_json:
            dashboards_ok = False
            stale.append(f"Dashboard {did} absent from dashboard snapshot.")
    add("contains_current_known_dashboards", dashboards_ok, f"known_dashboards={len(known_dashboards)}")

    # 18 artifacts and receipts coverage
    has_artifacts = isinstance(artifacts_index.get("items", []), list) and len(artifacts_index.get("items", [])) > 0
    has_receipts = isinstance(receipts_index.get("receipts", []), list) and len(receipts_index.get("receipts", [])) > 0
    add("contains_current_artifacts_and_receipts", has_artifacts and has_receipts, f"artifacts={has_artifacts}, receipts={has_receipts}")

    # 19 chronology depth
    chronology_text = read_text(old_pack / "SYSTEM_CHRONOLOGY.md")
    chrono_ok = chronology_text.count("- ") >= 7
    add("contains_enough_chronology", chrono_ok, f"bullet_count={chronology_text.count('- ')}")

    # 20 new-chat sufficiency
    critical_checks = [
        "mentions_doctrinarium_dashboard_v0_8",
        "mentions_playwright_pass_for_doctrinarium_v0_8",
        "mentions_administratum_task_finalization",
        "contains_current_next_action",
        "contains_do_not_do",
        "contains_evidence_paths",
        "contains_limitations",
        "entrypoint_role_neutral_enough",
    ]
    crit_ok = all(next((c["ok"] for c in checks if c["check"] == n), False) for n in critical_checks)
    add("sufficient_for_new_chat_without_additional_memory", crit_ok, "critical handoff checks")

    # Derive verdict
    if contradictions:
        verdict = "OLD_PACK_CONTRADICTS_REALITY"
    elif crit_ok and len(stale) == 0 and len(warnings) == 0:
        verdict = "OLD_PACK_SUFFICIENT_FOR_BOOTSTRAP_HANDOFF"
    elif crit_ok:
        verdict = "OLD_PACK_PARTIALLY_SUFFICIENT_REPAIR_RECOMMENDED"
    else:
        verdict = "OLD_PACK_INSUFFICIENT_FOR_RELIABLE_HANDOFF"

    report = {
        "schema_version": "OLD_PACK_VS_REALITY_QA_V0_1",
        "old_pack_path": str(old_pack),
        "real_state_json": args.real_state_json,
        "generated_at": now_iso(),
        "checks": checks,
        "missing_state_items": missing,
        "stale_state_items": stale,
        "contradictions": contradictions,
        "warnings": warnings,
        "verdict": verdict,
    }

    Path(args.output_json).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    md = ["# OLD PACK VS REALITY QA", "", f"- Verdict: {verdict}", "", "## Checks"]
    for c in checks:
        md.append(f"- {c['check']}: {c['ok']} ({c['detail']})")
    if missing:
        md += ["", "## Missing"]
        md += [f"- {m}" for m in missing]
    if stale:
        md += ["", "## Stale"]
        md += [f"- {s}" for s in stale]
    if contradictions:
        md += ["", "## Contradictions"]
        md += [f"- {x}" for x in contradictions]
    if warnings:
        md += ["", "## Warnings"]
        md += [f"- {w}" for w in warnings]
    Path(args.output_md).write_text("\n".join(md) + "\n", encoding="utf-8")

    Path(args.missing_md).write_text("# MISSING STATE REPORT\n\n" + ("\n".join([f"- {m}" for m in missing]) if missing else "- none\n"), encoding="utf-8")
    Path(args.stale_md).write_text("# STALE STATE REPORT\n\n" + ("\n".join([f"- {s}" for s in stale]) if stale else "- none\n"), encoding="utf-8")
    Path(args.contradiction_md).write_text(
        "# CONTRADICTION REPORT\n\n" + ("\n".join([f"- {x}" for x in contradictions]) if contradictions else "- none\n"),
        encoding="utf-8",
    )
    Path(args.handoff_md).write_text(
        "# HANDOFF SUFFICIENCY REPORT\n\n"
        f"- Verdict: {verdict}\n"
        f"- Sufficient now: {crit_ok}\n"
        f"- Missing count: {len(missing)}\n"
        f"- Stale count: {len(stale)}\n"
        f"- Contradictions count: {len(contradictions)}\n",
        encoding="utf-8",
    )

    print(json.dumps({"ok": True, "verdict": verdict, "missing": len(missing), "stale": len(stale), "contradictions": len(contradictions)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
