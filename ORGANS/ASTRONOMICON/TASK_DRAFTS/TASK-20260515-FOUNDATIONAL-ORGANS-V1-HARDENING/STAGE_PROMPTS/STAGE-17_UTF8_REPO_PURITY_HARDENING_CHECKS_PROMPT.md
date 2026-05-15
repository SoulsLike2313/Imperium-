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

# STAGE 17 PROMPT — UTF-8 and Repo Purity Hardening Checks

## ROLE

PC Servitor for IMPERIUM.

## MODE

Cold executor.  
Repository hygiene and encoding gate stage.  
No fake green.  
No broad cleanup.  
No deletion.  
No reset.  
No VM2 sync.  
No dashboard UI.  
No Sanctum production wiring.  
No private/local context ingestion.

## TASK

`TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING`

## LOCAL TASK

`LT-06-SANCTUM-E2E-CERTIFICATION`

## STAGE

`STAGE-17-UTF8-REPO-PURITY-HARDENING-CHECKS`

## DEPENDS ON

- `STAGE-01` through `STAGE-16`
- Especially:
  - `STAGE-03-SCHEMA-BASELINE-FREEZE`
  - `STAGE-04-GATE-INDEX-STOP-BEHAVIOR-LOCK`
  - `STAGE-15-DASHBOARD-RENDER-TRUTH-PANELS`
  - `STAGE-16-DASHBOARD-ACTION-RECEIPT-CONTROLS`

Required evidence:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/GATES/V1_HARDENING_GATE_INDEX_FREEZE.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/GATES/V1_STOP_BEHAVIOR_MODEL.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/SCHEMAS/BACKEND_TRUTH_BASELINE_INDEX.json
```

If `SCHEMAS/BACKEND_TRUTH_BASELINE_INDEX.json` does not exist because the actual index path is under `BACKEND_TRUTH/`, use:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/BACKEND_TRUTH_BASELINE_INDEX.json
```

## STAGE GOAL

Create hardening-local UTF-8/mojibake and repo-purity policies, fixtures, and stage-local checks.

This stage protects the 20-stage execution from:
- mojibake regression;
- Russian text in canonical machine artifacts;
- UI translation pollution of canonical state;
- runtime/outbox/bundle/private data leaking into Git;
- accidental writes into `E:\IMPERIUM_CONTEXT`;
- broad cleanup/destructive actions;
- untracked junk after stage execution.

## WHY THIS STAGE EXISTS

Owner repeatedly flagged mojibake and repo pollution as major pain points. Speculum required UTF-8/Mojibake Gate and Repo Purity Gate. Kiro recommended i18n separation and file-based evidence.

This stage ensures final hardening outputs remain readable, clean, and safe to commit.

## SOURCE FILES TO READ

Read:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/V1_REPO_PURITY_CONTRACT.md
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/V1_HARDENING_GATE_INDEX.md
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-DEFINITION-V0_1/DASHBOARD_TRUTH_AND_BEAUTY_DOCTRINE_V0_1.md
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/DASHBOARD_UI/RENDER_TRUTH/dashboard_i18n_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/DASHBOARD_UI/ACTION_CONTROLS/dashboard_action_control_contract.json
```

Also inspect current `.gitignore` and repo root listing in read-only mode:
```text
.gitignore
```

Do not edit `.gitignore` in this stage unless Owner explicitly approves. This stage creates policy/check artifacts under the hardening package.

## ALLOWED WRITE PATHS

Write only under:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/
```

Recommended outputs:

```text
CHECKS/
├── UTF8_REPO_PURITY/
│   ├── utf8_mojibake_policy.md
│   ├── utf8_mojibake_rules.json
│   ├── repo_purity_policy.md
│   ├── repo_purity_rules.json
│   ├── canonical_language_policy.json
│   ├── i18n_boundary_policy.md
│   ├── allowed_repo_roots.json
│   ├── forbidden_repo_patterns.json
│   ├── fixtures/
│   │   ├── good_canonical_english_json.json
│   │   ├── good_ui_ru_i18n_json.json
│   │   ├── bad_canonical_russian_state.json
│   │   ├── bad_mojibake_text_sample.txt
│   │   ├── bad_private_context_repo_path.json
│   │   ├── bad_runtime_outbox_repo_path.json
│   │   └── bad_untracked_junk_path.json
│   ├── utf8_repo_purity_stage_local_check.py
│   └── utf8_repo_purity_check_report.json
LOCAL_TASKS/LT-06-SANCTUM-E2E-CERTIFICATION/STAGES/STAGE-17-UTF8-REPO-PURITY-HARDENING-CHECKS/
├── STAGE_PLAN.md
├── STAGE_REPORT.json
└── EVIDENCE/
    └── utf8_repo_purity_evidence.json
REPORTS/
└── stage_17_utf8_repo_purity_hardening_checks_report.json
```

## FORBIDDEN PATHS

Do not write to:

```text
.gitignore
ORGANS/*/DASHBOARD/
ORGANS/*/DASHBOARD_DATA/
SANCTUM/
scripts/
TOOLS/
E:\IMPERIUM_CONTEXT\
E:\IMPERIUM_LOCAL\
E:\IMPERIUM_PRIVATE\
```

Do not delete or move files.  
Do not run cleanup.  
Do not reset Git.  
Do not stage or commit.  
Do not touch private/local context.

## UTF-8 / LANGUAGE RULES

Create `utf8_mojibake_rules.json` with at least:

1. `CANONICAL_MACHINE_FILES_UTF8_REQUIRED`
2. `NO_REPLACEMENT_CHARACTER_IN_COMMITTED_TEXT`
3. `NO_MOJIBAKE_MARKERS`
   Include detection strings:
   - `Р’`
   - `Р°`
   - `Рµ`
   - `Ð`
   - `Ñ`
   - `вЂ`
   - `�`
4. `CANONICAL_STATE_ENGLISH_ONLY`
5. `RUSSIAN_ALLOWED_IN_UI_I18N`
6. `RUSSIAN_ALLOWED_IN_OWNER_FACING_RU_NOTES`
7. `RUSSIAN_FORBIDDEN_IN_CANONICAL_STATUS_KEYS`
8. `I18N_CANNOT_CHANGE_STATUS_SEMANTICS`
9. `UI_TRANSLATION_FILES_MUST_BE_SEPARATE`
10. `DASHBOARD_UI_MUST_SUPPORT_EN_RU_WHEN_UI_EXISTS`

## REPO PURITY RULES

Create `repo_purity_rules.json` with at least:

1. `REPO_CONTAINS_CANONICAL_TRACKED_PROJECT_ARTIFACTS`
2. `PRIVATE_CONTEXT_OUTSIDE_REPO`
3. `LOCAL_RUNTIME_OUTSIDE_REPO_UNLESS_CANONICALIZED`
4. `NO_OUTBOX_RUNTIME_DUMPS_IN_REPO`
5. `NO_RAW_BUNDLE_ZIPS_IN_CANONICAL_TREE_UNLESS_APPROVED`
6. `NO_BROAD_CLEANUP_DURING_STAGE_EXECUTION`
7. `NO_DELETE_WITHOUT_OWNER_APPROVAL`
8. `FINAL_BUNDLE_HAS_CONTROLLED_DESTINATION`
9. `ARCHIVE_INDEX_REQUIRED_FOR_MOVED_EVIDENCE`
10. `UNTRACKED_JUNK_BLOCKS_COMMIT`

## STAGE-LOCAL CHECKER

Create:

```text
CHECKS/UTF8_REPO_PURITY/utf8_repo_purity_stage_local_check.py
```

It may:
- read only the fixtures under its folder;
- check mojibake markers in fixture text;
- check canonical-vs-i18n path policy in fixture metadata;
- check forbidden repo path fixtures;
- produce `utf8_repo_purity_check_report.json`.

It must not:
- scan entire repo unless read-only and explicitly limited;
- modify files;
- delete files;
- change `.gitignore`;
- stage/commit.

## REQUIRED CHECK REPORT

`utf8_repo_purity_check_report.json` must include:

```text
task_id
stage_id
created_utc
checker_path
fixtures_checked
good_fixtures_passed
bad_fixtures_detected
warnings
blockers
coverage_limitations
not_production_checker: true
verdict
```

## PASS CRITERIA

Stage PASS only if:
- UTF-8/mojibake policy exists;
- repo purity policy exists;
- rules JSON files parse;
- fixtures exist and parse/read;
- checker/report exists;
- bad mojibake/private/runtime fixtures fail;
- good canonical/i18n fixtures pass;
- report states checker is stage-local/not production;
- no repo cleanup or deletion performed;
- no files outside target path changed.

## STOP CRITERIA

Stop if:
- dependency evidence missing;
- output permits Russian canonical status keys;
- output permits mojibake in committed files;
- output permits private context in repo;
- output deletes/moves files;
- checker modifies repo;
- output writes outside target path.

## FINAL RESPONSE TO OWNER

Use exactly this 4-part Russian form:

1. Step name
2. Full path to stage evidence
3. Verdict
4. 3-4 short Russian comment lines for Owner
