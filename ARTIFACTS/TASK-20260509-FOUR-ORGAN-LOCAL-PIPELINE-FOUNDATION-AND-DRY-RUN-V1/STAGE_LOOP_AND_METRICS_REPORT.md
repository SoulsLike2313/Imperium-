# STAGE LOOP AND METRICS REPORT

Schemas created in E:/IMPERIUM/ORGANS/_PORTS/SCHEMAS:
- BLOCKED_RECEIPT_SCHEMA.json
- ORGAN_PORT_PACKET_SCHEMA.json
- PIPELINE_RUN_LEDGER_SCHEMA.json
- REPAIR_ATTEMPT_SCHEMA.json
- STAGE_METRICS_SCHEMA.json
- STAGE_RECEIPT_SCHEMA.json
- STAGE_VALIDATION_REPORT_SCHEMA.json

Loop contract:
1. Read stage + policies + allowed tools.
2. Execute bounded stage scope only.
3. Run validation.
4. PASS -> write pass receipt + validation report.
5. FAIL safe -> bounded repair + rerun.
6. Semantic/destructive conflict -> BLOCKED receipt + Owner stop.
