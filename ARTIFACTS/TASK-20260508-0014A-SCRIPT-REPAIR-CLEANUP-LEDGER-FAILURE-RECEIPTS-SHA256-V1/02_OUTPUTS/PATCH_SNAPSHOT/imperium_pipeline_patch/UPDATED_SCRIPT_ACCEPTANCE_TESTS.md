# UPDATED_SCRIPT_ACCEPTANCE_TESTS

## PASS smoke tests
- Python compile for all top-level scripts and `lib/*.py`.
- Ledger append without timestamp_utc creates UTC timestamp.
- Ledger append with timestamp_utc="" creates UTC timestamp.
- Ledger append with valid timestamp keeps valid UTC timestamp.
- send_prompt_to_vm2 failure path creates DISPATCH_RECEIPT.json + STAGE_FAILED event.
- fetch_vm2_stage_bundle failure path creates FETCH_RECEIPT.json + STAGE_FAILED event.
- barrier_verify non-pass path creates BARRIER_REPORT.json + BARRIER_RECEIPT.json + barrier ledger event.
- final_bundle_assemble blocks when barrier is not BARRIER_PASS and writes receipt + failure event.
- Portable .sha256 writer emits filename-only reference.

## FAIL policy tests
- Missing RUN_ID should fail validation.
- Any path containing latest/newest should be rejected.
- Missing provenance for accepted artifacts should fail validation.
- Mismatched sha256 should fail verification.
- Wrong producer_type should fail acceptance checks.
- VM2 claiming FINAL_TASK_BUNDLE authority should fail.
- Origin hash conflict for same TASK/STAGE/RUN/CONTOUR should produce conflict outcome.
- Malformed ledger JSONL line should fail read/summary.
- Non-portable absolute path in external .sha256 is forbidden.
