# PC VM2 PIPELINE

Purpose:
PC-side transport and verification scripts for VM2 stage execution lifecycle.

Rules:
- exact TASK_ID/STAGE_ID/RUN_ID addressing only
- no latest-bundle logic
- no THRONE transfer
- no watcher automation

Active tools in this folder:
- send_prompt_to_vm2.py
- fetch_vm2_stage_bundle.py
- barrier_verify.py
- final_bundle_assemble.py
- task_status_append.py
- task_status_view.py

Trace policy:
Pipeline tools must emit receipts, ledger events, and Owner report output.
