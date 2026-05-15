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

# STAGE 13 PROMPT — Dashboard Adapter Contract Set A

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

`STAGE-13-DASHBOARD-ADAPTER-CONTRACT-SET-A`

## DEPENDS ON

- `STAGE-01` through `STAGE-12`
- Especially:
  - `STAGE-05-BACKEND-REPORT-CONTRACT-IMPLEMENTATION-LANE-A`
  - `STAGE-06-BACKEND-REPORT-CONTRACT-IMPLEMENTATION-LANE-B`
  - `STAGE-07-NO-FAKE-GREEN-CHECKERS`
  - `STAGE-08-STALE-STATUS-CHECKERS`
  - `STAGE-12-ROLLBACK-STOP-RECEIPT-PATH`

Required evidence:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/BACKEND_TRUTH_BASELINE_INDEX.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/CHECKS/NO_FAKE_GREEN/no_fake_green_rules.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/CHECKS/STALE_STATUS/stale_status_rules.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/GATES/V1_HARDENING_GATE_INDEX_FREEZE.json
```

## STAGE GOAL

Create dashboard data adapter contracts and fixture models for the first two foundational organs:

1. Astronomicon
2. Administratum

This stage defines how their dashboards will read real backend reports and expose truth-safe dashboard data without building UI yet.

## WHY THIS STAGE EXISTS

Kiro recommended dashboard data adapters before dashboard UI. Speculum warned that dashboards can become fake-green surfaces if they read mock data, stale data, or mutate canonical state.

Owner wants dashboards where:
- every shown backend mechanism is drawn correctly;
- every script shown actually exists or is disabled;
- every button works or is disabled with reason;
- every green status has evidence;
- stage progress in Astronomicon comes from Administratum truth.

This stage creates the adapter contracts that make that possible for Astronomicon and Administratum.

## SOURCE FILES TO READ

Read:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_A/contracts/organ_self_report_v1_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_A/contracts/stage_map_v1_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_A/contracts/stage_record_v1_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_A/contracts/work_packet_v1_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_A/contracts/route_sheet_v1_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_B/contracts/admin_stage_completion_receipt_v1_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_B/contracts/final_bundle_manifest_v1_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/OWNERSHIP/FOUNDATIONAL_ORGANS_V1_OWNERSHIP_FREEZE.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/V1_DASHBOARD_TRUTH_CONTRACT.md
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-DEFINITION-V0_1/DASHBOARD_TRUTH_AND_BEAUTY_DOCTRINE_V0_1.md
```

Inspect existing folders only for compatibility:
```text
ORGANS/ASTRONOMICON/
ORGANS/ADMINISTRATUM/
SANCTUM/
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
│   ├── dashboard_adapter_common_contract.json
│   ├── dashboard_adapter_common_contract.md
│   ├── ASTRONOMICON/
│   │   ├── astronomicon_dashboard_adapter_contract.json
│   │   ├── astronomicon_dashboard_state_contract.json
│   │   ├── astronomicon_dashboard_metrics_contract.json
│   │   ├── astronomicon_dashboard_evidence_index_contract.json
│   │   ├── astronomicon_dashboard_panels_contract.json
│   │   ├── fixtures/
│   │   │   ├── astronomicon_dashboard_state_sample.json
│   │   │   ├── astronomicon_stage_map_panel_sample.json
│   │   │   ├── astronomicon_stage_progress_from_admin_receipt_sample.json
│   │   │   └── astronomicon_blocked_stage_sample.json
│   │   └── report.json
│   └── ADMINISTRATUM/
│       ├── administratum_dashboard_adapter_contract.json
│       ├── administratum_dashboard_state_contract.json
│       ├── administratum_dashboard_metrics_contract.json
│       ├── administratum_dashboard_evidence_index_contract.json
│       ├── administratum_dashboard_panels_contract.json
│       ├── fixtures/
│       │   ├── administratum_dashboard_state_sample.json
│       │   ├── administratum_work_packet_ledger_panel_sample.json
│       │   ├── administratum_route_sheet_panel_sample.json
│       │   └── administratum_bundle_status_panel_sample.json
│       └── report.json
│   └── reports/
│       └── dashboard_adapter_contract_set_a_report.json
LOCAL_TASKS/LT-04-DASHBOARD-DATA-ADAPTERS/STAGES/STAGE-13-DASHBOARD-ADAPTER-CONTRACT-SET-A/
├── STAGE_PLAN.md
├── STAGE_REPORT.json
└── EVIDENCE/
    └── dashboard_adapter_contract_set_a_evidence.json
REPORTS/
└── stage_13_dashboard_adapter_contract_set_a_report.json
```

## FORBIDDEN PATHS

Do not write to:

```text
ORGANS/ASTRONOMICON/DASHBOARD_DATA/
ORGANS/ADMINISTRATUM/DASHBOARD_DATA/
SANCTUM/
scripts/
TOOLS/
ORGANS/DOCTRINARIUM/
ORGANS/OFFICIO_AGENTIS/
```

Do not create real dashboard UI.  
Do not register buttons.  
Do not mutate organ state.  
Do not create production dashboard data adapters in organ folders yet.

## COMMON DASHBOARD ADAPTER CONTRACT

`dashboard_adapter_common_contract.json` must define:

```text
adapter_id
organ_id
adapter_status
source_reports
source_hashes
generated_at_utc
git_head
dashboard_state_path
dashboard_metrics_path
dashboard_evidence_index_path
dashboard_panels_path
dashboard_actions_path
freshness
warnings
blockers
mock_data_allowed: false
truth_source_required: true
not_source_of_truth: true
```

Required common output types:
- `dashboard_state`
- `dashboard_metrics`
- `dashboard_evidence_index`
- `dashboard_panels`
- `dashboard_actions` placeholder with disabled actions only in this stage

## ASTRONOMICON ADAPTER REQUIREMENTS

Astronomicon dashboard adapter must express:

- Astronomicon owns task memory, task scope, stage topology, registration workflow.
- Astronomicon does not own execution lifecycle truth.
- Stage progress display must reference Administratum receipt paths/hashes.
- Future/active/completed/blocked visuals are display states, not completion truth.
- Review pack/export/import panels must be disabled until action contracts exist.
- Any registration action is disabled in this stage with `disabled_reason`.

Required Astronomicon panels:
```text
task_corridor_panel
stage_map_panel
stage_progress_display_panel
registration_readiness_panel
review_pack_panel
blocked_stage_panel
evidence_links_panel
```

Required Astronomicon metrics:
```text
task_count_known
stage_count_total
stage_count_with_admin_receipts
blocked_stage_count
missing_evidence_count
stale_source_count
```

## ADMINISTRATUM ADAPTER REQUIREMENTS

Administratum dashboard adapter must express:

- Administratum owns execution lifecycle truth, work packets, route sheets, stage completion truth, final bundle, continuity pack.
- Administratum does not own stage topology, law/canon, role contracts.
- Work packet ledger must expose stage state from Admin receipts.
- Bundle status must require final bundle manifest evidence.
- Continuity pack builder button must be disabled until action receipt contract exists.
- State transitions must be disabled until action controls are created in later stage.

Required Administratum panels:
```text
work_packet_ledger_panel
route_sheet_panel
stage_ledger_panel
receipt_history_panel
bundle_status_panel
continuity_pack_panel
git_truth_panel
```

Required Administratum metrics:
```text
work_packet_count
active_work_packet_count
blocked_work_packet_count
stage_receipt_coverage
route_sheet_count
bundle_completeness
continuity_pack_readiness
stale_report_count
```

## FIXTURE REQUIREMENTS

Every fixture:
- valid JSON;
- `fixture_only: true`;
- `not_production_evidence: true`;
- references source reports/evidence;
- includes freshness fields;
- includes warnings/blockers arrays;
- must not claim real dashboard PASS from mock data.

Bad patterns must be explicitly prevented in contracts:
- Astronomicon completed stage without Admin receipt;
- Admin bundle green without bundle manifest;
- dashboard green with stale/unknown freshness;
- action button enabled without receipt contract.

## PASS CRITERIA

Stage PASS only if:
- common adapter contract exists and parses;
- Astronomicon adapter contracts/fixtures exist and parse;
- Administratum adapter contracts/fixtures exist and parse;
- all fixtures are fixture-only;
- contracts say `mock_data_allowed: false`;
- contracts say dashboards are not source of truth;
- Astronomicon progress requires Admin receipts;
- Administratum bundle status requires bundle manifest;
- no production organ files modified.

## STOP CRITERIA

Stop if:
- dependency evidence missing;
- any adapter allows mock truth data;
- any adapter claims source-of-truth ownership that violates ownership matrix;
- Astronomicon adapter can mark completion without Admin receipt;
- Administratum adapter can show bundle green without manifest;
- any real dashboard UI is created;
- writes occur outside target path.

## FINAL RESPONSE TO OWNER

Use exactly this 4-part Russian form:

1. Step name
2. Full path to stage evidence
3. Verdict
4. 3-4 short Russian comment lines for Owner
