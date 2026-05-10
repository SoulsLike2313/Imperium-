# UPDATED_SCRIPT_REPAIR_REQUIREMENTS_V1

## Scope
Script implementation is out of scope for this patch. This document updates mandatory reporting requirements for the next script-repair task.

## Owner-facing report contract (mandatory)
- Every future script wrapper must print or emit the standard final Owner report from `AGENT_EXECUTION_REPORT_STANDARD_V1.md`.
- Script receipts may remain detailed.
- Chat-facing response must use exactly four sections: `ШАГ`, `БАНДЛ`, `ВЕРДИКТ`, `КОММЕНТАРИЙ ДЛЯ OWNER`.

## Coverage requirement
The following scripts must support the reporting contract:
- send_prompt_to_vm2.py
- fetch_vm2_stage_bundle.py
- task_status_append.py
- task_status_view.py
- barrier_verify.py
- final_bundle_assemble.py

## Existing strict requirements retained
- mandatory identifiers: TASK_ID, STAGE_ID, RUN_ID, CONTOUR_ID
- mandatory provenance/origin linkage
- no latest-bundle logic
- no anonymous artifacts
- no THRONE transfer claims
