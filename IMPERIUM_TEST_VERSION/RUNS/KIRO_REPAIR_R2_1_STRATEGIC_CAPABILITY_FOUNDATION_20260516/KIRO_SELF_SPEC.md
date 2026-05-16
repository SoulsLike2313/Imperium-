# KIRO SELF-SPEC: REPAIR R2.1 + STRATEGIC CAPABILITY FOUNDATION

**Task ID:** KIRO_REPAIR_R2_1_STRATEGIC_CAPABILITY_FOUNDATION_20260516  
**Author:** Kiro  
**Created:** 2026-05-16  
**Baseline HEAD:** `9a7f4dabe9fff71c6722df0293855f18306c4106`

---

## Objective

1. **Repair incomplete R2 outputs** — create missing Agent Exchange Window, Owner guides, response bundles, and self-audit from previous task.
2. **Build strategic capability foundation** — create specs, schemas, and minimal working prototypes for six Owner strategic requirements:
   - Freelance task execution corridor
   - Presentation/product summary system
   - Distributed two-contour (PC + Ubuntu laptop) architecture
   - Second Brain memory zones
   - CLI agent port for Servitor/Codex
   - Local LLM port foundation
3. **Enforce verdict discipline** — separate scope-safe from quality-green, never fake green.

---

## Non-Goals

- Do NOT touch main canon outside IMPERIUM_TEST_VERSION
- Do NOT commit or push
- Do NOT fake external integrations (SSH, local LLM, Codex)
- Do NOT create decorative dashboards that don't read real files
- Do NOT use Cyrillic in canonical/internal JSON/schema/protocol files
- Do NOT claim PASS without evidence

---

## Current Blockers

| Blocker | Status | Resolution |
|---------|--------|------------|
| Missing agent_exchange_window.html | REPAIR_REQUIRED | Create in Phase 3 |
| Missing OWNER_USAGE_GUIDE_RU.md | REPAIR_REQUIRED | Create in Phase 3 |
| Missing KIRO_RESPONSE_BUNDLE | REPAIR_REQUIRED | Create in Phase 3 |
| Missing self-audit folder | REPAIR_REQUIRED | Create in Phase 3 |
| Truth state FAIL in previous run | REPAIR_REQUIRED | Fix underlying issues |
| Strategic capabilities not started | NOT_STARTED | Create in Phase 4-8 |

---

## Target Files

### Phase 3 — R2 Repair

| File | Purpose |
|------|---------|
| `AGENT_EXCHANGE/agent_exchange_window.html` | Interactive operator window |
| `RUNS/KIRO_DELTA_R2_AGENT_EXCHANGE_WINDOW_R1_20260516/OWNER_USAGE_GUIDE_RU.md` | Russian Owner guide |
| `AGENT_EXCHANGE/OUTBOX/KIRO/KIRO_RESPONSE_BUNDLE_DELTA_R2_AGENT_EXCHANGE_R1_20260516.md` | Response bundle |
| `AUDITS/KIRO_SELF_AUDIT_DELTA_R2_AGENT_EXCHANGE_R1_20260516/*` | Self-audit package |

### Phase 4 — Strategic Capabilities

| Directory | Contents |
|-----------|----------|
| `STRATEGIC_CAPABILITIES/FREELANCE_EXECUTION/` | Spec, schema, samples |
| `STRATEGIC_CAPABILITIES/PRESENTATION_SYSTEM/` | Spec, schema, self-summary |
| `STRATEGIC_CAPABILITIES/DISTRIBUTED_CONTOURS/` | Spec, schema, SSH check script |
| `STRATEGIC_CAPABILITIES/SECOND_BRAIN/` | Spec, schema, sample zones |
| `STRATEGIC_CAPABILITIES/CLI_AGENT_PORT/` | Spec, schema, working CLI |
| `STRATEGIC_CAPABILITIES/LOCAL_LLM_PORT/` | Spec, schema, health check |

### Phase 8 — Interactive Summary

| File | Purpose |
|------|---------|
| `STRATEGIC_CAPABILITIES/strategic_capability_window.html` | Capability dashboard |

### Phase 9 — Verification

| File | Purpose |
|------|---------|
| `TOOLS/check_strategic_capability_foundation.py` | Automated checker |

---

## PASS Criteria

1. All required outputs from Phase 3 exist and are non-empty
2. All strategic capability directories exist with required files
3. `imperium_cli_agent_port.py --mode health` returns valid JSON
4. `imperium_cli_agent_port.py --mode summarize --input sample_request.json` returns valid JSON
5. `local_llm_health_check.py` returns honest NOT_CONFIGURED/NOT_INSTALLED/PASS
6. `ssh_capability_check.ps1` returns MANUAL_CONFIRMATION_REQUIRED when no credentials
7. `check_strategic_capability_foundation.py` passes all checks
8. Delta Window STANDARD completes without truth FAIL
9. All canonical/internal files are English-only
10. No main canon touched
11. Owner guides exist in Russian
12. Self-audit exists with honest verdicts

---

## FAIL Criteria

1. Any required output missing
2. CLI agent port crashes or returns invalid JSON
3. Local LLM health check fakes availability
4. SSH check claims success without verification
5. Cyrillic in canonical JSON/schema files
6. Main canon touched
7. Fake green verdict
8. Missing evidence for any PASS claim

---

## Evidence Requirements

| Evidence | Location |
|----------|----------|
| Intake report | `RUNS/.../INTAKE_REPORT.md` |
| Self-spec | `RUNS/.../KIRO_SELF_SPEC.md` |
| Pass/fail gates | `RUNS/.../PASS_FAIL_GATES.json` |
| CLI health output | `RUNS/.../CLI_HEALTH_OUTPUT.json` |
| CLI summarize output | `RUNS/.../CLI_SUMMARIZE_OUTPUT.json` |
| LLM health output | `RUNS/.../LLM_HEALTH_OUTPUT.json` |
| SSH check output | `RUNS/.../SSH_CHECK_OUTPUT.txt` |
| Strategic check report | `RUNS/.../STRATEGIC_CAPABILITY_CHECK_REPORT.json` |
| Delta STANDARD report | `TESTING_FIELD/DELTA_WINDOW/REPORTS/` |
| Self-audit | `AUDITS/.../` |

---

## Manual Confirmation Required

| Item | Reason |
|------|--------|
| SSH to Ubuntu laptop | No credentials provided, cannot test |
| Local LLM availability | No model installed/configured |
| Real Codex/Servitor integration | Not wired, only contract defined |
| Real freelance task execution | Only spec/sample, not executable |
| Real memory zone data | Only synthetic samples |

---

## What Can Be Implemented Now

1. ✅ Agent Exchange Window HTML (reads real files)
2. ✅ Owner guides in Russian
3. ✅ Response bundles
4. ✅ Self-audit packages
5. ✅ All specs and schemas
6. ✅ CLI agent port with health/summarize/inspect commands
7. ✅ Local LLM health check (honest NOT_CONFIGURED)
8. ✅ SSH capability check (honest MANUAL_CONFIRMATION_REQUIRED)
9. ✅ Strategic capability window HTML
10. ✅ Verification script

---

## What Must Remain Backlog

1. ❌ Real SSH execution to Ubuntu laptop
2. ❌ Real local LLM inference
3. ❌ Real Codex/Servitor agent integration
4. ❌ Real freelance task execution
5. ❌ Real private memory zone data ingestion

---

## Fake Green Prevention

1. Every PASS claim must have evidence file
2. External integrations marked MANUAL_CONFIRMATION_REQUIRED
3. Separate verdicts: scope_safe, quality_green, owner_ready, promotion_ready
4. Check scripts verify real file existence, not invented status
5. HTML dashboards read real files, not hardcoded status
6. Final verdict cannot be green if any required output missing

---

## Scope-Safe vs Quality-Green Separation

| Concept | Meaning |
|---------|---------|
| `scope_safe_to_commit` | No main canon touched, only test version modified |
| `quality_green` | All checks pass, all outputs exist, no fake green |
| `owner_ready_for_manual_review` | Owner can inspect and verify |
| `ready_for_promotion_to_main_canon` | Quality green + Owner approved + Servitor audited |

---

## Canonical Files Language Policy

| File Type | Language |
|-----------|----------|
| JSON schemas | English |
| JSON configs | English |
| Protocol definitions | English |
| State files | English |
| Specs | English |
| README files | English |
| Owner guides (*_RU.md) | Russian allowed |
| Self-summary (*_RU.md) | Russian allowed |
| Chat responses to Owner | Russian |

---

## How Owner Should Use the Result

1. Open `STRATEGIC_CAPABILITIES/strategic_capability_window.html` in browser
2. Open `AGENT_EXCHANGE/agent_exchange_window.html` in browser
3. Open `TESTING_FIELD/DELTA_WINDOW/delta_window.html` in browser
4. Read `RUNS/.../OWNER_FINAL_REPORT_RU.md`
5. Follow `RUNS/.../MANUAL_VERIFICATION_CHECKLIST_RU.md`
6. Run CLI commands manually to verify:
   - `python STRATEGIC_CAPABILITIES/CLI_AGENT_PORT/imperium_cli_agent_port.py --mode health`
   - `python STRATEGIC_CAPABILITIES/LOCAL_LLM_PORT/local_llm_health_check.py`
7. Review self-audit in `AUDITS/.../`
8. Decide whether to commit test version changes
