# TASK AGENT MAP

task_id: TASK-20260508-0003-IMPERIUM-ROOT-MAP-ARTIFACT-ROUTING
task_name: IMPERIUM_ROOT_AGENT_MAP_AND_ARTIFACT_ROUTING_BASELINE_V1
purpose: Create root baseline map and artifact routing policy without moving/deleting files.
inputs:
- Top-level root observation only.
outputs:
- root map files
- artifact routing policy files
- cleanup candidates registry
receipts:
- 03_RECEIPTS/ROOT_MAP_RECEIPT.md
bundles:
- FINAL_STEP_BUNDLE/TASK-20260508-0003-IMPERIUM-ROOT-MAP-ARTIFACT-ROUTING_FINAL_STEP_BUNDLE.zip
current_status: draft_until_receipt
source_pointers:
- root files and artifact policy files created in this task
owner_notes:
- No movement/delete on this step.
next_action:
- owner-approved routing of root-level zip/sha256 files into ARTIFACTS by TASK_ID
