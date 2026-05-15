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

# STAGE 09 PROMPT — Route Sheet and Work Packet Wiring

## ROLE

PC Servitor for IMPERIUM.

## MODE

Cold executor.  
Task-corridor wiring stage.  
No fake green.  
No dashboard UI.  
No Sanctum UI.  
No VM2 sync.  
No broad cleanup.  
Do not execute a real task through the corridor yet.  
Do not modify production organ state outside the hardening package unless this prompt explicitly allows a read-only inspection.

## TASK

`TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING`

## LOCAL TASK

`LT-03-TASK-CORRIDOR-WIRING`

## STAGE

`STAGE-09-ROUTE-SHEET-WORK-PACKET-WIRING`

## DEPENDS ON

- `STAGE-01-SOURCE-INTEGRITY-OWNER-MATRIX-FREEZE`
- `STAGE-02-OWNERSHIP-MATRIX-FREEZE-BOUNDARY-LINT`
- `STAGE-03-SCHEMA-BASELINE-FREEZE`
- `STAGE-04-GATE-INDEX-STOP-BEHAVIOR-LOCK`
- `STAGE-05-BACKEND-REPORT-CONTRACT-IMPLEMENTATION-LANE-A`
- `STAGE-06-BACKEND-REPORT-CONTRACT-IMPLEMENTATION-LANE-B`
- `STAGE-07-NO-FAKE-GREEN-CHECKERS`
- `STAGE-08-STALE-STATUS-CHECKERS`

Required evidence:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/BACKEND_TRUTH_BASELINE_INDEX.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/CHECKS/NO_FAKE_GREEN/no_fake_green_check_report.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/CHECKS/STALE_STATUS/stale_status_check_report.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/GATES/V1_HARDENING_GATE_INDEX_FREEZE.json
```

## STAGE GOAL

Create the hardening-local route sheet and work packet wiring model that proves how Administratum will accept a TASK_ID, find the corresponding Astronomicon task/stage map, and issue a route sheet without executing the task yet.

This stage prepares the entry lane of the future V1 task corridor.

## WHY THIS STAGE EXISTS

Owner intent: Servitor should come with a `TASK_ID`. Administratum must then:
- accept the task ticket;
- find the task in Astronomicon;
- understand the task scope and stage map;
- issue address/route instructions;
- start recording the task lifecycle only after proper confirmation.

This stage makes that route/work-packet handoff explicit and evidence-backed.

## SOURCE FILES TO READ

Read:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_A/contracts/work_packet_v1_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_A/contracts/route_sheet_v1_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_A/contracts/stage_map_v1_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_B/contracts/source_package_manifest_v1_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/OWNERSHIP/FOUNDATIONAL_ORGANS_V1_OWNERSHIP_FREEZE.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/GATES/V1_HARDENING_GATE_INDEX_FREEZE.json
```

Also read current Astronomicon/Administratum structures for compatibility only:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/
ORGANS/ASTRONOMICON/METHODS/
ORGANS/ADMINISTRATUM/
```

Do not modify existing Administratum or Astronomicon operational files.

## ALLOWED WRITE PATHS

Write only under:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/
```

Recommended outputs:

```text
CORRIDOR/
├── ROUTE_WORK_PACKET/
│   ├── route_work_packet_wiring_model.md
│   ├── route_work_packet_wiring_model.json
│   ├── route_sheet_contract_binding.json
│   ├── work_packet_contract_binding.json
│   ├── task_lookup_trace_contract.json
│   ├── fixtures/
│   │   ├── sample_task_ticket.json
│   │   ├── sample_astronomicon_task_lookup_result.json
│   │   ├── sample_route_sheet.json
│   │   ├── sample_work_packet_opened.json
│   │   └── sample_route_sheet_blocked_missing_task.json
│   └── reports/
│       └── route_work_packet_wiring_report.json
LOCAL_TASKS/LT-03-TASK-CORRIDOR-WIRING/STAGES/STAGE-09-ROUTE-SHEET-WORK-PACKET-WIRING/
├── STAGE_PLAN.md
├── STAGE_REPORT.json
└── EVIDENCE/
    └── route_work_packet_wiring_evidence.json
REPORTS/
└── stage_09_route_sheet_work_packet_wiring_report.json
```

## FORBIDDEN PATHS

Do not write to:

```text
ORGANS/ADMINISTRATUM/
ORGANS/ASTRONOMICON/REGISTRY/
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/
ORGANS/DOCTRINARIUM/
ORGANS/OFFICIO_AGENTIS/
SANCTUM/
scripts/
TOOLS/
E:\IMPERIUM_CONTEXT\
```

Do not start a real work packet in production Administratum.  
Do not register real task execution.  
Do not set `READY_FOR_AGENT=true`.

## REQUIRED MODEL

The route/work-packet wiring model must define this flow:

```text
Servitor or Owner provides TASK_ID
→ Administratum accepts task ticket
→ Administratum reads Astronomicon source for task/stage map
→ Administratum validates task exists
→ Administratum records lookup trace
→ Administratum issues route sheet
→ Administratum opens work packet in planned/not-started state
→ Later stages will add Officio/Doctrinarium proofs before start confirmation
```

## REQUIRED JSON FIELDS

`route_work_packet_wiring_model.json` must include:

```text
task_id
stage_id
created_utc
corridor_phase
source_of_truth_rules
flow_steps[]
required_inputs[]
required_outputs[]
blocking_conditions[]
owner_organ_map
not_execution_start: true
ready_for_agent: false
```

`sample_task_ticket.json`:
```text
task_ticket_id
task_id
submitted_by
submitted_at_utc
source_context
expected_astronomicon_lookup_path
fixture_only: true
```

`sample_route_sheet.json`:
```text
route_sheet_id
task_id
issued_by: ADMINISTRATUM
required_organs
route_steps
source_task_path
source_stage_map_path
source_hashes
required_gates
issued_at_utc
fixture_only: true
not_execution_authorization: true
```

`sample_work_packet_opened.json`:
```text
work_packet_id
task_id
state: PLANNED_NOT_STARTED
current_stage_id: null
assigned_role: null
route_sheet_path
stage_map_path
evidence_paths
created_at_utc
updated_at_utc
owner_organ: ADMINISTRATUM
fixture_only: true
not_execution_start: true
```

## BLOCKING CONDITIONS

Define at least:

- missing TASK_ID;
- task not found in Astronomicon;
- stage map missing;
- source hash mismatch;
- work packet already active for same TASK_ID without Owner override;
- Administratum cannot issue route sheet;
- ownership conflict;
- source package stale;
- dirty worktree;
- VM2 dependency accidentally required.

## PASS CRITERIA

Stage PASS only if:
- all route/work-packet model files exist;
- all JSON files parse;
- all fixtures are `fixture_only: true`;
- work packet state is not execution-started;
- route sheet says not execution authorization;
- no production Administratum/Astronomicon files modified;
- missing-task blocked fixture exists;
- report states this is wiring model, not live corridor execution.

## STOP CRITERIA

Stop if:
- dependency evidence missing;
- work packet fixture claims active execution;
- route sheet fixture implies final authorization;
- any source-of-truth ownership is ambiguous;
- any production organ file is modified;
- JSON invalid;
- output claims task corridor fully operational.

## FINAL RESPONSE TO OWNER

Use exactly this 4-part Russian form:

1. Step name
2. Full path to stage evidence
3. Verdict
4. 3-4 short Russian comment lines for Owner
