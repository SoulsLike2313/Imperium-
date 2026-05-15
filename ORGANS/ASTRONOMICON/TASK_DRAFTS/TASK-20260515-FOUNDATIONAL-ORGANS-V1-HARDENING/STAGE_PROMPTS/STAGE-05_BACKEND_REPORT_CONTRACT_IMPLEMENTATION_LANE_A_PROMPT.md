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

# STAGE 05 PROMPT — Backend Report Contract Implementation Lane A

## ROLE

PC Servitor for IMPERIUM.

## MODE

Cold executor.  
Backend-truth implementation lane A.  
No fake green.  
No dashboard UI.  
No Sanctum UI.  
No VM2 sync.  
No broad cleanup.  
No execution of later stages.  
No production dashboard buttons.  
Do not claim the four-organ corridor is fully operational.

## TASK

`TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING`

## LOCAL TASK

`LT-02-BACKEND-TRUTH-LAYER`

## STAGE

`STAGE-05-BACKEND-REPORT-CONTRACT-IMPLEMENTATION-LANE-A`

## DEPENDS ON

- `STAGE-01-SOURCE-INTEGRITY-OWNER-MATRIX-FREEZE`
- `STAGE-02-OWNERSHIP-MATRIX-FREEZE-BOUNDARY-LINT`
- `STAGE-03-SCHEMA-BASELINE-FREEZE`
- `STAGE-04-GATE-INDEX-STOP-BEHAVIOR-LOCK`

Required evidence:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/SOURCE_PACKAGE/HARDENING_SOURCE_PACKAGE_MANIFEST.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/OWNERSHIP/FOUNDATIONAL_ORGANS_V1_OWNERSHIP_FREEZE.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/SCHEMAS/SCHEMA_BASELINE_INDEX.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/GATES/V1_HARDENING_GATE_INDEX_FREEZE.json
```

## STAGE GOAL

Create the first half of the backend truth layer contracts and stage-local baseline artifacts for:

1. `organ_self_report`
2. `evidence_common`
3. `receipt_common`
4. `gate_report`
5. `work_packet`
6. `route_sheet`
7. `stage_map`
8. `stage_record`

This stage makes the basic backend reporting vocabulary concrete enough for later organ wiring and dashboard data adapters.

## WHY THIS STAGE EXISTS

The hardening task cannot safely build dashboards or task-corridor wiring until the backend report objects are stable.

This stage translates the schema baseline into usable, hardening-local contracts and sample fixtures for the first backend truth lane.

It does not yet wire the live organs. It prepares the contracts and examples that later stages use.

## SOURCE FILES TO READ

Read:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/SCHEMAS/SCHEMA_BASELINE_INDEX.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/SCHEMAS/V1_SCHEMA_FIELD_REQUIREMENTS.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/SCHEMAS/V1_SCHEMA_FREEZE_REPORT.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/OWNERSHIP/FOUNDATIONAL_ORGANS_V1_OWNERSHIP_FREEZE.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/GATES/V1_HARDENING_GATE_INDEX_FREEZE.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/GATES/V1_STOP_BEHAVIOR_MODEL.json
```

Also read existing organ self-report/status files for field compatibility only:

```text
ORGANS/DOCTRINARIUM/ORGAN_SELF_REPORT.json
ORGANS/DOCTRINARIUM/ORGAN_STATUS.json
ORGANS/DOCTRINARIUM/ORGAN_CONTRACT.json
ORGANS/ADMINISTRATUM/REPORTS/
ORGANS/OFFICIO_AGENTIS/
ORGANS/ASTRONOMICON/
```

Do not modify those existing organ files in this stage.

## ALLOWED WRITE PATHS

Write only under:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/
```

Recommended outputs:

```text
BACKEND_TRUTH/
├── LANE_A/
│   ├── backend_truth_lane_a_index.json
│   ├── backend_truth_lane_a_contracts.md
│   ├── contracts/
│   │   ├── organ_self_report_v1_contract.json
│   │   ├── evidence_common_v1_contract.json
│   │   ├── receipt_common_v1_contract.json
│   │   ├── gate_report_v1_contract.json
│   │   ├── work_packet_v1_contract.json
│   │   ├── route_sheet_v1_contract.json
│   │   ├── stage_map_v1_contract.json
│   │   └── stage_record_v1_contract.json
│   ├── fixtures/
│   │   ├── organ_self_report_sample.json
│   │   ├── evidence_common_sample.json
│   │   ├── receipt_common_sample.json
│   │   ├── gate_report_sample.json
│   │   ├── work_packet_sample.json
│   │   ├── route_sheet_sample.json
│   │   ├── stage_map_sample.json
│   │   └── stage_record_sample.json
│   └── reports/
│       └── backend_truth_lane_a_report.json
LOCAL_TASKS/LT-02-BACKEND-TRUTH-LAYER/STAGES/STAGE-05-BACKEND-REPORT-CONTRACT-IMPLEMENTATION-LANE-A/
├── STAGE_PLAN.md
├── STAGE_REPORT.json
└── EVIDENCE/
    └── backend_truth_lane_a_evidence.json
REPORTS/
└── stage_05_backend_report_contract_implementation_lane_a_report.json
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
E:\IMPERIUM_CONTEXT\
```

Do not create dashboard UI.  
Do not create production checkers.  
Do not create route execution behavior.  
Do not mutate current organ state.

## CONTRACT REQUIREMENTS

For each Lane A contract, define:

```text
contract_id
schema_id
owner_organ
purpose
source_of_truth_category
required_fields
optional_fields
status_values_allowed
warning_rules
blocker_rules
evidence_rules
freshness_rules
producer
consumer
dashboard_visibility
sanctum_visibility
validation_expectation
v1_stub_allowed
notes
```

## SAMPLE FIXTURE REQUIREMENTS

Each sample fixture must:
- include `schema_id`;
- include `schema_version`;
- include `generated_at_utc`;
- include `git_head`;
- include at least one evidence path or explicit `evidence_required_later`;
- include `warnings` array;
- include `blockers` array;
- include owner/source information;
- be valid JSON;
- not claim real production PASS if it is only a sample.

Fixtures must mark themselves:

```json
"fixture_only": true
```

and:

```json
"not_production_evidence": true
```

## CONTRACT-SPECIFIC MINIMUMS

### organ_self_report

Required fields:
```text
organ_id
organ_name
status
generated_at_utc
git_head
source_paths
checks
warnings
blockers
evidence_paths
freshness
```

### evidence_common

Required fields:
```text
evidence_id
evidence_type
owner_organ
created_at_utc
git_head
source_paths
source_hashes
related_task_id
related_stage_id
status
warnings
blockers
```

### receipt_common

Required fields:
```text
receipt_id
receipt_type
actor
action
timestamp_utc
before_state
after_state
evidence_hashes
source_report_paths
warnings
blockers
```

### gate_report

Required fields:
```text
gate_id
gate_owner
verdict
required_inputs
required_outputs
pass_condition
stop_condition
checks
evidence_paths
generated_at_utc
git_head
```

### work_packet

Required fields:
```text
work_packet_id
task_id
state
current_stage_id
assigned_role
route_sheet_path
stage_map_path
evidence_paths
created_at_utc
updated_at_utc
owner_organ
```

### route_sheet

Required fields:
```text
route_sheet_id
task_id
issued_by
route_steps
required_organs
required_gates
source_task_path
stage_map_hash
issued_at_utc
```

### stage_map

Required fields:
```text
stage_map_id
task_id
stages
dependencies
source_of_truth_owner
created_at_utc
git_head
```

### stage_record

Required fields:
```text
stage_record_id
task_id
stage_id
state
started_at_utc
completed_at_utc
admin_receipt_path
evidence_paths
warnings
blockers
```

## REQUIRED VALIDATION

Perform:
- JSON parse for every created `.json`;
- non-empty check for every `.md`;
- verify all samples have `fixture_only: true`;
- verify no sample claims production evidence;
- verify all contracts include `owner_organ`;
- verify all contracts include evidence/freshness expectations.

## PASS CRITERIA

Stage PASS only if:
- all Lane A contracts exist;
- all Lane A fixtures exist;
- all JSON files parse;
- every fixture is clearly marked fixture-only;
- every contract has owner, required fields, evidence rules, and validation expectations;
- no production organ files modified;
- no dashboard code created;
- no hardening execution readiness claimed.

## STOP CRITERIA

Stop if:
- dependency evidence missing;
- a required contract cannot be defined;
- any JSON invalid;
- any fixture implies real PASS/prod evidence;
- any contract lacks owner organ;
- writes occur outside target path;
- existing organ files are modified.

## FINAL RESPONSE TO OWNER

Use exactly this 4-part Russian form:

1. Step name
2. Full path to stage evidence
3. Verdict
4. 3-4 short Russian comment lines for Owner
