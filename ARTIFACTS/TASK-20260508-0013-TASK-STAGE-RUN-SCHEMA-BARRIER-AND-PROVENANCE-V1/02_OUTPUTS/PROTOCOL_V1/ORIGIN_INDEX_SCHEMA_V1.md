# ORIGIN_INDEX_SCHEMA_V1

## Purpose
Prevent provenance confusion and silent hash collisions.

## Minimum index key
`TASK_ID + STAGE_ID + RUN_ID + CONTOUR_ID + PRODUCER_TYPE + PRODUCER_ID + ARTIFACT_SHA256`

## Required fields
- task_id
- stage_id
- run_id
- contour_id
- producer_type
- producer_id
- artifact_name
- artifact_path
- artifact_sha256
- provenance_ref
- receipt_ref
- first_seen_utc
- last_seen_utc
- origin_status

## Origin status enum
- UNIQUE
- DUPLICATE_SAME_HASH
- CONFLICT_DIFFERENT_HASH
- REJECTED_UNKNOWN_ORIGIN

## Conflict prevention requirements
1. PC Servitor bundle must not be interpreted as OWNER_MANUAL bundle.
2. OWNER_MANUAL bundle must not be interpreted as VM2 output.
3. VM2 stage bundle must not be accepted as PC final bundle.
4. same TASK/STAGE/RUN with different hash must raise conflict.
5. manually renamed bundle without valid provenance must be rejected.
