# Staleness and Broken Source Audit

Generated: 2026-05-16T17:55:26Z

## Controlled Tests
- missing_snapshot_file: {"test": "missing_snapshot_file", "performed": true, "detected_by_checker": true, "checker_exit_code": 1}
- stale_snapshot_timestamp: {"test": "stale_snapshot_timestamp", "performed": true, "detected_by_checker": false, "checker_exit_code": 0, "note": "Current checker does not validate freshness age."}
- missing_truth_matrix_file: {"test": "missing_truth_matrix_file", "performed": true, "detected_by_checker": true, "checker_exit_code": 1}
- broken_zone_binding_snapshot_count: {"test": "broken_zone_binding_snapshot_count", "performed": true, "detected_by_checker": true, "checker_exit_code": 1}
- missing_runtime_source_outside_v0_5_scope: {"test": "missing_runtime_source_outside_v0_5_scope", "performed": false, "reason": "Skipped by scope policy: runtime files are outside NEURAL_BASE_V0_5.", "status": "UNPROVEN"}

## Conclusion

Does V0.5 currently guarantee stale/missing source honesty? **PARTIAL**

Notes:
- Missing snapshot and missing truth matrix are detected by checker.
- Stale timestamp freshness is not currently checker-gated.
- Runtime source removal outside V0.5 was not executed due strict scope policy.