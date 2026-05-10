# CLEANHASH_REPAIR_REPORT

Task:
TASK-20260508-0014C1-CLEANHASH-REGISTRY-PACKAGING-REPAIR-V1

Scope:
- targeted cleanhash/packaging repair for TASK-0014C merged artifact
- read-only explorer UX flag alignment
- local-only validation evidence

Repairs applied:
1. Rebuilt top-level MANIFEST.json and SHA256SUMS.txt with stable control-file policy.
2. Ensured SHA256SUMS uses archive-relative POSIX paths only.
3. Ensured SHA256SUMS includes MANIFEST.json hash and excludes SHA256SUMS self-hash.
4. Repacked final bundle with safe POSIX zip members.
5. Updated read-only explorer flag UX to support `--readonly-assert` as boolean flag.
6. Updated explorer README/examples for explicit flag usage.

Validation summary:
- External sidecar .sha256 check: PASS.
- Extracted bundle internal SHA verification: PASS.
- MANIFEST.json hash entry verification: PASS.
- No absolute/backslash/traversal paths in SHA256SUMS: PASS.
- Zip member hygiene checks: PASS.
- Explorer summary/map mode with `--readonly-assert`: PASS.
- Registry JSON parse: PASS.
- Python compile: PASS.

Scope guard:
- No VM2 contact.
- No THRONE transfer.
- No watcher/background automation.
- No real PC↔VM2 E2E execution.
