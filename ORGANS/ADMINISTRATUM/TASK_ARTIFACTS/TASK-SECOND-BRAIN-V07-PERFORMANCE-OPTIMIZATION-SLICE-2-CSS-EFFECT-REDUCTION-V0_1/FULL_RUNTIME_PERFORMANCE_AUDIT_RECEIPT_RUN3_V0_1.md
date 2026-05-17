# FULL RUNTIME PERFORMANCE AUDIT RECEIPT V0.1

- task_id: `TASK-SECOND-BRAIN-V07-FULL-RUNTIME-PERFORMANCE-AUDIT-RUNNER`
- generated_at: `2026-05-17T20:59:32+00:00`
- current_head: `e74138a5c65085a185b97dfd8ea7453d1f432552`
- backend_runtime_launch_status: `RUNTIME_LAUNCHED`
- backend_runtime_url: `http://127.0.0.1:8767`
- full_runtime_mode: `FULL_RUNTIME_NATIVE_ROUTE`
- route_strategy: `NATIVE_ROUTE_DISCOVERY`
- audit_proxy_used: `False`
- audit_proxy_url: `None`
- browser_target_url: `http://127.0.0.1:8767/`
- browser_target_http_status: `200`
- html_loaded: `True`
- css_loaded: `True`
- js_loaded: `True`
- failed_required_requests: `0`
- runtime_isolation_mode: `TEMP_RUNTIME_AUDIT_ROOT:DISPOSABLE_LOCAL_RUNTIME_SERVER_WITH_QUARANTINE_WRITES`
- runtime_launch_status: `RUNTIME_LAUNCHED`
- runtime_url: `http://127.0.0.1:8767`
- server_shutdown_status: `SERVER_STOPPED`
- proxy_shutdown_status: `NOT_APPLICABLE`
- required_assets_status: `REQUIRED_ASSETS_LOADED`
- fps_status: `FPS_MEASURED`
- fps_acceptance_status: `FULL_RUNTIME_FPS_VALID`
- repo_pollution_status: `NO_REPO_POLLUTION_FROM_RUNTIME`
- verdict: `PASS_FULL_RUNTIME_BASELINE_NATIVE_ROUTE`

## API Checks
- status: `API_CHECKS_PASS`
- /api/status: code=`200` elapsed_ms=`3.26` ok=`True`
- /api/snapshot: code=`200` elapsed_ms=`1.94` ok=`True`
- /api/tasks: code=`200` elapsed_ms=`1.79` ok=`True`
- /api/task_packages: code=`200` elapsed_ms=`13.29` ok=`True`
- /api/export/status: code=`200` elapsed_ms=`3.44` ok=`True`

## Browser Audit
- browser_audit_status: `BROWSER_AUDIT_RUN`
- browser_backend: `python_playwright` availability=`BROWSER_AUTOMATION_AVAILABLE`
- css_loaded: `True`
- js_loaded: `True`
- failed_request_count: `0`
- console_error_count: `0`

## Runtime Side Effects
- isolation_root: `C:/Users/PC/AppData/Local/Temp/imperium_runtime_audits/full_runtime_audit_20260517_205928_6616`
- created_outside_repo_count: `0`
- isolated_created_count: `0`
- isolated_modified_count: `0`
- isolated_deleted_count: `0`

## Limitations
- Runner does not install dependencies or download browsers.
- Only compact samples are stored; no raw trace files are created.
- Read-only policy for source files is enforced through isolated runtime copy.
