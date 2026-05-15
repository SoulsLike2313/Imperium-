# FULL QUESTIONNAIRE PREFILL MATRIX — OWNER-READABLE RU V0.1

Document ID: FULL_QUESTIONNAIRE_PREFILL_MATRIX_RU_OWNER_APPROVED_V0_1  
Task ID: TASK-20260515-FOUNDATIONAL-ORGANS-V1-DEFINITION-V0_1  
Status: Owner-readable approved draft  
Canonical policy: machine/canonical artifacts remain English; this file is a Russian Owner-facing companion.  
Created UTC: 2026-05-15T00:00:00Z  
Source basis:
- Kiro foundational organs V1 questionnaire advisory.
- Owner 15 decisive answers.
- Owner follow-up dispute resolutions.
- Doctrinarium MVP/0.1 already built.
- Owner dashboard truth + beauty doctrine.

---

## 0. Short meaning

Эта матрица фиксирует, какой Owner видит V1-форму первых четырёх органов IMPERIUM:

1. **Astronomicon** — память будущих задач, scope, stage maps, registration workflow, review/export/import packs, визуальная карта задачи.
2. **Administratum** — execution truth, lifecycle, route sheet, black-box ledger, stage metrics, receipts, bundle/continuity pack.
3. **Officio Agentis** — role/mode/agent contracts, response contracts, prompt rules, stop conditions, доказательство, что агент действует в правильной роли и по правильным законам.
4. **Doctrinarium** — law/canon/doctrine, organ health gate, task-start readiness gate, law execution proof, violations, disabled Inquisition hook.

Главный V1-target: **полностью рабочий logged task corridor**, где Servitor приходит только с `TASK_ID`, проходит через четыре органа, выполняет stages, а система знает всё: что было, где было, почему было разрешено, какие evidence, какие reports, какой bundle.

---

## 1. Status dictionary / словарь статусов

| Status | Русское значение |
|---|---|
| `accepted_draft` | Owner принимает как базовое решение v0.1. Ещё не финальный закон, но это рабочая позиция для hardening plan. |
| `needs_owner_review` | Требует уточнения Owner. После этой версии почти все спорные пункты закрыты. |
| `defer_to_v1_1` | Не делаем в первом V1; откладываем на V1.1 / следующий hardening layer. |
| `mega_hardening` | Большая будущая тема, не сейчас. |
| `reference_only` | Только справочный материал, не принято как решение. |
| `owner_resolved` | Ранее спорный пункт закрыт Owner-ответом. |

---

## 2. Cross-organ standards / общие стандарты для всех органов

| ID | Area | Prefill / decision | Русское пояснение | Status |
|---|---|---|---|---|
| CROSS-01 | Universal evidence format | `json_plus_markdown_summary` | Основное evidence хранится в JSON, чтобы его читали scripts/checkers/dashboards. MD-summary можно добавлять для человека. | accepted_draft |
| CROSS-02 | Common self-report schema | `organ_id`, `timestamp`, `status_enum`, `check_results_array`, `warnings_array`, `blockers_array`, `evidence_links`, `source_reports`, `freshness` | У всех органов должен быть единый self-report: кто он, когда обновлялся, какой статус, какие warnings/blockers, где evidence. | accepted_draft |
| CROSS-03 | Universal status enum | `PASS`, `PASS_WITH_WARNINGS`, `FAIL`, `BLOCKED`, `UNKNOWN`, `NOT_APPLICABLE` | Все органы используют один язык статусов. | accepted_draft |
| CROSS-04 | Warning severity scale | `INFO`, `WARNING`, `ERROR`, `BLOCKER`, `CRITICAL` | Единая шкала серьёзности для alerts/reports/dashboards. | accepted_draft |
| CROSS-05 | Blocker vocabulary | `MISSING_EVIDENCE`, `SCHEMA_VIOLATION`, `OWNER_APPROVAL_REQUIRED`, `DEPENDENCY_FAILED`, `TIMEOUT`, `CONFLICT_UNRESOLVED`, `STALE_TRUTH`, `OWNERSHIP_COLLISION`, `FAKE_GREEN_RISK` | Общий словарь причин блокировки. Dashboard не должен писать произвольную кашу. | accepted_draft |
| CROSS-06 | Lifecycle hooks | `on_task_registered`, `on_task_requested`, `on_task_started`, `on_stage_started`, `on_stage_completed`, `on_task_blocked`, `on_task_failed`, `on_task_completed`, `on_bundle_collected` | Органы должны понимать общие события жизненного цикла задачи. | accepted_draft |
| CROSS-07 | No-fake-green proof | evidence exists + non-empty + schema-valid + fresh + provenance/hash + linked to visible status | Зелёный статус разрешён только если есть настоящее доказательство, и оно связано с видимым статусом. | accepted_draft |
| CROSS-08 | Dashboard language policy | canonical files English; UI/dashboard bilingual EN/RU toggle | Canonical machine state на английском; любой dashboard/app UI обязан иметь EN/RU. | accepted_draft |
| CROSS-09 | Visual style source | organ-specific themes + Sanctum unified command-flow shell | У каждого органа свой дух/стиль, Sanctum сшивает это в единый красивый поток. | accepted_draft |
| CROSS-10 | Sanctum integration | organs have standalone backend/report truth; Sanctum aggregates through ports/adapters | Органы не растворяются в Sanctum. У них своя правда, а Sanctum её агрегирует. | accepted_draft |
| CROSS-11 | Receipt filename convention | `{TIMESTAMP}_{ORGAN}_{ACTION}.json` | Название receipts должно сортироваться по времени и ясно показывать орган/action. | accepted_draft |
| CROSS-12 | Report filename convention | `{TIMESTAMP}_{ORGAN}_{REPORT_TYPE}.json` | Reports тоже должны быть сортируемыми и понятными. | accepted_draft |
| CROSS-13 | Ownership enforcement | registry-based ownership check + folder boundary + schema field `owner_organ` | Границы органов проверяются не “на глаз”, а registry/schema/folder policy. | accepted_draft |
| CROSS-14 | Timestamp format | `ISO8601_UTC` | Везде единый формат времени UTC. | accepted_draft |
| CROSS-15 | Evidence retention | canonical active evidence kept; routine archive threshold starts at 14 days; canonical receipts/history are not casually deleted | Owner решил начать с 2 недель до архивирования обычных operational reports/evidence. Canonical receipts/history не удаляются, а архивируются/переносятся с индексом. | owner_resolved |

### CROSS-15 Owner resolution

Owner decision: **2 недели для начала**.  
Interpretation:
- operational evidence/reports older than 14 days may be moved into archive structure;
- canonical receipts, final bundles, law receipts, task completion records and continuity-significant artifacts are not deleted casually;
- archive must keep index/path/hash so evidence remains findable.

---

## 3. Astronomicon matrix

### Main role

Astronomicon — это память будущих задач и навигационная карта. Он хранит task scope, stage maps, registration workflow, review/export/import packs и визуализирует движение задачи. Фактическую execution progress truth он получает из Administratum.

### Role / rules / limits

| ID | Decision | Русское пояснение | Status |
|---|---|---|---|
| ASTRO-01 | Atomic unit = `stage` inside `task` | Astronomicon думает задачами и стадиями; stage — главная единица карты. | accepted_draft |
| ASTRO-02 | Reads lifecycle states from Administratum; owns stage topology/scope map | Lifecycle truth не у Astronomicon. Он показывает карту, но фактические execution states берёт из Administratum. | accepted_draft |
| ASTRO-03 | V1 design target: up to 50 concurrent stages | Дизайн V1 должен не рассыпаться на задачах до примерно 50 stages. | accepted_draft |
| ASTRO-04 | `routing_recommendations` in V1; mandatory gates later through Doctrinarium/Admin integration | В V1 Astronomicon не становится главным блокирующим судом. Блоки идут через Doctrinarium/Admin. | accepted_draft |
| ASTRO-05 | JSON receipt + optional MD summary | Переходы stages подтверждаются JSON receipt; MD-summary если надо человеку. | accepted_draft |
| ASTRO-06 | Owner + controlled registration scripts may modify stage maps | Stage map не редактирует кто попало. | accepted_draft |
| ASTRO-07 | Owns task/stage dependency graph; Strategium later owns higher strategic graph | Astronomicon владеет зависимостями внутри task/stage. Большая стратегия — позже Strategium. | accepted_draft |
| ASTRO-08 | No valid next stage = `block_and_alert`; Owner override requires receipt | Если нет следующей стадии — блокируем и показываем alert. Override только с доказательством. | accepted_draft |
| ASTRO-09 | Full history for registered tasks; archive later | История registered tasks должна сохраняться. | accepted_draft |
| ASTRO-10 | Self-report now; future Inquisition audit later | В V1 organ self-report, позже Inquisition сможет аудитить. | accepted_draft |
| ASTRO-11 | `on_event` + manual refresh | Обновление по событию и вручную, без тяжёлого polling. | accepted_draft |
| ASTRO-12 | Displays blocked state; source of block belongs to declaring organ/gate | Astronomicon показывает blocked, но не всегда является источником block. | accepted_draft |
| ASTRO-13 | Directed graph + linear pipeline mode | Для сложных задач graph, для простых — pipeline. | accepted_draft |
| ASTRO-14 | Standalone dashboard + Sanctum integration port | У Astronomicon есть свой dashboard и порт в Sanctum. | accepted_draft |

### Astronomicon dashboard

| ID | Decision | Русское пояснение | Status |
|---|---|---|---|
| ASTRO-DASH-01 | Stage map / task corridor is primary panel | Главная панель — карта задачи и stages. | accepted_draft |
| ASTRO-DASH-02 | Owner custom stage palette | Completed — тусклое мерцание; active — активный pulse; future — бело-платиновое звёздное сияние; blocked — severe red/amber. | accepted_draft |
| ASTRO-DASH-03 | Blocked stages pulse or border-highlight with reason | Блокировка должна быть видна и объяснена. | accepted_draft |
| ASTRO-DASH-04 | Hover shows stage name, goal, last update, blocker reason, receipt links, evidence completeness | Hover/details должны давать смысл, а не просто красивую всплывашку. | accepted_draft |
| ASTRO-DASH-05 | Transitions only with confirmation + receipt; unsafe zones display-only | Если dashboard делает переход — он создаёт receipt. Опасные действия только display/disabled. | accepted_draft |
| ASTRO-DASH-06 | 1000 ms normal target, 2000 ms acceptable for large map | Performance budget: быстро и плавно. | accepted_draft |
| ASTRO-DASH-07 | Inline timeline + separate detail view | История transitions видна прямо в dashboard и в деталях. | accepted_draft |
| ASTRO-DASH-08 | EN/RU toggle | UI двуязычный. | accepted_draft |

### Astronomicon V1 dashboard function target

Owner wants:
- кнопками провести регистрацию задачи;
- скачать/загрузить все нужные packs;
- оформить pack для Speculum/Kiro без лишних промтов;
- видеть stage progress, где цвет/свечение берётся из состояния, которое даёт Administratum;
- completed stage = тусклое мерцание;
- active stage = активное мерцание и анимация;
- future stage = бело-платиновое медленное звёздное сияние.

---

## 4. Administratum matrix

### Main role

Administratum — execution black box. Он принимает TASK_ID, ищет задачу в Astronomicon, выдаёт адреса и путевой лист, подтверждает старт, пишет каждый stage и собирает final bundle / continuity pack.

### Role / rules / limits

| ID | Decision | Русское пояснение | Status |
|---|---|---|---|
| ADMIN-01 | Canonical unit = `work_packet`, linked to TASK_ID/STAGE_ID/RUN_ID | Work packet связывает task, stage и конкретный run. | accepted_draft |
| ADMIN-02 | Owns task lifecycle execution state exclusively | Execution lifecycle truth принадлежит Administratum. | accepted_draft |
| ADMIN-03 | Mandatory fields: id, task_id, title, owner, created_utc, state, assigned_role, current_stage, route_sheet, evidence_paths, priority, source_registry_path | Work packet должен быть достаточно полным, чтобы система понимала, что происходит. | accepted_draft |
| ADMIN-04 | Every meaningful transition requires receipt | Каждый meaningful transition пишет receipt. | accepted_draft |
| ADMIN-05 | JSON canonical + MD summary where useful | Машина читает JSON, Owner может читать MD-summary. | accepted_draft |
| ADMIN-06 | Owner or controlled scripts create canonical packets; organs may propose | Canonical packets создаются только контролируемо. | accepted_draft |
| ADMIN-07 | Servitor submits evidence; Admin confirms via validated completion gate | Servitor не сам объявляет финальную правду; он приносит evidence, Admin подтверждает. | accepted_draft |
| ADMIN-08 | Stores/recommends priority in V1; hard enforcement later | В V1 Admin показывает priority и может рекомендовать, но жёстко не командует всем порядком. | accepted_draft |
| ADMIN-09 | Orphaned packets block/alert until assigned or Owner resolves | Задача без ответственного не должна тихо висеть зелёной. | accepted_draft |
| ADMIN-10 | Owns address book / artifact routing index; Doctrinarium owns policy law | Admin знает где что лежит; Doctrinarium говорит какие законы это регулируют. | accepted_draft |
| ADMIN-11 | Strict schema validation on accept | Приём work packet только через validation. | accepted_draft |
| ADMIN-12 | On-demand reports in V1; scheduled reports later | В V1 отчёты по запросу, расписание позже. | defer_to_v1_1 |
| ADMIN-13 | 14-day initial archive threshold for routine evidence; canonical task/continuity records retained by archive/index, not deleted | Owner решил: тоже пока 2 недели. Архивируем, не удаляем. Важные records должны оставаться доступными через индекс. | owner_resolved |
| ADMIN-14 | Owns Git truth check integration operationally; scripts can live under TOOLS/Mechanicus pattern | Git truth — часть operational truth Admin, но конкретные scripts могут быть registered elsewhere. | accepted_draft |

### Administratum dashboard

| ID | Decision | Русское пояснение | Status |
|---|---|---|---|
| ADMIN-DASH-01 | Work packet / task ledger is primary view | Главный вид — task ledger. | accepted_draft |
| ADMIN-DASH-02 | Columns: TASK_ID, state, current_stage, assigned_role, priority, last_update, blocker, evidence completeness, bundle status | Таблица должна сразу показывать живое состояние задачи. | accepted_draft |
| ADMIN-DASH-03 | State transitions only with confirmation + receipt | Dashboard transition без receipt запрещён. | accepted_draft |
| ADMIN-DASH-04 | Stale/overdue get badge + row highlight + alerts | Просрочки/зависания должны бросаться в глаза. | accepted_draft |
| ADMIN-DASH-05 | Receipt history visible in row and detail panel | История receipts должна читаться. | accepted_draft |
| ADMIN-DASH-06 | Filters by state, role/agent, priority, date, organ, blocker, task_id | Нужны фильтры для плотной работы. | accepted_draft |
| ADMIN-DASH-07 | No bulk actions in V1 except safe filters/exports | Массовые действия рискованны; пока только безопасные операции. | defer_to_v1_1 |
| ADMIN-DASH-08 | Active/blockers first, then updated_at desc | Самое важное наверху. | accepted_draft |

### Administratum priority owner resolution

Owner would like Admin to be able to force required order eventually, but tasks should be designed so stages already go one after another logically and chronologically.  
V1 decision:
- Admin shows priority;
- Admin can warn/block if a required dependency/order is violated;
- Admin does not become an arbitrary autonomous scheduler in V1.

---

## 5. Officio Agentis matrix

### Main role

Officio Agentis — organ of role/mode/agent contracts. Он доказывает, что агент работает в правильной роли, с правильными ограничениями, читает нужные laws/contracts и не самовольничает.

### Role / rules / limits

| ID | Decision | Русское пояснение | Status |
|---|---|---|---|
| OFFAG-01 | Agent = AI/human/script executor acting under role contract | Главное не имя агента, а role contract и mode. | accepted_draft |
| OFFAG-02 | Capabilities: role_id, mode_id, allowed_actions, forbidden_actions, task_type_allowlist, required_reads, response_contract, stop_conditions, evidence_requirements | Capability — это не просто skill list, а полный contract. | accepted_draft |
| OFFAG-03 | Recommend/validate only; no autonomous assignment in V1 | Пока без free auto-assign. Owner-gated. | accepted_draft |
| OFFAG-04 | No match = capability gap report + Owner/Logos decision | Если нет подходящего агента/роли — не продолжаем молча. | accepted_draft |
| OFFAG-05 | Advisory workload tracking only in V1 | Workload tracking позже. | defer_to_v1_1 |
| OFFAG-06 | Owner or controlled script with Owner approval registers agents/contracts | Регистрация ролей/агентов только контролируемо. | accepted_draft |
| OFFAG-07 | Owner can retire/deactivate; future Inquisition can suspend | Снятие/заморозка ролей под контролем. | accepted_draft |
| OFFAG-08 | Agents self-report/read receipt + Officio validates role contract health | Есть self-report/read receipt и валидация со стороны Officio. | accepted_draft |
| OFFAG-09 | On-demand task-context availability | В V1 нет полноценного scheduler. | accepted_draft |
| OFFAG-10 | Minimal performance history in V1; detailed metrics later | История performance позже. | defer_to_v1_1 |
| OFFAG-11 | Conflict = block until resolved | Конфликт ролей/агентов блокирует. | accepted_draft |
| OFFAG-12 | External agents via adapter/advisory buffer only | Kiro/other external agents только через controlled adapter/advisory. | accepted_draft |
| OFFAG-13 | Liveness = role contract exists + recent valid output/read receipt + assignment evidence | Живость агента доказывается evidence, не словами. | accepted_draft |

### Officio dashboard

| ID | Decision | Русское пояснение | Status |
|---|---|---|---|
| OFFAG-DASH-01 | Hybrid: role cards + permission matrix table | Нужны и карточки ролей, и матрица прав. | accepted_draft |
| OFFAG-DASH-02 | Statuses: active/inactive, available/busy, contract-valid/invalid, read-proof/missing, blocked | Dashboard должен показывать доверие к роли/агенту. | accepted_draft |
| OFFAG-DASH-03 | Current assignments visible: count + detail panel | Нужно видеть, кто сейчас где назначен. | accepted_draft |
| OFFAG-DASH-04 | Match visualization = why this role is allowed/not allowed | Dashboard должен объяснять, почему агент подходит или не подходит. | accepted_draft |
| OFFAG-DASH-05 | V1 only displays/validates; registration forms may be disabled/Owner-gated | Owner решил: пока только показывать и валидировать. Регистрация из UI не активная V1-функция. | owner_resolved |
| OFFAG-DASH-06 | Capability gaps in dedicated panel | Разрывы capabilities видны отдельно. | accepted_draft |
| OFFAG-DASH-07 | Simple charts later; V1 evidence/status metrics | Графики позже, сначала truth metrics. | defer_to_v1_1 |

---

## 6. Doctrinarium matrix

### Main role

Doctrinarium — закон, канон, doctrine, organ health gate, task-start gate. Servitor спрашивает: живы ли органы, можно ли работать, исполнимы ли законы?

### Role / rules / limits

| ID | Decision | Русское пояснение | Status |
|---|---|---|---|
| DOCTR-01 | Doctrine = accepted normative content: law, policy, organ rule, operational rule | Doctrine — принятое нормативное содержание системы. | accepted_draft |
| DOCTR-02 | Lifecycle: draft → review → owner_accepted → active → superseded/retired → archived | У doctrine/law должен быть lifecycle. | accepted_draft |
| DOCTR-03 | Owner, organs, external advisory may propose; only controlled ingest | Предлагать можно, canonize нельзя без Owner. | accepted_draft |
| DOCTR-04 | Canon acceptance = Owner only | Канон принимает только Owner. | accepted_draft |
| DOCTR-05 | V1 enforces compliance for defined gates; broader interpretation API later | В V1 Doctrinarium исполняет конкретные gates, широкий API позже. | accepted_draft |
| DOCTR-06 | Advisory/canon distinction by folders + status field + naming convention | Advisory и canon разделяются физически и статусно. | accepted_draft |
| DOCTR-07 | Compliance evidence = schema-valid report + gate verdict + checklist receipt + Owner approval where needed | Compliance доказывается report/verdict/receipt, не словами. | accepted_draft |
| DOCTR-08 | Owns law/doctrine schemas; cross-organ evidence schemas shared/registry-owned | Doctrinarium владеет law/doctrine schemas, но общие evidence schemas лучше shared. | accepted_draft |
| DOCTR-09 | Higher law wins; same-level conflict blocks until Owner decision or defined rule | Высший закон побеждает. Same-level conflict блокирует до решения. | accepted_draft |
| DOCTR-10 | Basic keyword/path search in V1; semantic search later | Простого поиска хватит для V1, semantic позже. | defer_to_v1_1 |
| DOCTR-11 | JSON canonical + MD human-readable pair | Закон машинно в JSON, человечески в MD. | accepted_draft |
| DOCTR-12 | Git history + law_change_receipt | История закона доказывается Git + change receipt. | accepted_draft |
| DOCTR-13 | External advisory ingested as draft/reference with Owner review gate | External advisory не становится canon автоматически. | accepted_draft |
| DOCTR-14 | Per-organ compliance reports in V1; global reports later | В V1 отчёты по органам, глобальный позже. | accepted_draft |

### Doctrinarium dashboard

| ID | Decision | Русское пояснение | Status |
|---|---|---|---|
| DOCTR-DASH-01 | Tree by category + flat searchable list | Законы/доктрины можно смотреть деревом и списком. | accepted_draft |
| DOCTR-DASH-02 | Badge + color + icon, all backed by reports | Статусы красивы, но всегда backed by reports. | accepted_draft |
| DOCTR-DASH-03 | Advisory visible in separate tab with warning: reference only | Advisory видно отдельно, с предупреждением. | accepted_draft |
| DOCTR-DASH-04 | Acceptance from dashboard only Owner-gated with approval receipt | Принятие закона из dashboard только Owner-gated + receipt. | accepted_draft |
| DOCTR-DASH-05 | Basic search V1; advanced filters later | Basic search достаточно. | accepted_draft |
| DOCTR-DASH-06 | Dedicated conflict panel | Конфликты законов должны быть отдельной панелью. | accepted_draft |
| DOCTR-DASH-07 | V1 requires law timeline + git history + law_change_receipt; simple field-change summary when practical; full visual side-by-side diff deferred to V1.1/hardening | Owner принял предложение: в V1 обязательно timeline + Git history + receipt. Если недорого — simple field-change summary. Красивый diff view позже. | owner_resolved |
| DOCTR-DASH-08 | Detailed compliance breakdown per organ | Видно, какие органы и как соблюдают laws. | accepted_draft |

### DOCTR-DASH-07 explanation

- **Timeline** показывает человеческую историю: law created, owner accepted, activated, updated, superseded/retired.
- **Git history** доказывает технический факт изменения файла в commit.
- **law_change_receipt** фиксирует approved law change with hashes/metadata.
- **Simple field-change summary** объясняет важные изменения вроде `warning → blocker`.
- **Full visual diff view** — удобный side-by-side UI, но это отдельная работа, поэтому откладывается.

---

## 7. Disputed points after Owner resolution

| Point | Resolution | Status |
|---|---|---|
| Evidence retention | Start with 14 days for routine evidence before archive. Canonical receipts/final evidence are archived/indexed, not casually deleted. | owner_resolved |
| Dashboard registration buttons | Seek balance using common practice: meaningful dashboard actions require confirmation, receipt, and safety scope. | accepted_draft |
| Officio registration from dashboard | V1 only shows and validates. Active registration from UI is not V1 default. | owner_resolved |
| Astronomicon routing gates | Blocks should go through Doctrinarium/Admin; Astronomicon recommends/routes/visualizes. | accepted_draft |
| Doctrinarium version diff | V1 timeline + Git history + law_change_receipt + simple field summary if practical; full visual diff later. | owner_resolved |
| Administratum priority enforcement | Desired eventually, but V1 mainly stores/recommends and enforces dependency/order violations, not arbitrary scheduling. | accepted_draft |
| Dashboard animation richness | Owner wants maximum beauty/animation if feasible; still preserve 60 FPS, truth, and architecture. | accepted_draft |

---

## 8. General Task / Local Tasks / Stages interpretation

Owner interpretation accepted:

This matrix is the current **General Task plan** for first-four-organs V1 hardening. It is not yet the final stage prompt package.

Layering:

1. **General Task**  
   Build first-four foundational organs V1 readiness:
   - complete task corridor;
   - dashboards;
   - Sanctum integration;
   - no-fake-green evidence;
   - beautiful truthful operator surfaces.

2. **Local Tasks**  
   Likely local task groups:
   - cross-organ standards;
   - Astronomicon V1 hardening;
   - Administratum V1 hardening;
   - Officio Agentis V1 hardening;
   - Doctrinarium V1 hardening;
   - Dashboard Truth + Beauty layer;
   - Sanctum aggregation layer;
   - E2E task corridor proof;
   - V1 certification and continuity pack.

3. **Stages**  
   Stages are not final yet. They must be produced after:
   - Kiro practical recommendations;
   - Logos-Speculum red-team;
   - Owner matrix review;
   - reconciliation of matrix + Kiro + Speculum.

---

## 9. Next advisory/review pipeline

Owner-approved plan:

```text
1. Commit this approved matrix.
2. Ask Kiro to read Git/plan and provide practical recommendations, internet/practice-informed suggestions, easier/lighter implementation options.
3. Keep Kiro answer bounded; useful but not enormous.
4. Ask Logos-Speculum for hard red-team of the matrix/plan.
5. Ingest and commit Kiro recommendations and Speculum red-team.
6. Reconcile:
   Owner matrix + Kiro recommendations + Speculum critique.
7. Produce final hardening General Task.
8. Decompose into Local Tasks.
9. Decompose Local Tasks into stages.
10. Write prompts for each stage.
11. Execute as a complex multi-stage task.
```

Kiro prompt should ask for:
- practical architecture recommendations;
- known patterns and common practice;
- ways to simplify implementation;
- risks;
- suggested stage grouping;
- what to defer;
- how to keep dashboards truthful and performant;
- how to design Sanctum data density.

Speculum prompt should ask for:
- ownership collision attacks;
- fake green attacks;
- dashboard mock-data risks;
- state lifecycle contradictions;
- evidence/receipt insufficiency;
- overreach by any organ;
- stage plan weaknesses;
- missing STOP gates.

---

## 10. Owner visual/dashboard doctrine summary

Owner wants:

- dashboards of unique beauty and theme;
- Warhammer/Imperial spirit;
- sci-fi;
- Jarvis style;
- cosmic animations;
- smooth architecture;
- 60 FPS target where feasible;
- every backend mechanism drawn correctly and elegantly;
- every script visible and working;
- every button working or explicitly disabled;
- no dashboard truth without evidence;
- no fake green;
- Sanctum as the Infinity Gauntlet aggregating all organ powers.

---

## 11. Current acceptance verdict

Owner-readable matrix status: **accepted for commit as v0.1**.

Remaining work:
- commit this matrix;
- request Kiro recommendations;
- request Speculum red-team;
- ingest both;
- reconcile;
- generate stage prompts and execute hardening task.
