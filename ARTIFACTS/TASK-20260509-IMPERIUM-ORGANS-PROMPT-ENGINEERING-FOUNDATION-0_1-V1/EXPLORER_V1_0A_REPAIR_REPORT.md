# EXPLORER V1.0A Repair Report

Explorer candidate: `E:/IMPERIUM/EXPLORER/imperium_explorer_v1_0a.py`

Explorer repair status: `PASS_EXPLORER_V1_0A_ARCHIVE_POLICY_REPAIR`

Proof chain:
- static_readonly_source_scan_v1_0a: `PASS_STATIC_READ_ONLY_SCAN`
- explorer_truth_audit_v1_0a: `PASS_TRUTH_SNAPSHOT_READY_FOR_SCREENSHOT_COMPARE`
- auto_explorer_screenshot_truth_check_v1_0a: `PASS_AUTOSCREENSHOT_TRUTH_COMPARE`

Archive required checks (autoscreenshot):
- seen: ['visible_ARCHIVE_ACTIVE_PROCESS_line', 'visible_ARCHIVE_POLICY_line', 'visible_ARCHIVE_RECURSIVE_SCAN_line', 'visible_path_matches_target', 'visible_type_is_ARCHIVE_COLD_STORAGE']
- missing required checks: []
- failed required checks: []

Required archive lines in details panel for `ARCHIVE_COLD_STORAGE`:
- ARCHIVE_POLICY: COLD_STORAGE_TOP_LEVEL_ONLY
- ARCHIVE_RECURSIVE_SCAN: DISABLED
- ARCHIVE_ACTIVE_PROCESS: FALSE
- ARCHIVE_MANUAL_BROWSING: INSPECTION_ONLY_NOT_ACTIVE_HISTORY

Claim level:
- EXPLORER_V1_0A_CANDIDATE
- final baseline approval pending Speculum.
