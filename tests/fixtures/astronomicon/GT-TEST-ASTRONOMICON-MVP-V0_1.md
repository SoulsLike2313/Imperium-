---
schema_version: general_task_frontmatter_v0_2
general_task_id: GT-TEST-ASTRONOMICON-MVP-V0_1
title: Test General Task for Astronomicon MVP dense base
owner_goal: Build parseable general-task pipeline and dashboard-first workbench skeleton
desired_outcome: Produce schemas templates scripts and UI skeleton that supports owner flow without fake green
scope_in:
  - ORGANS/ASTRONOMICON/
  - scripts/
  - tests/fixtures/astronomicon/
scope_out:
  - SANCTUM/
  - KIRO_PLAN_ADVISOR/
  - VM2 routes
constraints:
  - PC-only
  - no commit
  - no push
forbidden_actions:
  - no fake green
  - no READY_FOR_AGENT change
  - no destructive cleanup
known_context:
  - VM2_DEFERRED_OFFLINE
  - active general task remains null until explicit registration
unknowns:
  - exact future Speculum import automation details
success_criteria:
  - parse validate and decompose scripts pass on fixture
  - dashboard data files generated
failure_criteria:
  - parse or validate fails
  - repo-local OUTBOX or runtime recreated
expected_deliverables:
  - schemas
  - templates
  - scripts
  - workbench html
  - dashboard data
target_organs:
  - ASTRONOMICON
risk_level: MEDIUM
owner_approval_points:
  - accept MVP skeleton boundaries
  - accept staged follow-up for full registration loop
decomposition_hints:
  - split parser validator and dashboard generator into separate scripts
  - keep workbench server minimal and dependency-free
local_task_candidate_count_hint: 2
priority: HIGH
dependencies:
  - active state json
  - schema files
local_private_boundary_notes:
  - LOCAL root is E:\\IMPERIUM_CONTEXT\\LOCAL
  - PRIVATE root is E:\\IMPERIUM_CONTEXT\\PRIVATE
  - keep payload outside git
dashboard_display_title: Astronomicon MVP test GT
tags:
  - test-fixture
  - astronomicon
  - mvp
created_by: PC_SERVITOR
created_at: 2026-05-14T15:45:00Z
current_status: DRAFT_TEST_NOT_ACTIVE
---

# General Task

## Background

Astronomicon needs a dense but honest base before full lifecycle automation.

## Detailed Owner Intent

Owner wants workbench-first interaction with structured forms, validation, decomposition, and Speculum-ready exports/import placeholders.

## Known Context

PC-only execution, VM2 deferred, and no canonical active task registration in this fixture.

## Unknowns and Questions

Exact modernization and registration automation details are deferred to next tasks.

## Notes for Decomposition

Generate at least one candidate with metric zones initialized and review status pending.

## Notes for Speculum

Review must be strict structured fields, not free-form only.

## Notes for Dashboard Display

Display NO_ACTIVE_GENERAL_TASK unless explicit registration occurs.
