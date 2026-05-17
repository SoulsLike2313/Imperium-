# BROWSER AUDIT TARGET PATH BLOCKER MAP V0.1

## Blocker
- blocker_id: `BLOCKER-V07-BROWSER-TARGET-PATH-001`
- blocker_name: Required CSS/JS not loaded in current browser audit target/path mode.

## Failed CSS/JS Requests
- `GET file:///E:/neural_map_v0_6.css :: net::ERR_FILE_NOT_FOUND`
- `GET file:///E:/neural_map_v0_6.js :: net::ERR_FILE_NOT_FOUND`

## Why Current Target/Path Mode Is Insufficient
- Browser audit executed, but page dependency chain was incomplete.
- file:// target/path resolution produced missing asset requests.
- With missing CSS/JS, FPS can only reflect partial page state, not real UI performance truth.

## Safe Fix Options
- A. Safe local static server mode with no runtime side effects.
- B. Correct file:// base/path handling to resolve required assets.
- C. Runner acceptance gate: do not accept FPS if required assets did not load.

## Required Future Evidence
- Required CSS/JS requests successful.
- failed_required_requests = 0.
- Re-run audit with valid full page load.
- Then evaluate FPS/performance acceptance.

## Stop Conditions For Next Task
- STOP if fix requires runtime/app behavior change.
- STOP if raw trace artifacts would need commit by default.
- STOP if performance PASS is claimed while required assets are still missing.
