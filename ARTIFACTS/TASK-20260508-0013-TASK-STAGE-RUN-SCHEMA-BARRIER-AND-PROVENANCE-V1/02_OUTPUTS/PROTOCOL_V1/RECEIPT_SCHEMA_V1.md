# RECEIPT_SCHEMA_V1

## Purpose
Define a strict receipt format for every meaningful action and failure path.

## Required fields
- receipt_schema_version
- task_id
- stage_id
- run_id
- contour_id
- executor_id
- executor_type
- producer_type
- producer_id
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
- provenance_ref
- origin_index_ref
- sha256_checks
- verdict
- blockers
- notes

## Verdict enum
- PASS
- PARTIAL
- BLOCKED
- FAILED

## Validation
1. failure receipts are mandatory.
2. no-delete/no-throne/no-autosync flags must be explicit booleans.
3. provenance_ref and origin_index_ref are mandatory for accepted artifacts.
4. local_route_values_included must be false for shareable artifacts.

## Rejection conditions
- receipt without task/stage/run/contour
- receipt without provenance_ref
- receipt claiming final authority from VM2
