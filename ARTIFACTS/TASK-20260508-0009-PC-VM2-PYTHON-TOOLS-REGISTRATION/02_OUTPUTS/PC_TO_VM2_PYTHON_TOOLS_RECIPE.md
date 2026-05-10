# PC TO VM2 PYTHON TOOLS RECIPE

Status:
DRAFT_TOOLS_CREATED

Purpose:
Python wrappers for the already verified manual PC <-> VM2 workflow.

Tools:
- 06_TOOLS\send_prompt_to_vm2.py
- 06_TOOLS\fetch_vm2_stage_bundle.py

Local route config:
- 00_CONNECTION_PROFILES\VM2_ROUTE.local.json

Important:
- The local config is LOCAL_ONLY.
- Do not export local route values without redaction.
- Do not use latest bundle logic.
- Fetch uses exact TASK/STAGE/CONTOUR/RUN identifiers.

## Send prompt to VM2

Example:

python "E:\IMPERIUM\SSH_COMMAND_LIBRARY\06_TOOLS\send_prompt_to_vm2.py" --task-id TASK-TEST-VM2-PROMPT-COPY --stage-id STAGE-001-VM2 --open-remote

## Fetch VM2 stage bundle

Example:

python "E:\IMPERIUM\SSH_COMMAND_LIBRARY\06_TOOLS\fetch_vm2_stage_bundle.py" --task-id TASK-20260508-0008-VM2-LEGACY-INBOX-REPAIR --stage-id STAGE-001-VM2-LEGACY-INBOX-REPAIR --run-id RUN-20260508-0001 --open-folder

## Next required validation

Run smoke tests for both scripts and register successful script receipts under ARTIFACTS.
