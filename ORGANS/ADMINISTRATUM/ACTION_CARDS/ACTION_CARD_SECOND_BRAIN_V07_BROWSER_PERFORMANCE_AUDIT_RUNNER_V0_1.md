# ACTION CARD: SECOND BRAIN V0.7 BROWSER PERFORMANCE AUDIT RUNNER

| Поле | Значение |
|---|---|
| Task Name | Second Brain V0.7 Browser Performance Audit Runner |
| Current HEAD | `94cf6b7fb773ea967f47e087337c5461aa9a017a` |
| Browser Audit Ran | `true` |
| FPS Measured | `true` |
| Next Allowed Task | `TASK-SECOND-BRAIN-V07-PERFORMANCE-AUDIT-INTERPRETATION` |

## Что создано
- `browser_performance_audit_runner_v0_1.py` + README.
- `BROWSER_PERFORMANCE_AUDIT_RECEIPT_V0_1.json/.md`.
- `BROWSER_PERFORMANCE_AUDIT_RUNNER_REPORT_V0_1.json/.md`.
- Gate receipt + JSONL index entry.

## Что намеренно не тронуто
- Любые runtime/app/server/assets/css/js/html implementation файлы.
- Любые визуальные изменения и оптимизации.
- Любые raw trace/archive/screenshot артефакты.

## Browser/FPS Truth
- browser_audit_status: `BROWSER_AUDIT_RUN`
- fps_status: `FPS_MEASURED`
- if_not_measured_reason: `None`

## Compact Report Paths
- `E:/IMPERIUM/IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/BROWSER_PERFORMANCE_AUDIT_RECEIPT_V0_1.json`
- `E:/IMPERIUM/IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/BROWSER_PERFORMANCE_AUDIT_RUNNER_REPORT_V0_1.json`

## Stop Warnings
- STOP при любом fake FPS claim.
- STOP при попытке commit raw traces/har/zip/png.
- STOP при выходе отчётов за budget GATE-U12.
