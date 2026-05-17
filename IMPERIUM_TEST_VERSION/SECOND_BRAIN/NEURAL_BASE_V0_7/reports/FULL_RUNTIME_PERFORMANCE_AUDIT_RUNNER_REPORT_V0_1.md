# FULL RUNTIME PERFORMANCE AUDIT RUNNER REPORT V0.1

- task_id: `TASK-SECOND-BRAIN-V07-FULL-RUNTIME-PERFORMANCE-AUDIT-RUNNER`
- current_head: `1464306ecaba5a48db5450dccc986e84e1b9575f`
- tool_created: `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/tools/full_runtime_performance_audit_runner_v0_1.py`
- tool_ran: `true`
- runtime_launched: `true`
- runtime_isolation_mode: `TEMP_RUNTIME_AUDIT_ROOT:DISPOSABLE_LOCAL_RUNTIME_SERVER_WITH_QUARANTINE_WRITES`
- api_checks_status: `API_CHECKS_PASS`
- browser_audit_status: `BROWSER_AUDIT_RUN`
- required_assets_status: `REQUIRED_ASSETS_MISSING`
- fps_status: `FPS_MEASURED`
- fps_acceptance_status: `FPS_INVALID_FOR_UI_PERFORMANCE_ACCEPTANCE`
- server_shutdown_status: `SERVER_STOPPED`
- report_output_budget_enforced: `true`
- forbidden_paths_touched_count: `0`
- verdict: `BLOCKED_REQUIRED_ASSETS_MISSING`
- next_allowed_task: `TASK-SECOND-BRAIN-V07-RUNTIME-AUDIT-BLOCKER-INTERPRETATION`

## Notes
- Runtime server was launched in isolated root outside the repository and then stopped.
- Required API checks passed.
- Runtime target URL returned HTTP 404, so required CSS/JS were not loaded.
- FPS was measured but explicitly not accepted as full runtime performance truth.

