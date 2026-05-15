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

# STAGE 20 PROMPT — Final Bundle and Certification Closure

## ROLE

PC Servitor for IMPERIUM.

## MODE

Cold executor.  
Final bundle/certification closure stage.  
No fake green.  
No hidden warnings.  
No deletion.  
No broad cleanup.  
No VM2 sync unless Owner explicitly commands later.  
Do not set READY_FOR_AGENT true unless Owner explicitly approved and all gates require it; expected value is false.

## TASK

`TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING`

## LOCAL TASK

`LT-06-SANCTUM-E2E-CERTIFICATION`

## STAGE

`STAGE-20-FINAL-BUNDLE-CERTIFICATION-CLOSURE`

## DEPENDS ON

- `STAGE-01` through `STAGE-19`

Required evidence:
```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/E2E_PROOF/SYNTHETIC_TASK_CORRIDOR/reports/e2e_synthetic_task_corridor_report.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/REPORTS/stage_19_end_to_end_proof_run_report.json
```

## STAGE GOAL

Collect the final hardening evidence bundle, verify all 20 stages are represented, produce certification closure reports, and explicitly preserve warnings/blockers/unresolved items.

This stage closes the hardening package for Owner review.

Expected final state:
- V1 hardening evidence package complete;
- final bundle manifest exists;
- all stage reports indexed;
- unresolved warnings are visible;
- certification candidate created;
- Owner review required;
- `READY_FOR_AGENT` remains false unless Owner separately approves a later launch;
- no fake green.

## WHY THIS STAGE EXISTS

A 20-stage execution is only useful if the final evidence is complete and easy to hand off. Administratum’s future role includes final bundle and continuity pack collection. This stage creates the hardening-local final bundle/certification pattern.

It must not hide warnings or claim more readiness than proven.

## SOURCE FILES TO READ

Read all stage reports and key indexes:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/REPORTS/
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/LOCAL_TASKS/
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/SOURCE_PACKAGE/HARDENING_SOURCE_PACKAGE_MANIFEST.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/OWNERSHIP/FOUNDATIONAL_ORGANS_V1_OWNERSHIP_FREEZE.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/GATES/V1_HARDENING_GATE_INDEX_FREEZE.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/BACKEND_TRUTH/BACKEND_TRUTH_BASELINE_INDEX.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/DASHBOARD_DATA/ADAPTER_CONTRACTS/FOUR_ORGAN_DASHBOARD_ADAPTER_INDEX.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/SANCTUM_AGGREGATION/READ_ONLY/sanctum_read_only_aggregation_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/E2E_PROOF/SYNTHETIC_TASK_CORRIDOR/reports/e2e_synthetic_task_corridor_report.json
```

## ALLOWED WRITE PATHS

Write only under:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/
```

Recommended outputs:

```text
FINAL_BUNDLE/
├── FINAL_HARDENING_BUNDLE_MANIFEST.json
├── FINAL_HARDENING_BUNDLE_SUMMARY.md
├── STAGE_REPORT_INDEX.json
├── STAGE_REPORT_INDEX.md
├── EVIDENCE_COMPLETENESS_REPORT.json
├── WARNING_AND_BLOCKER_LEDGER.md
├── UNRESOLVED_ITEMS_FOR_OWNER_REVIEW.md
├── CERTIFICATION/
│   ├── V1_HARDENING_CERTIFICATION_CANDIDATE.json
│   ├── V1_HARDENING_CERTIFICATION_CANDIDATE.md
│   ├── READY_FOR_OWNER_REVIEW_VERDICT.json
│   ├── READY_FOR_AGENT_VERDICT.json
│   └── OWNER_REVIEW_NOTES_RU.md
├── HANDOFF/
│   ├── NEW_CHAT_HANDOFF_SUMMARY.md
│   ├── LOGOS_PRIME_CONTINUITY_NOTE.md
│   └── SOURCE_PATHS_FOR_NEXT_CHAT.json
└── reports/
    └── final_bundle_certification_closure_report.json

LOCAL_TASKS/LT-06-SANCTUM-E2E-CERTIFICATION/STAGES/STAGE-20-FINAL-BUNDLE-CERTIFICATION-CLOSURE/
├── STAGE_PLAN.md
├── STAGE_REPORT.json
└── EVIDENCE/
    └── final_bundle_certification_evidence.json

REPORTS/
└── stage_20_final_bundle_certification_closure_report.json
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
E:\IMPERIUM_CONTEXT\
```

Do not create zip bundles unless Owner explicitly asks.  
Do not delete or move files.  
Do not modify Git history.  
Do not set `READY_FOR_AGENT=true` unless a separate Owner launch receipt exists and all gates explicitly allow it. Expected result is `READY_FOR_AGENT=false`.

## FINAL BUNDLE MANIFEST

`FINAL_HARDENING_BUNDLE_MANIFEST.json` must include:

```text
bundle_id
task_id
created_utc
git_head
included_stage_reports
included_stage_evidence
source_package_manifest
ownership_matrix
gate_index
schema_baseline
backend_truth_baseline
dashboard_adapter_index
dashboard_truth_contract
sanctum_aggregation_contract
e2e_proof_report
warnings
blockers
unresolved_items
ready_for_owner_review
ready_for_agent
not_production_deployment
```

## STAGE REPORT INDEX

`STAGE_REPORT_INDEX.json` must list S01-S20:

For each stage:
```text
stage_id
stage_title
expected_report_path
report_exists
report_sha256
stage_verdict
warnings_count
blockers_count
evidence_paths
```

If a stage report is missing:
- bundle verdict must not be PASS;
- mark blocker;
- stop before claiming closure.

## EVIDENCE COMPLETENESS REPORT

`EVIDENCE_COMPLETENESS_REPORT.json` must verify:

- 20 stage reports present;
- all required high-level package folders present;
- source package manifest present;
- ownership matrix present;
- gate index present;
- schema baseline present;
- backend truth baseline present;
- no-fake-green report present;
- stale-status report present;
- corridor models present;
- dashboard adapter index present;
- dashboard truth/action contracts present;
- UTF-8/repo purity report present;
- Sanctum aggregation contract present;
- E2E synthetic proof report present;
- final unresolved warning/blocker ledger present.

## WARNING AND BLOCKER LEDGER

`WARNING_AND_BLOCKER_LEDGER.md` must:
- collect warnings/blockers from all stage reports;
- separate blocking vs non-blocking;
- preserve PASS_WITH_WARNINGS items;
- never hide warnings;
- include recommended next actions;
- include Owner decision needed items.

## CERTIFICATION CANDIDATE

`V1_HARDENING_CERTIFICATION_CANDIDATE.json` must include:

```text
certification_id
task_id
created_utc
git_head
stage_count_expected: 20
stage_count_found
all_stage_reports_present
all_json_valid
all_required_evidence_present
e2e_synthetic_proof_passed
warnings
blockers
certification_verdict
ready_for_owner_review
ready_for_agent: false
owner_approval_required: true
```

Expected:
```text
ready_for_owner_review: true
ready_for_agent: false
owner_approval_required: true
```

## READY FOR AGENT VERDICT

`READY_FOR_AGENT_VERDICT.json` must be conservative:

Expected fields:
```text
ready_for_agent: false
reason: "Owner review and explicit launch/acceptance required after hardening bundle."
required_owner_action
warnings
blockers
```

If all stages pass, that does not automatically set ready_for_agent true.

## OWNER_REVIEW_NOTES_RU.md

Allowed Russian Owner-facing file.

Write concise Russian notes:
- что было собрано;
- что доказано;
- какие warnings/blockers остались;
- что Owner должен проверить;
- можно ли считать hardening package готовым к review;
- почему READY_FOR_AGENT всё ещё false до отдельного решения.

## HANDOFF FILES

Create:

### `NEW_CHAT_HANDOFF_SUMMARY.md`
English summary for next Logos-Prime/Speculum/Advisor:
- Git truth;
- task status;
- what was built;
- final bundle paths;
- unresolved items;
- next recommended action.

### `LOGOS_PRIME_CONTINUITY_NOTE.md`
English continuity note:
- remind exact Owner workflow preferences;
- no prompt unless exact trigger;
- table-first;
- no fake green;
- commit all 20 prompts together policy;
- current stage completion state.

### `SOURCE_PATHS_FOR_NEXT_CHAT.json`
Machine-readable list of important paths.

## PASS CRITERIA

Stage PASS only if:
- all S01-S20 reports present and indexed;
- final bundle manifest exists and parses;
- evidence completeness report exists and parses;
- warning/blocker ledger exists;
- certification candidate exists and parses;
- ready-for-agent verdict exists and says false unless Owner launch receipt exists;
- Owner review notes RU exists;
- handoff files exist;
- no unresolved blocker hidden;
- no production organ files modified;
- no writes outside target path.

## STOP CRITERIA

Stop if:
- any prior stage report missing;
- any critical JSON invalid;
- final bundle omits warnings/blockers;
- READY_FOR_AGENT is set true without Owner launch receipt;
- output claims production deployment;
- output deletes/moves evidence;
- output writes outside target path.

## COMMIT POLICY FOR FUTURE EXECUTION

If all 20 stages are later executed and this final bundle is created:
- commit may be performed only if Owner instructed stage execution commit.
- suggested commit message:
  `TASK-20260515: complete foundational organs V1 hardening package`
- print final Git truth.
- no VM2 sync unless Owner explicitly asks.

## FINAL RESPONSE TO OWNER

Use exactly this 4-part Russian form:

1. Step name
2. Full path to final bundle/certification evidence
3. Verdict
4. 3-4 short Russian comment lines for Owner
