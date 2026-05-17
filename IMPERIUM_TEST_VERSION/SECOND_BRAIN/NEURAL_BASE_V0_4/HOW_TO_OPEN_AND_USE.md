# How To Open And Use

## What to open
Primary operator page:
- `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_4/app/neural_base_v0_4.html`

## Recommended local server command
From `E:\IMPERIUM\IMPERIUM_TEST_VERSION\SECOND_BRAIN\NEURAL_BASE_V0_4\app`:

```powershell
python -m http.server 8787
```

Then open:
- `http://localhost:8787/neural_base_v0_4.html`

Reason: browser `file://` mode may block JSON fetch from `../reports/neural_base_snapshot_v0_4.json`.

## Panel guide
- `Neural Shell`: visual core and node/strand legend.
- `Snapshot Status`: current snapshot metadata and scope state.
- `Feature Registry`: registered modules with zone, truth, and limitation states.
- `Truth Matrix`: mapping from UI elements to backend source patterns.
- `Action Registry`: allowed actions and safety class.
- `Evidence Channels`: source presence and evidence metrics.

## What is real now
- Registry contracts are real files.
- Snapshot builder reads real paths and writes real JSON.
- Checker validates required files, JSON integrity, feature coverage, action safety, and scope policy.
- UI is real static operator prototype.

## What is disabled or constrained
- Mutating future actions are declared as `MUTATING_DISABLED`.
- Local LLM and external agent execution remain not integrated in this base.
- Some legacy module paths remain partial by design and are reported as such.

## How future features attach
1. Add a module manifest in `features/<module_id>.feature.json`.
2. Add/update the feature entry in `registry/neural_feature_registry.json`.
3. Add truth bindings in `registry/neural_truth_matrix.json`.
4. Add action definitions in `registry/neural_action_registry.json`.
5. Rebuild snapshot:
   - `python ..\\tools\\build_neural_base_snapshot_v0_4.py`
6. Re-run checker:
   - `python ..\\tools\\check_neural_base_v0_4.py`

## Next practical step
- Add a new module that binds Strategic Capability Foundation into this registry model using the same contracts.

