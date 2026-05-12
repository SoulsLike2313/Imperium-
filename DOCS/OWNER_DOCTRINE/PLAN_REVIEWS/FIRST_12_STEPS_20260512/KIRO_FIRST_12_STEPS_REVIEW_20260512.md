
```markdown
# IMPERIUM — REVIEW 12-STEP PLAN
## Kiro Advisory | 2026-05-12 | HEAD: 6bf6d19 | Commits: 36

---

# 0. Verdict on the 12-step plan

**Overall verdict: GOOD / NEEDS MINOR SPLITS**

План когерентен, порядок правильный, масштаб каждого шага разумный. Это один из лучших планов, которые я видел для этого проекта — маленькие шаги, честные acceptance criteria, no fake green.

**Что сильнее всего:**
- Фокус на первых 4 органах прозрения, а не на всём сразу
- Явное разделение "plan" (Step 4) и "execute" (Step 5) для warning flood
- Dry-run как финальный шаг — правильная проверка всей цепочки
- Честное ожидание DEGRADED, а не CLEAR

**Что слабее всего:**
- Step 9 (Astronomicon) слишком большой — содержит и General Task registration, и Stage Map generation, и current stage pointer. Это 2-3 отдельных шага.
- Нет явного шага для Kiro/Speculum clarification loop (Owner хочет это, но в плане нет отдельного step)
- Step 11 (Sanctum HUD data service) может быть сделан раньше — после Step 3, параллельно с warning flood fix

**Можно ли начинать VM2 construction:** ДА. Step 1 (missing organ scaffolds) — идеальный первый VM2 task. Маленький, безопасный, чётко определённый.

---

# 1. Step-by-step critique

## STEP 0 — Baseline already done
- **Verdict:** DONE ?
- **Комментарий:** Правильно зафиксировано. Doctrine в репо.

## STEP 1 — Missing 4 organs scaffold
- **Verdict:** KEEP AS IS
- **VM2:** создаёт файлы, возвращает bundle
- **PC/Owner:** review, commit, push, VM2 sync
- **Required outputs:** 4 папки ? (README.md + ORGAN_STATUS.json + ORGAN_CONTRACT.json + PORTS/ + SCHEMAS/ + SCRIPTS/ + UTILITY/)
- **Missing acceptance:** Добавить: `python scripts/check_agent_entrypoint.py` PASS. Добавить: ORGAN_STATUS.json должен содержать `"maturity": "LEVEL_0_SCAFFOLD"`, не `"LEVEL_7_OPERATIONAL"`.
- **Fake-green risk:** Если ORGAN_STATUS.json содержит `"operational": true` для scaffold — это fake green. Должно быть `"operational": false`.
- **SUGGESTION:** Включить в этот же step обновление ORGAN_REGISTRY (Step 3). Причина: scaffold без registry entry = невидимый орган. Но если Owner хочет отдельно — OK.

## STEP 2 — Organ folder standard
- **Verdict:** KEEP, но можно объединить с Step 1
- **Причина:** Стандарт нужен ДО создания scaffold, чтобы scaffold соответствовал стандарту. Логичнее: сначала стандарт, потом scaffold.
- **SUGGESTION:** Переставить: Step 2 ? Step 1, Step 1 ? Step 2. Или объединить: "создать стандарт + создать scaffold по стандарту" = один VM2 task.
- **VM2:** пишет документ + scaffold
- **PC/Owner:** review стандарта, approve, commit
- **Fake-green risk:** Минимальный. Это документ.

## STEP 3 — ORGAN_REGISTRY sync
- **Verdict:** KEEP, но можно объединить с Step 1
- **Причина:** Registry sync — это 10 JSON entries. Маленькая работа. Если scaffold уже создан, registry sync = 5 минут.
- **SUGGESTION:** Объединить Steps 1+3 в один VM2 task: "Create 4 organ scaffolds + sync ORGAN_REGISTRY to 10 entries". Это всё ещё маленький шаг.
- **Missing acceptance:** Добавить gate: `jq '.organs | length' REGISTRY/ORGAN_REGISTRY.json` = 10. Добавить: canonical_order field matches Owner doctrine.
- **Fake-green risk:** Если registry помечает scaffold как operational.

## STEP 4 — Warning flood cleanup plan
- **Verdict:** KEEP AS IS
- **Комментарий:** Правильно разделить plan и execution. Owner должен approve перед `git rm --cached`.
- **VM2:** пишет plan document
- **PC/Owner:** review plan, approve execution
- **Missing acceptance:** Plan должен содержать: exact file count to untrack, exact .gitignore additions, rollback command if needed.
- **Fake-green risk:** Минимальный (это только plan).

## STEP 5 — Warning flood fix execution
- **Verdict:** KEEP, но это PC-ONLY step
- **BLOCKER:** `git rm --cached` должен выполняться на PC, не на VM2. VM2 не должен менять Git tracking.
- **VM2:** НЕ участвует в этом шаге
- **PC/Owner:** выполняет git rm --cached, обновляет .gitignore, commit, push
- **Missing acceptance:** Добавить: `python scripts/verify_repo.py` warnings < 500 (не 0 — останутся legacy warnings из других источников). Добавить: физические файлы continuity packs всё ещё существуют локально (не удалены).
- **Fake-green risk:** Если warnings упали до 0 — подозрительно. Должны остаться warnings от Sanctum subprocess и hardcoded paths.

## STEP 6 — Doctrinarium real preflight v0.1
- **Verdict:** KEEP AS IS
- **Комментарий:** Отличный шаг. Первый реальный gate.
- **VM2:** пишет script, возвращает bundle
- **PC/Owner:** review, test, commit
- **Missing acceptance:** Добавить: preflight на текущем состоянии должен вернуть DEGRADED (не CLEAR и не BLOCKED). Если вернёт CLEAR — это fake green. Если BLOCKED — слишком строгий.
- **Fake-green risk:** Preflight возвращает CLEAR когда 6 органов = scaffold. Должен возвращать DEGRADED с explicit list of non-operational organs.
- **SUGGESTION:** Добавить в receipt поле `"degraded_organs": [...]` со списком scaffold-only органов.

## STEP 7 — Administratum task registration
- **Verdict:** KEEP AS IS
- **Комментарий:** Правильный scope. Один script, один packet, один receipt.
- **VM2:** пишет script
- **PC/Owner:** review, test with fake task, commit
- **Missing acceptance:** Добавить: duplicate TASK_ID detection test. Добавить: forbidden_zones в address packet должны включать ORGANS/THRONE/, ORGANS/CUSTODES/ (canon zones).
- **Fake-green risk:** Task registered без preflight receipt = bypass Doctrinarium. Script должен REQUIRE preflight receipt path as input.

## STEP 8 — Officio Agentis corridor
- **Verdict:** KEEP AS IS
- **Комментарий:** Правильный scope.
- **VM2:** пишет script
- **PC/Owner:** review, commit
- **Missing acceptance:** Добавить: corridor packet должен содержать `"no_push": true` для VM2 agents. Добавить: corridor должен reference task_address_packet (chain dependency).
- **Fake-green risk:** Corridor без reference to task address = disconnected from chain. Must require task_address_packet path as input.

## STEP 9 — Astronomicon General Task / Stage Map
- **Verdict:** NEEDS SPLIT — слишком большой
- **Причина:** Содержит 3 разных функции:
  1. General Task registration (markdown ? structured record)
  2. Stage Map generation (task ? stages with criteria)
  3. Current stage pointer + advancement logic
- **SUGGESTION:** Split into:
  - Step 9a: General Task registration only (register markdown, create GENERAL_TASK.md + TASKS.md)
  - Step 9b: Stage Map generation (create STAGE_MAP.json + CURRENT_STAGE.json from registered task)
- Stage advancement logic = later (not needed for first dry-run)
- **Fake-green risk:** Stage map without pass_criteria = fake progress tracking. Every stage MUST have explicit pass_criteria.

## STEP 10 — Work packet generator
- **Verdict:** KEEP AS IS
- **Комментарий:** Правильный финальный assembly step.
- **VM2:** пишет script
- **PC/Owner:** review, commit
- **Missing acceptance:** Добавить: work packet MUST fail if any of 4 organ outputs is missing. Добавить: work packet must include `"honest_blockers"` section listing what's NOT available (Mechanicus tools, Inquisition audit, etc.)
- **Fake-green risk:** Work packet generated without all 4 organ receipts = incomplete chain. Script must validate chain completeness.

## STEP 11 — Sanctum HUD data service
- **Verdict:** KEEP, но можно сделать раньше (после Step 3)
- **Причина:** Data service не зависит от Steps 6-10. Он читает ORGAN_STATUS.json и registry. Можно сделать параллельно с organ scripts.
- **SUGGESTION:** Переместить после Step 3 (registry sync). Тогда Sanctum сразу показывает 10 органов с реальным maturity.
- **VM2:** пишет data service
- **PC/Owner:** review, integrate minimally into Sanctum
- **Fake-green risk:** Data service returns hardcoded data instead of reading files. Must read from filesystem every call.

## STEP 12 — Dry-run
- **Verdict:** KEEP AS IS — отличный финальный шаг
- **Комментарий:** Правильная проверка всей цепочки.
- **VM2:** может подготовить dry-run script
- **PC/Owner:** выполняет dry-run, review results, commit evidence
- **Missing acceptance:** Добавить: dry-run receipt must contain `"chain_complete": false` (because Mechanicus/Inquisition/Throne/Custodes not operational). Если `"chain_complete": true` — fake green.
- **Fake-green risk:** Dry-run "passes" without honest blocker reporting.

---

# 2. Recommended corrected 12-step sequence

```
Step 0:  Baseline (DONE)
Step 1:  Organ folder standard document
Step 2:  Missing 4 organ scaffolds + ORGAN_REGISTRY sync to 10
Step 3:  Sanctum HUD data service v0.1 (reads organ statuses)
Step 4:  Warning flood cleanup plan (document only)
Step 5:  Warning flood fix execution (PC-only, git rm --cached)
Step 6:  Doctrinarium real preflight v0.1
Step 7:  Administratum task registration + address packet v0.1
Step 8:  Officio Agentis corridor packet v0.1
Step 9a: Astronomicon General Task registration v0.1
Step 9b: Astronomicon Stage Map generation v0.1
Step 10: First-four-organs work packet generator
Step 11: Sanctum HUD minimal integration (connect data service to UI)
Step 12: First-four-organs dry-run
```

**Изменения:**
- Steps 1+3 объединены (scaffold + registry = один VM2 task)
- Step 2 (standard) перемещён перед scaffold
- Sanctum HUD data service перемещён раньше (Step 3)
- Step 9 разделён на 9a + 9b
- Sanctum UI integration добавлен как Step 11 (отдельно от data service)
- Итого: 13 шагов вместо 12, но каждый меньше

---

# 3. Required files per step

| Step | Files to create/update | Runtime outputs | Registry changes | Checks | Commit message |
|------|----------------------|-----------------|------------------|--------|----------------|
| 1 | `DOCS/OWNER_DOCTRINE/ORGAN_FOLDER_STANDARD_V0_1.md` | — | — | py_compile, verify_repo | TASK-...: add organ folder standard |
| 2 | `ORGANS/{CUSTODES,STRATEGIUM,SCHOLA_IMPERIALIS,THRONE}/` (each: README, STATUS, CONTRACT, PORTS/, SCHEMAS/, SCRIPTS/, UTILITY/); `REGISTRY/ORGAN_REGISTRY.json` update | — | ORGAN_REGISTRY ? 10 entries | verify_repo, agent_entrypoint, `jq .organs.length` = 10 | TASK-...: add missing organ scaffolds and sync registry |
| 3 | `SANCTUM/organ_hud_data_v0_1.py` | — | — | py_compile, import test | TASK-...: add Sanctum organ HUD data service |
| 4 | `DOCS/PLANS/WARNING_FLOOD_FIX_PLAN_V0_1.md` | — | — | — | TASK-...: add warning flood fix plan |
| 5 | `.gitignore` update; `REGISTRY/WARNING_BASELINE.json` | — | WARNING_BASELINE | verify_repo warnings < 500 | TASK-...: untrack continuity packs and add warning baseline |
| 6 | `ORGANS/DOCTRINARIUM/SCRIPTS/doctrinarium_preflight_v0_1.py` | `.imperium_runtime/doctrinarium/preflight/` | — | script runs, returns DEGRADED | TASK-...: add Doctrinarium real preflight v0.1 |
| 7 | `ORGANS/ADMINISTRATUM/SCRIPTS/administratum_register_task_v0_1.py` | `ORGANS/ADMINISTRATUM/MEMORY/TASKS/{id}/` | — | registers test task, detects duplicate | TASK-...: add Administratum task registration v0.1 |
| 8 | `ORGANS/OFFICIO_AGENTIS/SCRIPTS/officio_issue_corridor_v0_1.py` | `.imperium_runtime/officio_agentis/{id}/` | — | produces corridor packet | TASK-...: add Officio Agentis corridor v0.1 |
| 9a | `ORGANS/ASTRONOMICON/SCRIPTS/astronomicon_register_general_task_v0_1.py` | `ORGANS/ASTRONOMICON/TASKS/{id}/GENERAL_TASK.md` | — | registers test task | TASK-...: add Astronomicon General Task registration v0.1 |
| 9b | `ORGANS/ASTRONOMICON/SCRIPTS/astronomicon_issue_stage_map_v0_1.py` | `ORGANS/ASTRONOMICON/TASKS/{id}/STAGE_MAP.json` | — | produces valid stage map | TASK-...: add Astronomicon Stage Map v0.1 |
| 10 | `TOOLS/build_servitor_work_packet_v0_1.py` | `.imperium_runtime/task_work_packets/{id}/` | — | produces packet, fails if chain incomplete | TASK-...: add Servitor work packet generator v0.1 |
| 11 | `SANCTUM/sanctum_v0_29_qt.py` (minimal edit: read from data service) | — | — | Sanctum launches, shows real data, FPS > 50 | TASK-...: connect Sanctum HUD to organ data service |
| 12 | `TOOLS/run_first_four_organs_dryrun_v0_1.py` | `.imperium_runtime/dryrun/` | — | dry-run receipt exists, honest blockers listed | TASK-...: first four organs dry-run v0.1 |

---

# 4. Minimal schemas and packets

## PREFLIGHT_RECEIPT
```
schema_version, task_id (optional), timestamp_utc,
organs_checked (list of {organ_id, exists, maturity, operational, issues}),
verify_repo_verdict, known_defects_active (list),
verdict (CLEAR/DEGRADED/BLOCKED),
degraded_organs (list), blockers (list), warnings (list)
```

## TASK_ADDRESS_PACKET
```
schema_version, task_id, registered_at, source_document_path,
workspace_path, forbidden_zones (list), read_sources (list),
write_targets (list), runtime_receipt_dir, downstream_organs (list),
preflight_receipt_path, status (REGISTERED/ACTIVE/COMPLETE/FAILED)
```

## AGENT_CORRIDOR_PACKET
```
schema_version, task_id, agent_id, agent_profile,
mode (DRAFT_ONLY/EXECUTE/REVIEW), allowed_actions (list),
forbidden_actions (list), stop_conditions (list),
owner_approval_required_for (list), no_push (bool),
no_broad_refactor (bool), bundle_rules (text),
final_report_format (text), language (text)
```

## GENERAL_TASK_RECORD
```
schema_version, task_id, title, owner_goal (text),
source_document_path, clarification_history (list of {agent, advice_path, date}),
final_registration_date, status (DRAFT/CLARIFYING/REGISTERED/ACTIVE/COMPLETE),
tasks (list of task_id references)
```

## STAGE_MAP
```
schema_version, task_id, stages (list of {
  stage_id, title, order, dependencies (list),
  pass_criteria (list of text), owner_approval_required (bool),
  status (PLANNED/ACTIVE/PASS/FAIL/SKIPPED),
  expected_output_bundle (text), assigned_organ (text)
}),
current_stage_id, total_stages, completed_stages
```

## CURRENT_STAGE
```
schema_version, task_id, stage_id, title, order,
pass_criteria (list), status, started_at, tools_assigned (list),
honest_blockers (list)
```

## SERVITOR_WORK_PACKET
```
schema_version, task_id, stage_id, generated_at,
preflight_verdict, task_address (embedded or path),
agent_corridor (embedded or path), stage_map_summary,
current_stage (embedded), tools_available (list),
honest_blockers (list of {mechanism, organ, impact}),
chain_complete (bool), instructions_for_servitor (text)
```

## DRY_RUN_RECEIPT
```
schema_version, task_id, timestamp_utc, steps_executed (list of {
  organ, action, verdict, output_path
}),
chain_complete (bool), honest_blockers (list),
work_packet_generated (bool), work_packet_path,
overall_verdict (PASS/DEGRADED/FAIL)
```

---

# 5. First four organs operational contract

## 1. Doctrinarium

| Field | Value |
|-------|-------|
| Input | task_id (optional) |
| Output | PREFLIGHT_RECEIPT.json + PREFLIGHT_VERDICT.md |
| Script | `ORGANS/DOCTRINARIUM/SCRIPTS/doctrinarium_preflight_v0_1.py` |
| Port | `preflight_task_execution` |
| Receipt | `.imperium_runtime/doctrinarium/preflight/PREFLIGHT_RECEIPT.json` |
| Stop condition | verdict = BLOCKED |
| Owner approval | Не нужен (автоматический gate) |
| Sanctum display | "System Health" chip: CLEAR/DEGRADED/BLOCKED + degraded organ list |

## 2. Administratum

| Field | Value |
|-------|-------|
| Input | task_id + preflight_receipt_path + source_document_path |
| Output | TASK_ADDRESS_PACKET.json + TASK_REGISTRATION_RECEIPT.json |
| Script | `ORGANS/ADMINISTRATUM/SCRIPTS/administratum_register_task_v0_1.py` |
| Port | `register_task` |
| Receipt | `ORGANS/ADMINISTRATUM/MEMORY/TASKS/{id}/TASK_REGISTRATION_RECEIPT.json` |
| Stop condition | duplicate task_id, missing preflight receipt |
| Owner approval | Не нужен |
| Sanctum display | "Task Registry" chip: active task count + current task_id |

## 3. Officio Agentis

| Field | Value |
|-------|-------|
| Input | task_id + task_address_packet_path + agent_profile_id |
| Output | AGENT_CORRIDOR_PACKET.json |
| Script | `ORGANS/OFFICIO_AGENTIS/SCRIPTS/officio_issue_corridor_v0_1.py` |
| Port | `issue_agent_corridor` |
| Receipt | `.imperium_runtime/officio_agentis/{id}/AGENT_CORRIDOR_PACKET.json` |
| Stop condition | unknown agent profile, missing task address |
| Owner approval | Mode change DRAFT?EXECUTE |
| Sanctum display | "Agent Mode" chip: current mode + agent_id |

## 4. Astronomicon

| Field | Value |
|-------|-------|
| Input | task_id + general_task_document_path |
| Output | GENERAL_TASK.md + STAGE_MAP.json + CURRENT_STAGE.json |
| Scripts | `astronomicon_register_general_task_v0_1.py` + `astronomicon_issue_stage_map_v0_1.py` |
| Port | `register_general_task` + `issue_stage_map` |
| Receipt | `ORGANS/ASTRONOMICON/TASKS/{id}/REGISTRATION_RECEIPT.json` |
| Stop condition | invalid stage map, missing pass criteria |
| Owner approval | Stage map modification after registration |
| Sanctum display | "Task Map" chip: stage count + current stage + completion % |

---

# 6. Sanctum HUD practical plan

## Data service (Step 3)

**File:** `SANCTUM/organ_hud_data_v0_1.py`

**Reads:**
- `REGISTRY/ORGAN_REGISTRY.json` (10 organs, maturity, status)
- `ORGANS/*/ORGAN_STATUS.json` (alive, operational, issues)
- `.imperium_runtime/doctrinarium/preflight/PREFLIGHT_RECEIPT.json` (latest verdict)
- `.imperium_runtime/task_work_packets/*/` (active task if exists)
- `ORGANS/ASTRONOMICON/TASKS/*/CURRENT_STAGE.json` (if exists)

**Returns:**
```python
{
    "organs": [{"id": "DOCTRINARIUM", "maturity": "LEVEL_5", "operational": True, ...}, ...],
    "system_health": "DEGRADED",
    "active_task": {"task_id": "...", "stage": "...", "completion": 0.33} or None,
    "preflight_verdict": "DEGRADED",
    "honest_blockers": ["Mechanicus not operational", ...],
    "warnings_count": 42,
}
```

**How UI uses it:**
- Call `get_hud_data()` once on startup and on Refresh button click
- Do NOT call in paint loop
- Store result in instance variable
- Paint loop reads instance variable (fast, no I/O)
- Optional: QTimer every 30 seconds for background refresh

**How to avoid FPS drop:**
- NEVER read files in `paintEvent`
- NEVER run subprocess in `paintEvent`
- Data service = separate call, result cached
- Paint loop only reads cached dict

**What NOT to do:**
- Do not add 10 separate panels/tabs now
- Do not create new QMainWindow
- Do not rewrite PlanetMapWidget
- Do not add blocking operations to UI thread
- Just replace hardcoded chip values with data from cached dict

## UI integration (Step 11)

**Minimal change to sanctum_v0_29_qt.py:**
- Import `organ_hud_data_v0_1`
- On startup: call `get_hud_data()`, store result
- Replace hardcoded chips ("Stages: 6", "Pass: 1", etc.) with real values from dict
- Add one small text area or label showing: `"Health: DEGRADED | Task: TASK-... | Stage: 2/5"`
- Keep PlanetMapWidget animation unchanged

**Estimated code change:** ~30 lines. No structural refactor.

---

# 7. Kiro / Speculum clarification loop

## Process

```
1. Owner writes General Task draft
   ? saves to: ORGANS/ASTRONOMICON/DRAFTS/{task_id}_DRAFT.md

2. Owner gives draft to Kiro for clarification
   ? Kiro reads draft + AGENTS.md + doctrine
   ? Kiro returns advice
   ? saved to: ORGANS/ASTRONOMICON/DRAFTS/{task_id}_KIRO_ADVICE.md

3. Owner optionally gives to Speculum for red-team
   ? Speculum returns critique
   ? saved to: ORGANS/ASTRONOMICON/DRAFTS/{task_id}_SPECULUM_CRITIQUE.md

4. Owner updates draft based on advice
   ? saves final: ORGANS/ASTRONOMICON/TASKS/{task_id}/GENERAL_TASK.md

5. Astronomicon registers final General Task
   ? creates REGISTRATION_RECEIPT.json
   ? receipt contains: clarification_history with paths to advice files
```

## Proof that clarification happened

Receipt field:
```json
"clarification_history": [
    {"agent": "KIRO", "advice_path": "DRAFTS/{id}_KIRO_ADVICE.md", "date": "..."},
    {"agent": "SPECULUM", "advice_path": "DRAFTS/{id}_SPECULUM_CRITIQUE.md", "date": "..."}
]
```

If no clarification: `"clarification_history": []` — valid but noted.

---

# 8. Dry-run design

**TASK_ID:** `TASK-DRYRUN-FIRST-FOUR-ORGANS-V0_1`

**Input files:**
- Fake General Task markdown (2-3 sentences)
- Agent profile: `SERVITOR_PC` or `VM2_SERVITOR`

**Command sequence:**
```bash
python ORGANS/DOCTRINARIUM/SCRIPTS/doctrinarium_preflight_v0_1.py
python ORGANS/ADMINISTRATUM/SCRIPTS/administratum_register_task_v0_1.py --task-id TASK-DRYRUN-FIRST-FOUR-ORGANS-V0_1 --source DRAFTS/dryrun_task.md --preflight .imperium_runtime/doctrinarium/preflight/PREFLIGHT_RECEIPT.json
python ORGANS/OFFICIO_AGENTIS/SCRIPTS/officio_issue_corridor_v0_1.py --task-id TASK-DRYRUN-FIRST-FOUR-ORGANS-V0_1 --agent VM2_SERVITOR --address ORGANS/ADMINISTRATUM/MEMORY/TASKS/TASK-DRYRUN-FIRST-FOUR-ORGANS-V0_1/TASK_ADDRESS_PACKET.json
python ORGANS/ASTRONOMICON/SCRIPTS/astronomicon_register_general_task_v0_1.py --task-id TASK-DRYRUN-FIRST-FOUR-ORGANS-V0_1 --source DRAFTS/dryrun_task.md
python ORGANS/ASTRONOMICON/SCRIPTS/astronomicon_issue_stage_map_v0_1.py --task-id TASK-DRYRUN-FIRST-FOUR-ORGANS-V0_1
python TOOLS/build_servitor_work_packet_v0_1.py --task-id TASK-DRYRUN-FIRST-FOUR-ORGANS-V0_1
```

**Expected outputs:**
- PREFLIGHT_RECEIPT: verdict = DEGRADED (honest)
- TASK_ADDRESS_PACKET: workspace assigned
- AGENT_CORRIDOR_PACKET: VM2 rules applied
- STAGE_MAP: 1-2 stages with pass criteria
- SERVITOR_WORK_PACKET: complete, with honest_blockers

**Expected honest blockers in work packet:**
```json
"honest_blockers": [
    {"mechanism": "tool_assignment", "organ": "MECHANICUS", "impact": "no automated tool selection"},
    {"mechanism": "post_stage_audit", "organ": "INQUISITION", "impact": "no automated audit"},
    {"mechanism": "canon_acceptance", "organ": "THRONE", "impact": "no formal acceptance gate"},
    {"mechanism": "canon_protection", "organ": "CUSTODES", "impact": "no backup/boundary enforcement"}
]
```

**PASS criteria:**
- All 6 files generated without crash
- Preflight = DEGRADED (not CLEAR)
- Work packet contains honest_blockers
- Work packet `chain_complete` = false
- All receipts are valid JSON

**What would be fake green:**
- Preflight = CLEAR (impossible with scaffold organs)
- Work packet `chain_complete` = true
- No honest_blockers listed
- Any step skipped silently

---

# 9. Risks and fake-green traps

| # | Risk | Affected step | Mitigation |
|---|------|--------------|------------|
| 1 | Scaffold organs marked operational in ORGAN_STATUS | Step 2 | Enforce `"operational": false` for LEVEL_0 |
| 2 | Preflight returns CLEAR with scaffold organs | Step 6 | Test: must return DEGRADED on current state |
| 3 | Stage map without pass_criteria | Step 9b | Validate: every stage must have ?1 pass criterion |
| 4 | Sanctum shows hardcoded "PASS" instead of real data | Step 11 | Test: change ORGAN_STATUS ? verify chip changes |
| 5 | Task registered without preflight receipt | Step 7 | Script must require --preflight argument |
| 6 | Corridor issued without task address | Step 8 | Script must require --address argument |
| 7 | Work packet generated with missing chain links | Step 10 | Script must check all 4 outputs exist |
| 8 | Warning flood hides new regressions | Step 5 | Baseline + threshold gate |
| 9 | VM2 modifies too many files | All VM2 steps | Strict scope in prompt, review on PC |
| 10 | Dry-run "passes" without blocker reporting | Step 12 | Receipt must contain honest_blockers list |
| 11 | Registry drift after scaffold creation | Step 2 | Include registry sync in same step |
| 12 | Data service returns stale cache | Step 3 | Always read from filesystem, no persistent cache |

---

# 10. Final recommended first VM2 task

**Target:**
```
TASK-20260512-ORGAN-STANDARD-AND-SCAFFOLDS-V0_1
```

**Scope (one VM2 bundle):**
1. Create `DOCS/OWNER_DOCTRINE/ORGAN_FOLDER_STANDARD_V0_1.md`
2. Create scaffold for CUSTODES, STRATEGIUM, SCHOLA_IMPERIALIS, THRONE (each: README.md, ORGAN_STATUS.json with LEVEL_0, ORGAN_CONTRACT.json, empty PORTS/, SCHEMAS/, SCRIPTS/, UTILITY/)
3. Update `REGISTRY/ORGAN_REGISTRY.json` to 10 entries with canonical_order

**NOT included:**
- No Sanctum changes
- No script logic
- No warning flood fix
- No registry beyond ORGAN_REGISTRY

**Why combined:** Стандарт + scaffold + registry = логически связаны. Scaffold без стандарта = inconsistent. Scaffold без registry = invisible. Всё вместе = один coherent VM2 task.

**Expected bundle size:** ~20 new files, 1 updated file, 1 new doc.

---

# 11. Questions for Owner

1. **Step 5 (warning flood fix 

```markdown
# 11. Questions for Owner (продолжение)

1. **Step 5 (warning flood fix):** Подтверждаете ли вы, что `git rm --cached` для continuity packs безопасен? Физические файлы останутся на диске, но выйдут из Git-трекинга. Это необратимо в том смысле, что Git history сохранит их, но новые коммиты не будут их отслеживать. Нужен ли вам отдельный backup перед этим шагом?

2. **Sanctum HUD:** Достаточно ли для v0.1 просто заменить hardcoded chips на реальные данные (одна строка: "Health: DEGRADED | Task: ... | Stage: 2/5")? Или вы хотите видеть все 10 органов как отдельные элементы уже сейчас?

3. **Agent profiles:** Сейчас существует только `SERVITOR_PC.json`. Нужен ли `VM2_SERVITOR.json` как отдельный профиль с другими ограничениями (no push, no commit, bundle-only output)? Или один профиль с параметром contour?

4. **General Task format:** Достаточно ли для v0.1 простого markdown файла с заголовком, целью и ожидаемым результатом? Или нужна structured форма (JSON/YAML) с самого начала?

5. **Dry-run task:** Для первого dry-run использовать полностью фейковую задачу ("test task: add README to empty folder") или реальную маленькую задачу из текущего backlog?

6. **Clarification loop:** Kiro/Speculum clarification — это обязательный шаг для КАЖДОЙ задачи или только для крупных General Tasks? Маленькие operational tasks (fix typo, add file) могут пропускать clarification?

7. **Порог DEGRADED vs BLOCKED:** При каком количестве non-operational органов Doctrinarium должен возвращать BLOCKED вместо DEGRADED? Предложение: BLOCKED только если один из первых 4 органов прозрения мёртв. DEGRADED если органы 5-10 scaffold-only. Согласны?

---

# Дополнение: что отправить Speculum позже

После завершения Steps 1-6 (scaffold + registry + warning fix + preflight), отправить Speculum:

1. **ORGAN_FOLDER_STANDARD_V0_1.md** — red-team на полноту и consistency
2. **doctrinarium_preflight_v0_1.py** — red-team на fake green scenarios:
   - Что если ORGAN_STATUS.json повреждён?
   - Что если файл существует но содержит `"operational": true` для scaffold?
   - Что если verify_repo не запускался?
3. **ORGAN_REGISTRY.json (10 entries)** — red-team на drift:
   - Что если орган удалён но запись осталась?
   - Что если canonical_order не совпадает с doctrine?
4. **Dry-run receipt** — red-team на честность:
   - Все ли blockers перечислены?
   - Нет ли скрытых assumptions?
   - Может ли Servitor начать работу с этим work packet?

**Формат для Speculum:**
```
"Вот артефакт X. Попробуй сломать его. Найди сценарии, где он даёт fake green, скрывает проблему, или позволяет агенту обойти ограничения. Не предлагай fixes — только findings."
```

---

# Финальная сводка

| Аспект | Оценка |
|--------|--------|
| План когерентен | ? Да |
| Порядок органов сохранён | ? CANONICAL |
| Шаги достаточно малы | ?? Step 9 нужен split |
| Fake-green защита | ?? Нужны explicit checks на DEGRADED |
| VM2 scope ясен | ? Да |
| Sanctum не перегружен | ? Data service first, UI later |
| Freelance Console отложен | ? Правильно |
| Можно начинать VM2 | ? Да, Step 1+2+3 combined |

**Рекомендуемый следующий шаг Owner:**
1. Ответить на 7 вопросов выше
2. Approve первый VM2 task scope (scaffold + standard + registry)
3. Написать VM2 prompt для `TASK-20260512-ORGAN-STANDARD-AND-SCAFFOLDS-V0_1`

---

*Review завершён. Репозиторий не модифицирован. План готов к execution после Owner approval.*
```