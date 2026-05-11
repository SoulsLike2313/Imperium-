# Speculum Local Task Refinements

LOCAL_TASK_ID:
LTASK-002

GENERAL_TASK_ID:
GTASK-20260511-ASTRONOMICON-DASHBOARD-V0_6-REALRUN

RECOMMENDED_STATUS:
READY_FOR_STAGE_DECOMPOSITION

## Scope Narrowing
- Keep execution scope aligned with LTASK-002.

## Technical Execution Risks
- Parser schema drift can break consistency.

## Missing Inputs
- Confirm destination files before execution.

## Required Tools Or Scripts
- PowerShell 5+
- astronomicon_decompose_local_task_to_stages_v0_2.ps1

## Readiness Questions
- Are pass criteria and fail conditions explicit?

## Pass Criteria
- All expected outputs exist and are inspectable.

## Fail Conditions
- Any required artifact is missing.

## Do Not Do
- Do not modify unrelated task records.

## Decomposition Hints
- Prepare inputs and constraints.
- Apply change and produce evidence.
- Verify outputs and finalize.

SHOULD_SPLIT:
False