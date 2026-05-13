# Q02: Address Rewrite Implementation

## ВОПРОС
Какие старые пути/bindings вероятно сломаны после миграции внешнего контекста и как их исправить?

## РЕШЕНИЕ

### Устаревшие пути для замены

| Старый путь | Новый путь | Риск |
|-------------|------------|------|
| `E:\IMPERIUM\INBOX` | `E:\IMPERIUM_CONTEXT\LOCAL\VM2_BUNDLES` | MEDIUM |
| `E:\IMPERIUM_LOCAL` | `E:\IMPERIUM_CONTEXT\LOCAL` | HIGH |
| `E:\IMPERIUM_PRIVATE` | `E:\IMPERIUM_CONTEXT\PRIVATE` | HIGH |
| `INBOX/VM2_BUNDLES` (внутри репо) | `E:\IMPERIUM_CONTEXT\LOCAL\VM2_BUNDLES` | MEDIUM |
| `BUNDLE_REVIEWS` (внутри репо) | `E:\IMPERIUM_CONTEXT\LOCAL\BUNDLE_REVIEWS` | MEDIUM |

### Файлы для обновления (must_update_soon = 20)

```
ORGANS/ADMINISTRATUM/SCRIPTS/administratum_build_resume_continuity_pack_v0_2.py
ORGANS/ADMINISTRATUM/SCRIPTS/administratum_qa_developer_handoff_pack.py
ORGANS/ADMINISTRATUM/SCRIPTS/administratum_build_continuity_pack.py
ORGANS/ADMINISTRATUM/SCRIPTS/administratum_build_developer_grade_continuity_pack.py
ORGANS/ADMINISTRATUM/SCRIPTS/administratum_scan_real_imperium_state.py
ORGANS/ADMINISTRATUM/UTILITY/run_administratum_context_bundle_workflow.ps1
TOOLS/review_worker_bundle_intake.ps1
TOOLS/build_chat_compilation_from_analysis.ps1
... (ещё 12 файлов)
```

### Путь решения — Шаги

#### Шаг 1: Создать чекер для поиска устаревших путей
Файл: `TOOLS/check_address_rewrite_v0_1.py`

```python
LEGACY_PATTERNS = [
    r"E:\\IMPERIUM\\INBOX",
    r"E:\\IMPERIUM_LOCAL",
    r"E:\\IMPERIUM_PRIVATE",
    r"E:/IMPERIUM/INBOX",
    r"E:/IMPERIUM_LOCAL", 
    r"E:/IMPERIUM_PRIVATE",
]
```

#### Шаг 2: Для каждого файла из must_update_soon
1. Прочитать файл
2. Найти все вхождения legacy patterns
3. Заменить на новые пути
4. Проверить компиляцию: `python3 -m py_compile`
5. Записать в отчёт

#### Шаг 3: Создать отчёт о замене
Файл: `CURRENT_STATE/ADDRESS_REWRITE_IMPLEMENTATION_REPORT_20260514.md`

#### Шаг 4: Запустить чекер для проверки
```bash
python3 TOOLS/check_address_rewrite_v0_1.py --repo-root . --human
```

### Алгоритм замены

```python
def rewrite_addresses(file_path: Path) -> dict:
    """Заменить устаревшие пути на новые."""
    replacements = {
        r"E:\\IMPERIUM\\INBOX": r"E:\\IMPERIUM_CONTEXT\\LOCAL\\VM2_BUNDLES",
        r"E:\\IMPERIUM_LOCAL": r"E:\\IMPERIUM_CONTEXT\\LOCAL",
        r"E:\\IMPERIUM_PRIVATE": r"E:\\IMPERIUM_CONTEXT\\PRIVATE",
        r"E:/IMPERIUM/INBOX": r"E:/IMPERIUM_CONTEXT/LOCAL/VM2_BUNDLES",
        r"E:/IMPERIUM_LOCAL": r"E:/IMPERIUM_CONTEXT/LOCAL",
        r"E:/IMPERIUM_PRIVATE": r"E:/IMPERIUM_CONTEXT/PRIVATE",
    }
    
    content = file_path.read_text(encoding='utf-8')
    original = content
    
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    if content != original:
        file_path.write_text(content, encoding='utf-8')
        return {"modified": True, "path": str(file_path)}
    
    return {"modified": False, "path": str(file_path)}
```

### Критерии успеха
- [ ] Все 20 файлов обновлены
- [ ] Чекер `check_address_rewrite_v0_1.py` проходит с 0 violations
- [ ] Все обновлённые скрипты компилируются
- [ ] Отчёт создан

### Критерии блокировки
- Любой скрипт не компилируется после замены
- Legacy path всё ещё найден в must_update_soon файлах

## ПРИМЕР СТРУКТУРЫ

См. `TASKS/TASK_02_ADDRESS_REWRITE/`
