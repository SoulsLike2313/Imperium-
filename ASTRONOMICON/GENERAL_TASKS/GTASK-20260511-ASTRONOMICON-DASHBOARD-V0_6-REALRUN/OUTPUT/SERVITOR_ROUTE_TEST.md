# Servitor Route Test

Purpose:
Verify that a Servitor can route to a Local Task by ID.

General Task:
GTASK-20260511-ASTRONOMICON-DASHBOARD-V0_6-REALRUN

Example route:
1. Servitor receives LOCAL_TASK_ID: LTASK-001
2. Servitor opens LOCAL_TASKS/LTASK-001/LOCAL_TASK.json
3. Servitor reads parent_general_task_id, scope_text, expected_output, required_organs, execution_mode.
4. Servitor moves to required organs with evidence-first discipline.

Available Local Tasks:
- LTASK-001: Create robust parser pipeline evidence
- LTASK-002: Run Local Task Speculum exchange
- LTASK-003: Run Stage Speculum exchange