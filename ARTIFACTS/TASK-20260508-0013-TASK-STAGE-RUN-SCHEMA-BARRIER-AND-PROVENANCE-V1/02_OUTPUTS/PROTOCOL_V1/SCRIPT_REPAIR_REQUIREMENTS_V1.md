# SCRIPT_REPAIR_REQUIREMENTS_V1

## Scope
This document defines repair requirements only. No script repair is performed in this task.

## 1) send_prompt_to_vm2.py
### Required arguments
- --task-id
- --stage-id
- --run-id
- --contour-id VM2
- --producer-type PC_SERVITOR
- --producer-id
- --prompt-file
- --output-receipt

### Must forbid
- dummy prompt default
- missing run_id
- latest path logic
- anonymous dispatch

### Must emit
- DISPATCH_RECEIPT.json
- ledger event STAGE_DISPATCHED or STAGE_FAILED

## 2) fetch_vm2_stage_bundle.py
### Required arguments
- --task-id
- --stage-id
- --run-id
- --contour-id VM2
- --expected-producer-type VM2_WORKER
- --remote-bundle-path
- --remote-sha256-path
- --local-output-dir
- --output-receipt

### Must verify
- remote sha256 exists
- local sha256 matches
- manifest exists
- receipt exists
- provenance exists
- task/stage/run/contour match
- producer_type is expected
- no latest logic

### Must emit
- FETCH_RECEIPT.json
- ledger event BUNDLE_FETCHED or STAGE_FAILED

## 3) task_status_append.py
- append exactly one JSONL event
- never rewrite full ledger
- validate required event fields
- include provenance/origin fields

## 4) task_status_view.py
- read ledger timeline
- show WAITING/RUNNING/PASS/FAIL/CONFLICT/BLOCKED

## 5) barrier_verify.py
- read expected stage map, receipts, manifest, sha256, provenance, origin index, ledger
- output only BARRIER_PASS/BARRIER_FAIL/BARRIER_WAITING/BARRIER_CONFLICT

## 6) final_bundle_assemble.py
- run only after BARRIER_PASS
- create PC-side final bundle only
- include inputs, fetched VM2 bundle, receipts, ledger, origin index, provenance, barrier report, manifest, sha256, owner summary, speculum request
