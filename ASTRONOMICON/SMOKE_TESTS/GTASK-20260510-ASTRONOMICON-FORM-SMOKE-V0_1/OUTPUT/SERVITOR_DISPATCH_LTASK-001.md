# Servitor Dispatch Test

LOCAL_TASK_ID:
LTASK-001

PARENT_GENERAL_TASK_ID:
GTASK-20260511-ASTRONOMICON-FORM-SMOKE-V0_1

TITLE:
Define General Task form contract

EXECUTION_MODE:
manual

REQUIRED_ORGANS:
Astronomicon, Administratum

SCOPE:
Зафиксировать минимальную форму General Task, которую Owner может заполнить руками.

EXPECTED_OUTPUT:
SOURCE_TEXT.md and parsed GENERAL_TASK.json.

SERVITOR ROUTE:
1. Open this dispatch file.
2. Open LOCAL_TASKS/LTASK-001/LOCAL_TASK.json.
3. Read scope, expected_output, execution_mode, required_organs.
4. Go to Doctrinarium for law/preflight check.
5. Go to Officio Agentis for role/work settings.
6. Go to Administratum for context/readiness and relevant history.
7. If Administratum says READY_TO_EXECUTE, continue to assigned organs.
8. If missing context/tool/input, stop and report missing requirements.

STATUS:
DISPATCH_TEST_CREATED