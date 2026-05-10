# REGISTRY_REPAIR_TEST_RESULTS

Task:
TASK-20260508-0014C2-REGISTRY-INTEGRITY-REPAIR-V1

1) External .sha256 verification
Result: PASS

2) Extracted bundle internal SHA verification
Result: PASS
Details: SHA256SUMS entries matched from extracted bundle root.

3) MANIFEST.json hash entry verification
Result: PASS

4) SHA256SUMS path safety
Result: PASS
Details: no absolute path, no drive prefix, no backslash, no traversal segments.

5) Zip member path hygiene
Result: PASS
Details: POSIX relative paths only, no unsafe members.

6) Python compile check
Result: PASS
Details: source-compile validation passed for included .py files.

7) Registry JSON parse
Result: PASS

8) ACTIVE/ACTIVE_NEEDS_SPECULUM hash verification
Result: PASS
Details:
- active_checked_count: 15
- active_hash_match_count: 15
- active_hash_mismatch_count: 0
- missing_active_files_count: 0
- unknown_active_tools_count: 0

9) READONLY_EXPLORER sha sync
Result: PASS
Details: registry sha256 equals actual file sha256.

10) Read-only explorer summary mode
Result: PASS

11) Read-only explorer map mode
Result: PASS

12) Read-only explorer summary mode with --verify-registry-hashes
Result: PASS

13) __pycache__ / .pyc exclusion
Result: PASS
Details: no __pycache__ entries and no .pyc files in final bundle.

14) Scope guard
Result: PASS
Details: no VM2 contact, no real E2E, no THRONE transfer, no watcher automation, no latest-bundle logic.

Note:
`sha256sum` CLI is unavailable in this Windows shell, so machine-checkable verification was executed via deterministic Python verification against SHA256SUMS entries from extracted root.
