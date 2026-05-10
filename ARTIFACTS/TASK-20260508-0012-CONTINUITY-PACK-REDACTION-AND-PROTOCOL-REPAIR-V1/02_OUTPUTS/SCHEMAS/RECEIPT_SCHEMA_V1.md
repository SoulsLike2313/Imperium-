# RECEIPT SCHEMA V1

Required fields:
- receipt_schema_version
- task_id
- stage_id
- run_id
- contour_id
- executor_id
- executor_type
- action_type
- timestamp_start
- timestamp_end
- inputs
- outputs
- commands_or_tools_used
- deleted_anything
- moved_anything
- touched_throne
- touched_vm2
- touched_vm3
- autosync_used
- latest_logic_used
- network_used
- secrets_included
- local_route_values_included
- sha256_checks
- verdict
- blockers
- notes

Verdict enum:
- PASS
- PARTIAL
- BLOCKED
- FAILED

Rules:
- Future receipts must include TASK_ID, STAGE_ID, RUN_ID, and CONTOUR_ID.
- Failure receipts are mandatory.
- No-delete, no-throne, and no-autosync must be explicit.
- Shareable receipts must redact local route values.
