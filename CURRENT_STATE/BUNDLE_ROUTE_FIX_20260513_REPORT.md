# BUNDLE_ROUTE_FIX_20260513_REPORT

- task_id: `TASK-20260513-STEP7_1F-STEP7_2-BUNDLE-ROUTE-ASSET-REGISTRATION-SANCTUM-V0_4`
- part: Step 7.1F

## Implemented
- Added `REGISTRY/BUNDLE_ROUTE_REGISTRY.json` with canonical/legacy route truth.
- Added `DOCS/BUNDLE_ROUTE_POLICY_V0_1.md`.
- Added `schemas/bundle_route_registry_v0_1.schema.json`.
- Added checker `TOOLS/check_bundle_route_registry_v0_1.py`.
- Updated `TOOLS/build_sanctum_state_v0_1.py` to read route registry and apply canonical-first dedupe policy.

## Canonical Policy
- VM2 canonical outbox: `/home/vboxuser2/IMPERIUM_WORK/VM2_BUNDLES/`
- PC canonical inbox: `E:\IMPERIUM\INBOX\VM2_BUNDLES\`
- Legacy scan-only dirs:
  - `/home/vboxuser2/IMPERIUM_WORK/_handoff_out/`
  - `/home/vboxuser2/IMPERIUM_PRIVATE/OUTBOX/`

## Safety
- READY_FOR_AGENT remains false.
- Act 5 execution remains blocked.
- Baseline `SANCTUM/sanctum_v0_29_qt.py` was preserved.

## Validation
- `python3 TOOLS/check_bundle_route_registry_v0_1.py` => `PASS`
- `python3 TOOLS/build_sanctum_state_v0_1.py --repo-root . --out .imperium_runtime/sanctum/state/SANCTUM_STATE_V0_1.json --human` => `PASS_WITH_WARNINGS`
- Sanctum state now reports canonical bundle source first:
  `/home/vboxuser2/IMPERIUM_WORK/VM2_BUNDLES/`
