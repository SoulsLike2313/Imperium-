# OWNER PAIN POINTS — Индекс решений

## Метаданные
- advisory_id: `ADVISORY-20260514-KIRO-OWNER-PAIN-POINTS-SOLUTIONS`
- source: `OWNER-PAIN-POINTS-AND-ARCHITECTURE-REQUIREMENTS-20260514.md`
- status: `advisory_not_canon`
- created: `2026-05-14`
- total_pain_points: 40

## Назначение

Этот раздел содержит детальные решения для каждой из 40 болевых точек Owner.
Каждое решение включает:
1. **Проблема** — что болит
2. **Требование** — что должно быть
3. **Решение** — как это сделать
4. **Файлы** — что создать/изменить
5. **Проверка** — как убедиться что работает
6. **Связь с задачами** — какие TASK_0N решают

## Группировка по категориям

### A. Continuity & Memory (Pain Points 1-2)
Проблемы с передачей контекста между сессиями.
- [PP01: Memory/Continuity Loss](./PP01_MEMORY_CONTINUITY_LOSS.md)
- [PP02: Continuity Pack Not Ideal](./PP02_CONTINUITY_PACK_NOT_IDEAL.md)

### B. Command & Launcher (Pain Points 3-4)
Проблемы с PowerShell и ручными командами.
- [PP03: PowerShell Fragility](./PP03_POWERSHELL_FRAGILITY.md)
- [PP04: Too Many Manual Commands](./PP04_TOO_MANY_MANUAL_COMMANDS.md)

### C. Evidence & Verification (Pain Points 5, 17, 30)
Проблемы с доказательствами и верификацией.
- [PP05: False/Partial Green](./PP05_FALSE_PARTIAL_GREEN.md)
- [PP17: Fake Green Risk](./PP17_FAKE_GREEN_RISK.md)
- [PP30: Git Truth Verification Manual](./PP30_GIT_TRUTH_VERIFICATION_MANUAL.md)

### D. Routes & Paths (Pain Points 6-9, 27)
Проблемы с маршрутами и путями.
- [PP06: Bundle Routes Confused](./PP06_BUNDLE_ROUTES_CONFUSED.md)
- [PP07: Paths Break After Moving](./PP07_PATHS_BREAK_AFTER_MOVING.md)
- [PP08: Git Repo Was Local Dump](./PP08_GIT_REPO_WAS_LOCAL_DUMP.md)
- [PP09: Local/Private Context Poorly Described](./PP09_LOCAL_PRIVATE_CONTEXT_POORLY_DESCRIBED.md)
- [PP27: No Single Source of Truth for Addresses](./PP27_NO_SINGLE_SOURCE_OF_TRUTH_FOR_ADDRESSES.md)

### E. Doctrine & Registration (Pain Points 10-12, 23-25)
Проблемы с регистрацией и доктриной.
- [PP10: Law/Doctrine Registration Weak](./PP10_LAW_DOCTRINE_REGISTRATION_WEAK.md)
- [PP11: Organs Can Become Ceremonial](./PP11_ORGANS_CAN_BECOME_CEREMONIAL.md)
- [PP12: Task Registration Not Reliable](./PP12_TASK_REGISTRATION_NOT_RELIABLE.md)
- [PP23: SCRIPTORIUM Not Strong Enough](./PP23_SCRIPTORIUM_NOT_STRONG_ENOUGH.md)
- [PP24: ARSENAL Not Strong Enough](./PP24_ARSENAL_NOT_STRONG_ENOUGH.md)
- [PP25: Script Errors No System Learning](./PP25_SCRIPT_ERRORS_NO_SYSTEM_LEARNING.md)

### F. Task & Stage Execution (Pain Points 13-15, 28-29)
Проблемы с выполнением задач.
- [PP13: Steps Often Too Small](./PP13_STEPS_OFTEN_TOO_SMALL.md)
- [PP14: Stage Continuation Weak](./PP14_STAGE_CONTINUATION_WEAK.md)
- [PP15: TASK/STAGE/RUN Not Railway](./PP15_TASK_STAGE_RUN_NOT_RAILWAY.md)
- [PP28: Advisory to Task Modernization Weak](./PP28_ADVISORY_TO_TASK_MODERNIZATION_WEAK.md)
- [PP29: Big Task Intake Not Mature](./PP29_BIG_TASK_INTAKE_NOT_MATURE.md)

### G. Warnings & Debt (Pain Points 16, 26)
Проблемы с warnings и техническим долгом.
- [PP16: Warning Noise High](./PP16_WARNING_NOISE_HIGH.md)
- [PP26: Temporary Files Lack TTL](./PP26_TEMPORARY_FILES_LACK_TTL.md)

### H. UI & Dashboard (Pain Points 18-22, 36)
Проблемы с UI и dashboard.
- [PP18: Visual/UI Work Poor Results](./PP18_VISUAL_UI_WORK_POOR_RESULTS.md)
- [PP19: Sanctum Grows Too Slowly](./PP19_SANCTUM_GROWS_TOO_SLOWLY.md)
- [PP20: Buttons Not Reliably Wired](./PP20_BUTTONS_NOT_RELIABLY_WIRED.md)
- [PP21: Dashboards May Be Decorative](./PP21_DASHBOARDS_MAY_BE_DECORATIVE.md)
- [PP22: Architecture Feels Incomplete](./PP22_ARCHITECTURE_FEELS_INCOMPLETE.md)
- [PP36: Backend Truth Before UI Beauty](./PP36_BACKEND_TRUTH_BEFORE_UI_BEAUTY.md)

### I. Delta & Reporting (Pain Points 31, 35)
Проблемы с отчётами и дельтами.
- [PP31: Hard to See What Changed](./PP31_HARD_TO_SEE_WHAT_CHANGED.md)
- [PP35: System Doesn't Explain Lack of Resources](./PP35_SYSTEM_DOESNT_EXPLAIN_LACK_OF_RESOURCES.md)

### J. Manual Intervention & Recovery (Pain Points 32, 40)
Проблемы с ручным вмешательством.
- [PP32: Owner Has to Rescue Too Much](./PP32_OWNER_HAS_TO_RESCUE_TOO_MUCH.md)
- [PP40: Owner Wants Stronger Adaptive Scripts](./PP40_OWNER_WANTS_STRONGER_ADAPTIVE_SCRIPTS.md)

### K. Boundaries & Status (Pain Points 33-34)
Проблемы с границами и статусами.
- [PP33: Canon/Advisory/Draft Boundaries Not Clear](./PP33_CANON_ADVISORY_DRAFT_BOUNDARIES_NOT_CLEAR.md)
- [PP34: Too Many Files Not Enough Navigation](./PP34_TOO_MANY_FILES_NOT_ENOUGH_NAVIGATION.md)

### L. Security & Authority (Pain Points 37-39)
Проблемы с безопасностью и авторитетом.
- [PP37: Private Payload Leak Risk](./PP37_PRIVATE_PAYLOAD_LEAK_RISK.md)
- [PP38: VM2 Must Not Become Second Authority](./PP38_VM2_MUST_NOT_BECOME_SECOND_AUTHORITY.md)
- [PP39: Route Health Not Visible](./PP39_ROUTE_HEALTH_NOT_VISIBLE.md)

## Матрица: Pain Point → TASK

| Pain Point | TASK_01 | TASK_02 | TASK_03 | TASK_04 | TASK_05 | TASK_06 | TASK_07 | TASK_08 |
|------------|---------|---------|---------|---------|---------|---------|---------|---------|
| PP01 | | | | | | | | ● |
| PP02 | | | | | | | | ● |
| PP03 | ● | | | | | | | |
| PP04 | ● | | | | | | | |
| PP05 | ● | | | | | | | ● |
| PP06 | ● | | | | | | | |
| PP07 | | ● | | | | | | |
| PP08 | | | | | | | | |
| PP09 | | | | | | | | |
| PP10 | | | | | | ● | | |
| PP11 | | | | | | ● | | |
| PP12 | | | | | | | | |
| PP13 | | | | | | | | |
| PP14 | | | | | | | | |
| PP15 | | | | | | | | |
| PP16 | | | | | | | ● | |
| PP17 | ● | | | | | | | ● |
| PP18 | | | | | | | | |
| PP19 | | | | | | | | ● |
| PP20 | | | | | | | | |
| PP21 | | | | | | | | ● |
| PP22 | | | | | | | | |
| PP23 | | | | ● | | | | |
| PP24 | | | | | ● | | | |
| PP25 | | | | ● | | | | |
| PP26 | | | | | | | ● | |
| PP27 | ● | ● | | | | | | |
| PP28 | | | | | | | | |
| PP29 | | | | | | | | |
| PP30 | ● | | | | | | | |
| PP31 | | | ● | | | | | ● |
| PP32 | ● | | | | | | | |
| PP33 | | | | | | | | |
| PP34 | | | ● | | | | | ● |
| PP35 | ● | | | | | | | |
| PP36 | | | | | | | | ● |
| PP37 | | | | | | | | |
| PP38 | ● | | | | | | | |
| PP39 | | | | | | | | ● |
| PP40 | ● | | | | | | | |

**Легенда:** ● = задача напрямую решает pain point

## Приоритеты решения

### Критические (решить в San-Cleaning)
- PP03, PP04 → TASK_01 (Launcher Spine)
- PP07 → TASK_02 (Address Rewrite)
- PP23 → TASK_04 (SCRIPTORIUM)
- PP24 → TASK_05 (ARSENAL)
- PP16 → TASK_07 (Warning Budget)
- PP05, PP17, PP21, PP36 → TASK_08 (Dashboard Data)

### Высокие (решить после San-Cleaning)
- PP01, PP02 — Continuity Pack v2
- PP10, PP11 — Doctrine Formalization
- PP12, PP15 — Task Railway
- PP30 — Git Truth Automation

### Средние (отдельные арки)
- PP18, PP19, PP20 — Sanctum Enhancement
- PP13, PP14, PP28, PP29 — Task Orchestration
- PP22 — Architecture Review

### Низкие (долгосрочные)
- PP33, PP34 — Navigation & Status
- PP37, PP38, PP39 — Security Hardening
