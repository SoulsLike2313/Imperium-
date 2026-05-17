# Performance Optimization Plan V0.1

## Current Truth Summary
- Full runtime route is valid: HTTP 200, HTML/CSS/JS loaded, API checks pass, failed required requests = 0, console errors = 0.
- FPS evidence is valid but blocked: average FPS `33.085`, 1% low FPS `11.976`.
- Assets are not primary blocker: `FILE_ASSET_PRESSURE_NOT_PRIMARY`, estimated payload `0.1591` MB.

## Why Current FPS Is Unacceptable
- Baseline is truthful and still below budget, so lag is real and must be addressed.
- Owner performance intent requires smooth operation on available hardware.

## Primary Pressure Hypothesis
- Strong CSS/JS pressure signals: many keyframes/animations, heavy shadows/gradients/filters, rAF/timer loops, DOM churn.

## Optimization Principle
- "Optimization must restore FPS without breaking route truth, API truth, visual identity, or Owner observability."

## Safe Implementation Levels
- L1: performance mode and motion throttle.
- L2: CSS effect pressure reduction.
- L3: JS frame-loop and DOM churn reduction.
- L4 (future): LOD visual architecture.

## First Recommended Implementation Slice
- `PERFORMANCE_MODE_AND_MOTION_THROTTLE` as reversible first step.
- Preserve truth overlays and semantic observability; do not remove meaningful UI behavior.

## Validation Plan
- Must keep route/API truth gates PASS.
- FPS acceptance targets: average >=50 (target 55), 1% low >=35 (target 45).
- Repeat bounded runs to reduce measurement noise.

## Stop Conditions
- Any route/API truth break.
- Any visual identity collapse.
- Any interaction/state regression.
- Any fake gain achieved by disabling meaningful UI behavior.

## Visual Construction Admission
- Still blocked until FPS acceptance criteria are met with truth gates intact.
