# VISUAL PERFORMANCE RECEIPT V0.1

- task_id: `TASK-SECOND-BRAIN-V07-VISUAL-PERFORMANCE-RECEIPT-RUNNER`
- generated_at: `2026-05-17T01:27:57.322498+00:00`
- current_head: `df0f8985c5cf2015dc2739dff6149d949aefa01a`
- verdict: `BLOCKED`

## Inspected Paths
- `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7`
- `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6`

## Static Audit
- status: `STATIC_AUDIT`
- html_files: `2`
- css_files: `2`
- js_files: `2`
- visual_assets: `29`
- visual_assets_total_mb: `31.515`

## Optional Browser Audit
- status: `NOT_MEASURED`
- browser_audit_status: `BROWSER_AUDIT_NOT_RUN`
- reason: Run without --browser-audit flag.

## Budget Comparison
- approx_dom_nodes_from_html_tags: value=450 target=2200 blocker=3200 status=PASS
- svg_related_strings: value=204 target=900 blocker=1500 status=PASS
- compressed_visual_assets_mb: value=31.515 target=4.0 blocker=8.0 status=BLOCKED

## Limitations
- No runtime mutation performed; static audit only by default.
- FPS and load timings cannot be claimed without executable browser probe.
- BROWSER_AUDIT_NOT_RUN is honest outcome when probe is unavailable or disabled.

## Next Recommended Action
- TASK-SECOND-BRAIN-V07-PERFORMANCE-BASELINE-INTERPRETATION
