# Act 4 — Inquisition GENERAL_TASK Decomposition Summary

## Task Identity

- **TASK_ID**: TASK-20260513-INQUISITION-GENERAL-TASK-DECOMPOSITION-V0_1
- **STAGE_ID**: STAGE-001-CONVERT-GENERAL-TASK-DRAFT-AND-DECOMPOSE-INTO-TASK-CANDIDATES-V0_1
- **Base Git Truth**: 8a7d279047669fc37a9cda49b460362c5bede952 (commit 61)

## What Was Decomposed

The human-readable GENERAL_TASK draft:
`ORGANS/ASTRONOMICON/REGISTRY/GENERAL_TASKS/GENERAL-TASK-20260513-BUILD-INQUISITION-V0_1-SELF-DESCRIPTIVE-ORGAN-DRAFT.md`

was converted into a machine-readable GENERAL_TASK record:
`ORGANS/ASTRONOMICON/REGISTRY/GENERAL_TASKS/GENERAL-TASK-20260513-BUILD-INQUISITION-V0_1-SELF-DESCRIPTIVE-ORGAN.json`

Status: `REGISTERED_FOR_DECOMPOSITION`

## TASK Candidates Created

10 task candidates were created under `ORGANS/ASTRONOMICON/REGISTRY/TASK_CANDIDATES/`:

| # | Task ID | Purpose | Depends On |
|---|---------|---------|------------|
| 001 | TASK-CANDIDATE-20260513-INQUISITION-001-BLUEPRINT-V0_1 | Register Inquisition v0.1 blueprint | (none) |
| 002 | TASK-CANDIDATE-20260513-INQUISITION-002-REVIEW-PACK-V0_1 | Export review pack for Speculum/Kiro | 001 |
| 003 | TASK-CANDIDATE-20260513-INQUISITION-003-ADVISORY-INGEST-V0_1 | Register advisory responses | 002 |
| 004 | TASK-CANDIDATE-20260513-INQUISITION-004-TASK-MODERNIZATION-V0_1 | Modernize task after advisory responses | 003 |
| 005 | TASK-CANDIDATE-20260513-INQUISITION-005-STAGE-MAP-APPROVAL-V0_1 | Approve stage map and gate criteria | 004 |
| 006 | TASK-CANDIDATE-20260513-INQUISITION-006-CONTRACT-REGISTRY-SCHEMAS-V0_1 | Build Inquisition contract/registry/schemas | 005 |
| 007 | TASK-CANDIDATE-20260513-INQUISITION-007-SELF-REPORT-PORT-V0_1 | Build Inquisition self-report port | 006 |
| 008 | TASK-CANDIDATE-20260513-INQUISITION-008-FIRST-AUDIT-CHECKER-V0_1 | Build first Inquisition audit checker | 007 |
| 009 | TASK-CANDIDATE-20260513-INQUISITION-009-VM2-BUNDLE-PC-INTAKE-SYNC-V0_1 | Execute through VM2 bundle / PC intake / VM2 sync | 008 |
| 010 | TASK-CANDIDATE-20260513-INQUISITION-010-OBSERVE-AGENT-BLOCKERS-V0_1 | Observe agent behavior and feed blockers back | 009 |

All candidates have status `REGISTERED_CANDIDATE_NEEDS_REVIEW` and `ready_for_agent: false`.

## Why First Task Was Split Into Stages

Task Candidate 001 (Blueprint) was split into 10 stages because:

1. **It tests Act 4** — proves that stage mapping works for real tasks.
2. **It proves stages can be mapped** — creates evidence for agent navigation.
3. **It creates evidence for agent navigation** — each stage has clear inputs/outputs/checks.
4. **It shows where blockers appear** — Owner decision gates are explicit.
5. **It is the corridor test** — if this works, subsequent tasks can use simpler decomposition.

Stage map: `ORGANS/ASTRONOMICON/REGISTRY/STAGE_MAPS/STAGE-MAP-DRAFT-20260513-INQUISITION-001-BLUEPRINT-V0_1.json`
Status: `DRAFT_NEEDS_REVIEW`

## What Remains Blocked

- **READY_FOR_AGENT**: `false` (v0_2 gate created)
- **Advisory responses**: not yet received for blueprint task
- **Task modernization**: cannot proceed without advisory responses
- **Stage map approval**: Owner has not approved
- **Implementation**: not started (Act 5 not entered)

## What Next Review Should Ask Kiro/Speculum

A review pack has been created:
`ORGANS/ASTRONOMICON/REGISTRY/REVIEW_PACKS/REVIEW-PACK-20260513-INQUISITION-001-BLUEPRINT-SPECULUM-KIRO-V0_1.json`

Key questions:
1. What is the smallest useful Inquisition v0.1 organ contract?
2. Which audit categories are mandatory for v0.1?
3. What should Inquisition v0.1 explicitly NOT audit yet?
4. Which files are mandatory for a real organ?
5. How should Inquisition report UNKNOWN without false PASS?

## How This Prepares Sanctum Registration Corridor Workbench

This decomposition creates the data structures that Sanctum's future Registration Corridor Workbench will display:

- GENERAL_TASK records → Sanctum can list and open them
- TASK candidates → Sanctum can show decomposition tree
- Stage maps → Sanctum can show stage progress
- Review packs → Sanctum can export to reviewers
- READY_FOR_AGENT gates → Sanctum can show blocked/ready status

The machine-readable format enables Sanctum to render corridor state without parsing markdown.

## Why READY_FOR_AGENT Remains False

The READY_FOR_AGENT gate (v0_2) explicitly states `false` because:

1. GENERAL_TASK is decomposed but review responses are not ingested
2. Task modernization is missing
3. First stage map draft is not approved
4. Owner decision is pending
5. Act 5 implementation has not started
6. No advisory responses received for blueprint task
7. No complete READY_FOR_AGENT evidence chain

This is honest and by design. Decomposition alone does not prove readiness.

## Files Created

1. `ORGANS/ASTRONOMICON/REGISTRY/GENERAL_TASKS/GENERAL-TASK-20260513-BUILD-INQUISITION-V0_1-SELF-DESCRIPTIVE-ORGAN.json`
2. `ORGANS/ASTRONOMICON/REGISTRY/TASK_CANDIDATES/TASK-CANDIDATE-20260513-INQUISITION-001-BLUEPRINT-V0_1.json`
3. `ORGANS/ASTRONOMICON/REGISTRY/TASK_CANDIDATES/TASK-CANDIDATE-20260513-INQUISITION-002-REVIEW-PACK-V0_1.json`
4. `ORGANS/ASTRONOMICON/REGISTRY/TASK_CANDIDATES/TASK-CANDIDATE-20260513-INQUISITION-003-ADVISORY-INGEST-V0_1.json`
5. `ORGANS/ASTRONOMICON/REGISTRY/TASK_CANDIDATES/TASK-CANDIDATE-20260513-INQUISITION-004-TASK-MODERNIZATION-V0_1.json`
6. `ORGANS/ASTRONOMICON/REGISTRY/TASK_CANDIDATES/TASK-CANDIDATE-20260513-INQUISITION-005-STAGE-MAP-APPROVAL-V0_1.json`
7. `ORGANS/ASTRONOMICON/REGISTRY/TASK_CANDIDATES/TASK-CANDIDATE-20260513-INQUISITION-006-CONTRACT-REGISTRY-SCHEMAS-V0_1.json`
8. `ORGANS/ASTRONOMICON/REGISTRY/TASK_CANDIDATES/TASK-CANDIDATE-20260513-INQUISITION-007-SELF-REPORT-PORT-V0_1.json`
9. `ORGANS/ASTRONOMICON/REGISTRY/TASK_CANDIDATES/TASK-CANDIDATE-20260513-INQUISITION-008-FIRST-AUDIT-CHECKER-V0_1.json`
10. `ORGANS/ASTRONOMICON/REGISTRY/TASK_CANDIDATES/TASK-CANDIDATE-20260513-INQUISITION-009-VM2-BUNDLE-PC-INTAKE-SYNC-V0_1.json`
11. `ORGANS/ASTRONOMICON/REGISTRY/TASK_CANDIDATES/TASK-CANDIDATE-20260513-INQUISITION-010-OBSERVE-AGENT-BLOCKERS-V0_1.json`
12. `ORGANS/ASTRONOMICON/REGISTRY/STAGE_MAPS/STAGE-MAP-DRAFT-20260513-INQUISITION-001-BLUEPRINT-V0_1.json`
13. `ORGANS/ASTRONOMICON/REGISTRY/REVIEW_PACKS/REVIEW-PACK-20260513-INQUISITION-001-BLUEPRINT-SPECULUM-KIRO-V0_1.json`
14. `ORGANS/ASTRONOMICON/REGISTRY/REVIEW_PACKS/REVIEW-PACK-20260513-INQUISITION-001-BLUEPRINT-SPECULUM-KIRO-V0_1.md`
15. `ORGANS/ASTRONOMICON/REGISTRY/READY_FOR_AGENT/READY-FOR-AGENT-20260513-INQUISITION-V0_1-SELF-BUILD-BLOCKED-V0_2.json`
16. `DOCS/ACT4_INQUISITION_GENERAL_TASK_DECOMPOSITION_20260513.md`

## Verdict

`PASS_READY_FOR_OWNER_REVIEW`

Decomposition is complete. No implementation was performed. READY_FOR_AGENT remains false.
