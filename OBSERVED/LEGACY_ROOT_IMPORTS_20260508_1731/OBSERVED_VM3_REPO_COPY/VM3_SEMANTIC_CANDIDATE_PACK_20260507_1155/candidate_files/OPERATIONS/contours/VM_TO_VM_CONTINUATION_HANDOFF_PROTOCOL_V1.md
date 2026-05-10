# VM_TO_VM_CONTINUATION_HANDOFF_PROTOCOL_V1

Status: candidate protocol.

## Continuation preconditions

A target worker may continue source worker task only if all conditions are true:

1. Owner command exists.
2. Latest THRONE state is read.
3. Latest source worker bundle/artifacts are read.
4. Latest source worker signal is read.
5. Divergence check is explicit.
6. Target emits TASK_STARTED or CONTINUATION_STARTED.
7. Target records source contour and source bundle.
8. No simultaneous writes to same surfaces without explicit partition.

## Required evidence

- source_contour
- target_contour
- owner_command reference
- source_bundle path
- source_latest_signal path
- throne_head
- target_worker_head
- divergence_status
- accepted_scope
- forbidden_scope
- continuation_task_id

## Stop conditions

- unresolved divergence
- missing owner command
- missing source bundle/signal
- stale target worker copy not aligned with THRONE
