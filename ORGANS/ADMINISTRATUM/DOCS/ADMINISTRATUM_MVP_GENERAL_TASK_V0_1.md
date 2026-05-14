# Administratum MVP General Task Frame v0.1

task_id: TASK-20260514-BUILD-ADMINISTRATUM-MVP-V0_1
created_utc: 20260514T211100Z
planning_owner: Owner + Logos-Prime
planning_mode: manual_administratum_frame
astronomicon_used: false
astra_used: false
ready_for_agent: false
vm2_sync_required_now: false

## 0. Purpose

Build the first basic Administratum MVP without using Astronomicon/Astra for this task.

Administratum MVP must prove three core functions:

1. Address Book:
   - Administratum stores a clear indexed address book for IMPERIUM.
   - It distinguishes Git repo, local context, private context, handoff area, task bundle area, GitHub exact tree, and VM2 deferred/offline route.
   - Agents work inside the Git repo by default.
   - Local/private context is used only when a task explicitly references it.
   - Private payload must not be pulled into Git; only redacted/index-level descriptions are allowed.

2. Chronicle / Memory:
   - Administratum stores IMPERIUM memory/history as a machine-checkable chronicle.
   - It records commits, task events, closures, stopped work, lessons learned, policies, handoff points, and provenance.
   - It must prevent or flag contradictory history entries.

3. Task Lifecycle + Bundle Collection:
   - Administratum can record task start.
   - Administratum can accept stage progress reports.
   - Administratum can stop work with a reason.
   - Administratum can close completed work.
   - Administratum can collect a task bundle independently, without requiring Servitor to assemble the bundle.

## 1. Operating Rules

- Canonical repo artifacts must be English-only by default.
- Russian is allowed in live chat and controlled UI/i18n presentation resources only.
- No fake green.
- PASS requires evidence.
- Artifact provenance git_head is not the same thing as current Git HEAD.
- Task IDs must be copied exactly.
- PowerShell ConvertTo-Json depth must not exceed 100.
- Use Python for deep JSON if needed.
- Do not modify Astronomicon for this task.
- Do not mark READY_FOR_AGENT true during this MVP.
- Do not sync VM2 unless Owner explicitly commands it.
- Do not place local/private/runtime outputs back inside the Git repo.

## 2. Target Repo Layout

Recommended canonical paths:

```text
ORGANS/ADMINISTRATUM/
  ADDRESS_BOOK/
  CHRONICLE/
  TASK_LIFECYCLE/
  BUNDLE_BUILDER/
  REGISTRY/
  REPORTS/
  DOCS/

schemas/
  administratum_address_book.schema.json
  administratum_chronicle_entry.schema.json
  administratum_task_session.schema.json
  administratum_task_bundle_manifest.schema.json

scripts/
  administratum_address_book_check_v0_1.py
  administratum_chronicle_check_v0_1.py
  administratum_task_start_v0_1.py
  administratum_stage_report_v0_1.py
  administratum_task_stop_v0_1.py
  administratum_task_close_v0_1.py
  administratum_build_task_bundle_v0_1.py
  administratum_check_all_v0_1.py
```

External context must remain outside the Git repo:

```text
E:\IMPERIUM_CONTEXT\LOCAL
E:\IMPERIUM_CONTEXT\PRIVATE
```

## 3. Six-Stage Plan

This plan is intentionally written as one large Administratum-owned task with six sequential stages.

Servitor should later read Stage 1, execute it, self-check green, and proceed to the next stage only if the stage gate is PASS. Autonomous stop is allowed only on a true blocker, missing required Owner approval, or the deliberate fail-stop condition in Stage 6.2.

### Stage 1 - Register Administratum MVP Frame

stage_id: STAGE-01-REGISTER-ADMINISTRATUM-MVP-FRAME

Goal:
Create the minimal Administratum task frame and organ documentation inside Administratum, without invoking Astronomicon.

Expected outputs:
- ORGANS/ADMINISTRATUM/DOCS/ADMINISTRATUM_MVP_V0_1.md
- ORGANS/ADMINISTRATUM/REGISTRY/ADMINISTRATUM_MVP_TASK_PLAN_V0_1.json
- Minimal folder skeleton under ORGANS/ADMINISTRATUM/
- Explicit flags:
  - astronomicon_used=false
  - astra_used=false
  - ready_for_agent=false

Green criteria:
- All required paths exist.
- Files are UTF-8 and English-only.
- No Astronomicon files are changed.
- The task ID is exact: TASK-20260514-BUILD-ADMINISTRATUM-MVP-V0_1
- Stage plan contains exactly 6 top-level stages.
- Stage 5 and Stage 6 contain synthetic substages.
- The plan explicitly includes stop behavior.

Stop criteria:
- Stop if required Administratum directories cannot be created.
- Stop if the repo root is not E:\IMPERIUM.
- Stop if files would need to be written outside approved locations.
- Stop if a path conflict would overwrite existing canonical artifacts.

### Stage 2 - Build Address Book v0.1

stage_id: STAGE-02-BUILD-ADDRESS-BOOK-V0_1

Goal:
Create and verify the Administratum address book.

Expected outputs:
- ORGANS/ADMINISTRATUM/ADDRESS_BOOK/imperium_address_book_v0_1.json
- schemas/administratum_address_book.schema.json
- scripts/administratum_address_book_check_v0_1.py
- ORGANS/ADMINISTRATUM/REPORTS/address_book_check_report_v0_1.json

Required address entries:
- pc_git_repo: E:\IMPERIUM
- local_context_root: E:\IMPERIUM_CONTEXT\LOCAL
- private_context_root: E:\IMPERIUM_CONTEXT\PRIVATE
- handoff_root: E:\IMPERIUM_CONTEXT\LOCAL\HANDOFF
- task_bundles_root: E:\IMPERIUM_CONTEXT\LOCAL\TASK_BUNDLES
- github_exact_tree_url: exact HEAD tree URL, not floating master
- vm2_repo_root: /home/vboxuser2/IMPERIUM_WORK/Imperium-
- vm2_status: DEFERRED_OFFLINE unless Owner commands sync

Green criteria:
- Address book validates against schema.
- Each required entry has:
  - zone_id
  - path_or_url
  - scope
  - privacy_class
  - agent_access_rule
  - git_tracked_expected
  - description
  - verification_method
- Private context entry is redacted/index-only.
- No private payload is copied into Git.
- Local/private use rule is explicit:
  - use only when a task explicitly references it;
  - otherwise operate only inside the Git repo.
- Exact Git tree URL is present.
- Checker returns PASS.

Stop criteria:
- Stop if local/private paths are inside E:\IMPERIUM.
- Stop if private payload would be committed.
- Stop if the address book uses floating master as the only Git truth.
- Stop if required entries are missing.

### Stage 3 - Build Chronicle / Memory v0.1

stage_id: STAGE-03-BUILD-CHRONICLE-MEMORY-V0_1

Goal:
Create the first append-only Administratum chronicle for IMPERIUM history and lessons.

Expected outputs:
- ORGANS/ADMINISTRATUM/CHRONICLE/imperium_chronicle_v0_1.jsonl
- schemas/administratum_chronicle_entry.schema.json
- scripts/administratum_chronicle_check_v0_1.py
- ORGANS/ADMINISTRATUM/REPORTS/chronicle_check_report_v0_1.json

Required initial memory entries:
- Astronomicon backend corridor proved.
- Servitor execution intake proved.
- Language policy accepted.
- Handoff created.
- READY_FOR_AGENT remains false.
- VM2 remains DEFERRED_OFFLINE.
- Lesson: PowerShell ConvertTo-Json -Depth max is 100.
- Lesson: Task IDs must be copied exactly.
- Lesson: artifact provenance git_head is not current Git HEAD.
- Lesson: canonical machine/repo artifacts should be English-only by default.

Green criteria:
- JSONL is valid: every line parses.
- Each event has:
  - event_id
  - event_type
  - task_id or global_scope
  - timestamp_utc
  - summary
  - evidence
  - provenance
- Event IDs are unique.
- No contradictory status entries.
- Closed tasks are not reopened without an explicit event.
- Artifact provenance and current Git truth are separate fields.
- Checker returns PASS.

Stop criteria:
- Stop if chronicle has invalid JSONL.
- Stop if any event claims unsupported PASS.
- Stop if old artifact provenance is used as current HEAD.
- Stop if task ID mismatch appears.

### Stage 4 - Build Task Lifecycle Backend v0.1

stage_id: STAGE-04-BUILD-TASK-LIFECYCLE-BACKEND-V0_1

Goal:
Create the minimal backend scripts and schemas for Administratum task lifecycle.

Expected outputs:
- schemas/administratum_task_session.schema.json
- schemas/administratum_stage_report.schema.json
- schemas/administratum_task_bundle_manifest.schema.json
- scripts/administratum_task_start_v0_1.py
- scripts/administratum_stage_report_v0_1.py
- scripts/administratum_task_stop_v0_1.py
- scripts/administratum_task_close_v0_1.py
- scripts/administratum_build_task_bundle_v0_1.py
- scripts/administratum_check_all_v0_1.py
- ORGANS/ADMINISTRATUM/TASK_LIFECYCLE/SESSIONS/.gitkeep or equivalent safe placeholder

Required lifecycle states:
- PLANNED
- ACTIVE
- STAGE_PASS
- BLOCKED
- STOPPED
- STOPPED_PENDING_OWNER_APPROVAL
- CLOSED_PASS
- CLOSED_FAIL
- BUNDLED

Green criteria:
- task_start creates a valid task_session.json.
- stage_report appends valid stage evidence.
- task_close refuses to close if required stages are missing or failed.
- task_stop records a reason and prevents fake success closure.
- build_task_bundle collects evidence from session records without Servitor manually assembling the bundle.
- check_all runs address book, chronicle, lifecycle fixture checks, and returns PASS.
- Scripts support machine-readable JSON output.
- Scripts do not require PowerShell ConvertTo-Json depth > 100.

Stop criteria:
- Stop if scripts cannot validate their own fixture data.
- Stop if task_close can close a failed or incomplete task as PASS.
- Stop if task_stop loses the failure reason.
- Stop if bundle builder depends on untracked private payload.

### Stage 5 - Synthetic Success Proof

stage_id: STAGE-05-SYNTHETIC-SUCCESS-PROOF

Goal:
Prove Administratum can run a small successful two-stage task and collect the task bundle independently.

Synthetic task:
TASK-20260514-ADMINISTRATUM-PROOF-SUCCESS-V0_1

Substages:
- STAGE-05-01-OPEN-SUCCESS-SESSION
  - Create an ACTIVE task session for the synthetic success task.
- STAGE-05-02-RECORD-SUCCESS-STAGE-1
  - Record a valid stage report with a small tracked evidence artifact.
- STAGE-05-03-RECORD-SUCCESS-STAGE-2
  - Record a second valid stage report with a small tracked evidence artifact.
- STAGE-05-04-CLOSE-SUCCESS-TASK
  - Close the synthetic task as CLOSED_PASS.
- STAGE-05-05-BUILD-SUCCESS-BUNDLE
  - Build a task bundle from Administratum session records.

Expected outputs:
- ORGANS/ADMINISTRATUM/TASK_LIFECYCLE/SESSIONS/TASK-20260514-ADMINISTRATUM-PROOF-SUCCESS-V0_1/task_session.json
- stage reports under that session
- final_verdict.json with CLOSED_PASS
- task bundle manifest
- external bundle under E:\IMPERIUM_CONTEXT\LOCAL\TASK_BUNDLES\TASK-20260514-ADMINISTRATUM-PROOF-SUCCESS-V0_1\

Green criteria:
- Synthetic task starts as ACTIVE.
- Both synthetic stage reports validate.
- CLOSED_PASS is allowed only after both substages pass.
- Bundle manifest lists all evidence artifacts.
- Bundle is collected by Administratum bundle builder, not manually by Servitor.
- check_all returns PASS after success proof.

Stop criteria:
- Stop if either synthetic stage report is invalid.
- Stop if task closes without both substages.
- Stop if bundle omits required evidence.
- Stop if success proof produces fake green.

### Stage 6 - Synthetic Fail-Stop Proof

stage_id: STAGE-06-SYNTHETIC-FAIL-STOP-PROOF

Goal:
Prove Administratum can detect a deliberate stage failure, stop work, record the reason, and prevent fake green.

Synthetic task:
TASK-20260514-ADMINISTRATUM-PROOF-FAILSTOP-V0_1

Substages:
- STAGE-06-01-OPEN-FAILSTOP-SESSION-AND-PASS-STAGE-1
  - Create an ACTIVE task session.
  - Record a valid first synthetic stage report.
  - This substage should PASS.
- STAGE-06-02-DELIBERATE-STAGE-2-FAILURE-AND-STOP
  - Attempt a second synthetic stage with a deliberately missing required artifact or invalid manifest.
  - Expected result is STOPPED_PENDING_OWNER_APPROVAL or STOPPED with a clear reason.
  - This is the ideal autonomous stop point.
  - Servitor must not repair, bypass, or continue past this point without Owner approval.
- STAGE-06-03-OWNER-APPROVED-FAILED-EVIDENCE-BUNDLE
  - Optional post-stop action only after Owner approval.
  - Build a failed/stopped evidence bundle from Administratum records.

Expected outputs:
- ORGANS/ADMINISTRATUM/TASK_LIFECYCLE/SESSIONS/TASK-20260514-ADMINISTRATUM-PROOF-FAILSTOP-V0_1/task_session.json
- valid stage 1 report
- failed or rejected stage 2 report
- stop_record.json with reason
- final_verdict.json with STOPPED or STOPPED_PENDING_OWNER_APPROVAL
- optional failed evidence bundle after Owner approval

Green criteria:
- Stage 6.1 PASS.
- Stage 6.2 fails for the deliberate expected reason.
- Administratum records the stop reason.
- The task is not closed as CLOSED_PASS.
- Servitor stops at Stage 6.2 and does not continue automatically.
- Any continuation after Stage 6.2 requires explicit Owner approval.
- check_all treats this as expected fail-stop proof, not as a system failure.

Stop criteria:
- Stage 6.2 is itself the expected autonomous stop point.
- Stop if the system tries to mark the deliberate fail task as success.
- Stop if failure reason is missing.
- Stop if Servitor tries to bypass Owner approval.
- Stop if failed task bundle is built before stop evidence exists.

## 4. Final Acceptance for the Whole MVP

The whole Administratum MVP task can be considered accepted only when:

- Stage 1 PASS.
- Stage 2 PASS.
- Stage 3 PASS.
- Stage 4 PASS.
- Stage 5 PASS.
- Stage 6 reaches expected stop at Stage 6.2 and records it correctly.
- Optional Stage 6.3 may run only after Owner approval.
- READY_FOR_AGENT remains false unless a later separate task changes it.
- VM2 remains deferred/offline unless Owner explicitly commands sync.
- Final Administratum report states:
  - address book proved;
  - chronicle/memory proved;
  - task lifecycle proved;
  - success bundle collection proved;
  - fail-stop protection proved.
