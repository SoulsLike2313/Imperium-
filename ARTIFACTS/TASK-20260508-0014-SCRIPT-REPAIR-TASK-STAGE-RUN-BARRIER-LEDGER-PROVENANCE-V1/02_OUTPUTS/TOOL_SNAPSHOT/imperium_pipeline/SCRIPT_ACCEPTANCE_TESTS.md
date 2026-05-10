# SCRIPT_ACCEPTANCE_TESTS

## PASS CASES
- Valid dispatch with required IDs and provenance output creates DISPATCH_RECEIPT + STAGE_DISPATCHED event.
- Valid fetch with exact TASK/STAGE/RUN/CONTOUR and matching sha256 creates FETCH_RECEIPT + verification events.
- Valid ledger append writes one JSON object line and preserves append-only history.
- Valid status view returns summary without changing ledger.
- Barrier returns BARRIER_WAITING when expected stage evidence is missing.
- Barrier returns BARRIER_PASS when all required evidence is present and conflict-free.
- Final bundle assembly succeeds only after BARRIER_PASS.

## FAIL CASES
- Missing RUN_ID in dispatch/fetch/append input.
- Any latest path/newest path pattern in input arguments.
- Missing provenance for accepted artifacts.
- Mismatched sha256 during fetch verification.
- Wrong producer_type for fetched bundle (not VM2_WORKER).
- VM2 provenance claiming FINAL_TASK_BUNDLE authority.
- Conflicting sha256 for same TASK/STAGE/RUN/CONTOUR in origin index.
- Malformed ledger event JSON.
- Non-portable SHA256 output using absolute local Windows path.

## Additional policy checks
- No THRONE transfer claim in receipts.
- No auto-sync claim in receipts.
- Owner-facing output uses standardized 4-section format.
