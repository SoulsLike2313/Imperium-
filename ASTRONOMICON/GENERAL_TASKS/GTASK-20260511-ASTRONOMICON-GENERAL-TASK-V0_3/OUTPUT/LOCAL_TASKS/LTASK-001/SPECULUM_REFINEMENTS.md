# Speculum Refinements

LOCAL_TASK_ID:
LTASK-001

GENERAL_TASK_ID:
GTASK-20260511-ASTRONOMICON-GENERAL-TASK-V0_1

RECOMMENDED_STATUS:
READY_FOR_STAGE_DECOMPOSITION

## Scope Narrowing
- Define only the minimum strict General Task form contract required for parser input.
- Do not design the full Astronomicon dashboard in this task.


## Technical Execution Risks
- Form fields may be too flexible for deterministic parsing.
- Encoding mismatch may corrupt Russian text if UTF-8-BOM is not enforced.


## Missing Inputs
- Canonical required field list.
- Validation failure behavior.


## Required Tools Or Scripts
- General Task form validator.
- UTF-8-BOM writer helper.


## Readiness Questions
- Does the form contain all required blocks?
- Can the parser reject malformed PLAN_ITEMS without guessing?


## Pass Criteria
- A valid form produces GENERAL_TASK.json.
- A malformed form produces VALIDATION_REPORT.json and stops.


## Fail Conditions
- Parser silently accepts missing PLAN_ITEMS.
- Parser creates Local Tasks with empty required fields.


## Do Not Do
- Do not infer missing tasks from free text.
- Do not proceed when required fields are absent.


## Decomposition Hints
- Stage 1: define required fields.
- Stage 2: define validation rules.
- Stage 3: test malformed input.


SHOULD_SPLIT:
False