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

# STAGE 01 PROMPT — Source Integrity and Owner Matrix Freeze

## ROLE

PC Servitor for IMPERIUM.

## MODE

Cold executor.  
Evidence-first.  
No fake green.  
No broad cleanup.  
No VM2 sync.  
No implementation beyond this stage.  
No dashboard building.  
No organ hardening beyond source integrity and matrix freeze.  
No stage skipping.

## TASK

`TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING`

## LOCAL TASK

`LT-01-RECONCILIATION-SCHEMAS-CONTRACTS`

## STAGE

`STAGE-01-SOURCE-INTEGRITY-OWNER-MATRIX-FREEZE`

## STAGE GOAL

Create the hardening source-integrity foundation and freeze the Owner-approved V1 matrix as a stable source package for the future 20-stage V1 hardening task.

This stage proves that the large hardening task starts from the correct Git commit, correct matrix, correct reconciliation/gates package, correct Kiro/Speculum advisory inputs, and explicit source hashes.

## WHY THIS STAGE EXISTS

The future hardening execution depends on many source files:
- Owner V1 matrix;
- Kiro practical recommendations;
- Speculum red-team;
- reconciliation/gates package;
- ownership matrix;
- gate index;
- schema set;
- stage blueprint;
- execution playbook.

If any of these are stale, missing, mutated, or read from the wrong commit, the entire 20-stage execution becomes unreliable. This stage prevents stale-source and fake-green launch.

## EXPECTED GIT TRUTH

Before doing anything, verify:

```text
HEAD: c8458ed4eb3d8a6660b11cc21eedbf21c6a575e0
commit_count: 100
latest_commit: TASK-20260515: reconcile V1 hardening gates
```

Also verify:
- `git status --short` is clean.
- `origin/master` matches local HEAD.
- HEAD length is exactly 40.
- The exact tree URL can be printed in the stage report.

## SOURCE FILES TO READ

Read these files first:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-DEFINITION-V0_1/PREFILL_RU_OWNER_READABLE/FULL_QUESTIONNAIRE_PREFILL_MATRIX_RU_OWNER_APPROVED_V0_1.md

ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-DEFINITION-V0_1/OWNER_ANSWER_EXTRACT.json

ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-DEFINITION-V0_1/FOUNDATIONAL_ORGANS_V1_DECISION_MATRIX.md

ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-DEFINITION-V0_1/DASHBOARD_TRUTH_AND_BEAUTY_DOCTRINE_V0_1.md

ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-DEFINITION-V0_1/SANCTUM_INFINITY_GAUNTLET_INTEGRATION_DRAFT.md

ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-DEFINITION-V0_1/ADVISORY_REVIEWS/KIRO_PRACTICAL_RECOMMENDATIONS_20260515/KIRO_FOUNDATIONAL_ORGANS_V1_PRACTICAL_RECOMMENDATIONS_20260515.md

ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-DEFINITION_V0_1/ADVISORY_REVIEWS/SPECULUM_RED_TEAM_20260515/SPECULUM_FOUNDATIONAL_ORGANS_V1_RED_TEAM_20260515.md
```

If the path with `_DEFINITION_V0_1` does not exist, use the actual package path:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-DEFINITION-V0_1/
```

Also read from reconciliation package:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/SOURCE_PACKAGE_MANIFEST.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/RECONCILIATION_TABLE.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/RECONCILIATION_SUMMARY.md
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/V1_LOCAL_TASKS_AND_STAGE_BLUEPRINT.md
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/V1_20_STAGE_EXECUTION_PLAYBOOK.md
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/READY_FOR_STAGE_DECOMPOSITION_VERDICT.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/READY_FOR_HARDENING_EXECUTION_VERDICT.json
```

## ALLOWED WRITE PATHS

Create only under:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/
```

Recommended structure for this stage:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/
├── README.md
├── GENERAL_TASK.json
├── SOURCE_PACKAGE/
│   ├── HARDENING_SOURCE_PACKAGE_MANIFEST.json
│   ├── OWNER_MATRIX_FREEZE.md
│   ├── OWNER_MATRIX_FREEZE.json
│   ├── SOURCE_HASHES.sha256
│   └── SOURCE_README.md
├── LOCAL_TASKS/
│   └── LT-01-RECONCILIATION-SCHEMAS-CONTRACTS/
│       ├── LOCAL_TASK.json
│       └── STAGES/
│           └── STAGE-01-SOURCE-INTEGRITY-OWNER-MATRIX-FREEZE/
│               ├── STAGE_PLAN.md
│               ├── STAGE_REPORT.json
│               └── EVIDENCE/
│                   └── source_integrity_evidence.json
└── REPORTS/
    └── stage_01_source_integrity_owner_matrix_freeze_report.json
```

## FORBIDDEN PATHS

Do not write under:
```text
ORGANS/DOCTRINARIUM/
ORGANS/ADMINISTRATUM/
ORGANS/ASTRONOMICON/REGISTRY/
ORGANS/OFFICIO_AGENTIS/
SANCTUM/
scripts/
TOOLS/
E:\IMPERIUM_CONTEXT\
```

Do not modify:
- existing source matrix;
- Kiro/Speculum advisory files;
- reconciliation/gates package;
- Doctrinarium MVP files;
- any existing organ runtime files.

## REQUIRED OUTPUTS

Create:

1. `README.md`
   - Explain this is the hardening package root.
   - State this package is not execution authorization.
   - State `READY_FOR_AGENT` remains false.
   - State hardening execution remains blocked until all 20 prompts exist and Owner launch receipt exists.

2. `GENERAL_TASK.json`
   Required fields:
   - `task_id`
   - `title`
   - `status`
   - `created_utc`
   - `git_head_at_creation`
   - `source_package_manifest_path`
   - `ready_for_agent: false`
   - `ready_for_hardening_execution: false`
   - `owner_launch_receipt_required: true`
   - `local_tasks_expected`
   - `stage_count_expected`
   - `no_vm2_sync: true`

3. `SOURCE_PACKAGE/HARDENING_SOURCE_PACKAGE_MANIFEST.json`
   For every source file read:
   - `source_id`
   - `source_role`
   - `repo_path`
   - `exists`
   - `sha256`
   - `size_bytes`
   - `git_head_used`
   - `required_for_execution`
   - `source_status`

4. `SOURCE_PACKAGE/SOURCE_HASHES.sha256`
   - SHA256 list of source files.

5. `SOURCE_PACKAGE/OWNER_MATRIX_FREEZE.md`
   - Short English summary of Owner decisions that are frozen for execution planning.

6. `SOURCE_PACKAGE/OWNER_MATRIX_FREEZE.json`
   Machine-readable freeze:
   - `matrix_status`
   - `owner_resolutions`
   - `frozen_decisions`
   - `disputed_points_remaining`
   - `source_hashes`
   - `hardening_execution_authorized: false`

7. Stage local task files:
   - `LOCAL_TASKS/LT-01-RECONCILIATION-SCHEMAS-CONTRACTS/LOCAL_TASK.json`
   - `.../STAGES/STAGE-01-SOURCE-INTEGRITY-OWNER-MATRIX-FREEZE/STAGE_PLAN.md`
   - `.../STAGES/STAGE-01-SOURCE-INTEGRITY-OWNER-MATRIX-FREEZE/STAGE_REPORT.json`
   - `.../EVIDENCE/source_integrity_evidence.json`

8. Root report:
   - `REPORTS/stage_01_source_integrity_owner_matrix_freeze_report.json`

## REQUIRED VALIDATIONS

Run or perform:

1. Git validation:
   - HEAD matches expected.
   - worktree clean before changes.
   - origin/master matches local HEAD.

2. Source file validation:
   - all required source files exist;
   - all source hashes recorded;
   - all source sizes recorded;
   - all source statuses explicit.

3. JSON validation:
   - all created JSON parses.

4. Scope validation:
   - `git status --short` after writes touches only hardening package target directory.

5. No-fake-green validation:
   - no output claims hardening execution is ready;
   - `ready_for_agent` remains false;
   - `ready_for_hardening_execution` remains false;
   - stage may claim PASS only if manifest/hash/evidence files exist and parse.

## PASS CRITERIA

Stage PASS only if:
- all required files created;
- all JSON files parse;
- all source files exist and have hashes;
- `HARDENING_SOURCE_PACKAGE_MANIFEST.json` exists;
- `OWNER_MATRIX_FREEZE.json` exists;
- `source_integrity_evidence.json` exists;
- no unrelated files changed;
- hardening execution is still explicitly blocked.

## STOP CRITERIA

Stop without commit if:
- Git HEAD mismatch;
- worktree dirty before writing;
- any required source file missing;
- source file hash cannot be computed;
- JSON validation fails;
- output claims hardening execution ready;
- any write occurs outside allowed target;
- any existing organ implementation file is modified.

## COMMIT POLICY

This stage may be committed only if Owner has launched the 20-stage execution package writing/validation flow.

If committing as part of the future hardening execution:
- Commit message suggestion:
  `TASK-20260515: stage 01 freeze hardening source package`
- Do not push if Owner asked for local-only stage execution.
- Print final Git truth.

## FINAL RESPONSE TO OWNER

Use exactly this 4-part Russian form:

1. Step name
2. Full path to stage evidence
3. Verdict
4. 3-4 short Russian comment lines for Owner

Do not dump huge file contents.
Do not claim hardening execution is ready.
