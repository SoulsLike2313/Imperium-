# SANCTUM_V0_4_VISUAL_FACTORY_PROTOTYPE

## Scope
`SANCTUM/sanctum_v0_4_visual_factory_qt.py` is an experimental runtime prototype for Step 7.2.
It is not promoted as production Sanctum.

## Why v0.4 Exists
- Preserve accepted baseline `SANCTUM/sanctum_v0_29_qt.py`.
- Test visual direction grounded in Owner asset intake.
- Bind bundle panel to canonical route registry policy.

## Prototype Features
- Reads `REGISTRY/BUNDLE_ROUTE_REGISTRY.json` and prioritizes canonical VM2 bundle outbox.
- Scans bundles with dedupe (canonical-first, then mtime).
- Shows core/orbit visual grammar in a separate experimental shell.
- Loads `ASSETS/ASSET_MANIFEST.json` summary to keep evidence awareness visible.

## Safety Constraints
- No READY_FOR_AGENT promotion.
- No Act 5 execution-ready claim.
- No destructive rewrite of v0.29 baseline.
- Visual intake remains proposal-only until Owner confirmation.

## Validation
- `python3 -m py_compile SANCTUM/sanctum_v0_4_visual_factory_qt.py`
- Optional headless smoke: `python3 SANCTUM/sanctum_v0_4_visual_factory_qt.py --smoke`
- `python3 TOOLS/check_sanctum_v0_4_visual_factory_v0_1.py`
