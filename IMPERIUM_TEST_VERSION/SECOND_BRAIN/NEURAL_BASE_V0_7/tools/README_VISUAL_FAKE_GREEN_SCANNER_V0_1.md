# README VISUAL FAKE GREEN SCANNER V0.1

## What This Scanner Does
- Scans configured read-only Second Brain V0.6/V0.7 text targets for suspicious fake-green patterns.
- Classifies findings as `HARD_BLOCKER`, `WARNING`, `REVIEW_REQUIRED`, `ALLOWED_CONTEXT`, `NOT_APPLICABLE`.
- Produces:
  - `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/VISUAL_FAKE_GREEN_SCAN_V0_1.json`
  - `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/VISUAL_FAKE_GREEN_SCAN_V0_1.md`

## What This Scanner Does Not Do
- Does not modify runtime/app/server/js/css/html implementation.
- Does not optimize performance.
- Does not run browser FPS measurement.
- Does not replace backend truth-parity audit.

## How To Run
```powershell
python IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/tools/visual_fake_green_scanner_v0_1.py
```

Optional custom output paths:
```powershell
python IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/tools/visual_fake_green_scanner_v0_1.py --json-out <path.json> --md-out <path.md>
```

## Verdict Interpretation
- `PASS`: no hard blockers and no high-risk warnings; expected paths were readable.
- `WARN`: suspicious or ambiguous wording found, or some expected paths were not readable.
- `BLOCKED`: confirmed fake-green risk found (forbidden performance claim/readiness lie/screenshot-truth claim).
- `REVIEW_REQUIRED`: context is ambiguous and needs manual decision.

## Important Boundary
- A `PASS` here is only for fake-green text/static-risk scanning.
- Browser performance audit and truth-parity audit are still required for runtime claims.
