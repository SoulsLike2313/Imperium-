# TOOLS REGISTRY UPDATE PLAN

Goal: introduce class `STAGE_COORDINATION` into the tool registry without falsely marking skeleton tools as active.

Planned tool IDs:
- STAGE_PLAN_READ
- STAGE_DEPENDENCY_CHECK
- STAGE_SIGNAL_EMIT
- STAGE_SIGNAL_ACK
- STAGE_WAIT_FOR_SIGNAL
- STAGE_GATE_DECIDE
- STAGE_HEARTBEAT_EMIT
- STAGE_COORDINATION_VIEW
- STAGE_REPAIR_REQUEST
- STAGE_STOP_WITH_REASON

Registry policy for this task:
- tool_class: STAGE_COORDINATION
- status: SKELETON_CONTRACT
- requires_task_id: true
- requires_stage_id: true
- requires_run_id: true
- requires_provenance: true
- writes_receipt: true (contract target)
- writes_ledger_event: true (contract target)
- writes_owner_report: true (contract target)
- blocked_actions: ["throne_write", "latest_logic", "fallback", "autosync", "watchers"]

Activation gate:
A tool may move from SKELETON_CONTRACT to ACTIVE_NEEDS_SPECULUM only after implementation, local tests, compile check, and registry hash verification.
