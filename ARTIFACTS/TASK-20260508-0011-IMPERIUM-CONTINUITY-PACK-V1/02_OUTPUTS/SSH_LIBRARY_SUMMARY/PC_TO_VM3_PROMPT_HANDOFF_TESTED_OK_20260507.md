# PC -> VM3 Prompt Handoff
Status: TESTED_OK
Date: 2026-05-07

PC source root: E:\IMPERIUM\PROMPT_OUTBOX_TO_VM3
VM3 target root: /home/vboxuser3/Desktop/IMPERIUM_STAGING/bridge_exchange/current_task_inputs

SSH user: vboxuser3
SSH host: 127.0.0.1
SSH port: 2225
SSH key: C:\Users\PC\.ssh\imperium_pc_to_vm3_ed25519_20260418

Folder contract:
PC: E:\IMPERIUM\PROMPT_OUTBOX_TO_VM3\01_READY_TO_SEND\<STEP_ID>\PROMPT.txt
VM3: /home/vboxuser3/Desktop/IMPERIUM_STAGING/bridge_exchange/current_task_inputs/<STEP_ID>/PROMPT.txt

Working tested sequence:
1. Create STEP_ID folder on PC.
2. Create PROMPT.txt as UTF-8.
3. ssh mkdir remote step folder.
4. scp PROMPT.txt to VM3.
5. sha256sum remote prompt.
6. xdg-open remote prompt on VM3 desktop.

Expected success: remote file exists, sha256 printed, OPEN_SENT printed, PROMPT.txt opens on VM3.

Rules: one step = one folder; no secrets; staging only; not canon.

Verdict: PASS
