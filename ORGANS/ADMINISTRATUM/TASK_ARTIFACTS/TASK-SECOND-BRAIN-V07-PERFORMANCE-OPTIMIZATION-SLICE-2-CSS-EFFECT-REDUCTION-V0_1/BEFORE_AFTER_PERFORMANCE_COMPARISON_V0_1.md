# Before/After Performance Comparison V0.1

- Slice1 after baseline: avg 56.368, 1pct_low 20
- Slice2 run1: avg 59.05, 1pct_low 59.524, verdict PASS_FULL_RUNTIME_BASELINE_NATIVE_ROUTE
- Slice2 run2: avg 58.517, 1pct_low 29.94, verdict WARN_FULL_RUNTIME_BASELINE_PARTIAL
- Slice2 run3: avg 58.945, 1pct_low 59.524, verdict PASS_FULL_RUNTIME_BASELINE_NATIVE_ROUTE

## Min/Median/Max
- avg FPS: 58.517 / 58.945 / 59.05
- 1pct low: 29.94 / 59.524 / 59.524

## Delta vs Slice1 after
- avg min delta: 2.149
- avg median delta: 2.577
- 1pct low min delta: 9.94
- 1pct low median delta: 39.524

## Acceptance
- conservative method: min of 3 runs
- minimum observed 1pct low: 29.94 (required >= 35)
- verdict: WARN_PARTIAL_IMPROVEMENT

