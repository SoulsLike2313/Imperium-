# ACTIVE STATE V0.1

This folder answers one question: what is active right now?

## Stage 0 truth

- current status: `NO_ACTIVE_GENERAL_TASK`
- `active_general_task`: `null`
- `active_task`: `null`
- `active_stage`: `null`
- `active_run`: `null`

Null active pointers are intentional clean-entry state, not missing data.
Any dashboard/viewer must show `NO_ACTIVE_GENERAL_TASK` and must not show fake green.
Future intake/registration scripts must update this active-state set consistently.

Operational bundles/runtime live under E:\\IMPERIUM_CONTEXT\\LOCAL; repo-local OUTBOX/.imperium_runtime are not active working zones.

