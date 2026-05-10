# UPDATED_SCRIPT_ACCEPTANCE_TESTS

## PASS regression tests for TASK-0014B
- Python compile for all top-level scripts and `lib/*.py`.
- final_bundle_assemble produces internal `SHA256SUMS.txt` with archive-relative POSIX paths for nested files.
- Extracted final bundle passes hash verification from bundle root using internal `SHA256SUMS.txt`.
- `FINAL_PROVENANCE.json` inside final bundle does not contain `source_bundle_sha256: "PENDING"`.
- `FINAL_PROVENANCE.json` uses sidecar model (`source_bundle_sha256: null`, `source_bundle_sha256_status: EXTERNAL_HASH_RECORDED_IN_SIDECAR`).
- `MANIFEST.json` inside final bundle states bundle hash location in external `.sha256` sidecar.
- Zip archive member names are POSIX-clean (`/` separators), no backslashes, no absolute paths, no traversal.
- External `.sha256` remains portable and filename-only.

## FAIL policy tests
- Reject output paths containing latest/newest patterns.
- Reject unsafe archive member paths (absolute, traversal, drive-like, backslash).
- Reject provenance records with `source_bundle_sha256: "PENDING"`.
- Reject accepted provenance records with missing `source_bundle_sha256` unless sidecar status is explicit.

## Scope guard
- No PC<->VM2 E2E execution.
- No THRONE transfer.
- No watcher automation.
