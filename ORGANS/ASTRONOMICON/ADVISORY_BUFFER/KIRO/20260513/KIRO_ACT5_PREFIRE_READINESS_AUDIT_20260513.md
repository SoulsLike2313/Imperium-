# KIRO ACT 5 PREFIRE READINESS AUDIT

- source: Kiro / Opus 4.7
- date: 2026-05-13
- status: RAW_ADVISORY_INPUT
- owner_verdict: PENDING_REVIEW
- target_arc: ARC_5_SELF_BUILD_PREFIRE
- repo_exact_head_for_prompt: 22399fd72e3da5300c73e75ff68809f3fbbb4f08
- repo_commit_count_for_prompt: 64
- latest_for_prompt: TASK-20260513: register Arc 5 prefire readiness

## Purpose

This file preserves the Kiro hard red-team architecture audit before Arc 5.

It is stored in Astronomicon Advisory Buffer because it is advisory input, not direct execution authority.

Expected use:

- Logos-Prime reads and summarizes findings.
- Owner marks useful directions.
- Useful findings are promoted into formal GENERAL_TASK / TASK / STAGE records.
- Rejected findings remain preserved to prevent repeated mistakes.

---

PASTE KIRO RESPONSE BELOW THIS LINE.

Understood.

Начинаю hard red-team audit для Act 5 readiness. Сначала мне нужно инспектировать ключевые области репозитория.

Теперь инспектирую ключевые области для Act 5 audit.

Теперь у меня достаточно информации для составления полного red-team audit. Продолжаю анализ.

Теперь у меня достаточно информации для полного red-team audit. Составляю ответ.

---

# IMPERIUM Act 5 Readiness — Hard Red-Team Architecture Audit

**HEAD**: `71279657d64e1023acf47d923e20b217daabdd89` (commit 63)
**Дата аудита**: 2026-05-13
**Режим**: Read-only architectural research

---

## 1. Короткий verdict

**Act 5 NOT READY — ready after P0 prerequisites**

Репозиторий находится в состоянии **PASS_WITH_WARNINGS** с 117,615 warnings (warning flood). Архитектура task registration corridor существует и формально корректна. GENERAL_TASK для Inquisition зарегистрирован, декомпозирован на 10 TASK candidates, stage map draft создан. Однако:

1. **READY_FOR_AGENT = false** by design — review responses не получены, task modernization отсутствует
2. **Warning flood** делает PASS_WITH_WARNINGS бессмысленным — невозможно отличить новые проблемы от legacy debt
3. **CURRENT_STATE stale** — указывает на задачу от 2026-05-10, не синхронизирован с HEAD
4. **Первые 4 органа просветления** не достигли operational status — все в BOOTSTRAP/SCAFFOLD
5. **Sanctum** помечен как SUPER_EXPERIMENTAL — кнопки не тестируются, action registry отсутствует
6. **Servitor long-session continuation** не реализован — нет WORK_SESSION schema

**Минимальный путь к Act 5**: исправить P0 blockers (warning budget, CURRENT_STATE sync, advisory response ingest), затем Owner approval stage map.

---

## 2. Что было проверено

### Repo zones inspected:
- Root: `AGENTS.md`, `START_HERE.md`, `README.md`
- `CURRENT_STATE/` — stale, указывает на 2026-05-10
- `DOCS/ACT3_*`, `DOCS/ACT4_*` — актуальны
- `REGISTRY/ORGAN_REGISTRY.json`, `REGISTRY/SCRIPT_REGISTRY.json`
- `schemas/*.schema.json`
- `scripts/verify_repo.py` — выполнен, 117,615 warnings
- `ORGANS/ASTRONOMICON/REGISTRY/` — GENERAL_TASKS, TASK_CANDIDATES, STAGE_MAPS, READY_FOR_AGENT
- `ORGANS/ASTRONOMICON/ADVISORY_BUFFER/`
- `ORGANS/{DOCTRINARIUM,ADMINISTRATUM,OFFICIO_AGENTIS,ASTRONOMICON,INQUISITION}/ORGAN_STATUS.json`
- `SANCTUM/sanctum_v0_29_qt.py`, `SANCTUM/README_SANCTUM_EXPERIMENTAL_STATUS.md`

### Important files inspected:
- `READY-FOR-AGENT-20260513-INQUISITION-V0_1-SELF-BUILD-BLOCKED-V0_2.json` — `ready_for_agent: false`
- `GENERAL-TASK-20260513-BUILD-INQUISITION-V0_1-SELF-DESCRIPTIVE-ORGAN.json` — status: `REGISTERED_FOR_DECOMPOSITION`
- `STAGE-MAP-DRAFT-20260513-INQUISITION-001-BLUEPRINT-V0_1.json` — 10 stages, status: `DRAFT_NEEDS_REVIEW`
- 10 TASK candidates — all `REGISTERED_CANDIDATE_NEEDS_REVIEW`, `ready_for_agent: false`

### Files that appear stale or missing:
- `CURRENT_STATE/LAST_POINT_STATE.json` — указывает на `TASK-20260510-*`, не обновлён после 3 дней коммитов
- `CURRENT_STATE/NEXT_ATOMIC_STEP.md` — stale
- `START_HERE.md` — указывает на `TASK-20260510-*`
- Missing: `ORGANS/INQUISITION/ORGAN_CONTRACT.json`
- Missing: `ORGANS/ASTRONOMICON/ORGAN_CONTRACT.json`
- Missing: unified `SERVITOR_WORKFLOW_CONTRACT.md`
- Missing: `WORK_SESSION.schema.json`
- Missing: `STAGE_PROGRESS_REPORT.schema.json`

---

## 3. Главные blockers перед Аркой 5

### P0 Blockers (must fix before any Act 5 work)

| # | Blocker | Impact | Fix |
|---|---------|--------|-----|
| 1 | **Warning flood: 117,615 warnings** | PASS_WITH_WARNINGS meaningless, cannot detect new issues | Implement warning budget, classify legacy vs new |
| 2 | **CURRENT_STATE stale** | New Servitor reads wrong entrypoint | Sync CURRENT_STATE with HEAD after each major commit |
| 3 | **Advisory responses not ingested** | READY_FOR_AGENT blocked by design | Complete TASK-CANDIDATE-002 (review pack export) and TASK-CANDIDATE-003 (advisory ingest) |
| 4 | **Task modernization missing** | Cannot approve stage map without reconciled advisory | Complete TASK-CANDIDATE-004 |
| 5 | **Stage map not approved** | READY_FOR_AGENT gate requires Owner approval | Owner must review and approve stage map |

### P1 Blockers (should fix before first self-build task)

| # | Blocker | Impact | Fix |
|---|---------|--------|-----|
| 6 | **First 4 organs not operational** | Cannot guide Servitor properly | Bring Doctrinarium, Administratum, Officio Agentis, Astronomicon to MINIMAL_OPERATIONAL |
| 7 | **Missing ORGAN_CONTRACT.json** for Astronomicon, Inquisition | Organ boundaries undefined | Create contracts from schema |
| 8 | **Sanctum action registry missing** | Buttons not testable | Create ACTION_REGISTRY.json, wire buttons |
| 9 | **No Servitor long-session model** | Owner must restart Servitor repeatedly | Create WORK_SESSION schema and Administratum ACK flow |
| 10 | **Registry drift** | ORGAN_REGISTRY claims scripts that may not exist | Run registry sync checker |

### P2 Blockers (can defer but creates risk)

| # | Blocker | Impact | Fix |
|---|---------|--------|-----|
| 11 | **Sanctum raw subprocess** | Bypasses command gateway | Migrate to gateway |
| 12 | **Visual factory missing** | UI changes break runtime | Create ASSETS/DESIGN_SYSTEM/UI_LAB skeleton |
| 13 | **Missing 4 organs** | Custodes, Strategium, Schola, Throne are scaffolds only | Defer to post-Inquisition |

---

## 4. Current truth / stale truth map

### Current truth files (reliable at HEAD 7127965):
```
AGENTS.md                                          ✓ current
DOCS/ACT3_ADDRESS_TRUTH_CAPABILITY_SPINE_SEED_20260513.md  ✓ current
DOCS/ACT4_FULL_REGISTRATION_CORRIDOR_SEED_20260513.md      ✓ current
DOCS/ACT4_INQUISITION_GENERAL_TASK_DECOMPOSITION_20260513.md ✓ current
SANCTUM/README_SANCTUM_EXPERIMENTAL_STATUS.md      ✓ current
ORGANS/ASTRONOMICON/REGISTRY/GENERAL_TASKS/*.json  ✓ current
ORGANS/ASTRONOMICON/REGISTRY/TASK_CANDIDATES/*.json ✓ current
ORGANS/ASTRONOMICON/REGISTRY/STAGE_MAPS/*.json     ✓ current
ORGANS/ASTRONOMICON/REGISTRY/READY_FOR_AGENT/*.json ✓ current
REGISTRY/SCRIPT_REGISTRY.json                      ✓ current (but may drift)
schemas/*.schema.json                              ✓ current
```

### Stale files (need update):
```
CURRENT_STATE/LAST_POINT_STATE.json    ✗ stale (points to 2026-05-10)
CURRENT_STATE/NEXT_ATOMIC_STEP.md      ✗ stale
START_HERE.md                          ✗ stale (points to 2026-05-10)
ORGANS/*/ORGAN_STATUS.json             ⚠ partially stale (not updated after Act 3/4)
```

### Missing entrypoint files:
```
CURRENT_STATE/ACT5_READINESS_STATE.json           missing
DOCS/SERVITOR_ENTRYPOINT_CONTRACT.md              missing
ORGANS/INQUISITION/ORGAN_CONTRACT.json            missing
ORGANS/ASTRONOMICON/ORGAN_CONTRACT.json           missing
schemas/work_session.schema.json                  missing
schemas/stage_progress_report.schema.json         missing
```

### How to fix state continuity:

1. **After each major commit**, run:
   ```powershell
   py -3 scripts/verify_repo.py
   # Update CURRENT_STATE/LAST_POINT_STATE.json with:
   # - current_task
   # - last_completed_task
   # - current HEAD
   # - current blockers
   ```

2. **Create CURRENT_STATE refresh script**:
   ```
   TOOLS/refresh_current_state.py
   - reads git HEAD
   - reads latest READY_FOR_AGENT gate
   - reads latest verification report
   - writes CURRENT_STATE/LAST_POINT_STATE.json
   ```

---

## 5. Идеальная архитектура TASK_ID / GENERAL_TASK / TASK / STAGE

### Lifecycle state machine:

```
OWNER_TEXT (structured markdown)
    │
    ▼
RAW_INTAKE (parsed, not validated)
    │
    ▼
GENERAL_TASK_DRAFT (human-readable .md)
    │
    ▼
GENERAL_TASK_REGISTERED (machine-readable .json)
    │ status: REGISTERED_NOT_DECOMPOSED
    ▼
TASK_CANDIDATES_CREATED
    │ status: REGISTERED_CANDIDATE_NEEDS_REVIEW
    │ ready_for_agent: false
    ▼
REVIEW_PACK_EXPORTED
    │ exported to Speculum/Kiro
    ▼
ADVISORY_RESPONSES_INGESTED
    │ status: ADVISORY_INGESTED
    ▼
TASK_MODERNIZATION_COMPLETE
    │ accepted/rejected recommendations recorded
    ▼
STAGE_MAP_DRAFT_CREATED
    │ status: DRAFT_NEEDS_REVIEW
    ▼
STAGE_MAP_APPROVED
    │ Owner approval recorded
    ▼
READY_FOR_AGENT_TRUE
    │ all gates pass
    ▼
SERVITOR_EXECUTION
    │ stage-by-stage with receipts
    ▼
TASK_COMPLETE
    │ all stages pass
    ▼
OWNER_VERDICT
    │ ACCEPTED / REJECTED / NEEDS_REWORK
    ▼
ARCHIVE / NEXT_TASK
```

### Folder structure:

```
ORGANS/ASTRONOMICON/REGISTRY/
├── CORRIDOR/
│   └── ACT4_REGISTRATION_CORRIDOR_V0_1.json
├── GENERAL_TASKS/
│   ├── GENERAL-TASK-{DATE}-{NAME}-DRAFT.md
│   └── GENERAL-TASK-{DATE}-{NAME}.json
├── TASK_CANDIDATES/
│   ├── README.md
│   └── TASK-CANDIDATE-{DATE}-{NAME}-{NNN}-{SUBTASK}-V0_1.json
├── REVIEW_PACKS/
│   ├── README.md
│   ├── REVIEW-PACK-{DATE}-{NAME}-{REVIEWER}-V0_1.json
│   └── REVIEW-PACK-{DATE}-{NAME}-{REVIEWER}-V0_1.md
├── ADVISORY_INPUTS/
│   └── ADVISORY-{DATE}-{SOURCE}-{NAME}-V0_1.json
├── ADVISORY_RESPONSES/
│   └── ADVISORY-RESPONSE-{DATE}-{SOURCE}-{NAME}-V0_1.json
├── TASK_MODERNIZATIONS/
│   └── TASK-MODERNIZATION-{DATE}-{NAME}-V0_1.json
├── STAGE_MAPS/
│   ├── README.md
│   └── STAGE-MAP-{STATUS}-{DATE}-{NAME}-V0_1.json
└── READY_FOR_AGENT/
    ├── README.md
    └── READY-FOR-AGENT-{DATE}-{NAME}-{STATUS}-V0_N.json
```

### Status vocabulary (unified):

**GENERAL_TASK status:**
- `REGISTERED_NOT_DECOMPOSED`
- `REGISTERED_FOR_DECOMPOSITION`
- `DECOMPOSED_TO_TASK_CANDIDATES`
- `UNDER_REVIEW`
- `REFINED`
- `BLOCKED`
- `ARCHIVED`

**TASK_CANDIDATE status:**
- `REGISTERED_CANDIDATE_NEEDS_REVIEW`
- `REVIEW_PACK_EXPORTED`
- `ADVISORY_INGESTED`
- `MODERNIZED`
- `APPROVED`
- `BLOCKED`
- `REJECTED`

**STAGE_MAP status:**
- `DRAFT_NEEDS_REVIEW`
- `UNDER_REVIEW`
- `APPROVED`
- `BLOCKED`

**READY_FOR_AGENT status:**
- `BLOCKED_PENDING_REVIEW_AND_MODERNIZATION`
- `BLOCKED_PENDING_OWNER_APPROVAL`
- `READY`

### Example fields for GENERAL_TASK:

```json
{
  "schema_version": "imperium.general_task.v0_1",
  "general_task_id": "GENERAL-TASK-20260513-BUILD-INQUISITION-V0_1",
  "title": "Build Inquisition v0.1",
  "status": "REGISTERED_FOR_DECOMPOSITION",
  "current_phase": "DECOMPOSED_TO_TASK_CANDIDATES",
  "owner_intent": "...",
  "base_git_truth": {
    "repo": "https://github.com/...",
    "head": "71279657...",
    "exact_tree_url": "https://github.com/.../tree/71279657...",
    "commit_count": 63
  },
  "decomposition_outputs": {
    "task_candidates": ["..."],
    "first_stage_map_draft": "...",
    "review_pack": "...",
    "ready_for_agent_gate": "..."
  },
  "next_required_phase": "REVIEW_RESPONSES_REQUIRED",
  "ready_for_agent": false
}
```

---

## 6. Manual Owner text -> full registration corridor

### Step-by-step flow:

```
1. OWNER WRITES STRUCTURED TEXT
   ├── Location: ORGANS/ASTRONOMICON/REGISTRY/GENERAL_TASKS/
   ├── Format: GENERAL-TASK-{DATE}-{NAME}-DRAFT.md
   └── Contains: title, intent, scope, non-goals, context files

2. ASTRONOMICON PARSES TO JSON
   ├── Script: TOOLS/astronomicon_parse_general_task_v0_2.ps1
   ├── Output: GENERAL-TASK-{DATE}-{NAME}.json
   └── Status: REGISTERED_NOT_DECOMPOSED

3. ASTRONOMICON DECOMPOSES TO TASK CANDIDATES
   ├── Script: TOOLS/astronomicon_decompose_local_task_to_stages_v0_2.ps1
   ├── Output: TASK-CANDIDATE-{DATE}-{NAME}-{NNN}-*.json
   └── Status: REGISTERED_CANDIDATE_NEEDS_REVIEW

4. REVIEW PACK EXPORTED
   ├── Output: REVIEW-PACK-{DATE}-{NAME}-SPECULUM-KIRO-V0_1.json
   ├── Output: REVIEW-PACK-{DATE}-{NAME}-SPECULUM-KIRO-V0_1.md
   └── Contains: targeted questions for Kiro/Speculum

5. ADVISORY RESPONSES INGESTED
   ├── Input: Kiro/Speculum advisory output
   ├── Output: ADVISORY-RESPONSE-{DATE}-{SOURCE}-{NAME}-V0_1.json
   └── Status: ADVISORY_INGESTED

6. TASK MODERNIZATION
   ├── Output: TASK-MODERNIZATION-{DATE}-{NAME}-V0_1.json
   ├── Contains: accepted/rejected recommendations
   └── Status: MODERNIZED

7. STAGE MAP CREATED
   ├── Output: STAGE-MAP-DRAFT-{DATE}-{NAME}-V0_1.json
   └── Status: DRAFT_NEEDS_REVIEW

8. OWNER REVIEWS STAGE MAP
   ├── Owner reads stage map
   ├── Owner approves or requests changes
   └── Status: APPROVED (if approved)

9. READY_FOR_AGENT GATE
   ├── Output: READY-FOR-AGENT-{DATE}-{NAME}-V0_N.json
   ├── Checks: all required evidence present
   └── ready_for_agent: true (if all pass)

10. SERVITOR EXECUTION
    ├── Servitor reads stage map
    ├── Executes stage-by-stage
    ├── Creates receipts per stage
    └── Reports progress to Administratum

11. OWNER VERDICT
    ├── Owner reviews final output
    └── ACCEPTED / REJECTED / NEEDS_REWORK
```

---

## 7. Первые 4 органа просветления

### Readiness matrix:

| Organ | Declared Status | Real Status | ORGAN_CONTRACT | ORGAN_STATUS | Scripts | Ports | Dashboard | Act 5 Ready |
|-------|-----------------|-------------|----------------|--------------|---------|-------|-----------|-------------|
| Doctrinarium | STRICT_BOOTSTRAP_GATE | BOOTSTRAP | ✓ exists | ✓ exists | partial | partial | ✗ | ⚠ needs work |
| Administratum | BOOTSTRAP | BOOTSTRAP | ✓ exists | ✓ exists | ✓ good | partial | ✗ | ⚠ needs work |
| Officio Agentis | MINIMAL_SCOPE_ACTIVE | MINIMAL | ✗ missing | ✓ exists | minimal | minimal | ✗ | ⚠ needs work |
| Astronomicon | ORGAN_SCAFFOLD_0_1 | SCAFFOLD | ✗ missing | ✓ exists | ✓ good | ✓ good | ✓ exists | ⚠ needs contract |

### Required unified organ form:

```
ORGANS/<ORGAN>/
├── README.md                    # human-readable overview
├── ORGAN_CONTRACT.json          # machine-readable contract (required)
├── ORGAN_STATUS.json            # current operational status
├── ORGAN_SELF_REPORT.json       # latest self-report (optional)
├── PORTS/
│   ├── *.schema.json            # port message schemas
│   └── *_PORT.json              # port configurations
├── SCHEMAS/
│   └── *.schema.json            # organ-specific schemas
├── SCRIPTS/
│   └── *.py / *.ps1             # organ-owned scripts
├── CHECKS/
│   └── check_*.py               # organ-specific checkers
├── RECEIPTS/
│   └── *.json                   # runtime receipts (gitignored)
├── REPORTS/
│   └── *.json                   # generated reports
├── UTILITY/ or DASHBOARD/
│   └── *.py / *.ps1             # utility scripts or dashboard
└── TESTS/
    └── test_*.py                # organ-specific tests
```

### Missing pieces per organ:

**Doctrinarium:**
- Missing: `ORGAN_CONTRACT.json` (has old format)
- Missing: `CHECKS/` folder
- Missing: `TESTS/` folder
- Blocker: `canon_for_real_task_execution: false`

**Administratum:**
- Missing: `CHECKS/` folder
- Missing: `TESTS/` folder
- Has: good registry structure under `REGISTRY/`

**Officio Agentis:**
- Missing: `ORGAN_CONTRACT.json`
- Missing: `SCHEMAS/` content
- Missing: `CHECKS/` folder
- Missing: `TESTS/` folder
- Status too minimal

**Astronomicon:**
- Missing: `ORGAN_CONTRACT.json`
- Missing: `CHECKS/` folder
- Missing: `TESTS/` folder
- Has: good registry structure, dashboard exists

### Minimal Act 5-ready definition:

For each of the first 4 organs to be "Act 5 ready":
1. `ORGAN_CONTRACT.json` exists and validates against schema
2. `ORGAN_STATUS.json` reflects real operational state
3. At least one working script registered in SCRIPT_REGISTRY
4. At least one port schema exists
5. Can respond to basic queries (preflight, status, map)

---

## 8. Astronomicon Advisory Buffer

### Correct ownership:
**Astronomicon** owns the advisory buffer. This is correct because:
- Astronomicon owns task planning and registration
- Advisory inputs feed into task decomposition
- Promotion to GENERAL_TASK is Astronomicon's responsibility

### Lifecycle:

```
RAW_ADVISORY
    │ external input (Kiro, Speculum, Owner idea)
    ▼
REGISTERED_RAW_ADVISORY
    │ stored in ADVISORY_BUFFER/{SOURCE}/{DATE}/
    ▼
REVIEWED
    │ Owner or Doctrinarium reviewed
    ▼
OWNER_MARKED_USEFUL / OWNER_MARKED_NOT_USEFUL
    │
    ├─► PROMOTION_CANDIDATE (if useful)
    │       │
    │       ▼
    │   PROMOTED_TO_GENERAL_TASK
    │       │
    │       ▼
    │   (enters registration corridor)
    │
    └─► REJECTED / ARCHIVED (if not useful)
            │
            ▼
        ADVISORY_BUFFER/REJECTED/ (preserved for learning)
```

### Schemas/manifests needed:

**ADVISORY_MANIFEST.json:**
```json
{
  "schema_version": "imperium.advisory_manifest.v0_1",
  "advisory_id": "ADVISORY-20260513-KIRO-VISUAL-AUDIT-V0_1",
  "source": "KIRO",
  "source_date": "2026-05-13",
  "title": "Assets/Visual/UI Factory Audit",
  "status": "REGISTERED_RAW_ADVISORY",
  "file_path": "ADVISORY_BUFFER/KIRO/20260513/KIRO_ASSETS_VISUAL_UI_FACTORY_AUDIT_20260513.md",
  "owner_verdict": null,
  "promotion_status": null,
  "promoted_to": null,
  "rejection_reason": null
}
```

**ADVISORY_LEDGER.json:**
```json
{
  "schema_version": "imperium.advisory_ledger.v0_1",
  "entries": [
    {
      "advisory_id": "...",
      "status": "...",
      "owner_verdict": "...",
      "promoted_to": "..."
    }
  ]
}
```

### Promotion rules:
1. Raw advisory is NOT doctrine until Owner marks useful
2. Promotion requires explicit Owner decision
3. Promoted advisory becomes GENERAL_TASK draft
4. Rejected advisory preserved in `REJECTED/` with reason
5. Administratum indexes but does not authorize promotion
6. Doctrinarium prevents advisory from becoming canon without reconciliation

---

## 9. Sanctum architecture

### Current problem:
- Sanctum is `SUPER_EXPERIMENTAL_TRANSITIONAL_OPERATOR_DASHBOARD`
- Buttons execute raw subprocess calls, not through command gateway
- No action registry — buttons are hardcoded
- No UI tests — cannot prove buttons work
- Visual changes mixed with runtime logic
- EE/R1/R2 rejected but lessons not extracted

### Target dashboard architecture:

```
SANCTUM/
├── RUNTIME/
│   ├── sanctum_core.py              # state management, no UI
│   ├── action_executor.py           # executes actions through gateway
│   └── state_builder.py             # builds dashboard state from sources
├── ACTIONS/
│   ├── ACTION_REGISTRY.json         # registered actions with gates
│   └── action_handlers/
│       ├── git_check.py
│       ├── bundle_fetch.py
│       └── transfer_prompt.py
├── DASHBOARD_MODULES/
│   ├── organ_hud.py                 # organ status display
│   ├── transfer_panel.py            # VM2 transfer controls
│   ├── task_corridor.py             # registration corridor view
│   └── bundle_list.py               # bundle listing
├── DESIGN_SYSTEM/
│   ├── DESIGN_TOKENS.json
│   ├── VISUAL_BUDGET.json
│   └── components/
├── UI_LAB/
│   ├── prototypes/
│   ├── golden_screenshots/
│   └── tools/
├── TESTS/
│   ├── test_action_registry.py
│   ├── test_state_builder.py
│   └── test_ui_smoke.py
├── RECEIPTS/
│   └── (gitignored runtime receipts)
└── sanctum_launcher.py              # entry point
```

### Runtime/UI separation:

```
┌─────────────────────────────────────────────────────────────────┐
│                    UI LAYER (can change visuals)                │
│  sanctum_v0_29_qt.py → reads state, sends intents               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ STATE_CONTRACT.json (read)
                              │ INTENT (write)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ACTION REGISTRY                              │
│  ACTION_REGISTRY.json → maps button_id to action_id             │
│  action_executor.py → validates intent, checks gates            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    COMMAND GATEWAY                              │
│  src/imperium/security/command_gateway.py                       │
│  REGISTRY/COMMAND_ALLOWLIST.json                                │
└─────────────────────────────────────────────────────────────────┘
```

### ACTION_REGISTRY.json example:

```json
{
  "schema_version": "imperium.action_registry.v0_1",
  "actions": [
    {
      "action_id": "ACTION-GIT-CLI-CHECK",
      "button_id": "btn_git_check",
      "label": "Run Git CLI Check",
      "script_id": "SCRIPT-ADMINISTRATUM-GIT-CLI-CHECK-PS1-V0_1",
      "gates": ["git_available"],
      "dangerous": false,
      "requires_owner_approval": false,
      "receipt_path": ".imperium_runtime/administratum/git_cli_check/"
    },
    {
      "action_id": "ACTION-FETCH-BUNDLE",
      "button_id": "btn_fetch_bundle",
      "label": "Fetch Bundle from VM2",
      "script_id": "SCRIPT-REVIEW-WORKER-BUNDLE-INTAKE-PS1-V0_1",
      "gates": ["ssh_route_available", "bundle_selected"],
      "dangerous": true,
      "requires_owner_approval": true,
      "receipt_path": ".imperium_runtime/bundle_intake_review/"
    }
  ]
}
```

### Testable buttons (first 5):

| Button | Action ID | Test | Status |
|--------|-----------|------|--------|
| Refresh State | ACTION-REFRESH-STATE | state_builder returns valid JSON | ⚠ needs test |
| Git CLI Check | ACTION-GIT-CLI-CHECK | receipt created, verdict returned | ⚠ needs test |
| Test Route | ACTION-TEST-ROUTE | SSH connection succeeds | ⚠ needs test |
| List Bundles | ACTION-LIST-BUNDLES | bundle list returned | ⚠ needs test |
| Send Prompt | ACTION-SEND-PROMPT | file transferred to VM2 | ⚠ needs test |

### What NOT to do:
- Do NOT revive EE/R1/R2
- Do NOT replace working operator behavior with visual rewrite
- Do NOT call generic HTML page "Sanctum Dashboard"
- Do NOT add buttons without ACTION_REGISTRY entry
- Do NOT execute commands without command gateway
- Do NOT mix visual changes with runtime logic changes

---

## 10. Visual factory integration

### Minimum visual factory v0.1 plan:

```
E:\IMPERIUM\ASSETS\
├── README.md
├── ASSET_MANIFEST.json
├── OWNER_VISUAL_PREFERENCES.md
├── screenshots/
│   ├── accepted/
│   │   └── sanctum_v0_29_baseline.png
│   └── rejected/
│       └── sanctum_ee_r2_rejected.png

E:\IMPERIUM\SANCTUM\DESIGN_SYSTEM\
├── README.md
├── DESIGN_TOKENS.json
├── VISUAL_BUDGET.json
└── components/
    └── (empty for now)

E:\IMPERIUM\SANCTUM\UI_LAB\
├── README.md
├── UI_EXPERIMENT_LEDGER.json
├── integration_checklist.md
├── golden_screenshots/
│   └── GOLDEN_MANIFEST.json
├── prototypes/
│   └── .gitkeep
└── tools/
    ├── validate_prototype.py
    └── generate_diff.py
```

### Design token files (minimal):

**DESIGN_TOKENS.json:**
```json
{
  "version": "0.1.0",
  "colors": {
    "background": { "primary": "#06111d", "secondary": "#092033" },
    "text": { "primary": "#defcff", "muted": "#7eb8c7" },
    "status": {
      "pass": "#28ffb7",
      "warn": "#ffcf4a",
      "fail": "#ff5f86"
    }
  },
  "spacing": { "xs": 4, "sm": 8, "md": 12, "lg": 16 },
  "borders": { "radius": { "sm": 4, "md": 8 } }
}
```

### Visual delta budget:

**VISUAL_BUDGET.json:**
```json
{
  "budgets": {
    "spacing_change_max_px": 4,
    "border_radius_max": 8,
    "new_colors_per_version": 2,
    "animation_duration_max_ms": 300
  },
  "forbidden_without_approval": [
    "layout_grid_change",
    "navigation_structure_change",
    "font_family_change"
  ]
}
```

### Checks that block visual changes touching runtime:

```python
# tools/runtime_isolation_check.py
RUNTIME_FILES = [
    "sanctum_core.py",
    "action_executor.py",
    "command_gateway.py",
    "handlers/*.py"
]

UI_FILES = [
    "sanctum_v0_29_qt.py",
    "DESIGN_SYSTEM/",
    "UI_LAB/"
]

def check_isolation():
    # If git diff shows changes to both RUNTIME_FILES and UI_FILES
    # in same commit → BLOCKED
    pass
```

---

## 11. Verification / no-fake-green gates

### Mandatory checks before Act 5:
Продолжаю.

---

## 11. Verification / no-fake-green gates (продолжение)

### Mandatory checks before Act 5:

| Check | Current Status | Required Status | Blocker? |
|-------|----------------|-----------------|----------|
| `verify_repo.py` | PASS_WITH_WARNINGS (117,615) | PASS or PASS_WITH_WARNINGS (<100) | **P0** |
| `check_act3_address_truth_capability_spine` | exists | PASS | P1 |
| `check_act4_registration_corridor` | exists | PASS | P1 |
| `check_agent_entrypoint` | exists | PASS | P1 |
| `check_general_task_registration` | exists | PASS | P1 |
| READY_FOR_AGENT gate | false | true (after review) | **P0** |
| CURRENT_STATE sync | stale | current | **P0** |

### Warning budget policy:

**Current problem:** 117,615 warnings makes PASS_WITH_WARNINGS meaningless.

**Proposed policy:**

```json
{
  "warning_budget": {
    "legacy_debt_baseline": 117000,
    "new_warnings_allowed": 100,
    "categories": {
      "continuity_packs": "LEGACY_ACCEPTED",
      "encoding_mojibake": "LEGACY_ACCEPTED",
      "stale_references": "WARNING",
      "path_mismatch": "WARNING",
      "raw_subprocess": "WARNING_MUST_FIX",
      "missing_receipt": "WARNING",
      "fake_green_risk": "BLOCKER",
      "advisory_as_doctrine": "BLOCKER"
    }
  }
}
```

**Implementation:**
1. Create `WARNING_BUDGET.json` in `REGISTRY/`
2. Modify `verify_repo.py` to classify warnings
3. Report: `PASS_WITH_LEGACY_DEBT` vs `PASS_WITH_NEW_WARNINGS` vs `FAIL`

### PASS/WARN/BLOCKED semantics:

| Verdict | Meaning | Action |
|---------|---------|--------|
| `PASS` | No blockers, no warnings | Proceed |
| `PASS_WITH_LEGACY_DEBT` | Only legacy warnings within budget | Proceed with note |
| `PASS_WITH_NEW_WARNINGS` | New warnings detected | Review before proceed |
| `FAIL` | Blockers detected | Stop, fix blockers |
| `BLOCKED` | Policy prevented execution | Cannot proceed |

### Inquisition no-fake-green enforcement requirements:

Inquisition v0.1 must check:
1. **READY_FOR_AGENT claims** — verify evidence_refs exist
2. **Status claims** — verify declared status matches real state
3. **Receipt claims** — verify receipts are machine-readable and valid
4. **Advisory-as-doctrine** — flag raw advisory treated as canon
5. **Stale HEAD** — flag references to old commits
6. **Missing files** — flag evidence_refs pointing to non-existent files

### Checks to add before self-build:

```
scripts/check_ready_for_agent_evidence.py
  - verify all evidence_refs in READY_FOR_AGENT gate exist
  - verify required_checks have corresponding receipts

scripts/check_organ_status_truth.py
  - compare ORGAN_STATUS.json declared status with real files
  - flag drift between declared and actual

scripts/check_warning_budget.py
  - classify warnings into legacy vs new
  - fail if new warnings exceed budget

TOOLS/check_current_state_sync.py
  - verify CURRENT_STATE matches HEAD
  - flag stale entrypoints
```

---

## 12. Servitor long-session continuation

### WORK_SESSION schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "IMPERIUM Work Session v0.1",
  "type": "object",
  "required": [
    "schema_version",
    "work_session_id",
    "task_id",
    "stage_range",
    "started_at_utc",
    "servitor_id",
    "status",
    "current_stage",
    "completed_stages",
    "pending_stages"
  ],
  "properties": {
    "schema_version": { "const": "imperium.work_session.v0_1" },
    "work_session_id": { "type": "string" },
    "task_id": { "type": "string" },
    "stage_range": {
      "type": "object",
      "properties": {
        "start": { "type": "string" },
        "end": { "type": "string" }
      }
    },
    "started_at_utc": { "type": "string", "format": "date-time" },
    "servitor_id": { "type": "string" },
    "status": {
      "type": "string",
      "enum": [
        "IN_PROGRESS",
        "AWAITING_ACK",
        "CONTINUED",
        "STOPPED_BY_OWNER",
        "COMPLETED",
        "FAILED"
      ]
    },
    "current_stage": { "type": "string" },
    "completed_stages": {
      "type": "array",
      "items": { "type": "string" }
    },
    "pending_stages": {
      "type": "array",
      "items": { "type": "string" }
    },
    "progress_reports": {
      "type": "array",
      "items": { "$ref": "#/definitions/progress_report" }
    },
    "administratum_acks": {
      "type": "array",
      "items": { "$ref": "#/definitions/administratum_ack" }
    }
  },
  "definitions": {
    "progress_report": {
      "type": "object",
      "required": ["stage_id", "status", "timestamp_utc"],
      "properties": {
        "stage_id": { "type": "string" },
        "status": { "type": "string" },
        "timestamp_utc": { "type": "string" },
        "outputs": { "type": "array" },
        "receipts": { "type": "array" },
        "blockers": { "type": "array" },
        "next_stage": { "type": "string" }
      }
    },
    "administratum_ack": {
      "type": "object",
      "required": ["ack_id", "decision", "timestamp_utc"],
      "properties": {
        "ack_id": { "type": "string" },
        "decision": {
          "type": "string",
          "enum": ["CONTINUE_ALLOWED", "STOP_OWNER_REQUIRED", "BLOCKED"]
        },
        "timestamp_utc": { "type": "string" },
        "reason": { "type": "string" },
        "owner_notified": { "type": "boolean" }
      }
    }
  }
}
```

### STAGE_PROGRESS_REPORT schema:

```json
{
  "schema_version": "imperium.stage_progress_report.v0_1",
  "report_id": "PROGRESS-20260513-INQUISITION-001-STAGE-003-V0_1",
  "work_session_id": "WORK-SESSION-20260513-001",
  "task_id": "TASK-CANDIDATE-20260513-INQUISITION-001-BLUEPRINT-V0_1",
  "stage_id": "STAGE-003-DEFINE-RESPONSIBILITIES",
  "status": "COMPLETED",
  "timestamp_utc": "2026-05-13T10:30:00Z",
  "outputs": [
    "ORGANS/INQUISITION/BLUEPRINT/responsibilities.json"
  ],
  "receipts": [
    ".imperium_runtime/inquisition/STAGE-003-RECEIPT.json"
  ],
  "pass_criteria_met": [
    "At least 5 responsibilities defined",
    "At least 5 forbidden actions defined"
  ],
  "blockers": [],
  "warnings": [],
  "next_stage": "STAGE-004-DEFINE-ZONES",
  "continuation_request": {
    "requested": true,
    "reason": "Stage completed successfully, ready for next stage"
  }
}
```

### ADMINISTRATUM_ACK schema:

```json
{
  "schema_version": "imperium.administratum_ack.v0_1",
  "ack_id": "ACK-20260513-WORK-SESSION-001-003",
  "work_session_id": "WORK-SESSION-20260513-001",
  "progress_report_id": "PROGRESS-20260513-INQUISITION-001-STAGE-003-V0_1",
  "decision": "CONTINUE_ALLOWED",
  "timestamp_utc": "2026-05-13T10:31:00Z",
  "validation": {
    "receipts_valid": true,
    "outputs_exist": true,
    "pass_criteria_verified": true,
    "no_blockers": true
  },
  "reason": "Stage 003 completed successfully. All pass criteria met. No blockers.",
  "next_allowed_stage": "STAGE-004-DEFINE-ZONES",
  "owner_notified": false,
  "owner_approval_required": false
}
```

### Continuation workflow:

```
┌─────────────────────────────────────────────────────────────────┐
│ SERVITOR completes STAGE-N                                      │
│ Creates STAGE_PROGRESS_REPORT                                   │
│ Sends to ADMINISTRATUM                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ ADMINISTRATUM validates:                                        │
│ - receipts exist and valid                                      │
│ - outputs exist                                                 │
│ - pass criteria met                                             │
│ - no blockers                                                   │
│ - stage within approved range                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ALL PASS         WARNINGS       BLOCKERS
              │               │               │
              ▼               ▼               ▼
    CONTINUE_ALLOWED   CONTINUE_ALLOWED   STOP_OWNER_REQUIRED
    (auto)             (with note)        (escalate)
              │               │               │
              ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│ ADMINISTRATUM creates ACK                                       │
│ Writes to WORK_SESSION                                          │
│ Returns decision to SERVITOR                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
    CONTINUE_ALLOWED                 STOP_OWNER_REQUIRED
              │                               │
              ▼                               ▼
    SERVITOR proceeds              SERVITOR stops
    to STAGE-N+1                   Waits for Owner
```

### Stop/escalation conditions:

| Condition | Decision | Action |
|-----------|----------|--------|
| Stage completed, all pass | CONTINUE_ALLOWED | Auto-continue |
| Stage completed, warnings | CONTINUE_ALLOWED | Continue with note |
| Stage completed, owner_decision_gate | STOP_OWNER_REQUIRED | Wait for Owner |
| Stage failed, recoverable | STOP_OWNER_REQUIRED | Escalate |
| Stage failed, blocker | BLOCKED | Stop session |
| Stage outside approved range | BLOCKED | Stop session |
| Dangerous action detected | STOP_OWNER_REQUIRED | Escalate |

### Sanctum display:

```
┌─────────────────────────────────────────────────────────────────┐
│ WORK SESSION: WORK-SESSION-20260513-001                         │
│ Task: TASK-CANDIDATE-20260513-INQUISITION-001-BLUEPRINT-V0_1    │
│ Status: IN_PROGRESS                                             │
├─────────────────────────────────────────────────────────────────┤
│ Stages:                                                         │
│ [✓] STAGE-001-READ-SCHEMAS          COMPLETED                   │
│ [✓] STAGE-002-DRAFT-BLUEPRINT       COMPLETED                   │
│ [✓] STAGE-003-DEFINE-RESPONSIBILITIES COMPLETED                 │
│ [►] STAGE-004-DEFINE-ZONES          IN_PROGRESS                 │
│ [ ] STAGE-005-DEFINE-AUDIT-CATEGORIES PENDING                   │
│ ...                                                             │
├─────────────────────────────────────────────────────────────────┤
│ Latest ACK: CONTINUE_ALLOWED (2026-05-13 10:31)                 │
│ Next: STAGE-004-DEFINE-ZONES                                    │
│                                                                 │
│ [Stop Session] [View Receipts] [View Progress]                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 13. Inquisition v0.1 self-build architecture

### Purpose:

Inquisition v0.1 is the **audit and cleanup organ** responsible for:
- Detecting drift, duplicates, and fake green
- Scanning for forbidden references and stale artifacts
- Proposing cleanup actions (never auto-deleting)
- Enforcing no-fake-green discipline
- Reporting findings with evidence

### Non-goals (explicitly deferred):

- Auto-deletion of any files
- Modifying other organs' files
- Overriding Owner decisions
- Blocking tasks without evidence
- Full tree cleanup (only targeted categories)
- Sanctum integration beyond basic status display
- Complex TTL enforcement (simple TTL only)

### Cleanup taxonomy:

| Category | Detection | Action | Risk |
|----------|-----------|--------|------|
| **Duplicates** | Hash comparison | Report + quarantine proposal | Low |
| **Temp files** | Pattern match (`*.tmp`, `__pycache__`) | Report + delete proposal | Low |
| **Stale artifacts** | Age > TTL, no references | Report + archive proposal | Medium |
| **Rejected experiments** | Status = REJECTED | Report + archive proposal | Low |
| **Warning flood sources** | Warning count > budget | Report + fix proposal | Medium |
| **Fake green risks** | PASS without evidence | Report + BLOCKER | High |
| **Wrong files in repo** | Pattern match (secrets, binaries) | Report + quarantine proposal | High |
| **Bundle garbage** | Orphan bundles, failed intake | Report + cleanup proposal | Low |
| **Generated outputs** | In tracked source | Report + gitignore proposal | Medium |
| **Public/private boundary** | Private paths in public | Report + BLOCKER | High |

### Quarantine policy:

```
QUARANTINE RULES:
1. Inquisition NEVER deletes files automatically
2. Inquisition proposes quarantine to ORGANS/INQUISITION/QUARANTINE/
3. Quarantine requires Owner approval
4. Quarantined files are moved, not deleted
5. Quarantine has TTL (default 30 days)
6. After TTL, Owner must decide: restore or delete
7. Quarantine manifest tracks all quarantined items
```

**QUARANTINE_MANIFEST.json:**
```json
{
  "schema_version": "imperium.quarantine_manifest.v0_1",
  "entries": [
    {
      "quarantine_id": "Q-20260513-001",
      "original_path": "ARCHIVE/old_experiment/",
      "quarantine_path": "ORGANS/INQUISITION/QUARANTINE/Q-20260513-001/",
      "reason": "Stale artifact, no references, age > 30 days",
      "category": "stale_artifact",
      "quarantined_at": "2026-05-13T10:00:00Z",
      "ttl_days": 30,
      "expires_at": "2026-06-12T10:00:00Z",
      "owner_decision": null,
      "status": "QUARANTINED"
    }
  ]
}
```

### TTL policy:

```json
{
  "ttl_zones": {
    ".imperium_runtime/": {
      "ttl_days": 7,
      "action": "auto_cleanup_proposal"
    },
    "ORGANS/INQUISITION/QUARANTINE/": {
      "ttl_days": 30,
      "action": "owner_decision_required"
    },
    "ARTIFACTS/": {
      "ttl_days": null,
      "action": "manual_only"
    },
    "ARCHIVE/": {
      "ttl_days": null,
      "action": "manual_only"
    }
  }
}
```

### First 5-10 checkers:

| # | Checker | Purpose | Output |
|---|---------|---------|--------|
| 1 | `check_fake_green.py` | Detect PASS without evidence | BLOCKER if found |
| 2 | `check_ready_for_agent_evidence.py` | Verify READY_FOR_AGENT evidence_refs | BLOCKER if missing |
| 3 | `check_stale_current_state.py` | Detect stale CURRENT_STATE | WARNING |
| 4 | `check_duplicate_files.py` | Find duplicate files by hash | Report |
| 5 | `check_temp_files.py` | Find temp files in tracked source | Report |
| 6 | `check_warning_flood.py` | Classify warnings, check budget | WARNING/BLOCKER |
| 7 | `check_advisory_as_doctrine.py` | Detect raw advisory treated as canon | BLOCKER |
| 8 | `check_public_private_boundary.py` | Detect private paths in public | BLOCKER |
| 9 | `check_orphan_bundles.py` | Find bundles without intake | Report |
| 10 | `check_organ_status_drift.py` | Compare declared vs actual status | WARNING |

### First dashboard requirements:

```
INQUISITION DASHBOARD (minimal):
┌─────────────────────────────────────────────────────────────────┐
│ INQUISITION v0.1 — Audit Status                                 │
├─────────────────────────────────────────────────────────────────┤
│ Last Audit: 2026-05-13 10:00 UTC                                │
│ Verdict: PASS_WITH_WARNINGS                                     │
│                                                                 │
│ Findings:                                                       │
│ [!] 3 fake green risks detected                                 │
│ [⚠] 12 stale artifacts found                                    │
│ [⚠] 5 duplicate files found                                     │
│ [i] 117,000 legacy warnings (within budget)                     │
│                                                                 │
│ Quarantine:                                                     │
│ 2 items pending Owner decision                                  │
│                                                                 │
│ [Run Full Audit] [View Findings] [View Quarantine]              │
└─────────────────────────────────────────────────────────────────┘
```

### Test plan:

| Test | Purpose | Pass Criteria |
|------|---------|---------------|
| `test_check_fake_green.py` | Verify fake green detection | Detects planted fake green |
| `test_check_evidence_refs.py` | Verify evidence ref validation | Detects missing refs |
| `test_quarantine_flow.py` | Verify quarantine workflow | File moved, manifest updated |
| `test_no_auto_delete.py` | Verify no auto-deletion | No files deleted without approval |
| `test_report_format.py` | Verify report schema | Report validates against schema |

### Stage map for building Inquisition v0.1:

Already exists: `STAGE-MAP-DRAFT-20260513-INQUISITION-001-BLUEPRINT-V0_1.json`

10 stages defined:
1. Read schemas and advisory
2. Draft blueprint
3. Define responsibilities and forbidden actions
4. Define owned/read/write zones
5. Define first audit categories
6. Define required capabilities and scripts
7. Define evidence/receipt model
8. Produce blueprint review pack
9. Run corridor checks
10. Prepare Owner review summary

---

## 14. Act 5 preparation plan

### Exact first 3 safe steps:

**Step 1: Fix warning budget (P0)**
```
Task: TASK-20260513-WARNING-BUDGET-IMPLEMENTATION-V0_1
- Create REGISTRY/WARNING_BUDGET.json
- Modify scripts/verify_repo.py to classify warnings
- Establish legacy baseline: 117,000
- Set new warning budget: 100
- Verdict: PASS_WITH_LEGACY_DEBT vs PASS_WITH_NEW_WARNINGS
Duration: 1-2 hours
```

**Step 2: Sync CURRENT_STATE (P0)**
```
Task: TASK-20260513-CURRENT-STATE-SYNC-V0_1
- Update CURRENT_STATE/LAST_POINT_STATE.json to HEAD 7127965
- Update START_HERE.md
- Create TOOLS/refresh_current_state.py
- Run after each major commit
Duration: 30 minutes
```

**Step 3: Complete advisory response ingest (P0)**
```
Task: TASK-CANDIDATE-20260513-INQUISITION-003-ADVISORY-INGEST-V0_1
- This audit IS the advisory response
- Create ADVISORY-RESPONSE-20260513-KIRO-INQUISITION-REDTEAM-V0_1.json
- Register in ORGANS/ASTRONOMICON/REGISTRY/ADVISORY_RESPONSES/
- Update READY_FOR_AGENT gate status
Duration: 1 hour
```

### Next 10 tasks:

| # | Task | Priority | Depends On |
|---|------|----------|------------|
| 4 | Task modernization (accept/reject recommendations) | P0 | Step 3 |
| 5 | Owner approves stage map | P0 | Step 4 |
| 6 | Update READY_FOR_AGENT to true | P0 | Step 5 |
| 7 | Create Inquisition ORGAN_CONTRACT.json | P1 | Step 6 |
| 8 | Create Astronomicon ORGAN_CONTRACT.json | P1 | - |
| 9 | Create first Inquisition checker (fake_green) | P1 | Step 7 |
| 10 | Create WORK_SESSION schema | P1 | - |
| 11 | Create ACTION_REGISTRY.json for Sanctum | P1 | - |
| 12 | Create visual factory skeleton | P2 | - |
| 13 | Run first Inquisition audit | P1 | Step 9 |

### Recommended stage map for Act 5 preparation:

```json
{
  "stage_map_id": "STAGE-MAP-ACT5-PREPARATION-V0_1",
  "stages": [
    {
      "stage_id": "STAGE-001-WARNING-BUDGET",
      "goal": "Implement warning budget to make PASS_WITH_WARNINGS meaningful",
      "owner_decision_gates": []
    },
    {
      "stage_id": "STAGE-002-CURRENT-STATE-SYNC",
      "goal": "Sync CURRENT_STATE with HEAD",
      "owner_decision_gates": []
    },
    {
      "stage_id": "STAGE-003-ADVISORY-INGEST",
      "goal": "Ingest this red-team audit as advisory response",
      "owner_decision_gates": []
    },
    {
      "stage_id": "STAGE-004-TASK-MODERNIZATION",
      "goal": "Accept/reject recommendations from advisory",
      "owner_decision_gates": ["Owner confirms accepted recommendations"]
    },
    {
      "stage_id": "STAGE-005-STAGE-MAP-APPROVAL",
      "goal": "Owner approves Inquisition blueprint stage map",
      "owner_decision_gates": ["Owner approves stage map"]
    },
    {
      "stage_id": "STAGE-006-READY-FOR-AGENT-TRUE",
      "goal": "Update READY_FOR_AGENT gate to true",
      "owner_decision_gates": ["Owner confirms READY_FOR_AGENT"]
    }
  ]
}
```

### Acceptance criteria for Act 5 launch:

1. ✓ Warning budget implemented, new warnings < 100
2. ✓ CURRENT_STATE synced with HEAD
3. ✓ Advisory responses ingested
4. ✓ Task modernization complete
5. ✓ Stage map approved by Owner
6. ✓ READY_FOR_AGENT = true
7. ✓ First 4 organs have ORGAN_CONTRACT.json
8. ✓ At least one Inquisition checker works
9. ✓ verify_repo.py passes (with legacy debt)

### Stop conditions:

| Condition | Action |
|-----------|--------|
| New blockers detected | Stop, fix blockers |
| Owner rejects stage map | Stop, revise stage map |
| Warning budget exceeded | Stop, classify new warnings |
| Fake green detected | Stop, investigate |
| Advisory treated as doctrine | Stop, reconcile |

---

## 15. Concrete files to create/change

### Files to CREATE:

| Path | Purpose | Owner Organ | Checker Needed |
|------|---------|-------------|----------------|
| `REGISTRY/WARNING_BUDGET.json` | Warning classification and budget | Mechanicus | verify_repo.py |
| `ORGANS/ASTRONOMICON/REGISTRY/ADVISORY_RESPONSES/ADVISORY-RESPONSE-20260513-KIRO-INQUISITION-REDTEAM-V0_1.json` | This audit as advisory response | Astronomicon | check_advisory_response.py |
| `ORGANS/ASTRONOMICON/ORGAN_CONTRACT.json` | Astronomicon contract | Astronomicon | check_organ_contract.py |
| `ORGANS/INQUISITION/ORGAN_CONTRACT.json` | Inquisition contract | Inquisition | check_organ_contract.py |
| `schemas/work_session.schema.json` | Work session schema | Administratum | - |
| `schemas/stage_progress_report.schema.json` | Progress report schema | Administratum | - |
| `schemas/administratum_ack.schema.json` | ACK schema | Administratum | - |
| `SANCTUM/ACTIONS/ACTION_REGISTRY.json` | Action registry | Mechanicus | check_action_registry.py |
| `TOOLS/refresh_current_state.py` | Sync CURRENT_STATE | Administratum | - |
| `scripts/check_warning_budget.py` | Warning budget checker | Inquisition | - |
| `scripts/check_fake_green.py` | Fake green detector | Inquisition | - |
| `ASSETS/README.md` | Visual assets readme | Mechanicus | - |
| `ASSETS/OWNER_VISUAL_PREFERENCES.md` | Owner visual preferences | Owner | - |
| `SANCTUM/DESIGN_SYSTEM/DESIGN_TOKENS.json` | Design tokens | Mechanicus | - |
| `SANCTUM/UI_LAB/README.md` | UI lab readme | Mechanicus | - |

### Files to UPDATE:

| Path | Change | Owner Organ |
|------|--------|-------------|
| `CURRENT_STATE/LAST_POINT_STATE.json` | Sync with HEAD 7127965 | Administratum |
| `CURRENT_STATE/NEXT_ATOMIC_STEP.md` | Update to Act 5 preparation | Administratum |
| `START_HERE.md` | Update current task | Administratum |
| `scripts/verify_repo.py` | Add warning budget classification | Mechanicus |
| `ORGANS/ASTRONOMICON/REGISTRY/READY_FOR_AGENT/READY-FOR-AGENT-20260513-INQUISITION-V0_1-SELF-BUILD-BLOCKED-V0_2.json` | Update after advisory ingest | Astronomicon |

---

## 16. What NOT to do

### Dangerous shortcuts:

| Shortcut | Why Dangerous | Correct Approach |
|----------|---------------|------------------|
| Set READY_FOR_AGENT=true without evidence | Fake green | Complete all required phases |
| Skip advisory ingest | Missing reconciliation | Ingest and modernize |
| Ignore warning flood | Cannot detect new issues | Implement warning budget |
| Auto-approve stage map | Missing Owner decision | Wait for explicit approval |
| Treat this audit as doctrine | Advisory is not canon | Reconcile through modernization |

### Visual rewrite traps:

| Trap | Why Dangerous | Correct Approach |
|------|---------------|------------------|
| Revive EE/R1/R2 | Already rejected | Use v0.29 baseline |
| Replace working operator behavior | Breaks functionality | Preserve behavior, improve visuals separately |
| Big visual jump | Owner dislikes | Small deltas with approval |
| Mix visual and runtime changes | Breaks isolation | Separate commits |

### Fake green traps:

| Trap | Why Dangerous | Correct Approach |
|------|---------------|------------------|
| Claim PASS when warnings exist | Misleading | Use PASS_WITH_WARNINGS |
| Claim organ operational when scaffold | Misleading | Use accurate status |
| Claim button works without test | Unverified | Create test first |
| Claim advisory reconciled without modernization | Skipped step | Complete modernization |

### Task registry traps:

| Trap | Why Dangerous | Correct Approach |
|------|---------------|------------------|
| Create TASK without GENERAL_TASK | Orphan task | Follow corridor |
| Skip review pack | Missing feedback | Export review pack |
| Skip stage map | No navigation | Create stage map |
| Duplicate task IDs | Confusion | Check registry first |

### Organ status traps:

| Trap | Why Dangerous | Correct Approach |
|------|---------------|------------------|
| Claim OPERATIONAL when SCAFFOLD | Fake green | Use accurate status |
| Claim scripts exist when missing | Broken references | Verify scripts exist |
| Claim ports work when untested | Unverified | Test ports |
| Update status without evidence | No proof | Create receipt |

---

## 17. Final recommendation

### One clear recommended route:

```
MINIMAL SAFE PATH TO ACT 5:

Day 1 (today):
├── Step 1: Implement warning budget (2 hours)
├── Step 2: Sync CURRENT_STATE (30 min)
└── Step 3: Ingest this audit as advisory response (1 hour)

Day 2:
├── Step 4: Task modernization — Owner reviews recommendations (1 hour)
├── Step 5: Owner approves stage map (30 min)
└── Step 6: Update READY_FOR_AGENT to true (30 min)

Day 3:
├── Step 7: Create Inquisition ORGAN_CONTRACT.json (1 hour)
├── Step 8: Create first checker (check_fake_green.py) (2 hours)
└── Step 9: Run first Inquisition audit (1 hour)

Day 4:
└── BEGIN ACT 5 EXECUTION
    └── Execute STAGE-001-READ-SCHEMAS-AND-ADVISORY
```

### Minimal safe next action:

**Create `REGISTRY/WARNING_BUDGET.json`** with:
```json
{
  "schema_version": "imperium.warning_budget.v0_1",
  "legacy_debt_baseline": 117000,
  "new_warnings_allowed": 100,
  "categories": {
    "continuity_packs": "LEGACY_ACCEPTED",
    "raw_subprocess": "WARNING_MUST_FIX",
    "fake_green_risk": "BLOCKER"
  }
}
```

This single file:
1. Makes PASS_WITH_WARNINGS meaningful
2.
Понял. Продолжаю с того места, где прервался — завершаю секцию 17 (Финальная рекомендация) аудита готовности к Act 5.

Сначала прочитаю указанные файлы для актуализации контекста:

Отлично. Теперь у меня полная картина. Завершаю аудит.

---

# ACT 5 READINESS HARD RED-TEAM AUDIT — СЕКЦИЯ 17 (ФИНАЛ)

## 17. ИТОГОВАЯ РЕКОМЕНДАЦИЯ И МИНИМАЛЬНЫЙ БЕЗОПАСНЫЙ СЛЕДУЮЩИЙ ШАГ

### 17.1 ФИНАЛЬНЫЙ ВЕРДИКТ

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                         ACT 5 READINESS VERDICT                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STATUS:  NOT READY — READY AFTER P0 PREREQUISITES                           ║
║  DATE:    2026-05-13                                                         ║
║  HEAD:    71279657d64e1023acf47d923e20b217daabdd89 (commit 63)               ║
║  AUDITOR: Kiro / Opus 4.5 (read-only architectural research mode)            ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### 17.2 СВОДКА БЛОКЕРОВ

| Приоритет | Блокер | Статус | Влияние на Act 5 |
|-----------|--------|--------|------------------|
| **P0-1** | Warning flood (117,615 warnings) | НЕ РЕШЁН | Маскирует реальные проблемы |
| **P0-2** | CURRENT_STATE/LAST_POINT_STATE.json устарел | НЕ РЕШЁН | Указывает на задачу от 2026-05-10 |
| **P0-3** | Advisory responses не ingested | НЕ РЕШЁН | READY_FOR_AGENT = false |
| **P0-4** | Task modernization отсутствует | НЕ РЕШЁН | Нет accepted/rejected рекомендаций |
| **P0-5** | Stage map не одобрен Owner | НЕ РЕШЁН | status = DRAFT_NEEDS_REVIEW |
| **P1-1** | Первые 4 органа не операционны | НЕ РЕШЁН | Нет ORGAN_CONTRACT.json |
| **P1-2** | Sanctum action registry отсутствует | НЕ РЕШЁН | Нет gate-контроля UI-действий |
| **P1-3** | Servitor long-session model не определён | НЕ РЕШЁН | Нет модели для длинных задач |
| **P1-4** | WARNING_BUDGET.json не создан | НЕ РЕШЁН | Нет формального бюджета warnings |

### 17.3 ЧТО РАБОТАЕТ (ПОЛОЖИТЕЛЬНЫЕ НАХОДКИ)

1. **Verification spine функционирует** — `verify_repo.py` выдаёт PASS_WITH_WARNINGS
2. **Git CLI check работает** — Administratum Git CLI check service operational
3. **Sanctum v0.29 стабилен** — базовый UI работает без критических ошибок
4. **Astronomicon registry структурирован** — READY_FOR_AGENT, TASK_CANDIDATES, STAGE_MAPS существуют
5. **No-fake-green discipline соблюдается** — READY_FOR_AGENT честно показывает `false`
6. **Stage map детализирован** — 10 стадий с pass/fail criteria, forbidden paths, receipts
7. **Bundle workflow работает** — 5 bundle snapshots в `.imperium_runtime/bundles/`
8. **Схемы существуют** — `schemas/` содержит контракты для receipts, organs, reports

### 17.4 КРИТИЧЕСКАЯ ЦЕПОЧКА ЗАВИСИМОСТЕЙ

```
WARNING_BUDGET.json (P0-1)
         │
         ▼
CURRENT_STATE update (P0-2)
         │
         ▼
Advisory ingest (P0-3)
         │
         ▼
Task modernization (P0-4)
         │
         ▼
Stage map approval (P0-5)
         │
         ▼
═══════════════════════════
    ACT 5 GATE OPEN
═══════════════════════════
         │
         ▼
First 4 organs operational (P1-1)
         │
         ▼
Sanctum action registry (P1-2)
         │
         ▼
Servitor long-session model (P1-3)
```

### 17.5 МИНИМАЛЬНЫЙ БЕЗОПАСНЫЙ СЛЕДУЮЩИЙ ШАГ

**Рекомендуемое действие:** Создать `REGISTRY/WARNING_BUDGET.json`

**Почему это первый шаг:**
- Не требует изменения кода
- Не требует одобрения stage map
- Формализует текущий долг (117,615 warnings)
- Позволяет отличать "известные warnings" от "новых проблем"
- Создаёт baseline для измерения прогресса

**Предлагаемая структура (для Owner review):**

```json
{
  "schema_version": "imperium.warning_budget.v0_1",
  "budget_id": "WARNING-BUDGET-20260513-BASELINE-V0_1",
  "created": "2026-05-13",
  "baseline_count": 117615,
  "baseline_source": "verify_repo.py PASS_WITH_WARNINGS",
  "baseline_commit": "71279657d64e1023acf47d923e20b217daabdd89",
  "known_warning_categories": [
    {
      "category": "continuity_pack_legacy",
      "estimated_count": 115000,
      "source_paths": ["ORGANS/*/CONTINUITY/PACKS/"],
      "resolution_plan": "cleanup_or_archive",
      "priority": "P2"
    },
    {
      "category": "registry_drift",
      "estimated_count": 2000,
      "source_paths": ["REGISTRY/"],
      "resolution_plan": "registry_sync_task",
      "priority": "P1"
    },
    {
      "category": "other",
      "estimated_count": 615,
      "source_paths": ["various"],
      "resolution_plan": "triage_required",
      "priority": "P1"
    }
  ],
  "budget_policy": {
    "new_warnings_allowed": 0,
    "reduction_target_per_week": 1000,
    "escalation_threshold": 120000
  },
  "owner_approval": {
    "required": true,
    "granted": false
  }
}
```

### 17.6 АЛЬТЕРНАТИВНЫЕ СЛЕДУЮЩИЕ ШАГИ (ЕСЛИ OWNER ВЫБЕРЕТ ДРУГОЙ ПУТЬ)

| Вариант | Действие | Риск | Польза |
|---------|----------|------|--------|
| A | Создать WARNING_BUDGET.json | Низкий | Формализует долг |
| B | Обновить CURRENT_STATE | Низкий | Актуализирует фокус |
| C | Ingest advisory responses | Средний | Разблокирует task modernization |
| D | Одобрить stage map | Средний | Разблокирует Act 5 execution |
| E | Начать Act 5 без P0 | **ВЫСОКИЙ** | Fake green риск |

**Рекомендация:** Вариант A → B → C → D последовательно.

### 17.7 ЧЕГО НЕ ДЕЛАТЬ

1. **НЕ начинать Act 5 execution** пока READY_FOR_AGENT = false
2. **НЕ игнорировать warning flood** — это маскирует реальные проблемы
3. **НЕ объявлять органы operational** без ORGAN_CONTRACT.json
4. **НЕ создавать Inquisition blueprint** без одобренного stage map
5. **НЕ коммитить с VM2** — только bundle transfer на PC
6. **НЕ реанимировать Sanctum EE/R2** — это отвергнутая линия
7. **НЕ добавлять новые органы** пока первые 4 не operational

### 17.8 МЕТРИКИ ДЛЯ ОТСЛЕЖИВАНИЯ ПРОГРЕССА

| Метрика | Текущее значение | Целевое значение | Когда измерять |
|---------|------------------|------------------|----------------|
| Warning count | 117,615 | < 10,000 | После каждого commit |
| READY_FOR_AGENT gates | 0 true | ≥ 1 true | После task modernization |
| Operational organs | 0 | 4 | После ORGAN_CONTRACT.json |
| Stage maps approved | 0 | 1 | После Owner review |
| Advisory responses ingested | 0 | 1 | После ingest task |

### 17.9 ЗАКЛЮЧЕНИЕ

**Act 5 НЕ ГОТОВ к запуску**, но система находится в здоровом состоянии для подготовки:

- Инфраструктура регистрации существует и работает
- No-fake-green дисциплина соблюдается
- Verification spine функционирует
- Stage map детализирован и готов к review
- Блокеры известны и документированы

**Путь к Act 5:**
1. Формализовать warning budget (1 день)
2. Обновить CURRENT_STATE (1 час)
3. Ingest advisory responses (1 день)
4. Task modernization (1 день)
5. Owner approval stage map (Owner decision)
6. **Act 5 GATE OPEN**

**Оценка времени до готовности:** 3-5 рабочих дней при активной работе Owner.

---

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                         END OF ACT 5 READINESS AUDIT                         ║
║                                                                              ║
║  Auditor: Kiro / Opus 4.5                                                    ║
║  Mode: Read-only architectural research                                      ║
║  Date: 2026-05-13                                                            ║
║  Verdict: NOT READY — READY AFTER P0 PREREQUISITES                           ║
║  Confidence: HIGH (based on direct file inspection)                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

Аудит завершён
