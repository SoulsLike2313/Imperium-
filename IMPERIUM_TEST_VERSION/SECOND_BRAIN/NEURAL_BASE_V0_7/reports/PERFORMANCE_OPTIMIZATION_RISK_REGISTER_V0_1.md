# Performance Optimization Risk Register V0.1

## R1_VISUAL_IDENTITY_DEGRADED
- risk: Visual identity degraded too much during performance edits.
- mitigation: Use bounded effect reductions and preserve zone semantics/colors.
- rollback condition: Revert effect changes if identity/readability drops below Owner acceptance.
- stop condition: Stop slice if identity collapse is observed.

## R2_FAKE_FPS_GAIN
- risk: FPS improves only by disabling meaningful UI behavior.
- mitigation: Require truth overlay/API/interaction acceptance checks with FPS checks.
- rollback condition: Rollback any change that removes essential observability.
- stop condition: Stop on any attempt to achieve FPS by making UI empty/useless.

## R3_ROUTE_API_TRUTH_BREAK
- risk: Route or API truth breaks while optimizing front-end pressure.
- mitigation: Hard gate on 200 + HTML/CSS/JS/API pass + failed requests = 0.
- rollback condition: Immediate rollback on route/API regression.
- stop condition: Stop if required requests fail or API checks fail.

## R4_JS_STATE_BREAK
- risk: JS state/click behavior breaks after loop/throttle refactor.
- mitigation: Small reversible edits with explicit interaction smoke checklist.
- rollback condition: Rollback batch/timer changes on behavior regression.
- stop condition: Stop slice if interaction reliability regresses.

## R5_FAKE_PERF_TOGGLE
- risk: Reduced-motion/performance mode toggle exists but does not reduce real workload.
- mitigation: Measure active animation/timer counts before and after mode toggle.
- rollback condition: Remove/redo toggle implementation if no measurable effect.
- stop condition: Stop acceptance if toggle effect is non-functional.

## R6_MEASUREMENT_NOISE
- risk: Single-run measurement noise misleads optimization decisions.
- mitigation: Use repeated runs and median-oriented interpretation.
- rollback condition: Defer conclusions if results fluctuate without stable trend.
- stop condition: Stop claiming gains without repeated evidence.

## R7_NO_IMPROVEMENT_AFTER_SLICE
- risk: No measurable improvement after slice implementation.
- mitigation: Predefine slice hypotheses and escalate to next slice only with evidence.
- rollback condition: Rollback low-value edits and prioritize next hypothesis slice.
- stop condition: Stop broad edits if slice yields no improvement and root cause remains unknown.

