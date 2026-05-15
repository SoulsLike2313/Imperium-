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

# STAGE 11 PROMPT — Task Start Corridor Gate Link

## ROLE

PC Servitor for IMPERIUM.

## MODE

Cold executor.  
Task-start corridor gate stage.  
No fake green.  
No real task execution.  
No dashboard UI.  
No Sanctum UI.  
No VM2 sync.  
No broad cleanup.

## TASK

`TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING`

## LOCAL TASK

`LT-03-TASK-CORRIDOR-WIRING`

## STAGE

`STAGE-11-TASK-START-CORRIDOR-GATE-LINK`

## DEPENDS ON

- `STAGE-09-ROUTE-SHEET-WORK-PACKET-WIRING`
- `STAGE-10-STAGE-COMPLETION-RECEIPT-PATH`

Required evidence:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/CORRIDOR/ROUTE_WORK_PACKET/route_work_packet_wiring_model.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/CORRIDOR/STAGE_COMPLETION/stage_completion_receipt_path.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_B/contracts/task_start_gate_verdict_v1_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_B/contracts/role_read_receipt_v1_contract.json
```

## STAGE GOAL

Create the hardening-local task-start corridor gate model that links:

- Doctrinarium organ/law readiness;
- Administratum work packet and route sheet;
- Officio role/mode/read proof;
- Astronomicon task scope and stage map;
- Administratum final start confirmation.

This stage defines what must be true before a Servitor is allowed to start executing stages.

## WHY THIS STAGE EXISTS

Owner intent: there is no task start until Administratum confirms that the Servitor is executing the right task, with correct stage map, after Doctrinarium and Officio proofs.

Speculum risk: Admin starts work without law/role proof; Doctrinarium allows stale law; Officio validates wrong role; Astronomicon and Admin disagree on stage map.

This stage links the four-organ corridor before real execution.

## SOURCE FILES TO READ

Read:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/CORRIDOR/ROUTE_WORK_PACKET/route_work_packet_wiring_model.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_B/contracts/task_start_gate_verdict_v1_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_B/contracts/role_read_receipt_v1_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_A/contracts/route_sheet_v1_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_A/contracts/work_packet_v1_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/OWNERSHIP/FOUNDATIONAL_ORGANS_V1_OWNERSHIP_FREEZE.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/GATES/V1_HARDENING_GATE_INDEX_FREEZE.json
```

Inspect Doctrinarium current status for caution:
```text
ORGANS/DOCTRINARIUM/ORGAN_STATUS.json
ORGANS/DOCTRINARIUM/ORGAN_SELF_REPORT.json
ORGANS/DOCTRINARIUM/ORGAN_CONTRACT.json
```

Do not modify those files.

## ALLOWED WRITE PATHS

Write only under:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/
```

Recommended outputs:

```text
CORRIDOR/
├── TASK_START/
│   ├── task_start_corridor_gate_model.md
│   ├── task_start_corridor_gate_model.json
│   ├── task_start_required_proofs.json
│   ├── admin_task_start_confirmation_contract.json
│   ├── fixtures/
│   │   ├── sample_doctrinarium_task_start_gate_verdict.json
│   │   ├── sample_officio_role_read_receipt.json
│   │   ├── sample_astronomicon_stage_map_reference.json
│   │   ├── sample_admin_route_sheet_reference.json
│   │   ├── sample_admin_task_start_confirmation.json
│   │   ├── bad_start_missing_doctrinarium_proof.json
│   │   ├── bad_start_missing_officio_role_receipt.json
│   │   ├── bad_start_stage_map_hash_mismatch.json
│   │   └── bad_start_stale_doctrinarium_gate.json
│   └── reports/
│       └── task_start_corridor_gate_report.json
LOCAL_TASKS/LT-03-TASK-CORRIDOR-WIRING/STAGES/STAGE-11-TASK-START-CORRIDOR-GATE-LINK/
├── STAGE_PLAN.md
├── STAGE_REPORT.json
└── EVIDENCE/
    └── task_start_corridor_gate_evidence.json
REPORTS/
└── stage_11_task_start_corridor_gate_link_report.json
```

## FORBIDDEN PATHS

Do not write to:

```text
ORGANS/DOCTRINARIUM/
ORGANS/ADMINISTRATUM/
ORGANS/OFFICIO_AGENTIS/
ORGANS/ASTRONOMICON/REGISTRY/
SANCTUM/
scripts/
TOOLS/
```

Do not start a real task.  
Do not create real Owner launch receipt.  
Do not mark hardening execution authorized.  
Do not set `READY_FOR_AGENT=true`.

## REQUIRED CORRIDOR MODEL

Define this flow:

```text
TASK_ID exists in Astronomicon task memory
→ Administratum route sheet exists
→ Administratum work packet exists in PLANNED_NOT_STARTED
→ Doctrinarium task-start gate verdict exists
→ Officio role contract/read receipt exists
→ Astronomicon stage map hash matches route sheet
→ Git/source package matches expected HEAD
→ Administratum creates task start confirmation
→ only then stage execution may begin
```

## REQUIRED PROOFS

`task_start_required_proofs.json` must include:

1. `astronomicon_task_scope_proof`
2. `astronomicon_stage_map_hash_proof`
3. `administratum_route_sheet_proof`
4. `administratum_work_packet_proof`
5. `doctrinarium_organ_health_gate_proof`
6. `doctrinarium_law_readiness_gate_proof`
7. `officio_role_contract_proof`
8. `officio_role_read_receipt_proof`
9. `git_truth_proof`
10. `source_package_integrity_proof`
11. `no_fake_green_proof`
12. `stale_status_proof`

For each:
- `owner_organ`
- `required_artifact`
- `hash_required`
- `freshness_required`
- `missing_behavior`
- `stale_behavior`
- `blocker_if_missing`

## ADMIN TASK START CONFIRMATION CONTRACT

Create `admin_task_start_confirmation_contract.json`.

Required fields:
```text
confirmation_id
task_id
work_packet_id
route_sheet_id
stage_map_id
stage_map_hash
doctrinarium_gate_verdict_path
doctrinarium_gate_verdict_hash
officio_role_receipt_path
officio_role_receipt_hash
source_package_manifest_path
source_package_manifest_hash
git_head
confirmation_verdict
warnings
blockers
confirmed_at_utc
confirmed_by
not_owner_launch_receipt: true
```

Important:
- This is task-start confirmation for a specific execution run.
- It is not Owner launch receipt for the entire hardening task unless explicitly created separately.
- In this stage, all fixtures must be fixture-only.

## BAD FIXTURES

Bad fixtures must show failures:
- missing Doctrinarium proof;
- missing Officio receipt;
- stage map hash mismatch;
- stale Doctrinarium gate.

They must include:
```json
"expected_result": "FAIL"
```

## PASS CRITERIA

Stage PASS only if:
- route/work-packet and stage completion dependencies exist;
- task-start model exists;
- required proofs JSON exists;
- admin task start confirmation contract exists;
- all fixtures parse;
- bad fixtures are marked expected fail;
- no real execution start is created;
- Doctrinarium stale/canon uncertainty is not hidden;
- output keeps hardening execution blocked.

## STOP CRITERIA

Stop if:
- dependency evidence missing;
- task start can happen without Doctrinarium proof;
- task start can happen without Officio role proof;
- task start can happen with stage map hash mismatch;
- task start can happen with stale gate;
- output creates real task start;
- output sets `READY_FOR_AGENT=true`;
- existing organ files are modified.

## FINAL RESPONSE TO OWNER

Use exactly this 4-part Russian form:

1. Step name
2. Full path to stage evidence
3. Verdict
4. 3-4 short Russian comment lines for Owner
