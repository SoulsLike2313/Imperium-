# Q05: ARSENAL Registry Design

## ВОПРОС
Какой должен быть минимально жизнеспособный дизайн ARSENAL registry под MECHANICUS?

## РЕШЕНИЕ

### Назначение ARSENAL
ARSENAL — это **реестр внешних инструментов и возможностей**, отслеживает что установлено, что доступно, что одобрено.

### Обязательные поля записи

| Поле | Тип | Описание |
|------|-----|----------|
| `tool_id` | string | Уникальный ID: `TOOL-[NAME]` |
| `name` | string | Название инструмента |
| `category` | enum | Категория |
| `platform` | enum | `CROSS_PLATFORM`, `WINDOWS_ONLY`, `UBUNTU_ONLY` |
| `tool_type` | enum | `runtime`, `cli`, `library`, `app`, `service` |
| `purpose_for_imperium` | string | Зачем нужен IMPERIUM |
| `verification_command` | string | Команда проверки |
| `install_status` | object | Статус установки на PC и VM2 |
| `owner_approval` | enum | `APPROVED`, `PENDING`, `REJECTED`, `NOT_REQUIRED` |
| `status` | enum | Статус инструмента |

### Опциональные поля записи

| Поле | Тип | Описание |
|------|-----|----------|
| `installation_method` | string | Как установить |
| `version_command` | string | Команда версии |
| `allowed_use_cases` | array | Разрешённые use cases |
| `forbidden_use_cases` | array | Запрещённые use cases |
| `scripts_depending_on_it` | array | Зависимые скрипты |
| `last_verification` | object | Последняя проверка |
| `risks` | object | Риски |
| `dashboard_visibility` | object | Настройки dashboard |

### Инструменты для первой волны

| tool_id | name | platform | PC | VM2 |
|---------|------|----------|-----|-----|
| `TOOL-GIT` | Git | CROSS_PLATFORM | ✅ | ✅ |
| `TOOL-OPENSSH` | OpenSSH | CROSS_PLATFORM | ✅ | ✅ |
| `TOOL-PYTHON3` | Python 3 | CROSS_PLATFORM | ✅ | ✅ |
| `TOOL-POWERSHELL` | PowerShell | WINDOWS_ONLY | ✅ | ❌ |
| `TOOL-BASH` | Bash | UBUNTU_ONLY | ❌ | ✅ |
| `TOOL-PYSIDE6` | PySide6 | CROSS_PLATFORM | ✅ | ? |
| `TOOL-ZIP` | zip/unzip | CROSS_PLATFORM | ✅ | ✅ |
| `TOOL-SHA256` | sha256sum/Get-FileHash | CROSS_PLATFORM | ✅ | ✅ |

### Путь решения — Шаги

#### Шаг 1: Создать схему записи
Файл: `schemas/arsenal_entry_v0_1.schema.json`

#### Шаг 2: Создать скрипт верификации
Файл: `TOOLS/verify_arsenal_install_v0_1.py`

```python
def verify_tool(tool: dict) -> dict:
    """Проверить установку инструмента."""
    cmd = tool["verification_command"]
    
    try:
        result = subprocess.run(
            cmd.split(),
            capture_output=True,
            text=True,
            timeout=10
        )
        return {
            "tool_id": tool["tool_id"],
            "installed": result.returncode == 0,
            "version": result.stdout.strip() if result.returncode == 0 else None,
            "error": result.stderr if result.returncode != 0 else None
        }
    except Exception as e:
        return {
            "tool_id": tool["tool_id"],
            "installed": False,
            "error": str(e)
        }
```

#### Шаг 3: Для каждого инструмента
1. Определить verification_command
2. Запустить на PC
3. Запустить на VM2 (через SSH)
4. Записать результат

#### Шаг 4: Создать ARSENAL registry
Файл: `ORGANS/MECHANICUS/ARSENAL/ARSENAL_REGISTRY_V0_1.json`

#### Шаг 5: Обновить существующие файлы
- `REGISTRY/ARSENAL_TOOL_INDEX.json`
- `REGISTRY/ARSENAL_INSTALL_STATUS.json`

#### Шаг 6: Создать чекер покрытия
Файл: `TOOLS/check_arsenal_coverage_v0_1.py`

### Алгоритм определения зависимых скриптов

```python
def find_dependent_scripts(tool_name: str, registry: dict) -> list:
    """Найти скрипты, зависящие от инструмента."""
    dependent = []
    
    for script in registry.get("scripts", []):
        deps = script.get("known_dependencies", [])
        if tool_name.lower() in [d.lower() for d in deps]:
            dependent.append(script["script_id"])
    
    return dependent
```

### Критерии успеха
- [ ] Core tools зарегистрированы (git, ssh, python3, powershell, bash)
- [ ] Install status проверен на PC и VM2
- [ ] Чекер `check_arsenal_coverage_v0_1.py` проходит
- [ ] Схема валидна

### Критерии блокировки
- Core tool отсутствует
- Verification command не работает

## ПРИМЕР СТРУКТУРЫ

См. `SCHEMAS/arsenal_entry_v0_1.schema.json` и `EXAMPLES/arsenal_entry_example.json`
