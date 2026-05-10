# VM2 LIVE MANUAL PROBE SUMMARY

## Verdict
PASS_AS_VM2_LIVE_MANUAL_PROBE

## What happened
- PC created VM2 stage prompt package.
- send_prompt_to_vm2.py dry-run passed with old stage-id format STAGE-PC-001.
- send_prompt_to_vm2.py live dispatch returned PASS and touched VM2.
- VM2 created VM2_LIVE_PROBE_RESULT.md and VM2_LIVE_PROBE_RECEIPT.json.
- PC fetched VM2 result and receipt manually by scp.

## Important finding
- Current send_prompt_to_vm2.py rejects PC-STAGE-001 and accepts STAGE-PC-001.
- This is a schema mismatch against newer 0014D/0014E stage naming direction.
- It must be repaired before strict multi-stage E2E.

## Scope
- This was not full E2E.
- No THRONE.
- No watchers.
- No latest-bundle logic.

## Evidence
- PC dispatch receipt: MANUAL_RECEIPTS/SEND_PROMPT_TO_VM2_LIVE_RECEIPT_004.json
- VM2 returned result: VM2_RETURNED/VM2_LIVE_PROBE_RESULT.md
- VM2 returned receipt: VM2_RETURNED/VM2_LIVE_PROBE_RECEIPT.json
- PC fetch receipt: MANUAL_RECEIPTS/PC_MANUAL_FETCH_VM2_RESULT_RECEIPT.json
