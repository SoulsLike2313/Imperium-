# REPAIR_TEST_RESULTS

Task:
TASK-20260508-0014A-SCRIPT-REPAIR-CLEANUP-LEDGER-FAILURE-RECEIPTS-SHA256-V1

## Test 1: Python compile
Result: PASS
Details: all `imperium_pipeline/*.py` and `imperium_pipeline/lib/*.py` compile with `py_compile`.

## Test 2: Ledger timestamp normalization
Result: PASS
Details:
- append without `timestamp_utc` produced UTC timestamp.
- append with `timestamp_utc=""` produced UTC timestamp.
- append with `timestamp_utc="2026-05-08T20:30:00Z"` remained valid UTC timestamp.
- empty timestamp count in JSONL: 0.

## Test 3: send failure receipt and STAGE_FAILED
Result: PASS
Scenario: missing prompt file.
Evidence:
- DISPATCH_RECEIPT.json created.
- ledger event `STAGE_FAILED` present.
- Owner report verdict `FAIL` printed.

## Test 4: latest-path rejection
Result: PASS
Scenario: prompt path containing `latest`.
Evidence:
- command rejected.
- failure receipt created.
- ledger contains `STAGE_FAILED`.

## Test 5: fetch failure receipt and STAGE_FAILED
Result: PASS
Scenario: missing/invalid route config in controlled local test.
Evidence:
- FETCH_RECEIPT.json created with FAIL.
- ledger event `STAGE_FAILED` present.

## Test 6: barrier non-pass evidence
Result: PASS
Scenario: bundle missing required internal evidence.
Evidence:
- BARRIER_REPORT.json created.
- BARRIER_RECEIPT.json created.
- ledger has `BARRIER_FAIL` event.

## Test 7: final assembly blocked when barrier not pass
Result: PASS
Scenario: barrier report `BARRIER_WAITING`.
Evidence:
- no final bundle created.
- FINAL_ASSEMBLY_RECEIPT.json created with BLOCKED/FAIL path.
- ledger contains failure event.

## Test 8: portable external .sha256
Result: PASS
Scenario: write `.sha256` for dummy bundle.
Evidence:
- output format uses filename only.
- no absolute Windows path in checksum line.

## Scope confirmation
- No PC<->VM2 E2E execution was performed.
- No THRONE transfer was performed.
- No automation/watchers were enabled.

## Test 9: malformed timestamp behavior
Result: PASS
Scenario: append ledger event with `timestamp_utc="NOT_A_TIMESTAMP"`.
Behavior: rejected with `ValueError` (documented strict-fail normalization policy).
