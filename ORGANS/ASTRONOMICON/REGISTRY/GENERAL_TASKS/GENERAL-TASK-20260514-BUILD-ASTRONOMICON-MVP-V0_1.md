---
schema_version: general_task_frontmatter_v0_2
general_task_id: GENERAL-TASK-20260514-BUILD-ASTRONOMICON-MVP-V0_1
title: Build Astronomicon Workbench MVP corridor
owner_goal: Prove that Astronomicon can register a real General Task, decompose it into Local Task candidates, select one Local Task, export/import structured Speculum review, modernize the task, create a stage map, review stages, register the task, and prepare Servitor handoff.
desired_outcome: A minimal but real Astronomicon corridor proof with files, dashboard state, review artifacts, stage map, receipts, and no READY_FOR_AGENT change until gates pass.
scope_in:
  - Astronomicon Workbench MVP
  - General Task registration
  - Local Task candidates
  - Selected Local Task
  - Speculum structured review
  - Modernization
  - Stage map
  - Stage review
  - Registration proof
  - Servitor handoff pack
scope_out:
  - Inquisition build
  - VM2 sync
  - READY_FOR_AGENT true
  - Sanctum EE revival
  - UI polish beyond necessary Workbench usability
  - Full Doctrinarium build
  - Full Administratum build
  - Full Officio Agentis build
constraints:
  - PC-only execution in current proof step
  - Keep repo pure
  - Runtime and outbox must stay under E:\IMPERIUM_CONTEXT
  - Do not change READY_FOR_AGENT
forbidden_actions:
  - no VM2 sync
  - no READY_FOR_AGENT true
  - no Inquisition build
  - no Sanctum EE revival
  - no fake green
known_context:
  - Git HEAD 9d5c92c64afcacc40db6e74bcdd1145d5233a44d is the accepted repair point
  - HTML plus Python server Workbench is accepted as Astronomicon MVP dev surface
  - Current Workbench buttons are partly placeholder
  - Fixture parse validate dashboard decompose proof already passed
unknowns:
  - Which Local Task candidate should be selected first
  - Which Speculum review fields must become hard gates in the next implementation
success_criteria:
  - General Task markdown validates
  - Local Task candidates are generated into Astronomicon registry
  - Dashboard data refresh shows candidates
  - One candidate can be selected for next review step
  - READY_FOR_AGENT remains false
failure_criteria:
  - General Task parse or validation fails
  - Candidates are not generated
  - Dashboard claims green without evidence
  - Runtime or outbox is written back into Git repo
expected_deliverables:
  - General Task markdown file
  - Candidate JSON files
  - Dashboard JSON refresh
  - Next-step blocker list for missing Workbench actions
target_organs:
  - ASTRONOMICON
risk_level: MEDIUM
owner_approval_points:
  - Owner approves selected Local Task before Speculum review
  - Owner approves registration before any Servitor handoff
decomposition_hints:
  - Implement real Workbench General Task intake and active-state registration
  - Implement candidate selection and structured Speculum task review export/import
  - Implement stage map generation and stage review loop
local_task_candidate_count_hint: 3
priority: HIGH
dependencies:
  - Astronomicon Workbench MVP baseline
  - Existing General Task parser and validator
  - Existing candidate decomposition script
local_private_boundary_notes:
  - LOCAL context root: E:\IMPERIUM_CONTEXT\LOCAL
  - PRIVATE context root: E:\IMPERIUM_CONTEXT\PRIVATE
  - payload stays outside Git
dashboard_display_title: Astronomicon MVP Corridor Proof
tags:
  - astronomicon
  - workbench
  - general-task
  - corridor-proof
created_by: Owner_Logos_Prime
created_at: 2026-05-14T00:00:00Z
current_status: DRAFT
---

# General Task

## Background

Astronomicon is now the current strategic focus of IMPERIUM. HTML plus Python server Workbench is accepted as the MVP/dev surface.

The goal is not to build all organs now. The goal is to prove one real corridor from General Task to Servitor handoff.

## Detailed Owner Intent

Owner wants Astronomicon to prove one real corridor before any large organ build.

Workbench should be the main interaction surface. CLI scripts are allowed as backend proof, but not as the final Owner workflow.

Do not set READY_FOR_AGENT true. Do not build Inquisition. Do not sync VM2 unless Owner explicitly commands it.

Repo must stay pure. Runtime, outbox, bundles, handoff, local context and private context must remain outside E:\IMPERIUM under E:\IMPERIUM_CONTEXT.

## Known Context

Fixture parse, validate, dashboard generation, and decomposition already passed.

Current Workbench UI is useful as a dashboard, but several buttons are not implemented yet.

## Unknowns and Questions

Which generated Local Task candidate should be selected first?

Which missing Workbench action should be implemented before committing this corridor as usable?

## Notes for Decomposition

Split into small Local Tasks. The first selected task should probably focus on real Workbench intake and active-state registration, because button placeholders are currently blocking Owner flow.

## Notes for Speculum

Speculum must review for fake green risk, missing gates, active-state correctness, repo purity, and whether the selected task is small enough for stage-by-stage execution.

## Notes for Dashboard Display

Astronomicon MVP corridor proof is active as a real General Task draft. READY_FOR_AGENT must remain false.