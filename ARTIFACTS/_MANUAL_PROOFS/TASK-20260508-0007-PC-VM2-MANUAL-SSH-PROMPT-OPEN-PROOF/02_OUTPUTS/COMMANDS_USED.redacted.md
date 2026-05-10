# COMMANDS USED — REDACTED MANUAL PROOF

Status:
VERIFIED_MANUALLY_BY_OWNER

Purpose:
Manual PC to VM2 prompt dispatch and open workflow.

## Access check

ssh -i REDACTED_LOCAL_KEY_PATH -p REDACTED_PORT REDACTED_USER@REDACTED_HOST "echo VM2_OK && whoami && hostname && pwd && ls -la /home/vboxuser2/IMPERIUM_WORKER_ROOM"

Observed:
- VM2_OK returned.
- User: vboxuser2
- Host: GPT2
- Worker root exists:
  /home/vboxuser2/IMPERIUM_WORKER_ROOM

## Prompt dispatch pattern

Local prompt:
E:\IMPERIUM\ARTIFACTS\<TASK_ID>\01_INPUTS\PROMPT.md

Remote prompt:
 /home/vboxuser2/IMPERIUM_WORKER_ROOM/01_INBOX/tasks/<TASK_ID>/PROMPT.md

Commands:
ssh -i REDACTED_LOCAL_KEY_PATH -p REDACTED_PORT REDACTED_USER@REDACTED_HOST "mkdir -p '<REMOTE_TASK_DIR>'"
scp -i REDACTED_LOCAL_KEY_PATH -P REDACTED_PORT "<LOCAL_PROMPT>" REDACTED_USER@REDACTED_HOST:"<REMOTE_PROMPT>"

## Delivery verification

ssh -i REDACTED_LOCAL_KEY_PATH -p REDACTED_PORT REDACTED_USER@REDACTED_HOST "ls -la '<REMOTE_TASK_DIR>' && sha256sum '<REMOTE_PROMPT>'"

Observed:
- PROMPT.md delivered to VM2.
- sha256sum returned successfully.

## Open prompt on VM2 in graphical text editor

ssh -i REDACTED_LOCAL_KEY_PATH -p REDACTED_PORT REDACTED_USER@REDACTED_HOST "export DISPLAY=:0; export XDG_RUNTIME_DIR=/run/user/1000; export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus; nohup gnome-text-editor '<REMOTE_PROMPT>' >/tmp/imperium_open_prompt.log 2>&1 &"

Observed:
- gnome-text-editor opened PROMPT.md on VM2.
- Owner confirmed file opened successfully.

Forbidden reuse:
- Do not write to THRONE.
- Do not write to VM3.
- Do not delete files.
- Do not use latest bundle logic.
- Do not export raw secrets.
