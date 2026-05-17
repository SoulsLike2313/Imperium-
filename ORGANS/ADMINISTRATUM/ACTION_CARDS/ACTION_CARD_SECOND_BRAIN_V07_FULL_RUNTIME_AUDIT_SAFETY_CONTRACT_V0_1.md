# ACTION CARD: SECOND BRAIN V0.7 FULL RUNTIME AUDIT SAFETY CONTRACT

| Поле | Значение |
|---|---|
| Task Name | Second Brain V0.7 Full Runtime Audit Safety Contract |
| Current HEAD | `e488ea5224dccd3b2fd768c838fac7a9a434e6be` |
| Что создано | Safety Contract (MD+JSON), Source Survey (MD+JSON), Inquisition rules, Gate Receipt, Task Report |
| Что намеренно не тронуто | Не запускался runtime/server; не изменялись V0.6/V0.7 app/server/tools/source файлы |
| Ключевые риски | Runtime writes в `MEMORY_ZONES`/`RUNTIME`, mutating API endpoints, риск pollution без quarantine |
| Safety Contract Path | `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/VISUAL_SYSTEM/FULL_RUNTIME_AUDIT_SAFETY_CONTRACT_V0_1.md` |
| Source Survey Path | `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/FULL_RUNTIME_AUDIT_SOURCE_SURVEY_V0_1.md` |
| Next Allowed Task | `TASK-SECOND-BRAIN-V07-FULL-RUNTIME-PERFORMANCE-AUDIT-RUNNER` |

## Stop Warnings
- Нельзя заявлять full runtime PASS до изолированного запуска и receipt-подтверждения side effects.
- Нельзя коммитить raw traces/screenshots без Owner gate.
- Нельзя выполнять silent cleanup runtime-следов.
