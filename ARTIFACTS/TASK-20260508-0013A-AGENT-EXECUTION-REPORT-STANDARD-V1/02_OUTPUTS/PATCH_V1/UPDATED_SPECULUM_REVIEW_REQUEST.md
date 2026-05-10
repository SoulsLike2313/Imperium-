# UPDATED_SPECULUM_REVIEW_REQUEST

Review target:
Protocol patch for mandatory unified Owner-facing execution report.

Speculum must verify:
1. Whether the final Owner-facing response follows `AGENT_EXECUTION_REPORT_STANDARD_V1.md`.
2. Whether missing `ШАГ/БАНДЛ/ВЕРДИКТ/КОММЕНТАРИЙ ДЛЯ OWNER` is treated as validation failure.
3. Whether non-standard reporting is marked `REPAIR_REQUIRED` (not cosmetic).
4. Whether updated validation/script/final-bundle contracts consistently enforce the reporting standard.
5. Whether any latest-bundle, THRONE, or auto-sync leakage remains.

Expected review output:
- PASS / PARTIAL / BLOCKED
- REPAIR_REQUIRED items
- readiness for TASK-0014 script repair
