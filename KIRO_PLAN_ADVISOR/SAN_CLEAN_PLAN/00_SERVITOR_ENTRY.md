# SERVITOR ENTRY — SAN_CLEAN_PLAN

## Метаданные
- advisory_id: `ADVISORY-20260514-KIRO-SAN-CLEANING-BACKEND-TRUTH-PLAN-REFRESH-V0_1`
- task_context: `TASK-20260514-KIRO-SAN-CLEANING-BACKEND-TRUTH-PLAN-REFRESH-AFTER-REPO-PARITY-AND-EXTERNAL-CONTEXT-V0_1`
- required_head: `9307c4883926edd3f843fd1224fdee244b47b1a0`
- status: `advisory_not_canon`
- created: `2026-05-14`
- source_pain_points: `OWNER-PAIN-POINTS-AND-ARCHITECTURE-REQUIREMENTS-20260514.md` (40 pain points)

## Инструкция для Servitor

### Порядок чтения
1. Прочитай этот файл полностью.
2. Прочитай `01_CURRENT_STATE_ASSESSMENT.md` — понять что уже сделано.
3. Прочитай `02_TASK_SEQUENCE.md` — понять последовательность задач.
4. Для каждой задачи читай соответствующую папку в `TASKS/`.
5. Перед выполнением задачи читай `QUESTIONS/` для понимания проблемы и решения.

### Жёсткие правила
1. **НЕ КОММИТИТЬ с VM2** — только PC делает commit/push.
2. **НЕ УДАЛЯТЬ файлы** без явного одобрения Owner.
3. **НЕ МОДИФИЦИРОВАТЬ Sanctum runtime** — `sanctum_v0_29_qt.py` не трогать.
4. **READY_FOR_AGENT остаётся false**.
5. **Каждый скрипт должен компилироваться** — `python3 -m py_compile <file>`.
6. **Каждый скрипт должен иметь receipt** — записывать результат выполнения.
7. **Dry-run сначала** — все опасные операции сначала в dry-run режиме.

### Структура папки
```
KIRO_PLAN_ADVISOR/SAN_CLEAN_PLAN/
├── 00_SERVITOR_ENTRY.md              # ← ТЫ ЗДЕСЬ
├── 01_CURRENT_STATE_ASSESSMENT.md    # Текущее состояние
├── 02_TASK_SEQUENCE.md               # Последовательность задач
├── INDEX.md                          # Полный индекс
├── ANTI_PATTERNS.md                  # Запрещённые действия
├── ASTRONOMICON_DECOMPOSITION_TEMPLATE.md  # Шаблон декомпозиции
├── OWNER_PAIN_POINTS/                # Решения для 40 Owner Pain Points
│   ├── 00_PAIN_POINTS_INDEX.md       # Индекс и матрица PP → TASK
│   ├── PP01_MEMORY_CONTINUITY_LOSS.md
│   ├── PP03_POWERSHELL_FRAGILITY.md
│   ├── PP05_FALSE_PARTIAL_GREEN.md
│   ├── PP11_ORGANS_CAN_BECOME_CEREMONIAL.md
│   ├── PP15_TASK_STAGE_RUN_NOT_RAILWAY.md
│   ├── PP16_WARNING_NOISE_HIGH.md
│   ├── PP23_SCRIPTORIUM_NOT_STRONG_ENOUGH.md
│   ├── PP36_BACKEND_TRUTH_BEFORE_UI_BEAUTY.md
│   └── ... (остальные PP файлы по мере создания)
├── QUESTIONS/                        # Вопросы и решения
│   ├── Q01_LAUNCHER_SPINE.md
│   ├── Q02_ADDRESS_REWRITE.md
│   ├── Q03_CURRENT_TRUTH_INVENTORY.md
│   ├── Q04_SCRIPTORIUM_REGISTRY.md
│   ├── Q05_ARSENAL_REGISTRY.md
│   ├── Q06_WARNING_BUDGET.md
│   ├── Q07_DASHBOARD_DATA.md
│   └── Q08_BROKEN_PATHS.md
├── TASKS/                            # Детальные задачи
│   ├── TASK_01_LAUNCHER_SPINE/
│   ├── TASK_02_ADDRESS_REWRITE/
│   ├── TASK_03_CURRENT_TRUTH_INVENTORY/
│   ├── TASK_04_SCRIPTORIUM/
│   ├── TASK_05_ARSENAL/
│   ├── TASK_06_MECHANICUS/
│   ├── TASK_07_WARNING_BUDGET/
│   └── TASK_08_DASHBOARD_DATA/
├── SCHEMAS/                          # JSON схемы
│   ├── launcher_receipt_v0_1.schema.json
│   ├── scriptorium_entry_v0_1.schema.json
│   ├── arsenal_entry_v0_1.schema.json
│   └── warning_budget_v0_1.schema.json
├── EXAMPLES/                         # Примеры кода и конфигов
│   ├── launcher_config_example.json
│   ├── scriptorium_entry_example.json
│   ├── arsenal_entry_example.json
│   └── receipt_example.json
└── ANTI_PATTERNS.md                  # Запрещённые действия
```

### Контекст маршрутов
- PC repo root: `E:\IMPERIUM`
- VM2 repo root: `/home/vboxuser2/IMPERIUM_WORK/Imperium-`
- External local root: `E:\IMPERIUM_CONTEXT\LOCAL`
- External private root: `E:\IMPERIUM_CONTEXT\PRIVATE`
- PC → VM2 SSH: `vboxuser2@127.0.0.1:2223` key: `$env:USERPROFILE\.ssh\imperium_pc_to_vm2_ed25519_20260418`
- VM2 → PC SSH: `pc@10.0.2.2` key: `/home/vboxuser2/.ssh/imperium_vm2_to_pc_ed25519_20260418`

### Цель арки San-Cleaning
Создать надёжный backend truth layer:
1. Python-first лаунчеры вместо ad hoc PowerShell команд.
2. Полная регистрация скриптов в SCRIPTORIUM.
3. Полная регистрация инструментов в ARSENAL.
4. Warning budget с классификацией legacy vs new.
5. Dashboard data model для отображения правды.
6. Исправление устаревших путей после миграции внешнего контекста.
