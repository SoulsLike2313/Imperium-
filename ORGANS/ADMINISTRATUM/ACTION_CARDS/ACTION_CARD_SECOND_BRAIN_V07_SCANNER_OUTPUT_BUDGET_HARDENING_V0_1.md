# ACTION CARD: SECOND BRAIN V0.7 SCANNER OUTPUT BUDGET HARDENING

| Поле | Значение |
|---|---|
| Task Name | Second Brain V0.7 Scanner Output Budget Hardening |
| Current HEAD | `6cd43c85fb08f4f8cc556c5992148986a3840685` |
| Bloat Cause | Scanner report dumped oversized findings payload (`164480` lines in JSON) |
| Hardened Scanner | `visual_fake_green_scanner_v0_1.py` compact-by-default |
| New Gate | `GATE-U12-REPORT-OUTPUT-BUDGET` |
| Next Allowed Task | `TASK-SECOND-BRAIN-V07-BROWSER-PERFORMANCE-AUDIT-RUNNER` |

## Что было укреплено
- Введён закон `REPORT_OUTPUT_BUDGET / NO_REPORT_AVALANCHE`.
- Добавлен `GATE-U12-REPORT-OUTPUT-BUDGET` в registry + базовые gate-документы.
- Сканер ограничен по top/samples/excerpt и перестал писать unlimited findings.
- Компактный отчёт перегенерирован по тому же пути без удаления файла.

## Что намеренно не тронуто
- Любые runtime/app/server/assets/css/js/html реализации.
- Любые визуальные изменения UI.
- Любая оптимизация производительности.

## Compact Report Path
- `E:/IMPERIUM/IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/VISUAL_FAKE_GREEN_SCAN_V0_1.json`

## New Gate/Rule Paths
- `E:/IMPERIUM/ORGANS/DOCTRINARIUM/GATES/REPORT_OUTPUT_BUDGET_V0_1.md`
- `E:/IMPERIUM/ORGANS/DOCTRINARIUM/GATES/REPORT_OUTPUT_BUDGET_V0_1.json`

## Stop Warnings
- STOP если отчёты снова выходят за budget без Owner gate.
- STOP если scanner начинает recursive/raw dump в tracked repo.
- STOP при любом forbidden path в diff.
