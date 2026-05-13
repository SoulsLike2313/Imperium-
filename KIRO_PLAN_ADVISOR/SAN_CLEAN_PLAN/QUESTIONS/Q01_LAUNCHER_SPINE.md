# Q01: Python-First Launcher Spine

## ВОПРОС
Как IMPERIUM должен спроектировать Python-first launcher layer, который может:
- Забирать VM2 bundles
- Проверять sha256
- Распаковывать для review
- Запускать scope gates
- Применять разрешённые файлы
- Коммитить/пушить только с PC
- Exact-sync VM2
- Производить receipts/evidence
- Избегать fake green
- Безопасно работать с Windows + Linux маршрутами

## РЕШЕНИЕ

### Архитектура
```
TOOLS/
├── imperium_launcher_v0_1.py          # Core framework — базовый класс
├── launcher_fetch_bundle_v0_1.py      # Fetch VM2 bundle → PC
├── launcher_apply_bundle_v0_1.py      # Apply reviewed bundle → repo
├── launcher_commit_push_v0_1.py       # Commit and push (PC only)
├── launcher_sync_vm2_v0_1.py          # Exact-sync VM2 to PC HEAD
└── launcher_config_v0_1.py            # Route/path configuration loader

CONFIG/
└── launcher_routes_v0_1.json          # Route configuration

schemas/
└── launcher_receipt_v0_1.schema.json  # Receipt schema

REGISTRY/
└── LAUNCHER_REGISTRY.json             # Registered launchers
```

### Принципы дизайна
1. **Каждый лаунчер наследует BaseLauncher** — единый интерфейс.
2. **Каждый лаунчер производит receipt** — JSON файл с результатом.
3. **Dry-run режим обязателен** — `--dry-run` флаг для preview.
4. **Конфигурация из файла** — не hardcoded пути.
5. **Cross-platform** — работает на Windows и Linux.
6. **Verbose режим** — `--verbose` для отладки.

### Путь решения — Шаги

#### Шаг 1: Создать базовый framework
Файл: `TOOLS/imperium_launcher_v0_1.py`
- Класс `LauncherConfig` — загрузка конфигурации
- Класс `LauncherReceipt` — генерация receipts
- Класс `BaseLauncher` — базовый класс для всех лаунчеров

#### Шаг 2: Создать конфигурацию маршрутов
Файл: `CONFIG/launcher_routes_v0_1.json`
- PC repo root
- VM2 repo root
- External context roots
- SSH credentials (без паролей!)

#### Шаг 3: Создать fetch bundle лаунчер
Файл: `TOOLS/launcher_fetch_bundle_v0_1.py`
- Проверка SSH route
- Список bundles на VM2
- SCP fetch
- SHA256 verification

#### Шаг 4: Создать apply bundle лаунчер
Файл: `TOOLS/launcher_apply_bundle_v0_1.py`
- Распаковка bundle
- Scope gate check
- Apply allowed files
- Generate receipt

#### Шаг 5: Создать commit/push лаунчер
Файл: `TOOLS/launcher_commit_push_v0_1.py`
- Git status check
- Git add
- Git commit
- Git push
- **ТОЛЬКО НА PC!**

#### Шаг 6: Создать VM2 sync лаунчер
Файл: `TOOLS/launcher_sync_vm2_v0_1.py`
- SSH to VM2
- Git fetch
- Git reset --hard
- Verify HEAD match

#### Шаг 7: Создать схему receipt
Файл: `schemas/launcher_receipt_v0_1.schema.json`

#### Шаг 8: Зарегистрировать лаунчеры
Файл: `REGISTRY/LAUNCHER_REGISTRY.json`

### Критерии успеха
- [ ] 5 лаунчеров созданы
- [ ] Все компилируются: `python3 -m py_compile`
- [ ] Все имеют `--dry-run` режим
- [ ] Все производят receipts
- [ ] Чекер `check_launcher_registry_v0_1.py` проходит

### Критерии блокировки
- Любой лаунчер не компилируется
- Receipt schema невалидна
- SSH route не работает

## ПРИМЕР СТРУКТУРЫ

См. `EXAMPLES/launcher_config_example.json` и `TASKS/TASK_01_LAUNCHER_SPINE/`
