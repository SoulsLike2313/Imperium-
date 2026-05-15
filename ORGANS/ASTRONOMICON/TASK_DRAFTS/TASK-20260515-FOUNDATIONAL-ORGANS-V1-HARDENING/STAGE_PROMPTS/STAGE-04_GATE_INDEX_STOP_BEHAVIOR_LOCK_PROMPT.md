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

# STAGE 04 PROMPT — Gate Index and Stop Behavior Lock

## ROLE

PC Servitor for IMPERIUM.

## MODE

Cold executor.  
Gate/STOP discipline stage.  
No fake green.  
No organ implementation.  
No dashboard implementation.  
No VM2 sync.  
No broad cleanup.

## TASK

`TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING`

## LOCAL TASK

`LT-01-RECONCILIATION-SCHEMAS-CONTRACTS`

## STAGE

`STAGE-04-GATE-INDEX-STOP-BEHAVIOR-LOCK`

## DEPENDS ON

- `STAGE-01-SOURCE-INTEGRITY-OWNER-MATRIX-FREEZE`
- `STAGE-02-OWNERSHIP-MATRIX-FREEZE-BOUNDARY-LINT`
- `STAGE-03-SCHEMA-BASELINE-FREEZE`

Required evidence:
```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/SOURCE_PACKAGE/HARDENING_SOURCE_PACKAGE_MANIFEST.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/OWNERSHIP/OWNERSHIP_BOUNDARY_LINT_REPORT.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/SCHEMAS/V1_SCHEMA_FREEZE_REPORT.json
```

## STAGE GOAL

Freeze the V1 hardening gate index and STOP behavior model for the future 20-stage execution.

This stage ensures the future Servitor knows exactly:
- what must be checked before execution;
- what must be checked before each local task;
- what must be checked before each stage;
- what causes immediate STOP;
- what can continue with warning;
- what needs Owner decision;
- what must never be treated as PASS.

## WHY THIS STAGE EXISTS

Speculum blocked hardening execution until a gate index and stop behavior exist. Kiro recommended stable stage prompts with exact pass/fail criteria and validation commands.

Without this stage:
- future stages may proceed after a real blocker;
- warnings may be hidden behind PASS;
- dashboard green may appear without evidence;
- wrong Git/source files may be used;
- VM2 may be accidentally assumed;
- Owner launch gate may be bypassed;
- final execution may turn into fake green.

## SOURCE FILES TO READ

Read:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/V1_HARDENING_GATE_INDEX.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/V1_HARDENING_GATE_INDEX.md
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/V1_SERVITOR_PRE_EXECUTION_CHECKLIST.md
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/V1_20_STAGE_EXECUTION_PLAYBOOK.md
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/V1_KNOWN_FAILURES_AND_PREVENTIONS.md
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/SCHEMAS/SCHEMA_BASELINE_INDEX.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/OWNERSHIP/FOUNDATIONAL_ORGANS_V1_OWNERSHIP_FREEZE.json
```

## ALLOWED WRITE PATHS

Write only under:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/
```

Recommended outputs:

```text
GATES/
├── V1_HARDENING_GATE_INDEX_FREEZE.json
├── V1_HARDENING_GATE_INDEX_FREEZE.md
├── V1_STOP_BEHAVIOR_MODEL.json
├── V1_STOP_BEHAVIOR_MODEL.md
├── V1_WARNING_BUDGET_POLICY.json
├── V1_OWNER_LAUNCH_GATE_REQUIREMENT.md
├── V1_GATE_TO_STAGE_USAGE_MAP.json
└── GATE_FREEZE_REPORT.json

LOCAL_TASKS/LT-01-RECONCILIATION-SCHEMAS-CONTRACTS/STAGES/STAGE-04-GATE-INDEX-STOP-BEHAVIOR-LOCK/
├── STAGE_PLAN.md
├── STAGE_REPORT.json
└── EVIDENCE/
    ├── gate_index_freeze_evidence.json
    └── stop_behavior_evidence.json

REPORTS/
└── stage_04_gate_index_stop_behavior_lock_report.json
```

## FORBIDDEN PATHS

Do not write to:
```text
ORGANS/DOCTRINARIUM/
ORGANS/ADMINISTRATUM/
ORGANS/ASTRONOMICON/REGISTRY/
ORGANS/OFFICIO_AGENTIS/
SANCTUM/
scripts/
TOOLS/
```

Do not implement gate checkers in production paths.  
Do not enable execution.  
Do not create Owner launch receipt.  
Do not set `READY_FOR_AGENT=true`.

## GATES TO FREEZE

Include at minimum these gates:

1. `GIT_TRUTH_GATE`
2. `SOURCE_PACKAGE_INTEGRITY_GATE`
3. `OWNER_DECISION_MATRIX_GATE`
4. `OWNERSHIP_BOUNDARY_GATE`
5. `STAGE_MAP_VALIDITY_GATE`
6. `EVIDENCE_SCHEMA_GATE`
7. `NO_FAKE_GREEN_GATE`
8. `DASHBOARD_TRUTH_GATE`
9. `TASK_START_CORRIDOR_GATE`
10. `ROLLBACK_STOP_GATE`
11. `VM2_PC_BOUNDARY_GATE`
12. `REGISTRATION_GATE`
13. `UTF8_MOJIBAKE_GATE`
14. `REPO_PURITY_GATE`
15. `STALE_STATUS_GATE`
16. `OWNER_LAUNCH_GATE`

For each gate define:
- `gate_id`
- `owner_organ`
- `purpose`
- `required_inputs`
- `required_outputs`
- `pass_condition`
- `warning_condition`
- `stop_condition`
- `evidence_path_pattern`
- `used_before_execution`
- `used_before_each_local_task`
- `used_before_each_stage`
- `future_stage_usage`
- `blocker_if_missing`
- `related_schema_ids`

## STOP BEHAVIOR MODEL

Create `V1_STOP_BEHAVIOR_MODEL.json` with categories:

1. `STOP_IMMEDIATE`
   Examples:
   - Git HEAD mismatch.
   - Dirty worktree before stage.
   - Required source missing.
   - JSON invalid.
   - Ownership collision.
   - PASS without evidence.
   - Dashboard green from stale/missing data.
   - Writes outside allowed paths.
   - Inquisition claimed active.
   - VM2 assumed without route gate.
   - Owner launch gate missing before execution.

2. `PASS_WITH_WARNINGS_ALLOWED`
   Only if:
   - warnings are explicit and non-blocking;
   - warning list is non-empty;
   - evidence paths exist;
   - future stage impact is documented.

3. `OWNER_DECISION_REQUIRED`
   Examples:
   - source-of-truth ownership change;
   - enabling dashboard mutation action;
   - accepting hard gate PASS_WITH_WARNINGS;
   - changing stage count above budget;
   - enabling VM2;
   - canonizing advisory material.

4. `DEFER_TO_V1_1`
   Examples:
   - semantic search;
   - full visual law diff;
   - event bus;
   - autonomous agent scheduling;
   - heavy WebGL/particle animation;
   - bulk actions.

## WARNING BUDGET POLICY

Define:
- warnings must be categorized;
- warnings cannot be hidden behind PASS;
- `PASS_WITH_WARNINGS` requires non-empty warnings;
- any warning touching evidence integrity, ownership, Git truth, stale green, or repo purity becomes BLOCKER unless explicitly Owner-accepted;
- warnings must be carried forward into final bundle.

## OWNER LAUNCH GATE REQUIREMENT

Explicitly state:
- this stage does not create Owner launch receipt;
- hardening execution remains blocked;
- Owner launch receipt is required after all 20 prompts exist and after Owner approves execution;
- prompt authoring may continue;
- stage decomposition/prompt writing is allowed if prior verdicts allow it.

## GATE TO STAGE USAGE MAP

Create `V1_GATE_TO_STAGE_USAGE_MAP.json` mapping gates to provisional stages S01-S20.

Example expectations:
- S01 uses Git Truth, Source Package Integrity, Owner Decision Matrix.
- S02 uses Ownership Boundary.
- S03 uses Evidence Schema.
- S04 uses Gate Index and Stop Behavior.
- S07 uses No-Fake-Green.
- S08 uses Stale Status.
- S15/S16 use Dashboard Truth.
- S17 uses UTF8/Mojibake and Repo Purity.
- S18 uses Sanctum read-only aggregation.
- S19 uses Task Start Corridor.
- S20 uses Final Bundle / Owner review / certification closure.

## PASS CRITERIA

Stage PASS only if:
- Stage 01-03 evidence exists and parses.
- Gate index freeze JSON exists and parses.
- Stop behavior model JSON exists and parses.
- Warning budget policy exists.
- Owner launch gate requirement exists and says execution is not yet authorized.
- Gate-to-stage usage map exists and parses.
- All 16 gates listed.
- No output claims hardening execution ready.
- No unrelated files changed.

## STOP CRITERIA

Stop if:
- any dependency evidence missing;
- any required gate omitted;
- any gate has no stop condition;
- any gate has no evidence path pattern;
- Owner launch gate is bypassed;
- output sets `READY_FOR_AGENT=true`;
- output implies dashboard/Sanctum may show green without evidence;
- output writes outside allowed path.

## EXPECTED VERDICT

Expected stage verdict:
```text
PASS
```

Expected execution readiness after this stage:
```text
READY_FOR_STAGE_DECOMPOSITION: true or unchanged true
READY_FOR_HARDENING_EXECUTION: false
READY_FOR_AGENT: false
OWNER_LAUNCH_RECEIPT_CREATED: false
```

This is not a failure. This is the correct state.

## FINAL RESPONSE TO OWNER

Use exactly this 4-part Russian form:

1. Step name
2. Full path to stage evidence
3. Verdict
4. 3-4 short Russian comment lines for Owner
