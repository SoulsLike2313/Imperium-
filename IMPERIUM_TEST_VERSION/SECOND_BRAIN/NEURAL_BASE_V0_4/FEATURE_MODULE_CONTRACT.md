# Feature Module Contract

## Contract Goal
Define a deterministic attachment path for new Second Brain neural modules.

## Required Module Fields
- `id`: unique stable module id.
- `title`: operator-visible display name.
- `status`: current maturity (`FOUNDATION`, `PARTIAL`, `WORKING`, `BLOCKED`).
- `scope_path`: primary filesystem scope for the module.
- `dashboard_paths`: operator-facing HTML paths if present.
- `data_sources`: concrete JSON/schema/runtime file sources.
- `receipts_paths`: receipt/report paths used as evidence.
- `checker_paths`: checker scripts tied to module truth.
- `visual_zone`: target neural shell panel/zone.
- `allowed_actions`: action ids from action registry.
- `current_limitations`: explicit known limits.
- `backend_truth_status`: honest truth binding status.

## Module Registration Rules
1. Module must exist in both:
   - `features/<id>.feature.json`
   - `registry/neural_feature_registry.json`
2. `allowed_actions` must reference existing ids in action registry.
3. `dashboard_paths` and `data_sources` must remain under `IMPERIUM_TEST_VERSION`.
4. Missing checker is allowed only with explicit limitation note.

## Integration Status Levels
- `TRUTH_BOUND`: has clear data and evidence bindings.
- `PARTIAL_BINDING`: some truth bindings exist, gaps documented.
- `SPEC_ONLY`: defined but not wired to runtime truth.
- `BLOCKED`: known blocker prevents reliable integration.

