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

# STAGE 06 PROMPT — Backend Report Contract Implementation Lane B

## ROLE

PC Servitor for IMPERIUM.

## MODE

Cold executor.  
Backend-truth implementation lane B.  
No fake green.  
No dashboard UI.  
No Sanctum UI.  
No VM2 sync.  
No broad cleanup.  
No production mutation outside target hardening package.

## TASK

`TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING`

## LOCAL TASK

`LT-02-BACKEND-TRUTH-LAYER`

## STAGE

`STAGE-06-BACKEND-REPORT-CONTRACT-IMPLEMENTATION-LANE-B`

## DEPENDS ON

- `STAGE-05-BACKEND-REPORT-CONTRACT-IMPLEMENTATION-LANE-A`

Required Stage 05 evidence:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_A/backend_truth_lane_a_index.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_A/reports/backend_truth_lane_a_report.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/LOCAL_TASKS/LT-02-BACKEND-TRUTH-LAYER/STAGES/STAGE-05-BACKEND-REPORT-CONTRACT-IMPLEMENTATION-LANE-A/STAGE_REPORT.json
```

Also depends on Stage 01-04 foundation.

## STAGE GOAL

Create the second half of backend truth contracts and sample fixtures for:

1. `admin_stage_completion_receipt`
2. `role_contract`
3. `role_read_receipt`
4. `law_registry_entry`
5. `law_change_receipt`
6. `task_start_gate_verdict`
7. `source_package_manifest`
8. `final_bundle_manifest`

This stage completes the backend contract baseline needed before no-fake-green, stale-status, task corridor wiring, dashboard adapters, dashboard UI, and final bundle work.

## WHY THIS STAGE EXISTS

Lane A creates general evidence/work/stage/report vocabulary. Lane B creates the specialized contracts needed to connect the four foundational organs:

- Administratum stage truth;
- Officio role proof;
- Doctrinarium law/gate proof;
- Astronomicon source package proof;
- final bundle proof.

Without Lane B, future stages can accidentally record incomplete stage completion, role validation, law changes, task-start verdicts, or bundle closure.

## SOURCE FILES TO READ

Read:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_A/backend_truth_lane_a_index.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/SCHEMAS/SCHEMA_BASELINE_INDEX.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/OWNERSHIP/FOUNDATIONAL_ORGANS_V1_OWNERSHIP_FREEZE.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/GATES/V1_HARDENING_GATE_INDEX_FREEZE.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/V1_EVIDENCE_RECEIPT_CONTRACTS.md
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/V1_LOCAL_TASKS_AND_STAGE_BLUEPRINT.md
```

Inspect current MVP patterns for compatibility only:

```text
ORGANS/DOCTRINARIUM/LAWS/
ORGANS/DOCTRINARIUM/LAW_REGISTRY/
ORGANS/DOCTRINARIUM/GATES/
ORGANS/OFFICIO_AGENTIS/ROLE_CONTRACTS/
ORGANS/ADMINISTRATUM/
ORGANS/ASTRONOMICON/TASK_DRAFTS/
```

Do not modify those existing organ folders.

## ALLOWED WRITE PATHS

Write only under:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/
```

Recommended outputs:

```text
BACKEND_TRUTH/
├── LANE_B/
│   ├── backend_truth_lane_b_index.json
│   ├── backend_truth_lane_b_contracts.md
│   ├── contracts/
│   │   ├── admin_stage_completion_receipt_v1_contract.json
│   │   ├── role_contract_v1_contract.json
│   │   ├── role_read_receipt_v1_contract.json
│   │   ├── law_registry_entry_v1_contract.json
│   │   ├── law_change_receipt_v1_contract.json
│   │   ├── task_start_gate_verdict_v1_contract.json
│   │   ├── source_package_manifest_v1_contract.json
│   │   └── final_bundle_manifest_v1_contract.json
│   ├── fixtures/
│   │   ├── admin_stage_completion_receipt_sample.json
│   │   ├── role_contract_sample.json
│   │   ├── role_read_receipt_sample.json
│   │   ├── law_registry_entry_sample.json
│   │   ├── law_change_receipt_sample.json
│   │   ├── task_start_gate_verdict_sample.json
│   │   ├── source_package_manifest_sample.json
│   │   └── final_bundle_manifest_sample.json
│   └── reports/
│       └── backend_truth_lane_b_report.json
├── BACKEND_TRUTH_BASELINE_SUMMARY.md
└── BACKEND_TRUTH_BASELINE_INDEX.json

LOCAL_TASKS/LT-02-BACKEND-TRUTH-LAYER/STAGES/STAGE-06-BACKEND-REPORT-CONTRACT-IMPLEMENTATION-LANE-B/
├── STAGE_PLAN.md
├── STAGE_REPORT.json
└── EVIDENCE/
    └── backend_truth_lane_b_evidence.json

REPORTS/
└── stage_06_backend_report_contract_implementation_lane_b_report.json
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

Do not implement production validators.  
Do not create dashboard code.  
Do not start task corridor execution.  
Do not create final bundle.  
This stage creates contracts and fixtures only.

## CONTRACT REQUIREMENTS

For each Lane B contract define:

```text
contract_id
schema_id
owner_organ
purpose
source_of_truth_category
required_fields
optional_fields
producer
consumer
required_inputs
required_outputs
evidence_rules
hash_rules
freshness_rules
warning_rules
blocker_rules
dashboard_visibility
sanctum_visibility
validation_expectation
v1_stub_allowed
notes
```

## CONTRACT-SPECIFIC MINIMUMS

### admin_stage_completion_receipt

Owner: Administratum.

Required fields:
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
```

Must state: Astronomicon may display completion, but cannot own completion truth.

### role_contract

Owner: Officio Agentis.

Required fields:
```text
role_id
role_name
mode_id
allowed_actions
forbidden_actions
required_reads
response_contract
stop_conditions
evidence_requirements
owner_approval_required
contract_status
```

### role_read_receipt

Owner: Officio Agentis.

Required fields:
```text
receipt_id
role_id
agent_label
task_id
required_reads
read_paths
read_hashes
read_at_utc
acknowledged_stop_conditions
warnings
blockers
```

### law_registry_entry

Owner: Doctrinarium.

Required fields:
```text
law_id
law_title
law_status
law_version
law_path
law_hash
owner_accepted
active_from_utc
supersedes
evidence_paths
```

### law_change_receipt

Owner: Doctrinarium.

Required fields:
```text
receipt_id
law_id
change_type
before_hash
after_hash
changed_at_utc
owner_approval_path
summary
warnings
blockers
```

### task_start_gate_verdict

Owner: Doctrinarium, consumed by Administratum.

Required fields:
```text
verdict_id
task_id
gate_id
law_index_hash
organ_health_report_path
officio_contract_reference
admin_work_packet_reference
verdict
warnings
blockers
evidence_paths
generated_at_utc
git_head
```

### source_package_manifest

Owner: Astronomicon task draft package.

Required fields:
```text
manifest_id
task_id
source_files
sha256
size_bytes
source_status
git_head_used
created_at_utc
required_for_execution
```

### final_bundle_manifest

Owner: Administratum.

Required fields:
```text
bundle_id
task_id
run_id
created_at_utc
included_files
included_hashes
per_stage_receipts
warnings
blockers
unresolved_items
continuity_summary_path
git_head_final
```

## FIXTURE REQUIREMENTS

Every fixture must:
- be valid JSON;
- mark `fixture_only: true`;
- mark `not_production_evidence: true`;
- not claim real PASS;
- include warnings/blockers arrays;
- include owner organ;
- include sample evidence path(s);
- include git_head placeholder or actual current HEAD with fixture-only marker.

## BACKEND_TRUTH_BASELINE_INDEX.json

Create one index that includes Lane A and Lane B contracts:
- `lane_a_contracts[]`
- `lane_b_contracts[]`
- `total_contracts`
- `contracts_ready_for_later_stages`
- `contracts_stubbed`
- `warnings`
- `blockers`
- `verdict`

## PASS CRITERIA

Stage PASS only if:
- Stage 05 evidence exists and parses.
- All Lane B contracts exist.
- All Lane B fixtures exist.
- Backend truth baseline index exists and parses.
- All JSON files parse.
- Every fixture is marked fixture-only.
- No production organ files changed.
- No final execution readiness claimed.

## STOP CRITERIA

Stop if:
- Stage 05 missing/invalid;
- any Lane B contract lacks owner organ;
- any fixture implies production evidence;
- final bundle manifest claims real bundle;
- task start gate verdict claims real gate execution;
- any output activates Inquisition;
- any existing organ files are modified.

## FINAL RESPONSE TO OWNER

Use exactly this 4-part Russian form:

1. Step name
2. Full path to stage evidence
3. Verdict
4. 3-4 short Russian comment lines for Owner
