# VM2 WORKER FOLDER SEMANTIC MAP

## ~/IMPERIUM_WORKER_ROOM

Path:
~/IMPERIUM_WORKER_ROOM

Role:
VM2 worker execution root.

What lives here:
- Worker subfolders
- Semantic files

Allowed writes:
- Write worker-local outputs

Forbidden writes:
- write to THRONE
- delete unrelated files
- autosync
- run broad scan outside worker root
- export secrets

Inputs:
- Task packages from PC

Outputs:
- Stage outputs and evidence

Related PC zones:
- E:\IMPERIUM\ARTIFACTS
- E:\IMPERIUM\SSH_COMMAND_LIBRARY
- E:\IMPERIUM\PC_ENGINEERING_ROOM

Agent instruction:
Operate only inside worker root.

Status:
active

## 01_INBOX

Path:
~/IMPERIUM_WORKER_ROOM/01_INBOX

Role:
Received task packages from PC.

What lives here:
- Inbound package folders

Allowed writes:
- Store inbound package files

Forbidden writes:
- write to THRONE
- delete unrelated files
- autosync
- run broad scan outside worker root
- export secrets

Inputs:
- PC dispatch

Outputs:
- Task package folders

Related PC zones:
- E:\IMPERIUM\ARTIFACTS
- E:\IMPERIUM\SSH_COMMAND_LIBRARY
- E:\IMPERIUM\PC_ENGINEERING_ROOM

Agent instruction:
Keep inbound task packages only.

Status:
active

## 01_INBOX/tasks

Path:
~/IMPERIUM_WORKER_ROOM/01_INBOX/tasks

Role:
Task package folders by TASK_ID.

What lives here:
- TASK_ID package folders

Allowed writes:
- Create folders by TASK_ID

Forbidden writes:
- write to THRONE
- delete unrelated files
- autosync
- run broad scan outside worker root
- export secrets

Inputs:
- Task payload files

Outputs:
- Per-task package folders

Related PC zones:
- E:\IMPERIUM\ARTIFACTS
- E:\IMPERIUM\SSH_COMMAND_LIBRARY
- E:\IMPERIUM\PC_ENGINEERING_ROOM

Agent instruction:
Use strict TASK_ID folder separation.

Status:
active

## 02_ACTIVE

Path:
~/IMPERIUM_WORKER_ROOM/02_ACTIVE

Role:
Current assigned stage workspace.

What lives here:
- Stage work files

Allowed writes:
- Write assigned stage files

Forbidden writes:
- write to THRONE
- delete unrelated files
- autosync
- run broad scan outside worker root
- export secrets

Inputs:
- Assigned stage package

Outputs:
- Intermediate stage files

Related PC zones:
- E:\IMPERIUM\ARTIFACTS
- E:\IMPERIUM\SSH_COMMAND_LIBRARY
- E:\IMPERIUM\PC_ENGINEERING_ROOM

Agent instruction:
Execute only assigned stage here.

Status:
active

## 03_OUTBOX

Path:
~/IMPERIUM_WORKER_ROOM/03_OUTBOX

Role:
Completed outputs waiting for PC fetch.

What lives here:
- Prepared output files

Allowed writes:
- Write completed outputs

Forbidden writes:
- write to THRONE
- delete unrelated files
- autosync
- run broad scan outside worker root
- export secrets

Inputs:
- Stage results

Outputs:
- Fetch-ready outputs

Related PC zones:
- E:\IMPERIUM\ARTIFACTS
- E:\IMPERIUM\SSH_COMMAND_LIBRARY
- E:\IMPERIUM\PC_ENGINEERING_ROOM

Agent instruction:
Prepare outputs for explicit fetch routes only.

Status:
active

## 03_OUTBOX/stage_bundles

Path:
~/IMPERIUM_WORKER_ROOM/03_OUTBOX/stage_bundles

Role:
Stage bundles named by TASK_ID/STAGE_ID/CONTOUR_ID/RUN_ID.

What lives here:
- Stage bundle zips
- Hash files

Allowed writes:
- Write explicitly named bundles

Forbidden writes:
- latest bundle logic
- write to THRONE
- delete
- autosync
- run broad scan outside worker root
- export secrets

Inputs:
- Stage outputs and manifests

Outputs:
- Stage bundle artifacts

Related PC zones:
- E:\IMPERIUM\ARTIFACTS
- E:\IMPERIUM\SSH_COMMAND_LIBRARY
- E:\IMPERIUM\PC_ENGINEERING_ROOM

Agent instruction:
Do not use latest logic; use explicit IDs.

Status:
active

## 04_RECEIPTS

Path:
~/IMPERIUM_WORKER_ROOM/04_RECEIPTS

Role:
Proof of actions performed by VM2.

What lives here:
- Action and stage receipts

Allowed writes:
- Write receipts per stage action

Forbidden writes:
- write to THRONE
- delete unrelated files
- autosync
- run broad scan outside worker root
- export secrets

Inputs:
- Execution trace

Outputs:
- Receipt files

Related PC zones:
- E:\IMPERIUM\ARTIFACTS
- E:\IMPERIUM\SSH_COMMAND_LIBRARY
- E:\IMPERIUM\PC_ENGINEERING_ROOM

Agent instruction:
Emit receipts for each stage action.

Status:
active

## 05_MANIFESTS

Path:
~/IMPERIUM_WORKER_ROOM/05_MANIFESTS

Role:
File lists and bundle manifests.

What lives here:
- Output manifests
- Bundle manifests

Allowed writes:
- Write manifest files

Forbidden writes:
- write to THRONE
- delete unrelated files
- autosync
- run broad scan outside worker root
- export secrets

Inputs:
- Produced file lists

Outputs:
- Manifest files

Related PC zones:
- E:\IMPERIUM\ARTIFACTS
- E:\IMPERIUM\SSH_COMMAND_LIBRARY
- E:\IMPERIUM\PC_ENGINEERING_ROOM

Agent instruction:
Maintain deterministic manifests for verification.

Status:
active

## 06_HASHES

Path:
~/IMPERIUM_WORKER_ROOM/06_HASHES

Role:
SHA256 and integrity files.

What lives here:
- SHA256 checksum files

Allowed writes:
- Write sha256 records

Forbidden writes:
- write to THRONE
- delete unrelated files
- autosync
- run broad scan outside worker root
- export secrets

Inputs:
- Output file paths

Outputs:
- Integrity files

Related PC zones:
- E:\IMPERIUM\ARTIFACTS
- E:\IMPERIUM\SSH_COMMAND_LIBRARY
- E:\IMPERIUM\PC_ENGINEERING_ROOM

Agent instruction:
Generate hashes for outputs and bundles.

Status:
active

## 07_LOCAL_TOOLS

Path:
~/IMPERIUM_WORKER_ROOM/07_LOCAL_TOOLS

Role:
Safe worker helper scripts.

What lives here:
- Helper scripts

Allowed writes:
- Write minimal safe helpers

Forbidden writes:
- write to THRONE
- delete unrelated files
- autosync
- run broad scan outside worker root
- export secrets

Inputs:
- Execution requirements

Outputs:
- Local helper tools

Related PC zones:
- E:\IMPERIUM\ARTIFACTS
- E:\IMPERIUM\SSH_COMMAND_LIBRARY
- E:\IMPERIUM\PC_ENGINEERING_ROOM

Agent instruction:
Keep tools minimal and task-scoped.

Status:
active

## 08_CONFIG_TEMPLATES

Path:
~/IMPERIUM_WORKER_ROOM/08_CONFIG_TEMPLATES

Role:
Templates only. No raw secrets.

What lives here:
- Config templates

Allowed writes:
- Write non-secret templates

Forbidden writes:
- raw secrets
- private keys
- tokens
- write to THRONE
- delete
- autosync
- run broad scan outside worker root
- export secrets

Inputs:
- Template requirements

Outputs:
- Reusable template files

Related PC zones:
- E:\IMPERIUM\ARTIFACTS
- E:\IMPERIUM\SSH_COMMAND_LIBRARY
- E:\IMPERIUM\PC_ENGINEERING_ROOM

Agent instruction:
Store templates only; no credentials.

Status:
active

## 09_LOCAL_STATE

Path:
~/IMPERIUM_WORKER_ROOM/09_LOCAL_STATE

Role:
Temporary local state. Not canon. Not portable unless explicitly bundled.

What lives here:
- Temporary runtime state

Allowed writes:
- Write temporary state files

Forbidden writes:
- write to THRONE
- delete unrelated files
- autosync
- run broad scan outside worker root
- export secrets

Inputs:
- Runtime context

Outputs:
- Local temporary state

Related PC zones:
- E:\IMPERIUM\ARTIFACTS
- E:\IMPERIUM\SSH_COMMAND_LIBRARY
- E:\IMPERIUM\PC_ENGINEERING_ROOM

Agent instruction:
Treat as non-canon local scratch state.

Status:
active

## 99_WORKER_STATUS

Path:
~/IMPERIUM_WORKER_ROOM/99_WORKER_STATUS

Role:
Current worker status, health, last task, blockers.

What lives here:
- Status files
- Health markers

Allowed writes:
- Write worker status files

Forbidden writes:
- write to THRONE
- delete unrelated files
- autosync
- run broad scan outside worker root
- export secrets

Inputs:
- Worker runtime signals

Outputs:
- Status reports

Related PC zones:
- E:\IMPERIUM\ARTIFACTS
- E:\IMPERIUM\SSH_COMMAND_LIBRARY
- E:\IMPERIUM\PC_ENGINEERING_ROOM

Agent instruction:
Keep status explicit and current.

Status:
active

