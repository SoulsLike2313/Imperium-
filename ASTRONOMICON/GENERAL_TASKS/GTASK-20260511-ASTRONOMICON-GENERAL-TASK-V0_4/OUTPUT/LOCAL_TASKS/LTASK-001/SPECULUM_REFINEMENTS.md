# Speculum Refinements

LOCAL_TASK_ID:
LTASK-001

GENERAL_TASK_ID:
GTASK-20260511-ASTRONOMICON-GENERAL-TASK-V0_1

RECOMMENDED_STATUS:
BLOCKED_NEEDS_OWNER_SCOPE

## Scope Narrowing
- Replace the placeholder title and placeholder expected output with a concrete contract task before execution.
- Limit this task to defining the minimum General Task input contract only: required fields, block boundaries, validation rules, encoding rule, and failure behavior.
- Exclude dashboard UI, Speculum import, stage decomposition, commit/push automation, and any runtime execution from this Local Task.


## Technical Execution Risks
- The current task text is still a placeholder, so any stage decomposition would be invented rather than derived from a real scope.
- If the parser accepts free-form text or missing PLAN_ITEMS, Astronomicon will create fake executable tasks.
- If UTF-8-BOM and CRLF are not enforced, Russian or mixed-language owner text may be corrupted in Windows tooling.
- If GENERAL_TASK_ID in the UI, form, registry, and folder path diverge, downstream imports will attach refinements to the wrong task tree.


## Missing Inputs
- Canonical General Task field list with required/optional flags.
- Validation failure matrix: missing header, missing ID, missing PLAN_ITEMS, malformed ITEM, duplicate ITEM_ID, empty expected output.
- Stable ID synchronization rule: UI field, form field, folder name, registry ID, and export ID must match.
- Definition of allowed human-language content versus machine-readable English keys.


## Required Tools Or Scripts
- General Task strict-format validator.
- UTF-8-BOM/CRLF writer helper.
- GENERAL_TASK_ID synchronization check.
- Validation report generator that stops on malformed input.


## Readiness Questions
- Does the form contain the required schema header and explicit GENERAL_TASK_ID?
- Does every PLAN ITEM contain ITEM_ID, TITLE, TEXT, EXPECTED_OUTPUT, REQUIRED_ORGANS, EXECUTION_MODE, DEPENDS_ON, and END_ITEM?
- Does the parser fail closed instead of guessing when required fields are missing?
- Does the saved form preserve exact text, encoding, and line endings?
- Do UI task ID, form task ID, output registry ID, and folder path agree?


## Pass Criteria
- A valid General Task form produces GENERAL_TASK.json, HASH.json, VALIDATION_REPORT.json, and a source text copy.
- A malformed General Task form produces VALIDATION_REPORT.json and does not create Local Tasks.
- The saved source text is UTF-8-BOM with CRLF and can be reopened without mojibake.
- GENERAL_TASK_ID remains identical across UI, form, output folder, registry, and export payload.


## Fail Conditions
- Parser creates Local Tasks from placeholder or malformed PLAN_ITEMS.
- GENERAL_TASK_ID mismatch appears between dashboard card, form, registry, and Speculum export.
- Required field is missing but the script continues.
- Encoding corruption appears in saved source or generated records.


## Do Not Do
- Do not use this Local Task to build the full dashboard.
- Do not infer missing scope from Owner notes.
- Do not declare READY_FOR_STAGE_DECOMPOSITION while the task still contains placeholder title/output.
- Do not overwrite the original SOURCE_TEXT.


## Decomposition Hints
- Stage 1: Define the canonical required field list and allowed values.
- Stage 2: Define validation failure behavior and stop conditions.
- Stage 3: Add ID synchronization verification.
- Stage 4: Add encoding and line-ending verification.
- Stage 5: Run one valid and one malformed form test.


SHOULD_SPLIT:
True