# Requirements: Truth Spine Evidence Timestamp Repair

## Problem Statement
Truth Spine checker fails with "PASS claimed but no evidence timestamp" because receipt files use `started_at_utc`/`finished_at_utc` fields, but `truth_state_checker.py` looks for `timestamp`/`started` fields.

## Root Cause Analysis
| Receipt Field | Checker Expects | Match |
|---------------|-----------------|-------|
| `started_at_utc` | `timestamp` or `started` | ❌ NO |
| `finished_at_utc` | - | ❌ NOT USED |

## Requirements

### REQ-1: Fix timestamp extraction in truth_state_checker.py
- **Priority:** HIGH
- **Description:** Update `validate_truth_state()` to also check `started_at_utc` and `finished_at_utc` fields
- **Acceptance Criteria:**
  - Receipts with `started_at_utc` field are correctly parsed
  - `evidence_timestamp` is populated from available timestamp fields
  - Existing receipts with `timestamp`/`started` still work (backward compatibility)

### REQ-2: Verify fix with RUN_ALL.ps1
- **Priority:** HIGH
- **Description:** Run full verification to confirm Truth Spine now passes
- **Acceptance Criteria:**
  - Truth Spine step shows PASS or PASS_WITH_WARNINGS
  - No "PASS claimed but no evidence timestamp" blockers

### REQ-3: Update COMMAND_LOG.md with results
- **Priority:** MEDIUM
- **Description:** Document the fix and final verification results
- **Acceptance Criteria:**
  - Fix description added to COMMAND_LOG.md
  - Final RUN_ALL results recorded

## Out of Scope
- Anti-pattern violations (separate task)
- Smoke test PARTIAL status (expected during development)
