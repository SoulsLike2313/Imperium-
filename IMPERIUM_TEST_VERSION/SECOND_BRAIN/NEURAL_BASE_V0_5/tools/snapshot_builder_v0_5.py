"""
Second Brain Neural Base V0.5 — Snapshot Builder
Reads zone_registry + truth_matrix, evaluates health per zone,
collects telemetry, writes neural_snapshot_live.json.

Runtime mode: PROTOTYPE_INTERACTIVE | RULE_BASED_ONLY | NO_LOCAL_LLM | NO_AGENT_API
"""

import json
import os
import sys
import datetime
import glob
import time

# ── Paths ──────────────────────────────────────────────────────────────────────
TOOLS_DIR       = os.path.dirname(os.path.abspath(__file__))
V05_ROOT        = os.path.dirname(TOOLS_DIR)
SECOND_BRAIN    = os.path.dirname(V05_ROOT)
TEST_VERSION    = os.path.dirname(SECOND_BRAIN)
REPO_ROOT       = os.path.dirname(TEST_VERSION)

REGISTRY_DIR    = os.path.join(V05_ROOT, "registry")
TRUTH_DIR       = os.path.join(V05_ROOT, "truth_matrix")
REPORTS_DIR     = os.path.join(V05_ROOT, "reports")

ZONE_REGISTRY   = os.path.join(REGISTRY_DIR, "zone_registry_v0_5.json")
LAYOUT_CONFIG   = os.path.join(REGISTRY_DIR, "layout_config.json")
SNAPSHOT_OUT    = os.path.join(REPORTS_DIR, "neural_snapshot_live.json")

os.makedirs(REPORTS_DIR, exist_ok=True)


def now_iso():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def resolve_path(pattern):
    """Resolve a source pattern relative to REPO_ROOT."""
    full = os.path.join(REPO_ROOT, pattern.replace("/", os.sep))
    return full


def source_exists(pattern):
    """Check if a source pattern resolves to at least one existing file/dir."""
    full = resolve_path(pattern)
    if "*" in full:
        return len(glob.glob(full)) > 0
    return os.path.exists(full)


def load_json_safe(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), None
    except Exception as e:
        return None, str(e)


def collect_telemetry_for_zone(zone_id, zone_def):
    """Collect zone-specific telemetry metrics."""
    tel = {}

    if zone_id == "task_intake":
        p = resolve_path("IMPERIUM_TEST_VERSION/SECOND_BRAIN/MEMORY_ZONES/TASK_INTAKE/accepted_tasks.json")
        d, _ = load_json_safe(p)
        if d:
            tasks = d.get("tasks", [])
            tel["task_count"] = len(tasks)
            linked = sum(1 for t in tasks if t.get("links"))
            tel["unlinked_task_count"] = len(tasks) - linked
            if tasks:
                try:
                    last_ts = tasks[-1].get("created_at", "")
                    if last_ts:
                        dt = datetime.datetime.strptime(last_ts, "%Y-%m-%dT%H:%M:%SZ")
                        tel["last_task_age_seconds"] = int((datetime.datetime.utcnow() - dt).total_seconds())
                except Exception:
                    tel["last_task_age_seconds"] = -1

    elif zone_id == "owner_comments":
        p = resolve_path("IMPERIUM_TEST_VERSION/SECOND_BRAIN/MEMORY_ZONES/OWNER_COMMENTS/owner_comments_runtime.json")
        d, _ = load_json_safe(p)
        if d:
            comments = d.get("comments", [])
            tel["comment_count"] = len(comments)
            tel["linked_count"] = sum(1 for c in comments if c.get("linked_tasks"))
            tel["unlinked_count"] = sum(1 for c in comments if not c.get("linked_tasks"))
            tel["needs_interpretation_count"] = sum(1 for c in comments if c.get("status") == "NEEDS_INTERPRETATION")

    elif zone_id == "memory_threads":
        lp = resolve_path("IMPERIUM_TEST_VERSION/SECOND_BRAIN/MEMORY_ZONES/MEMORY_LINKS/task_comment_links.json")
        tp = resolve_path("IMPERIUM_TEST_VERSION/SECOND_BRAIN/MEMORY_ZONES/TASK_INTAKE/accepted_tasks.json")
        cp = resolve_path("IMPERIUM_TEST_VERSION/SECOND_BRAIN/MEMORY_ZONES/OWNER_COMMENTS/owner_comments_runtime.json")
        ld, _ = load_json_safe(lp)
        td, _ = load_json_safe(tp)
        cd, _ = load_json_safe(cp)
        if ld:
            links = ld.get("links", [])
            tel["link_count"] = len(links)
            task_ids = {t["task_id"] for t in (td or {}).get("tasks", [])}
            comment_ids = {c["comment_id"] for c in (cd or {}).get("comments", [])}
            broken = sum(1 for l in links if l.get("source_id") not in task_ids or l.get("target_id") not in comment_ids)
            tel["broken_link_count"] = broken
            tel["orphaned_task_count"] = len(task_ids - {l.get("source_id") for l in links})
            tel["orphaned_comment_count"] = len(comment_ids - {l.get("target_id") for l in links})

    elif zone_id in ("progress_spine", "evidence_receipts"):
        receipts_dir = resolve_path("IMPERIUM_TEST_VERSION/SECOND_BRAIN/RUNTIME/receipts")
        if os.path.isdir(receipts_dir):
            rfiles = [f for f in os.listdir(receipts_dir) if f.endswith(".json")]
            tel["receipt_count"] = len(rfiles)
            tel["event_count"] = len(rfiles)
            no_llm_count = 0
            last_ts = None
            for rf in rfiles:
                rd, _ = load_json_safe(os.path.join(receipts_dir, rf))
                if rd:
                    if rd.get("no_llm_used") is True:
                        no_llm_count += 1
                    ts = rd.get("created_at", "")
                    if ts and (last_ts is None or ts > last_ts):
                        last_ts = ts
            tel["no_llm_rate"] = round(no_llm_count / max(len(rfiles), 1) * 100)
            if last_ts:
                try:
                    dt = datetime.datetime.strptime(last_ts, "%Y-%m-%dT%H:%M:%SZ")
                    tel["last_event_age_seconds"] = int((datetime.datetime.utcnow() - dt).total_seconds())
                except Exception:
                    tel["last_event_age_seconds"] = -1
        exports_dir = resolve_path("IMPERIUM_TEST_VERSION/SECOND_BRAIN/RUNTIME/exports")
        if os.path.isdir(exports_dir):
            manifests = glob.glob(os.path.join(exports_dir, "**", "manifest.json"), recursive=True)
            tel["export_count"] = len(manifests)

    elif zone_id == "action_control":
        ap = resolve_path("IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_4/registry/neural_action_registry.json")
        d, _ = load_json_safe(ap)
        if d:
            actions = d.get("actions", [])
            tel["enabled_action_count"] = sum(1 for a in actions if "DISABLED" not in a.get("status", ""))
            tel["disabled_action_count"] = sum(1 for a in actions if "DISABLED" in a.get("status", ""))

    elif zone_id == "agent_exchange":
        ep = resolve_path("IMPERIUM_TEST_VERSION/AGENT_EXCHANGE/EXCHANGE_STATE.json")
        d, _ = load_json_safe(ep)
        if d:
            tel["exchange_state"] = d.get("status", "UNKNOWN")
        threads_dir = resolve_path("IMPERIUM_TEST_VERSION/AGENT_EXCHANGE/THREADS")
        if os.path.isdir(threads_dir):
            tel["thread_count"] = len([x for x in os.listdir(threads_dir) if os.path.isdir(os.path.join(threads_dir, x))])

    elif zone_id == "delta_verification":
        dp = resolve_path("IMPERIUM_TEST_VERSION/TESTING_FIELD/DELTA_WINDOW/REPORTS/latest_delta_report.json")
        d, _ = load_json_safe(dp)
        if d:
            tel["last_verdict"] = d.get("verdict", d.get("overall", "UNKNOWN"))

    elif zone_id == "testing_field":
        sp = resolve_path("IMPERIUM_TEST_VERSION/TESTING_FIELD/SMOKE_RESULTS/latest_smoke_report.json")
        d, _ = load_json_safe(sp)
        if d:
            tel["smoke_status"] = d.get("overall", d.get("verdict", "UNKNOWN"))

    elif zone_id == "export_bundle_gate":
        exports_dir = resolve_path("IMPERIUM_TEST_VERSION/SECOND_BRAIN/RUNTIME/exports")
        if os.path.isdir(exports_dir):
            manifests = glob.glob(os.path.join(exports_dir, "**", "manifest.json"), recursive=True)
            tel["export_count"] = len(manifests)
            tel["gate_status"] = "READY" if manifests else "NO_EXPORTS"

    elif zone_id == "feature_module_dock":
        fp = resolve_path("IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_4/registry/neural_feature_registry.json")
        d, _ = load_json_safe(fp)
        if d:
            features = d.get("features", [])
            tel["module_count"] = len(features)
            tel["working_count"] = sum(1 for f in features if f.get("status") == "WORKING")
            tel["partial_count"] = sum(1 for f in features if f.get("status") == "PARTIAL")
            tel["blocked_count"] = sum(1 for f in features if f.get("status") == "BLOCKED")

    return tel


def evaluate_zone_health(zone_id, zone_def, truth_contract):
    """Evaluate health of a zone based on its truth contract."""
    source_patterns = truth_contract.get("source_patterns", [])
    present = []
    missing = []

    for pattern in source_patterns:
        if source_exists(pattern):
            present.append(pattern)
        else:
            missing.append(pattern)

    missing_count = len(missing)
    present_count = len(present)

    # Determine health
    declared_state = zone_def.get("capability_state", "MISSING")

    if missing_count == len(source_patterns) and len(source_patterns) > 0:
        health = "MISSING"
    elif missing_count > 0:
        health = "PARTIAL"
    elif declared_state == "PARTIAL":
        health = "PARTIAL"
    elif declared_state in ("BLOCKED", "DISABLED", "EXPERIMENTAL", "TEST_ONLY"):
        health = declared_state
    else:
        health = "WORKING"

    return {
        "health": health,
        "source_present_count": present_count,
        "source_missing_count": missing_count,
        "missing_sources": missing,
        "present_sources": present
    }


def build_snapshot():
    build_started = time.perf_counter()
    print("=" * 60)
    print("Second Brain V0.5 — Snapshot Builder")
    print("=" * 60)

    # Load zone registry
    registry, err = load_json_safe(ZONE_REGISTRY)
    if err:
        print(f"[FATAL] Cannot load zone_registry_v0_5.json: {err}")
        sys.exit(1)

    zones = registry.get("zones", [])
    print(f"Zones loaded: {len(zones)}")

    # Load layout config
    layout, _ = load_json_safe(LAYOUT_CONFIG)
    layout_zones = layout.get("zones", {}) if layout else {}

    snapshot_zones = []
    total_missing = 0
    total_broken = 0
    warning_count = 0

    for zone_def in zones:
        zone_id = zone_def["zone_id"]

        # Load truth contract
        truth_path = os.path.join(TRUTH_DIR, f"zone_{zone_id}_truth.json")
        truth_contract, terr = load_json_safe(truth_path)
        if terr:
            print(f"  [WARN] No truth contract for {zone_id}: {terr}")
            truth_contract = {"source_patterns": []}
            warning_count += 1

        # Evaluate health
        health_result = evaluate_zone_health(zone_id, zone_def, truth_contract)

        # Collect telemetry
        telemetry = collect_telemetry_for_zone(zone_id, zone_def)

        # Get layout position
        layout_pos = layout_zones.get(zone_id, {"x": 50, "y": 50, "r": 28, "size": "medium", "group": "ring_1"})

        total_missing += health_result["source_missing_count"]
        if health_result["health"] in ("BLOCKED", "MISSING"):
            total_broken += 1
        if health_result["health"] == "PARTIAL":
            warning_count += 1

        zone_snapshot = {
            "zone_id": zone_id,
            "display_name": zone_def["display_name"],
            "health": health_result["health"],
            "capability_state": zone_def["capability_state"],
            "visual_token": zone_def["visual_token"],
            "source_present_count": health_result["source_present_count"],
            "source_missing_count": health_result["source_missing_count"],
            "missing_sources": health_result["missing_sources"],
            "telemetry": telemetry,
            "layout": layout_pos,
            "honest_limitations": zone_def.get("honest_limitations_display", []),
            "missing_capabilities": zone_def.get("missing_capabilities_display", []),
            "hover_summary_template": zone_def.get("hover_summary_template", ""),
            "last_evaluated": now_iso()
        }
        snapshot_zones.append(zone_snapshot)

        status_icon = "OK" if health_result["health"] == "WORKING" else ("PARTIAL" if health_result["health"] == "PARTIAL" else "FAIL")
        print(f"  [{status_icon}] {zone_id:30s} {health_result['health']}")

    # Overall health score
    working_count = sum(1 for z in snapshot_zones if z["health"] == "WORKING")
    partial_count = sum(1 for z in snapshot_zones if z["health"] == "PARTIAL")
    blocked_count = sum(1 for z in snapshot_zones if z["health"] in ("BLOCKED", "MISSING"))
    receipts_dir = resolve_path("IMPERIUM_TEST_VERSION/SECOND_BRAIN/RUNTIME/receipts")
    receipt_count = len([f for f in os.listdir(receipts_dir) if f.endswith(".json")]) if os.path.isdir(receipts_dir) else 0

    # Load strands from layout
    strands = layout.get("strands", []) if layout else []

    snapshot = {
        "snapshot_id": f"NBV05-SNAP-{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "truth_lock_run_id": f"TRUTHLOCK-{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "timestamp_utc": now_iso(),
        "schema_version": "neural_snapshot.v0.5",
        "scope_policy": "IMPERIUM_TEST_VERSION_ONLY",
        "runtime_mode": "PROTOTYPE_INTERACTIVE",
        "no_local_llm": True,
        "no_agent_api": True,
        "not_production_ready": True,
        "zone_count": len(snapshot_zones),
        "working_count": working_count,
        "partial_count": partial_count,
        "blocked_count": blocked_count,
        "total_missing_sources": total_missing,
        "missing_source_count": total_missing,
        "stale_count": 0,
        "total_broken_zones": total_broken,
        "warning_count": warning_count,
        "health_score": f"{working_count}/{len(snapshot_zones)}",
        "staleness_policy": {
            "max_snapshot_age_seconds": 900,
            "stale_warning_threshold_seconds": 300,
            "stale_failure_threshold_seconds": 900,
        },
        "telemetry": {
            "snapshot_age_seconds": 0,
            "api_latency_ms_by_endpoint": "NOT_IMPLEMENTED",
            "failed_api_count": "NOT_IMPLEMENTED",
            "last_snapshot_build_time_ms": None,
            "zone_render_count": len(snapshot_zones),
            "missing_source_count": total_missing,
            "stale_source_count": 0,
            "receipt_count": receipt_count,
            "latest_receipt_age_seconds": "NOT_IMPLEMENTED",
            "action_failure_count": "NOT_IMPLEMENTED",
            "console_error_count": "NOT_IMPLEMENTED",
            "network_error_count": "NOT_IMPLEMENTED",
            "browser_test_passed": "NOT_IMPLEMENTED",
            "checker_passed": "NOT_IMPLEMENTED",
            "parity_verdict": "NOT_IMPLEMENTED",
            "page_load_ms": "NOT_IMPLEMENTED",
        },
        "zones": snapshot_zones,
        "strands": strands
    }
    snapshot["telemetry"]["last_snapshot_build_time_ms"] = round((time.perf_counter() - build_started) * 1000.0, 2)

    with open(SNAPSHOT_OUT, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)

    print()
    print(f"Health score:    {working_count}/{len(snapshot_zones)} zones WORKING")
    print(f"Partial:         {partial_count}")
    print(f"Blocked/Missing: {blocked_count}")
    print(f"Warnings:        {warning_count}")
    print(f"Snapshot written: {SNAPSHOT_OUT}")
    print()
    print("NOT PRODUCTION READY | PROTOTYPE_INTERACTIVE | RULE_BASED_ONLY")

    return snapshot


if __name__ == "__main__":
    build_snapshot()
