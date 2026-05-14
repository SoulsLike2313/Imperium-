# Servitor Prompt

task_id: TASK-20260514-BUILD-ADMINISTRATUM-MVP-V0_1
created_utc: 2026-05-14T21:15:35Z
prompt_set: ADMINISTRATUM_MVP_STAGE_PROMPTS_V0_1
canonical_language: English
owner_chat_language: Russian
astronomicon_used: false
astra_used: false
ready_for_agent_must_remain: false
vm2_sync_required_now: false

## Role

You are PC Servitor working inside IMPERIUM.

You are not Astronomicon.
You are not Astra.
You are building the first basic Administratum MVP from the Administratum-owned task frame.

## Hard Rules

1. Work from repo root: `E:\IMPERIUM`.
2. Do not modify Astronomicon for this task.
3. Do not set READY_FOR_AGENT to true.
4. Do not sync VM2 unless Owner explicitly commands it.
5. Do not move local/private/runtime payloads back inside the Git repo.
6. Canonical repo artifacts must be English-only.
7. Russian is allowed only in live chat and controlled UI/i18n resources.
8. No fake green.
9. PASS requires evidence.
10. Task IDs must be copied exactly.
11. Do not use PowerShell `ConvertTo-Json -Depth` above 100.
12. Use Python for deep JSON if needed.
13. Keep artifact provenance `git_head` separate from current Git HEAD.
14. If you hit a true blocker or Owner approval is required, stop and report.

## Required Owner-Facing Final Response Form

When you report to Owner, use this exact shape in Russian:

1. step name;
2. full path to bundle/report/artifact;
3. verdict;
4. 3-4 concise Russian comments for Owner.

## Required Self-Check Before Final Response

Run or create the stage checker required by this prompt.
Show evidence paths.
Do not claim PASS without machine-readable evidence.

# Stage 04 Prompt - Build Task Lifecycle Backend v0.1

stage_id: STAGE-04-BUILD-TASK-LIFECYCLE-BACKEND-V0_1

## Goal

Create the minimal backend scripts and schemas for Administratum task lifecycle:

- start task session;
- record stage report;
- stop task with reason;
- close successful task only when gates pass;
- build task bundle from Administratum records;
- run all checks.

## Read First

Read:

- `ORGANS/ADMINISTRATUM/REGISTRY/ADMINISTRATUM_MVP_TASK_PLAN_V0_1.json`
- `ORGANS/ADMINISTRATUM/ADDRESS_BOOK/imperium_address_book_v0_1.json`
- `ORGANS/ADMINISTRATUM/CHRONICLE/imperium_chronicle_v0_1.jsonl`
- `ORGANS/ADMINISTRATUM/REGISTRY/TASKS/TASK-20260514-BUILD-ADMINISTRATUM-MVP-V0_1/PROMPTS/04_STAGE-04_BUILD_TASK_LIFECYCLE_BACKEND_V0_1.md`

## Create / Update

Create:

```text
schemas/administratum_task_session.schema.json
schemas/administratum_stage_report.schema.json
schemas/administratum_task_bundle_manifest.schema.json
scripts/administratum_task_start_v0_1.py
scripts/administratum_stage_report_v0_1.py
scripts/administratum_task_stop_v0_1.py
scripts/administratum_task_close_v0_1.py
scripts/administratum_build_task_bundle_v0_1.py
scripts/administratum_check_all_v0_1.py
ORGANS/ADMINISTRATUM/TASK_LIFECYCLE/SESSIONS/.gitkeep
ORGANS/ADMINISTRATUM/REPORTS/task_lifecycle_backend_check_report_v0_1.json
```

## Required Lifecycle States

```text
PLANNED
ACTIVE
STAGE_PASS
BLOCKED
STOPPED
STOPPED_PENDING_OWNER_APPROVAL
CLOSED_PASS
CLOSED_FAIL
BUNDLED
```

## Script Contract

### administratum_task_start_v0_1.py

Must create:

```text
ORGANS/ADMINISTRATUM/TASK_LIFECYCLE/SESSIONS/<TASK_ID>/task_session.json
ORGANS/ADMINISTRATUM/TASK_LIFECYCLE/SESSIONS/<TASK_ID>/events.jsonl
ORGANS/ADMINISTRATUM/TASK_LIFECYCLE/SESSIONS/<TASK_ID>/stage_reports/
```

### administratum_stage_report_v0_1.py

Must accept or create stage reports with:

```text
task_id
stage_id
status
evidence_paths
checker_status
timestamp_utc
```

### administratum_task_stop_v0_1.py

Must record:

```text
status = STOPPED or STOPPED_PENDING_OWNER_APPROVAL
stop_reason
failed_stage_id
owner_approval_required
```

### administratum_task_close_v0_1.py

Must refuse CLOSED_PASS if:

- required stage reports are missing;
- any required stage failed;
- task is stopped pending approval;
- required evidence paths are missing.

### administratum_build_task_bundle_v0_1.py

Must build a task bundle from Administratum session records.
It must not require Servitor to manually assemble the bundle.

### administratum_check_all_v0_1.py

Must run:

- address book checker;
- chronicle checker;
- lifecycle fixture checks;
- bundle builder dry-run or fixture-run.

## Stage Green Criteria

PASS only if:

- task_start creates a valid task_session.json;
- stage_report appends valid stage evidence;
- task_close refuses to close missing/failed stages as PASS;
- task_stop records reason and prevents fake success closure;
- build_task_bundle collects evidence from session records;
- check_all returns PASS;
- scripts support machine-readable JSON output;
- scripts do not require PowerShell ConvertTo-Json depth greater than 100.

## Stop Criteria

Stop if:

- scripts cannot validate their own fixture data;
- task_close can close a failed or incomplete task as PASS;
- task_stop loses failure reason;
- bundle builder depends on untracked private payload;
- checker cannot produce deterministic PASS/FAIL.

## Required Evidence

Create:

```text
ORGANS/ADMINISTRATUM/REPORTS/stage_04_task_lifecycle_backend_report_v0_1.json
```

The report must include:

- task_id;
- stage_id;
- created scripts;
- created schemas;
- checker command;
- checker status;
- fixture evidence;
- pass/fail reason.

## Final Action

If Stage 04 is PASS and you are confident, proceed to Stage 05 prompt automatically.

If not PASS, stop and report.
