# RUN_SCHEMA_V1

## Purpose
Define a run attempt for a specific TASK_ID + STAGE_ID + CONTOUR_ID.

## Required fields
- task_id
- stage_id
- run_id
- contour_id
- producer_type
- producer_id
- run_attempt_index
- triggered_by
- started_at_utc
- ended_at_utc
- run_status
- output_bundle_ref
- output_bundle_sha256
- receipt_ref
- provenance_ref

## Allowed values
contour_id:
- PC
- VM2
- OWNER_MANUAL

producer_type:
- PC_SERVITOR
- VM2_WORKER
- OWNER_MANUAL

run_status:
- RUNNING
- PASS
- FAIL
- BLOCKED
- CONFLICT

## Validation
1. run_id is mandatory and cannot be auto-defaulted.
2. run_id must be immutable after creation.
3. one run record corresponds to one producer_type + producer_id.
4. output_bundle_sha256 is mandatory when run_status is PASS.

## Rejection conditions
- missing run_id
- run marked PASS without output_bundle_sha256
- producer_type mismatch with contour_id contract
