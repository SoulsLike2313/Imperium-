# PC TO VM2 WORKER ROOM RECIPES

## Purpose
Verified manual recipes for accessing VM2 worker room.

## Route alias
PC_TO_VM2_PROMPT_DISPATCH_V1

## Recipes

### Check connectivity
ssh -i REDACTED_LOCAL_IDENTITY_PATH -p REDACTED_PORT REDACTED_USER@REDACTED_HOST "whoami; pwd; hostname"

### Show worker root
ssh -i REDACTED_LOCAL_IDENTITY_PATH -p REDACTED_PORT REDACTED_USER@REDACTED_HOST "ls -lah ~/IMPERIUM_WORKER_ROOM"

### Create worker room folders
ssh -i REDACTED_LOCAL_IDENTITY_PATH -p REDACTED_PORT REDACTED_USER@REDACTED_HOST "mkdir -p <worker_room_subfolders>"

### Upload semantic file
scp -i REDACTED_LOCAL_IDENTITY_PATH -P REDACTED_PORT <local_file> REDACTED_USER@REDACTED_HOST:~/IMPERIUM_WORKER_ROOM/<target_file>

### List task inbox
ssh -i REDACTED_LOCAL_IDENTITY_PATH -p REDACTED_PORT REDACTED_USER@REDACTED_HOST "ls -lah ~/IMPERIUM_WORKER_ROOM/01_INBOX/tasks"

### List stage bundle outbox
ssh -i REDACTED_LOCAL_IDENTITY_PATH -p REDACTED_PORT REDACTED_USER@REDACTED_HOST "ls -lah ~/IMPERIUM_WORKER_ROOM/03_OUTBOX/stage_bundles"

### Calculate remote sha256
ssh -i REDACTED_LOCAL_IDENTITY_PATH -p REDACTED_PORT REDACTED_USER@REDACTED_HOST "sha256sum ~/IMPERIUM_WORKER_ROOM/<file_name>"

## Forbidden
- Do not delete.
- Do not write to THRONE.
- Do not use latest bundle logic.
- Do not store raw secrets.
