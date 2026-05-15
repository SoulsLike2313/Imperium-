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

# STAGE 07 PROMPT — No-Fake-Green Checkers

## ROLE

PC Servitor for IMPERIUM.

## MODE

Cold executor.  
No-fake-green enforcement stage.  
Checker/proof focused.  
No dashboard UI.  
No Sanctum UI.  
No VM2 sync.  
No broad cleanup.  
Do not make fake green in the anti-fake-green stage.

## TASK

`TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING`

## LOCAL TASK

`LT-02-BACKEND-TRUTH-LAYER`

## STAGE

`STAGE-07-NO-FAKE-GREEN-CHECKERS`

## DEPENDS ON

- `STAGE-05-BACKEND-REPORT-CONTRACT-IMPLEMENTATION-LANE-A`
- `STAGE-06-BACKEND-REPORT-CONTRACT-IMPLEMENTATION-LANE-B`

Required evidence:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/BACKEND_TRUTH_BASELINE_INDEX.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/GATES/V1_HARDENING_GATE_INDEX_FREEZE.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/GATES/V1_STOP_BEHAVIOR_MODEL.json
```

## STAGE GOAL

Create the no-fake-green contract, test fixtures, and hardening-local checker design for the future V1 execution.

This stage should produce a stage-local validation tool or validation method that can detect the most dangerous false-success patterns in the hardening package.

Allowed: create a hardening-package-local checker script under the hardening target directory.  
Forbidden: create production scripts under `scripts/`, `TOOLS/`, or organ implementation folders.

## WHY THIS STAGE EXISTS

Dashboard truth, stage completion, source package integrity, stale status, role/law compliance, and final bundle closure can all fake success if PASS/GREEN statuses are not bound to evidence.

This stage establishes a concrete no-fake-green rule set before dashboard adapters and UI work begin.

## SOURCE FILES TO READ

Read:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/BACKEND_TRUTH_BASELINE_INDEX.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_A/contracts/
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_B/contracts/
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/GATES/V1_STOP_BEHAVIOR_MODEL.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/GATES/V1_WARNING_BUDGET_POLICY.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/V1_DASHBOARD_TRUTH_CONTRACT.md
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/V1_KNOWN_FAILURES_AND_PREVENTIONS.md
```

## ALLOWED WRITE PATHS

Write only under:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/
```

Recommended outputs:

```text
CHECKS/
├── NO_FAKE_GREEN/
│   ├── no_fake_green_rules.json
│   ├── no_fake_green_contract.md
│   ├── no_fake_green_checker_design.md
│   ├── no_fake_green_fixture_index.json
│   ├── fixtures/
│   │   ├── good_status_with_evidence.json
│   │   ├── bad_pass_without_evidence.json
│   │   ├── bad_pass_with_empty_evidence_array.json
│   │   ├── bad_pass_with_warnings.json
│   │   ├── bad_dashboard_green_missing_report.json
│   │   ├── bad_button_enabled_without_receipt.json
│   │   ├── bad_script_visible_without_last_report.json
│   │   ├── bad_sanctum_green_from_stale_source.json
│   │   └── bad_fixture_claims_production_pass.json
│   ├── no_fake_green_stage_local_check.py
│   └── no_fake_green_check_report.json
LOCAL_TASKS/LT-02-BACKEND-TRUTH-LAYER/STAGES/STAGE-07-NO-FAKE-GREEN-CHECKERS/
├── STAGE_PLAN.md
├── STAGE_REPORT.json
└── EVIDENCE/
    └── no_fake_green_evidence.json
REPORTS/
└── stage_07_no_fake_green_checkers_report.json
```

## FORBIDDEN PATHS

Do not write to:
```text
scripts/
TOOLS/
ORGANS/DOCTRINARIUM/
ORGANS/ADMINISTRATUM/
ORGANS/OFFICIO_AGENTIS/
ORGANS/ASTRONOMICON/REGISTRY/
SANCTUM/
```

Do not create production dashboard code.  
Do not edit existing organ reports.  
Do not mark actual organ status as green.  
Do not create final bundle.

## NO-FAKE-GREEN RULES TO ENCODE

Create `no_fake_green_rules.json` with at least these rules:

1. `PASS_REQUIRES_EVIDENCE`
   - Any `PASS`, `GREEN`, `READY`, or `COMPLETE` status requires non-empty evidence paths or evidence hashes.

2. `PASS_WITH_WARNINGS_REQUIRES_WARNING_LIST`
   - `PASS_WITH_WARNINGS` requires non-empty warnings array.

3. `PASS_FORBIDS_HIDDEN_WARNINGS`
   - `PASS` cannot have non-empty warnings.

4. `BLOCKERS_FORBID_PASS`
   - Any non-empty blockers array forbids PASS/GREEN.

5. `DASHBOARD_GREEN_REQUIRES_SOURCE_REPORT`
   - Dashboard green requires source report path and evidence index.

6. `ENABLED_ACTION_REQUIRES_RECEIPT_CONTRACT`
   - Enabled action requires expected receipt path/type and failure behavior.

7. `VISIBLE_SCRIPT_REQUIRES_EXISTENCE_OR_DISABLED_REASON`
   - Script displayed in UI must exist and have last report, or be explicitly disabled.

8. `SANCTUM_CANNOT_OVERRIDE_ORGAN_STATUS`
   - Sanctum aggregate cannot upgrade an organ status.

9. `FIXTURE_CANNOT_COUNT_AS_PRODUCTION_EVIDENCE`
   - Fixture-only samples cannot satisfy production evidence.

10. `STALE_CANNOT_BE_GREEN`
    - Stale/unknown freshness cannot render as green.

11. `ADVISORY_CANNOT_BE_CANON`
    - Advisory material cannot satisfy canon/law acceptance.

12. `READY_FOR_AGENT_REQUIRES_OWNER_LAUNCH`
    - Any true `READY_FOR_AGENT` requires Owner launch receipt.

## CHECKER IMPLEMENTATION RULE

A stage-local checker is allowed:

```text
CHECKS/NO_FAKE_GREEN/no_fake_green_stage_local_check.py
```

It may:
- read fixture files;
- evaluate simple JSON rules;
- produce `no_fake_green_check_report.json`;
- prove that known bad fixtures fail and good fixture passes.

It must not:
- scan entire repo unless limited/read-only;
- modify files;
- be registered as production script;
- claim full production no-fake-green coverage.

## REQUIRED CHECK REPORT

`no_fake_green_check_report.json` must include:

```text
task_id
stage_id
created_utc
checker_path
fixtures_checked
expected_pass_count
expected_fail_count
actual_pass_count
actual_fail_count
bad_fixtures_detected
good_fixtures_passed
warnings
blockers
verdict
coverage_limitations
not_production_checker: true
```

## PASS CRITERIA

Stage PASS only if:
- no-fake-green rules JSON exists and parses;
- no-fake-green contract markdown exists;
- fixture index exists and parses;
- all fixture JSON files parse;
- checker/design exists;
- known bad fixtures are detected as failures;
- good fixture passes;
- report clearly says checker is stage-local/not production;
- no production organ files modified;
- no dashboard green status created.

## STOP CRITERIA

Stop if:
- Stage 05/06 evidence missing;
- no-fake-green rules omit evidence requirement;
- bad fixtures pass;
- good fixture fails without explanation;
- checker modifies files;
- output claims full production coverage;
- any dashboard/Sanctum green is created without evidence;
- writes occur outside allowed path.

## FINAL RESPONSE TO OWNER

Use exactly this 4-part Russian form:

1. Step name
2. Full path to stage evidence
3. Verdict
4. 3-4 short Russian comment lines for Owner
