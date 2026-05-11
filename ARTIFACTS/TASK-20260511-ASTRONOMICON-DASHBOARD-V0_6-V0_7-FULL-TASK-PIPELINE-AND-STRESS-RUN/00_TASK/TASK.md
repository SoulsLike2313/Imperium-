# TASK.md

TASK_ID:
TASK-20260511-ASTRONOMICON-DASHBOARD-V0_6-V0_7-FULL-TASK-PIPELINE-AND-STRESS-RUN

PRIMARY_GOAL:
Bring Astronomicon Dashboard from fragile v0.5 to technically usable v0.6, then create v0.7 with synthetic full-run testing and stronger visual feedback.

MANDATORY_OUTPUTS:
- New dashboards: v0.6 and v0.7 + launchers.
- Backend helpers for stage export/import, safe commit/push, synthetic run.
- Full artifact tree with baseline, implementation, run evidence, defects, git verification, owner summary.

EXECUTION_NOTES:
- Do not touch THRONE.
- Do not stage forbidden secrets/credentials paths.
- No blind git add.
- No overwrite of previous dashboard versions.
- After synthetic stress test, discovered bugs are recorded and not fixed.