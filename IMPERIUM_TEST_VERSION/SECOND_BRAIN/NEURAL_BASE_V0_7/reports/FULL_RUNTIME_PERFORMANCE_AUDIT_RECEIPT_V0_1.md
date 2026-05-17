# FULL RUNTIME PERFORMANCE AUDIT RECEIPT V0.1

- task_id: `TASK-SECOND-BRAIN-V07-FULL-RUNTIME-PERFORMANCE-AUDIT-RUNNER`
- generated_at: `2026-05-17T03:25:23+00:00`
- current_head: `1464306ecaba5a48db5450dccc986e84e1b9575f`
- runtime_isolation_mode: `TEMP_RUNTIME_AUDIT_ROOT:DISPOSABLE_LOCAL_RUNTIME_SERVER_WITH_QUARANTINE_WRITES`
- runtime_launch_status: `RUNTIME_LAUNCHED`
- runtime_url: `http://127.0.0.1:8767`
- server_shutdown_status: `SERVER_STOPPED`
- required_assets_status: `REQUIRED_ASSETS_MISSING`
- fps_status: `FPS_MEASURED`
- fps_acceptance_status: `FPS_INVALID_FOR_UI_PERFORMANCE_ACCEPTANCE`
- repo_pollution_status: `NO_REPO_POLLUTION_FROM_RUNTIME`
- verdict: `BLOCKED_REQUIRED_ASSETS_MISSING`

## API Checks
- status: `API_CHECKS_PASS`
- /api/status: code=`200` elapsed_ms=`3.15` ok=`True`
- /api/snapshot: code=`200` elapsed_ms=`1.93` ok=`True`
- /api/tasks: code=`200` elapsed_ms=`1.73` ok=`True`
- /api/task_packages: code=`200` elapsed_ms=`4.39` ok=`True`
- /api/export/status: code=`200` elapsed_ms=`1.88` ok=`True`

## Browser Audit
- browser_audit_status: `BROWSER_AUDIT_RUN`
- browser_backend: `python_playwright` availability=`BROWSER_AUTOMATION_AVAILABLE`
- css_loaded: `False`
- js_loaded: `False`
- failed_request_count: `0`
- console_error_count: `1`

## Runtime Side Effects
- isolation_root: `C:/Users/PC/AppData/Local/Temp/imperium_runtime_audits/full_runtime_audit_20260517_032520_15408`
- created_outside_repo_count: `0`
- isolated_created_count: `0`
- isolated_modified_count: `0`
- isolated_deleted_count: `0`

## Limitations
- Runner does not install dependencies or download browsers.
- Only compact samples are stored; no raw trace files are created.
- Read-only policy for source files is enforced through isolated runtime copy.
