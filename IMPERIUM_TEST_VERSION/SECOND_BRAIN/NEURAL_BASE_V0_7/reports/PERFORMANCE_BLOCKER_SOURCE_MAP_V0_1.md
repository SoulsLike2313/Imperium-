# PERFORMANCE BLOCKER SOURCE MAP V0.1

## Baseline Truth Summary
- receipt_verdict: `WARN_FULL_RUNTIME_BASELINE_PARTIAL`
- performance_acceptance: `BLOCKED_BY_FPS_BUDGET`
- full_runtime_fps_average: `33.085`
- full_runtime_fps_1pct_low: `11.976`

## Source Files Inspected
- IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.html
- IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css
- IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.js

## Strongest Source Indicators
- CSS animation declarations: `45`
- CSS keyframes: `37`
- JS requestAnimationFrame: `2`
- JS style writes: `8`
- JS layout reads: `6`

## Likely Blocker Categories
- A `heavy_visual_effects` -> `EVIDENCE_STRONG` (score=248.0): CSS animation/filter/shadow/gradient indicator density.
- E `js_main_thread_work` -> `EVIDENCE_STRONG` (score=239.0): Layout reads + style writes + DOM mutations heuristics from JS source.
- C `animation_frame_pressure` -> `EVIDENCE_MODERATE` (score=85.0): rAF/timers combined with animation declarations under blocked FPS baseline.
- F `layout_reflow_pressure` -> `EVIDENCE_WEAK` (score=54.0): Reflow-related source markers (layout reads/classList/fixed-layer hints).
- G `measurement_environment_limitation` -> `EVIDENCE_WEAK` (score=0.0): Environment can influence absolute FPS but does not invalidate baseline truth.
- D `asset_weight_pressure` -> `UNKNOWN_REQUIRES_MEASUREMENT` (score=532.58): Resolvable local referenced asset size signals and missing references.
- B `excessive_dom_svg` -> `UNKNOWN_REQUIRES_MEASUREMENT` (score=250.0): DOM/SVG structural markers plus querySelectorAll usage.

## Unknowns
- Exact runtime frame-time split between CSS animation, JS update cost, and compositor behavior is not measurable from static source only.
- Asset payload runtime decode/render cost requires dedicated asset budget classification and runtime profiling.
- Environment variance contribution cannot be isolated without repeated controlled baseline runs.

## Why No Optimization Is Done Yet
- This report is a diagnostic source map only.
- Optimization remains blocked until source-map and asset classification are interpreted together.

- recommended_next_task: `TASK-SECOND-BRAIN-V07-ASSET-BUDGET-CLASSIFICATION`
- verdict: `PERFORMANCE_BLOCKER_SOURCES_LIKELY_MAPPED_NOT_CONFIRMED_AS_EXACT_ROOT_CAUSE`
