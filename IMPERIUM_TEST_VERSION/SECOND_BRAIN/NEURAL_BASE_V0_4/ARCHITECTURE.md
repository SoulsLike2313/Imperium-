# Architecture

## Intent
Create a stable neural operator base where each feature is a registered module with explicit truth, safety, and evidence contracts.

## Architecture Layers
1. Neural Shell
- Visual command shell with central brain and zone panels.
- Presents modules, links, blockers, and evidence states.
- Reads generated snapshot data only; no hidden runtime assumptions.

2. Feature Module Layer
- Each module has a manifest (`features/*.feature.json`) and one shared entry in `registry/neural_feature_registry.json`.
- Module fields include: id, title, scope, data sources, checker paths, actions, and integration limits.

3. Backend Truth Layer
- `registry/neural_truth_matrix.json` maps each UI node/strand/panel state to concrete files or runtime artifacts.
- Every displayed state must point to a real path family and a verification note.

4. Action Safety Layer
- `registry/neural_action_registry.json` is the only action definition source.
- Action types: `READ_ONLY`, `CHECK`, `EXPORT`, `MUTATING_DISABLED`.
- Mutating actions are disabled unless explicitly owner-gated and safely implemented.

5. Evidence Layer
- Receipts, reports, and checker outputs are linked in module metadata and snapshot output.
- Green states require proof references and cannot be cosmetic.

## Data Flow
1. Registry files define structure and policies.
2. Snapshot builder reads registry and scans known runtime/report folders.
3. Snapshot JSON is written to `reports/neural_base_snapshot_v0_4.json`.
4. UI reads snapshot JSON and renders module states.
5. Checker validates contracts, scope safety, and snapshot integrity.

## Scope Safety
- All V0.4 assets live under `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_4`.
- Checker audits changed paths from git and fails on paths outside `IMPERIUM_TEST_VERSION`.

