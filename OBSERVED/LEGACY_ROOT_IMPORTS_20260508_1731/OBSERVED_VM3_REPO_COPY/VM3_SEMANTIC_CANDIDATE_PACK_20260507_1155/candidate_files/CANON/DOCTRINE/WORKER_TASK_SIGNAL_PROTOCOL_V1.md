# WORKER_TASK_SIGNAL_PROTOCOL_V1

Status: candidate protocol.

## Purpose

Lightweight worker heartbeat/progress signaling for SSH-readable operational visibility.

## Signal types

- TASK_STARTED
- PHASE_STARTED
- PHASE_COMPLETED
- BLOCKED
- LIMIT_NEAR
- BUNDLE_READY
- HANDOFF_READY
- TASK_DONE

## Required envelope

Each signal MUST contain:

- schema_version
- contour_id
- host
- user
- repo_path
- task_id_or_step_name
- phase
- status
- timestamp_utc
- artifact_path (nullable)
- bundle_path (nullable)
- next_expected_action
- safe_for_pc_read
- not_truth_center
- owner_attention_required
- limitation_notes

## Operational rules

1. Write signal JSON to `runtime/contours/signals/<contour_id>/`.
2. Update `LATEST_SIGNAL.json` atomically after each signal write.
3. Signals are operational heartbeat/evidence only; not canon truth.
4. If no fresh signal is available, PC must display `unknown`.
5. No daemon requirement.

## Non-authority

- no canon mutation
- no admission
- no push/autosync
- no truth-center reassignment
