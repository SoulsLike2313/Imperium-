# Asset Budget Classification V0.1

## Baseline Truth
- task_id: `TASK-SECOND-BRAIN-V07-ASSET-BUDGET-CLASSIFICATION`
- baseline performance remains blocked by FPS despite valid runtime route and successful HTML/CSS/JS/API loading.

## Source Files Inspected
- html: `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.html`
- css: `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css`
- js: `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.js`

## Route Required File Sizes
- html_bytes: `15783`
- css_bytes: `56312`
- js_bytes: `94754`
- route_required_total_kb: `162.94`

## Referenced Assets Summary
- total_references_detected: `3`
- resolvable_existing_local_references: `2`
- missing_or_unresolved_local_references: `1`
- images_or_svg_references: `0`
- font_references: `0`
- video_references: `0`
- audio_references: `0`

## Estimated Payload vs Budget
- estimated_payload_mb: `0.1591`
- compressed_visual_assets_target_mb: `4.0`
- compressed_visual_assets_blocker_mb: `8.0`
- estimated_payload_vs_budget_status: `PASS`

## Verdict
- asset_pressure_verdict: `FILE_ASSET_PRESSURE_NOT_PRIMARY`
- assessment scope: diagnostic classification only, no optimization and no source edits.

## Non-File Complexity Warning
- source_map_strong_categories: `heavy_visual_effects, js_main_thread_work`
- css_keyframes: `37`
- css_animation_declarations: `45`
- css_filter_declarations: `11`
- js_requestAnimationFrame: `2`
- js_dom_append_count: `58`
- js_style_write_count: `8`

## Unknowns
- exact runtime transfer/compression/decode costs are not measured here;
- dynamic/runtime-only references may exist beyond static source scan.

## Missing Referenced Assets (sample)
- `e.g. Python 3.12, no Node.js` from `js` -> missing at `E:/IMPERIUM/IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/e.g. Python 3.12, no Node.js`

## Next Recommended Task
- `TASK-SECOND-BRAIN-V07-PERFORMANCE-OPTIMIZATION-PLAN-V0_1`

## Limitations
- This is metadata/source classification only; no browser/runtime execution.
- Payload is a local estimated payload, not actual compressed transfer bytes.
- Some references may be runtime-generated or API-fed and cannot be resolved statically.
- Exact root cause cannot be proven from asset metadata alone.
