# BROWSER PERFORMANCE AUDIT RECEIPT V0.1

- task_id: `TASK-SECOND-BRAIN-V07-BROWSER-PERFORMANCE-AUDIT-RUNNER`
- generated_at: `2026-05-17T02:45:15+00:00`
- current_head: `2cf311540229e850a0107fbec2f04b50873c7da1`
- verdict: `WARN`
- target_mode: `STATIC_READ_ONLY_LOCAL_SERVER`
- target_url: `http://127.0.0.1:64648/neural_map_v0_6.html`
- browser_automation_status: `BROWSER_AUTOMATION_AVAILABLE`
- browser_audit_status: `BROWSER_AUDIT_RUN`
- required_assets_status: `REQUIRED_ASSETS_LOADED`
- fps_status: `FPS_MEASURED`
- fps_acceptance_status: `FPS_MEASURED_VALID_FOR_STATIC_FRONTEND_ONLY`
- full_runtime_audit_status: `FULL_RUNTIME_AUDIT_NOT_RUN`
- raw_trace_status: `NOT_CREATED`

## Required Assets
- css_loaded: `True`
- js_loaded: `True`

## Static Browser Precheck
- html_exists: `True`
- css_exists: `True`
- js_exists: `True`
- approx_html_tag_count: `240`
- svg_related_string_count: `15`
- raw_visual_asset_total_bytes_estimate: `0`

## Budget Comparison
- load_to_domcontentloaded_ms: value=`64.5` target=`1800` blocker=`3000` status=`PASS`
- load_to_load_event_ms: value=`69.5` target=`1800` blocker=`3000` status=`PASS`
- dom_nodes: value=`248.0` target=`2200` blocker=`3200` status=`PASS`
- svg_elements: value=`108.0` target=`900` blocker=`1500` status=`PASS`
- average_fps: value=`59.637` target=`55` blocker=`50` status=`PASS`
- fps_1pct_low: value=`59.524` target=`45` blocker=`35` status=`PASS`
- console_errors: value=`8.0` target=`0.0` blocker=`0.0` status=`BLOCKED`
- failed_requests: value=`0.0` target=`0.0` blocker=`0.0` status=`PASS`

## Console / Requests
- console_error_count: `8`
- failed_request_count: `0`
- console_error_samples:
  - Failed to load resource: the server responded with a status of 404 (File not found)
  - Failed to load resource: the server responded with a status of 404 (File not found)
  - Failed to load resource: the server responded with a status of 404 (File not found)
  - Failed to load resource: the server responded with a status of 404 (File not found)
  - Failed to load resource: the server responded with a status of 404 (File not found)
  - Failed to load resource: the server responded with a status of 404 (File not found)
  - Failed to load resource: the server responded with a status of 404 (File not found)
  - Failed to load resource: the server responded with a status of 404 (File not found)

## Limitations
- Runner is read-only for source/runtime files and writes only compact reports.
- No dependency install or browser download is performed.
- Static frontend audit is not equal to full runtime audit.
- FPS is accepted only after required CSS/JS load validation.
- No full runtime performance PASS is claimed in static-only mode.
