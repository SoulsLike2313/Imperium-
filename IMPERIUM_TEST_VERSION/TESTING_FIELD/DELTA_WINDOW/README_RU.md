# TESTING FIELD DELTA WINDOW MVP

## Назначение

Delta Window — окно наблюдения за изменениями в тестовом полигоне IMPERIUM_TEST_VERSION.

Позволяет Owner:
1. Видеть что было на baseline commit
2. Видеть что стало в текущем worktree
3. Какие файлы изменились
4. Какие проверки улучшились/ухудшились
5. Есть ли fake green / stale truth / broken dashboards
6. Можно ли коммитить или нужно чинить

## Scope

**СТРОГО ОГРАНИЧЕН:** `E:\IMPERIUM\IMPERIUM_TEST_VERSION\`

Main repo читается только для git truth/reference.

## Запуск

```powershell
cd E:\IMPERIUM\IMPERIUM_TEST_VERSION
.\TESTING_FIELD\DELTA_WINDOW\run_delta_check.ps1
```

## Режимы работы

### MODE A — Pre-commit (основной)
Сравнивает: Git HEAD vs текущий worktree
Scope: только IMPERIUM_TEST_VERSION

### MODE B — Historical
Сравнивает два коммита:
- OLD: 3274087e1f597a43ced3252c7edefcb3fda310f1
- NEW: ff9457d2e5d5d4da9d5b39d039dc1622cbf34810

## Выходные файлы

| Файл | Описание |
|------|----------|
| `delta_window.html` | Главное окно |
| `REPORTS/latest_delta_report.json` | JSON отчёт |
| `REPORTS/latest_delta_report_ru.md` | Markdown отчёт |
| `REPORTS/latest_precommit_verdict.json` | Вердикт |
| `REPORTS/command_log.md` | Лог команд |
| `REPORTS/run_receipt.json` | Квитанция запуска |

## Ограничения MVP

1. Screenshots требуют Playwright (опционально)
2. Historical mode — только file diff
3. Кнопки действий — DISPLAY_ONLY (не выполняют git)

## Статус

- [x] Pre-commit mode
- [x] Historical mode (partial)
- [ ] Screenshots (requires Playwright)
- [x] HTML opens locally
- [x] Scoped to test version only
