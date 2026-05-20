# MECHANICUS_PANEL_SLICE_V0_1

Isolated visual lab slice for:
`SANCTUM.RIGHT_CONTEXT_DOCK.MECHANICUS_PANEL`

## Scope
- Root: `IMPERIUM_NEW_GENERATION/SANCTUM_VISUAL_FOUNDRY/LABS/MECHANICUS_PANEL_SLICE_V0_1/`
- Stack: plain HTML/CSS/JS only
- Mode: static/mock-backed demo with explicit truth boundaries

## What Is Implemented
- Header / Identity zone
- Current Activity / Work zone
- Command / Operator Palette zone
- Tool Registry / Capability Overview zone
- Footer / Evidence / Mission Focus zone

## State Behavior
Small local state logic in `app.js`:
- `idle`
- `active`
- `warn`
- `blocked`
- `unknown`

Includes reduced-motion toggle and keeps uncertainty visible.

## Truth Discipline
- `UNKNOWN`, `STUB`, and `LOCKED` lanes are explicit.
- No fake `CONNECTED` / `PASS` / `READY` claims.
- Registry rows are intentionally bounded snapshot rows and marked as partial.

## Grounding Inputs
- Visual shape/style grounded by asset references (`01_TARGET...` primary)
- Semantics grounded by current Sanctum/live-console references (`02_CURRENT...`, `03_CURRENT...`)
- Topology/truth anchoring from V0.2R visual registry/truth map/unit files

## Evidence
- Screenshots in `SCREENSHOTS/`
- Reports in `REPORTS/`
- Final receipt in `RECEIPTS/FINAL_RECEIPT.json`

## Open Locally
Open `index.html` in browser (no build step required).
