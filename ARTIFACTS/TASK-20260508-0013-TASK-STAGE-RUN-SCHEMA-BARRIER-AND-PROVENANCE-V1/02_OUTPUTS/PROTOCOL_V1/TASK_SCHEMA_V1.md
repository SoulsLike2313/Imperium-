# TASK_SCHEMA_V1

## Purpose
Define a task-level contract that allows PC, VM2, and Owner-manual artifacts to coexist without provenance ambiguity.

## Required fields
- task_id
- task_name
- purpose
- owner_authority_required
- created_at_utc
- allowed_contours
- allowed_producer_types
- stage_ids
- stage_execution_order
- expected_stage_map_ref
- blocked_actions
- notes

## Allowed values
allowed_contours:
- PC
- VM2
- OWNER_MANUAL

allowed_producer_types:
- PC_SERVITOR
- VM2_WORKER
- OWNER_MANUAL

future_producer_types_listed_not_active:
- LOCAL_LLM_WORKER
- REMOTE_AGENT_WORKER
- SPECULUM_REVIEWER

## Validation
1. task_id must match `TASK-<date>-<seq>-<slug>`.
2. task_id must be present in all stage, run, receipt, provenance, ledger, and bundle records.
3. allowed_producer_types must not include UNKNOWN for accepted artifacts.
4. blocked_actions must include: `THRONE_TRANSFER`, `AUTOMATION_WATCHERS`, `LATEST_BUNDLE_LOGIC`.
5. expected_stage_map_ref must resolve to a versioned stage map document.

## Rejection conditions
- missing task_id
- empty stage_ids
- UNKNOWN as accepted producer
- task contract claiming production readiness
