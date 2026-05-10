# PARALLEL_EXECUTION_PROTOCOL_V1

## Scope
Parallel-safe execution for shared TASK_ID across PC and VM2 with optional OWNER_MANUAL artifacts.

## Core rules
1. TASK_ID may be shared.
2. STAGE_ID is the work unit.
3. RUN_ID is the specific execution attempt.
4. Each contour writes only to its own stage/run namespace.
5. No producer may claim the same TASK_ID + STAGE_ID + RUN_ID + CONTOUR_ID unless hashes are identical and provenance confirms duplication.
6. Conflict yields `BARRIER_CONFLICT` or `ORIGIN_CONFLICT`, never PASS.

## Namespace rule
Artifact namespace key:
`TASK_ID/STAGE_ID/RUN_ID/CONTOUR_ID/PRODUCER_TYPE/PRODUCER_ID`

## Collision handling
- Same namespace key + different hash => ORIGIN_CONFLICT.
- Same namespace key + same hash + duplication proof => allowed duplicate reference.
- Missing producer_id => reject as anonymous artifact.

## Forbidden shortcuts
- latest bundle fetch
- anonymous dispatch
- final bundle authority on VM2
- implicit overwrite without ledger event
