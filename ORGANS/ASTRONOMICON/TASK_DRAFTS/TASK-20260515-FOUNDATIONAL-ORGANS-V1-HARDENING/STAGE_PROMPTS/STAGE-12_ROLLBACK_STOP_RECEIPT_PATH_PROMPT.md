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

# STAGE 12 PROMPT — Rollback Stop Receipt Path

## ROLE

PC Servitor for IMPERIUM.

## MODE

Cold executor.  
Rollback/STOP discipline stage.  
No fake green.  
No dashboard UI.  
No real hardening execution.  
No VM2 sync.  
No broad cleanup.  
No destructive actions.

## TASK

`TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING`

## LOCAL TASK

`LT-03-TASK-CORRIDOR-WIRING`

## STAGE

`STAGE-12-ROLLBACK-STOP-RECEIPT-PATH`

## DEPENDS ON

- `STAGE-09-ROUTE-SHEET-WORK-PACKET-WIRING`
- `STAGE-10-STAGE-COMPLETION-RECEIPT-PATH`
- `STAGE-11-TASK-START-CORRIDOR-GATE-LINK`

Required evidence:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/CORRIDOR/ROUTE_WORK_PACKET/route_work_packet_wiring_model.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/CORRIDOR/STAGE_COMPLETION/stage_completion_receipt_path.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/CORRIDOR/TASK_START/task_start_corridor_gate_model.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/GATES/V1_STOP_BEHAVIOR_MODEL.json
```

## STAGE GOAL

Create the rollback/STOP receipt path that future stages must use when execution cannot safely continue.

This stage defines how the future 20-stage Servitor records:
- immediate stop;
- failed gate;
- blocked stage;
- warning accepted for continuation;
- Owner decision required;
- rollback/quarantine recommendation;
- partial outputs;
- evidence preservation.

## WHY THIS STAGE EXISTS

A large 20-stage hardening execution must not improvise when something goes wrong.

Speculum required rollback/stop gates. Kiro recommended explicit fail criteria and validation commands for every stage. Owner wants fewer stops, but only if real blockers are handled properly and non-blocking issues are documented.

This stage lets future execution continue through non-blocking warnings and stop cleanly on real blockers.

## SOURCE FILES TO READ

Read:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/GATES/V1_STOP_BEHAVIOR_MODEL.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/GATES/V1_WARNING_BUDGET_POLICY.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/CHECKS/NO_FAKE_GREEN/no_fake_green_rules.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/CHECKS/STALE_STATUS/stale_status_rules.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_A/contracts/receipt_common_v1_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_A/contracts/gate_report_v1_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/V1_20_STAGE_EXECUTION_PLAYBOOK.md
```

If `V1_20_STAGE_EXECUTION_PLAYBOOK.md` exists only in reconciliation package, read:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/V1_20_STAGE_EXECUTION_PLAYBOOK.md
```

## ALLOWED WRITE PATHS

Write only under:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/
```

Recommended outputs:

```text
CORRIDOR/
├── ROLLBACK_STOP/
│   ├── rollback_stop_receipt_path.md
│   ├── rollback_stop_receipt_path.json
│   ├── rollback_stop_receipt_contract.json
│   ├── stage_blocked_receipt_contract.json
│   ├── warning_acceptance_receipt_contract.json
│   ├── owner_decision_required_receipt_contract.json
│   ├── partial_output_quarantine_policy.md
│   ├── fixtures/
│   │   ├── sample_stop_immediate_receipt.json
│   │   ├── sample_stage_blocked_receipt.json
│   │   ├── sample_pass_with_warnings_receipt.json
│   │   ├── sample_owner_decision_required_receipt.json
│   │   ├── sample_partial_output_quarantine_record.json
│   │   ├── bad_stop_without_reason.json
│   │   └── bad_pass_with_blockers.json
│   └── reports/
│       └── rollback_stop_receipt_path_report.json
LOCAL_TASKS/LT-03-TASK-CORRIDOR-WIRING/STAGES/STAGE-12-ROLLBACK-STOP-RECEIPT-PATH/
├── STAGE_PLAN.md
├── STAGE_REPORT.json
└── EVIDENCE/
    └── rollback_stop_receipt_path_evidence.json
REPORTS/
└── stage_12_rollback_stop_receipt_path_report.json
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

Do not execute rollback commands.  
Do not delete files.  
Do not quarantine real outputs.  
Do not change Git history.  
Do not reset worktree.  
This stage defines contracts and fixtures only.

## STOP/ROLLBACK RECEIPT MODEL

Create `rollback_stop_receipt_path.json` defining:

```text
when_to_stop
when_to_continue_with_warning
when_owner_decision_required
how_to_preserve_partial_outputs
how_to record blockers
how_to record warnings
how_to record quarantine recommendation
how_to avoid hiding warnings in PASS
how_to carry unresolved warnings into final bundle
```

## RECEIPT CONTRACTS

### rollback_stop_receipt_contract.json

Required fields:
```text
receipt_id
receipt_type: ROLLBACK_STOP
task_id
stage_id
trigger
stop_category
reason
blocking_gate
affected_files
partial_outputs
preservation_action
recommended_next_action
owner_decision_required
created_at_utc
git_head
warnings
blockers
```

### stage_blocked_receipt_contract.json

Required fields:
```text
receipt_id
task_id
stage_id
blocked_by
blocker_code
blocker_description
evidence_paths
created_at_utc
git_head
recommended_fix
```

### warning_acceptance_receipt_contract.json

Required fields:
```text
receipt_id
task_id
stage_id
warning_codes
warning_descriptions
accepted_by
acceptance_scope
carry_forward_to_final_bundle
created_at_utc
evidence_paths
```

### owner_decision_required_receipt_contract.json

Required fields:
```text
receipt_id
task_id
stage_id
decision_topic
options
recommended_option
risk_if_unanswered
blocked_until_answered
created_at_utc
source_paths
```

## WARNING POLICY

Encode:
- warnings cannot be hidden behind PASS;
- `PASS_WITH_WARNINGS` requires non-empty warning list;
- evidence integrity, ownership, Git truth, repo purity, stale green, and fake green warnings become blockers unless Owner explicitly accepts;
- accepted warnings must be carried into final bundle;
- repeated warning of same type may become blocker if not resolved.

## PARTIAL OUTPUT QUARANTINE POLICY

Define:
- if a stage fails after creating files under target hardening package, do not delete automatically;
- list partial outputs;
- mark them as partial/untrusted;
- recommend quarantine path inside stage folder if needed;
- never reset or delete without Owner instruction;
- never move private/runtime data into repo;
- preserve evidence for debugging.

## FIXTURE REQUIREMENTS

All fixtures:
- valid JSON;
- `fixture_only: true`;
- no real deletion;
- no real rollback;
- expected result clear.

Bad fixtures:
- `bad_stop_without_reason.json` must fail because stop reason missing.
- `bad_pass_with_blockers.json` must fail because blockers forbid PASS.

## OPTIONAL STAGE-LOCAL STATIC CHECK

If simple and safe, create:

```text
CORRIDOR/ROLLBACK_STOP/rollback_stop_receipt_path_static_check.py
```

It may verify:
- required fields exist in fixture receipts;
- bad fixture without reason fails;
- bad PASS with blockers fails;
- warning receipt carries forward to final bundle.

It must not modify files or run rollback actions.

## PASS CRITERIA

Stage PASS only if:
- rollback/stop path docs exist;
- all receipt contracts exist and parse;
- fixture files exist and parse;
- bad fixtures are marked expected fail;
- warning carry-forward rule exists;
- partial output preservation/quarantine policy exists;
- no real rollback/delete/reset performed;
- no production organ files modified;
- hardening execution remains blocked.

## STOP CRITERIA

Stop if:
- dependency evidence missing;
- rollback receipt lacks reason;
- blockers can still PASS;
- warning can be hidden;
- fixture performs destructive action;
- output instructs automatic deletion/reset;
- writes outside target path;
- existing organ files modified.

## FINAL RESPONSE TO OWNER

Use exactly this 4-part Russian form:

1. Step name
2. Full path to stage evidence
3. Verdict
4. 3-4 short Russian comment lines for Owner
