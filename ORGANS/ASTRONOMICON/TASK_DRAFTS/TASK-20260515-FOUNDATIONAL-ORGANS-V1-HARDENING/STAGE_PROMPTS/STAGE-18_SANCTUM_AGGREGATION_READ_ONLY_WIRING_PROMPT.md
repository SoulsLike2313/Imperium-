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

# STAGE 18 PROMPT — Sanctum Aggregation Read-Only Wiring

## ROLE

PC Servitor for IMPERIUM.

## MODE

Cold executor.  
Sanctum read-only aggregation contract stage.  
No fake green.  
No production Sanctum modification.  
No production dashboard deployment.  
No canonical organ state mutation.  
No VM2 sync.  
No broad cleanup.

## TASK

`TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING`

## LOCAL TASK

`LT-06-SANCTUM-E2E-CERTIFICATION`

## STAGE

`STAGE-18-SANCTUM-AGGREGATION-READ-ONLY-WIRING`

## DEPENDS ON

- `STAGE-13-DASHBOARD-ADAPTER-CONTRACT-SET-A`
- `STAGE-14-DASHBOARD-ADAPTER-CONTRACT-SET-B`
- `STAGE-15-DASHBOARD-RENDER-TRUTH-PANELS`
- `STAGE-16-DASHBOARD-ACTION-RECEIPT-CONTROLS`
- `STAGE-17-UTF8-REPO-PURITY-HARDENING-CHECKS`

Required evidence:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/DASHBOARD_DATA/ADAPTER_CONTRACTS/FOUR_ORGAN_DASHBOARD_ADAPTER_INDEX.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/DASHBOARD_UI/RENDER_TRUTH/dashboard_render_truth_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/DASHBOARD_UI/ACTION_CONTROLS/dashboard_action_control_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/CHECKS/UTF8_REPO_PURITY/utf8_repo_purity_check_report.json
```

## STAGE GOAL

Create the Sanctum read-only aggregation wiring contract and stage-local proof fixtures.

This stage defines how Sanctum will aggregate the four foundational organ dashboard data streams without becoming source of truth.

No production Sanctum app changes are allowed in this stage.

## WHY THIS STAGE EXISTS

Owner wants Sanctum to become the “Infinity Gauntlet”: it gathers organ powers and shows a unified command bridge while preserving organ identity.

Speculum warned that Sanctum can become a fake source of truth or hide blockers. Kiro recommended dashboard adapters and aggregation only after backend/dashboard data contracts exist.

This stage creates the read-only aggregation model that future Sanctum implementation must obey.

## SOURCE FILES TO READ

Read:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-DEFINITION-V0_1/SANCTUM_INFINITY_GAUNTLET_INTEGRATION_DRAFT.md
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/DASHBOARD_DATA/ADAPTER_CONTRACTS/FOUR_ORGAN_DASHBOARD_ADAPTER_INDEX.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/DASHBOARD_UI/RENDER_TRUTH/dashboard_visual_state_semantics.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/CHECKS/NO_FAKE_GREEN/no_fake_green_rules.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/CHECKS/STALE_STATUS/stale_status_rules.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/OWNERSHIP/FOUNDATIONAL_ORGANS_V1_OWNERSHIP_FREEZE.json
```

Inspect current `SANCTUM/` only for compatibility and naming awareness. Do not modify it.

## ALLOWED WRITE PATHS

Write only under:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/
```

Recommended outputs:

```text
SANCTUM_AGGREGATION/
├── READ_ONLY/
│   ├── sanctum_read_only_aggregation_contract.md
│   ├── sanctum_read_only_aggregation_contract.json
│   ├── sanctum_organ_input_index.json
│   ├── sanctum_status_aggregation_rules.json
│   ├── sanctum_visual_integration_notes.md
│   ├── sanctum_data_density_model.md
│   ├── sanctum_action_boundary_policy.md
│   ├── fixtures/
│   │   ├── four_organ_input_fresh_all_pass.json
│   │   ├── four_organ_input_one_warning.json
│   │   ├── four_organ_input_one_blocked.json
│   │   ├── four_organ_input_one_stale.json
│   │   ├── sanctum_aggregate_all_pass_sample.json
│   │   ├── sanctum_aggregate_warning_sample.json
│   │   ├── sanctum_aggregate_blocked_sample.json
│   │   ├── bad_sanctum_upgrades_stale_to_green.json
│   │   └── bad_sanctum_writes_canonical_truth.json
│   ├── proof_static_shell/
│   │   ├── README.md
│   │   ├── sanctum_read_only_demo.json
│   │   └── NOT_PRODUCTION.txt
│   └── reports/
│       └── sanctum_read_only_aggregation_report.json
LOCAL_TASKS/LT-06-SANCTUM-E2E-CERTIFICATION/STAGES/STAGE-18-SANCTUM-AGGREGATION-READ-ONLY-WIRING/
├── STAGE_PLAN.md
├── STAGE_REPORT.json
└── EVIDENCE/
    └── sanctum_read_only_aggregation_evidence.json
REPORTS/
└── stage_18_sanctum_aggregation_read_only_wiring_report.json
```

## FORBIDDEN PATHS

Do not write to:

```text
SANCTUM/
ORGANS/*/DASHBOARD/
ORGANS/*/DASHBOARD_DATA/
scripts/
TOOLS/
ORGANS/ADMINISTRATUM/
ORGANS/ASTRONOMICON/REGISTRY/
ORGANS/DOCTRINARIUM/
ORGANS/OFFICIO_AGENTIS/
```

Do not create production Sanctum UI.  
Do not mutate organ state.  
Do not create real dashboard action buttons.  
Do not hide blocker/warning/stale states.

## SANCTUM READ-ONLY CONTRACT

`sanctum_read_only_aggregation_contract.json` must define:

```text
contract_id
created_utc
aggregation_mode: read_only
source_of_truth_owner: individual_organs
sanctum_truth_ownership: none
may_read
may_render
may_request_action
may_write_canonical_state: false
may_upgrade_status: false
must_preserve_source_status: true
must_preserve_source_hash: true
must_preserve_source_path: true
must_preserve_freshness: true
warnings_visible_required: true
blockers_visible_required: true
evidence_links_visible_required: true
```

## ORGAN INPUT INDEX

`sanctum_organ_input_index.json` must include four organs:

- Astronomicon
- Administratum
- Officio Agentis
- Doctrinarium

For each:
```text
organ_id
dashboard_adapter_contract_path
dashboard_state_contract_path
metrics_contract_path
evidence_index_contract_path
style_note
source_truth_categories
must_not_decide
freshness_required
status_can_only_degrade_in_sanctum: true
```

## STATUS AGGREGATION RULES

Create `sanctum_status_aggregation_rules.json`.

Rules:
1. Sanctum aggregate status is worst-status, never best-status.
2. Any BLOCKED organ makes aggregate BLOCKED.
3. Any FAIL organ makes aggregate FAIL unless BLOCKED is worse.
4. Any stale required source prevents GREEN.
5. Any unknown freshness prevents GREEN.
6. Missing evidence prevents GREEN.
7. Warnings must be visible.
8. Sanctum cannot hide source organ status.
9. Sanctum cannot convert disabled Inquisition hook into audit coverage.
10. Sanctum cannot treat advisory as canon.

## DATA DENSITY MODEL

`sanctum_data_density_model.md` must define layers:

1. Level 0: global truth bar.
2. Level 1: four-organ status cards.
3. Level 2: selected organ panel.
4. Level 3: evidence/report viewer.
5. Level 4: raw JSON/source path drawer.

Rule:
- blockers and warnings are always reachable from Level 0/1.
- evidence links are never more than two interactions away.
- animation must not hide status.

## ACTION BOUNDARY POLICY

`sanctum_action_boundary_policy.md` must state:
- Sanctum may show action requests defined by organ action contracts.
- Sanctum does not directly execute hidden shell actions.
- Any meaningful action routes to organ-defined action contract.
- Any action that mutates canonical state needs receipt and correct owner organ.
- In this V1 hardening stage, production actions remain disabled.

## PROOF STATIC SHELL

A static proof folder is allowed:
```text
SANCTUM_AGGREGATION/READ_ONLY/proof_static_shell/
```

It must:
- be clearly not production;
- contain no script execution;
- contain no production UI wiring;
- contain demo JSON only;
- show how four organ statuses could aggregate;
- preserve stale/warning/blocker examples.

## PASS CRITERIA

Stage PASS only if:
- read-only aggregation contract exists and parses;
- organ input index exists and parses;
- status aggregation rules exist and parse;
- data density model exists;
- action boundary policy exists;
- bad fixtures show status upgrade/write truth as expected failures;
- proof shell, if present, is not production;
- no `SANCTUM/` production files modified;
- no organ dashboard production files modified.

## STOP CRITERIA

Stop if:
- dependency evidence missing;
- Sanctum can write canonical truth;
- Sanctum can upgrade stale/blocked/warning status;
- blocker/warning can be hidden;
- action boundary allows hidden shell execution;
- production Sanctum files are modified;
- output claims full Sanctum implementation complete.

## FINAL RESPONSE TO OWNER

Use exactly this 4-part Russian form:

1. Step name
2. Full path to stage evidence
3. Verdict
4. 3-4 short Russian comment lines for Owner
