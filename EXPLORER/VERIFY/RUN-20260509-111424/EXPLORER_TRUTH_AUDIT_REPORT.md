# IMPERIUM Explorer Truth Audit V0.2

RUN_ID: `RUN-20260509-111424`
CREATED_AT: `2026-05-09T11:14:29`
IMPERIUM_ROOT: `E:\IMPERIUM`

## Verdict

`PASS_TRUTH_SNAPSHOT_READY_FOR_SCREENSHOT_COMPARE`

## Read-only statement

- This audit reads filesystem state and writes only its own report files.
- It does not modify IMPERIUM data, does not contact VM2, does not touch THRONE.
- ARCHIVE folders are not scanned recursively; only top-level archive index is collected.

## Archive policy

- ARCHIVE is treated as cold storage.
- ARCHIVE is not recursively scanned.
- Only top-level archive index is collected.
- ARCHIVE currently does not participate in active working process.

## Critical paths

- `OK` — `IMPERIUM_ROOT` — `E:\IMPERIUM`
- `OK` — `ARTIFACTS_ROOT` — `E:\IMPERIUM\ARTIFACTS`
- `OK` — `MANUAL_PROOFS_ROOT` — `E:\IMPERIUM\ARTIFACTS\_MANUAL_PROOFS`
- `OK` — `EXPLORER_ROOT` — `E:\IMPERIUM\EXPLORER`
- `OK` — `MARKDOWN_FILE` — `E:\IMPERIUM\EXPLORER\README.md`
- `OK` — `PYTHON_SCRIPT` — `E:\IMPERIUM\EXPLORER\imperium_explorer_v0_3.py`
- `OK` — `PYTHON_SCRIPT` — `E:\IMPERIUM\EXPLORER\imperium_explorer_v0_4.py`

## Archive top index

### `E:\IMPERIUM\ARCHIVE`

- recursive_scan: `DISABLED`
- direct_folders: `2`
- direct_files: `0`
- direct_items_sample_count: `2`


## Tree scan summary

- total_nodes_scanned_excluding_archive_contents: `27917`
- archive_roots_skipped_recursive_count: `1`
- task_folders_count: `104`
- receipts_count: `574`
- manifests_count: `125`
- bundles_count: `303`
- organ_scaffolds_count: `8`

## Counts by Explorer node type

- ARCHIVE_COLD_STORAGE: `1`
- ARTIFACTS_ROOT: `15`
- BUNDLE_ZIP: `303`
- EXPLORER_ROOT: `1`
- FILE: `4438`
- FOLDER: `5297`
- HASH_FILE: `232`
- IMPERIUM_ROOT: `2`
- JSONL_LEDGER: `174`
- JSON_FILE: `8625`
- MANIFEST: `125`
- MANUAL_PROOFS_ROOT: `1`
- MARKDOWN_FILE: `6650`
- ORGANS_ROOT: `13`
- ORGAN_SCAFFOLD: `8`
- PYTHON_SCRIPT: `1320`
- RECEIPT: `574`
- TASK_FOLDER: `104`
- TOOLS_ROOT: `34`

## Findings

- `INFO` `ARCHIVE_RECURSIVE_SCAN_DISABLED` — Skipped recursive scan for 1 archive root(s).

## Interpretation

This audit does not prove that the GUI displays every node correctly.
It proves the filesystem truth snapshot that Explorer must match.
ARCHIVE is intentionally indexed only at top level.
Next step: screenshot pack must visually compare Explorer v0.4 with this report.
