# Administratum MVP v0.1

task_id: TASK-20260514-BUILD-ADMINISTRATUM-MVP-V0_1
created_utc: 2026-05-14T21:15:35Z
planning_owner: Owner + Logos-Prime
planning_mode: manual_administratum_frame
astronomicon_used: false
astra_used: false
ready_for_agent: false
vm2_sync_required_now: false

## Purpose

Build the first basic Administratum MVP without Astronomicon/Astra usage for this task.

The MVP must prove:

1. Indexed address book with explicit boundaries for Git, LOCAL, PRIVATE, handoff, bundles, and VM2 deferred route.
2. Append-only chronicle/memory with contradiction checks.
3. Task lifecycle backend: start, stage report, stop, close, bundle build.
4. Synthetic success proof and synthetic fail-stop proof.

## Global Rules

- Canonical machine-readable repo artifacts are English-only by default.
- Russian is used only for live chat and controlled UI/i18n resources.
- No fake green.
- PASS requires evidence.
- Task IDs must be copied exactly.
- Artifact provenance git_head is separate from current Git HEAD.
- Do not use PowerShell ConvertTo-Json depth above 100.
- Use Python for deep JSON when required.
- Do not modify Astronomicon for this task.
- Do not set READY_FOR_AGENT true during this MVP.
- Do not sync VM2 unless Owner explicitly commands it.
- Do not move local/private/runtime payloads into Git.

## Six-Stage Execution Contract

1. STAGE-01-REGISTER-ADMINISTRATUM-MVP-FRAME
2. STAGE-02-BUILD-ADDRESS-BOOK-V0_1
3. STAGE-03-BUILD-CHRONICLE-MEMORY-V0_1
4. STAGE-04-BUILD-TASK-LIFECYCLE-BACKEND-V0_1
5. STAGE-05-SYNTHETIC-SUCCESS-PROOF
6. STAGE-06-SYNTHETIC-FAIL-STOP-PROOF

Stage 5 and Stage 6 include synthetic substages.

Stage 6 stop behavior is explicit:
- Stage 6.1 should PASS.
- Stage 6.2 is a deliberate fail-stop and expected autonomous stop point.
- Stage 6.3 is optional and requires explicit Owner approval.
