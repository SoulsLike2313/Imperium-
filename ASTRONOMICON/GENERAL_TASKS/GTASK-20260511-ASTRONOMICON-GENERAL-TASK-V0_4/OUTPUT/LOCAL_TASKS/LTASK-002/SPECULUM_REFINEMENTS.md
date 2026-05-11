# Speculum Refinements

LOCAL_TASK_ID:
LTASK-002

GENERAL_TASK_ID:
GTASK-20260511-ASTRONOMICON-GENERAL-TASK-V0_1

RECOMMENDED_STATUS:
BLOCKED_NEEDS_OWNER_SCOPE

## Scope Narrowing
- Replace the placeholder title and expected output with a concrete parser-build task before execution.
- Limit this task to converting registered PLAN_ITEMS into Local Task records and registry files.
- Do not include Speculum import, stage generation, dashboard layout work, or commit/push automation in this Local Task.


## Technical Execution Risks
- Regex-based ITEM parsing can silently miss malformed or nested fields.
- Local Task IDs may become unstable if they are generated only from item order and the plan is edited later.
- Hash records may become misleading if the hash input is not normalized and documented.
- Generated Local Tasks may look executable even when source PLAN_ITEM content is placeholder text.


## Missing Inputs
- Stable LTASK ID policy: order-based, source ITEM_ID-based, or combined mapping.
- Duplicate ITEM_ID handling rule.
- Expected registry schema for LOCAL_TASK_REGISTRY.json.
- Hash policy: exact normalized JSON fields included in each hash.
- Rule for placeholder detection and blocked status.


## Required Tools Or Scripts
- astronomicon_parse_general_task_v0_1.ps1 or successor.
- Local Task registry validator.
- Hash generation helper.
- Placeholder-content detector for TITLE/TEXT/EXPECTED_OUTPUT.


## Readiness Questions
- Does every PLAN_ITEM create exactly one LTASK folder?
- Does every LTASK include parent_general_task_id, source_plan_item_id, title, scope_text, expected_output, required_organs, execution_mode, status, and hash?
- Does LOCAL_TASK_REGISTRY.json match the actual LOCAL_TASKS directory count?
- Does the script reject duplicate source_plan_item_id values?
- Does the output mark placeholder tasks as blocked rather than ready?


## Pass Criteria
- Two PLAN_ITEMS create exactly LTASK-001 and LTASK-002 in the current test.
- Each LTASK has LOCAL_TASK.json, LOCAL_TASK.md, HASH.json, and STATUS.json.
- LOCAL_TASK_REGISTRY.json lists all generated LTASK records with matching hashes.
- The parser creates a receipt showing input path, output path, task count, and PASS_WITH_LIMITATIONS.
- Placeholder content is flagged as not execution-ready.


## Fail Conditions
- Task count mismatch between registry and folders.
- Local Task folder exists without LOCAL_TASK.json or STATUS.json.
- Task hash changes without source content or schema change.
- Parser overwrites source General Task text.
- Dashboard shows a task as ready when placeholder content remains.


## Do Not Do
- Do not create stage maps in this Local Task.
- Do not import Speculum refinements here.
- Do not hide parser errors inside dashboard logs only.
- Do not use git add . for generated output.


## Decomposition Hints
- Stage 1: Validate PLAN_ITEMS block and ITEM boundaries.
- Stage 2: Generate deterministic LTASK records.
- Stage 3: Generate registry and hash files.
- Stage 4: Validate registry-to-folder consistency.
- Stage 5: Produce parse receipt and blocked/ready status.


SHOULD_SPLIT:
True