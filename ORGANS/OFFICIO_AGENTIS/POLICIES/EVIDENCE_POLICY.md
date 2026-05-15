# EVIDENCE_POLICY v0.1

Core rules:

- No PASS without evidence.
- Every checker verdict must include command and output reference.
- Every stage marker must include evidence paths.
- Source paths and hashes should be recorded where applicable.
- Facts, assumptions, and proposals must be explicitly separated when role contract requires it.

Evidence artifacts include:

- checker reports (`*_check_report_*.json`);
- stage reports (`stage_*_report_*.json`);
- stage markers (`stage_marker.json`);
- role test dry-run report (`role_test_dry_run_report_v0_1.json`).
