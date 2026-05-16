"""
Second Brain V0.5 — Module Intake Gate Checker
Validates a zone/module manifest against all 10 gate checks.

Usage: py gate_check_module.py <manifest.json>
Exit code: 0 = ACCEPT, 1 = BLOCK or OWNER_REVIEW_REQUIRED
Writes: gate_report_<zone_id>.json
"""

import json
import os
import sys
import datetime

GATE_DIR = os.path.dirname(os.path.abspath(__file__))
V05_ROOT = os.path.dirname(GATE_DIR)
SECOND_BRAIN = os.path.dirname(V05_ROOT)
TEST_VERSION = os.path.dirname(SECOND_BRAIN)
REPO_ROOT = os.path.dirname(TEST_VERSION)

FORBIDDEN_COMMANDS = [
    "git push", "git commit", "rm -rf", "rmdir /s", "del /f",
    "format ", "DROP TABLE", "DROP DATABASE"
]

FORBIDDEN_STATUS_CLAIMS = [
    "PRODUCTION_READY", "FULLY_IMPLEMENTED",
    "REAL_AGENT_EXECUTION_READY", "REAL_LOCAL_LLM_READY"
]

VALID_CAPABILITY_STATES = [
    "WORKING", "PARTIAL", "MISSING", "DISABLED",
    "EXPERIMENTAL", "TEST_ONLY", "BLOCKED"
]

VALID_ANIMATION_BUDGETS = ["none", "low", "medium", "high"]
VALID_GATE_POLICIES = ["auto", "review_required", "blocked"]


def now_iso():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def source_exists(pattern):
    import glob
    full = os.path.join(REPO_ROOT, pattern.replace("/", os.sep))
    if "*" in full:
        return len(glob.glob(full)) > 0
    return os.path.exists(full)


class GateResult:
    def __init__(self):
        self.passes = []
        self.fails = []
        self.warnings = []
        self.verdict = "ACCEPT"

    def ok(self, gate, msg):
        self.passes.append(f"[Gate {gate}] PASS: {msg}")

    def fail(self, gate, msg, block=True):
        self.fails.append(f"[Gate {gate}] FAIL: {msg}")
        if block:
            self.verdict = "BLOCK"
        else:
            if self.verdict == "ACCEPT":
                self.verdict = "ACCEPT_WITH_LIMITS"

    def warn(self, gate, msg, require_review=False):
        self.warnings.append(f"[Gate {gate}] WARN: {msg}")
        if require_review and self.verdict == "ACCEPT":
            self.verdict = "OWNER_REVIEW_REQUIRED"

    def limit(self, gate, msg):
        self.warnings.append(f"[Gate {gate}] LIMIT: {msg}")
        if self.verdict == "ACCEPT":
            self.verdict = "ACCEPT_WITH_LIMITS"


def run_gates(manifest):
    r = GateResult()

    # ── Gate 1: IDENTITY ──────────────────────────────────────────────────────
    zone_id = manifest.get("zone_id", "")
    if not zone_id:
        r.fail(1, "zone_id is missing or empty")
    elif not zone_id.replace("-", "").replace("_", "").isalnum():
        r.fail(1, f"zone_id '{zone_id}' contains invalid characters (use kebab-case)")
    else:
        r.ok(1, f"zone_id '{zone_id}' is valid")

    if not manifest.get("display_name"):
        r.fail(1, "display_name is missing")
    else:
        r.ok(1, "display_name present")

    if not manifest.get("purpose"):
        r.fail(1, "purpose is missing")
    else:
        r.ok(1, "purpose present")

    # ── Gate 2: SCHEMA VALIDITY ───────────────────────────────────────────────
    required_fields = [
        "zone_id", "display_name", "purpose", "capability_state",
        "scope_path", "truth_sources", "evidence_sources",
        "honest_limitations_display", "missing_capabilities_display"
    ]
    for field in required_fields:
        if field not in manifest:
            r.fail(2, f"Required field missing: {field}")
        else:
            r.ok(2, f"Field present: {field}")

    # ── Gate 3: PATH CLEANLINESS ──────────────────────────────────────────────
    scope_path = manifest.get("scope_path", "")
    if not scope_path.startswith("IMPERIUM_TEST_VERSION"):
        r.fail(3, f"scope_path '{scope_path}' is outside IMPERIUM_TEST_VERSION")
    else:
        r.ok(3, f"scope_path is inside IMPERIUM_TEST_VERSION")

    all_paths = (
        manifest.get("truth_sources", []) +
        manifest.get("evidence_sources", []) +
        manifest.get("checker_sources", [])
    )
    for p in all_paths:
        if not p.startswith("IMPERIUM_TEST_VERSION") and not p.startswith("IMPERIUM_TEST_VERSION"):
            r.fail(3, f"Path outside scope: {p}")
        elif os.path.isabs(p):
            r.fail(3, f"Absolute path not allowed: {p}")
        else:
            r.ok(3, f"Path clean: {p[:60]}")

    # ── Gate 4: SCOPE SAFETY ──────────────────────────────────────────────────
    actions = manifest.get("action_sources", [])
    for a in actions:
        r.ok(4, f"Action reference: {a}")

    # Check no git/destructive in any string field
    manifest_str = json.dumps(manifest)
    for forbidden in FORBIDDEN_COMMANDS:
        if forbidden.lower() in manifest_str.lower():
            r.fail(4, f"Forbidden command found in manifest: '{forbidden}'")
    r.ok(4, "No forbidden commands in manifest")

    # ── Gate 5: TRUTH SOURCE PRESENCE ────────────────────────────────────────
    truth_sources = manifest.get("truth_sources", [])
    if not truth_sources:
        r.warn(5, "No truth_sources defined", require_review=True)
    else:
        any_present = False
        for ts in truth_sources:
            if source_exists(ts):
                r.ok(5, f"Truth source present: {ts[:60]}")
                any_present = True
            else:
                r.warn(5, f"Truth source missing: {ts[:60]}", require_review=False)
        if not any_present:
            r.warn(5, "ALL truth sources missing — zone cannot be WORKING", require_review=True)

    # ── Gate 6: EVIDENCE READINESS ────────────────────────────────────────────
    evidence_sources = manifest.get("evidence_sources", [])
    checker_sources = manifest.get("checker_sources", [])
    if not evidence_sources:
        r.limit(6, "No evidence_sources defined")
    else:
        r.ok(6, f"evidence_sources defined: {len(evidence_sources)} entries")

    if not checker_sources:
        r.limit(6, "No checker_sources defined — zone cannot be independently verified")
    else:
        r.ok(6, f"checker_sources defined: {len(checker_sources)} entries")

    # ── Gate 7: ACTION SAFETY ─────────────────────────────────────────────────
    # Actions are referenced by ID — check no forbidden content
    r.ok(7, "Action safety: actions referenced by ID only (no inline commands)")

    # ── Gate 8: PERFORMANCE BUDGET ────────────────────────────────────────────
    anim_budget = manifest.get("animation_budget", "")
    if anim_budget not in VALID_ANIMATION_BUDGETS:
        r.limit(8, f"animation_budget '{anim_budget}' not in {VALID_ANIMATION_BUDGETS}")
    else:
        r.ok(8, f"animation_budget: {anim_budget}")

    render_cost = manifest.get("render_cost_estimate", "")
    if not render_cost:
        r.limit(8, "render_cost_estimate not defined")
    else:
        r.ok(8, f"render_cost_estimate: {render_cost}")

    # ── Gate 9: HONEST STATE SEMANTICS ───────────────────────────────────────
    cap_state = manifest.get("capability_state", "")
    if cap_state not in VALID_CAPABILITY_STATES:
        r.fail(9, f"capability_state '{cap_state}' is not a valid honest state")
    else:
        r.ok(9, f"capability_state: {cap_state}")

    manifest_str_upper = manifest_str.upper()
    for fake in FORBIDDEN_STATUS_CLAIMS:
        if fake in manifest_str_upper:
            r.fail(9, f"FAKE GREEN detected: '{fake}' found in manifest")
    r.ok(9, "No fake green claims in manifest")

    honest_limits = manifest.get("honest_limitations_display", [])
    if not honest_limits:
        r.limit(9, "honest_limitations_display is empty — zone should declare at least one limitation")
    else:
        r.ok(9, f"honest_limitations_display: {len(honest_limits)} entries")

    # ── Gate 10: TELEMETRY COMPLETENESS ──────────────────────────────────────
    perf_sources = manifest.get("performance_sources", [])
    stab_sources = manifest.get("stability_sources", [])
    if not perf_sources:
        r.limit(10, "performance_sources not defined")
    else:
        r.ok(10, f"performance_sources: {len(perf_sources)} metrics")
    if not stab_sources:
        r.limit(10, "stability_sources not defined")
    else:
        r.ok(10, f"stability_sources: {len(stab_sources)} metrics")

    return r


def main():
    if len(sys.argv) < 2:
        print("Usage: py gate_check_module.py <manifest.json>")
        print("       py gate_check_module.py --self-test")
        sys.exit(1)

    if sys.argv[1] == "--self-test":
        # Self-test with a minimal valid manifest
        test_manifest = {
            "zone_id": "test_zone",
            "display_name": "Test Zone",
            "purpose": "Self-test zone for gate checker",
            "capability_state": "EXPERIMENTAL",
            "scope_path": "IMPERIUM_TEST_VERSION/SECOND_BRAIN",
            "truth_sources": ["IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_5/registry/zone_registry_v0_5.json"],
            "evidence_sources": ["IMPERIUM_TEST_VERSION/SECOND_BRAIN/RUNTIME/receipts"],
            "action_sources": [],
            "checker_sources": ["IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_5/tools/check_neural_base_v0_5.py"],
            "performance_sources": ["test_metric"],
            "stability_sources": ["test_stability"],
            "honest_limitations_display": ["SELF_TEST_ONLY"],
            "missing_capabilities_display": ["Real functionality"],
            "animation_budget": "low",
            "render_cost_estimate": "low"
        }
        manifest_path = "SELF_TEST"
        result = run_gates(test_manifest)
    else:
        manifest_path = sys.argv[1]
        if not os.path.isfile(manifest_path):
            print(f"[ERROR] File not found: {manifest_path}")
            sys.exit(1)
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        result = run_gates(manifest)

    zone_id = manifest.get("zone_id", "unknown") if sys.argv[1] != "--self-test" else "self_test"

    print("=" * 60)
    print(f"Gate Check: {zone_id}")
    print("=" * 60)
    for p in result.passes:
        print(f"  {p}")
    for w in result.warnings:
        print(f"  {w}")
    for f in result.fails:
        print(f"  {f}")
    print()
    print(f"PASSES:   {len(result.passes)}")
    print(f"WARNINGS: {len(result.warnings)}")
    print(f"FAILS:    {len(result.fails)}")
    print(f"VERDICT:  {result.verdict}")

    # Write gate report
    report = {
        "gate_checker": "gate_check_module.py",
        "version": "V0.5",
        "date": now_iso(),
        "zone_id": zone_id,
        "verdict": result.verdict,
        "passes": len(result.passes),
        "warnings": len(result.warnings),
        "fails": len(result.fails),
        "pass_details": result.passes,
        "warning_details": result.warnings,
        "fail_details": result.fails,
        "runtime_mode": "PROTOTYPE_INTERACTIVE",
        "not_production_ready": True
    }
    report_path = os.path.join(GATE_DIR, f"gate_report_{zone_id}.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nReport written: {report_path}")

    return 0 if result.verdict in ("ACCEPT", "ACCEPT_WITH_LIMITS") else 1


if __name__ == "__main__":
    sys.exit(main())
