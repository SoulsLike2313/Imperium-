# IMPERIUM FOLDER SEMANTIC MAP V1

## Purpose
This document is the address and semantic map for IMPERIUM folders.
It is used by agents and future Administratum to understand folder meaning and write boundaries.

## Root law
- E:\IMPERIUM root contains only major zones.
- Task artifacts go to E:\IMPERIUM\ARTIFACTS\<TASK_ID>\...
- Active engineering work goes to PC_ENGINEERING_ROOM.
- Observed historical copies go to OBSERVED.
- SSH route tools go to SSH_COMMAND_LIBRARY.
- Old or inactive material goes to ARCHIVE.
- No root-level task output files.
- No secrets in maps.
- No THRONE write from this PC mapping task.

## Major zones

### ARCHIVE

Path:
E:\IMPERIUM\ARCHIVE

Role:
Archive zone for old, inactive, or legacy materials that should not stay in active root.

What lives here:
- Historical imports
- Legacy batches
- Old task context

Allowed writes:
- Owner-approved archival moves
- Archive manifests and rollback notes

Forbidden writes:
- Active task outputs without task routing
- Secrets without redaction

Inputs:
- Legacy folders from root hygiene
- Inactive snapshots

Outputs:
- Archived folders and manifests

Related zones:
- ARTIFACTS
- OBSERVED
- PC_ENGINEERING_ROOM

Agent instruction:
Use ARCHIVE for storage, not for active execution outputs.

Status:
archive

Canon status:
not_canon

Artifact policy:
Keep archive evidence pointers in ARTIFACTS by TASK_ID when relevant.

Notes:
- No delete policy applies.

### ARTIFACTS

Path:
E:\IMPERIUM\ARTIFACTS

Role:
Primary evidence root for task outputs, proofs, manifests, and final bundles by TASK_ID.

What lives here:
- Task folders
- Receipts
- Hashes
- Final bundles

Allowed writes:
- Files under E:\IMPERIUM\ARTIFACTS\<TASK_ID>\...
- Index updates by task scope

Forbidden writes:
- Raw secrets
- Untracked random files
- Root-level dumps

Inputs:
- Task inputs and source pointers

Outputs:
- Task outputs and final bundle artifacts

Related zones:
- PC_ENGINEERING_ROOM
- SSH_COMMAND_LIBRARY
- ARCHIVE

Agent instruction:
Always write task outputs into a dedicated TASK_ID folder.

Status:
active

Canon status:
not_canon

Artifact policy:
All proofs and bundles must be registered by TASK_ID.

Notes:
- Artifacts are evidence surfaces, not canonical authority.

### OBSERVED

Path:
E:\IMPERIUM\OBSERVED

Role:
Read-only historical and observed contour copies for reference analysis.

What lives here:
- Observed copies
- Historical contour snapshots
- Legacy observed imports

Allowed writes:
- Only owner-approved observed imports
- Read-only mapping notes

Forbidden writes:
- Mutation of observed copies
- Task output bundles

Inputs:
- Imported observed folders

Outputs:
- Reference-only snapshots

Related zones:
- PC_ENGINEERING_ROOM
- ARCHIVE

Agent instruction:
Treat OBSERVED content as read-only reference unless a dedicated task says otherwise.

Status:
observed

Canon status:
not_canon

Artifact policy:
Use ARTIFACTS for proof of analysis performed on observed copies.

Notes:
- No deep mutation from root mapping tasks.

### PC_ENGINEERING_ROOM

Path:
E:\IMPERIUM\PC_ENGINEERING_ROOM

Role:
Active engineering headquarters for architecture, reviews, labs, maps, and decision preparation.

What lives here:
- System maps
- Architecture docs
- Review and test materials
- Owner decision drafts

Allowed writes:
- Engineering docs, maps, and lab outputs

Forbidden writes:
- THRONE writes
- Untracked root-level task outputs

Inputs:
- Task questions
- Observed references
- SSH diagnostics summaries

Outputs:
- Engineering maps, plans, and controlled reports

Related zones:
- ARTIFACTS
- SSH_COMMAND_LIBRARY
- OBSERVED

Agent instruction:
Keep active engineering work here; publish proof copies to ARTIFACTS.

Status:
active

Canon status:
not_canon

Artifact policy:
Any task result proof should also be stored under ARTIFACTS\<TASK_ID>\.

Notes:
- Engineering room is not admission authority.

### SSH_COMMAND_LIBRARY

Path:
E:\IMPERIUM\SSH_COMMAND_LIBRARY

Role:
Library of SSH route knowledge, diagnostics, tools, and tested recipes.

What lives here:
- Route profiles
- Send/fetch/open instructions
- Diagnostics
- Tools
- Baseline route contexts

Allowed writes:
- Route docs and helper scripts
- Diagnostics receipts

Forbidden writes:
- Private key contents
- Raw credentials
- Unrelated task bundles

Inputs:
- Route requirements and diagnostics results

Outputs:
- Reusable route instructions and helper tools

Related zones:
- ARTIFACTS
- PC_ENGINEERING_ROOM

Agent instruction:
Keep route tools here; keep usage proof in ARTIFACTS.

Status:
active

Canon status:
not_canon

Artifact policy:
Route usage evidence must be copied or pointed from ARTIFACTS by TASK_ID.

Notes:
- No secrets in route docs.

## PC_ENGINEERING_ROOM subfolders

### 00_SYSTEM_MAPS

Path:
E:\IMPERIUM\PC_ENGINEERING_ROOM\00_SYSTEM_MAPS

Role:
System maps, folder maps, address maps, and machine-readable structure maps.

What lives here:
- Folder-specific engineering materials

Allowed writes:
- Scoped documents and receipts

Forbidden writes:
- Secrets
- Out-of-scope binaries

Inputs:
- Engineering inputs from active tasks

Outputs:
- Engineering outputs and planning docs

Related zones:
- PC_ENGINEERING_ROOM
- ARTIFACTS

Agent instruction:
Write only files that match 00_SYSTEM_MAPS purpose and keep evidence in ARTIFACTS.

Status:
active

Canon status:
not_canon

Artifact policy:
Task-level proof copy belongs in ARTIFACTS.

Notes:
- Subfolder policy follows engineering room boundaries.

### 01_CURRENT_STATE

Path:
E:\IMPERIUM\PC_ENGINEERING_ROOM\01_CURRENT_STATE

Role:
Current working state, active baseline, blocked areas, and current truth snapshot.

What lives here:
- Folder-specific engineering materials

Allowed writes:
- Scoped documents and receipts

Forbidden writes:
- Secrets
- Out-of-scope binaries

Inputs:
- Engineering inputs from active tasks

Outputs:
- Engineering outputs and planning docs

Related zones:
- PC_ENGINEERING_ROOM
- ARTIFACTS

Agent instruction:
Write only files that match 01_CURRENT_STATE purpose and keep evidence in ARTIFACTS.

Status:
active

Canon status:
not_canon

Artifact policy:
Task-level proof copy belongs in ARTIFACTS.

Notes:
- Subfolder policy follows engineering room boundaries.

### 02_ARCHITECTURE_ATLAS

Path:
E:\IMPERIUM\PC_ENGINEERING_ROOM\02_ARCHITECTURE_ATLAS

Role:
Architecture, contours, organs, authority model, and task/stage/run model.

What lives here:
- Folder-specific engineering materials

Allowed writes:
- Scoped documents and receipts

Forbidden writes:
- Secrets
- Out-of-scope binaries

Inputs:
- Engineering inputs from active tasks

Outputs:
- Engineering outputs and planning docs

Related zones:
- PC_ENGINEERING_ROOM
- ARTIFACTS

Agent instruction:
Write only files that match 02_ARCHITECTURE_ATLAS purpose and keep evidence in ARTIFACTS.

Status:
active

Canon status:
not_canon

Artifact policy:
Task-level proof copy belongs in ARTIFACTS.

Notes:
- Subfolder policy follows engineering room boundaries.

### 03_OWNER_DECISIONS

Path:
E:\IMPERIUM\PC_ENGINEERING_ROOM\03_OWNER_DECISIONS

Role:
Owner decision records: approve, reject, block, rerun, repair, defer.

What lives here:
- Folder-specific engineering materials

Allowed writes:
- Scoped documents and receipts

Forbidden writes:
- Secrets
- Out-of-scope binaries

Inputs:
- Engineering inputs from active tasks

Outputs:
- Engineering outputs and planning docs

Related zones:
- PC_ENGINEERING_ROOM
- ARTIFACTS

Agent instruction:
Write only files that match 03_OWNER_DECISIONS purpose and keep evidence in ARTIFACTS.

Status:
active

Canon status:
not_canon

Artifact policy:
Task-level proof copy belongs in ARTIFACTS.

Notes:
- Subfolder policy follows engineering room boundaries.

### 04_REVIEW_BENCH

Path:
E:\IMPERIUM\PC_ENGINEERING_ROOM\04_REVIEW_BENCH

Role:
Review inputs and outputs for Logos and Speculum, including blocker lists.

What lives here:
- Folder-specific engineering materials

Allowed writes:
- Scoped documents and receipts

Forbidden writes:
- Secrets
- Out-of-scope binaries

Inputs:
- Engineering inputs from active tasks

Outputs:
- Engineering outputs and planning docs

Related zones:
- PC_ENGINEERING_ROOM
- ARTIFACTS

Agent instruction:
Write only files that match 04_REVIEW_BENCH purpose and keep evidence in ARTIFACTS.

Status:
active

Canon status:
not_canon

Artifact policy:
Task-level proof copy belongs in ARTIFACTS.

Notes:
- Subfolder policy follows engineering room boundaries.

### 05_TEST_LAB

Path:
E:\IMPERIUM\PC_ENGINEERING_ROOM\05_TEST_LAB

Role:
Smoke tests, fixtures, validators, hardware probe, and resource checks.

What lives here:
- Folder-specific engineering materials

Allowed writes:
- Scoped documents and receipts

Forbidden writes:
- Secrets
- Out-of-scope binaries

Inputs:
- Engineering inputs from active tasks

Outputs:
- Engineering outputs and planning docs

Related zones:
- PC_ENGINEERING_ROOM
- ARTIFACTS

Agent instruction:
Write only files that match 05_TEST_LAB purpose and keep evidence in ARTIFACTS.

Status:
active

Canon status:
not_canon

Artifact policy:
Task-level proof copy belongs in ARTIFACTS.

Notes:
- Subfolder policy follows engineering room boundaries.

### 06_ORGANS_WORKSHOP

Path:
E:\IMPERIUM\PC_ENGINEERING_ROOM\06_ORGANS_WORKSHOP

Role:
Organ templates and pilot organs before operational use.

What lives here:
- Folder-specific engineering materials

Allowed writes:
- Scoped documents and receipts

Forbidden writes:
- Secrets
- Out-of-scope binaries

Inputs:
- Engineering inputs from active tasks

Outputs:
- Engineering outputs and planning docs

Related zones:
- PC_ENGINEERING_ROOM
- ARTIFACTS

Agent instruction:
Write only files that match 06_ORGANS_WORKSHOP purpose and keep evidence in ARTIFACTS.

Status:
active

Canon status:
not_canon

Artifact policy:
Task-level proof copy belongs in ARTIFACTS.

Notes:
- Subfolder policy follows engineering room boundaries.

### 07_WORKER_TEMPLATE_LAB

Path:
E:\IMPERIUM\PC_ENGINEERING_ROOM\07_WORKER_TEMPLATE_LAB

Role:
Worker room templates, VM2 protocol drafts, and stage bundle rules.

What lives here:
- Folder-specific engineering materials

Allowed writes:
- Scoped documents and receipts

Forbidden writes:
- Secrets
- Out-of-scope binaries

Inputs:
- Engineering inputs from active tasks

Outputs:
- Engineering outputs and planning docs

Related zones:
- PC_ENGINEERING_ROOM
- ARTIFACTS

Agent instruction:
Write only files that match 07_WORKER_TEMPLATE_LAB purpose and keep evidence in ARTIFACTS.

Status:
active

Canon status:
not_canon

Artifact policy:
Task-level proof copy belongs in ARTIFACTS.

Notes:
- Subfolder policy follows engineering room boundaries.

### 08_LOCAL_LLM_LAB

Path:
E:\IMPERIUM\PC_ENGINEERING_ROOM\08_LOCAL_LLM_LAB

Role:
Local LLM candidates, resource policy, wrappers, and code-health tasks.

What lives here:
- Folder-specific engineering materials

Allowed writes:
- Scoped documents and receipts

Forbidden writes:
- Secrets
- Out-of-scope binaries

Inputs:
- Engineering inputs from active tasks

Outputs:
- Engineering outputs and planning docs

Related zones:
- PC_ENGINEERING_ROOM
- ARTIFACTS

Agent instruction:
Write only files that match 08_LOCAL_LLM_LAB purpose and keep evidence in ARTIFACTS.

Status:
active

Canon status:
not_canon

Artifact policy:
Task-level proof copy belongs in ARTIFACTS.

Notes:
- Subfolder policy follows engineering room boundaries.

### 09_INTERNET_RESEARCH_GATEWAY

Path:
E:\IMPERIUM\PC_ENGINEERING_ROOM\09_INTERNET_RESEARCH_GATEWAY

Role:
Controlled internet research, source registry, and no-secrets policy.

What lives here:
- Folder-specific engineering materials

Allowed writes:
- Scoped documents and receipts

Forbidden writes:
- Secrets
- Out-of-scope binaries

Inputs:
- Engineering inputs from active tasks

Outputs:
- Engineering outputs and planning docs

Related zones:
- PC_ENGINEERING_ROOM
- ARTIFACTS

Agent instruction:
Write only files that match 09_INTERNET_RESEARCH_GATEWAY purpose and keep evidence in ARTIFACTS.

Status:
active

Canon status:
not_canon

Artifact policy:
Task-level proof copy belongs in ARTIFACTS.

Notes:
- Subfolder policy follows engineering room boundaries.

### 10_RECEIPTS_AND_AUDIT

Path:
E:\IMPERIUM\PC_ENGINEERING_ROOM\10_RECEIPTS_AND_AUDIT

Role:
Audit records and engineering-room operation receipts.

What lives here:
- Folder-specific engineering materials

Allowed writes:
- Scoped documents and receipts

Forbidden writes:
- Secrets
- Out-of-scope binaries

Inputs:
- Engineering inputs from active tasks

Outputs:
- Engineering outputs and planning docs

Related zones:
- PC_ENGINEERING_ROOM
- ARTIFACTS

Agent instruction:
Write only files that match 10_RECEIPTS_AND_AUDIT purpose and keep evidence in ARTIFACTS.

Status:
active

Canon status:
not_canon

Artifact policy:
Task-level proof copy belongs in ARTIFACTS.

Notes:
- Subfolder policy follows engineering room boundaries.

### 11_QUARANTINE_NO_DELETE

Path:
E:\IMPERIUM\PC_ENGINEERING_ROOM\11_QUARANTINE_NO_DELETE

Role:
Move-only quarantine planning, rollback notes, and no-delete evidence.

What lives here:
- Folder-specific engineering materials

Allowed writes:
- Scoped documents and receipts

Forbidden writes:
- Secrets
- Out-of-scope binaries

Inputs:
- Engineering inputs from active tasks

Outputs:
- Engineering outputs and planning docs

Related zones:
- PC_ENGINEERING_ROOM
- ARTIFACTS

Agent instruction:
Write only files that match 11_QUARANTINE_NO_DELETE purpose and keep evidence in ARTIFACTS.

Status:
active

Canon status:
not_canon

Artifact policy:
Task-level proof copy belongs in ARTIFACTS.

Notes:
- Subfolder policy follows engineering room boundaries.

### 99_DASHBOARD

Path:
E:\IMPERIUM\PC_ENGINEERING_ROOM\99_DASHBOARD

Role:
Plain dashboard data for active tasks, blockers, barriers, and latest verified bundles.

What lives here:
- Folder-specific engineering materials

Allowed writes:
- Scoped documents and receipts

Forbidden writes:
- Secrets
- Out-of-scope binaries

Inputs:
- Engineering inputs from active tasks

Outputs:
- Engineering outputs and planning docs

Related zones:
- PC_ENGINEERING_ROOM
- ARTIFACTS

Agent instruction:
Write only files that match 99_DASHBOARD purpose and keep evidence in ARTIFACTS.

Status:
active

Canon status:
not_canon

Artifact policy:
Task-level proof copy belongs in ARTIFACTS.

Notes:
- Subfolder policy follows engineering room boundaries.

## SSH_COMMAND_LIBRARY subfolders

### 00_CONNECTION_PROFILES

Path:
E:\IMPERIUM\SSH_COMMAND_LIBRARY\00_CONNECTION_PROFILES

Role:
Redacted route profiles, aliases, allowed actions, and forbidden actions.

What lives here:
- Route-specific docs and helper content

Allowed writes:
- Route docs, tools, diagnostics notes

Forbidden writes:
- Private keys
- Passwords
- Raw tokens

Inputs:
- Route requirements

Outputs:
- Route instructions and scripts

Related zones:
- SSH_COMMAND_LIBRARY
- ARTIFACTS
- PC_ENGINEERING_ROOM

Agent instruction:
Use this folder for route tooling; register proof of use in ARTIFACTS.

Status:
active

Canon status:
not_canon

Artifact policy:
Proof of route execution must be saved in ARTIFACTS task folders.

Notes:
- Keep redacted and safe content only.

### 01_SEND_PROMPT_TO_VM

Path:
E:\IMPERIUM\SSH_COMMAND_LIBRARY\01_SEND_PROMPT_TO_VM

Role:
Dispatch instructions and future scripts for prompt and task packages.

What lives here:
- Route-specific docs and helper content

Allowed writes:
- Route docs, tools, diagnostics notes

Forbidden writes:
- Private keys
- Passwords
- Raw tokens

Inputs:
- Route requirements

Outputs:
- Route instructions and scripts

Related zones:
- SSH_COMMAND_LIBRARY
- ARTIFACTS
- PC_ENGINEERING_ROOM

Agent instruction:
Use this folder for route tooling; register proof of use in ARTIFACTS.

Status:
active

Canon status:
not_canon

Artifact policy:
Proof of route execution must be saved in ARTIFACTS task folders.

Notes:
- Keep redacted and safe content only.

### 02_FETCH_FROM_VM

Path:
E:\IMPERIUM\SSH_COMMAND_LIBRARY\02_FETCH_FROM_VM

Role:
Fetch instructions and future scripts for stage bundles by TASK/STAGE/CONTOUR/RUN.

What lives here:
- Route-specific docs and helper content

Allowed writes:
- Route docs, tools, diagnostics notes

Forbidden writes:
- Private keys
- Passwords
- Raw tokens

Inputs:
- Route requirements

Outputs:
- Route instructions and scripts

Related zones:
- SSH_COMMAND_LIBRARY
- ARTIFACTS
- PC_ENGINEERING_ROOM

Agent instruction:
Use this folder for route tooling; register proof of use in ARTIFACTS.

Status:
active

Canon status:
not_canon

Artifact policy:
Proof of route execution must be saved in ARTIFACTS task folders.

Notes:
- Keep redacted and safe content only.

### 03_OPEN_ON_VM

Path:
E:\IMPERIUM\SSH_COMMAND_LIBRARY\03_OPEN_ON_VM

Role:
Safe manual access commands for remote paths and shell checks.

What lives here:
- Route-specific docs and helper content

Allowed writes:
- Route docs, tools, diagnostics notes

Forbidden writes:
- Private keys
- Passwords
- Raw tokens

Inputs:
- Route requirements

Outputs:
- Route instructions and scripts

Related zones:
- SSH_COMMAND_LIBRARY
- ARTIFACTS
- PC_ENGINEERING_ROOM

Agent instruction:
Use this folder for route tooling; register proof of use in ARTIFACTS.

Status:
active

Canon status:
not_canon

Artifact policy:
Proof of route execution must be saved in ARTIFACTS task folders.

Notes:
- Keep redacted and safe content only.

### 04_DIAGNOSTICS

Path:
E:\IMPERIUM\SSH_COMMAND_LIBRARY\04_DIAGNOSTICS

Role:
SSH alive checks, remote path checks, ls proof, sha256 proof, and permission checks.

What lives here:
- Route-specific docs and helper content

Allowed writes:
- Route docs, tools, diagnostics notes

Forbidden writes:
- Private keys
- Passwords
- Raw tokens

Inputs:
- Route requirements

Outputs:
- Route instructions and scripts

Related zones:
- SSH_COMMAND_LIBRARY
- ARTIFACTS
- PC_ENGINEERING_ROOM

Agent instruction:
Use this folder for route tooling; register proof of use in ARTIFACTS.

Status:
active

Canon status:
not_canon

Artifact policy:
Proof of route execution must be saved in ARTIFACTS task folders.

Notes:
- Keep redacted and safe content only.

### 05_SUCCESSFUL_RECIPES

Path:
E:\IMPERIUM\SSH_COMMAND_LIBRARY\05_SUCCESSFUL_RECIPES

Role:
Verified working SSH and SCP recipes only.

What lives here:
- Route-specific docs and helper content

Allowed writes:
- Route docs, tools, diagnostics notes

Forbidden writes:
- Private keys
- Passwords
- Raw tokens

Inputs:
- Route requirements

Outputs:
- Route instructions and scripts

Related zones:
- SSH_COMMAND_LIBRARY
- ARTIFACTS
- PC_ENGINEERING_ROOM

Agent instruction:
Use this folder for route tooling; register proof of use in ARTIFACTS.

Status:
active

Canon status:
not_canon

Artifact policy:
Proof of route execution must be saved in ARTIFACTS task folders.

Notes:
- Keep redacted and safe content only.

### 06_TOOLS

Path:
E:\IMPERIUM\SSH_COMMAND_LIBRARY\06_TOOLS

Role:
Reusable SSH and SCP helper scripts, hash helpers, and redaction helpers.

What lives here:
- Route-specific docs and helper content

Allowed writes:
- Route docs, tools, diagnostics notes

Forbidden writes:
- Private keys
- Passwords
- Raw tokens

Inputs:
- Route requirements

Outputs:
- Route instructions and scripts

Related zones:
- SSH_COMMAND_LIBRARY
- ARTIFACTS
- PC_ENGINEERING_ROOM

Agent instruction:
Use this folder for route tooling; register proof of use in ARTIFACTS.

Status:
active

Canon status:
not_canon

Artifact policy:
Proof of route execution must be saved in ARTIFACTS task folders.

Notes:
- Keep redacted and safe content only.

### VM2_ROUTE_BASELINE_20260508_1651

Path:
E:\IMPERIUM\SSH_COMMAND_LIBRARY\VM2_ROUTE_BASELINE_20260508_1651

Role:
VM2 route baseline context; proof copies belong in ARTIFACTS.

What lives here:
- Route-specific docs and helper content

Allowed writes:
- Route docs, tools, diagnostics notes

Forbidden writes:
- Private keys
- Passwords
- Raw tokens

Inputs:
- Route requirements

Outputs:
- Route instructions and scripts

Related zones:
- SSH_COMMAND_LIBRARY
- ARTIFACTS
- PC_ENGINEERING_ROOM

Agent instruction:
Use this folder for route tooling; register proof of use in ARTIFACTS.

Status:
active

Canon status:
not_canon

Artifact policy:
Proof of route execution must be saved in ARTIFACTS task folders.

Notes:
- Keep redacted and safe content only.

## ARTIFACTS task folder standard

E:\IMPERIUM\ARTIFACTS\<TASK_ID>\
|-- 00_AGENT_MAP.md
|-- 01_INPUTS
|-- 02_OUTPUTS
|-- 03_RECEIPTS
|-- 04_MANIFESTS
|-- 05_HASHES
|-- 06_BUNDLES
|-- 07_REPORTS
|-- 08_OWNER_SUMMARY
|-- 09_SOURCE_POINTERS
`-- FINAL_STEP_BUNDLE

### 00_AGENT_MAP.md

Path:
E:\IMPERIUM\ARTIFACTS\<TASK_ID>\00_AGENT_MAP.md

Role:
Task-local map for agents.

What lives here:
- Task-scoped evidence content

Allowed writes:
- Task-scoped files only

Forbidden writes:
- Secrets
- Unrelated files
- Files without task relation

Inputs:
- Task inputs and references

Outputs:
- Task evidence outputs

Related zones:
- ARTIFACTS
- PC_ENGINEERING_ROOM
- SSH_COMMAND_LIBRARY

Agent instruction:
Keep this section task-scoped and do not mix unrelated artifacts.

Status:
active

Canon status:
not_canon

Artifact policy:
All files must remain inside the matching TASK_ID folder.

Notes:
- Standard structure for every task artifact folder.

### 01_INPUTS

Path:
E:\IMPERIUM\ARTIFACTS\<TASK_ID>\01_INPUTS

Role:
Inputs used by the task.

What lives here:
- Task-scoped evidence content

Allowed writes:
- Task-scoped files only

Forbidden writes:
- Secrets
- Unrelated files
- Files without task relation

Inputs:
- Task inputs and references

Outputs:
- Task evidence outputs

Related zones:
- ARTIFACTS
- PC_ENGINEERING_ROOM
- SSH_COMMAND_LIBRARY

Agent instruction:
Keep this section task-scoped and do not mix unrelated artifacts.

Status:
active

Canon status:
not_canon

Artifact policy:
All files must remain inside the matching TASK_ID folder.

Notes:
- Standard structure for every task artifact folder.

### 02_OUTPUTS

Path:
E:\IMPERIUM\ARTIFACTS\<TASK_ID>\02_OUTPUTS

Role:
Generated outputs from task execution.

What lives here:
- Task-scoped evidence content

Allowed writes:
- Task-scoped files only

Forbidden writes:
- Secrets
- Unrelated files
- Files without task relation

Inputs:
- Task inputs and references

Outputs:
- Task evidence outputs

Related zones:
- ARTIFACTS
- PC_ENGINEERING_ROOM
- SSH_COMMAND_LIBRARY

Agent instruction:
Keep this section task-scoped and do not mix unrelated artifacts.

Status:
active

Canon status:
not_canon

Artifact policy:
All files must remain inside the matching TASK_ID folder.

Notes:
- Standard structure for every task artifact folder.

### 03_RECEIPTS

Path:
E:\IMPERIUM\ARTIFACTS\<TASK_ID>\03_RECEIPTS

Role:
Proof records that task actions happened.

What lives here:
- Task-scoped evidence content

Allowed writes:
- Task-scoped files only

Forbidden writes:
- Secrets
- Unrelated files
- Files without task relation

Inputs:
- Task inputs and references

Outputs:
- Task evidence outputs

Related zones:
- ARTIFACTS
- PC_ENGINEERING_ROOM
- SSH_COMMAND_LIBRARY

Agent instruction:
Keep this section task-scoped and do not mix unrelated artifacts.

Status:
active

Canon status:
not_canon

Artifact policy:
All files must remain inside the matching TASK_ID folder.

Notes:
- Standard structure for every task artifact folder.

### 04_MANIFESTS

Path:
E:\IMPERIUM\ARTIFACTS\<TASK_ID>\04_MANIFESTS

Role:
File lists, folder lists, and bundle manifests.

What lives here:
- Task-scoped evidence content

Allowed writes:
- Task-scoped files only

Forbidden writes:
- Secrets
- Unrelated files
- Files without task relation

Inputs:
- Task inputs and references

Outputs:
- Task evidence outputs

Related zones:
- ARTIFACTS
- PC_ENGINEERING_ROOM
- SSH_COMMAND_LIBRARY

Agent instruction:
Keep this section task-scoped and do not mix unrelated artifacts.

Status:
active

Canon status:
not_canon

Artifact policy:
All files must remain inside the matching TASK_ID folder.

Notes:
- Standard structure for every task artifact folder.

### 05_HASHES

Path:
E:\IMPERIUM\ARTIFACTS\<TASK_ID>\05_HASHES

Role:
SHA256 and integrity files.

What lives here:
- Task-scoped evidence content

Allowed writes:
- Task-scoped files only

Forbidden writes:
- Secrets
- Unrelated files
- Files without task relation

Inputs:
- Task inputs and references

Outputs:
- Task evidence outputs

Related zones:
- ARTIFACTS
- PC_ENGINEERING_ROOM
- SSH_COMMAND_LIBRARY

Agent instruction:
Keep this section task-scoped and do not mix unrelated artifacts.

Status:
active

Canon status:
not_canon

Artifact policy:
All files must remain inside the matching TASK_ID folder.

Notes:
- Standard structure for every task artifact folder.

### 06_BUNDLES

Path:
E:\IMPERIUM\ARTIFACTS\<TASK_ID>\06_BUNDLES

Role:
Stage or intermediate bundles.

What lives here:
- Task-scoped evidence content

Allowed writes:
- Task-scoped files only

Forbidden writes:
- Secrets
- Unrelated files
- Files without task relation

Inputs:
- Task inputs and references

Outputs:
- Task evidence outputs

Related zones:
- ARTIFACTS
- PC_ENGINEERING_ROOM
- SSH_COMMAND_LIBRARY

Agent instruction:
Keep this section task-scoped and do not mix unrelated artifacts.

Status:
active

Canon status:
not_canon

Artifact policy:
All files must remain inside the matching TASK_ID folder.

Notes:
- Standard structure for every task artifact folder.

### 07_REPORTS

Path:
E:\IMPERIUM\ARTIFACTS\<TASK_ID>\07_REPORTS

Role:
Technical reports, blocker reports, and verdicts.

What lives here:
- Task-scoped evidence content

Allowed writes:
- Task-scoped files only

Forbidden writes:
- Secrets
- Unrelated files
- Files without task relation

Inputs:
- Task inputs and references

Outputs:
- Task evidence outputs

Related zones:
- ARTIFACTS
- PC_ENGINEERING_ROOM
- SSH_COMMAND_LIBRARY

Agent instruction:
Keep this section task-scoped and do not mix unrelated artifacts.

Status:
active

Canon status:
not_canon

Artifact policy:
All files must remain inside the matching TASK_ID folder.

Notes:
- Standard structure for every task artifact folder.

### 08_OWNER_SUMMARY

Path:
E:\IMPERIUM\ARTIFACTS\<TASK_ID>\08_OWNER_SUMMARY

Role:
Human-facing summary for Owner.

What lives here:
- Task-scoped evidence content

Allowed writes:
- Task-scoped files only

Forbidden writes:
- Secrets
- Unrelated files
- Files without task relation

Inputs:
- Task inputs and references

Outputs:
- Task evidence outputs

Related zones:
- ARTIFACTS
- PC_ENGINEERING_ROOM
- SSH_COMMAND_LIBRARY

Agent instruction:
Keep this section task-scoped and do not mix unrelated artifacts.

Status:
active

Canon status:
not_canon

Artifact policy:
All files must remain inside the matching TASK_ID folder.

Notes:
- Standard structure for every task artifact folder.

### 09_SOURCE_POINTERS

Path:
E:\IMPERIUM\ARTIFACTS\<TASK_ID>\09_SOURCE_POINTERS

Role:
Original path to new path source pointers.

What lives here:
- Task-scoped evidence content

Allowed writes:
- Task-scoped files only

Forbidden writes:
- Secrets
- Unrelated files
- Files without task relation

Inputs:
- Task inputs and references

Outputs:
- Task evidence outputs

Related zones:
- ARTIFACTS
- PC_ENGINEERING_ROOM
- SSH_COMMAND_LIBRARY

Agent instruction:
Keep this section task-scoped and do not mix unrelated artifacts.

Status:
active

Canon status:
not_canon

Artifact policy:
All files must remain inside the matching TASK_ID folder.

Notes:
- Standard structure for every task artifact folder.

### FINAL_STEP_BUNDLE

Path:
E:\IMPERIUM\ARTIFACTS\<TASK_ID>\FINAL_STEP_BUNDLE

Role:
Final zip and sha256 for the task.

What lives here:
- Task-scoped evidence content

Allowed writes:
- Task-scoped files only

Forbidden writes:
- Secrets
- Unrelated files
- Files without task relation

Inputs:
- Task inputs and references

Outputs:
- Task evidence outputs

Related zones:
- ARTIFACTS
- PC_ENGINEERING_ROOM
- SSH_COMMAND_LIBRARY

Agent instruction:
Keep this section task-scoped and do not mix unrelated artifacts.

Status:
active

Canon status:
not_canon

Artifact policy:
All files must remain inside the matching TASK_ID folder.

Notes:
- Standard structure for every task artifact folder.

