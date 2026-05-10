# TOOLS_INDEX

## Chosen tools root
E:\IMPERIUM\SSH_COMMAND_LIBRARY\06_TOOLS\imperium_pipeline

## Script inventory
- send_prompt_to_vm2.py
  - purpose: strict prompt dispatch preparation with identity/provenance/ledger enforcement
  - full path: E:\IMPERIUM\SSH_COMMAND_LIBRARY\06_TOOLS\imperium_pipeline\send_prompt_to_vm2.py

- fetch_vm2_stage_bundle.py
  - purpose: exact fetch + integrity/provenance verification for VM2 stage bundle
  - full path: E:\IMPERIUM\SSH_COMMAND_LIBRARY\06_TOOLS\imperium_pipeline\fetch_vm2_stage_bundle.py

- task_status_append.py
  - purpose: append one JSON event into append-only TASK_STATUS_LEDGER.jsonl
  - full path: E:\IMPERIUM\SSH_COMMAND_LIBRARY\06_TOOLS\imperium_pipeline\task_status_append.py

- task_status_view.py
  - purpose: summarize current task state from ledger without barrier decision authority
  - full path: E:\IMPERIUM\SSH_COMMAND_LIBRARY\06_TOOLS\imperium_pipeline\task_status_view.py

- barrier_verify.py
  - purpose: reducer for PASS/FAIL/WAITING/CONFLICT over identity/integrity/provenance/origin/ledger
  - full path: E:\IMPERIUM\SSH_COMMAND_LIBRARY\06_TOOLS\imperium_pipeline\barrier_verify.py

- final_bundle_assemble.py
  - purpose: PC-only final bundle assembly gated by BARRIER_PASS
  - full path: E:\IMPERIUM\SSH_COMMAND_LIBRARY\06_TOOLS\imperium_pipeline\final_bundle_assemble.py

## Shared library inventory
- E:\IMPERIUM\SSH_COMMAND_LIBRARY\06_TOOLS\imperium_pipeline\lib\id_validation.py
- E:\IMPERIUM\SSH_COMMAND_LIBRARY\06_TOOLS\imperium_pipeline\lib\sha256_utils.py
- E:\IMPERIUM\SSH_COMMAND_LIBRARY\06_TOOLS\imperium_pipeline\lib\manifest_utils.py
- E:\IMPERIUM\SSH_COMMAND_LIBRARY\06_TOOLS\imperium_pipeline\lib\provenance_utils.py
- E:\IMPERIUM\SSH_COMMAND_LIBRARY\06_TOOLS\imperium_pipeline\lib\ledger_utils.py
- E:\IMPERIUM\SSH_COMMAND_LIBRARY\06_TOOLS\imperium_pipeline\lib\owner_report.py
- E:\IMPERIUM\SSH_COMMAND_LIBRARY\06_TOOLS\imperium_pipeline\lib\path_safety.py
