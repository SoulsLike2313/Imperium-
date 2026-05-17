# RUNTIME AUDIT STATIC ASSET ROUTE BLOCKER MAP V0.1

- blocker_id: `RT-BLOCKER-STATIC-ASSET-ROUTE-404`
- blocker_name: `Runtime browser target/static asset route mismatch`

## Failed Route and Asset Symptoms
- Browser target returned HTTP 404.
- Required CSS did not load.
- Required JS did not load.
- FPS was measured on incomplete page context.

## Likely Cause Categories
- A. wrong browser target URL
- B. server serves API but not app route
- C. isolated runtime copy missing app static files
- D. runner target path does not match server static mount
- E. required asset verification too late or wrong path

## Required Future Checks
- Runtime HTML route must return HTTP 200.
- Required CSS URL must return HTTP 200 and load.
- Required JS URL must return HTTP 200 and load.
- API checks must remain PASS.
- FPS acceptance only after all required assets are loaded.

## Safe Fix Options
- Add explicit route and static-asset preflight in runner before FPS phase.
- Align runtime browser target with server static mount.
- Emit blocker verdict early when route/assets fail.

## Forbidden Fixes
- Editing V0.6 app/server/CSS/JS/HTML in this task.
- Accepting FPS while required assets are missing.
- Screenshot-only or raw-trace compensation for missing route truth.

## Next Task Scope
- Recommended: `TASK-SECOND-BRAIN-V07-RUNTIME-AUDIT-STATIC-ASSET-ROUTE-FIX`
- Alternative: `TASK-SECOND-BRAIN-V07-RUNTIME-AUDIT-ISOLATED-COPY-FIX`

