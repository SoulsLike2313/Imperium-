# Review Pack: Inquisition v0.1 Blueprint Task

## Identity

- **review_pack_id**: REVIEW-PACK-20260513-INQUISITION-001-BLUEPRINT-SPECULUM-KIRO-V0_1
- **target_task**: TASK-CANDIDATE-20260513-INQUISITION-001-BLUEPRINT-V0_1
- **source_general_task**: GENERAL-TASK-20260513-BUILD-INQUISITION-V0_1-SELF-DESCRIPTIVE-ORGAN
- **status**: READY_FOR_EXTERNAL_REVIEW_NOT_INGESTED
- **reviewer_target**: Logos-Speculum / Kiro Technical Reviewer

## Current Git Truth

- **repo**: https://github.com/SoulsLike2313/Imperium-
- **HEAD**: 8a7d279047669fc37a9cda49b460362c5bede952
- **commit_count**: 61
- **exact_tree_url**: https://github.com/SoulsLike2313/Imperium-/tree/8a7d279047669fc37a9cda49b460362c5bede952

## Context

This review pack asks for structured advisory on the **first task candidate** in the Inquisition v0.1 self-build GENERAL_TASK decomposition.

The task is: **Register Inquisition v0.1 Blueprint** — define what Inquisition v0.1 is, its responsibilities, forbidden actions, zones, audit categories, capabilities, and evidence model.

### Act 3 Dependencies
- ZONE_REGISTRY_V0_1
- TRUTH_SOURCE_REGISTRY_V0_1
- CAPABILITY_SPINE_V0_1
- WARNING_STALE_BASELINE_V0_1

### Act 4 Dependencies
- ACT4_REGISTRATION_CORRIDOR_V0_1
- GENERAL-TASK-20260513-BUILD-INQUISITION-V0_1-SELF-DESCRIPTIVE-ORGAN (machine-readable)

### Raw Advisory Reference
- ORGANS/ASTRONOMICON/REGISTRY/ADVISORY_INPUTS/ADVISORY-20260513-KIRO-INQUISITION-SELF-BUILD-V0_1.json
- Status: RAW_ADVISORY_INPUT_NOT_YET_RECONCILED

## Questions for Reviewer

1. What is the smallest useful Inquisition v0.1 organ contract that guarantees no-fake-green audit capability?
2. Which audit categories must Inquisition v0.1 detect before READY_FOR_AGENT can be set true for any task?
3. What should Inquisition v0.1 explicitly NOT audit yet to avoid scope creep?
4. Which files are mandatory for a real organ (minimum viable organ structure)?
5. Which schemas are missing that Inquisition v0.1 needs?
6. Which checks prevent fake green most effectively with minimal implementation?
7. What could cause unsafe over-automation if Inquisition is given too much authority?
8. Which stage in the blueprint task should be executed first and why?
9. What conditions should block READY_FOR_AGENT for the blueprint task specifically?
10. How should Inquisition report UNKNOWN status without turning it into a false PASS?

## Constraints

- No commit/push from VM2
- PC-only commit/push authority
- Advisory is not doctrine until reconciled
- No READY_FOR_AGENT without explicit evidence and owner approval
- Blueprint task is planning only — no implementation
- Advice is raw input until ingested and reconciled through modernization

## Required Response Format

Use `ORGANS/ASTRONOMICON/REGISTRY/ADVISORY_RESPONSES/*` with schema `advisory_response.schema.json`.

Map accepted/rejected recommendations explicitly. Include risk assessment for each recommendation.

## No Fake Green Rules

- Do not declare READY_FOR_AGENT in review response
- Flag unknowns as UNKNOWN/WARNING
- Provide blockers instead of optimistic PASS claims
- Do not claim implementation exists based on blueprint alone
- Do not treat this review pack as proof of Inquisition readiness

## Important Notice

This review pack is an **input request** for external advisory. The advisory response will be:
1. Registered as RAW advisory input
2. Not treated as doctrine until reconciled
3. Subject to Owner accept/reject decisions
4. Used as input to task modernization (TASK-CANDIDATE-004)

The reviewer should provide honest, critical feedback. Optimistic claims without evidence are not useful.
