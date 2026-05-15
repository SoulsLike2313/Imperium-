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

# STAGE 14 PROMPT — Dashboard Adapter Contract Set B

## ROLE

PC Servitor for IMPERIUM.

## MODE

Cold executor.  
Dashboard data adapter contract stage.  
No fake green.  
No dashboard UI rendering.  
No Sanctum UI.  
No production dashboard buttons.  
No VM2 sync.  
No broad cleanup.  
Do not mutate existing organ state outside the hardening package.

## TASK

`TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING`

## LOCAL TASK

`LT-04-DASHBOARD-DATA-ADAPTERS`

## STAGE

`STAGE-14-DASHBOARD-ADAPTER-CONTRACT-SET-B`

## DEPENDS ON

- `STAGE-13-DASHBOARD-ADAPTER-CONTRACT-SET-A`

Required evidence:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/DASHBOARD_DATA/ADAPTER_CONTRACTS/dashboard_adapter_common_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/DASHBOARD_DATA/ADAPTER_CONTRACTS/ASTRONOMICON/report.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/DASHBOARD_DATA/ADAPTER_CONTRACTS/ADMINISTRATUM/report.json
```

## STAGE GOAL

Create dashboard data adapter contracts and fixture models for the remaining two foundational organs:

1. Officio Agentis
2. Doctrinarium

Then create a unified four-organ dashboard adapter index that future dashboard UI and Sanctum stages can read.

## WHY THIS STAGE EXISTS

Officio and Doctrinarium are high-risk dashboard areas:
- Officio dashboard can accidentally imply autonomous agent assignment.
- Doctrinarium dashboard can accidentally imply full canon-green law enforcement or active Inquisition.
- Both can fake trust if read receipts, law receipts, or gate verdicts are stale/missing.

This stage prevents those false claims before UI work begins.

## SOURCE FILES TO READ

Read:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/DASHBOARD_DATA/ADAPTER_CONTRACTS/dashboard_adapter_common_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_B/contracts/role_contract_v1_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_B/contracts/role_read_receipt_v1_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_B/contracts/law_registry_entry_v1_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_B/contracts/law_change_receipt_v1_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_B/contracts/task_start_gate_verdict_v1_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/OWNERSHIP/FOUNDATIONAL_ORGANS_V1_OWNERSHIP_FREEZE.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-DEFINITION-V0_1/DASHBOARD_TRUTH_AND_BEAUTY_DOCTRINE_V0_1.md
```

Inspect existing folders for compatibility only:

```text
ORGANS/OFFICIO_AGENTIS/
ORGANS/DOCTRINARIUM/
```

Do not modify them.

## ALLOWED WRITE PATHS

Write only under:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/
```

Recommended outputs:

```text
DASHBOARD_DATA/
├── ADAPTER_CONTRACTS/
│   ├── OFFICIO_AGENTIS/
│   │   ├── officio_agentis_dashboard_adapter_contract.json
│   │   ├── officio_agentis_dashboard_state_contract.json
│   │   ├── officio_agentis_dashboard_metrics_contract.json
│   │   ├── officio_agentis_dashboard_evidence_index_contract.json
│   │   ├── officio_agentis_dashboard_panels_contract.json
│   │   ├── fixtures/
│   │   │   ├── officio_dashboard_state_sample.json
│   │   │   ├── officio_role_contract_panel_sample.json
│   │   │   ├── officio_role_read_receipt_panel_sample.json
│   │   │   ├── officio_capability_gap_panel_sample.json
│   │   │   └── officio_disabled_registration_action_sample.json
│   │   └── report.json
│   ├── DOCTRINARIUM/
│   │   ├── doctrinarium_dashboard_adapter_contract.json
│   │   ├── doctrinarium_dashboard_state_contract.json
│   │   ├── doctrinarium_dashboard_metrics_contract.json
│   │   ├── doctrinarium_dashboard_evidence_index_contract.json
│   │   ├── doctrinarium_dashboard_panels_contract.json
│   │   ├── fixtures/
│   │   │   ├── doctrinarium_dashboard_state_sample.json
│   │   │   ├── doctrinarium_law_registry_panel_sample.json
│   │   │   ├── doctrinarium_task_start_gate_panel_sample.json
│   │   │   ├── doctrinarium_organ_health_panel_sample.json
│   │   │   ├── doctrinarium_disabled_inquisition_hook_panel_sample.json
│   │   │   └── doctrinarium_advisory_reference_only_panel_sample.json
│   │   └── report.json
│   ├── FOUR_ORGAN_DASHBOARD_ADAPTER_INDEX.json
│   ├── FOUR_ORGAN_DASHBOARD_ADAPTER_INDEX.md
│   └── reports/
│       └── dashboard_adapter_contract_set_b_report.json
LOCAL_TASKS/LT-04-DASHBOARD-DATA-ADAPTERS/STAGES/STAGE-14-DASHBOARD-ADAPTER-CONTRACT-SET-B/
├── STAGE_PLAN.md
├── STAGE_REPORT.json
└── EVIDENCE/
    └── dashboard_adapter_contract_set_b_evidence.json
REPORTS/
└── stage_14_dashboard_adapter_contract_set_b_report.json
```

## FORBIDDEN PATHS

Do not write to:

```text
ORGANS/OFFICIO_AGENTIS/DASHBOARD_DATA/
ORGANS/DOCTRINARIUM/DASHBOARD_DATA/
SANCTUM/
scripts/
TOOLS/
ORGANS/ADMINISTRATUM/
ORGANS/ASTRONOMICON/REGISTRY/
```

Do not activate Inquisition.  
Do not create real law acceptance.  
Do not create agent assignment automation.  
Do not create production dashboard UI.

## OFFICIO AGENTIS ADAPTER REQUIREMENTS

Officio dashboard adapter must express:

- Officio owns role contracts, mode contracts, response contracts, prompt rules, stop conditions, role/read proof.
- Officio does not own execution lifecycle.
- Officio does not autonomously assign agents in V1.
- Registration/creation from dashboard is disabled or Owner-gated in V1.
- Role validity requires contract evidence and read receipts.
- Capability gap must display as warning/blocker, not silent pass.

Required panels:
```text
role_contract_registry_panel
mode_permission_matrix_panel
agent_scope_panel
prompt_trigger_rules_panel
stop_condition_panel
role_read_receipt_panel
capability_gap_panel
trust_proof_panel
```

Required metrics:
```text
role_contract_count
valid_role_contract_count
missing_read_receipt_count
capability_gap_count
blocked_role_count
owner_gated_action_count
```

## DOCTRINARIUM ADAPTER REQUIREMENTS

Doctrinarium dashboard adapter must express:

- Doctrinarium owns law registry, doctrine registry, canon acceptance, organ health gate, task-start gate, violations, disabled Inquisition hook.
- Doctrinarium does not own task scope/stage topology or execution lifecycle.
- Doctrinarium must not pretend full canon-green if current reports/status say owner review or blockers remain.
- Inquisition hook is disabled and must display as disabled/future hook, not active audit.
- Advisory material must display reference-only unless canon receipt exists.
- Law state requires law path/hash/status evidence.
- Task-start gate requires gate verdict evidence/freshness.

Required panels:
```text
organ_health_matrix_panel
law_registry_panel
doctrine_browser_panel
law_readability_panel
law_execution_proof_panel
task_start_gate_panel
violations_panel
disabled_inquisition_hook_panel
advisory_reference_only_panel
```

Required metrics:
```text
active_law_count
draft_law_count
law_integrity_warning_count
organ_health_gate_status
task_start_gate_status
open_violation_count
disabled_hook_count
advisory_reference_count
stale_law_report_count
```

## FOUR-ORGAN ADAPTER INDEX

`FOUR_ORGAN_DASHBOARD_ADAPTER_INDEX.json` must include:
- `organs[]`
- for each organ:
  - `organ_id`
  - `adapter_contract_path`
  - `state_contract_path`
  - `metrics_contract_path`
  - `evidence_index_contract_path`
  - `panels_contract_path`
  - `owner_truth_categories`
  - `must_not_decide`
  - `mock_data_allowed: false`
  - `not_source_of_truth: true`
- `sanctum_ready_for_read_only_aggregation: false`
- `reason`: Sanctum stage not yet executed.

## FIXTURE REQUIREMENTS

Every fixture:
- valid JSON;
- `fixture_only: true`;
- `not_production_evidence: true`;
- includes source evidence references;
- includes freshness fields;
- includes warnings/blockers arrays;
- must not claim real production PASS.

Specific musts:
- Officio disabled registration action sample has `enabled: false`, `disabled_reason`, `owner_gate_required: true`.
- Doctrinarium disabled Inquisition panel sample has `hook_status: DISABLED_V1`, `not_audit: true`.
- Doctrinarium advisory panel sample has `reference_only: true`, `not_canon: true`.

## PASS CRITERIA

Stage PASS only if:
- Officio adapter contracts/fixtures exist and parse;
- Doctrinarium adapter contracts/fixtures exist and parse;
- four-organ adapter index exists and parses;
- all fixtures are fixture-only;
- Officio auto-assignment is not enabled;
- Doctrinarium Inquisition hook remains disabled/not audit;
- advisory does not become canon;
- Sanctum read-only aggregation is not yet claimed ready;
- no production organ files modified.

## STOP CRITERIA

Stop if:
- Stage 13 evidence missing;
- Officio adapter enables autonomous assignment;
- Doctrinarium adapter implies active Inquisition audit;
- Doctrinarium adapter treats advisory as canon;
- any adapter allows mock truth data;
- any production organ file is modified;
- dashboard UI is created prematurely.

## FINAL RESPONSE TO OWNER

Use exactly this 4-part Russian form:

1. Step name
2. Full path to stage evidence
3. Verdict
4. 3-4 short Russian comment lines for Owner
