# KIRO PRACTICAL RECOMMENDATIONS — FOUNDATIONAL ORGANS V1

---

## 0. HTTP Git Verification

| Check | Result |
|-------|--------|
| Exact tree URL | GitHub tree page returned extraction error, but raw content accessible |
| Primary matrix file | **SUCCESS** — `FULL_QUESTIONNAIRE_PREFILL_MATRIX_RU_OWNER_APPROVED_V0_1.md` fully read (31,594 bytes) |
| Commit hash match | Verified via raw URL path: `931940980288cd42ece295d1107633d1fc55abf2` |
| Files read | Matrix file ✓, schema_registry.json ✓, local workspace schemas ✓, organ folder structure ✓ |
| **Verdict** | **PROCEED** — Primary matrix and supporting context successfully retrieved |

---

## 1. Executive Recommendation

**Build backend truth contracts first, dashboards second.**

The Owner matrix is comprehensive and well-structured. The main risk is attempting to build beautiful dashboards before the backend evidence/receipt/report contracts are stable. This will create fake green or constant rework.

**Recommended execution order:**
1. **Schema layer** — finalize V1 minimum schemas for all four organs (2-3 stages)
2. **Backend truth layer** — self-reports, receipts, evidence files working (4 stages)
3. **Cross-organ corridor** — prove TASK_ID flows through all four organs (2 stages)
4. **Dashboard data adapters** — JSON files that dashboards read (2 stages)
5. **Dashboard UI** — visual layer reads real data (4 stages)
6. **Sanctum aggregation** — unified view (2 stages)
7. **E2E proof + bundle** — synthetic task proves corridor (1-2 stages)

**Total recommended: 17-19 stages across 5-6 Local Tasks.**

---

## 2. Practical Implementation Strategy

### 2.1 Order of Work

| Phase | What | Why First |
|-------|------|-----------|
| 1 | Cross-organ schemas + self-report contract | Everything else depends on stable data shapes |
| 2 | Doctrinarium gates (organ health, task-start) | Must block bad starts before corridor runs |
| 3 | Administratum work packet + route sheet | Central execution truth needed for all tracking |
| 4 | Astronomicon stage map + registration | Task memory needed before stages execute |
| 5 | Officio Agentis role contracts + read receipts | Proves agent operates under correct laws |
| 6 | Dashboard data files (per-organ) | Decouples UI from backend; UI reads JSON |
| 7 | Dashboard UI (per-organ) | Visual layer last, reads stable data |
| 8 | Sanctum aggregation | Aggregates after organs have stable ports |

### 2.2 Avoiding Blocker Cascades

| Risk | Mitigation |
|------|------------|
| Schema changes mid-task | Freeze V1 schemas before stage execution begins |
| Dashboard blocks on missing backend | Build dashboard data adapters as intermediate layer |
| Cross-organ dependency loops | Use file-based reports, not runtime calls |
| Fake green from mock data | Every dashboard field must have `evidence_path` |
| Scope creep | Strict V1/V1.1 split enforced per stage |

### 2.3 Critical Path

```
Schemas → Doctrinarium gates → Administratum work packet → 
Astronomicon stage map → Officio role contracts → 
Dashboard data files → Dashboard UI → Sanctum → E2E proof
```

Do not parallelize dashboard UI with schema work. Sequential is safer.

---

## 3. Recommended General Task → Local Tasks → Stages Shape

### 3.1 One General Task

**TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING**

### 3.2 Recommended Local Tasks (6)

| Local Task | Scope | Est. Stages |
|------------|-------|-------------|
| LT-01: Schema Finalization | Freeze V1 schemas for all four organs + cross-organ | 2-3 |
| LT-02: Backend Truth Layer | Self-reports, receipts, evidence files for all four | 4 |
| LT-03: Task Corridor Wiring | Doctrinarium→Admin→Officio→Astro flow | 3 |
| LT-04: Dashboard Data Adapters | Per-organ dashboard_data.json generators | 4 |
| LT-05: Dashboard UI | Per-organ visual dashboards | 4 |
| LT-06: Sanctum + E2E Proof | Aggregation + synthetic task proof | 3 |

**Total: 20 stages (±2)**

### 3.3 Stage Grouping Rules

**Combine when:**
- Same organ, same file type (e.g., all Doctrinarium schemas in one stage)
- Read-only validation stages (can batch multiple checks)
- Dashboard data + dashboard UI for same organ if simple

**Never combine:**
- Schema creation + code that uses schema (dependency)
- Backend truth + dashboard UI (must verify backend first)
- Different organs' core logic (ownership collision risk)
- Any stage with Owner decision gate + any other work

### 3.4 What to Defer

| Defer to V1.1 | Defer to Mega-Hardening |
|---------------|------------------------|
| Scheduled reports | Semantic search in Doctrinarium |
| Bulk actions in Admin dashboard | Full visual diff for laws |
| Workload tracking in Officio | Inquisition audit integration |
| Advanced filters | Event bus between organs |
| Performance history metrics | Autonomous agent assignment |

---

## 4. V1 / V1.1 / Mega-Hardening Split

### 4.1 Must Be in V1

| Area | V1 Minimum |
|------|------------|
| **Schemas** | organ_self_report, receipt, work_packet, stage_map, role_contract, law_registry_entry |
| **Doctrinarium** | Organ health gate, task-start gate, law registry, compliance report |
| **Administratum** | Work packet CRUD, route sheet, stage logging, receipt on transition, bundle manifest |
| **Astronomicon** | Task registration, stage map storage, stage status display, review pack export |
| **Officio Agentis** | Role contract registry, role read receipt, capability match validation |
| **Dashboards** | One dashboard per organ reading real JSON, EN/RU toggle, no fake green |
| **Sanctum** | Aggregates four organ statuses, shows task corridor state |

### 4.2 Should Be in V1 If Easy

- Simple field-change summary for law updates
- Basic keyword search in Doctrinarium
- Stage transition animations (CSS-only, no complex WebGL)
- Receipt history panel in Admin dashboard

### 4.3 Defer to V1.1

- Scheduled/periodic reports
- Bulk actions
- Workload tracking
- Performance history
- Advanced filters
- Side-by-side law diff view

### 4.4 Defer to Mega-Hardening

- Inquisition audit hooks
- Semantic search
- Event bus architecture
- Autonomous agent scheduling
- Cross-task strategic graph (Strategium)

---

## 5. Dashboard Architecture Recommendations

### 5.1 Architecture Pattern

```
[Backend Truth Files]     [Dashboard Data Adapter]     [Dashboard UI]
      ↓                           ↓                         ↓
organ_self_report.json  →  dashboard_data.json      →   HTML/Qt reads JSON
receipts/*.json         →  (generated on demand)    →   No direct file access
reports/*.json          →                           →   Polls/refreshes data file
```

**Key principle:** Dashboard UI never reads raw backend files directly. An adapter script generates `dashboard_data.json` that UI consumes.

### 5.2 Per-Organ Dashboard Contract

Each organ provides:

| File | Purpose |
|------|---------|
| `ORGANS/{ORGAN}/DASHBOARD_DATA/dashboard_state.json` | Current status, warnings, blockers |
| `ORGANS/{ORGAN}/DASHBOARD_DATA/dashboard_actions.json` | Available buttons, enabled/disabled state |
| `ORGANS/{ORGAN}/DASHBOARD_DATA/dashboard_metrics.json` | Numeric health/freshness metrics |
| `ORGANS/{ORGAN}/DASHBOARD_DATA/evidence_index.json` | Links to receipts/reports backing each status |

### 5.3 Sanctum Aggregation

Sanctum reads each organ's `dashboard_state.json` and merges into unified view:

```json
{
  "organs": [
    {"organ_id": "DOCTRINARIUM", "status": "PASS", "evidence_path": "..."},
    {"organ_id": "ADMINISTRATUM", "status": "WARNING", "evidence_path": "..."},
    ...
  ],
  "task_corridor_status": "READY",
  "gate_truth": {"ready_for_agent": true}
}
```

### 5.4 Action Button Safety

| Button Type | V1 Behavior |
|-------------|-------------|
| Read-only (view, export) | Enabled, no confirmation |
| State transition | Confirmation dialog + receipt required |
| Destructive (delete, reset) | Disabled or Owner-gated |
| Registration/creation | Disabled in V1 UI; script-only |

### 5.5 EN/RU i18n

- Use JSON translation files: `i18n/en.json`, `i18n/ru.json`
- UI loads based on toggle state
- Canonical machine files remain English
- Display labels come from i18n files

### 5.6 Performance Budget

| Metric | Target |
|--------|--------|
| Dashboard load | < 1000ms |
| Large stage map render | < 2000ms |
| Animation frame rate | 60 FPS target, 30 FPS minimum |
| Data refresh | On-demand + manual, no heavy polling |

### 5.7 Animation Rules (Realistic for V1)

| Effect | V1 Implementation |
|--------|-------------------|
| Completed stage glow | CSS `box-shadow` with `animation: pulse` |
| Active stage pulse | CSS keyframe animation |
| Future stage shimmer | CSS gradient animation |
| Blocked stage | Red border + CSS shake on hover |
| Transitions | CSS `transition: all 0.3s ease` |

**Defer to V1.1:** WebGL effects, particle systems, complex 3D.

---

## 6. Backend Truth / Schema Recommendations

### 6.1 Schema Priority Table

| Schema | Why Needed | Owner | V1 Minimum Fields | Defer |
|--------|------------|-------|-------------------|-------|
| `organ_self_report` | Every organ must report health | Each organ | organ_id, status, warnings, blockers, evidence_links, generated_at | metrics detail |
| `receipt` | Proves transitions happened | Administratum | receipt_id, timestamp, action, actor, evidence_hash | extended metadata |
| `work_packet` | Central task tracking | Administratum | id, task_id, state, current_stage, route_sheet, evidence_paths | priority enforcement |
| `stage_map` | Task navigation | Astronomicon | stage_map_id, task_id, stages[], status | dependency graph viz |
| `role_contract` | Agent capability proof | Officio Agentis | role_id, allowed_actions, forbidden_actions, required_reads | workload fields |
| `law_registry_entry` | Law tracking | Doctrinarium | law_id, status, version, evidence_path | semantic tags |
| `dashboard_state` | UI data source | Each organ | organ_id, status, warnings, actions, evidence_index | animation hints |
| `compliance_report` | Gate verdicts | Doctrinarium | report_id, gate_id, verdict, checks[], timestamp | trend history |

### 6.2 Schema Freeze Rule

**Before stage execution begins:**
1. All V1 schemas committed
2. Schema validation scripts working
3. No schema changes during execution without Owner gate

---

## 7. Cross-Organ Communication Model

### 7.1 V1 Communication Pattern

**File-based reports + registry lookups.** No runtime event bus.

| From | To | Mechanism |
|------|-----|-----------|
| Doctrinarium | Administratum | Doctrinarium writes `compliance_report.json`; Admin reads before task start |
| Administratum | Astronomicon | Admin reads `TASK_REGISTRY.json` from Astronomicon |
| Officio Agentis | Administratum | Officio writes `role_assignment_receipt.json`; Admin reads |
| Officio Agentis | Doctrinarium | Officio reads law files; writes `law_read_receipt.json` |
| Sanctum | All organs | Sanctum reads each organ's `dashboard_state.json` |

### 7.2 Why Not Event Bus in V1

- Adds complexity
- Requires runtime coordination
- File-based is auditable and debuggable
- Event bus is V1.1/mega-hardening scope

### 7.3 Port Protocol

Existing `ORGANS/PORT_PROTOCOL/` schemas are good. Use them for cross-organ messages:
- `port_message_v1.schema.json`
- `port_receipt_v1.schema.json`
- `port_response_v1.schema.json`

---

## 8. Task Corridor Proof Strategy

### 8.1 Proof Tasks

| Proof Type | Description | When |
|------------|-------------|------|
| **Synthetic proof** | Fake TASK_ID flows through all four organs with mock data | After LT-03 |
| **Real small task** | Actual small task (e.g., "add one schema") runs through corridor | After LT-04 |
| **Failure proof** | Deliberately trigger block at each gate; verify system stops | After LT-03 |
| **Dashboard proof** | All four dashboards show correct state for synthetic task | After LT-05 |
| **Continuity pack proof** | Final bundle collected and validated | After LT-06 |

### 8.2 Corridor Checkpoints

```
TASK_ID arrives
  ↓
[Doctrinarium] → organ_health_gate → PASS/BLOCK
  ↓
[Doctrinarium] → task_start_gate → PASS/BLOCK
  ↓
[Administratum] → lookup task in Astronomicon → route_sheet issued
  ↓
[Officio Agentis] → role_contract assigned → read_receipt written
  ↓
[Astronomicon] → stage_map loaded → current_stage set
  ↓
[Administratum] → task_start_confirmed → receipt written
  ↓
[Servitor executes stages] → stage_completion_receipt per stage
  ↓
[Administratum] → final_bundle collected → continuity_pack written
```

Each checkpoint must produce a receipt or report.

---

## 9. Pre-Execution Readiness Checklist

### 9.1 Required Before Execution

| Category | Item | Status |
|----------|------|--------|
| **Decisions** | V1 schema fields frozen | ☐ |
| **Decisions** | Dashboard button scope confirmed | ☐ |
| **Decisions** | Animation complexity level confirmed | ☐ |
| **Source files** | All V1 schemas committed | ☐ |
| **Source files** | Stage prompt template approved | ☐ |
| **Scripts** | Schema validation script working | ☐ |
| **Scripts** | Self-report generator per organ | ☐ |
| **Scripts** | Dashboard data adapter per organ | ☐ |
| **Stop behavior** | Defined: what happens on BLOCK | ☐ |
| **Stop behavior** | Defined: rollback procedure | ☐ |
| **Evidence** | Receipt filename convention documented | ☐ |
| **Evidence** | Evidence retention policy documented | ☐ |

### 9.2 Stage Prompt Prerequisites

Each stage prompt must have before execution:
- Exact input files listed
- Exact output files listed
- Validation command specified
- Pass/fail criteria explicit
- Owner decision gates marked

---

## 10. Recommended Folder / File Structure

### 10.1 V1 Hardening Package

```
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/
├── GENERAL_TASK.json
├── LOCAL_TASKS/
│   ├── LT-01-SCHEMA-FINALIZATION/
│   │   ├── LOCAL_TASK.json
│   │   └── STAGES/
│   │       ├── STAGE-01-CROSS-ORGAN-SCHEMAS.json
│   │       └── STAGE-02-ORGAN-SPECIFIC-SCHEMAS.json
│   ├── LT-02-BACKEND-TRUTH/
│   ├── LT-03-CORRIDOR-WIRING/
│   ├── LT-04-DASHBOARD-DATA/
│   ├── LT-05-DASHBOARD-UI/
│   └── LT-06-SANCTUM-E2E/
├── STAGE_PROMPTS/
│   ├── STAGE-01-PROMPT.md
│   └── ...
├── EVIDENCE/
│   └── (receipts and reports during execution)
├── BUNDLE/
│   └── (final bundle after completion)
└── RECONCILIATION/
    ├── KIRO_RECOMMENDATIONS.md
    ├── SPECULUM_CRITIQUE.md
    └── RECONCILIATION_TABLE.json
```

### 10.2 Per-Organ Dashboard Data

```
ORGANS/{ORGAN}/DASHBOARD_DATA/
├── dashboard_state.json
├── dashboard_actions.json
├── dashboard_metrics.json
└── evidence_index.json
```

---

## 11. Metrics Recommendations

### 11.1 Per-Organ Metrics

| Organ | Metric | Calculation |
|-------|--------|-------------|
| **Doctrinarium** | law_compliance_rate | laws_passing / total_laws |
| **Doctrinarium** | gate_pass_rate | gates_passed / gates_checked |
| **Administratum** | task_completion_rate | tasks_completed / tasks_started |
| **Administratum** | receipt_coverage | transitions_with_receipt / total_transitions |
| **Astronomicon** | stage_completion_rate | stages_completed / stages_total |
| **Astronomicon** | registration_success_rate | tasks_registered / tasks_attempted |
| **Officio Agentis** | role_contract_validity | valid_contracts / total_contracts |
| **Officio Agentis** | read_receipt_coverage | roles_with_read_receipt / active_roles |

### 11.2 Sanctum Aggregate Metrics

| Metric | Description |
|--------|-------------|
| `corridor_health` | All four organs PASS = GREEN; any WARNING = YELLOW; any BLOCK = RED |
| `evidence_freshness` | Oldest evidence file age; stale > 24h = WARNING |
| `fake_green_risk` | Count of statuses without evidence_path |
| `bundle_completeness` | Required bundle files present / required total |

---

## 12. Stage Prompt Design Recommendations

### 12.1 Required Prompt Sections

Every stage prompt must include:

```markdown
## Stage: {STAGE_ID}
## Goal: {one sentence}

### Inputs
- {file path 1}
- {file path 2}

### Outputs
- {file path 1} — {description}
- {file path 2} — {description}

### Allowed Paths
- ORGANS/{ORGAN}/...
- schemas/...

### Forbidden Paths
- ORGANS/{OTHER_ORGAN}/...
- SANCTUM/...

### Validation Commands
- `python scripts/validate_schema.py {output_file}`
- `python scripts/verify_repo.py`

### Pass Criteria
- [ ] All output files exist
- [ ] All output files pass schema validation
- [ ] No new warnings in verify_repo

### Fail Criteria
- Any output file missing
- Schema validation fails
- New blockers introduced

### Owner Decision Gates
- {none / list if any}

### Evidence Output
- Receipt: `EVIDENCE/{TIMESTAMP}_{ORGAN}_STAGE_{N}_COMPLETE.json`

### Response Format
- Confirm outputs created
- List any warnings
- State PASS or FAIL
```

### 12.2 Prompt Anti-Patterns

| Avoid | Why |
|-------|-----|
| "Implement as you see fit" | Servitor will guess wrong |
| No validation command | No way to verify pass |
| Mixed organ scope | Ownership collision |
| No evidence output | Fake green risk |

---

## 13. Top Risks and Simplifications

### 13.1 Top 10 Things Likely to Break

1. Schema changes mid-execution → cascading rework
2. Dashboard reads mock data → fake green
3. Missing receipts → unproven transitions
4. Cross-organ file access without port → ownership violation
5. Animation complexity → performance collapse
6. i18n incomplete → broken UI in one language
7. Evidence retention unclear → files deleted or orphaned
8. Stage scope too broad → Servitor stuck
9. No validation command → silent failures
10. Owner decision gate unmarked → unexpected stop

### 13.2 Top 10 Simplifications That Save Time

1. Use existing `organ_self_report.schema.json` — don't reinvent
2. CSS-only animations — no WebGL in V1
3. File-based communication — no event bus
4. Dashboard data adapter pattern — decouples UI from backend
5. One dashboard per organ — don't try unified mega-dashboard first
6. Disable registration buttons in V1 — display-only safer
7. On-demand reports — no scheduled jobs
8. Reuse existing receipt schema — extend minimally
9. Stage prompts as markdown — no complex tooling
10. Synthetic proof task — don't wait for real task

### 13.3 Top 10 Things to Defer

1. Semantic search
2. Event bus
3. Bulk actions
4. Workload tracking
5. Performance history
6. Visual diff for laws
7. Inquisition hooks
8. Autonomous scheduling
9. WebGL animations
10. Cross-task strategic graph

### 13.4 Top 10 Checks That Prevent Fake Green

1. Every status field has `evidence_path`
2. Every transition has receipt
3. Schema validation on all JSON outputs
4. `verify_repo.py` runs every stage
5. Dashboard data adapter validates source files exist
6. Stale evidence (>24h) triggers WARNING
7. Missing receipt = UNKNOWN, not PASS
8. Empty evidence array = BLOCKED
9. Button disabled if action would have no receipt
10. Sanctum shows "evidence missing" badge if any organ lacks proof

---

## 14. Speculum Reconciliation Guidance

### 14.1 Reconciliation Process

1. Receive Speculum critique
2. Create reconciliation table
3. For each critique item: accept / defer / reject with reason
4. Map accepted items to affected Local Task and Stage
5. Update stage prompts if needed
6. Commit reconciliation table

### 14.2 Reconciliation Table Format

| ID | Source | Recommendation/Critique | Decision | Reason | Affected LT | Affected Stage | Evidence Required |
|----|--------|------------------------|----------|--------|-------------|----------------|-------------------|
| R-01 | Kiro | Build schemas first | ACCEPTED | Reduces rework | LT-01 | S-01, S-02 | Schema files committed |
| S-01 | Speculum | Ownership collision risk in Admin→Astro | ACCEPTED | Add port receipt | LT-03 | S-07 | Port receipt schema |
| S-02 | Speculum | Dashboard mock data risk | ACCEPTED | Add evidence_path check | LT-05 | S-15 | Validation script |
| K-05 | Kiro | Defer event bus | ACCEPTED | V1.1 scope | — | — | — |
| S-07 | Speculum | Missing STOP gate at X | DEFERRED | V1.1 | — | — | — |

### 14.3 Critique Categories to Expect from Speculum

- Ownership collision attacks
- Fake green scenarios
- State lifecycle contradictions
- Evidence insufficiency
- Overreach by any organ
- Missing STOP gates
- Stage plan weaknesses

---

## 15. Final Next-Step Plan

### 15.1 Immediate Actions

| Step | Action | Output |
|------|--------|--------|
| 1 | Commit this Kiro recommendations document | `KIRO_RECOMMENDATIONS.md` in task folder |
| 2 | Send Speculum red-team prompt | Speculum critique document |
| 3 | Commit Speculum critique | `SPECULUM_CRITIQUE.md` in task folder |
| 4 | Build reconciliation table | `RECONCILIATION_TABLE.json` |
| 5 | Finalize Local Task decomposition | `LOCAL_TASKS/` folder structure |
| 6 | Write stage prompts | `STAGE_PROMPTS/` folder |
| 7 | Owner reviews stage prompts | Owner approval receipt |
| 8 | Begin execution | Stage-by-stage with receipts |

### 15.2 Speculum Prompt Guidance

Ask Speculum to attack:
- Ownership boundaries between organs
- Fake green scenarios (status without evidence)
- Dashboard mock data risks
- State lifecycle contradictions
- Evidence/receipt gaps
- Overreach by any organ
- Stage plan weaknesses
- Missing STOP gates
- Blocker cascade scenarios

### 15.3 When to Write Stage Prompts

**After:**
- Kiro recommendations ingested ✓
- Speculum critique ingested
- Reconciliation table complete
- Local Task structure finalized

**Before:**
- Execution begins

### 15.4 Execution Readiness Gate

Do not begin execution until:
- [ ] All V1 schemas committed
- [ ] Stage prompts written and Owner-reviewed
- [ ] Validation scripts working
- [ ] Reconciliation table complete
- [ ] Pre-execution checklist passed

---

## FINAL VERDICT

| Gate | Status |
|------|--------|
| **READY_FOR_SPECULUM_REVIEW** | ✅ YES — Matrix is complete, Kiro recommendations ready |
| **READY_FOR_STAGE_DECOMPOSITION** | ⚠️ AFTER Speculum — Wait for critique reconciliation |
| **READY_FOR_HARDENING_EXECUTION** | ❌ NOT YET — Need stage prompts + validation scripts |
| **MUST_PREPARE_BEFORE_EXECUTION** | V1 schemas frozen, stage prompts written, validation scripts working, reconciliation complete |
| **RECOMMENDED_NEXT_ACTION** | **Send Speculum red-team prompt now** |

---

*Document generated: 2026-05-15*
*Source commit: 931940980288cd42ece295d1107633d1fc55abf2*
*Advisory only — does not claim final authority*