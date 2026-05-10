# 15_STAGE_COORDINATION

Status: ACTIVE_LOCAL_DRYRUN_ONLY

This folder contains minimal local runtime primitives implemented in TASK-20260508-0014E.

Hard constraints:
- No VM2 contact.
- No real PC-VM2 E2E.
- No THRONE transfer.
- No watchers/background automation.
- No latest-bundle logic.

Implemented local-runtime tools:
- identity_validate.py
- artifact_manifest_write.py
- artifact_manifest_verify.py
- ledger_append.py
- ledger_replay_verify.py
- stage_signal_emit.py
- stage_signal_ack.py
- stage_signal_verify.py
- stage_gate_decide.py
- stage_wait_for_signal.py
- stage_stop_with_reason.py
- stage_coordination_view.py
- stage_repair_request.py
- inquisition_trace_audit.py

Contract-only scripts retained from skeleton:
- stage_plan_read.py
- stage_dependency_check.py
- stage_heartbeat_emit.py

Policy:
- gate never defaults to READY.
- completion evidence requires receipt and integrity checks.
- wait is bounded (poll/max-attempts/timeout), not watcher mode.
- failures must emit receipts when --receipt-out is provided.
