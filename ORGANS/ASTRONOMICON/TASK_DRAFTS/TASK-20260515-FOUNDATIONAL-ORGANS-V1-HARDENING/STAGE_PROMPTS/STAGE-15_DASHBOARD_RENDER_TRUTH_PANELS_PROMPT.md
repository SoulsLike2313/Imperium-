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

# STAGE 15 PROMPT — Dashboard Render Truth Panels

## ROLE

PC Servitor for IMPERIUM.

## MODE

Cold executor.  
Dashboard truth panel design and fixture stage.  
No fake green.  
Minimal UI shell allowed only as static proof if kept inside hardening package.  
No production dashboard deployment.  
No Sanctum production wiring.  
No VM2 sync.  
No broad cleanup.

## TASK

`TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING`

## LOCAL TASK

`LT-05-DASHBOARD-UI-LAYER`

## STAGE

`STAGE-15-DASHBOARD-RENDER-TRUTH-PANELS`

## DEPENDS ON

- `STAGE-13-DASHBOARD-ADAPTER-CONTRACT-SET-A`
- `STAGE-14-DASHBOARD-ADAPTER-CONTRACT-SET-B`

Required evidence:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/DASHBOARD_DATA/ADAPTER_CONTRACTS/FOUR_ORGAN_DASHBOARD_ADAPTER_INDEX.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/DASHBOARD_DATA/ADAPTER_CONTRACTS/reports/dashboard_adapter_contract_set_b_report.json
```

## STAGE GOAL

Create the dashboard truth panel rendering contract and stage-local proof fixtures for all four organ dashboards.

This stage defines how UI panels must display truth from dashboard adapters:
- status;
- metrics;
- evidence links;
- freshness;
- warnings;
- blockers;
- source reports;
- disabled actions;
- EN/RU labels;
- visual state semantics.

This stage must not build final production dashboards. It prepares the render contract and safe UI proof inside the hardening package.

## WHY THIS STAGE EXISTS

Owner wants dashboard = 100% truth + beauty. Speculum warned that dashboard beauty can hide blockers, stale reports, mock data, or non-working buttons.

Before building actual organ dashboards, the system needs render truth rules:
- what a green status needs;
- how stale appears;
- how blockers appear;
- how warnings appear;
- how evidence links appear;
- how bilingual labels are separated from canonical data;
- how animations communicate state rather than hide truth.

## SOURCE FILES TO READ

Read:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/DASHBOARD_DATA/ADAPTER_CONTRACTS/FOUR_ORGAN_DASHBOARD_ADAPTER_INDEX.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/DASHBOARD_DATA/ADAPTER_CONTRACTS/dashboard_adapter_common_contract.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-DEFINITION-V0_1/DASHBOARD_TRUTH_AND_BEAUTY_DOCTRINE_V0_1.md
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-DEFINITION-V0_1/SANCTUM_INFINITY_GAUNTLET_INTEGRATION_DRAFT.md
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/CHECKS/NO_FAKE_GREEN/no_fake_green_rules.json
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/CHECKS/STALE_STATUS/stale_status_rules.json
```

## ALLOWED WRITE PATHS

Write only under:

```text
ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING/
```

Recommended outputs:

```text
DASHBOARD_UI/
├── RENDER_TRUTH/
│   ├── dashboard_render_truth_contract.md
│   ├── dashboard_render_truth_contract.json
│   ├── dashboard_visual_state_semantics.json
│   ├── dashboard_i18n_contract.json
│   ├── dashboard_accessibility_and_density_notes.md
│   ├── dashboard_animation_budget.md
│   ├── fixtures/
│   │   ├── render_green_with_evidence_sample.json
│   │   ├── render_warning_with_warnings_sample.json
│   │   ├── render_blocked_with_blockers_sample.json
│   │   ├── render_stale_source_sample.json
│   │   ├── render_unknown_freshness_sample.json
│   │   ├── render_disabled_action_sample.json
│   │   └── render_bilingual_labels_sample.json
│   ├── proof_static_panel/
│   │   ├── README.md
│   │   ├── index.html
│   │   ├── dashboard_truth_demo_data.json
│   │   └── i18n/
│   │       ├── en.json
│   │       └── ru.json
│   └── reports/
│       └── dashboard_render_truth_panels_report.json
LOCAL_TASKS/LT-05-DASHBOARD-UI-LAYER/STAGES/STAGE-15-DASHBOARD-RENDER-TRUTH-PANELS/
├── STAGE_PLAN.md
├── STAGE_REPORT.json
└── EVIDENCE/
    └── dashboard_render_truth_panels_evidence.json
REPORTS/
└── stage_15_dashboard_render_truth_panels_report.json
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

Do not modify existing dashboards.  
Do not deploy the static proof as production UI.  
Do not add production buttons.  
Do not use mock data in any production truth panel.  
Stage-local proof demo data is allowed only if marked fixture/demo.

## RENDER TRUTH CONTRACT

`dashboard_render_truth_contract.json` must define:

```text
render_contract_id
created_utc
source_adapter_index
truth_binding_required: true
mock_data_in_truth_panels_allowed: false
green_requires_evidence: true
stale_can_render_green: false
unknown_can_render_green: false
warnings_visible_required: true
blockers_visible_required: true
source_report_link_required: true
evidence_link_required: true
i18n_required: true
canonical_state_language: ENGLISH
ui_languages_required: [en, ru]
animation_must_not_hide_truth: true
```

## VISUAL STATE SEMANTICS

Create `dashboard_visual_state_semantics.json` with status-to-visual mapping:

```text
PASS / fresh / evidence present -> green or organ-approved success style
PASS_WITH_WARNINGS -> amber-green or amber warning style with visible warning count
FAIL -> red failure style
BLOCKED -> red/severe blocker style
UNKNOWN -> gray/amber unknown style
STALE -> amber/red stale style, never green
NOT_APPLICABLE -> neutral style with reason
DISABLED -> gray disabled style with disabled reason
```

Stage visual semantics:
```text
completed -> dim glow, but only if Admin receipt exists
active -> active pulse, but only if Admin/route state says active
future -> white-platinum slow stellar glow
blocked -> severe red/amber contour with reason/evidence
waiting_evidence -> cold/subdued missing-evidence marker
```

## I18N CONTRACT

`dashboard_i18n_contract.json` must define:
- canonical state keys remain English;
- UI labels come from `i18n/en.json` and `i18n/ru.json`;
- Russian may appear only in UI label files and Owner-facing notes;
- missing translation must show fallback with warning, not break state;
- i18n cannot change status semantics.

## STATIC PROOF PANEL

A small static proof panel is allowed inside:

```text
DASHBOARD_UI/RENDER_TRUTH/proof_static_panel/
```

It must:
- be clearly marked `NOT_PRODUCTION_DASHBOARD`;
- read only local demo JSON inside the same proof folder;
- show examples of PASS with evidence, PASS_WITH_WARNINGS, BLOCKED, STALE, DISABLED;
- include EN/RU label files;
- not call scripts;
- not mutate files;
- not claim real organ state;
- not be connected to Sanctum.

If creating HTML is too risky, create only `README.md` and fixtures. But if created, keep it simple and safe.

## ANIMATION BUDGET

`dashboard_animation_budget.md` must include:
- animations communicate state;
- no animation hides status labels, evidence links, warning counts, blocker reasons;
- CSS-only for V1 where possible;
- no heavy WebGL/particle systems in V1;
- 60 FPS target where feasible;
- performance degradation must reduce motion, not truth.

## PASS CRITERIA

Stage PASS only if:
- render truth contract exists and parses;
- visual state semantics exist and parse;
- i18n contract exists and parses;
- fixtures exist and parse;
- static proof panel, if created, is explicitly not production;
- stale/unknown cannot render green;
- blockers and warnings must be visible;
- stage completed visual requires Admin receipt;
- no production dashboard files modified.

## STOP CRITERIA

Stop if:
- dashboard adapter index missing;
- render contract allows mock truth data;
- stale/unknown can render green;
- warning/blocker can be hidden;
- i18n pollutes canonical state;
- static proof panel calls scripts or mutates files;
- files are written outside target path;
- existing dashboards are modified.

## FINAL RESPONSE TO OWNER

Use exactly this 4-part Russian form:

1. Step name
2. Full path to stage evidence
3. Verdict
4. 3-4 short Russian comment lines for Owner
