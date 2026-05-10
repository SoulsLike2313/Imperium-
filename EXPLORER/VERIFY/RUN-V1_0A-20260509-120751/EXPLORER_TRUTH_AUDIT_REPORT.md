# IMPERIUM Explorer Truth Audit V1.0A

RUN_ID: `RUN-V1_0A-20260509-120751`
CREATED_AT: `2026-05-09T12:07:55`
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

- total_nodes_scanned_excluding_archive_contents: `28512`
- archive_roots_skipped_recursive_count: `1`
- task_folders_count: `108`
- receipts_count: `577`
- manifests_count: `127`
- bundles_count: `308`
- organ_scaffolds_count: `11`

## Counts by Explorer node type

- ARCHIVE_COLD_STORAGE: `1`
- ARTIFACTS_ROOT: `15`
- BUNDLE_ZIP: `308`
- EXPLORER_ROOT: `1`
- FILE: `4841`
- FOLDER: `5340`
- HASH_FILE: `236`
- IMPERIUM_ROOT: `2`
- JSONL_LEDGER: `174`
- JSON_FILE: `8684`
- MANIFEST: `127`
- MANUAL_PROOFS_ROOT: `1`
- MARKDOWN_FILE: `6688`
- ORGANS_ROOT: `14`
- ORGAN_SCAFFOLD: `11`
- POLICY_ROOT: `3`
- PYTHON_SCRIPT: `1347`
- RECEIPT: `577`
- TASK_FOLDER: `108`
- TOOLS_ROOT: `34`

## Findings

- `INFO` `ARCHIVE_RECURSIVE_SCAN_DISABLED` — Skipped recursive scan for 1 archive root(s).
