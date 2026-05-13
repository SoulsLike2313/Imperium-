# TASK 02: Address Rewrite Implementation v0.1

## Метаданные
- task_id: `TASK-20260514-SAN-CLEANING-ADDRESS-REWRITE-V0_1`
- priority: P0 — КРИТИЧЕСКИЙ
- platform: VM2 разработка, PC приёмка
- estimated_files: 20+ (обновление)
- dependencies: TASK_01 (нужны лаунчеры для тестирования)

## Цель
Обновить все 20 must_update_soon скриптов с устаревших путей на новые.

## Проблема
После миграции внешнего контекста:
- `E:\IMPERIUM_LOCAL` → `E:\IMPERIUM_CONTEXT\LOCAL`
- `E:\IMPERIUM_PRIVATE` → `E:\IMPERIUM_CONTEXT\PRIVATE`

20 скриптов всё ещё ссылаются на старые пути.

## Входные данные
- `CURRENT_STATE/ADDRESS_REPAIR_REPORT_20260514.md` — список скриптов
- `ORGANS/ADMINISTRATUM/REGISTRY/EXTERNAL_CONTEXT_PATHS_V0_1.md` — новые пути

## Алгоритм

### Шаг 1: Сканирование
```python
# Найти все файлы с устаревшими путями
patterns = [
    r'E:\\IMPERIUM_LOCAL',
    r'E:/IMPERIUM_LOCAL',
    r'IMPERIUM_LOCAL',
    r'E:\\IMPERIUM_PRIVATE',
    r'E:/IMPERIUM_PRIVATE',
    r'IMPERIUM_PRIVATE'
]

# Исключить:
# - .git/
# - .imperium_runtime/
# - ARTIFACTS/
# - KIRO_PLAN_ADVISOR/ (это advisory, не canon)
```

### Шаг 2: Классификация
Для каждого найденного файла определить:
1. Тип замены (простая строка vs конфигурация)
2. Контекст использования (путь к файлу vs переменная)
3. Платформа (Windows path vs Unix path vs both)

### Шаг 3: Генерация патчей
```python
replacements = {
    'E:\\IMPERIUM_LOCAL': 'E:\\IMPERIUM_CONTEXT\\LOCAL',
    'E:/IMPERIUM_LOCAL': 'E:/IMPERIUM_CONTEXT/LOCAL',
    'E:\\IMPERIUM_PRIVATE': 'E:\\IMPERIUM_CONTEXT\\PRIVATE',
    'E:/IMPERIUM_PRIVATE': 'E:/IMPERIUM_CONTEXT/PRIVATE',
}
```

### Шаг 4: Применение с dry-run
```bash
python3 address_rewrite_v0_1.py --scan --dry-run --verbose
python3 address_rewrite_v0_1.py --apply --dry-run --verbose
python3 address_rewrite_v0_1.py --apply --verbose  # реальное применение
```

### Шаг 5: Верификация
```bash
# Проверить что старых путей больше нет
grep -r "IMPERIUM_LOCAL" --include="*.py" --include="*.ps1" --include="*.json" .
grep -r "IMPERIUM_PRIVATE" --include="*.py" --include="*.ps1" --include="*.json" .

# Проверить компиляцию
python3 -m py_compile <каждый изменённый .py файл>
```

## Файлы для создания

### 1. Address Rewrite Script
**Путь:** `TOOLS/address_rewrite_v0_1.py`

```python
#!/usr/bin/env python3
"""
Address Rewrite Tool v0.1

Обновление устаревших путей в скриптах.

Usage:
    python3 address_rewrite_v0_1.py --scan [--dry-run] [--verbose]
    python3 address_rewrite_v0_1.py --apply [--dry-run] [--verbose]
"""

import argparse
import re
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Tuple

REPLACEMENTS = {
    'E:\\\\IMPERIUM_LOCAL': 'E:\\\\IMPERIUM_CONTEXT\\\\LOCAL',
    'E:/IMPERIUM_LOCAL': 'E:/IMPERIUM_CONTEXT/LOCAL',
    'E:\\\\IMPERIUM_PRIVATE': 'E:\\\\IMPERIUM_CONTEXT\\\\PRIVATE',
    'E:/IMPERIUM_PRIVATE': 'E:/IMPERIUM_CONTEXT/PRIVATE',
}

EXCLUDE_DIRS = {'.git', '.imperium_runtime', 'ARTIFACTS', 'KIRO_PLAN_ADVISOR', '__pycache__'}
INCLUDE_EXTENSIONS = {'.py', '.ps1', '.sh', '.json', '.md', '.txt'}

def scan_file(file_path: Path) -> List[Tuple[int, str, str]]:
    """Сканировать файл на устаревшие пути. Возвращает (line_num, old, new)."""
    findings = []
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            for old, new in REPLACEMENTS.items():
                if old.replace('\\\\', '\\') in line or old in line:
                    findings.append((i, old, new))
    except Exception as e:
        pass  # Skip unreadable files
    return findings

def apply_replacements(file_path: Path, dry_run: bool = True) -> Dict:
    """Применить замены к файлу."""
    result = {'file': str(file_path), 'changes': [], 'status': 'unchanged'}
    
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        
        for old, new in REPLACEMENTS.items():
            # Обработать оба варианта экранирования
            content = content.replace(old.replace('\\\\', '\\'), new.replace('\\\\', '\\'))
            content = content.replace(old, new)
        
        if content != original:
            result['status'] = 'changed'
            if not dry_run:
                file_path.write_text(content, encoding='utf-8')
                result['status'] = 'applied'
    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)
    
    return result

def main():
    parser = argparse.ArgumentParser(description='Address Rewrite Tool')
    parser.add_argument('--scan', action='store_true', help='Scan for stale paths')
    parser.add_argument('--apply', action='store_true', help='Apply replacements')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--repo-root', type=Path, default=Path('.'))
    args = parser.parse_args()
    
    # ... implementation
    
if __name__ == '__main__':
    main()
```

## Проверки

### Обязательные проверки
```bash
# 1. Компиляция скрипта
python3 -m py_compile TOOLS/address_rewrite_v0_1.py

# 2. Scan dry-run
python3 TOOLS/address_rewrite_v0_1.py --scan --dry-run --verbose

# 3. Apply dry-run
python3 TOOLS/address_rewrite_v0_1.py --apply --dry-run --verbose

# 4. Проверка что старых путей нет
grep -r "IMPERIUM_LOCAL" --include="*.py" . | grep -v KIRO_PLAN_ADVISOR | grep -v .git
```

## Критерии успеха
- [ ] Скрипт создан и компилируется
- [ ] Scan находит все 20 файлов
- [ ] Apply в dry-run показывает корректные замены
- [ ] После apply grep не находит старых путей
- [ ] Все изменённые .py файлы компилируются
- [ ] Receipt создан

## Критерии блокировки
- Скрипт не компилируется
- Замена ломает синтаксис файлов
- Остаются файлы со старыми путями

## Ожидаемый Servitor prompt outline

```
TASK: TASK-20260514-SAN-CLEANING-ADDRESS-REWRITE-V0_1
GOAL: Update 20 must_update_soon scripts with new paths

STEPS:
1. Read KIRO_PLAN_ADVISOR/SAN_CLEAN_PLAN/TASKS/TASK_02_ADDRESS_REWRITE/
2. Read CURRENT_STATE/ADDRESS_REPAIR_REPORT_20260514.md
3. Create TOOLS/address_rewrite_v0_1.py
4. Run py_compile
5. Run --scan --dry-run --verbose
6. Verify scan finds expected files
7. Run --apply --dry-run --verbose
8. Review changes
9. Run --apply --verbose (real apply)
10. Run grep to verify no stale paths remain
11. Run py_compile on all changed .py files
12. Build bundle for PC review

CONSTRAINTS:
- Do NOT commit from VM2
- All scripts must compile after changes
- Preserve file encoding (UTF-8)
```
