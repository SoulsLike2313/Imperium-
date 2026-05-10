# IMPERIUM Explorer Truth Audit V1.0

RUN_ID: `RUN-V1_0-20260509-114429`
CREATED_AT: `2026-05-09T11:44:34`
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
- `OK` — `PYTHON_SCRIPT` — `E:\IMPERIUM\EXPLORER\imperium_explorer_v1_0.py`
- `OK` — `JSON_FILE` — `E:\IMPERIUM\EXPLORER\POLICIES\EXPLORER_BASELINE_POLICY.json`
- `OK` — `MARKDOWN_FILE` — `E:\IMPERIUM\EXPLORER\POLICIES\EXPLORER_BASELINE_POLICY.md`
- `OK` — `JSON_FILE` — `E:\IMPERIUM\EXPLORER\POLICIES\EXPLORER_ARCHIVE_POLICY.json`
- `OK` — `MARKDOWN_FILE` — `E:\IMPERIUM\EXPLORER\POLICIES\EXPLORER_ARCHIVE_POLICY.md`

## Tree scan summary

- total_nodes_scanned_excluding_archive_contents: `28173`
- archive_roots_skipped_recursive_count: `1`
- task_folders_count: `105`
- receipts_count: `575`
- manifests_count: `126`
- bundles_count: `307`
- organ_scaffolds_count: `8`

## Counts by Explorer node type

- ARCHIVE_COLD_STORAGE: `1`
- ARTIFACTS_ROOT: `15`
- BUNDLE_ZIP: `307`
- EXPLORER_ROOT: `1`
- FILE: `4634`
- FOLDER: `5309`
- HASH_FILE: `234`
- IMPERIUM_ROOT: `2`
- JSONL_LEDGER: `174`
- JSON_FILE: `8635`
- MANIFEST: `126`
- MANUAL_PROOFS_ROOT: `1`
- MARKDOWN_FILE: `6666`
- ORGANS_ROOT: `13`
- ORGAN_SCAFFOLD: `8`
- POLICY_ROOT: `2`
- PYTHON_SCRIPT: `1331`
- RECEIPT: `575`
- TASK_FOLDER: `105`
- TOOLS_ROOT: `34`

## Findings

- `INFO` `ARCHIVE_RECURSIVE_SCAN_DISABLED` — Skipped recursive scan for 1 archive root(s).
