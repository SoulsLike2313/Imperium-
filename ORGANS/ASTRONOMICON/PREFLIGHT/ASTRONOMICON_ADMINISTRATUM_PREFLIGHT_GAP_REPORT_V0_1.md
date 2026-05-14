# ASTRONOMICON + ADMINISTRATUM PREFLIGHT GAP REPORT V0.1

## 1) Current truth table

| area | exists? | implemented? | evidence path | verdict |
|---|---|---|---|---|
| Astronomicon active state files | YES | PARTIAL (preflight level) | ORGANS/ASTRONOMICON/ACTIVE_STATE/ | PASS_WITH_WARNINGS |
| Empty active indexes | YES | PARTIAL (placeholder) | ORGANS/ASTRONOMICON/ACTIVE_STATE/*_index.json | PASS_WITH_WARNINGS |
| Advisory retirement index | YES | PARTIAL (manual index) | ORGANS/ASTRONOMICON/RETIRED_INPUTS/RETIRED_OR_NOT_ACTIVE_ADVISORY_INDEX_20260514.md | PASS_WITH_WARNINGS |
| Administratum stage-control skeleton | YES | NO (scripts not built) | ORGANS/ADMINISTRATUM/STAGE_CONTROL/ | PASS_WITH_WARNINGS |
| Stage acceptance loop scripts | NO | NO | n/a | MISSING |

## 2) Missing foundation table

| missing item | why needed | future task | blocker level |
|---|---|---|---|
| general_task.schema.json | stable validation for General Task intake | TASK-20260514-ASTRONOMICON-WORKBENCH-MVP | HIGH |
| task_candidate.schema.json | normalize task-candidate structure | TASK-20260514-ASTRONOMICON-WORKBENCH-MVP | MEDIUM |
| stage.schema.json | enforce stage contract semantics | TASK-20260514-ASTRONOMICON-WORKBENCH-MVP | HIGH |
| validate_general_task.py | fail-closed intake validation | TASK-20260514-ASTRONOMICON-WORKBENCH-MVP | HIGH |
| decompose_general_task_to_tasks.py | deterministic decomposition helper | TASK-20260514-ASTRONOMICON-WORKBENCH-MVP | MEDIUM |
| decompose_task_to_stages.py | deterministic stage split helper | TASK-20260514-ASTRONOMICON-WORKBENCH-MVP | MEDIUM |
| register_general_task_bundle.py | canonical registration artifact pipeline | TASK-20260514-ASTRONOMICON-WORKBENCH-MVP | MEDIUM |
| generate_astronomicon_dashboard_data.py | backend truth feed for viewer/dashboard | TASK-20260514-ASTRONOMICON-WORKBENCH-MVP | HIGH |
| administratum_stage_start_permission.py | pre-stage permission gate | TASK-20260514-ADMINISTRATUM-STAGE-LOOP-MVP | HIGH |
| administratum_stage_submit.py | stage evidence submission entrypoint | TASK-20260514-ADMINISTRATUM-STAGE-LOOP-MVP | HIGH |
| administratum_stage_acceptance.py | evidence-based continue/block decision | TASK-20260514-ADMINISTRATUM-STAGE-LOOP-MVP | HIGH |
| administratum_final_bundle_aggregate.py | final artifact bundling discipline | TASK-20260514-ADMINISTRATUM-STAGE-LOOP-MVP | MEDIUM |
| dashboard data model | truthful NO_ACTIVE_GENERAL_TASK state rendering | TASK-20260514-ASTRONOMICON-WORKBENCH-MVP | HIGH |
| minimal dashboard/viewer | owner-readable state visibility | TASK-20260514-ASTRONOMICON-WORKBENCH-MVP | MEDIUM |

## 3) Next recommended task table

| next task | goal | files likely touched | checks | owner gate |
|---|---|---|---|---|
| TASK-20260514-ASTRONOMICON-WORKBENCH-MVP | implement clean General Task intake and read-only active state surfacing | ORGANS/ASTRONOMICON/, scripts/, schemas/, tests/ | schema validation, py_compile, fixture checks, active-state assertions | REQUIRED |
| TASK-20260514-ADMINISTRATUM-STAGE-LOOP-MVP | implement minimal stage permission/submit/accept loop | ORGANS/ADMINISTRATUM/, scripts/, tests/ | loop contract checks, evidence gate checks | REQUIRED |
