# HOW_TO_KEEP_TRUTH_WHEN_ADDING_MODULES

## Purpose
This guide defines the minimum steps to preserve strict frontend/backend truth parity when adding a new module or zone.

## 1) Adding a new zone
1. Add zone metadata to `registry/zone_registry_v0_5.json`.
2. Add `truth_matrix/zone_<zone_id>_truth.json` with source patterns and pass/fail logic.
3. Add layout entry to `registry/layout_config.json`.
4. Add bindings to `TRUTH_LOCK_V0_1/contracts/ui_binding_manifest_v0_2.json`.
5. Rebuild snapshot and verify zone appears in `/api/snapshot` and in UI.

## 2) Binding UI to backend
1. For every non-decorative UI value, define selector + API field + backend source path.
2. Record that chain in `ui_binding_manifest_v0_2.json`.
3. If source is unavailable, show explicit state (`MISSING`, `STALE`, `ERROR`, `UNAVAILABLE`).

## 3) What not to hardcode
- Do not hardcode counters, health, status counts, timestamps, or receipt/export counts.
- Static labels are allowed only for mode disclaimers.

## 4) Adding a truth source
1. Register source in `backend_truth_source_registry_v0_1.json`.
2. Define parser type and freshness policy.
3. Define consumers and mutation policy.
4. If source is mutating, ensure receipt policy is documented and implemented.

## 5) Adding telemetry
1. Expose telemetry under `/api/status.telemetry`.
2. If telemetry is unavailable, set value to `NOT_IMPLEMENTED`.
3. Never fake unavailable telemetry as zero.

## 6) Adding receipts
- Any mutating action must produce receipt evidence.
- Keep receipt paths parsable and countable by `/api/receipts`.

## 7) Running strict parity gate
1. `py -3.12 .\IMPERIUM_TEST_VERSION\SECOND_BRAIN\NEURAL_BASE_V0_5\tools\snapshot_builder_v0_5.py`
2. `py -3.12 .\IMPERIUM_TEST_VERSION\SECOND_BRAIN\NEURAL_BASE_V0_5\tools\check_neural_base_v0_5.py`
3. `py -3.12 .\IMPERIUM_TEST_VERSION\SECOND_BRAIN\NEURAL_BASE_V0_5\tools\playwright_v0_5_truth_lock.py`
4. `py -3.12 .\IMPERIUM_TEST_VERSION\SECOND_BRAIN\NEURAL_BASE_V0_5\tools\check_frontback_truth_parity_v0_2.py`

## 8) Required honest states
When data is incomplete, the UI must explicitly show one of:
- `PARTIAL`
- `MISSING`
- `STALE`
- `DISABLED`
- `ERROR`

## 9) Acceptance outcomes
- `ACCEPT_STRICT`: all strict parity conditions pass.
- `OWNER_REVIEW_REQUIRED`: parity not strict but bounded and documented.
- `BLOCK`: unresolved placeholder, hardcoded non-decorative value, missing truth binding, or unsafe mutating action.
