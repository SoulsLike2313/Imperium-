# FULL RUNTIME PERFORMANCE BASELINE INTERPRETATION V0.1

- task_id: `TASK-SECOND-BRAIN-V07-FULL-RUNTIME-PERFORMANCE-BASELINE-INTERPRETATION`
- generated_at: `2026-05-17T14:40:13Z`
- current_head: `6dee3394b3a2a77f092e548ad6fd06a6c265ef1b`
- source_receipt_path: `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/FULL_RUNTIME_PERFORMANCE_AUDIT_RECEIPT_V0_1.json`
- source_route_fix_report_path: `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/RUNTIME_AUDIT_STATIC_ASSET_ROUTE_FIX_REPORT_V0_1.json`
- route_status: `RESOLVED`
- browser_target_http_status: `200`
- full_runtime_mode: `FULL_RUNTIME_NATIVE_ROUTE`
- html_loaded: `True`
- css_loaded: `True`
- js_loaded: `True`
- failed_required_requests: `0`
- api_status: `API_CHECKS_PASS`
- api_all_required_pass: `True`
- console_errors_count: `0`
- failed_requests_count: `0`
- average_fps: `33.085`
- fps_1pct_low: `11.976`
- interpretation_verdict: `PERFORMANCE_BASELINE_VALID_BUT_BLOCKED`

## Core Statement
The full-runtime measurement route is now valid, but the valid measurement shows real performance blockers: average FPS and 1% low FPS are below budget.

## Blocked Evidence
- average_fps is below budget blocker threshold.
- fps_1pct_low is below budget blocker threshold.

- recommended_next_task: `TASK-SECOND-BRAIN-V07-PERFORMANCE-BLOCKER-SOURCE-MAP`
