# IMPERIUM Explorer Truth Audit V1.0A

RUN_ID: `RUN-V1_0A-20260509-120022`
CREATED_AT: `2026-05-09T12:00:27`
IMPERIUM_ROOT: `E:\IMPERIUM`

## Verdict

`PASS_TRUTH_SNAPSHOT_READY_FOR_SCREENSHOT_COMPARE`

## Archive policy

- ARCHIVE is treated as cold storage.
- ARCHIVE is not recursively scanned.
- Only top-level archive index is collected.

## Critical paths

- `OK` — `IMPERIUM_ROOT` — `E:\IMPERIUM`
- `OK` — `ARTIFACTS_ROOT` — `E:\IMPERIUM\ARTIFACTS`
- `OK` — `MANUAL_PROOFS_ROOT` — `E:\IMPERIUM\ARTIFACTS\_MANUAL_PROOFS`
- `OK` — `EXPLORER_ROOT` — `E:\IMPERIUM\EXPLORER`
- `OK` — `MARKDOWN_FILE` — `E:\IMPERIUM\EXPLORER\README.md`
- `OK` — `MARKDOWN_FILE` — `E:\IMPERIUM\EXPLORER\CHANGELOG.md`
- `OK` — `PYTHON_SCRIPT` — `E:\IMPERIUM\EXPLORER\imperium_explorer_v1_0a.py`
- `OK` — `JSON_FILE` — `E:\IMPERIUM\EXPLORER\POLICIES\EXPLORER_BASELINE_POLICY.json`
- `OK` — `MARKDOWN_FILE` — `E:\IMPERIUM\EXPLORER\POLICIES\EXPLORER_BASELINE_POLICY.md`
- `OK` — `JSON_FILE` — `E:\IMPERIUM\EXPLORER\POLICIES\EXPLORER_ARCHIVE_POLICY.json`
- `OK` — `MARKDOWN_FILE` — `E:\IMPERIUM\EXPLORER\POLICIES\EXPLORER_ARCHIVE_POLICY.md`

## Tree scan summary

- total_nodes_scanned_excluding_archive_contents: `28354`
- archive_roots_skipped_recursive_count: `1`
- task_folders_count: `106`
- receipts_count: `576`
- manifests_count: `127`
- bundles_count: `308`
- organ_scaffolds_count: `8`

## Counts by Explorer node type

- ARCHIVE_COLD_STORAGE: `1`
- ARTIFACTS_ROOT: `15`
- BUNDLE_ZIP: `308`
- EXPLORER_ROOT: `1`
- FILE: `4769`
- FOLDER: `5320`
- HASH_FILE: `236`
- IMPERIUM_ROOT: `2`
- JSONL_LEDGER: `174`
- JSON_FILE: `8643`
- MANIFEST: `127`
- MANUAL_PROOFS_ROOT: `1`
- MARKDOWN_FILE: `6679`
- ORGANS_ROOT: `13`
- ORGAN_SCAFFOLD: `8`
- POLICY_ROOT: `2`
- PYTHON_SCRIPT: `1339`
- RECEIPT: `576`
- TASK_FOLDER: `106`
- TOOLS_ROOT: `34`

## Findings

- `INFO` `ARCHIVE_RECURSIVE_SCAN_DISABLED` — Skipped recursive scan for 1 archive root(s).
