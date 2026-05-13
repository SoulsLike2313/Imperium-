# Local and Private Externalization Plan v0.2

## Objective
Externalize local/private/ignored/generated payloads out of canonical repo roots while preserving tracked source truth.

## Canonical Roots
- Git root (PC): `E:\IMPERIUM`
- Git root (VM2): `/home/vboxuser2/IMPERIUM_WORK/Imperium-`

## External Roots
- Local operational root: `E:\IMPERIUM_LOCAL`
- Private Owner root: `E:\IMPERIUM_PRIVATE`

## Classification Rules
- `move_to_local_runtime`: runtime and generated execution outputs.
- `move_to_local_inbox`: inbox and bundle intake materials.
- `move_to_local_bundle_reviews`: bundle extract/review folders.
- `move_to_local_reports`: local diagnostics, generated local reports, cleanup receipts.
- `move_to_private_owner_context`: owner/private handoff context.
- `delete_disposable_cache`: `__pycache__`, `*.pyc`, `.pytest_cache` (ignored/untracked only).
- `leave_in_place_ambiguous`: unclear payloads kept for Owner decision.

## Migration Map (Required Examples)
- `.imperium_runtime` -> `E:\IMPERIUM_LOCAL\RUNTIME`
- `INBOX` / `_INBOX` -> `E:\IMPERIUM_LOCAL\INBOX`
- `VM2_BUNDLES` -> `E:\IMPERIUM_LOCAL\VM2_BUNDLES`
- bundle reviews/extracts -> `E:\IMPERIUM_LOCAL\BUNDLE_REVIEWS`
- local reports -> `E:\IMPERIUM_LOCAL\GENERATED_LOCAL_REPORTS`
- local receipts -> `E:\IMPERIUM_LOCAL\LOCAL_CLEANUP_RECEIPTS`
- `CHAT_COMPILATIONS_LOCAL` / handoff supplements -> `E:\IMPERIUM_PRIVATE\FULL_HANDOFF_INPUTS` or `E:\IMPERIUM_PRIVATE\PRIVATE_CONTEXT_PACKS`
- `__pycache__` / `*.pyc` / `.pytest_cache` -> disposable cache deletion if ignored/untracked

## Safety Rules
- Do not move tracked files.
- Do not delete tracked files.
- Do not move `.git`.
- Do not mass-delete with broad wildcards.
- Ambiguous paths are left in place and reported.
- No broad cleanup without manifest.

## Manifest Requirement
Every run must write:
`E:\IMPERIUM_LOCAL\GENERATED_LOCAL_REPORTS\SAN_CLEANING_REPO_PARITY_20260513\PC_EXTERNALIZATION_MANIFEST_20260513.json`

Each record must include source, status kind, classification, action, destination, timestamp, success, and error.

## Advisory Input
Required advisory sections: 2, 3, 8, 10, 11, 12, 15.
Advisory is required input, not automatic canon.
