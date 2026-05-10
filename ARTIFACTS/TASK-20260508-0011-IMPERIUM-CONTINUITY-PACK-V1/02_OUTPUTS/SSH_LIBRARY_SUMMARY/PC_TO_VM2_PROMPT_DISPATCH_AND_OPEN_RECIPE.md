# PC TO VM2 PROMPT DISPATCH AND OPEN RECIPE

Status:
VERIFIED_MANUALLY

Purpose:
Create a prompt file on PC, send it to VM2 worker inbox, verify delivery, and open it on VM2 in a graphical text editor for manual copying.

Contour from:
PC

Contour to:
VM2

VM2 worker root:
/home/vboxuser2/IMPERIUM_WORKER_ROOM

Remote prompt target:
/home/vboxuser2/IMPERIUM_WORKER_ROOM/01_INBOX/tasks/<TASK_ID>/PROMPT.md

Important:
- This recipe uses TASK_ID-specific folders.
- Do not use latest logic.
- Do not write to THRONE.
- Do not write to VM3.
- Do not delete files.
- Do not store raw secrets in shareable artifacts.

PowerShell usage pattern:

$Key = "C:\Users\PC\.ssh\imperium_pc_to_vm2_ed25519_20260418"
$Port = 2223
$UserHost = "vboxuser2@127.0.0.1"
$TaskId = "TASK-TEST-VM2-PROMPT-COPY"

$LocalPrompt = "E:\IMPERIUM\ARTIFACTS\$TaskId\01_INPUTS\PROMPT.md"
$RemoteDir = "/home/vboxuser2/IMPERIUM_WORKER_ROOM/01_INBOX/tasks/$TaskId"
$RemotePrompt = "$RemoteDir/PROMPT.md"

Create local prompt on PC:

New-Item -ItemType Directory -Force -Path (Split-Path $LocalPrompt) | Out-Null
notepad $LocalPrompt

Send prompt to VM2:

ssh -i $Key -p $Port $UserHost "mkdir -p '$RemoteDir'"
scp -i $Key -P $Port "$LocalPrompt" "${UserHost}:$RemotePrompt"

Verify delivery and sha256:

ssh -i $Key -p $Port $UserHost "ls -la '$RemoteDir' && sha256sum '$RemotePrompt'"

Print prompt back to PC terminal:

ssh -i $Key -p $Port $UserHost "echo '--- PROMPT BEGIN ---'; cat '$RemotePrompt'; echo '--- PROMPT END ---'"

Open prompt on VM2 in graphical text editor:

ssh -i $Key -p $Port $UserHost "export DISPLAY=:0; export XDG_RUNTIME_DIR=/run/user/1000; export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus; nohup gnome-text-editor '$RemotePrompt' >/tmp/imperium_open_prompt.log 2>&1 &"

If editor does not open, check VM2 log:

ssh -i $Key -p $Port $UserHost "cat /tmp/imperium_open_prompt.log"

Expected result:
- PROMPT.md exists on VM2 under assigned TASK_ID folder.
- sha256sum command returns hash for remote PROMPT.md.
- gnome-text-editor opens PROMPT.md on VM2 desktop.
- User can select/copy prompt manually.

Forbidden reuse:
- THRONE writes
- VM3 writes
- auto-sync
- deleting files
- latest bundle fetching
- secret export
