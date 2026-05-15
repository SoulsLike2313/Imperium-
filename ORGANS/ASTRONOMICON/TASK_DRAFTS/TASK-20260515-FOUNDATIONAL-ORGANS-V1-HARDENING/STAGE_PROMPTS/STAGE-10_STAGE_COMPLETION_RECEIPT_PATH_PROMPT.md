# IMPERIUM Foundational Organs V1 Hardening — Stage Prompt

This file is part of the future 20-stage hardening prompt set authored by Logos-Prime.

Current source Git truth for authoring:
- HEAD: `c8458ed4eb3d8a6660b11cc21eedbf21c6a575e0`
- commit_count: `100`
- latest_commit: `TASK-20260515: reconcile V1 hardening gates`
- exact tree: `https://github.com/SoulsLike2313/Imperium-/tree/c8458ed4eb3d8a6660b11cc21eedbf21c6a575e0`

Important:
- This prompt is intended for PC Servitor execution later.
- Do not execute this stage unless the Owner explicitly launches the full hardening execution.
- These prompts are drafted now and should be committed together with all 20 stage prompts after all 20 are authored.

---

# STAGE 10 PROMPT — Stage Completion Receipt Path

## ROLE

PC Servitor for IMPERIUM.

## MODE

Cold executor.  
Stage-completion truth stage.  
No fake green.  
No dashboard UI.  
No real task execution.  
No VM2 sync.  
No broad cleanup.

## TASK

`TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING`

## LOCAL TASK

`LT-03-TASK-CORRIDOR-WIRING`

## STAGE

`STAGE-10-STAGE-COMPLETION-RECEIPT-PATH`

## DEPENDS ON

- `STAGE-09-ROUTE-SHEET-WORK-PACKET-WIRING`

Required evidence:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/CORRIDOR/ROUTE_WORK_PACKET/route_work_packet_wiring_model.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/CORRIDOR/ROUTE_WORK_PACKET/fixtures/sample_work_packet_opened.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_B/contracts/admin_stage_completion_receipt_v1_contract.json
```

## STAGE GOAL

Create the hardening-local stage completion receipt path that proves how a stage may become completed only through Administratum-owned evidence.

This stage prevents Astronomicon, dashboard UI, or Servitor final messages from becoming stage completion truth.

## WHY THIS STAGE EXISTS

Owner intent: Servitor executes stages and reports what was done in a machine-readable form. Administratum records each stage. Astronomicon visualizes progress from Administratum truth.

Speculum risk: stage can be marked complete without Admin receipt, or Astronomicon can show completion from its own graph state.

This stage locks the completion truth path.

## SOURCE FILES TO READ

Read:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_B/contracts/admin_stage_completion_receipt_v1_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_A/contracts/stage_record_v1_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_A/contracts/receipt_common_v1_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/OWNERSHIP/FOUNDATIONAL_ORGANS_V1_OWNERSHIP_FREEZE.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/CHECKS/NO_FAKE_GREEN/no_fake_green_rules.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/CHECKS/STALE_STATUS/stale_status_rules.json
```

## ALLOWED WRITE PATHS

Write only under:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/
```

Recommended outputs:

```text
CORRIDOR/
├── STAGE_COMPLETION/
│   ├── stage_completion_receipt_path.md
│   ├── stage_completion_receipt_path.json
│   ├── stage_completion_truth_rules.json
│   ├── fixtures/
│   │   ├── sample_stage_execution_report_from_servitor.json
│   │   ├── sample_admin_stage_completion_receipt.json
│   │   ├── sample_stage_record_completed.json
│   │   ├── sample_astronomicon_stage_display_update.json
│   │   ├── bad_stage_completed_without_admin_receipt.json
│   │   └── bad_astronomicon_claims_completion_truth.json
│   └── reports/
│       └── stage_completion_receipt_path_report.json
LOCAL_TASKS/LT-03-TASK-CORRIDOR-WIRING/STAGES/STAGE-10-STAGE-COMPLETION-RECEIPT-PATH/
├── STAGE_PLAN.md
├── STAGE_REPORT.json
└── EVIDENCE/
    └── stage_completion_receipt_path_evidence.json
REPORTS/
└── stage_10_stage_completion_receipt_path_report.json
```

## FORBIDDEN PATHS

Do not write to:

```text
ORGANS/ADMINISTRATUM/
ORGANS/ASTRONOMICON/REGISTRY/
ORGANS/DOCTRINARIUM/
ORGANS/OFFICIO_AGENTIS/
SANCTUM/
scripts/
TOOLS/
```

Do not execute a real stage.  
Do not mark actual stages completed.  
Do not modify existing stage maps.  
Do not change dashboards.

## REQUIRED COMPLETION FLOW

Define this flow:

```text
Servitor completes stage work
→ Servitor writes/submits stage execution report
→ Administratum validates required evidence
→ Administratum creates admin_stage_completion_receipt
→ Administratum updates stage_record
→ Astronomicon may display completed state by referencing Admin receipt
→ Dashboard may show completed only if Admin receipt exists and passes evidence/freshness checks
```

## REQUIRED RULES

Create `stage_completion_truth_rules.json` with at least:

1. `ADMINISTRATUM_OWNS_STAGE_COMPLETION_TRUTH`
2. `SERVITOR_REPORT_IS_INPUT_NOT_TRUTH`
3. `ASTRONOMICON_MAY_DISPLAY_NOT_DECIDE_COMPLETION`
4. `DASHBOARD_MAY_DISPLAY_NOT_DECIDE_COMPLETION`
5. `COMPLETED_REQUIRES_ADMIN_RECEIPT`
6. `ADMIN_RECEIPT_REQUIRES_EVIDENCE_PATHS`
7. `WARNINGS_REQUIRE_PASS_WITH_WARNINGS`
8. `BLOCKERS_FORBID_COMPLETED`
9. `STALE_CONTEXT_FORBIDS_GREEN_DISPLAY`
10. `FINAL_MESSAGE_CANNOT_BE_STAGE_COMPLETION_PROOF`

## FIXTURE REQUIREMENTS

All fixtures must be valid JSON and marked:

```json
"fixture_only": true
```

Bad fixtures must be clearly expected to fail.

`sample_admin_stage_completion_receipt.json` must include:
```text
receipt_id
task_id
stage_id
run_id
completed_by
completion_verdict
started_at_utc
completed_at_utc
evidence_paths
evidence_hashes
checks_run
warnings
blockers
admin_verification_status
git_head
fixture_only
```

`sample_astronomicon_stage_display_update.json` must include:
```text
stage_id
display_state
source_admin_receipt_path
source_admin_receipt_hash
display_only: true
not_completion_truth: true
fixture_only: true
```

## OPTIONAL STAGE-LOCAL STATIC CHECK

If simple and safe, create a stage-local static checker under:

```text
CORRIDOR/STAGE_COMPLETION/stage_completion_receipt_path_static_check.py
```

It may verify:
- good fixture has Admin receipt;
- bad fixture without Admin receipt fails;
- Astronomicon display fixture has `display_only: true`;
- no fixture claims completion truth outside Administratum.

It must not scan or modify the repo.

## PASS CRITERIA

Stage PASS only if:
- completion receipt path docs exist;
- completion truth rules JSON exists and parses;
- all fixtures exist and parse;
- bad fixtures are marked expected_fail;
- Astronomicon fixture is display-only;
- Admin receipt fixture owns completion truth;
- no production organ files modified;
- report states this is not real task execution.

## STOP CRITERIA

Stop if:
- Stage 09 evidence missing;
- completion can occur without Admin receipt;
- Astronomicon fixture claims truth owner;
- dashboard fixture claims truth owner;
- blocker can still result in completed;
- JSON invalid;
- output modifies existing organ state.

## FINAL RESPONSE TO OWNER

Use exactly this 4-part Russian form:

1. Step name
2. Full path to stage evidence
3. Verdict
4. 3-4 short Russian comment lines for Owner
