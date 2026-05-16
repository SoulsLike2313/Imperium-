# Visual Regression Diagnosis (V0.2)

## Symptoms observed
- Neural canvas looked dark/empty and operator interaction became unreliable.
- 12 zones were not reliably visible in broken state capture (`00_initial_broken_or_before_if_available.png`).
- Task Intake entry was not usable when rendering pipeline crashed.

## Root causes
1. **Critical runtime error in canvas strand rendering**
   - File: `app/neural_map_v0_6.js`
   - Fault: condition used undefined variable `zone` inside strand loop:
     - `if (strandColorShadow !== "transparent" && zone && zone.health !== "MISSING")`
   - Effect: `ReferenceError: zone is not defined` interrupted `renderNeuralCanvas()`, which also prevented normal panel refresh path after `fullRefresh()`.

2. **Readability pressure from low-contrast visual details (secondary)**
   - File: `app/neural_map_v0_6.css`
   - Zone labels and strand contrast were too close to background in dark scenes.
   - Effect: even when data existed, operator readability was degraded.

## Repairs applied
- Replaced faulty condition with source-target health validation:
  - `if (strandColorShadow !== "transparent" && fromHealth !== "MISSING" && toHealth !== "MISSING")`
- Increased strand visibility and zone label readability:
  - brighter strand alpha/shadow layers;
  - label backing plate in SVG render;
  - larger, stronger label typography and softer vignette/grid tuning.

## Backend truth impact
- Backend truth contracts and API endpoints were **not bypassed**.
- Snapshot/status/counters remained backend-driven.
- Task Intake Corridor remained rule-based and receipt-generating.
- Side effects from proof interaction were runtime writes in `SECOND_BRAIN/MEMORY_ZONES` and receipts/task_packages, consistent with intended corridor behavior.

## Evidence
- Broken-state evidence: `before_diagnostics.json`, screenshot `00_initial_broken_or_before_if_available.png`.
- Post-fix evidence: `after_fix_quick_diag.json`, `playwright_visual_repair_report.json`, screenshots `01..09`.
