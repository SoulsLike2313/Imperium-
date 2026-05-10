# PC_WORKER_SIGNAL_READ_MODEL_V1

Status: candidate operational model.

## PC role in signal flow

- PC reads worker signals by SSH/SCP or copied artifacts.
- Signal is heartbeat/evidence only.
- Signal is never canon truth and never admission proof by itself.

## Reading rules

1. Read `runtime/contours/signals/<contour>/LATEST_SIGNAL.json`.
2. Validate schema and required fields.
3. Mark status `unknown` if signal is missing or stale.
4. If `bundle_path` is present, fetch bundle and record receipt.
5. Display stale age and next expected action.

## Stale policy

- default stale threshold: 900 seconds
- if stale, UI must show `unknown` and not fake progress

## Safety

- no PC write to canon
- no PC writer role promotion
- no truth-center reassignment
