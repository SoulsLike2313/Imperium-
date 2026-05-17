# Performance Optimization Slice Plan V0.1

## SLICE_1_PERFORMANCE_MODE_AND_MOTION_THROTTLE
- purpose: Safely reduce animation/frame pressure via performance mode and motion throttle controls.
- expected impact: Immediate uplift to frame stability and 1% low FPS with minimal visual regression risk.
- risk: Fake toggle risk if controls do not actually reduce active animations/timers.
- required files (next task): `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css`, `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.js`
- pass criteria:
  - Performance mode reduces active animation density measurably.
  - Route/API truth remains intact (200, assets loaded, API checks pass).
  - Average FPS and 1% low FPS move upward vs baseline.
- rollback condition: If UI truth overlays or click/state behavior break, revert throttle hooks immediately.
- evidence required:
  - Regenerated full runtime receipt
  - Before/after FPS comparison
  - Truth overlay and API pass evidence

## SLICE_2_CSS_EFFECT_PRESSURE_REDUCTION
- purpose: Reduce heavy shadows/filters/gradients/keyframe cost while preserving visual identity.
- expected impact: Lower paint/compositor cost and improved smoothness under interaction.
- risk: Visual identity can degrade if effects are removed indiscriminately.
- required files (next task): `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css`
- pass criteria:
  - High-cost effect density reduced with style identity preserved.
  - No collapse of semantic zone readability or hierarchy.
  - FPS metrics improve or at minimum do not regress after Slice 1 gains.
- rollback condition: If visual identity collapses or readability worsens materially, restore prior effect set.
- evidence required:
  - Diff-level effect inventory
  - FPS comparison after Slice 2
  - Owner-facing visual integrity checklist

## SLICE_3_JS_FRAME_LOOP_AND_DOM_CHURN_REDUCTION
- purpose: Reduce main-thread pressure from timers, rAF loops, innerHTML churn, and frequent DOM append patterns.
- expected impact: Better 1% low FPS, reduced frame spikes, steadier interaction latency.
- risk: State synchronization or click behavior can break if update batching is incorrect.
- required files (next task): `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.js`
- pass criteria:
  - DOM update frequency reduced without loss of truth data fidelity.
  - No regressions in panel/task/comment/link interactions.
  - FPS 1% low shows measurable gain.
- rollback condition: If any interaction/state regression appears, roll back batching changes immediately.
- evidence required:
  - Loop/timer inventory before-after
  - Interaction smoke checklist
  - Runtime receipt with FPS deltas

## SLICE_4_LOD_VISUAL_ARCHITECTURE
- purpose: Future architecture split: cinematic static layer + thin live truth overlay layer.
- expected impact: Long-term stability of FPS with preserved aesthetic richness.
- risk: Overengineering risk if introduced before slices 1-3 stabilize baseline.
- required files (next task): `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.html`, `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css`, `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.js`
- pass criteria:
  - Live truth overlay remains complete and responsive.
  - Cinematic layer cost bounded independently from live telemetry updates.
  - FPS acceptance sustained across repeated runs.
- rollback condition: If layering breaks truth observability or increases complexity without gains, defer LOD architecture.
- evidence required:
  - Layer responsibility map
  - Per-layer update cost hypothesis
  - Post-change runtime receipt trend

