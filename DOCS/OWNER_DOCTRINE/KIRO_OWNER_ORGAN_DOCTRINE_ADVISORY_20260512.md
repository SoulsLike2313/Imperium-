# IMPERIUM — KIRO OWNER ORGAN DOCTRINE ADVISORY 2026-05-12

**Статус:** advisory hardening input / не канон  
**Назначение:** инженерно усилить Owner-доктрину, не меняя порядок органов.

---

## Boundary

Owner Doctrine имеет приоритет.  
Kiro advisory может предлагать ports, schemas, scripts, receipts, HUD и gates, но не может менять порядок органов или подменять Owner-смысл.

---

## Kiro advisory text

Файлы OWNER_DOCTRINE ещё не закоммичены в репозиторий, но Owner предоставил полный текст `OWNER-ORGAN-DOCTRINE-REGISTRATION-PLAN-V0-1.md` в промпте как вложенный документ. Этого достаточно для advisory pass. Прочитаю дополнительные файлы из репо для контекста.

У меня достаточно контекста. Owner предоставил полную доктрину в документе, Reality Map я уже знаю из предыдущего аудита, и текущее состояние репо подтверждено. Приступаю к advisory hardening report.

```markdown
# IMPERIUM — ADVISORY HARDENING REPORT
## Kiro Read-Only Advisory Pass  2026-05-12  HEAD 4eb4122  Коммиты 35

---

# 0. Executive advisory verdict

Доктрина Owner когерентна Да. Порядок органов логичен и отражает реальный операционный цикл сначала проверка здоровья системы → затем адресациярегистрация → затем рамки поведения → затем карта задачи → затем инструменты → затем аудит → затем канон → затем защита → затем улучшение → затем обучение.

Что сильнее всего
- Чёткое разделение на 4 категории (прозрение  исполнение  канон  усиление)
- Throne как kernel-like ядро, а не просто кнопка accept
- Custodes как shield layer, а не просто backup
- Strategium как тихий research, а не primary planner
- Schola как Owner learning path, а не просто docs

Что опаснонедоспецифицировано
- Граница между Throne и Custodes где заканчивается чистое ядро и начинается охрана Нужен конкретный файловыйконтурный boundary.
- Strategium тихо и малоресурсно — но кто его триггерит Когда Как часто Без этого он останется ceremonial.
- Schola смотрит diffprogress — но откуда берёт данные Нужен конкретный data source.
- Нет явного описания, что происходит при FAIL на каждом шаге (кроме Doctrinarium допускает старт или нет).

Что НЕЛЬЗЯ менять (CANONICAL)
- Порядок 10 органов
- Категории (I-IV)
- Роль Throne как kernel, не как accept button
- Роль Custodes как shield, не как backup script
- Роль Strategium как research, не как primary planner
- Принцип агент не начинает работу без прохождения через органы прозрения

---

# 1. Canonical chain preservation

## Почему Owner-порядок должен быть сохранён

Owner-порядок отличается от generic task lifecycle (типичный plan → assign → execute → review → accept) в нескольких ключевых местах

1. Doctrinarium первый, не Strategium. В generic системах планирование идёт первым. Здесь первым идёт health check системы. Это правильно для agent-driven workflow прежде чем давать задачу агенту, убедись что система жива.

2. Administratum второй, не последний. В generic системах registrymemory обновляется в конце. Здесь Administratum даёт адрес и workspace ДО начала работы. Это правильно агент должен знать, куда писать, прежде чем писать.

3. Officio Agentis третий. Executor corridor ДО карты задачи. Это значит сначала агент узнаёт свои ограничения, потом получает задачу. Правильно для safety.

4. ThroneCustodes после Inquisition, не в конце. Canon acceptance идёт до researchlearning. Это значит сначала результат принимается в канон, потом система учится. Правильно нельзя учиться на непринятом результате.

5. StrategiumSchola последние. Они не блокируют task completion. Они работают асинхронно после acceptance. Это правильно для operational speed.

## Как сделать это machine-operational без изменения порядка

Каждый переход между органами = message passing. Каждый орган
- Получает input packet
- Проверяетобрабатывает
- Выдаёт output packet или STOP signal
- Записывает receipt

Цепочка реализуется как sequential pipeline с stop conditions, не как event-driven mesh. Это проще, надёжнее, и соответствует Owner-порядку.

---

# 2. Organ-by-organ strengthening advice

## 1. DOCTRINARIUM (CANONICAL первый орган прозрения)

Owner meaning Первая прозвонка. Система допускает старт или нет.

Practical operational role Health gate. Проверяет органы живы, законы чисты, нет сломанного состояния.

Minimum viable operational function v0.1
```
Input task_id
Action проверить ORGAN_STATUS.json всех 10 органов, проверить verify_repo verdict, проверить KNOWN_DEFECTS
Output PREFLIGHT_RECEIPT.json с verdict CLEAR  BLOCKED  DEGRADED
Stop condition если verdict = BLOCKED → задача не начинается
```

Required files
- `ORGANSDOCTRINARIUMORGAN_STATUS.json` ✅ exists
- `ORGANSDOCTRINARIUMORGAN_CONTRACT.json` ✅ exists
- `ORGANSDOCTRINARIUMSCRIPTSdoctrinarium_preflight_v1.py` (нужен — текущий preflight = smoke)

Required ports
- `preflight_task_execution` (input task_id → output preflight_receipt)
- `check_organ_health` (input organ_id → output health_status)

Required schemas
- `preflight_receipt_v1.schema.json`
- `organ_health_response_v1.schema.json`

Required receipts
- `PREFLIGHT_RECEIPT_{task_id}_{timestamp}.json`

Required Sanctum HUD panel
- System Health — показывает все 10 органов, их status (alivedegradeddead), последний preflight verdict, кнопка Run Preflight

What can stop the task BLOCKED verdict (critical organ dead, law violated, known blocker active)

What requires Owner approval Ничего — Doctrinarium автоматический gate.

Failure modes
- Organ status files missing → DEGRADED (не BLOCKED)
- verify_repo FAIL → BLOCKED
- Known critical defect active → BLOCKED

First small task Написать `doctrinarium_preflight_v1.py` который читает все ORGAN_STATUS.json, читает verify_repo verdict из runtime, читает KNOWN_DEFECTS.json, выдаёт structured receipt.

---

## 2. ADMINISTRATUM (CANONICAL второй орган прозрения)

Owner meaning Память, адреса, регистрация, ledger. Диспетчер и архивист.

Practical operational role Task registration, workspace assignment, history recording.

Minimum viable operational function v0.1
```
Input task_id + preflight_receipt
Action создать TASK_ADDRESS_PACKET (где работать, что читать, что нельзя трогать), зарегистрировать task start в ledger
Output TASK_ADDRESS_PACKET.json + TASK_LEDGER_ENTRY.json
Stop condition если workspace conflict или duplicate task_id → BLOCKED
```

Required files
- `ORGANSADMINISTRATUMORGAN_STATUS.json` ✅
- `ORGANSADMINISTRATUMORGAN_CONTRACT.json` ✅
- `ORGANSADMINISTRATUMSCRIPTSadministratum_issue_task_address.py` (нужен)
- `ORGANSADMINISTRATUMMEMORYTASKS{task_id}` (runtime)

Required ports
- `issue_task_address` (input task_id, preflight_receipt → output task_address_packet)
- `register_stage_completion` (input task_id, stage_id, result → output ledger_entry)
- `close_task` (input task_id, final_result → output closure_receipt)

Required schemas
- `task_address_packet_v1.schema.json`
- `task_ledger_entry_v1.schema.json`

Required Sanctum HUD panel
- Task Registry — показывает active tasks, their stages, completion %, кнопка Register New Task

What can stop the task Duplicate task_id, workspace conflict

What requires Owner approval Ничего на этом шаге (Owner уже дал goal).

First small task Написать `administratum_issue_task_address.py` который принимает task_id, создаёт папку в MEMORYTASKS, записывает address packet с workspace path и forbidden zones.

---

## 3. OFFICIO AGENTIS (CANONICAL третий орган прозрения)

Owner meaning Рамки поведения исполнителя. Executor corridor.

Practical operational role Agent behavior constraints, mode assignment, stop conditions.

Minimum viable operational function v0.1
```
Input task_id + task_address_packet + agent_profile_id
Action сгенерировать AGENT_CORRIDOR_PACKET (что можно, что нельзя, где остановка, какой стиль)
Output AGENT_CORRIDOR_PACKET.json
Stop condition если agent_profile не найден или task type не поддерживается → BLOCKED
```

Required files
- `ORGANSOFFICIO_AGENTISAGENT_PROFILES` ✅ (SERVITOR_PC.json exists)
- `ORGANSOFFICIO_AGENTISSCRIPTSofficio_issue_corridor.py` (нужен)

Required ports
- `issue_agent_corridor` (input task_id, agent_id → output corridor_packet)

Required schemas
- `agent_corridor_packet_v1.schema.json`

Required Sanctum HUD panel
- Agent Mode — показывает текущий agent profile, mode (DRAFT_ONLYEXECUTEREVIEW), forbidden actions, кнопка Change Mode

What can stop the task Unknown agent profile, unsupported task type

What requires Owner approval Changing agent mode from DRAFT_ONLY to EXECUTE.

First small task Написать `officio_issue_corridor.py` который читает agent profile, генерирует corridor packet с allowedforbidden actions.

---

## 4. ASTRONOMICON (CANONICAL четвёртый орган прозрения)

Owner meaning Карта задачи. Место, где задача становится видимой как маршрут.

Practical operational role Task decomposition into stages, pass criteria, dependency tracking.

Minimum viable operational function v0.1
```
Input task_id + task_address_packet + agent_corridor
Action создать или загрузить STAGE_MAP (stages, order, pass criteria, dependencies)
Output STAGE_MAP.json + CURRENT_STAGE pointer
Stop condition если stage map невалидна или circular dependency → BLOCKED
```

Required files
- `ORGANSASTRONOMICONTASKS{task_id}STAGE_MAP.json` (runtime)
- `ORGANSASTRONOMICONSCRIPTSastronomicon_issue_stage_map.py` (нужен — текущие = smoke)

Required ports
- `issue_stage_map` (input task_id → output stage_map)
- `advance_stage` (input task_id, stage_id, result → output next_stage or COMPLETE)
- `get_current_stage` (input task_id → output current_stage_id + pass_criteria)

Required schemas
- `stage_map_v2.schema.json` (v1 exists but needs update)
- `stage_advance_signal_v1.schema.json`

Required Sanctum HUD panel
- Task Map — показывает visual stage pipeline, current stage highlighted, passfail per stage, кнопка View Stage Details

What can stop the task Invalid stage map, all stages FAIL

What requires Owner approval Modifying stage map after execution started.

First small task Написать `astronomicon_issue_stage_map.py` который принимает task brief, генерирует minimal stage map (1-3 stages), записывает в TASKS{task_id}.

---

## 5. MECHANICUS (CANONICAL первый орган исполнения)

Owner meaning Сердце машины. Инструменты, registry, здоровье кодовой базы.

Practical operational role Toolscript assignment for stage execution.

Minimum viable operational function v0.1
```
Input task_id + stage_id + stage requirements
Action выбрать scriptstools из SCRIPT_REGISTRY, проверить их health, выдать TOOL_ASSIGNMENT_PACKET
Output TOOL_ASSIGNMENT_PACKET.json (scripts to use, commands allowed, risk level)
Stop condition если required tool missing or unhealthy → DEGRADED (не BLOCKED — агент может работать вручную)
```

Required files
- `ORGANSMECHANICUSSCRIPTSmechanicus_assign_tools.py` (нужен)
- `ORGANSMECHANICUSREGISTRYSCRIPT_REGISTRY.json` ✅ exists

Required ports
- `assign_tools_for_stage` (input stage_id, requirements → output tool_assignment)
- `report_tool_health` (input tool_id → output health_status)

Required schemas
- `tool_assignment_packet_v1.schema.json`

Required Sanctum HUD panel
- Machinery — показывает available tools, their health, last used, risk level, кнопка Run Tool Health Check

What can stop the task Ничего (DEGRADED, не BLOCKED — агент может работать без tools)

What requires Owner approval Using HIGH risk tools.

First small task Написать `mechanicus_assign_tools.py` который читает SCRIPT_REGISTRY, фильтрует по stage requirements, выдаёт assignment packet.

---

## 6. INQUISITION (CANONICAL второй орган исполнения)

Owner meaning Чистота и правосудие. Смысловой и технический суд.

Practical operational role Post-stage audit of diffs, artifacts, receipts.

Minimum viable operational function v0.1
```
Input task_id + stage_id + stage_result (diff, artifacts, receipts)
Action проверить diff на грязь, проверить artifacts на completeness, проверить receipts на integrity
Output AUDIT_RECEIPT.json с verdict CLEAN  DIRTY  SUSPICIOUS
Stop condition если SUSPICIOUS → задача останавливается, Owner review required
```

Required files
- `ORGANSINQUISITIONSCRIPTSinquisition_audit_stage.py` (нужен — текущие scripts = partial)
- `ORGANSINQUISITIONAUDIT_RULES` ✅ exists

Required ports
- `audit_stage_result` (input stage_id, diff, artifacts → output audit_receipt)
- `check_receipt_integrity` (input receipt_path → output integrity_status)

Required schemas
- `audit_receipt_v1.schema.json`

Required Sanctum HUD panel
- Audit — показывает last audit verdict, dirty findings count, suspicious items, кнопка Run Audit

What can stop the task SUSPICIOUS verdict → Owner review

What requires Owner approval Accepting DIRTY result, overriding SUSPICIOUS.

First small task Написать `inquisition_audit_stage.py` который принимает git diff output, проверяет на forbidden patterns (secrets, hardcoded paths, shell=True), выдаёт structured audit receipt.

---

## 7. THRONE (CANONICAL первый орган канона)

Owner meaning Чистое ядро канона. Kernel-like. Не загрязняется экспериментами.

Practical operational role Canon acceptance gate. Stores accepted-only state.

Minimum viable operational function v0.1
```
Input task_id + all stage results + all audit receipts + final bundle
Action Owner reviews and explicitly accepts or rejects
Output CANON_ACCEPTANCE_PACKET.json с verdict ACCEPTED  REJECTED  REDO
Stop condition REJECTED → task fails, REDO → back to specific stage
```

Required files
- `ORGANSTHRONEORGAN_STATUS.json` (MISSING — нужен scaffold)
- `ORGANSTHRONESCRIPTSthrone_acceptance_gate.py` (нужен)
- `ORGANSTHRONECANON` — хранилище принятых состояний (future)

Required ports
- `request_canon_acceptance` (input task_id, evidence_bundle → output acceptance_packet)
- `get_canon_state` (input → output current canonical HEADstate)

Required schemas
- `canon_acceptance_packet_v1.schema.json`

Required Sanctum HUD panel
- Throne — показывает current canon state (HEAD, last accepted task), pending acceptance requests, кнопка Accept  Reject  Redo (Owner only)

What can stop the task Owner REJECT

What requires Owner approval ВСЕГДА. Throne = Owner-only gate.

IMPORTANT Throne не должен быть автоматизирован. Это единственный орган, где Owner ВСЕГДА решает лично.

First small task Создать scaffold `ORGANSTHRONEORGAN_STATUS.json` + `README.md` + minimal acceptance script that writes receipt.

---

## 8. CUSTODES (CANONICAL второй орган канона)

Owner meaning Охрана Трона. Shield layer. Backup policy. Граница между рабочим и каноническим контуром.

Practical operational role Canon boundary enforcement, backup verification, contamination prevention.

Minimum viable operational function v0.1
```
Input canon_acceptance_packet + current canon state
Action проверить что accepted state не содержит contamination, создать backup point, обновить canon boundary marker
Output CUSTODES_GUARD_RECEIPT.json
Stop condition если contamination detected → REJECT acceptance, escalate to Owner
```

Required files
- `ORGANSCUSTODESORGAN_STATUS.json` (MISSING — нужен scaffold)
- `ORGANSCUSTODESSCRIPTScustodes_guard_canon.py` (нужен)
- `ORGANSCUSTODESBOUNDARY` — boundary definitions

Required ports
- `guard_canon_acceptance` (input acceptance_packet → output guard_receipt)
- `verify_canon_integrity` (input → output integrity_status)
- `create_backup_point` (input → output backup_receipt)

Required schemas
- `custodes_guard_receipt_v1.schema.json`
- `canon_boundary_definition_v1.schema.json`

Required Sanctum HUD panel
- Custodes — показывает canon boundary status, last backup, integrity check result, contamination alerts

What can stop the task Contamination in accepted state

What requires Owner approval Overriding Custodes rejection (should be extremely rare).

First small task Создать scaffold + boundary definition file that lists what constitutes canon vs working state.

---

## 9. STRATEGIUM (CANONICAL первый орган усиления)

Owner meaning Тихий research organ. Малоресурсно анализирует, ищет улучшения.

Practical operational role Asynchronous improvement research triggered by completed tasks.

Minimum viable operational function v0.1
```
Input last N completed tasks + last N commits + current known_defects
Action тихо проанализировать, найти области для улучшения, поискать внешние ресурсы
Output RESEARCH_FINDING_PACKET.json (areas, links, why_useful, priority)
Trigger NOT per-task. Periodic or Owner-triggered.
```

Required files
- `ORGANSSTRATEGIUMORGAN_STATUS.json` (MISSING — нужен scaffold)
- `ORGANSSTRATEGIUMSCRIPTSstrategium_scan.py` (нужен)
- `ORGANSSTRATEGIUMFINDINGS` — accumulated research

Required ports
- `scan_for_improvements` (input recent_history → output findings_packet)
- `get_pending_findings` (input → output list of unreviewed findings)

Required schemas
- `research_finding_packet_v1.schema.json`

Required Sanctum HUD panel
- Research — показывает pending findings count, last scan date, top findings, кнопка Trigger Scan (Owner only)

What can stop the task Ничего. Strategium не блокирует.

What requires Owner approval Acting on findings (findings are advisory only).

IMPORTANT Strategium НИКОГДА не должен автоматически менять код или архитектуру. Только advisory output.

First small task Создать scaffold + minimal scan script that reads git log -10 and KNOWN_DEFECTS and outputs a findings packet.

---

## 10. SCHOLA IMPERIALIS (CANONICAL второй орган усиления)

Owner meaning Обучение Owner. Учебный путь из развития системы.

Practical operational role Extract learning topics from system changes for Owner growth.

Minimum viable operational function v0.1
```
Input last N completed tasks + their diffs + their audit receipts
Action выделить темы для обучения Owner, объяснить что стоит изучить
Output OWNER_LEARNING_NOTE.json (topics, why_learn, resources, priority)
Trigger NOT per-task. Periodic or Owner-triggered.
```

Required files
- `ORGANSSCHOLA_IMPERIALISORGAN_STATUS.json` (MISSING — нужен scaffold)
- `ORGANSSCHOLA_IMPERIALISSCRIPTSschola_extract_learning.py` (нужен)
- `ORGANSSCHOLA_IMPERIALISNOTES` — accumulated learning notes

Required ports
- `extract_learning_topics` (input recent_tasks → output learning_note)
- `get_learning_queue` (input → output prioritized topics)

Required schemas
- `owner_learning_note_v1.schema.json`

Required Sanctum HUD panel
- Learning — показывает pending learning topics, priority, last note date, кнопка Generate Learning Note

What can stop the task Ничего. Schola не блокирует.

What requires Owner approval Ничего (advisory only).

First small task Создать scaffold + minimal script that reads last 5 commit messages and generates a learning note.

---

# 3. Proposed organ folder standard

## v0.1 Minimum (для scaffold)

```
ORGANS{ORGAN_NAME}
├── ORGAN_STATUS.json          # maturity level, alivedead, last check
├── README.md                  # human description of role
└── PORTS                     # at least one port schema
    └── {port_name}.schema.json
```

## v0.2 Operational (для работающего органа)

```
ORGANS{ORGAN_NAME}
├── ORGAN_STATUS.json
├── ORGAN_CONTRACT.json        # responsibility, forbidden, upstream, downstream
├── README.md
├── PORTS
│   └── .schema.json
├── SCHEMAS
│   └── .schema.json
├── SCRIPTS
│   └── {organ}_{function}.py
├── UTILITY                   # organ-specific toolsdashboards
├── RECEIPTS                  # receipt templates or examples
└── CURRENT                   # current runtime state (if needed)
```

## v0.3 Full (позже)

```
+ TESTS                       # organ-specific tests
+ EXAMPLES                    # usage examples for agents
+ RECEIPT_TEMPLATES           # standard receipt shapes
```

SUGGESTION Не требовать v0.3 сейчас. v0.1 scaffold для missing organs, v0.2 для existing organs.

---

# 4. Machine-readable contracts

## Ключевые packet schemas (описание полей)

### organ_status_v1
```
organ_id, maturity_level (0-7), alive (bool), last_health_check (timestamp),
known_issues (list), can_accept_tasks (bool)
```

### organ_contract_v1
```
organ_id, responsibility (text), forbidden_actions (list),
upstream_callers (list), downstream_dependencies (list),
ports_provided (list), stop_conditions (list)
```

### preflight_receipt_v1
```
task_id, timestamp_utc, organ_statuses (map), verify_repo_verdict,
known_defects_active (list), verdict (CLEARBLOCKEDDEGRADED), blockers (list)
```

### task_address_packet_v1
```
task_id, workspace_path, forbidden_zones (list), read_sources (list),
write_targets (list), ledger_entry_id, registered_at
```

### agent_corridor_packet_v1
```
task_id, agent_id, mode (DRAFT_ONLYEXECUTEREVIEW),
allowed_actions (list), forbidden_actions (list),
stop_conditions (list), style_requirements (text),
owner_approval_required_for (list)
```

### stage_map_v2
```
task_id, stages (list of {stage_id, title, order, pass_criteria, dependencies, status}),
current_stage_id, completion_percentage
```

### tool_assignment_packet_v1
```
task_id, stage_id, assigned_tools (list of {tool_id, path, risk_level, command_gateway_id}),
manual_fallback_allowed (bool)
```

### audit_receipt_v1
```
task_id, stage_id, timestamp_utc, diff_summary, findings (list),
verdict (CLEANDIRTYSUSPICIOUS), recommendations (list)
```

### canon_acceptance_packet_v1
```
task_id, timestamp_utc, owner_decision (ACCEPTEDREJECTEDREDO),
accepted_commit_hash, evidence_bundle_path, notes
```

### research_finding_packet_v1
```
scan_id, timestamp_utc, trigger (periodicmanual), areas (list),
findings (list of {topic, why_useful, external_links, priority}),
actionable (bool)
```

### owner_learning_note_v1
```
note_id, timestamp_utc, source_tasks (list), topics (list of {title, why_learn, resources, priority}),
estimated_time_minutes
```

---

# 5. Full task path through organs

```
TASK_ID enters system (Owner gives goal)
│
├─→ [1] DOCTRINARIUM preflight
│   Input task_id
│   Output PREFLIGHT_RECEIPT.json
│   File .imperium_runtimedoctrinariumpreflight{task_id}.json
│   Stop verdict=BLOCKED → task rejected
│   Owner approval не нужен
│   Sanctum System Health panel shows greenyellowred
│
├─→ [2] ADMINISTRATUM task address
│   Input task_id + preflight_receipt
│   Output TASK_ADDRESS_PACKET.json
│   File ORGANSADMINISTRATUMMEMORYTASKS{task_id}ADDRESS.json
│   Stop duplicate task_id → BLOCKED
│   Owner approval не нужен
│   Sanctum Task Registry shows new task registered
│
├─→ [3] OFFICIO AGENTIS executor corridor
│   Input task_id + address_packet + agent_id
│   Output AGENT_CORRIDOR_PACKET.json
│   File .imperium_runtimeofficio{task_id}CORRIDOR.json
│   Stop unknown agent → BLOCKED
│   Owner approval mode change DRAFT→EXECUTE
│   Sanctum Agent Mode shows current corridor
│
├─→ [4] ASTRONOMICON stage map
│   Input task_id + address + corridor
│   Output STAGE_MAP.json
│   File ORGANSASTRONOMICONTASKS{task_id}STAGE_MAP.json
│   Stop invalid map → BLOCKED
│   Owner approval map modification after start
│   Sanctum Task Map shows stage pipeline
│
├─→ [5] MECHANICUS tool assignment (per stage)
│   Input stage_id + requirements
│   Output TOOL_ASSIGNMENT_PACKET.json
│   File .imperium_runtimemechanicus{task_id}{stage_id}TOOLS.json
│   Stop never (DEGRADED only)
│   Owner approval HIGH risk tools
│   Sanctum Machinery shows assigned tools
│
├─→ [6] SERVITOR EXECUTION (per stage)
│   Agent works within corridor, using assigned tools
│   Produces diff, artifacts, receipts
│
├─→ [7] INQUISITION audit (per stage)
│   Input stage_id + diff + artifacts
│   Output AUDIT_RECEIPT.json
│   File .imperium_runtimeinquisition{task_id}{stage_id}AUDIT.json
│   Stop SUSPICIOUS → Owner review
│   Owner approval override SUSPICIOUS
│   Sanctum Audit shows verdict
│
├─→ [8] ADMINISTRATUM stage record
│   Input stage_id + audit_receipt
│   Output LEDGER_ENTRY.json
│   Sanctum Task Registry updates completion %
│
├─→ [9] ASTRONOMICON stage advance
│   Input stage_id + result
│   Output next_stage or TASK_COMPLETE
│   Sanctum Task Map advances pointer
│
├─→ [LOOP repeat 5-9 for each stage]
│
├─→ [10] THRONE canon acceptance (Owner only)
│   Input task_id + all evidence
│   Output CANON_ACCEPTANCE_PACKET.json
│   Stop REJECTED → task fails
│   Owner approval ALWAYS
│   Sanctum Throne shows pending + AcceptReject buttons
│
├─→ [11] CUSTODES guard and backup
│   Input acceptance_packet
│   Output GUARD_RECEIPT.json + backup point
│   Stop contamination → reject acceptance
│   Sanctum Custodes shows boundary status
│
├─→ [12] STRATEGIUM async research (non-blocking)
│   Trigger periodic or Owner
│   Output RESEARCH_FINDINGS.json
│   Sanctum Research shows pending findings
│
└─→ [13] SCHOLA Owner learning (non-blocking)
    Trigger periodic or Owner
    Output LEARNING_NOTE.json
    Sanctum Learning shows topics
```

---

# 6. Sanctum as internal HUD

## Принципы

1. НЕ создавать sanctum_v0_30. Модуляризовать v0.29 позже.
2. Каждый орган = одна панельвиджет внутри Sanctum, не отдельное окно.
3. Панели читают runtimestate файлы, не hardcoded chips.
4. Sanctum = read + trigger, не execute. Execution идёт через command gateway.

## 10 organ panels

 Орган  Panel name  Показывает  Кнопки  Data source 
----

---


```markdown
# IMPERIUM — ADVISORY HARDENING REPORT (ПРОДОЛЖЕНИЕ)
## Секции 6–13 | Kiro | 2026-05-12

---

# 6. Sanctum as internal HUD (продолжение)

## 10 organ panels

| # | Орган | Panel name | Показывает | Кнопки | Data source | Actions allowed |
|---|-------|-----------|-----------|--------|-------------|-----------------|
| 1 | Doctrinarium | System Health | 10 organ statuses, verify_repo verdict, blockers | Run Preflight | `ORGANS/*/ORGAN_STATUS.json` + `.imperium_runtime/verification_spine/` | Trigger preflight (read-only result) |
| 2 | Administratum | Task Registry | Active tasks, stages, completion %, history | Register Task, View Ledger | `ORGANS/ADMINISTRATUM/MEMORY/TASKS/` | Register new task (creates address packet) |
| 3 | Officio Agentis | Agent Mode | Current agent profile, mode, corridor, forbidden | Change Mode (Owner only) | `.imperium_runtime/officio/` + `ORGANS/OFFICIO_AGENTIS/AGENT_PROFILES/` | Mode switch requires Owner confirm |
| 4 | Astronomicon | Task Map | Stage pipeline visual, current stage, pass/fail | View Stage Details | `ORGANS/ASTRONOMICON/TASKS/{task_id}/STAGE_MAP.json` | Read-only (map changes need Owner) |
| 5 | Mechanicus | Machinery | Available tools, health, risk, last used | Run Tool Health Check | `REGISTRY/SCRIPT_REGISTRY.json` + `ORGANS/MECHANICUS/REGISTRY/` | Trigger health check |
| 6 | Inquisition | Audit | Last audit verdict, findings, dirty count | Run Audit | `.imperium_runtime/inquisition/` | Trigger audit on current diff |
| 7 | Throne | Canon | Current canon HEAD, pending acceptances | Accept / Reject / Redo | `.imperium_runtime/throne/` | Owner-only buttons |
| 8 | Custodes | Guard | Boundary status, last backup, integrity | Verify Integrity | `.imperium_runtime/custodes/` | Trigger integrity check |
| 9 | Strategium | Research | Pending findings, last scan, top items | Trigger Scan | `ORGANS/STRATEGIUM/FINDINGS/` | Owner-triggered scan |
| 10 | Schola | Learning | Topics queue, priority, last note | Generate Note | `ORGANS/SCHOLA_IMPERIALIS/NOTES/` | Owner-triggered generation |

## Архитектурный подход к модуляризации

**SUGGESTION:** Не переписывать Sanctum сейчас. Вместо этого:

1. **Фаза 1 (сейчас):** Добавить один файл `SANCTUM/organ_hud_data.py` — сервис, который читает все ORGAN_STATUS.json и runtime файлы, возвращает structured dict.
2. **Фаза 2 (позже):** Заменить hardcoded chips в PlanetMapWidget на данные из organ_hud_data.
3. **Фаза 3 (ещё позже):** Вынести каждую панель в `SANCTUM/widgets/{organ}_panel.py`.

Это позволяет эволюционировать без version explosion.

---

# 7. Registry and discoverability plan

## Текущий drift (OBSERVED)

| Registry | Записей | Реальность | Drift severity |
|----------|---------|-----------|----------------|
| ORGAN_REGISTRY | 3 органа | 6 существуют, 10 в доктрине | CRITICAL |
| SCRIPT_REGISTRY | 8 (+ UNKNOWN) | 50+ скриптов | CRITICAL |
| COMMAND_ALLOWLIST | 7 команд | Sanctum использует 15+ | HIGH |
| PORT_REGISTRY | Существует | Не проверен | UNKNOWN |

## Staged synchronization plan

### Stage 1: ORGAN_REGISTRY (приоритет P0)

Добавить все 10 органов. Для missing 4 — status: `"maturity": "LEVEL_0_NAME_ONLY"`.

```
Минимальная запись для каждого органа:
{
  "organ_id": "CUSTODES",
  "path": "ORGANS/CUSTODES",
  "maturity": "LEVEL_0_NAME_ONLY",
  "responsibility": "canon boundary protection and backup",
  "exists_on_filesystem": false,
  "category": "canon_and_protection"
}
```

**Acceptance:** `jq '.organs | length' REGISTRY/ORGAN_REGISTRY.json` = 10

### Stage 2: COMMAND_ALLOWLIST (приоритет P1)

Добавить команды, которые Sanctum уже использует:
- `ssh.test_route`
- `scp.send_file`
- `scp.fetch_bundle`
- `explorer.open_folder`
- `powershell.run_git_cli_check`
- `python.verify_repo`
- `python.check_agent_entrypoint`
- `pytest.quick`

**Acceptance:** Каждый subprocess вызов в Sanctum имеет соответствующий command_id в allowlist.

### Stage 3: SCRIPT_REGISTRY (приоритет P2)

Автогенерация из filesystem:
```bash
git ls-files 'TOOLS/*.py' 'TOOLS/*.ps1' 'ORGANS/*/SCRIPTS/*.py' 'scripts/*.py'
```

Для каждого файла — минимальная запись: path, owner_organ, safe_to_run, destructive.

**Acceptance:** Нет UNKNOWN placeholder. Каждый tracked script имеет запись.

### Stage 4: PORT_REGISTRY (приоритет P3)

Синхронизировать с реальными `ORGANS/*/PORTS/*.schema.json`.

---

# 8. Verification and gates

## Необходимые gates перед full IMPERIUM run

| Gate ID | Что проверяет | Где живёт | Приоритет |
|---------|--------------|-----------|-----------|
| `organ_existence` | Все 10 органов имеют ORGAN_STATUS.json | `scripts/` | P0 |
| `organ_contract` | Все operational органы имеют ORGAN_CONTRACT.json | `scripts/` | P1 |
| `registry_drift` | ORGAN_REGISTRY.organs.length >= ORGANS/ folder count | `scripts/` | P0 |
| `script_registry_coverage` | Каждый tracked .py/.ps1 в TOOLS/ORGANS/scripts имеет запись | `scripts/` | P2 |
| `warning_baseline_regression` | warnings <= baseline + threshold | `scripts/` | P0 |
| `task_chain_dry_run` | Doctrinarium→Administratum→Officio→Astronomicon chain executes without crash | `tests/` | P2 |
| `sanctum_hud_data_source` | Sanctum chips read from files, not hardcoded | `tests/` | P3 |
| `command_gateway_coverage` | Каждый subprocess в active code имеет command_id | `scripts/` | P1 |
| `public_private_boundary` | Нет secrets в tracked files | `scripts/` ✅ exists | P0 |
| `canon_custodes_boundary` | Throne/Custodes folders exist and have boundary definition | `scripts/` | P2 |

## Реализация

Каждый gate = Python функция в `scripts/` которая:
- Возвращает `{"gate_id": "...", "verdict": "PASS|FAIL|PASS_WITH_WARNINGS", "blockers": [...], "warnings": [...]}`
- Добавляется в `scripts/verify_repo.py` как дополнительный gate

**SUGGESTION:** Добавлять gates по одному. Не все сразу. Порядок: organ_existence → registry_drift → warning_baseline → остальные.

---

# 9. Blocker map

## Blockers для "Full IMPERIUM organ-driven task run"

| # | Severity | Blocker | Affected organ | Evidence | Impact | Minimal fix | Acceptance |
|---|----------|---------|---------------|----------|--------|-------------|------------|
| 1 | CRITICAL | 4 органа не существуют | Custodes, Strategium, Schola, Throne | `ORGANS/` has 6 folders | Task lifecycle неисполним end-to-end | Создать scaffold (STATUS + README) | `ls ORGANS/*/ORGAN_STATUS.json \| wc -l` = 10 |
| 2 | CRITICAL | 121K warnings = шум | Все (verification) | verify_repo output | Regression detection невозможен | Untrack continuity packs + baseline | warnings < 200 |
| 3 | CRITICAL | Нет task orchestrator | Все | Отсутствие кода | Задачи не проходят через органы | Minimal pipeline script | Dry-run проходит без crash |
| 4 | HIGH | ORGAN_REGISTRY drift (3/10) | Administratum | REGISTRY/ORGAN_REGISTRY.json | Агенты не видят органы | Sync to 10 entries | `.organs \| length` = 10 |
| 5 | HIGH | Sanctum bypasses gateway | Mechanicus | sanctum_v0_29_qt.py subprocess calls | Security boundary нарушена | Migrate to gateway calls | `rg "subprocess\.(run\|Popen)" SANCTUM/sanctum_v0_29_qt.py` = 0 (кроме import) |
| 6 | HIGH | Hardcoded E:\IMPERIUM | Mechanicus | sanctum_v0_29_qt.py:43 | Не работает на VM2/другом PC | Use detect_repo_root() | `rg "Path.*E:" SANCTUM/sanctum_v0_29_qt.py` = 0 |
| 7 | HIGH | Нет Doctrinarium preflight v1 | Doctrinarium | Текущий = smoke заглушка | Первый gate не работает | Написать real preflight | Script reads all ORGAN_STATUS and returns structured receipt |
| 8 | MEDIUM | SCRIPT_REGISTRY drift (8/50+) | Mechanicus | REGISTRY/SCRIPT_REGISTRY.json | Tools не discoverable | Autogenerate from filesystem | No UNKNOWN entries |
| 9 | MEDIUM | Нет CI/CD | Все | .github/ empty | Нет автоматической проверки | GitHub Actions workflow | Push triggers CI |
| 10 | MEDIUM | Нет Owner approval gate в коде | Throne | Organ missing | Acceptance = manual chat only | Throne scaffold + acceptance script | Script writes CANON_ACCEPTANCE receipt |
| 11 | MEDIUM | Continuity packs в Git (429 files) | Administratum | git ls-files count | Repo bloat + warning source | git rm --cached + .gitignore | 0 tracked continuity pack files |
| 12 | LOW | 11 Sanctum versions tracked | Mechanicus | SANCTUM/*.py | Dead code noise | Archive v0.1-v0.28 | Only v0.29 + service in active |
| 13 | LOW | Нет Sanctum organ HUD | Все | Hardcoded chips | Sanctum не показывает реальность | organ_hud_data.py service | Chips read from files |

---

# 10. Suggested staged implementation (ADVISORY, не final roadmap)

## Stage 0: Preserve doctrine (ТЕКУЩИЙ ШАГ)
- Создать `DOCS/OWNER_DOCTRINE/`
- Положить Owner Organ Doctrine + Registration Plan
- Commit как doctrine registration
- **Acceptance:** Files exist, no code changes

## Stage 1: Missing organ scaffolds
- Создать `ORGANS/CUSTODES/`, `ORGANS/STRATEGIUM/`, `ORGANS/SCHOLA_IMPERIALIS/`, `ORGANS/THRONE/`
- Каждый: ORGAN_STATUS.json (LEVEL_0) + README.md
- **Acceptance:** 10 ORGAN_STATUS.json exist

## Stage 2: Registry sync
- ORGAN_REGISTRY → 10 entries
- SCRIPT_REGISTRY → autogenerate, remove UNKNOWN
- **Acceptance:** No drift between registry and filesystem

## Stage 3: Warning flood fix
- Untrack continuity packs (git rm --cached)
- Add to .gitignore
- Create WARNING_BASELINE.json
- **Acceptance:** verify_repo warnings < 200

## Stage 4: Doctrinarium preflight v1
- Real preflight script that checks all organ statuses
- Returns structured receipt
- **Acceptance:** `python doctrinarium_preflight_v1.py` returns valid JSON receipt

## Stage 5: Administratum task address
- Script that creates task workspace and address packet
- **Acceptance:** Running script creates MEMORY/TASKS/{id}/ADDRESS.json

## Stage 6: Officio corridor + Astronomicon stage map
- Corridor packet generator
- Stage map generator (minimal: 1-3 stages)
- **Acceptance:** Both produce valid JSON packets

## Stage 7: Mechanicus tool assignment + Inquisition audit
- Tool assignment from SCRIPT_REGISTRY
- Basic audit (forbidden patterns, secrets, hardcoded paths)
- **Acceptance:** Both produce valid receipts

## Stage 8: Throne/Custodes boundary
- Throne acceptance script (Owner-triggered)
- Custodes boundary definition
- **Acceptance:** Owner can Accept/Reject via script, receipt written

## Stage 9: Sanctum organ HUD skeleton
- organ_hud_data.py reads all organ statuses
- Replace hardcoded chips with real data
- **Acceptance:** Sanctum shows real organ maturity levels

## Stage 10: Strategium/Schola async loops
- Strategium scan script
- Schola learning note generator
- **Acceptance:** Both produce advisory output on demand

## Stage 11: Command gateway migration
- Migrate Sanctum subprocess to gateway
- Add all commands to allowlist
- **Acceptance:** No raw subprocess in active Sanctum code

## LATER (не сейчас):
- Full task orchestrator pipeline
- CI/CD
- Freelance Console
- Arsenal/Scriptorium
- Multi-agent coordination

---

# 11. Public/private and portfolio advice

## Что можно показывать публично

- "Я проектирую AI-assisted workflow systems с verification, receipts и evidence-based automation"
- "Я строю operator dashboards для управления LLM-агентами"
- "Я реализую agent workflow organization с gates, checks и Owner approval"
- "Я работаю с multi-contour systems (PC + VM + cloud)"
- "Я использую structured receipts и audit trails для контроля качества AI-работы"
- Screenshots Sanctum (без sensitive data в чипах)
- Screenshots AI Operator Console visual prototype
- Общие архитектурные диаграммы (без внутренних имён органов)

## Что НЕЛЬЗЯ показывать

- Полную цепочку 10 органов с именами и ролями
- Внутренние промпты для агентов
- Security boundaries и command gateway logic
- Private paths (VM2, SSH keys, transfer routes)
- Содержимое continuity packs
- Внутренние receipts с operational data
- Полный AGENTS.md
- Doctrine documents

## Безопасная формулировка для portfolio/LinkedIn/freelance

> "I design and build AI-assisted workflow automation systems with structured verification, evidence-based quality control, operator dashboards, and multi-environment agent coordination. My approach includes formal gates, receipts, audit trails, and explicit approval workflows — ensuring AI work is controlled, traceable, and reliable."

---

# 12. Advice to Logos-Prime

## Что делать дальше

1. **Немедленно:** Помочь Owner зафиксировать doctrine в `DOCS/OWNER_DOCTRINE/` (Stage 0). Это уже готово к commit.

2. **Следующий документ:** `DOCS/OWNER_DOCTRINE/ORGAN_OPERATING_MODEL_V0_1.md` — перевод доктрины в machine-readable форму (yaml/json описание каждого органа с полями из секции 4 этого отчёта).

3. **Спросить Owner:** Вопросы из секции 13 ниже. Особенно про Throne contour и Custodes boundary.

4. **НЕ делать:**
   - Не начинать код без Stage 0-1 completion
   - Не менять порядок органов
   - Не строить Freelance Console
   - Не создавать sanctum_v0_30
   - Не публиковать внутреннюю архитектуру

5. **Отправить Speculum/Inquisition позже:**
   - Organ Operating Model для red-team
   - Task path diagram для stress-test
   - Blocker map для verification

---

# 13. Questions for Owner

## Критические вопросы (нужны ответы до Stage 2)

**1. Throne contour:**
Throne = "живёт на ноуте / защищённом контуре". Это значит:
- Throne = отдельная папка в том же репо?
- Throne = отдельный Git branch?
- Throne = отдельный физический диск/раздел?
- Throne = snapshot на внешнем диске?

Какой именно contour? Это определяет, как Custodes будет работать.

**2. Custodes backup policy:**
- Backup = git tag на accepted commit?
- Backup = zip на внешний диск?
- Backup = отдельный clone?
- Как часто?
- Кто триггерит?

**3. Strategium trigger:**
- Запускается автоматически после каждого N-го коммита?
- Запускается только по Owner команде?
- Имеет доступ к интернету для research?
- Может ли использовать web search?

**4. Schola trigger:**
- После каждой завершённой задачи?
- Раз в неделю?
- Только по Owner запросу?

**5. Agent autonomy level:**
- Агент может commit самостоятельно? (текущий ответ: НЕТ, только PC Owner)
- Агент может push? (текущий ответ: НЕТ)
- Агент может менять stage map? (текущий ответ: НЕТ без Owner)
- Агент может override SUSPICIOUS audit? (текущий ответ: НЕТ)

**6. Sanctum feel:**
- Текущий cosmic/planet стиль сохраняется?
- Organ panels = отдельные вкладки или всё на одном экране?
- Приоритет: красота или информативность?

**7. Public boundary:**
- GitHub repo остаётся public?
- Если да — нужен ли отдельный private repo для sensitive parts?
- Или достаточно .gitignore + boundary scan?

---

*Advisory hardening report завершён. Порядок органов Owner сохранён (CANONICAL). Репозиторий не модифицирован. Следующий шаг: Owner отвечает на вопросы секции 13, затем Logos-Prime создаёт Organ Operating Model.*
```
