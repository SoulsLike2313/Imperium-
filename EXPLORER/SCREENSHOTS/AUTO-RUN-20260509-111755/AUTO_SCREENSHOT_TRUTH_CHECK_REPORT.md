# IMPERIUM Explorer Auto Screenshot Truth Check V0.1

RUN_ID: `AUTO-RUN-20260509-111755`
VERDICT: `PARTIAL_SCREENSHOTS_CREATED_WITH_TRUTH_MISMATCHES`
EXPLORER_SCRIPT: `E:\IMPERIUM\EXPLORER\imperium_explorer_v0_4.py`
TRUTH_AUDIT_REPORT: `E:\IMPERIUM\EXPLORER\VERIFY\RUN-20260509-111424\EXPLORER_TRUTH_AUDIT_REPORT.json`

## Summary

- targets_total: `8`
- screenshots_created: `8`
- checks_total: `26`
- checks_passed: `25`
- checks_failed: `1`

## Targets

### `E:\IMPERIUM`

- source: `truth_audit.critical_paths`
- select_status: `SELECTED`
- screenshot: `E:\IMPERIUM\EXPLORER\SCREENSHOTS\AUTO-RUN-20260509-111755\01_IMPERIUM.png`

- `PASS` visible_path_matches_target expected=`E:\IMPERIUM`
- `PASS` visible_type_matches_truth_audit expected=`IMPERIUM_ROOT`
- `PASS` visible_direct_folders_matches_truth_audit expected=`6`
- `PASS` visible_direct_files_matches_truth_audit expected=`0`

### `E:\IMPERIUM\ARTIFACTS`

- source: `truth_audit.critical_paths`
- select_status: `SELECTED`
- screenshot: `E:\IMPERIUM\EXPLORER\SCREENSHOTS\AUTO-RUN-20260509-111755\02_ARTIFACTS.png`

- `PASS` visible_path_matches_target expected=`E:\IMPERIUM\ARTIFACTS`
- `PASS` visible_type_matches_truth_audit expected=`ARTIFACTS_ROOT`
- `PASS` visible_direct_folders_matches_truth_audit expected=`27`
- `PASS` visible_direct_files_matches_truth_audit expected=`5`

### `E:\IMPERIUM\ARTIFACTS\_MANUAL_PROOFS`

- source: `truth_audit.critical_paths`
- select_status: `SELECTED`
- screenshot: `E:\IMPERIUM\EXPLORER\SCREENSHOTS\AUTO-RUN-20260509-111755\03__MANUAL_PROOFS.png`

- `PASS` visible_path_matches_target expected=`E:\IMPERIUM\ARTIFACTS\_MANUAL_PROOFS`
- `PASS` visible_type_matches_truth_audit expected=`MANUAL_PROOFS_ROOT`
- `PASS` visible_direct_folders_matches_truth_audit expected=`5`
- `PASS` visible_direct_files_matches_truth_audit expected=`4`

### `E:\IMPERIUM\EXPLORER`

- source: `truth_audit.critical_paths`
- select_status: `SELECTED`
- screenshot: `E:\IMPERIUM\EXPLORER\SCREENSHOTS\AUTO-RUN-20260509-111755\04_EXPLORER.png`

- `PASS` visible_path_matches_target expected=`E:\IMPERIUM\EXPLORER`
- `PASS` visible_type_matches_truth_audit expected=`EXPLORER_ROOT`
- `PASS` visible_direct_folders_matches_truth_audit expected=`2`
- `PASS` visible_direct_files_matches_truth_audit expected=`6`

### `E:\IMPERIUM\EXPLORER\README.md`

- source: `truth_audit.critical_paths`
- select_status: `SELECTED`
- screenshot: `E:\IMPERIUM\EXPLORER\SCREENSHOTS\AUTO-RUN-20260509-111755\05_README_md.png`

- `PASS` visible_path_matches_target expected=`E:\IMPERIUM\EXPLORER\README.md`
- `PASS` visible_type_matches_truth_audit expected=`MARKDOWN_FILE`

### `E:\IMPERIUM\EXPLORER\imperium_explorer_v0_3.py`

- source: `truth_audit.critical_paths`
- select_status: `SELECTED`
- screenshot: `E:\IMPERIUM\EXPLORER\SCREENSHOTS\AUTO-RUN-20260509-111755\06_imperium_explorer_v0_3_py.png`

- `PASS` visible_path_matches_target expected=`E:\IMPERIUM\EXPLORER\imperium_explorer_v0_3.py`
- `PASS` visible_type_matches_truth_audit expected=`PYTHON_SCRIPT`

### `E:\IMPERIUM\EXPLORER\imperium_explorer_v0_4.py`

- source: `truth_audit.critical_paths`
- select_status: `SELECTED`
- screenshot: `E:\IMPERIUM\EXPLORER\SCREENSHOTS\AUTO-RUN-20260509-111755\07_imperium_explorer_v0_4_py.png`

- `PASS` visible_path_matches_target expected=`E:\IMPERIUM\EXPLORER\imperium_explorer_v0_4.py`
- `PASS` visible_type_matches_truth_audit expected=`PYTHON_SCRIPT`

### `E:\IMPERIUM\ARCHIVE`

- source: `truth_audit.archive_top_index`
- select_status: `SELECTED`
- screenshot: `E:\IMPERIUM\EXPLORER\SCREENSHOTS\AUTO-RUN-20260509-111755\08_ARCHIVE.png`

- `PASS` visible_path_matches_target expected=`E:\IMPERIUM\ARCHIVE`
- `FAIL` visible_type_matches_truth_audit expected=`ARCHIVE_COLD_STORAGE`
- `PASS` visible_direct_folders_matches_truth_audit expected=`2`
- `PASS` visible_direct_files_matches_truth_audit expected=`0`

## Interpretation

This script opened Explorer v0.4, selected nodes programmatically, captured screenshots, and compared visible details against the latest truth audit where available.
It does not prove visual beauty. It checks whether key displayed node facts match filesystem truth.
If ARCHIVE type fails, Explorer needs explicit ARCHIVE_COLD_STORAGE classification.
