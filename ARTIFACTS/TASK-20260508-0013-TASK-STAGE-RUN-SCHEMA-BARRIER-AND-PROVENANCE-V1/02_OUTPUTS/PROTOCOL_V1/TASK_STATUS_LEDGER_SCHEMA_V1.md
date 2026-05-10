# TASK_STATUS_LEDGER_SCHEMA_V1

## Format
Append-only JSONL. One event per line. No in-place rewrite.

## Required event fields
- event_id
- task_id
- stage_id
- run_id
- contour_id
- producer_type
- producer_id
- event_type
- status
- artifact_ref
- artifact_sha256
- previous_event_ref
- timestamp_utc
- receipt_ref
- notes

## Required event types
- TASK_CREATED
- STAGE_DECLARED
- STAGE_DISPATCHED
- STAGE_STARTED
- STAGE_PROGRESS
- STAGE_COMPLETED
- STAGE_FAILED
- BUNDLE_CREATED
- BUNDLE_FETCHED
- HASH_VERIFIED
- MANIFEST_VERIFIED
- RECEIPT_VERIFIED
- BARRIER_PASS
- BARRIER_FAIL
- BARRIER_WAITING
- BARRIER_CONFLICT
- ORIGIN_CONFLICT
- FINAL_BUNDLE_CREATED
- SPECULUM_REVIEW_REQUESTED

## Ledger rules
1. previous_event_ref must chain events per task timeline.
2. any state-changing action must emit an event.
3. conflicting artifacts must emit ORIGIN_CONFLICT.
4. barrier decision must emit one of PASS/FAIL/WAITING/CONFLICT.
