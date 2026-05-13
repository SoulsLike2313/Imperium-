# Q03: Current Truth Inventory Design

## ВОПРОС
Как спроектировать расширенную инвентаризацию после миграции внешнего контекста?

## РЕШЕНИЕ

### Что должна инвентаризировать
1. Git repo скрипты
2. Local/private context категории (через redacted indexes)
3. Route maps
4. External context
5. Warnings
6. Blockers
7. SCRIPTORIUM candidates
8. ARSENAL candidates
9. Stale paths
10. Generated/cache traces
11. Unknown/orphan zones

### Зоны сканирования

| Зона | Путь | Тип сканирования |
|------|------|------------------|
| Активные скрипты | `TOOLS/`, `scripts/` | Полное |
| Органные скрипты | `ORGANS/*/SCRIPTS/`, `ORGANS/*/UTILITY/` | Полное |
| Схемы | `schemas/` | Полное |
| Реестры | `REGISTRY/` | Полное |
| Текущее состояние | `CURRENT_STATE/` | Полное |
| External local | `E:\IMPERIUM_CONTEXT\LOCAL` | Только метаданные |
| External private | `E:\IMPERIUM_CONTEXT\PRIVATE` | Только счётчики |

### Путь решения — Шаги

#### Шаг 1: Создать inventory скрипт
Файл: `TOOLS/inventory_repo_truth_v0_1.py`

#### Шаг 2: Сканировать каждую зону
```python
def scan_zone(zone_path: Path) -> dict:
    files = []
    for f in zone_path.rglob("*"):
        if f.is_file():
            files.append({
                "path": str(f.relative_to(repo_root)),
                "name": f.name,
                "extension": f.suffix,
                "size_bytes": f.stat().st_size
            })
    return {
        "total_files": len(files),
        "files": files
    }
```

#### Шаг 3: Проверить регистрацию скриптов
```python
def check_registration(script_path: str, registry: dict) -> bool:
    registered_paths = {e["path"] for e in registry.get("scripts", [])}
    return script_path in registered_paths
```

#### Шаг 4: Найти orphan candidates
```python
def find_orphans(repo_root: Path) -> list:
    # Файлы которые не в известных зонах и не в registry
    pass
```

#### Шаг 5: Найти stale paths
```python
def find_stale_paths(repo_root: Path) -> list:
    # Файлы которые ссылаются на legacy roots
    pass
```

#### Шаг 6: Сгенерировать отчёты
- `CURRENT_STATE/CURRENT_TRUTH_INVENTORY_20260514.json`
- `CURRENT_STATE/CURRENT_TRUTH_INVENTORY_20260514.md`
- `CURRENT_STATE/ORPHAN_FILE_CANDIDATES_20260514.json`

### Алгоритм классификации файлов

```python
def classify_file(file_path: Path, registry: dict) -> str:
    """Классифицировать файл."""
    rel_path = str(file_path.relative_to(repo_root))
    
    # Проверить регистрацию
    if is_registered(rel_path, registry):
        return "ACTIVE_REGISTERED_SCRIPT"
    
    # Проверить зону
    if rel_path.startswith("TOOLS/") or rel_path.startswith("scripts/"):
        return "SCRIPT_CANDIDATE"
    
    if rel_path.startswith("CURRENT_STATE/"):
        return "CURRENT_STATE"
    
    if rel_path.startswith("ARTIFACTS/"):
        return "LEGACY_OBSOLETE"
    
    if rel_path.startswith(".imperium_runtime/"):
        return "GENERATED_REPORT"
    
    return "UNKNOWN_ORPHAN"
```

### Критерии успеха
- [ ] Inventory скрипт создан и компилируется
- [ ] Все зоны просканированы
- [ ] JSON и MD отчёты созданы
- [ ] Orphan candidates идентифицированы
- [ ] Stale paths идентифицированы
- [ ] SCRIPTORIUM candidates идентифицированы
- [ ] ARSENAL candidates идентифицированы

### Критерии блокировки
- Inventory скрипт не компилируется
- Пропущены зоны сканирования

## ПРИМЕР СТРУКТУРЫ

См. `SCHEMAS/current_truth_inventory_v0_1.schema.json` и `TASKS/TASK_03_CURRENT_TRUTH_INVENTORY/`
