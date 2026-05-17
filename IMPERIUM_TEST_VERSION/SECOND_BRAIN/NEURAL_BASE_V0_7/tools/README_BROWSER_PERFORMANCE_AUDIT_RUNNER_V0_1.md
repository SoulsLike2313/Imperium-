# README BROWSER PERFORMANCE AUDIT RUNNER V0.1

## What This Runner Does
- Creates a compact browser performance receipt for Second Brain V0.7 discipline.
- Reads performance budget and report-output budget gates.
- Performs static browser precheck (V0.6 target availability, sizes, effect counters).
- Detects browser automation availability (Python Playwright / Node Playwright) without installing anything.
- Runs browser audit only when safe static target + automation are available.

## What This Runner Does Not Do
- Does not modify runtime/app/server/js/css/html behavior.
- Does not optimize performance.
- Does not install dependencies or download browsers.
- Does not create or commit raw traces, HAR, screenshots, or zip artifacts.
- Does not claim FPS unless FPS was actually measured.

## How To Run
```powershell
python IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/tools/browser_performance_audit_runner_v0_1.py
```

Optional output override:
```powershell
python IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/tools/browser_performance_audit_runner_v0_1.py --json-out <path.json> --md-out <path.md>
```

## When Browser Audit Is Skipped
- No safe static target detected (runner avoids live server side effects).
- Browser automation backend not available.
- Playwright backend detected but runtime launch fails in current environment.

## FPS Truth Rule
- `FPS_MEASURED` only when frame timing loop produced measurable data.
- Otherwise status is `FPS_NOT_MEASURED`, and PASS is not granted on fake FPS.

## Report Output Budget Rule
- Receipt outputs are compact and checked against `REPORT_OUTPUT_BUDGET_V0_1.json`.
- If JSON/MD exceeds configured line or size budget, runner stops with error.
