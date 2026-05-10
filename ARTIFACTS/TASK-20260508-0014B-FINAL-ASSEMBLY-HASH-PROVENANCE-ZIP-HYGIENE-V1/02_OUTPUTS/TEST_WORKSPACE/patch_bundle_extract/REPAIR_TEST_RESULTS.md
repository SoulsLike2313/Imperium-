# REPAIR_TEST_RESULTS

Task:
TASK-20260508-0014B-FINAL-ASSEMBLY-HASH-PROVENANCE-ZIP-HYGIENE-V1

## Test 1: Python compile
Result: PASS
Details: all `imperium_pipeline/*.py` and `imperium_pipeline/lib/*.py` compile with `py_compile`.

## Test 2: Final assembly nested SHA256 verification
Result: PASS
Scenario: assemble local final test bundle with nested input files (`lib/`, `receipts/`, `provenance/`, `nested/deep/`).
Evidence:
- internal `SHA256SUMS.txt` created with archive-relative POSIX paths.
- extracted bundle root verification passed with no missing files and no hash mismatches.

## Test 3: FINAL_PROVENANCE no-PENDING
Result: PASS
Evidence:
- `FINAL_PROVENANCE.json` inside final bundle has no `PENDING`.
- `source_bundle_sha256` is `null`.
- `source_bundle_sha256_status` is `EXTERNAL_HASH_RECORDED_IN_SIDECAR`.
- `MANIFEST.json` declares external sidecar hash location and `bundle_self_hash_embedded=false`.

## Test 4: Zip arcname hygiene
Result: PASS
Evidence:
- inspected all zip entries.
- no `\\` separators.
- no absolute path markers.
- no traversal segments (`..`).

## Test 5: External sidecar portability
Result: PASS
Evidence:
- `<final_bundle>.zip.sha256` line uses filename only.
- no absolute Windows path (`E:\\...`) in sidecar checksum line.

## Test 6: Latest-pattern rejection regression
Result: PASS
Scenario: `--output-dir` containing `latest`.
Evidence:
- command rejected with FAIL.
- failure receipt path created by script failure path.

## Scope confirmation
- No PC<->VM2 E2E execution was performed.
- No VM2 connectivity was used.
- No THRONE transfer was performed.
- No automation/watchers were enabled.
