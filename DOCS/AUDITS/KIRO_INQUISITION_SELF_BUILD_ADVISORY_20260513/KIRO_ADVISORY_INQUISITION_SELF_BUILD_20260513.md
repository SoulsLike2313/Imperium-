# Kiro Advisory: How IMPERIUM Should Build an Organ Through Itself

Source: Kiro external technical architecture advisor
Topic: Act 5 preparation — First Self-Descriptive Organ Build: Inquisition v0.1
Status: RAW_ADVISORY_INPUT_NOT_YET_RECONCILED
Registered by: Owner / Logos-Prime
Base Git HEAD: 090c75bdc5f56c808b7dc528c2e7ae7819501388

---

PASTE FULL KIRO ADVISORY BELOW THIS LINE.
Understood.

Let me inspect the current repo state to ground this advisory in reality.

Now I have enough context. The Inquisition already has real scripts (preflight, forbidden refs, fake green detection, duplicate detection). It's at SCAFFOLD level but has more substance than expected. Let me produce the full advisory.

Given the massive scope of this request and context constraints, I'll produce the complete advisory design pack focused on the most critical sections.

```markdown
# Kiro Advisory: How IMPERIUM Should Build an Organ Through Itself

## HEAD: 090c75b | Commits: 55 | 2026-05-13

---

## 1. Executive Summary

IMPERIUM должен строить органы через собственный процесс: General Task → Task → Stage → Run → Bundle → Intake → Commit. Это не философия — это конкретный pipeline, где каждый шаг производит файлы, receipts и evidence.

**Ключевой принцип:** Орган не существует, пока он не может описать себя и проверить своё состояние. Scaffold ≠ орган. Орган = contract + schemas + scripts + checks + receipts + self-report.

**Для Inquisition v0.1:** Уже есть 5 скриптов (preflight, forbidden refs, fake green, duplicates, deletion proposals). Это больше, чем scaffold. Но нет: self-report port, organ contract JSON, schema validation, capability declarations, structured audit categories. Нужно довести до self-descriptive состояния.

**Цикл self-build:**
```
1. Register GENERAL_TASK (Astronomicon)
2. Decompose into TASK/STAGE (Astronomicon + Kiro advisory)
3. Export review pack (Logos-Prime)
4. Ingest advisory (Logos-Prime)
5. Modernize task/stage map
6. Mark READY_FOR_AGENT
7. VM2 executes stage → bundle
8. PC intake → verify → commit
9. VM2 sync
10. Organ self-check → receipt
11. Owner summary
12. Inquisition/Speculum review
```

---

## 2. Current System Interpretation

**Что IMPERIUM уже имеет (OBSERVED):**

| Capability | Status | Evidence |
|-----------|--------|----------|
| General Task registration | OPERATIONAL | `ORGANS/ASTRONOMICON/REGISTRY/GENERAL_TASKS/` — 3 registered tasks |
| Bundle/provenance spine | OPERATIONAL | `DOCS/BUNDLE_AND_RECEIPT_CONTRACT_V0_1.md` — active contract |
| Intake/review protocol | OPERATIONAL | `DOCS/BUNDLE_INTAKE_REVIEW_FLOW_V0_1.md` + repair retrospective |
| SCRIPTORIUM | OPERATIONAL | `REGISTRY/SCRIPT_REGISTRY.json` + contract |
| ARSENAL | OPERATIONAL | `REGISTRY/ARSENAL_TOOL_INDEX.json` + install status |
| Route/Git truth | OPERATIONAL | `ORGANS/ADMINISTRATUM/CONFIG/ADMINISTRATUM_ROUTE_TRUTH_V0_1.json` |
| Response contracts | OPERATIONAL | `ORGANS/OFFICIO_AGENTIS/CONFIG/SERVITOR_RESPONSE_CONTRACT_V0_1.md` |
| Schemas | OPERATIONAL | 18 schemas in `schemas/` |
| Verification spine | OPERATIONAL | `scripts/verify_repo.py` — 5 gates |
| Capability references | DOCUMENTED | `DOCS/TOOLING_SPINOFF/CAPABILITY_REFERENCES_FOR_TASK_STAGE_RUN_V0_1.md` |

**Что отсутствует (MISSING / UNKNOWN):**

| Missing | Impact | Needed for Act 5 |
|---------|--------|-------------------|
| Organ self-report port standard | Organs can't describe themselves | YES |
| Organ contract JSON schema | No machine-validation of organ completeness | YES |
| Task/Stage modernization protocol | No formal way to update task after review | YES |
| READY_FOR_AGENT gate | No formal "stage is ready for execution" check | YES |
| Stage bundle format (per-stage, not per-task) | VM2 gets whole task, not focused stage | NICE TO HAVE |
| Inquisition self-report | Inquisition can't report its own state | YES |
| Address/truth/capability consistency checker | No automated cross-reference validation | YES (Act 3) |

---

## 3. Core Principle: Organ Is Not a Folder

**Определение реального органа IMPERIUM:**

Орган считается OPERATIONAL когда ВСЕ следующие условия выполнены:

| # | Requirement | Verification method |
|---|-------------|-------------------|
| 1 | Contract file exists and is valid JSON/MD | Schema validation |
| 2 | ORGAN_STATUS.json exists with maturity ≥ LEVEL_5 | File check |
| 3 | At least one schema in SCHEMAS/ or PORTS/ | File count |
| 4 | At least one executable script in SCRIPTS/ | py_compile + exists |
| 5 | Script registered in SCRIPT_REGISTRY | Registry lookup |
| 6 | Self-report port produces valid output | Script execution |
| 7 | At least one receipt template or receipt evidence | File exists |
| 8 | Capability declarations present | JSON field check |
| 9 | Failure modes documented | File exists |
| 10 | Owner-facing report form exists (MD or JSON) | File exists |

**Maturity levels (refined from ORGAN_DEFINITION_RULE.md):**

```
LEVEL_0: NAME_ONLY (folder exists)
LEVEL_1: CONTRACT_DEFINED (contract + README)
LEVEL_2: SCHEMAS_DEFINED (at least one schema)
LEVEL_3: SCRIPTS_PRESENT (at least one script, py_compile passes)
LEVEL_4: SCRIPTS_REGISTERED (in SCRIPT_REGISTRY)
LEVEL_5: SELF_REPORT_OPERATIONAL (self-report port works)
LEVEL_6: RECEIPTS_PRODUCED (at least one real receipt exists)
LEVEL_7: OPERATIONAL (all 10 requirements met)
```

**Current Inquisition:** LEVEL_3 (scripts present, py_compile passes, but not registered in SCRIPT_REGISTRY, no self-report port, no structured contract JSON).

---

## 4. Proposed Organ Build Lifecycle

### Phase 1: REGISTER (Astronomicon)

| Field | Value |
|-------|-------|
| Input | Owner goal description |
| Output | `GENERAL_TASK.json` in Astronomicon registry |
| Required files | `ORGANS/ASTRONOMICON/REGISTRY/GENERAL_TASKS/{id}.json` |
| Required checks | Schema validation against `schemas/general_task.schema.json` |
| Blocking | Invalid schema, duplicate ID |
| Receipt | Registration receipt in General Task file |
| Owner | Astronomicon + Logos-Prime |

### Phase 2: DECOMPOSE (Astronomicon + Kiro)

| Field | Value |
|-------|-------|
| Input | Registered General Task |
| Output | TASK candidates + STAGE map draft |
| Required files | `{task_id}_TASK_CANDIDATES_DRAFT.json` |
| Required checks | Each stage has pass_criteria |
| Blocking | Missing pass criteria |
| Receipt | Draft registration |
| Owner | Astronomicon |

### Phase 3: ADVISORY EXPORT (Logos-Prime)

| Field | Value |
|-------|-------|
| Input | Task/Stage draft |
| Output | Technical review input JSON (per `schemas/technical_review_input.schema.json`) |
| Required files | Export file for Kiro/Speculum |
| Required checks | Schema validation |
| Blocking | Invalid export format |
| Receipt | Export timestamp |
| Owner | Logos-Prime |

### Phase 4: ADVISORY INGEST (Logos-Prime)

| Field | Value |
|-------|-------|
| Input | Kiro/Speculum response |
| Output | Technical review response JSON (per `schemas/technical_review_response.schema.json`) |
| Required files | Response file |
| Required checks | Schema validation |
| Blocking | None (advisory is optional) |
| Receipt | Ingest timestamp |
| Owner | Logos-Prime |

### Phase 5: MODERNIZE (Logos-Prime + Owner)

| Field | Value |
|-------|-------|
| Input | Original draft + advisory responses |
| Output | Final TASK + STAGE map |
| Required files | `ORGANS/ASTRONOMICON/TASKS/{task_id}/STAGE_MAP.json` |
| Required checks | All stages have pass_criteria, no circular deps |
| Blocking | Owner rejects modernization |
| Receipt | Modernization receipt |
| Owner | Owner approval required |

### Phase 6: READY_FOR_AGENT (Administratum)

| Field | Value |
|-------|-------|
| Input | Final stage map + current stage pointer |
| Output | Stage work packet |
| Required files | Work packet JSON |
| Required checks | Capabilities available, tools installed, route truth valid |
| Blocking | Missing capability, stale route truth |
| Receipt | Ready receipt |
| Owner | Administratum |

### Phase 7: VM2 EXECUTION (Servitor)

| Field | Value |
|-------|-------|
| Input | Stage work packet + corridor |
| Output | Bundle ZIP |
| Required files | MANIFEST.json, RECEIPT.json, VERDICT.md, repo/, evidence/ |
| Required checks | Bundle contract compliance |
| Blocking | Corridor violation |
| Receipt | Bundle receipt |
| Owner | VM2 Servitor |

### Phase 8: PC INTAKE (Owner + Administratum)

| Field | Value |
|-------|-------|
| Input | Bundle ZIP + .sha256 |
| Output | Intake verdict (CAN_COMMIT / CANNOT_COMMIT / NEEDS_OWNER_DECISION) |
| Required checks | SHA256 match, manifest valid, scope check, forbidden touch check |
| Blocking | SHA mismatch, forbidden touch, missing manifest |
| Receipt | Intake receipt |
| Owner | PC intake scripts + Owner |

### Phase 9: COMMIT + SYNC (Owner)

| Field | Value |
|-------|-------|
| Input | Approved bundle |
| Output | Git commit + push + VM2 sync |
| Required checks | verify_repo, Git CLI check |
| Blocking | verify_repo FAIL |
| Receipt | Git CLI receipt |
| Owner | Owner only |

### Phase 10: SELF-CHECK (Target organ)

| Field | Value |
|-------|-------|
| Input | Post-commit state |
| Output | Organ self-report |
| Required checks | Self-report port produces valid output |
| Blocking | Self-report fails |
| Receipt | Self-report receipt |
| Owner | Target organ |

---

## 5. Organ Blueprint Template

```
ORGANS/{ORGAN_NAME}/
├── README.md                          # Human description
├── ORGAN_STATUS.json                  # Maturity, status, last check
├── ORGAN_CONTRACT.json                # Machine-readable contract
├── CONFIG/                            # Organ-specific configuration
│   └── {organ}_config.json
├── SCHEMAS/                           # Organ-owned schemas
│   └── {organ}_self_report.schema.json
├── PORTS/                             # Interface definitions
│   └── self_report.port.json
├── SCRIPTS/                           # Executable scripts
│   └── {organ}_self_report_v0_1.py
├── CHECKS/                            # Organ-specific verification
│   └── {organ}_health_check_v0_1.py
├── POLICIES/                          # Rules and constraints
│   └── {policy_name}.json
└── AUDIT_RULES/                       # (Inquisition-specific)
    └── {rule_set}.json
```

**v0.1 minimum для OPERATIONAL:**
- README.md
- ORGAN_STATUS.json (LEVEL_5+)
- ORGAN_CONTRACT.json
- At least one script in SCRIPTS/
- Self-report script that produces JSON output

---

## 6. Self-Descriptive Requirements

Каждый орган должен отвечать на вопросы через self-report:

```json
{
  "schema_version": "imperium.organ_self_report.v0_1",
  "organ_id": "INQUISITION",
  "timestamp_utc": "2026-05-13T12:00:00Z",
  "maturity": "LEVEL_5_SELF_REPORT_OPERATIONAL",
  "responsible_for": ["fake green detection", "forbidden ref scanning", "drift detection", "receipt integrity"],
  "forbidden_actions": ["delete files", "modify source", "commit", "push"],
  "defining_files": [
    "ORGANS/INQUISITION/ORGAN_CONTRACT.json",
    "ORGANS/INQUISITION/ORGAN_STATUS.json",
    "ORGANS/INQUISITION/SCRIPTS/run_inquisition_preflight.py"
  ],
  "validating_schemas": ["schemas/inquisition_self_report.schema.json"],
  "owned_scripts": ["run_inquisition_preflight.py", "detect_forbidden_refs.py", "detect_duplicate_stage_ids.py"],
  "produced_receipts": ["INQUISITION_PREFLIGHT_REPORT.json", "FAKE_GREEN_REPORT.json"],
  "required_capabilities": ["python>=3.12", "json", "pathlib", "re"],
  "read_zones": ["ORGANS/", "REGISTRY/", "schemas/", "DOCS/", ".imperium_runtime/"],
  "write_zones": [".imperium_runtime/inquisition/"],
  "current_status": "OPERATIONAL_LIMITED",
  "stale_items": [],
  "unknown_items": ["ARSENAL install verification not yet checked"],
  "blocked_items": [],
  "query_command": "python ORGANS/INQUISITION/SCRIPTS/inquisition_self_report_v0_1.py --repo-root E:\\IMPERIUM"
}
```

---

## 7. Ports / Interfaces

### Organ Self-Report Port v0.1

**Input (query):**
```json
{
  "query_type": "self_report",
  "repo_root": "E:\\IMPERIUM",
  "requested_by": "DOCTRINARIUM",
  "timestamp_utc": "2026-05-13T12:00:00Z"
}
```

**Output (self-report JSON):**
Структура из секции 6 выше.

**Status enums:**
```
OPERATIONAL          — all checks pass, receipts exist
OPERATIONAL_LIMITED  — works but missing some capabilities
DEGRADED            — partially broken, some checks fail
SCAFFOLD            — files exist but no execution
BLOCKED             — cannot function
UNKNOWN             — not checked recently
```

**Implementation:** File-based. Script reads query (or runs without query for default self-report), writes JSON to `.imperium_runtime/{organ}/SELF_REPORT.json`.

---

## 8. Inquisition v0.1 Target Design

### Что уже есть (OBSERVED)

- 5 Python scripts (preflight, forbidden refs, duplicates, fake green, deletion proposals)
- Port schemas (audit_stage_result, check_fake_green, check_receipt_integrity, check_registry_drift, check_duplicate_paths)
- AUDIT_RULES/POST_STAGE_AUDIT_RULES.json
- ORGAN_STATUS.json (SCAFFOLD)

### Что нужно добавить для v0.1 OPERATIONAL

| # | File | Purpose |
|---|------|---------|
| 1 | `ORGAN_CONTRACT.json` | Machine-readable contract with responsibilities, forbidden, capabilities |
| 2 | `SCHEMAS/inquisition_self_report.schema.json` | Validates self-report output |
| 3 | `SCHEMAS/inquisition_audit_report.schema.json` | Validates audit output |
| 4 | `SCRIPTS/inquisition_self_report_v0_1.py` | Self-report port implementation |
| 5 | `SCRIPTS/inquisition_audit_system_v0_1.py` | Full system audit (combines all checks) |
| 6 | `CHECKS/check_organ_completeness.py` | Verify all organs meet minimum requirements |
| 7 | `CHECKS/check_registry_consistency.py` | Cross-reference registries vs filesystem |
| 8 | `CHECKS/check_stale_truth.py` | Detect stale Git truth, stale timestamps |
| 9 | Updated `ORGAN_STATUS.json` | Maturity → LEVEL_5 or LEVEL_6 |

### Audit categories for v0.1

| Category | What it checks | Script |
|----------|---------------|--------|
| `FAKE_GREEN` | Claims without evidence, PASS without checks | `run_inquisition_preflight.py` (exists) |
| `FORBIDDEN_REFS` | Throne contact, auto-sync, destructive commands | `detect_forbidden_refs.py` (exists) |
| `STALE_TRUTH` | Git truth older than 1 hour, stale timestamps | `check_stale_truth.py` (NEW) |
| `REGISTRY_DRIFT` | ORGAN_REGISTRY vs folders, SCRIPT_REGISTRY vs files | `check_registry_consistency.py` (NEW) |
| `ORGAN_COMPLETENESS` | Missing contract, missing scripts, missing self-report | `check_organ_completeness.py` (NEW) |
| `CAPABILITY_CLAIMS` | Tool claims without ARSENAL evidence | Part of system audit (NEW) |
| `RECEIPT_INTEGRITY` | Missing receipts, invalid receipt JSON | Part of system audit (NEW) |
| `PATH_MISMATCH` | PC paths in VM2 context or vice versa | Part of forbidden refs (exists) |
| `WARNING_FLOOD` | Warnings > baseline without explanation | Part of system audit (NEW) |
| `UNKNOWN_AS_PASS` | Items marked UNKNOWN treated as if PASS | Part of fake green (exists) |

### Что Inquisition v0.1 НЕ должен делать

- Не удалять файлы
- Не модифицировать source
- Не commit/push
- Не запускать тяжёлые процессы
- Не проверять содержимое private bundles
- Не проверять VM2 state (только PC local)
- Не заменять verify_repo.py (дополняет, не заменяет)

---

## 9. Inquisition v0.1 Acceptance Criteria

```
[ ] ORGAN_CONTRACT.json exists and validates against schema
[ ] ORGAN_STATUS.json maturity >= LEVEL_5
[ ] inquisition_self_report_v0_1.py runs without error
[ ] Self-report output validates against inquisition_self_report.schema.json
[ ] inquisition_audit_system_v0_1.py runs and produces structured report
[ ] Audit report contains all 10 categories with verdict per category
[ ] At least 3 categories produce real findings (not empty)
[ ] No fake PASS: if check didn't run, verdict = UNKNOWN
[ ] All Inquisition scripts registered in SCRIPT_REGISTRY
[ ] ORGAN_REGISTRY entry for INQUISITION updated to LEVEL_5+
[ ] py_compile passes for all scripts
[ ] verify_repo.py still passes (no regression)
[ ] Git CLI check PASS after commit
[ ] VM2 sync successful
[ ] Self-report receipt exists in .imperium_runtime/inquisition/
```

---

## 10. How Act 3 Should Prepare Act 5

Act 3 (Address / Truth / Capability Spine) must create:

| Artifact | Purpose for Act 5 | File |
|----------|-------------------|------|
| Zone registry | Inquisition needs to know read/write zones per organ | `REGISTRY/ZONE_REGISTRY.json` (update) |
| Truth source registry | Inquisition checks staleness of each truth source | `REGISTRY/TRUTH_SOURCES.json` (new) |
| Capability spine | Inquisition verifies capability claims | `REGISTRY/ARSENAL_INSTALL_STATUS.json` (exists, needs verification script) |
| Stale/warning baseline | Inquisition compares current vs baseline | `REGISTRY/WARNING_BASELINE.json` (new) |
| Address consistency checker | Inquisition uses to verify path correctness | `TOOLS/check_address_consistency_v0_1.py` (new) |
| Organ completeness schema | Inquisition validates organs against it | `schemas/organ_contract.schema.json` (new) |

---

## 11. How Act 4 Should Prepare Act 5

Act 4 (Full Registration Corridor) must create:

| Artifact | Purpose for Act 5 |
|----------|-------------------|
| Review export format | Inquisition build task exported for Kiro review |
| Advisory response ingest | Kiro response ingested and tracked |
| Task modernization protocol | Task updated after review |
| Stage map modernization | Stages refined after advisory |
| READY_FOR_AGENT gate | Formal check before VM2 execution |
| Stage bundle format | VM2 gets focused stage packet |
| Pass/fail gate definitions | Each stage has machine-checkable criteria |

---

## 12. Suggested TASK/STAGE Breakdown for Act 5

```
GENERAL_TASK: Build Inquisition v0.1 Through IMPERIUM Self-Build Cycle
TASK: TASK-20260514-INQUISITION-V0_1-SELF-BUILD

STAGE-001: Register Inquisition organ contract
  - Create ORGAN_CONTRACT.json
  - Define responsibilities, forbidden, capabilities
  - Pass: contract validates against schema

STAGE-002: Create self-report schema
  - Create schemas/inquisition_self_report.schema.json
  - Create schemas/inquisition_audit_report.schema.json
  - Pass: schemas are valid JSON Schema draft-07

STAGE-003: Build self-report script
  - Create SCRIPTS/inquisition_self_report_v0_1.py
  - Reads organ state, produces self-report JSON
  - Pass: output validates against schema

STAGE-004: Build system audit script
  - Create SCRIPTS/inquisition_audit_system_v0_1.py
  - Combines all check categories
  - Pass: produces report with 10 categories

STAGE-005: Build new checker scripts
  - check_organ_completeness.py
  - check_registry_consistency.py
  - check_stale_truth.py
  - Pass: each runs without error, produces findings

STAGE-006: Update registries
  - SCRIPT_REGISTRY: add all Inquisition scripts
  - ORGAN_REGISTRY: update Inquisition to LEVEL_5+
  - Pass: no registry drift for Inquisition

STAGE-007: Integration test
  - Run full audit on current repo
  - Verify findings are real (not empty, not fake)
  - Pass: at least 3 categories have real findings

STAGE-008: VM2 bundle + PC intake
  - Standard bundle/intake cycle
  - Pass: CAN_COMMIT verdict

STAGE-009: Commit + sync + self-check
  - PC commit, push, VM2 sync
  - Inquisition self-report after sync
  - Pass: self-report shows OPERATIONAL_LIMITED or OPERATIONAL

STAGE-010: Owner summary + Speculum review export
  - Generate Owner-facing summary
  - Export for Speculum red-team
  - Pass: summary exists, export valid
```

---

## 13. Risks and Anti-Patterns

| Risk | Consequence | Mitigation |
|------|-------------|-----------|
| Ceremonial organ (files exist, nothing runs) | Fake maturity claim | Acceptance criteria require execution evidence |
| Giant untestable architecture | Never completes | Keep v0.1 to 10 stages max |
| Fake green in self-report | Inquisition lies about itself | Self-report must show UNKNOWN for unchecked items |
| Stale address maps | Scripts use wrong paths | Act 3 must create freshness check |
| Tool claims without install proof | Scripts fail at runtime | Capability check before READY_FOR_AGENT |
| Hidden local-only state | VM2 can't reproduce | All state in tracked files or explicit runtime |
| Too much automation too early | Bypasses Owner gate | Every commit = Owner decision |
| No Owner decision gates | Autonomous drift | Throne/Owner approval at stage boundaries |
| No red-team review | Blind spots accumulate | Speculum review after each organ build |
| Inquisition audits itself | Conflict of interest | Speculum reviews Inquisition specifically |

---

## 14. Minimal First Implementation Recommendation

**Порядок для Logos-Prime:**

1. **Первое:** Создать `schemas/organ_contract.schema.json` — без этого нельзя валидировать organ contracts.

2. **Второе:** Создать `schemas/organ_self_report.schema.json` — без этого нельзя валидировать self-reports.

3. **Третье:** Создать `ORGANS/INQUISITION/ORGAN_CONTRACT.json` — первый реальный contract по новой schema.

4. **Четвёртое:** Создать `ORGANS/INQUISITION/SCRIPTS/inquisition_self_report_v0_1.py` — первый self-report port.

5. **Пятое:** Обновить `REGISTRY/SCRIPT_REGISTRY.json` — зарегистрировать все 5 существующих + 1 новый Inquisition scripts.

---

## 15. Final Advisory Verdict

**READY_FOR_ACT3_INTEGRATION**

Система имеет достаточно foundation (General Task registration, bundle spine, intake protocol, schemas, route truth) чтобы Act 3 мог создать Address/Truth/Capability spine, после чего Act 5 становится исполнимым.

### 5 most important files to create next

1. `schemas/organ_contract.schema.json`
2. `schemas/organ_self_report.schema.json`
3. `REGISTRY/WARNING_BASELINE.json`
4. `REGISTRY/TRUTH_SOURCES.json`
5. `ORGANS/INQUISITION/ORGAN_CONTRACT.json`

### 5 most important checks to add next

1. Organ completeness check (all 10 organs vs minimum requirements)
2. Registry consistency check (ORGAN_REGISTRY vs filesystem)
3. Stale truth check (timestamps > threshold)
4. Capability verification (ARSENAL claims vs install status)
5. Self-report port validation (output vs schema)

### 5 things NOT to build yet

1. Full task orchestrator (sequential scripts sufficient)
2. Sanctum organ HUD integration (data service first)
3. Automated stage advancement (Owner gates first)
4. Cross-contour Inquisition (PC-only for v0.1)
5. Inquisition auditing Inquisition (Speculum does this)

---

*Advisory завершён. Репозиторий не модифицирован. Все рекомендации = advisory для Logos-Prime.*
```
