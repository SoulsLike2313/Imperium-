# VM2 TASK PACKAGE

TASK_ID:
TASK-20260508-0008-VM2-LEGACY-INBOX-REPAIR

STAGE_ID:
STAGE-001-VM2-LEGACY-INBOX-REPAIR

RUN_ID:
RUN-20260508-0001

CONTOUR:
VM2

ROLE:
SERVITOR_VM2

MODE:
Work only inside /home/vboxuser2/IMPERIUM_WORKER_ROOM.
Do not touch THRONE.
Do not touch VM3.
Do not write to PC.
Do not delete anything.
Do not auto-sync.
Do not scan outside /home/vboxuser2/IMPERIUM_WORKER_ROOM.
All generated system files must be English only.

PURPOSE:
Repair the VM2 worker room structural drift caused by the legacy folder:
/home/vboxuser2/IMPERIUM_WORKER_ROOM/INBOX

The accepted new inbox path is:
/home/vboxuser2/IMPERIUM_WORKER_ROOM/01_INBOX/tasks

The old INBOX folder must not be deleted.
It must be moved into a legacy import area with manifest and receipt, if it exists.

TARGET WORKER ROOT:
/home/vboxuser2/IMPERIUM_WORKER_ROOM

EXPECTED ACTIONS:

STAGE 1 — PREFLIGHT
1. Confirm current path:
   /home/vboxuser2/IMPERIUM_WORKER_ROOM
2. Confirm required folders exist:
   01_INBOX
   01_INBOX/tasks
   02_ACTIVE
   03_OUTBOX
   03_OUTBOX/stage_bundles
   04_RECEIPTS
   05_MANIFESTS
   06_HASHES
   07_LOCAL_TOOLS
   08_CONFIG_TEMPLATES
   09_LOCAL_STATE
   99_WORKER_STATUS
3. Write preflight report:
   /home/vboxuser2/IMPERIUM_WORKER_ROOM/04_RECEIPTS/TASK-20260508-0008-VM2-LEGACY-INBOX-REPAIR_PREFLIGHT.md

STAGE 2 — LEGACY INBOX CHECK
1. Check if this folder exists:
   /home/vboxuser2/IMPERIUM_WORKER_ROOM/INBOX
2. If it does not exist:
   write report saying legacy INBOX not found.
3. If it exists:
   do not delete it.
   create:
   /home/vboxuser2/IMPERIUM_WORKER_ROOM/09_LOCAL_STATE/legacy_imports/TASK-20260508-0008-VM2-LEGACY-INBOX-REPAIR/
   move old INBOX into:
   /home/vboxuser2/IMPERIUM_WORKER_ROOM/09_LOCAL_STATE/legacy_imports/TASK-20260508-0008-VM2-LEGACY-INBOX-REPAIR/INBOX_legacy_from_smoke_test
4. Record the original path and new path in a manifest.

STAGE 3 — MANIFESTS AND RECEIPTS
Create these files:

/home/vboxuser2/IMPERIUM_WORKER_ROOM/05_MANIFESTS/TASK-20260508-0008-VM2-LEGACY-INBOX-REPAIR_LEGACY_MOVE_MANIFEST.csv

CSV columns:
source_path,target_path,item_type,action,deleted,notes

/home/vboxuser2/IMPERIUM_WORKER_ROOM/04_RECEIPTS/TASK-20260508-0008-VM2-LEGACY-INBOX-REPAIR_STAGE_RECEIPT.md

Receipt fields:
task_id:
stage_id:
run_id:
contour:
legacy_inbox_found: YES/NO
legacy_inbox_moved: YES/NO
deleted_anything: NO
touched_throne: NO
touched_vm3: NO
wrote_to_pc: NO
autosync_used: NO
verdict: PASS/BLOCKED
notes:

STAGE 4 — UPDATE WORKER STATUS
Update or create:

/home/vboxuser2/IMPERIUM_WORKER_ROOM/99_WORKER_STATUS/WORKER_STATUS.json

Required meaning:
- VM2 worker room exists.
- accepted inbox is 01_INBOX/tasks.
- legacy INBOX is not active.
- ready_for_task_package_receive: true
- ready_for_stage_execution: false
- ready_for_fetch_protocol: false

STAGE 5 — CREATE STAGE OUTPUT FOLDER
Create:

/home/vboxuser2/IMPERIUM_WORKER_ROOM/03_OUTBOX/stage_bundles/TASK-20260508-0008-VM2-LEGACY-INBOX-REPAIR__STAGE-001-VM2-LEGACY-INBOX-REPAIR__CONTOUR-VM2__RUN-20260508-0001/

Inside it place copies of:
- stage receipt
- legacy move manifest
- worker status json
- preflight report
- notes or blocker report if needed

STAGE 6 — CREATE SHA256SUMS
Inside the stage output folder create:

SHA256SUMS.txt

Include hashes for all files in the stage output folder, except SHA256SUMS.txt itself.

STAGE 7 — CREATE STAGE BUNDLE
Create bundle in:

/home/vboxuser2/IMPERIUM_WORKER_ROOM/03_OUTBOX/stage_bundles/

Preferred zip name:
TASK-20260508-0008-VM2-LEGACY-INBOX-REPAIR__STAGE-001-VM2-LEGACY-INBOX-REPAIR__CONTOUR-VM2__RUN-20260508-0001__STAGE_BUNDLE.zip

If zip is not available, create tar.gz instead:
TASK-20260508-0008-VM2-LEGACY-INBOX-REPAIR__STAGE-001-VM2-LEGACY-INBOX-REPAIR__CONTOUR-VM2__RUN-20260508-0001__STAGE_BUNDLE.tar.gz

Create sha256 next to the bundle.

STAGE 8 — FINAL VM2 RESPONSE
After completing the task, respond in this short format:

1) Step name
VM2_LEGACY_INBOX_REPAIR_V1

2) Bundle path
<full remote path to created bundle>

3) Verdict
PASS / BLOCKED

4) Comment for Owner
3-4 short Russian lines:
- legacy INBOX found or not;
- moved or not;
- bundle created or blocked;
- next step: PC fetch and verify.

PASS CRITERIA:
- old INBOX was either not present or moved without deletion;
- accepted inbox remains 01_INBOX/tasks;
- receipt created;
- manifest created;
- worker status updated;
- stage bundle created;
- sha256 created;
- no THRONE/VM3/PC write;
- no delete.

If any required step fails:
verdict BLOCKED and explain why.
