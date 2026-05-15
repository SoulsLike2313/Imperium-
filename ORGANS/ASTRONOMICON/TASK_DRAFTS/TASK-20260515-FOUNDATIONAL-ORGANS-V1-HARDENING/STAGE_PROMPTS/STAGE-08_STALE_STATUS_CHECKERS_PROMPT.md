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

# STAGE 08 PROMPT — Stale-Status Checkers

## ROLE

PC Servitor for IMPERIUM.

## MODE

Cold executor.  
Staleness/freshness enforcement stage.  
No fake green.  
No dashboard UI.  
No Sanctum UI.  
No VM2 sync.  
No broad cleanup.  
Do not mutate existing organ truth.

## TASK

`TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING`

## LOCAL TASK

`LT-02-BACKEND-TRUTH-LAYER`

## STAGE

`STAGE-08-STALE-STATUS-CHECKERS`

## DEPENDS ON

- `STAGE-07-NO-FAKE-GREEN-CHECKERS`

Required evidence:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/CHECKS/NO_FAKE_GREEN/no_fake_green_check_report.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/BACKEND_TRUTH_BASELINE_INDEX.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/GATES/V1_HARDENING_GATE_INDEX_FREEZE.json
```

## STAGE GOAL

Create the stale-status model, fixtures, and stage-local checker for freshness enforcement.

This stage ensures that future dashboards, Sanctum aggregation, gate reports, organ self-reports, and task execution receipts cannot show green from stale or unknown freshness data.

## WHY THIS STAGE EXISTS

Speculum identified stale self-report and stale dashboard aggregation as hard fake-green attack surfaces. Kiro recommended evidence freshness and dashboard data adapters.

A stale report can be worse than a missing report because it looks legitimate. This stage prevents stale data from silently rendering as healthy.

## SOURCE FILES TO READ

Read:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/V1_STALE_STATUS_MODEL.md
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/CHECKS/NO_FAKE_GREEN/no_fake_green_rules.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_A/contracts/organ_self_report_v1_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_A/contracts/gate_report_v1_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/LANE_B/contracts/task_start_gate_verdict_v1_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/SCHEMAS/CONTRACTS/stale_status_report_contract.md
```

Also inspect current Doctrinarium self-report only as an example of stale-risk fields:

```text
ORGANS/DOCTRINARIUM/ORGAN_SELF_REPORT.json
ORGANS/DOCTRINARIUM/ORGAN_STATUS.json
```

Do not modify those files.

## ALLOWED WRITE PATHS

Write only under:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/
```

Recommended outputs:

```text
CHECKS/
├── STALE_STATUS/
│   ├── stale_status_rules.json
│   ├── stale_status_contract.md
│   ├── stale_status_checker_design.md
│   ├── stale_status_fixture_index.json
│   ├── fixtures/
│   │   ├── fresh_report_sample.json
│   │   ├── stale_report_sample.json
│   │   ├── unknown_freshness_sample.json
│   │   ├── missing_generated_at_sample.json
│   │   ├── missing_git_head_sample.json
│   │   ├── stale_dashboard_state_sample.json
│   │   └── fresh_dashboard_state_sample.json
│   ├── stale_status_stage_local_check.py
│   └── stale_status_check_report.json
LOCAL_TASKS/LT-02-BACKEND-TRUTH-LAYER/STAGES/STAGE-08-STALE-STATUS-CHECKERS/
├── STAGE_PLAN.md
├── STAGE_REPORT.json
└── EVIDENCE/
    └── stale_status_evidence.json
REPORTS/
└── stage_08_stale_status_checkers_report.json
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

Do not change organ self-reports.  
Do not modify dashboard code.  
Do not change current organ statuses.  
Do not create production checker in shared scripts yet.

## STALE STATUS RULES TO ENCODE

Create `stale_status_rules.json` with at least:

1. `ALL_REPORTS_REQUIRE_GENERATED_AT_UTC`
2. `ALL_REPORTS_REQUIRE_GIT_HEAD`
3. `FRESHNESS_REQUIRES_CHECKED_AT_UTC`
4. `FRESHNESS_REQUIRES_EXPIRES_AFTER_SECONDS`
5. `STALE_STATUS_ENUM`
   Allowed values:
   ```text
   fresh
   stale
   unknown
   not_applicable
   ```
6. `STALE_CANNOT_BE_PASS_GREEN`
7. `UNKNOWN_CANNOT_BE_PASS_GREEN`
8. `DASHBOARD_AGGREGATE_USES_WORST_FRESHNESS`
9. `SANCTUM_CANNOT_UPGRADE_STALE_ORGAN`
10. `STAGE_COMPLETION_RECEIPT_DOES_NOT_EXPIRE_BUT_CAN_HAVE_CONTEXT_FRESHNESS`
11. `SOURCE_PACKAGE_MANIFEST_FROZEN_BUT_MUST_MATCH_EXPECTED_GIT_HEAD`
12. `OWNER_LAUNCH_RECEIPT_DOES_NOT_EXPIRE_WITHIN_EXECUTION_RUN`

## FRESHNESS MODEL

Define in `stale_status_contract.md`:

- operational reports may expire;
- source package freeze is valid only for the expected Git HEAD;
- stage completion receipts are permanent evidence but may be context-stale if referenced by later dashboards without current aggregation;
- dashboard data files must have freshness fields;
- final bundle must preserve stale/warning state, not hide it.

Minimum fields:
```text
generated_at_utc
checked_at_utc
git_head
source_hash
expires_after_seconds
stale_status
freshness_verdict
stale_reason
display_behavior
```

Display behavior:
```text
fresh + PASS evidence -> may render green
fresh + PASS_WITH_WARNINGS -> amber/green-with-warning depending dashboard policy
stale -> amber/red, never green
unknown -> gray/amber, never green
missing freshness -> BLOCKED for truth panels
not_applicable -> allowed only with reason
```

## CHECKER IMPLEMENTATION RULE

A stage-local checker is allowed:

```text
CHECKS/STALE_STATUS/stale_status_stage_local_check.py
```

It may:
- read fixtures;
- compute simple freshness based on generated/checked times and expiration;
- verify stale cannot pass;
- produce report.

It must not:
- scan whole repo unless read-only and explicitly limited;
- modify files;
- be treated as production checker;
- claim full coverage of all future dashboards.

## REQUIRED CHECK REPORT

`stale_status_check_report.json` must include:

```text
task_id
stage_id
created_utc
checker_path
fixtures_checked
fresh_expected_pass
stale_expected_fail
unknown_expected_fail
missing_field_expected_fail
actual_results
warnings
blockers
verdict
coverage_limitations
not_production_checker: true
```

## RELATION TO NO-FAKE-GREEN

This stage must explicitly connect to Stage 07:

- stale green is a fake green;
- unknown freshness green is a fake green;
- dashboard aggregate green from stale organ is a fake green;
- evidence exists but stale may not satisfy current PASS unless the gate says historical evidence is enough;
- final bundle may contain stale historical evidence, but must label it correctly.

## PASS CRITERIA

Stage PASS only if:
- Stage 07 report exists and parses.
- stale status rules JSON exists and parses.
- stale status contract exists.
- fixture index exists and parses.
- fixture JSON files parse.
- stage-local checker/design exists.
- stale and unknown fixtures fail as expected.
- fresh fixture passes as expected.
- report states checker is stage-local/not production.
- no current organ files modified.
- no dashboard/Sanctum green created.

## STOP CRITERIA

Stop if:
- Stage 07 evidence missing;
- stale status enum omitted;
- stale can render green;
- unknown can render green;
- missing generated_at/git_head can pass;
- checker modifies files;
- output claims production freshness coverage;
- any current organ status file is modified.

## FINAL RESPONSE TO OWNER

Use exactly this 4-part Russian form:

1. Step name
2. Full path to stage evidence
3. Verdict
4. 3-4 short Russian comment lines for Owner
