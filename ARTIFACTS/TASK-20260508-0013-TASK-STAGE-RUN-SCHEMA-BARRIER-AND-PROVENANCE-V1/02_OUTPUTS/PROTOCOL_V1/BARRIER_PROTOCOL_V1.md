# BARRIER_PROTOCOL_V1

## Purpose
Deterministic reducer over task evidence to prevent fake PASS.

## Inputs
- task/stage/run schemas
- expected stage map
- manifests
- sha256 records
- receipts
- provenance records
- origin index
- ledger events

## Output enum
- BARRIER_PASS
- BARRIER_FAIL
- BARRIER_WAITING
- BARRIER_CONFLICT

## Reducer logic
1. Validate identity fields: task_id, stage_id, run_id, contour_id, producer_type, producer_id.
2. Validate artifact integrity: manifest exists, sha256 exists and matches, receipt exists.
3. Validate provenance/origin: producer and contour are allowed; origin index key uniqueness holds.
4. Validate policy: no THRONE transfer claim, no auto-sync claim, no latest-bundle logic evidence.
5. Validate authority boundaries: VM2 cannot claim FINAL_TASK_BUNDLE authority.
6. Validate conflict conditions: same namespace key with different hash => conflict.

## Mandatory reject reasons
- missing TASK_ID
- missing STAGE_ID
- missing RUN_ID
- missing CONTOUR_ID
- missing producer_type
- missing producer_id
- unknown origin
- anonymous bundle
- mismatched sha256
- missing manifest
- missing receipt
- receipt without provenance
- bundle claiming final authority from VM2
- Owner manual artifact pretending to be scripted output
- latest-fetch evidence
- THRONE transfer claim
- auto-sync claim
- conflicting bundles for same TASK/STAGE/RUN/CONTOUR

## Decision policy
- BARRIER_WAITING: required evidence is not complete yet.
- BARRIER_FAIL: evidence complete but validation failed.
- BARRIER_CONFLICT: competing valid-looking artifacts conflict by origin/hash.
- BARRIER_PASS: all required evidence passes and no conflicts remain.
