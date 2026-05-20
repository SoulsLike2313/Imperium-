# MECHANICUS_PANEL_SLICE_V0_1 (Enhanced to V0_2)

Isolated visual lab slice for:
`SANCTUM.RIGHT_CONTEXT_DOCK.MECHANICUS_PANEL`

## Current Stage
- Base implementation: V0_1
- Enhancement pass: V0_2 neuro-forge animation pressure pass
- Mode: static/mock-safe UI with explicit truth boundaries

## Scope
- Root: `IMPERIUM_NEW_GENERATION/SANCTUM_VISUAL_FOUNDRY/LABS/MECHANICUS_PANEL_SLICE_V0_1/`
- Stack: plain HTML/CSS/JS only
- No external CDN or framework runtime dependency

## What Was Strengthened in V0_2
1. Shell form moved closer to target reference language.
2. New neuro-memory field introduced as panel identity layer.
3. Ambient life animation system added (cosmetic-only):
   - edge breathing glow
   - scanline drift
   - sigil pulse
   - neural lattice flow
   - particle drift
4. Command zone received stronger terminal-lane hierarchy.
5. Work zone and footer styling density increased while preserving readability.

## Truth Discipline
- `UNKNOWN`, `STUB`, and `LOCKED` remain explicit.
- No fake `CONNECTED`/`PASS` claims were introduced by animation.
- Ambient effects are explicitly marked as atmospheric only.

## State Behavior
`app.js` includes:
- `idle`
- `active`
- `warn`
- `blocked`
- `unknown`

Reduced-motion support:
- `prefers-reduced-motion` CSS fallback
- manual UI toggle `Reduced Motion: ON/OFF`

## Evidence
- Screenshots in `SCREENSHOTS/`
- Reports in `REPORTS/`
- V0_2 receipt in `RECEIPTS/FINAL_RECEIPT_V0_2.json`

## Open Locally
Open `index.html` in browser (no build step required).
