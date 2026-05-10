# SCRIPT_ACCEPTANCE_TESTS

Required local-only checks for TASK-0014C:

1. Python compile for all included .py files.
2. final_bundle_assemble.py --help runtime smoke from installed root.
3. Dependency closure check for pipeline and explorer scripts.
4. Local final assembly dry-run with fake BARRIER_PASS fixture.
5. Internal SHA256SUMS verification after extraction.
6. FINAL_PROVENANCE no-PENDING check.
7. Zip path hygiene check (POSIX-only, no absolute/traversal paths).
8. External .sha256 portability check (filename-only).
9. Read-only explorer summary mode execution with `--readonly-assert` flag.
10. Read-only explorer map mode execution with `--readonly-assert` flag.
11. Registry JSON parse check.
12. Active tool registry presence check.

Scope guard:
- No VM2 contact.
- No real E2E.
- No THRONE transfer.
- No watcher automation.
