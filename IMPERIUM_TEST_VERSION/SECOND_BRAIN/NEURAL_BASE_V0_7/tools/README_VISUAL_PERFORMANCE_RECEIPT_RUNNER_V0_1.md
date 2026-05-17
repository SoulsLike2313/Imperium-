# README VISUAL PERFORMANCE RECEIPT RUNNER V0.1

## What The Runner Does
- Reads `VISUAL_SYSTEM/PERFORMANCE_BUDGET_V0_1.json`.
- Performs static audit on V0.6 and V0.7 HTML/CSS/JS and visual asset files.
- Computes evidence metrics (size counts, CSS effect counts, approximate DOM tags, SVG string counts).
- Produces:
  - `reports/VISUAL_PERFORMANCE_RECEIPT_V0_1.json`
  - `reports/VISUAL_PERFORMANCE_RECEIPT_V0_1.md`

## What The Runner Does Not Do
- Does not edit runtime/app/server files.
- Does not optimize performance.
- Does not change CSS/JS/HTML.
- Does not fake FPS values when browser measurement is unavailable.

## How To Run
```powershell
py -3 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/tools/visual_performance_receipt_runner_v0_1.py
```

Optional outputs:
```powershell
py -3 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/tools/visual_performance_receipt_runner_v0_1.py --json-out IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/VISUAL_PERFORMANCE_RECEIPT_V0_1.json --md-out IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/VISUAL_PERFORMANCE_RECEIPT_V0_1.md
```

## Verdict Meaning
- `PASS`: static and optional browser evidence satisfy current checks.
- `WARN`: measurable warnings exist but not hard blockers.
- `BLOCKED`: one or more blocker thresholds are exceeded.
- `NOT_MEASURED`: static audit completed but browser FPS/load evidence is unavailable.

## Why FPS Cannot Be Claimed Without Browser Audit
FPS and runtime frame timing require executable browser instrumentation. Static source inspection alone cannot produce honest FPS evidence.
