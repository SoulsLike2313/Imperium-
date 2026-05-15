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

# STAGE 19 PROMPT — End-to-End Proof Run

## ROLE

PC Servitor for IMPERIUM.

## MODE

Cold executor.  
Synthetic E2E proof stage.  
No fake green.  
No real production task execution.  
No production organ mutation.  
No VM2 sync.  
No broad cleanup.  
No dashboard/Sanctum production deployment.

## TASK

`TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING`

## LOCAL TASK

`LT-06-SANCTUM-E2E-CERTIFICATION`

## STAGE

`STAGE-19-END-TO-END-PROOF-RUN`

## DEPENDS ON

- `STAGE-01` through `STAGE-18`

Required evidence:
```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/CORRIDOR/TASK_START/task_start_corridor_gate_model.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/CORRIDOR/STAGE_COMPLETION/stage_completion_receipt_path.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/CORRIDOR/ROLLBACK_STOP/rollback_stop_receipt_path.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/DASHBOARD_DATA/ADAPTER_CONTRACTS/FOUR_ORGAN_DASHBOARD_ADAPTER_INDEX.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/SANCTUM_AGGREGATION/READ_ONLY/sanctum_read_only_aggregation_contract.json
```

## STAGE GOAL

Run a synthetic, hardening-local end-to-end proof of the foundational organ V1 corridor.

The proof must simulate the expected task flow without mutating production organ state:

```text
TASK_ID
→ Doctrinarium readiness proof fixture
→ Administratum route sheet/work packet fixture
→ Officio role/read proof fixture
→ Astronomicon stage map fixture
→ Administratum task-start confirmation fixture
→ synthetic stage completion receipt
→ dashboard adapter fixture updates
→ Sanctum read-only aggregate fixture
→ final synthetic proof report
```

This stage proves the contracts connect coherently.

## WHY THIS STAGE EXISTS

The future V1 hardening must prove not just that files exist, but that the corridor can be followed.

This synthetic proof is the first safe test of:
- source package;
- ownership;
- backend truth contracts;
- no-fake-green;
- stale-status;
- route/work packet;
- task start gate;
- stage completion receipt;
- rollback/STOP path;
- dashboard adapter truth;
- Sanctum read-only aggregation.

It does not certify production readiness by itself.

## SOURCE FILES TO READ

Read all prior stage reports if present:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/REPORTS/
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/LOCAL_TASKS/
```

Read key contracts:

```text
SOURCE_PACKAGE/HARDENING_SOURCE_PACKAGE_MANIFEST.json
OWNERSHIP/FOUNDATIONAL_ORGANS_V1_OWNERSHIP_FREEZE.json
SCHEMAS/SCHEMA_BASELINE_INDEX.json
BACKEND_TRUTH/BACKEND_TRUTH_BASELINE_INDEX.json
GATES/V1_HARDENING_GATE_INDEX_FREEZE.json
CHECKS/NO_FAKE_GREEN/no_fake_green_rules.json
CHECKS/STALE_STATUS/stale_status_rules.json
CORRIDOR/ROUTE_WORK_PACKET/route_work_packet_wiring_model.json
CORRIDOR/STAGE_COMPLETION/stage_completion_receipt_path.json
CORRIDOR/TASK_START/task_start_corridor_gate_model.json
CORRIDOR/ROLLBACK_STOP/rollback_stop_receipt_path.json
DASHBOARD_DATA/ADAPTER_CONTRACTS/FOUR_ORGAN_DASHBOARD_ADAPTER_INDEX.json
DASHBOARD_UI/RENDER_TRUTH/dashboard_render_truth_contract.json
DASHBOARD_UI/ACTION_CONTROLS/dashboard_action_control_contract.json
SANCTUM_AGGREGATION/READ_ONLY/sanctum_read_only_aggregation_contract.json
```

## ALLOWED WRITE PATHS

Write only under:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/
```

Recommended outputs:

```text
E2E_PROOF/
├── SYNTHETIC_TASK_CORRIDOR/
│   ├── synthetic_task_corridor_proof_plan.md
│   ├── synthetic_task_corridor_proof_run.json
│   ├── synthetic_task_id.txt
│   ├── proof_steps/
│   │   ├── 01_task_ticket.json
│   │   ├── 02_doctrinarium_readiness_verdict.json
│   │   ├── 03_administratum_route_sheet.json
│   │   ├── 04_administratum_work_packet.json
│   │   ├── 05_officio_role_read_receipt.json
│   │   ├── 06_astronomicon_stage_map_reference.json
│   │   ├── 07_admin_task_start_confirmation.json
│   │   ├── 08_synthetic_stage_execution_report.json
│   │   ├── 09_admin_stage_completion_receipt.json
│   │   ├── 10_dashboard_adapter_snapshot.json
│   │   ├── 11_sanctum_read_only_aggregate_snapshot.json
│   │   └── 12_synthetic_final_summary.json
│   ├── failure_proofs/
│   │   ├── missing_officio_receipt_blocks_start.json
│   │   ├── stale_doctrinarium_gate_blocks_start.json
│   │   ├── missing_admin_stage_receipt_blocks_completion_display.json
│   │   └── sanctum_stale_aggregate_not_green.json
│   └── reports/
│       └── e2e_synthetic_task_corridor_report.json
LOCAL_TASKS/LT-06-SANCTUM-E2E-CERTIFICATION/STAGES/STAGE-19-END-TO-END-PROOF-RUN/
├── STAGE_PLAN.md
├── STAGE_REPORT.json
└── EVIDENCE/
    └── e2e_proof_run_evidence.json
REPORTS/
└── stage_19_end_to_end_proof_run_report.json
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

Do not create a real task in production registries.  
Do not execute real organ lifecycle.  
Do not alter actual dashboards.  
Do not set `READY_FOR_AGENT=true`.  
Do not create Owner launch receipt.

## SYNTHETIC TASK REQUIREMENTS

Use a synthetic task ID:

```text
SYNTHETIC-TASK-FOUNDATIONAL-ORGANS-V1-CORRIDOR-PROOF
```

Every proof step must include:
- `synthetic_only: true`
- `not_production_evidence: true`
- `task_id`
- `step_id`
- `created_at_utc`
- `git_head`
- `source_contracts`
- `warnings`
- `blockers`

The successful path must show:
1. TASK_ID accepted as synthetic.
2. Doctrinarium readiness fixture is fresh and passes.
3. Administratum route sheet fixture points to stage map.
4. Work packet fixture remains under Administratum ownership.
5. Officio role/read receipt fixture exists.
6. Astronomicon stage map is topology/display source only.
7. Admin task start confirmation includes Doctrinarium and Officio hashes.
8. Stage execution report is input, not truth.
9. Admin stage completion receipt owns completion truth.
10. Dashboard adapter snapshot reads Admin receipt.
11. Sanctum aggregate reads dashboards and does not upgrade status.
12. Final synthetic summary lists all proofs.

## FAILURE PROOFS

Create failure proof fixtures for:

1. missing Officio receipt blocks task start;
2. stale Doctrinarium gate blocks task start;
3. missing Admin stage receipt blocks completion display;
4. Sanctum cannot show green when one organ aggregate is stale.

Each failure proof must:
- be valid JSON;
- include `expected_result: BLOCKED`;
- include blocker reason;
- include gate that catches it.

## SYNTHETIC PROOF REPORT

`e2e_synthetic_task_corridor_report.json` must include:

```text
task_id
stage_id
synthetic_task_id
created_utc
git_head
proof_steps_total
proof_steps_passed
failure_proofs_total
failure_proofs_passed
source_contracts_used
warnings
blockers
verdict
synthetic_only: true
not_production_execution: true
ready_for_hardening_execution: false
ready_for_agent: false
```

## PASS CRITERIA

Stage PASS only if:
- all previous required evidence exists;
- synthetic proof steps exist and parse;
- failure proof fixtures exist and parse;
- synthetic proof report exists and parses;
- successful synthetic path includes all four organs;
- failure proofs correctly block;
- Sanctum remains read-only;
- no production organ files modified;
- output does not claim real production execution readiness.

## STOP CRITERIA

Stop if:
- dependency evidence missing;
- synthetic proof omits an organ;
- task start succeeds without Doctrinarium or Officio proof;
- completion display succeeds without Admin receipt;
- Sanctum upgrades stale to green;
- output writes to production organ folders;
- output creates real task/registry record;
- output sets `READY_FOR_AGENT=true`.

## FINAL RESPONSE TO OWNER

Use exactly this 4-part Russian form:

1. Step name
2. Full path to stage evidence
3. Verdict
4. 3-4 short Russian comment lines for Owner
