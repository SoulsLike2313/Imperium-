# README BROWSER PERFORMANCE AUDIT RUNNER V0.1

## What This Runner Does
- Builds a compact browser performance receipt for Second Brain V0.7 discipline.
- Reads `PERFORMANCE_BUDGET_V0_1.json` and `REPORT_OUTPUT_BUDGET_V0_1.json`.
- Runs static precheck for V0.6 target files and front-end complexity indicators.
- Prefers `STATIC_READ_ONLY_LOCAL_SERVER` mode (`127.0.0.1` + ephemeral port) for correct asset path resolution.
- Validates required asset load (`neural_map_v0_6.css` and `neural_map_v0_6.js`) before FPS acceptance.
- Separates static frontend evidence from full runtime evidence.

## What This Runner Does Not Do
- Does not edit runtime/app/server/js/css/html sources.
- Does not optimize performance.
- Does not install dependencies or download browsers.
- Does not create/commit raw traces, HAR, screenshots, webm, or zip artifacts.
- Does not claim full runtime performance PASS from static-only audit.
- Does not accept FPS as UI truth when required CSS/JS failed to load.

## How To Run
```powershell
python IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/tools/browser_performance_audit_runner_v0_1.py
```

Optional output override:
```powershell
python IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/tools/browser_performance_audit_runner_v0_1.py --json-out <path.json> --md-out <path.md>
```

Optional target mode:
```powershell
python IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/tools/browser_performance_audit_runner_v0_1.py --target-mode auto
python IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/tools/browser_performance_audit_runner_v0_1.py --target-mode static_server
python IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/tools/browser_performance_audit_runner_v0_1.py --target-mode file
```

## Target Mode and Asset Truth
- Default `auto` mode uses local static server first, then `file://` fallback.
- Required CSS/JS load status is explicitly recorded in receipt.
- If required assets fail, `fps_acceptance_status` becomes `FPS_INVALID_FOR_UI_PERFORMANCE_ACCEPTANCE`.
- If required assets load but runtime/API path is not audited, FPS is labeled `FPS_MEASURED_VALID_FOR_STATIC_FRONTEND_ONLY`.

## When Browser Audit Is Skipped
- No safe target detected.
- Browser automation backend unavailable.
- Playwright backend detected but launch/navigation failed.

## Report Output Budget Rule
- JSON/MD outputs are compact and budget-checked.
- Exceeding configured line/size limits causes runner stop.
