# ACTION CARD: SECOND BRAIN V0.7 VISUAL FAKE-GREEN SCANNER

| Поле | Значение |
|---|---|
| Task Name | Second Brain V0.7 Visual Fake-Green Scanner |
| Current HEAD | `c448ad30d680eebf1b2857996970b7aa007a52cb` |
| Scan Verdict | `WARN` |
| Next Allowed Task | `TASK-SECOND-BRAIN-V07-BROWSER-PERFORMANCE-AUDIT-RUNNER` |

## Что создано
- Новый сканер: `visual_fake_green_scanner_v0_1.py`
- Отчёт сканера: `VISUAL_FAKE_GREEN_SCAN_V0_1.json/.md`
- Task report: `VISUAL_FAKE_GREEN_SCANNER_REPORT_V0_1.json/.md`
- Gate receipt: `GATE_RECEIPT_TASK_SECOND_BRAIN_V07_VISUAL_FAKE_GREEN_SCANNER_V0_1.json/.md`
- GATE_ACK для текущей задачи.

## Что намеренно не тронуто
- Любые runtime/app/server/assets реализации V0.6/V0.7.
- Любые CSS/JS/HTML изменения поведения UI.
- Любая оптимизация производительности.

## Ключевые выводы (3-6)
- `HARD_BLOCKER`: 0, но найден большой объём подозрительных паттернов для ручного разбора.
- Основной класс `WARNING`: декоративное/статусное использование `green` без явной evidence-привязки рядом.
- Найдены `REVIEW_REQUIRED` в условной логике PASS/READY/COMPLETE, где требуется ручная семантическая проверка.
- Базовый performance-контекст остаётся ограниченным: baseline ранее `BLOCKED`, FPS по browser-аудиту не подтверждён.
- Правило no-fake-green соблюдено: сканер не утверждает runtime truth parity и не даёт FPS PASS.

## Exact Paths
- `E:\IMPERIUM\IMPERIUM_TEST_VERSION\SECOND_BRAIN\NEURAL_BASE_V0_7\reports\VISUAL_FAKE_GREEN_SCAN_V0_1.json`
- `E:\IMPERIUM\IMPERIUM_TEST_VERSION\SECOND_BRAIN\NEURAL_BASE_V0_7\reports\VISUAL_FAKE_GREEN_SCANNER_REPORT_V0_1.json`
- `E:\IMPERIUM\ORGANS\ADMINISTRATUM\GATE_RECEIPTS\GATE_RECEIPT_TASK_SECOND_BRAIN_V07_VISUAL_FAKE_GREEN_SCANNER_V0_1.json`

## Stop Warnings
- STOP при любом изменении forbidden paths.
- STOP при попытке выдать WARN-скан за runtime PASS.
- STOP при попытке добавить FPS claim без browser/performance receipt.
