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

# STAGE 03 PROMPT — Schema Baseline Freeze

## ROLE

PC Servitor for IMPERIUM.

## MODE

Cold executor.  
Schema/contracts stage.  
No fake green.  
No dashboard implementation.  
No organ hardening implementation.  
No broad cleanup.  
No VM2 sync.  
Do not create production checkers unless explicitly required by this prompt.

## TASK

`TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING`

## LOCAL TASK

`LT-01-RECONCILIATION-SCHEMAS-CONTRACTS`

## STAGE

`STAGE-03-SCHEMA-BASELINE-FREEZE`

## DEPENDS ON

- `STAGE-01-SOURCE-INTEGRITY-OWNER-MATRIX-FREEZE`
- `STAGE-02-OWNERSHIP-MATRIX-FREEZE-BOUNDARY-LINT`

Required evidence:
```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/SOURCE_PACKAGE/HARDENING_SOURCE_PACKAGE_MANIFEST.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/OWNERSHIP/FOUNDATIONAL_ORGANS_V1_OWNERSHIP_FREEZE.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/OWNERSHIP/OWNERSHIP_BOUNDARY_LINT_REPORT.json
```

## STAGE GOAL

Freeze the minimum schema baseline for the V1 hardening execution.

This stage does not need to implement every final schema perfectly. It must create a stable, explicit baseline set of schema contracts and field requirements so future stages do not invent incompatible evidence, receipts, dashboard data, route sheets, work packets, gates, and bundle manifests.

## WHY THIS STAGE EXISTS

Kiro recommends schemas first, backend truth second, dashboard later. Speculum blocks execution until evidence/receipt schemas and minimum contracts exist.

Without this stage:
- each organ may define incompatible receipts;
- dashboards may use different status fields;
- stage completion evidence may be uncheckable;
- final bundle may miss required fields;
- no-fake-green cannot be enforced consistently.

## SOURCE FILES TO READ

Read:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/V1_MINIMUM_SCHEMA_SET.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/V1_MINIMUM_SCHEMA_SET.md
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/V1_EVIDENCE_RECEIPT_CONTRACTS.md
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/V1_DASHBOARD_TRUTH_CONTRACT.md
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/V1_STALE_STATUS_MODEL.md
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/OWNERSHIP/FOUNDATIONAL_ORGANS_V1_OWNERSHIP_FREEZE.json
```

Also inspect existing schemas if present:
```text
ORGANS/**/SCHEMAS/
ORGANS/PORT_PROTOCOL/
schemas/
```

Do not modify existing schemas in this stage unless they are copied/referenced into the hardening package as baseline references.

## ALLOWED WRITE PATHS

Write only under:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/
```

Recommended outputs:

```text
SCHEMAS/
├── SCHEMA_BASELINE_INDEX.json
├── SCHEMA_BASELINE_INDEX.md
├── V1_SCHEMA_FIELD_REQUIREMENTS.json
├── V1_SCHEMA_FREEZE_REPORT.json
├── CONTRACTS/
│   ├── organ_self_report_contract.md
│   ├── evidence_common_contract.md
│   ├── receipt_common_contract.md
│   ├── gate_report_contract.md
│   ├── work_packet_contract.md
│   ├── route_sheet_contract.md
│   ├── stage_map_contract.md
│   ├── stage_record_contract.md
│   ├── admin_stage_completion_receipt_contract.md
│   ├── role_contract_contract.md
│   ├── role_read_receipt_contract.md
│   ├── law_registry_entry_contract.md
│   ├── law_change_receipt_contract.md
│   ├── task_start_gate_verdict_contract.md
│   ├── dashboard_state_contract.md
│   ├── dashboard_actions_contract.md
│   ├── dashboard_metrics_contract.md
│   ├── dashboard_evidence_index_contract.md
│   ├── dashboard_render_report_contract.md
│   ├── source_package_manifest_contract.md
│   ├── final_bundle_manifest_contract.md
│   ├── stale_status_report_contract.md
│   └── repo_purity_report_contract.md
LOCAL_TASKS/LT-01-RECONCILIATION-SCHEMAS-CONTRACTS/STAGES/STAGE-03-SCHEMA-BASELINE-FREEZE/
├── STAGE_PLAN.md
├── STAGE_REPORT.json
└── EVIDENCE/
    └── schema_baseline_freeze_evidence.json
REPORTS/
└── stage_03_schema_baseline_freeze_report.json
```

## FORBIDDEN PATHS

Do not write to production schema folders yet:
```text
ORGANS/DOCTRINARIUM/SCHEMAS/
ORGANS/ADMINISTRATUM/SCHEMAS/
ORGANS/ASTRONOMICON/SCHEMAS/
ORGANS/OFFICIO_AGENTIS/SCHEMAS/
schemas/
```

Do not modify scripts.  
Do not implement validators.  
Do not change organ behavior.  
This stage freezes the baseline inside the hardening package.

## MINIMUM SCHEMA SET TO FREEZE

Include at minimum these schema/contract IDs:

1. `organ_self_report`
2. `evidence_common`
3. `receipt_common`
4. `gate_report`
5. `work_packet`
6. `route_sheet`
7. `stage_map`
8. `stage_record`
9. `admin_stage_completion_receipt`
10. `role_contract`
11. `role_read_receipt`
12. `law_registry_entry`
13. `law_change_receipt`
14. `task_start_gate_verdict`
15. `dashboard_state`
16. `dashboard_actions`
17. `dashboard_metrics`
18. `dashboard_evidence_index`
19. `dashboard_render_report`
20. `source_package_manifest`
21. `final_bundle_manifest`
22. `stale_status_report`
23. `repo_purity_report`

For each contract, define:

- `schema_id`
- `owner`
- `purpose`
- `source_of_truth_category`
- `v1_minimum_fields`
- `required_fields`
- `optional_fields`
- `produced_by`
- `consumed_by`
- `must_exist_before_execution`
- `can_be_stub_in_v1`
- `defer_notes`
- `fake_green_risks`
- `validation_expectation`

## FIELD REQUIREMENTS

Where applicable, include these universal fields:

```text
id
task_id
stage_id
organ_id
owner_organ
status
verdict
generated_at_utc
git_head
source_paths
source_hashes
evidence_paths
warnings
blockers
schema_version
created_by
```

For stale-sensitive reports:
```text
generated_at_utc
checked_at_utc
expires_after_seconds
stale_status
freshness_verdict
```

For receipts:
```text
receipt_id
receipt_type
action
actor
timestamp_utc
before_state
after_state
evidence_hashes
source_report_paths
```

For dashboard action contracts:
```text
action_id
label_key
enabled
disabled_reason
requires_confirmation
target_script_or_action
expected_report_path
expected_receipt_path
timeout_seconds
success_condition
failure_condition
allowed_roles
```

## REQUIRED OUTPUT BEHAVIOR

`SCHEMA_BASELINE_INDEX.json` must be machine-readable and parse.

`V1_SCHEMA_FIELD_REQUIREMENTS.json` must map every schema ID to minimum fields.

`V1_SCHEMA_FREEZE_REPORT.json` must state:
- schema count;
- which schemas must exist before execution;
- which may be stub contracts in V1;
- unresolved schema questions;
- warnings;
- blockers;
- verdict.

## PASS CRITERIA

Stage PASS only if:
- Stage 01 and 02 evidence exists.
- Minimum schema list contains at least 23 contracts above.
- All schema baseline JSON parses.
- Every schema contract has owner and minimum fields.
- No production schemas are modified.
- No validator implementation is created unless explicitly limited to stage-local reporting.
- No hardening execution readiness is claimed.

## STOP CRITERIA

Stop if:
- ownership freeze missing;
- any critical schema has no owner;
- any critical schema has empty required fields;
- dashboard schemas omit evidence links;
- receipt schemas omit timestamps/hash/evidence;
- stale status model omitted;
- repo purity report omitted;
- any existing production organ file modified.

## FINAL RESPONSE TO OWNER

Use exactly this 4-part Russian form:

1. Step name
2. Full path to stage evidence
3. Verdict
4. 3-4 short Russian comment lines for Owner
