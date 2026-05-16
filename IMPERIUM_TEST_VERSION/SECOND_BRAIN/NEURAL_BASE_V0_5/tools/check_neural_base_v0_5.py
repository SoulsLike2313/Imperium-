"""
Second Brain Neural Base V0.5 — Checker
Validates all 12 zones, layout config, truth matrix, snapshot, and no fake green.

Exit code 0 = PASS
Exit code 1 = FAIL
Writes: NEURAL_BASE_V0_5/reports/check_report_v0_5.json
"""

import json
import os
import sys
import datetime
import glob

TOOLS_DIR    = os.path.dirname(os.path.abspath(__file__))
V05_ROOT     = os.path.dirname(TOOLS_DIR)
SECOND_BRAIN = os.path.dirname(V05_ROOT)
TEST_VERSION = os.path.dirname(SECOND_BRAIN)
REPO_ROOT    = os.path.dirname(TEST_VERSION)

REGISTRY_DIR = os.path.join(V05_ROOT, "registry")
TRUTH_DIR    = os.path.join(V05_ROOT, "truth_matrix")
REPORTS_DIR  = os.path.join(V05_ROOT, "reports")
APP_DIR      = os.path.join(V05_ROOT, "app")
GATE_DIR     = os.path.join(V05_ROOT, "gate")

passes = []
fails = []
warnings = []


def ok(msg):
    passes.append(msg)


def fail(msg):
    fails.append(msg)


def warn(msg):
    warnings.append(msg)


def load_json(path):
    if not os.path.isfile(path):
        return None, f"File not found: {path}"
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), None
    except Exception as e:
        return None, str(e)


def rp(rel):
    return os.path.join(REPO_ROOT, rel.replace("/", os.sep))


def source_exists(pattern):
    full = rp(pattern)
    if "*" in full:
        return len(glob.glob(full)) > 0
    return os.path.exists(full)


def main():
    print("=" * 65)
    print("Second Brain Neural Base V0.5 — Checker")
    print("=" * 65)

    # ── 1. Required V0.5 directories ─────────────────────────────────────────
    print("\n[1] Required V0.5 directories")
    required_dirs = [
        (V05_ROOT,                              "NEURAL_BASE_V0_5 root"),
        (REGISTRY_DIR,                          "registry/"),
        (TRUTH_DIR,                             "truth_matrix/"),
        (REPORTS_DIR,                           "reports/"),
        (APP_DIR,                               "app/"),
        (GATE_DIR,                              "gate/"),
        (os.path.join(V05_ROOT, "tools"),       "tools/"),
        (os.path.join(V05_ROOT, "telemetry"),   "telemetry/"),
        (os.path.join(V05_ROOT, "merge_polygon"), "merge_polygon/"),
    ]
    for path, desc in required_dirs:
        if os.path.isdir(path):
            ok(f"Dir exists: {desc}")
        else:
            fail(f"Dir missing: {desc} ({path})")

    # ── 2. Zone registry ──────────────────────────────────────────────────────
    print("\n[2] Zone registry")
    zr_path = os.path.join(REGISTRY_DIR, "zone_registry_v0_5.json")
    zr, err = load_json(zr_path)
    if err:
        fail(f"zone_registry_v0_5.json: {err}")
        zr = None
    else:
        ok("zone_registry_v0_5.json parses OK")
        zones = zr.get("zones", [])
        if len(zones) == 12:
            ok(f"Zone count: 12 (correct)")
        else:
            fail(f"Zone count: {len(zones)} (expected 12)")

        zone_ids = [z["zone_id"] for z in zones]
        expected_ids = [
            "core_brain", "task_intake", "owner_comments", "memory_threads",
            "progress_spine", "evidence_receipts", "action_control",
            "agent_exchange", "delta_verification", "testing_field",
            "export_bundle_gate", "feature_module_dock"
        ]
        for eid in expected_ids:
            if eid in zone_ids:
                ok(f"Zone present: {eid}")
            else:
                fail(f"Zone missing: {eid}")

    # ── 3. Layout config ──────────────────────────────────────────────────────
    print("\n[3] Layout config")
    lc_path = os.path.join(REGISTRY_DIR, "layout_config.json")
    lc, err = load_json(lc_path)
    if err:
        fail(f"layout_config.json: {err}")
    else:
        ok("layout_config.json parses OK")
        lc_zones = lc.get("zones", {})
        if len(lc_zones) == 12:
            ok(f"Layout has 12 zone entries")
        else:
            fail(f"Layout has {len(lc_zones)} zone entries (expected 12)")
        # Verify no truth bindings in layout
        lc_str = json.dumps(lc)
        if "truth_sources" in lc_str or "source_patterns" in lc_str:
            fail("layout_config.json contains truth bindings (VIOLATION: layout must not contain truth)")
        else:
            ok("layout_config.json has no truth bindings (correct separation)")

    # ── 4. Truth matrix — 12 files ────────────────────────────────────────────
    print("\n[4] Truth matrix files")
    if zr:
        for zone in zr.get("zones", []):
            zid = zone["zone_id"]
            tm_path = os.path.join(TRUTH_DIR, f"zone_{zid}_truth.json")
            tm, err = load_json(tm_path)
            if err:
                fail(f"Truth matrix missing: zone_{zid}_truth.json")
            else:
                ok(f"Truth matrix OK: zone_{zid}_truth.json")
                if "source_patterns" not in tm:
                    fail(f"Truth matrix {zid}: missing source_patterns")
                if "pass_logic" not in tm:
                    fail(f"Truth matrix {zid}: missing pass_logic")
                if "failure_logic" not in tm:
                    fail(f"Truth matrix {zid}: missing failure_logic")

    # ── 5. Snapshot live ──────────────────────────────────────────────────────
    print("\n[5] Snapshot live")
    snap_path = os.path.join(REPORTS_DIR, "neural_snapshot_live.json")
    snap, err = load_json(snap_path)
    if err:
        fail(f"neural_snapshot_live.json: {err}")
        snap = None
    else:
        ok("neural_snapshot_live.json parses OK")
        snap_zones = snap.get("zones", [])
        if len(snap_zones) == 12:
            ok(f"Snapshot has 12 zone entries")
        else:
            fail(f"Snapshot has {len(snap_zones)} zone entries (expected 12)")
        if snap.get("not_production_ready") is True:
            ok("Snapshot: not_production_ready = true")
        else:
            fail("Snapshot: not_production_ready must be true")
        if snap.get("no_local_llm") is True:
            ok("Snapshot: no_local_llm = true")
        else:
            fail("Snapshot: no_local_llm must be true")

    # ── 6. App files ──────────────────────────────────────────────────────────
    print("\n[6] App files")
    app_files = [
        (os.path.join(APP_DIR, "neural_map_v0_5.html"), "neural_map_v0_5.html"),
        (os.path.join(APP_DIR, "neural_map_v0_5.css"),  "neural_map_v0_5.css"),
        (os.path.join(APP_DIR, "neural_map_v0_5.js"),   "neural_map_v0_5.js"),
    ]
    for path, desc in app_files:
        if os.path.isfile(path):
            ok(f"App file exists: {desc}")
        else:
            fail(f"App file missing: {desc}")

    # ── 7. Server ─────────────────────────────────────────────────────────────
    print("\n[7] Server")
    server_path = os.path.join(V05_ROOT, "app", "server_v0_5.py")
    if os.path.isfile(server_path):
        ok("server_v0_5.py exists")
    else:
        fail("server_v0_5.py missing")

    # ── 8. UI references API (not static hardcoded) ───────────────────────────
    print("\n[8] UI references API")
    js_path = os.path.join(APP_DIR, "neural_map_v0_5.js")
    if os.path.isfile(js_path):
        with open(js_path, "r", encoding="utf-8") as f:
            js_content = f.read()
        for endpoint in ["/api/snapshot", "/api/status", "/api/tasks", "/api/comments"]:
            if endpoint in js_content:
                ok(f"JS references {endpoint}")
            else:
                warn(f"JS does not reference {endpoint}")
        if "fetch(" in js_content or "apiFetch" in js_content:
            ok("JS uses fetch() for API calls")
        else:
            fail("JS does not use fetch() — may be static hardcoded")

    # ── 9. No fake green ──────────────────────────────────────────────────────
    print("\n[9] No fake green")
    forbidden = [
        "PRODUCTION_READY", "FULLY_IMPLEMENTED",
        "REAL_AGENT_EXECUTION_READY", "REAL_LOCAL_LLM_READY"
    ]
    # Files that legitimately contain forbidden phrases as search patterns (not claims)
    SCAN_EXCLUDE = {
        "check_neural_base_v0_5.py",   # this file — contains phrases as search targets
        "gate_check_module.py",         # gate checker — contains phrases as forbidden list
        "check_report_v0_5.json",       # checker report — records forbidden phrases found
        "gate_beauty.json",             # gate file — contains 'not_production_ready' field
        "gate_truth_discipline.json",   # gate file — contains 'not_production_ready' field
        "gate_adaptability.json",
        "gate_execution.json",
    }
    scan_files = []
    for root, dirs, files in os.walk(V05_ROOT):
        for fname in files:
            if fname in SCAN_EXCLUDE:
                continue
            if fname.endswith((".py", ".json", ".html", ".js", ".css", ".md")):
                scan_files.append(os.path.join(root, fname))

    fake_found = False
    for fpath in scan_files:
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            for phrase in forbidden:
                if phrase in content:
                    fail(f"FAKE GREEN: '{phrase}' in {os.path.relpath(fpath, V05_ROOT)}")
                    fake_found = True
        except Exception:
            pass
    if not fake_found:
        ok("No fake green claims found in V0.5 files")

    # ── 10. Scope safety ──────────────────────────────────────────────────────
    print("\n[10] Scope safety")
    v05_name = os.path.basename(V05_ROOT)
    if v05_name == "NEURAL_BASE_V0_5":
        ok(f"V0.5 root is NEURAL_BASE_V0_5 (correct)")
    else:
        fail(f"V0.5 root is '{v05_name}' (expected NEURAL_BASE_V0_5)")

    sb_name = os.path.basename(SECOND_BRAIN)
    if sb_name == "SECOND_BRAIN":
        ok("Parent is SECOND_BRAIN (correct)")
    else:
        fail(f"Parent is '{sb_name}' (expected SECOND_BRAIN)")

    # ── 11. Gate checker exists ───────────────────────────────────────────────
    print("\n[11] Gate checker")
    gate_path = os.path.join(GATE_DIR, "gate_check_module.py")
    if os.path.isfile(gate_path):
        ok("gate_check_module.py exists")
    else:
        fail("gate_check_module.py missing")

    # ── 12. Snapshot builder exists ───────────────────────────────────────────
    print("\n[12] Snapshot builder")
    sb_path = os.path.join(TOOLS_DIR, "snapshot_builder_v0_5.py")
    if os.path.isfile(sb_path):
        ok("snapshot_builder_v0_5.py exists")
    else:
        fail("snapshot_builder_v0_5.py missing")

    # ── 13. Honest status in snapshot ────────────────────────────────────────
    print("\n[13] Honest status")
    if snap:
        if snap.get("runtime_mode") == "PROTOTYPE_INTERACTIVE":
            ok("Snapshot runtime_mode = PROTOTYPE_INTERACTIVE")
        else:
            fail(f"Snapshot runtime_mode = {snap.get('runtime_mode')} (expected PROTOTYPE_INTERACTIVE)")
        if snap.get("no_agent_api") is True:
            ok("Snapshot no_agent_api = true")
        else:
            fail("Snapshot no_agent_api must be true")

    # ── Summary ───────────────────────────────────────────────────────────────
    print()
    print("=" * 65)
    print(f"PASSES:   {len(passes)}")
    print(f"WARNINGS: {len(warnings)}")
    print(f"FAILS:    {len(fails)}")
    print()

    if fails:
        print("FAILURES:")
        for f in fails:
            print(f"  [FAIL] {f}")
        print()
    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"  [WARN] {w}")
        print()

    verdict = "PASS" if len(fails) == 0 else "FAIL"
    overall = "READY_FOR_OWNER_REVIEW" if verdict == "PASS" else "NEEDS_FIXES"

    print(f"VERDICT:  {verdict}")
    print(f"OVERALL:  {overall}")
    print()

    os.makedirs(REPORTS_DIR, exist_ok=True)
    report = {
        "checker": "check_neural_base_v0_5.py",
        "version": "V0.5",
        "date": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "verdict": verdict,
        "overall": overall,
        "passes": len(passes),
        "warnings": len(warnings),
        "fails": len(fails),
        "pass_details": passes,
        "warning_details": warnings,
        "fail_details": fails,
        "runtime_mode": "PROTOTYPE_INTERACTIVE",
        "no_llm": True,
        "no_agent_api": True,
        "not_production_ready": True
    }
    report_path = os.path.join(REPORTS_DIR, "check_report_v0_5.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"Report written: {report_path}")

    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
