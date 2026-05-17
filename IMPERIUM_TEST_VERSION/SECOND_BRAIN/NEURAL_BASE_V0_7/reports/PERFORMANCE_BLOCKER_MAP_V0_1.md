# PERFORMANCE BLOCKER MAP V0.1

## Categories
- missing browser/FPS evidence
- static source complexity risks
- CSS animation/effect density risk
- DOM/SVG risk
- asset budget risk
- console/network not measured risk
- fake-green performance claim risk

## Risk Items
- FPS evidence missing: browser audit was not run.
- Asset budget blocker: compressed visual assets exceed blocker threshold.
- CSS effect density risk: keyframes/animations/shadows/gradients are non-trivial and need runtime confirmation.
- Console/network runtime gap: not measured in static audit.
- Fake-green risk: performance PASS wording is prohibited without runtime evidence.

## Required Future Evidence
- Browser FPS and frame-time receipts.
- Runtime load timing receipt.
- Console/network error receipts under runtime execution.
- Updated baseline after controlled mitigation task.

## Recommended Gate Before Optimization
- `TASK-SECOND-BRAIN-V07-VISUAL-FAKE-GREEN-SCANNER`
