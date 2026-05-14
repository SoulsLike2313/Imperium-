# ASTRONOMICON SCHEMAS README V0.1

## Scope

This folder contains MVP schema contracts for Astronomicon dense base:

- `general_task.schema.json`
- `task_candidate.schema.json`
- `local_task.schema.json`
- `stage.schema.json`
- `speculum_task_review_response.schema.json`
- `speculum_stage_review_response.schema.json`
- `astronomicon_dashboard_data.schema.json`

## Notes

- `schema_version` is required in each payload.
- Schema contracts are strict enough for MVP validation and future script hardening.
- Speculum response schemas enforce structured fields; free-form advice is secondary.
- These schemas do not declare canon or readiness by themselves.
