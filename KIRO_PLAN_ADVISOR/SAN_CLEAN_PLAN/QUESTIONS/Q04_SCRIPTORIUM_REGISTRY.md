# Q04: SCRIPTORIUM Registry Design

## ВОПРОС
Какой должен быть минимально жизнеспособный дизайн SCRIPTORIUM registry под MECHANICUS?

## РЕШЕНИЕ

### Назначение SCRIPTORIUM
SCRIPTORIUM — это **реестр скриптов и слой истины о скриптах**, не отдельный орган, а поддерживающий слой под MECHANICUS.

### Обязательные поля записи

| Поле | Тип | Описание |
|------|-----|----------|
| `script_id` | string | Уникальный ID: `SCRIPT-[NAME]-V[X]_[Y]` |
| `path` | string | Относительный путь от корня репо |
| `name` | string | Имя файла |
| `owner_organ` | enum | Орган-владелец |
| `purpose` | string | Что делает скрипт (мин. 10 символов) |
| `platform` | enum | `CROSS_PLATFORM`, `WINDOWS_ONLY`, `UBUNTU_ONLY` |
| `runtime` | enum | `PYTHON3`, `POWERSHELL`, `BASH` |
| `side_effects` | array | Побочные эффекты |
| `status` | enum | Статус скрипта |

### Опциональные поля записи

| Поле | Тип | Описание |
|------|-----|----------|
| `entrypoint_command` | string | Команда запуска |
| `required_args` | array | Обязательные аргументы |
| `optional_args` | array | Опциональные аргументы |
| `reads` | array | Что читает |
| `writes` | array | Куда пишет |
| `produces_receipts` | boolean | Создаёт ли receipts |
| `receipt_paths` | array | Пути к receipts |
| `modifies_repo` | boolean | Модифицирует ли репо |
| `requires_owner_approval` | boolean | Требует ли одобрения |
| `safe_for_servitor` | boolean | Безопасен ли для Servitor |
| `dangerous_if_misused` | boolean | Опасен ли |
| `known_dependencies` | array | Зависимости |
| `known_failures` | array | Известные сбои |
| `reliability_status` | enum | Надёжность |
| `growth_history` | array | История изменений |
| `dashboard_visibility` | object | Настройки dashboard |

### Путь решения — Шаги

#### Шаг 1: Определить скрипты для первой волны
Приоритет 1 — Активные чекеры:
```
TOOLS/check_script_registry_v0_1.py
TOOLS/check_repo_parity_external_context_v0_2.py
TOOLS/check_external_context_registry_v0_1.py
TOOLS/check_warning_budget_v0_1.py
scripts/verify_repo.py
```

Приоритет 2 — Активные билдеры:
```
TOOLS/build_sanctum_state_v0_1.py
TOOLS/administratum_git_cli_check_v0_1.py
```

Приоритет 3 — Лаунчеры (после создания):
```
TOOLS/imperium_launcher_v0_1.py
TOOLS/launcher_fetch_bundle_v0_1.py
...
```

#### Шаг 2: Создать схему записи
Файл: `schemas/scriptorium_entry_v0_1.schema.json`

#### Шаг 3: Создать скрипт для обнаружения незарегистрированных
Файл: `TOOLS/find_unregistered_scripts_v0_1.py`

```python
def find_unregistered_scripts(repo_root: Path, registry: dict) -> list:
    registered_paths = {e["path"] for e in registry.get("scripts", [])}
    
    script_zones = [
        repo_root / "TOOLS",
        repo_root / "scripts",
    ]
    
    # Добавить органные скрипты
    for organ in (repo_root / "ORGANS").iterdir():
        if organ.is_dir():
            for subdir in ["SCRIPTS", "UTILITY"]:
                zone = organ / subdir
                if zone.exists():
                    script_zones.append(zone)
    
    unregistered = []
    for zone in script_zones:
        for script in zone.rglob("*"):
            if script.suffix in [".py", ".ps1", ".sh"]:
                rel_path = str(script.relative_to(repo_root)).replace("\\", "/")
                if rel_path not in registered_paths:
                    unregistered.append(rel_path)
    
    return unregistered
```

#### Шаг 4: Для каждого незарегистрированного скрипта
1. Прочитать файл
2. Определить owner_organ по пути
3. Определить platform по расширению
4. Определить runtime по расширению
5. Извлечь purpose из docstring
6. Определить side_effects по содержимому
7. Создать запись

#### Шаг 5: Обновить REGISTRY/SCRIPT_REGISTRY.json

#### Шаг 6: Создать чекер покрытия
Файл: `TOOLS/check_scriptorium_coverage_v0_1.py`

### Алгоритм определения side_effects

```python
def detect_side_effects(content: str) -> list:
    effects = []
    
    # Проверить на модификацию репо
    if any(x in content for x in ["git add", "git commit", "git push"]):
        effects.append("MODIFIES_REPO")
    
    # Проверить на сетевой доступ
    if any(x in content for x in ["ssh", "scp", "requests.", "urllib"]):
        effects.append("NETWORK_ACCESS")
    
    # Проверить на запись в runtime
    if ".imperium_runtime" in content:
        effects.append("WRITES_RUNTIME_ONLY")
    
    # Если ничего не найдено
    if not effects:
        effects.append("SAFE_READONLY")
    
    return effects
```

### Критерии успеха
- [ ] ≥90% покрытие для TOOLS/ и scripts/
- [ ] Все записи имеют обязательные поля
- [ ] Чекер `check_scriptorium_coverage_v0_1.py` проходит
- [ ] Схема валидна

### Критерии блокировки
- Coverage <70%
- Отсутствуют обязательные поля

## ПРИМЕР СТРУКТУРЫ

См. `SCHEMAS/scriptorium_entry_v0_1.schema.json` и `EXAMPLES/scriptorium_entry_example.json`
