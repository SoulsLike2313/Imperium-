# SPECULUM_REVIEW_REQUEST

Please hard-review TASK-0014C1.

Checklist:
1. Verify top-level SHA256SUMS is machine-checkable from extracted bundle root.
2. Verify MANIFEST.json hash mismatch issue is fixed.
3. Verify manifest/control-file hash convention is explicit and recursion-safe.
4. Verify read-only explorer is truly read-only and Owner-usable with `--readonly-assert` flag.
5. Verify 0014C runtime/dry-run proofs are preserved in the merged repaired artifact.
6. Verify no VM2/E2E/THRONE/watchers/latest logic leak exists.
7. Provide go/no-go for TASK-0014D stage coordination scripts.
8. Confirm TASK-0015 remains blocked until stage coordination scripts are implemented and reviewed.
