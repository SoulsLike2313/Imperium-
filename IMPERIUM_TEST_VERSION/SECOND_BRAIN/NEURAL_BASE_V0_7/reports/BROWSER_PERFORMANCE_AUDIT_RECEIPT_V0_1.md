# BROWSER PERFORMANCE AUDIT RECEIPT V0.1

- task_id: `TASK-SECOND-BRAIN-V07-BROWSER-PERFORMANCE-AUDIT-RUNNER`
- generated_at: `2026-05-17T02:25:28+00:00`
- current_head: `94cf6b7fb773ea967f47e087337c5461aa9a017a`
- verdict: `BLOCKED`
- audit_target: `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.html`
- browser_automation_status: `BROWSER_AUTOMATION_AVAILABLE`
- browser_audit_status: `BROWSER_AUDIT_RUN`
- fps_status: `FPS_MEASURED`
- raw_trace_status: `NOT_CREATED`

## Static Browser Precheck
- v06_html_exists: `True`
- v06_css_exists: `True`
- v06_js_exists: `True`
- approx_html_tag_count: `240`
- svg_related_string_count: `15`
- raw_visual_asset_total_bytes_estimate: `0`

## Budget Comparison
- load_to_domcontentloaded_ms: value=`26.9` target=`1800` blocker=`3000` status=`PASS`
- load_to_load_event_ms: value=`28.0` target=`1800` blocker=`3000` status=`PASS`
- dom_nodes: value=`240.0` target=`2200` blocker=`3200` status=`PASS`
- svg_elements: value=`107.0` target=`900` blocker=`1500` status=`PASS`
- average_fps: value=`60.42` target=`55` blocker=`50` status=`PASS`
- fps_1pct_low: value=`59.524` target=`45` blocker=`35` status=`PASS`
- console_errors: value=`2.0` target=`0.0` blocker=`0.0` status=`BLOCKED`
- failed_requests: value=`2.0` target=`0.0` blocker=`0.0` status=`BLOCKED`

## Console / Requests
- console_error_count: `2`
- failed_request_count: `2`
- console_error_samples:
  - Failed to load resource: net::ERR_FILE_NOT_FOUND
  - Failed to load resource: net::ERR_FILE_NOT_FOUND
- failed_request_samples:
  - GET file:///E:/neural_map_v0_6.css :: net::ERR_FILE_NOT_FOUND
  - GET file:///E:/neural_map_v0_6.js :: net::ERR_FILE_NOT_FOUND

## Limitations
- Runner is read-only for source/runtime files and writes only compact reports.
- No dependency install or browser download is performed.
- FPS is reported only when frame pacing measurement actually succeeded.
- Live server startup is intentionally skipped when it risks runtime side effects.
