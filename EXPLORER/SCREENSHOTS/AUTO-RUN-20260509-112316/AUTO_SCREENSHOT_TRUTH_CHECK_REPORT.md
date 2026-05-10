# IMPERIUM Explorer Auto Screenshot Truth Check V0.2

RUN_ID: `AUTO-RUN-20260509-112316`
VERDICT: `PARTIAL_SCREENSHOTS_CREATED_WITH_TRUTH_MISMATCHES`
EXPLORER_SCRIPT: `E:\IMPERIUM\EXPLORER\imperium_explorer_v0_5.py`
TRUTH_AUDIT_REPORT: `E:\IMPERIUM\EXPLORER\VERIFY\RUN-20260509-111424\EXPLORER_TRUTH_AUDIT_REPORT.json`

## Summary

- targets_total: `62`
- screenshots_created: `62`
- checks_total: `80`
- checks_passed: `78`
- checks_failed: `2`

## Failed checks

- `E:\IMPERIUM\EXPLORER` — `visible_direct_files_matches_truth_audit` expected=`6`
- `E:\IMPERIUM\ARCHIVE` — `visible_type_matches_truth_audit` expected=`ARCHIVE_COLD_STORAGE`

## Notes

- This is still a read-only visual/truth check.
- It writes only screenshots and reports.
- It does not modify IMPERIUM data.
- It does not contact VM2 or THRONE.
- It does not run E2E.
