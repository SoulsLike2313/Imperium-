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

# STAGE 02 PROMPT — Ownership Matrix Freeze and Boundary Lint

## ROLE

PC Servitor for IMPERIUM.

## MODE

Cold executor.  
Boundary-focused.  
No fake green.  
No implementation beyond ownership contracts and boundary linting.  
No dashboard building.  
No organ mutation outside hardening package.  
No VM2 sync.

## TASK

`TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING`

## LOCAL TASK

`LT-01-RECONCILIATION-SCHEMAS-CONTRACTS`

## STAGE

`STAGE-02-OWNERSHIP-MATRIX-FREEZE-BOUNDARY-LINT`

## DEPENDS ON

`STAGE-01-SOURCE-INTEGRITY-OWNER-MATRIX-FREEZE`

Required Stage 01 evidence:
```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/SOURCE_PACKAGE/HARDENING_SOURCE_PACKAGE_MANIFEST.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/SOURCE_PACKAGE/OWNER_MATRIX_FREEZE.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/LOCAL_TASKS/LT-01-RECONCILIATION-SCHEMAS-CONTRACTS/STAGES/STAGE-01-SOURCE-INTEGRITY-OWNER-MATRIX-FREEZE/STAGE_REPORT.json
```

## STAGE GOAL

Freeze the foundational organs V1 ownership model into the future hardening package and create a boundary-lint artifact that future stages must obey.

This stage prevents ownership collisions:
- Astronomicon vs Administratum;
- Administratum vs Doctrinarium;
- Officio Agentis vs Administratum;
- Officio Agentis vs Doctrinarium;
- Doctrinarium vs future Inquisition;
- Sanctum vs organ dashboards;
- Mechanicus/scripts/tools vs organ-owned truth.

## WHY THIS STAGE EXISTS

Speculum blocked direct hardening execution until a machine-readable ownership boundary contract exists. Without this stage, future stages may accidentally make:
- Astronomicon write execution truth;
- Administratum decide law/canon;
- Officio assign agents autonomously;
- Doctrinarium own task scope;
- Sanctum become source of truth;
- scripts mutate organs without declared ownership.

This stage converts the reconciliation ownership matrix into a hardening-local contract and produces a lint report.

## SOURCE FILES TO READ

Read:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/FOUNDATIONAL_ORGANS_V1_OWNERSHIP_MATRIX.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/FOUNDATIONAL_ORGANS_V1_OWNERSHIP_MATRIX.md
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/RECONCILIATION_TABLE.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/V1_KNOWN_FAILURES_AND_PREVENTIONS.md
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/V1_20_STAGE_EXECUTION_PLAYBOOK.md
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/SOURCE_PACKAGE/HARDENING_SOURCE_PACKAGE_MANIFEST.json
```

## ALLOWED WRITE PATHS

Write only under:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/
```

Recommended outputs:

```text
OWNERSHIP/
├── FOUNDATIONAL_ORGANS_V1_OWNERSHIP_FREEZE.json
├── FOUNDATIONAL_ORGANS_V1_OWNERSHIP_FREEZE.md
├── OWNERSHIP_BOUNDARY_LINT_RULES.json
├── OWNERSHIP_BOUNDARY_LINT_REPORT.json
└── OWNERSHIP_COLLISION_REGISTER.md

LOCAL_TASKS/LT-01-RECONCILIATION-SCHEMAS-CONTRACTS/STAGES/STAGE-02-OWNERSHIP-MATRIX-FREEZE-BOUNDARY-LINT/
├── STAGE_PLAN.md
├── STAGE_REPORT.json
└── EVIDENCE/
    ├── ownership_freeze_evidence.json
    └── ownership_boundary_lint_evidence.json

REPORTS/
└── stage_02_ownership_matrix_freeze_boundary_lint_report.json
```

## FORBIDDEN PATHS

Do not modify:
```text
ORGANS/DOCTRINARIUM/
ORGANS/ADMINISTRATUM/
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1/
ORGANS/OFFICIO_AGENTIS/
SANCTUM/
scripts/
TOOLS/
```

Do not create actual checker scripts in this stage unless already explicitly approved by Owner. This stage creates lint rules and reports, not implementation code.

## REQUIRED OWNERSHIP DECISIONS TO ENCODE

Encode at minimum:

| Truth category | Source of truth owner |
|---|---|
| task future memory | Astronomicon |
| task scope | Astronomicon |
| stage topology | Astronomicon |
| planning/registration workflow | Astronomicon |
| execution lifecycle | Administratum |
| work packet | Administratum |
| route sheet | Administratum |
| stage completion truth | Administratum |
| final bundle | Administratum |
| continuity pack | Administratum |
| role contracts | Officio Agentis |
| mode contracts | Officio Agentis |
| response contracts | Officio Agentis |
| agent role/read proof | Officio Agentis |
| law registry | Doctrinarium |
| doctrine registry | Doctrinarium |
| law/canon acceptance | Doctrinarium + Owner gate |
| organ health gate | Doctrinarium |
| task-start gate | Doctrinarium |
| violation records | Doctrinarium |
| disabled Inquisition hook | Doctrinarium, explicitly disabled |
| dashboard rendering | each organ dashboard / Sanctum render layer |
| dashboard data adapter | organ-owned adapter |
| dashboard action receipt | action owner organ |
| Sanctum aggregation | Sanctum read-only aggregation |
| source package manifest | Astronomicon task draft package |
| evidence schemas | shared contract, with owner field |
| receipt schemas | shared contract, with owner field |
| Git truth | Administratum operational truth |
| repo purity | Administratum / Mechanicus-support pattern |

## REQUIRED JSON STRUCTURE

`FOUNDATIONAL_ORGANS_V1_OWNERSHIP_FREEZE.json` must include:
- `task_id`
- `stage_id`
- `created_utc`
- `source_reconciliation_package`
- `ownership_items[]`

Each ownership item:
- `truth_category`
- `source_of_truth_owner`
- `may_read[]`
- `may_write[]`
- `must_not_decide[]`
- `required_receipt`
- `dashboard_display_allowed`
- `sanctum_display_allowed`
- `notes`

`OWNERSHIP_BOUNDARY_LINT_RULES.json` must include:
- `rules[]`

Each rule:
- `rule_id`
- `description`
- `blocked_pattern`
- `required_owner`
- `allowed_writers[]`
- `stop_if_violated`
- `example_violation`
- `expected_fix`

`OWNERSHIP_BOUNDARY_LINT_REPORT.json` must include:
- `verdict`
- `rules_checked`
- `collisions_detected`
- `warnings`
- `blockers`
- `evidence_paths`

## REQUIRED LINT CHECKS

The lint report must check for at least these collision patterns conceptually:

1. Astronomicon writing execution state.
2. Administratum writing stage topology.
3. Administratum deciding canon/law acceptance.
4. Officio creating execution lifecycle truth.
5. Officio overriding Doctrinarium laws.
6. Doctrinarium writing task scope/stage map.
7. Doctrinarium claiming active Inquisition audit.
8. Sanctum writing canonical organ truth.
9. Dashboard writing source-of-truth state directly.
10. Any script/tool mutating an organ without owner/receipt declaration.

This may be a manual/static report in this stage. Implementation of automated lint can come later, but the lint rules must be machine-readable enough for later scripts.

## PASS CRITERIA

Stage PASS only if:
- Stage 01 evidence exists and parses.
- Ownership freeze JSON exists and parses.
- Ownership lint rules JSON exists and parses.
- Ownership lint report JSON exists and parses.
- All required truth categories have exactly one source-of-truth owner.
- Sanctum is explicitly read-only aggregator.
- Inquisition hook is explicitly disabled/not audit.
- No output grants hardening execution readiness.
- No unrelated files changed.

## STOP CRITERIA

Stop if:
- Stage 01 missing or invalid.
- Ownership source files missing.
- Any required truth category has no owner.
- Any required truth category has multiple owners without clear read/write distinction.
- Output implies dashboard/Sanctum may become canonical truth.
- Output implies Inquisition is active.
- Output modifies existing organs.

## FINAL RESPONSE TO OWNER

Use exactly this 4-part Russian form:

1. Step name
2. Full path to stage evidence
3. Verdict
4. 3-4 short Russian comment lines for Owner
