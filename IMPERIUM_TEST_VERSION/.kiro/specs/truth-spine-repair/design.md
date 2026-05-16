# Design: Truth Spine Evidence Timestamp Repair

## Overview
Fix timestamp field mapping in `truth_state_checker.py` to support receipt format with `started_at_utc`/`finished_at_utc` fields.

## Current State
```
Receipt JSON:
{
  "started_at_utc": "2026-05-16T03:56:11.9020236+03:00",
  "finished_at_utc": "2026-05-16T03:56:12.3777557+03:00",
  "verdict": "PASS"
}

Checker looks for:
  evidence_ts = receipt_data.get("timestamp") or receipt_data.get("started")
  → Returns None → "PASS claimed but no evidence timestamp"
```

## Solution Design

### Change 1: Update validate_truth_state() in truth_state_checker.py

**Before (line ~60):**
```python
evidence_ts = receipt_data.get("timestamp") or receipt_data.get("started")
```

**After:**
```python
evidence_ts = (
    receipt_data.get("timestamp") 
    or receipt_data.get("started")
    or receipt_data.get("started_at_utc")
    or receipt_data.get("finished_at_utc")
)
```

### Field Priority Order
1. `timestamp` - standard field (backward compat)
2. `started` - legacy field (backward compat)
3. `started_at_utc` - new receipt format
4. `finished_at_utc` - fallback if started missing

## Files Modified
| File | Change |
|------|--------|
| `TRUTH_SPINE/truth_state_checker.py` | Add `started_at_utc`/`finished_at_utc` to timestamp extraction |

## Verification
1. Run `py -3 TRUTH_SPINE/truth_aggregator.py --receipts-dir RECEIPTS`
2. Check `evidence_timestamp` is populated for all components
3. Run `RUN_ALL.ps1` - Truth Spine step should PASS

## Risks
- **LOW:** Simple field mapping change
- **Backward compatible:** Existing fields checked first
