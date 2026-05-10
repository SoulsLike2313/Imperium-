# NEW CHAT HANDOFF

Role:
Logos-Prime

Project:
IMPERIUM MetaOS

Current goal:
Build a strict human-in-the-loop engineering system where tasks move through folders, scripts, contours, receipts, bundles, checksums, and review.

Current root:
E:\IMPERIUM

Allowed root folders:
- ARCHIVE
- ARTIFACTS
- OBSERVED
- PC_ENGINEERING_ROOM
- SSH_COMMAND_LIBRARY

Current working contour status:
PC:
- orchestrator
- engineering room
- artifact collector
- SSH tool host
- fetch/verify side

VM2:
- disposable worker contour
- worker root: /home/vboxuser2/IMPERIUM_WORKER_ROOM
- receives prompts under 01_INBOX/tasks/<TASK_ID>
- emits stage bundles under 03_OUTBOX/stage_bundles

Current tools:
- E:\IMPERIUM\SSH_COMMAND_LIBRARY\06_TOOLS\send_prompt_to_vm2.py
- E:\IMPERIUM\SSH_COMMAND_LIBRARY\06_TOOLS\fetch_vm2_stage_bundle.py

Important policy:
- Do not write to THRONE.
- Do not auto-sync.
- Do not use latest bundle logic.
- Use TASK_ID / STAGE_ID / CONTOUR_ID / RUN_ID.
- Store evidence in ARTIFACTS.
- Keep local route values local-only.
- No full automation until manual E2E passes and Speculum reviews.

Current next step:
Speculum review of this continuity pack.
Then design first tiny two-contour TASK/STAGE/RUN test with barrier.
