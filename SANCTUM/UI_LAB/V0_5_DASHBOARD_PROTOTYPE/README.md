# SANCTUM Dashboard v0.5 Working Prototype

## Purpose
This UI_LAB prototype is the first serious operator dashboard slice after v0.4.
It is isolated from baseline runtime and does not replace `SANCTUM/sanctum_v0_29_qt.py`.

## Open Locally
1. Run data build:
   - `python3 TOOLS/build_sanctum_dashboard_v0_5_data.py`
2. Open:
   - `SANCTUM/UI_LAB/V0_5_DASHBOARD_PROTOTYPE/index.html`

## Data Sources
The dashboard reads `dashboard_data.json`, generated from real repo registries/reports:
- bundle route registry
- sanctum action registry + action test matrix
- asset manifest + interpretation cards
- current truth + step reports
- first four organs readiness registry

## Implemented Buttons
- Toggle Orbit Animation
- Show All Organs
- Show Guide Organs
- Show Warnings
- Filter Assets: Accepted/Candidate/Rejected
- Clear Asset Filters
- Show Route Policy
- Show Action Registry
- Show Reports
- Compact Mode Toggle
- Clear Console

All listed buttons have deterministic in-UI behavior (filtering, panel focus, or visible console logs).

## Disabled/Planned
- Real backend bundle fetch bridge
- Dangerous backend action execution
- Any gate mutation path

## Prototype Boundaries
- `READY_FOR_AGENT` stays false.
- Act 5 execution remains blocked.
- Asset interpretation remains proposal until Owner confirmation.
- This prototype is not production-ready.
