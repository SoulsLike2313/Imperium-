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

# STAGE 16 PROMPT — Dashboard Action Receipt Controls

## ROLE

PC Servitor for IMPERIUM.

## MODE

Cold executor.  
Dashboard action safety stage.  
No fake green.  
No production dashboard buttons.  
No destructive action.  
No script execution except stage-local validation if explicitly safe.  
No VM2 sync.  
No broad cleanup.

## TASK

`TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING`

## LOCAL TASK

`LT-05-DASHBOARD-UI-LAYER`

## STAGE

`STAGE-16-DASHBOARD-ACTION-RECEIPT-CONTROLS`

## DEPENDS ON

- `STAGE-13-DASHBOARD-ADAPTER-CONTRACT-SET-A`
- `STAGE-14-DASHBOARD-ADAPTER-CONTRACT-SET-B`
- `STAGE-15-DASHBOARD-RENDER-TRUTH-PANELS`

Required evidence:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/DASHBOARD_UI/RENDER_TRUTH/dashboard_render_truth_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/DASHBOARD_DATA/ADAPTER_CONTRACTS/FOUR_ORGAN_DASHBOARD_ADAPTER_INDEX.json
```

## STAGE GOAL

Create dashboard action receipt controls for the future organ dashboards.

This stage defines which dashboard buttons/actions may exist in V1, which must be disabled, which require Owner confirmation, and what receipt/report must be created for every meaningful action.

This stage must not enable production actions. It creates action safety contracts, disabled-action fixtures, and receipt-control rules.

## WHY THIS STAGE EXISTS

Owner wants dashboard buttons to work. Speculum warned that buttons are a major fake-green and unsafe side-effect risk. Kiro recommended action safety through contracts and receipts.

A button without a receipt is a fake control.  
A script button without a failure condition is dangerous.  
A dashboard action that mutates canonical state without ownership rules breaks the organ model.

This stage locks action controls before any real dashboard buttons are implemented.

## SOURCE FILES TO READ

Read:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/DASHBOARD_UI/RENDER_TRUTH/dashboard_render_truth_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/DASHBOARD_UI/RENDER_TRUTH/dashboard_i18n_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_A/contracts/receipt_common_v1_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/OWNERSHIP/FOUNDATIONAL_ORGANS_V1_OWNERSHIP_FREEZE.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/GATES/V1_STOP_BEHAVIOR_MODEL.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-DEFINITION-V0_1/DASHBOARD_TRUTH_AND_BEAUTY_DOCTRINE_V0_1.md
```

Also read dashboard adapter action placeholders from Stage 13/14 if present.

## ALLOWED WRITE PATHS

Write only under:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/
```

Recommended outputs:

```text
DASHBOARD_UI/
├── ACTION_CONTROLS/
│   ├── dashboard_action_control_contract.md
│   ├── dashboard_action_control_contract.json
│   ├── dashboard_action_receipt_contract.json
│   ├── dashboard_action_permission_matrix.json
│   ├── dashboard_action_disable_policy.md
│   ├── dashboard_action_failure_behavior.md
│   ├── per_organ_action_allowlist.json
│   ├── fixtures/
│   │   ├── safe_read_only_export_action.json
│   │   ├── disabled_registration_action.json
│   │   ├── owner_gated_state_transition_action.json
│   │   ├── blocked_destructive_action.json
│   │   ├── bad_enabled_action_without_receipt.json
│   │   ├── bad_action_without_failure_behavior.json
│   │   └── bad_action_wrong_owner_organ.json
│   ├── dashboard_action_receipt_control_static_check.py
│   └── dashboard_action_receipt_control_report.json
LOCAL_TASKS/LT-05-DASHBOARD-UI-LAYER/STAGES/STAGE-16-DASHBOARD-ACTION-RECEIPT-CONTROLS/
├── STAGE_PLAN.md
├── STAGE_REPORT.json
└── EVIDENCE/
    └── dashboard_action_receipt_controls_evidence.json
REPORTS/
└── stage_16_dashboard_action_receipt_controls_report.json
```

## FORBIDDEN PATHS

Do not write to:

```text
ORGANS/*/DASHBOARD/
ORGANS/*/DASHBOARD_DATA/
SANCTUM/
scripts/
TOOLS/
```

Do not enable production actions.  
Do not run destructive actions.  
Do not create real dashboard buttons in production dashboards.  
Do not mutate organ state.  
Do not create Owner launch receipt.

## ACTION CONTROL CONTRACT

`dashboard_action_control_contract.json` must define action fields:

```text
action_id
organ_id
action_type
label_key
description_key
enabled
disabled_reason
owner_gate_required
confirmation_required
allowed_roles
source_of_truth_owner
target_script_or_action
target_write_roots
expected_report_path
expected_receipt_path
receipt_schema_id
timeout_seconds
success_condition
failure_condition
rollback_or_stop_behavior
evidence_paths
warnings
blockers
```

Action types:
```text
read_only_view
read_only_export
refresh_dashboard_data
generate_report
state_transition
registration
bundle_collection
continuity_pack_collection
destructive
owner_gated
disabled_placeholder
```

## V1 ACTION POLICY

Define:

| Action type | V1 default |
|---|---|
| read_only_view | allowed |
| read_only_export | allowed if no mutation |
| refresh_dashboard_data | allowed only if adapter/report receipt exists |
| generate_report | Owner/role-gated with receipt |
| state_transition | disabled unless explicit receipt contract and Owner approval |
| registration | disabled or Owner-gated in V1 |
| bundle_collection | disabled until Administratum bundle contract stage |
| continuity_pack_collection | disabled until final bundle/continuity stage |
| destructive | disabled |
| owner_gated | disabled until Owner confirmation/receipt |
| disabled_placeholder | allowed as visible disabled button |

## PER-ORGAN ACTION ALLOWLIST

`per_organ_action_allowlist.json` must include:

### Astronomicon
Allowed:
- view stage map;
- export review pack if read-only;
- view registration readiness.
Disabled/gated:
- register task;
- import advisory result;
- mutate stage map;
- mark stage complete.

### Administratum
Allowed:
- view work packet ledger;
- view route sheet;
- export reports.
Disabled/gated:
- open work packet;
- confirm task start;
- mark stage complete;
- collect bundle;
- collect continuity pack.

### Officio Agentis
Allowed:
- view role contracts;
- view read receipts;
- view capability gaps.
Disabled/gated:
- register role;
- assign agent;
- change contract;
- override stop condition.

### Doctrinarium
Allowed:
- view laws;
- view doctrine;
- view gate reports;
- view violations.
Disabled/gated:
- accept canon;
- activate law;
- change law status;
- activate Inquisition hook.

## RECEIPT REQUIREMENTS

Every meaningful non-read-only action must require:

```text
receipt_id
action_id
organ_id
actor
role_id
started_at_utc
completed_at_utc
target_paths
before_hashes
after_hashes
verdict
warnings
blockers
expected_report_path
actual_report_path
failure_behavior
```

Read-only actions may not require receipt, but must not mutate state.

## STATIC CHECK

Create stage-local checker:

```text
DASHBOARD_UI/ACTION_CONTROLS/dashboard_action_receipt_control_static_check.py
```

It may:
- load action fixtures;
- verify enabled non-read-only actions require receipt;
- verify destructive actions disabled;
- verify wrong-owner action fails;
- verify disabled actions have disabled_reason;
- produce report.

It must not execute any action or mutate files.

## PASS CRITERIA

Stage PASS only if:
- action control contract exists and parses;
- action receipt contract exists and parses;
- permission matrix exists and parses;
- per-organ allowlist exists and parses;
- fixtures exist and parse;
- static check detects bad fixtures;
- destructive actions disabled;
- registration/state mutation actions disabled or Owner-gated;
- no production dashboard files modified;
- no real action executed.

## STOP CRITERIA

Stop if:
- Stage 15 evidence missing;
- enabled non-read-only action lacks receipt;
- destructive action enabled;
- action owner violates ownership matrix;
- disabled action lacks disabled_reason;
- output creates real production dashboard button;
- output creates Owner launch receipt;
- writes occur outside target path.

## FINAL RESPONSE TO OWNER

Use exactly this 4-part Russian form:

1. Step name
2. Full path to stage evidence
3. Verdict
4. 3-4 short Russian comment lines for Owner
