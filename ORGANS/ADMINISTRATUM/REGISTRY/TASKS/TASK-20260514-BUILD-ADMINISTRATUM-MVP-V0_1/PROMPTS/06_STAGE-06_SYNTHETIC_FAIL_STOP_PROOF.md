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

# Stage 06 Prompt - Synthetic Fail-Stop Proof

stage_id: STAGE-06-SYNTHETIC-FAIL-STOP-PROOF
synthetic_task_id: TASK-20260514-ADMINISTRATUM-PROOF-FAILSTOP-V0_1

## Goal

Prove Administratum can detect a deliberate stage failure, stop work, record the reason, and prevent fake green.

The ideal correct behavior is:

1. STAGE-06-01 passes.
2. STAGE-06-02 deliberately fails.
3. Administratum records STOPPED or STOPPED_PENDING_OWNER_APPROVAL.
4. Servitor stops at STAGE-06-02.
5. Servitor does not continue to STAGE-06-03 without explicit Owner approval.

## Read First

Read:

- `ORGANS/ADMINISTRATUM/REGISTRY/ADMINISTRATUM_MVP_TASK_PLAN_V0_1.json`
- `scripts/administratum_task_start_v0_1.py`
- `scripts/administratum_stage_report_v0_1.py`
- `scripts/administratum_task_stop_v0_1.py`
- `scripts/administratum_task_close_v0_1.py`
- `scripts/administratum_build_task_bundle_v0_1.py`
- `scripts/administratum_check_all_v0_1.py`
- `ORGANS/ADMINISTRATUM/REGISTRY/TASKS/TASK-20260514-BUILD-ADMINISTRATUM-MVP-V0_1/PROMPTS/06_STAGE-06_SYNTHETIC_FAIL_STOP_PROOF.md`

## Synthetic Substages

### STAGE-06-01-OPEN-FAILSTOP-SESSION-AND-PASS-STAGE-1

Create an ACTIVE task session for:

```text
TASK-20260514-ADMINISTRATUM-PROOF-FAILSTOP-V0_1
```

Create and record a valid first synthetic stage report with evidence.

Suggested artifact:

```text
ORGANS/ADMINISTRATUM/TASK_LIFECYCLE/SESSIONS/TASK-20260514-ADMINISTRATUM-PROOF-FAILSTOP-V0_1/evidence/stage_1_pass_evidence.json
```

Expected: PASS.

### STAGE-06-02-DELIBERATE-STAGE-2-FAILURE-AND-STOP

Deliberately attempt a second synthetic stage with a missing required artifact or invalid manifest.

Required expected behavior:

- checker rejects the second stage;
- task is not CLOSED_PASS;
- task_stop records the failure reason;
- final status becomes STOPPED or STOPPED_PENDING_OWNER_APPROVAL;
- owner_approval_required is true;
- Servitor stops here.

This is the expected autonomous stop point.

Do not repair the deliberate failure.
Do not bypass it.
Do not continue automatically.

Expected: STOPPED or STOPPED_PENDING_OWNER_APPROVAL.

### STAGE-06-03-OWNER-APPROVED-FAILED-EVIDENCE-BUNDLE

This substage is optional and forbidden without explicit Owner approval.

Only after Owner approval:

- build a stopped/failed evidence bundle from Administratum records;
- mark it as failed/stopped evidence bundle, not success bundle.

## Stage Green Criteria

PASS for this proof means expected fail-stop, not normal task success.

The proof is PASS only if:

- Stage 6.1 PASS;
- Stage 6.2 fails for the deliberate expected reason;
- Administratum records the stop reason;
- task is not closed as CLOSED_PASS;
- Servitor stops at Stage 6.2 and does not continue automatically;
- any continuation after Stage 6.2 requires explicit Owner approval;
- `scripts/administratum_check_all_v0_1.py` treats this as expected fail-stop proof, not system failure.

## Stop Criteria

Stage 6.2 is itself the expected autonomous stop point.

Stop if:

- the system tries to mark the deliberate fail task as success;
- failure reason is missing;
- Servitor tries to bypass Owner approval;
- failed task bundle is built before stop evidence exists;
- Servitor attempts STAGE-06-03 without Owner approval.

## Required Evidence Before Stopping

Create:

```text
ORGANS/ADMINISTRATUM/REPORTS/stage_06_synthetic_fail_stop_proof_report_v0_1.json
```

The report must include:

- task_id;
- stage_id;
- synthetic_task_id;
- STAGE-06-01 status;
- STAGE-06-02 deliberate failure reason;
- stop record path;
- owner_approval_required;
- final status: STOPPED or STOPPED_PENDING_OWNER_APPROVAL;
- confirmation that CLOSED_PASS was not produced;
- checker command;
- checker status;
- pass/fail-stop reason.

## Final Action

Stop at STAGE-06-02 after the expected fail-stop proof.

Report to Owner and wait for approval before any Stage 06.3 action.
