# Speculum Refinements

LOCAL_TASK_ID:
LTASK-002

GENERAL_TASK_ID:
GTASK-20260511-ASTRONOMICON-GENERAL-TASK-V0_1

RECOMMENDED_STATUS:
READY_FOR_STAGE_DECOMPOSITION

## Scope Narrowing
- Only parse PLAN_ITEMS into Local Task records.
- Do not implement Speculum import or stage decomposition here.


## Technical Execution Risks
- Regex parser may break if ITEM blocks are malformed.
- Generated Local Task IDs may become unstable if order changes.


## Missing Inputs
- Stable ID policy.
- Hash policy for Local Task records.


## Required Tools Or Scripts
- astronomicon_parse_general_task_v0_1.ps1


## Readiness Questions
- Are LTASK IDs deterministic?
- Does each Local Task have parent_general_task_id and hash?


## Pass Criteria
- Each PLAN ITEM creates exactly one LTASK folder.
- LOCAL_TASK_REGISTRY.json contains all created tasks.


## Fail Conditions
- Task count mismatch.
- Missing LOCAL_TASK.json or HASH.json.


## Do Not Do
- Do not overwrite source General Task text.
- Do not create tasks without source_plan_item_id.


## Decomposition Hints
- Stage 1: parse registry.
- Stage 2: create Local Task folder.
- Stage 3: create hash/status records.


SHOULD_SPLIT:
False