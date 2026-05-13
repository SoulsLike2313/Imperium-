# SAN_CLEAN_PLAN — Полный индекс

## Метаданные
- advisory_id: `ADVISORY-20260514-KIRO-SAN-CLEANING-BACKEND-TRUTH-PLAN-REFRESH-V0_1`
- status: `advisory_not_canon`
- created: `2026-05-14`
- total_files: 50+
- source_pain_points: 40 (OWNER-PAIN-POINTS-AND-ARCHITECTURE-REQUIREMENTS-20260514.md)

## Структура

```
KIRO_PLAN_ADVISOR/SAN_CLEAN_PLAN/
│
├── 00_SERVITOR_ENTRY.md              # Точка входа для Servitor
├── 01_CURRENT_STATE_ASSESSMENT.md    # Оценка текущего состояния
├── 02_TASK_SEQUENCE.md               # Последовательность 8 задач
├── ANTI_PATTERNS.md                  # Запрещённые действия
├── INDEX.md                          # ← ТЫ ЗДЕСЬ
├── ASTRONOMICON_DECOMPOSITION_TEMPLATE.md  # Шаблон для ASTRONOMICON
│
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
│   └── ... (остальные PP файлы)
│
├── QUESTIONS/                        # Вопросы и решения (8 файлов)
│   ├── Q01_LAUNCHER_SPINE.md
│   ├── Q02_ADDRESS_REWRITE.md
│   ├── Q03_CURRENT_TRUTH_INVENTORY.md
│   ├── Q04_SCRIPTORIUM_REGISTRY.md
│   ├── Q05_ARSENAL_REGISTRY.md
│   ├── Q06_WARNING_BUDGET.md
│   ├── Q07_DASHBOARD_DATA.md
│   └── Q08_BROKEN_PATHS.md
│
├── TASKS/                            # Детальные спецификации задач
│   ├── TASK_01_LAUNCHER_SPINE/
│   │   ├── TASK_SPEC.md
│   │   └── CODE_TEMPLATES/       # 7 файлов
│   │       ├── imperium_launcher_v0_1.py
│   │       ├── launcher_fetch_bundle_v0_1.py
│   │       ├── launcher_apply_bundle_v0_1.py
│   │       ├── launcher_commit_push_v0_1.py
│   │       ├── launcher_sync_vm2_v0_1.py
│   │       ├── launcher_routes_v0_1.json
│   │       └── launcher_registry.json
│   ├── TASK_02_ADDRESS_REWRITE/
│   │   └── TASK_SPEC.md
│   ├── TASK_03_CURRENT_TRUTH_INVENTORY/
│   │   └── TASK_SPEC.md
│   ├── TASK_04_SCRIPTORIUM/
│   │   └── TASK_SPEC.md
│   ├── TASK_05_ARSENAL/
│   │   └── TASK_SPEC.md
│   ├── TASK_06_MECHANICUS/
│   │   └── TASK_SPEC.md
│   ├── TASK_07_WARNING_BUDGET/
│   │   └── TASK_SPEC.md
│   └── TASK_08_DASHBOARD_DATA/
│       └── TASK_SPEC.md
│
├── SCHEMAS/                      # JSON схемы (4 файла)
│   ├── launcher_receipt_v0_1.schema.json
│   ├── scriptorium_entry_v0_1.schema.json
│   ├── arsenal_entry_v0_1.schema.json
│   └── warning_budget_v0_1.schema.json
│
└── EXAMPLES/                     # Примеры (4 файла)
    ├── launcher_config_example.json
    ├── scriptorium_entry_example.json
    ├── arsenal_entry_example.json
    └── receipt_example.json
```

## Порядок чтения для Servitor

### Фаза 1: Понимание контекста
1. `00_SERVITOR_ENTRY.md` — правила и ограничения
2. `01_CURRENT_STATE_ASSESSMENT.md` — что сделано, что сломано
3. `02_TASK_SEQUENCE.md` — последовательность задач
4. `ANTI_PATTERNS.md` — что НЕ делать
5. `OWNER_PAIN_POINTS/00_PAIN_POINTS_INDEX.md` — индекс 40 болевых точек

### Фаза 1.5: Понимание болевых точек (опционально, для глубокого понимания)
Для каждой задачи прочитать связанные Pain Points:
- TASK_01 → PP03, PP05, PP06, PP27, PP30, PP32, PP35, PP38, PP40
- TASK_02 → PP07, PP27
- TASK_03 → PP31, PP34
- TASK_04 → PP23, PP25
- TASK_05 → PP24
- TASK_06 → PP10, PP11
- TASK_07 → PP16, PP26
- TASK_08 → PP01, PP02, PP05, PP17, PP19, PP21, PP34, PP36, PP39

### Фаза 2: Выполнение задач
Для каждой задачи (1-8):
1. Прочитать `QUESTIONS/Q0N_*.md` — понять проблему
2. Прочитать `TASKS/TASK_0N_*/TASK_SPEC.md` — понять решение
3. Если есть `CODE_TEMPLATES/` — использовать как основу
4. Выполнить задачу
5. Создать bundle для PC

### Фаза 3: Валидация
1. Проверить все py_compile
2. Проверить все JSON валидны
3. Проверить receipts созданы
4. Передать bundle на PC

## Статистика

| Категория | Количество |
|-----------|------------|
| Markdown файлы | 21 |
| Python шаблоны | 5 |
| JSON конфиги | 2 |
| JSON схемы | 4 |
| JSON примеры | 4 |
| **Всего** | **36** |

## Задачи и приоритеты

| # | Задача | Приоритет | Зависимости |
|---|--------|-----------|-------------|
| 1 | Launcher Spine | P0 | — |
| 2 | Address Rewrite | P0 | TASK_01 |
| 3 | Current Truth Inventory | P1 | TASK_02 |
| 4 | SCRIPTORIUM | P1 | TASK_03 |
| 5 | ARSENAL | P1 | TASK_03 |
| 6 | MECHANICUS | P1 | TASK_04, TASK_05 |
| 7 | Warning Budget | P2 | TASK_06 |
| 8 | Dashboard Data | P2 | TASK_07 |

## Критерии завершения арки

| Критерий | Порог | Текущее |
|----------|-------|---------|
| Script registration coverage | ≥ 90% | ? |
| Tool registration coverage | ≥ 80% | ? |
| Stale address count | 0 | 20 |
| Launcher coverage | 5 core | 0 |
| MECHANICUS contract | EXISTS | NO |
| Warning budget | DEFINED | NO |
| Dashboard data | GENERATED | NO |

## Контакты

- **Owner**: Logos-Prime (PC)
- **Executor**: Servitor (VM2)
- **Reviewer**: Owner (PC)

## Важные напоминания

1. **НЕ КОММИТИТЬ С VM2**
2. **НЕ ТРОГАТЬ SANCTUM**
3. **READY_FOR_AGENT = false**
4. **Все скрипты должны компилироваться**
5. **Все скрипты должны иметь --dry-run**
6. **Все скрипты должны создавать receipts**
