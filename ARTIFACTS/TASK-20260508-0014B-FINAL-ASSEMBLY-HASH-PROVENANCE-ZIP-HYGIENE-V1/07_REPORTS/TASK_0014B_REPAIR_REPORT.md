# TASK_0014B_REPAIR_REPORT

Repaired components:
- final_bundle_assemble.py
- lib/sha256_utils.py
- lib/provenance_utils.py

Validated outcomes:
- internal bundle SHA256SUMS uses POSIX relative paths and verifies nested files.
- FINAL_PROVENANCE.json inside final bundle has no PENDING self-hash marker.
- MANIFEST.json inside final bundle declares external sidecar hash policy.
- zip member names are safe POSIX relative paths.
- external .sha256 sidecar remains filename-only and portable.

Scope limits respected:
- no VM2 contact;
- no THRONE transfer;
- no E2E execution;
- no watchers/automation.
