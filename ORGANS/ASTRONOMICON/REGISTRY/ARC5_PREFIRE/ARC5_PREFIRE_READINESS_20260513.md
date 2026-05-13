# ARC 5 PREFIRE READINESS — IMPERIUM SELF-BUILD PREPARATION

- status: PREFIRE_REGISTERED
- date_utc: 2026-05-13T09:28:57Z
- owner: Astronomicon
- purpose: readiness map before Arc 5 self-build launch
- current_head_at_creation: 71279657d64e1023acf47d923e20b217daabdd89
- commit_count_at_creation: 63
- latest_at_creation: TASK-20260513: register Sanctum experimental status and Kiro visual audit

## 1. Meaning

Arc 5 is not just another implementation step.

Arc 5 is the first serious test of whether IMPERIUM can help build itself through its own systems:

- structured Owner input;
- GENERAL_TASK registration;
- TASK decomposition;
- review/advisory cycle;
- task modernization;
- stage map creation;
- stage review and approval;
- READY_FOR_AGENT gate;
- Servitor execution;
- receipts and partial progress reports;
- Administratum continuation ACK;
- Inquisition cleanup/filtering;
- Sanctum dashboard visibility;
- no-fake-green discipline.

This prefire file freezes the preparation frame before Arc 5.

## 2. Current accepted truth

Current accepted Git truth before this prefire commit:

- repo: https://github.com/SoulsLike2313/Imperium-
- exact_head_before_prefire: 71279657d64e1023acf47d923e20b217daabdd89
- commit_count_before_prefire: 63
- latest_before_prefire: TASK-20260513: register Sanctum experimental status and Kiro visual audit

Current accepted Sanctum baseline:

- SANCTUM/sanctum_v0_29_qt.py
- status: super experimental transitional operator dashboard
- not final UI
- not stable product shell yet

Rejected Sanctum lines:

- Sanctum EE
- v0.30EE
- R1
- R2
- standalone generic Registration Corridor HTML preview as accepted Sanctum UI

## 3. Arc 5 high-level goal

Prepare the system so the first self-build organ task can be launched cleanly.

Target first self-build direction:

- build Inquisition as a real organ;
- give it contract/status/self-report/checkers;
- give it a dashboard;
- later embed that dashboard into Sanctum;
- make it useful for cleanup, duplicate detection, temporary file control, TTL policy, rejected experiment quarantine, warning-budget enforcement, and no-fake-green pressure.

## 4. Why Arc 5 is not ready to launch blindly

Known risks:

1. The first 4 guide-organs are not yet fully unified into a mature operational form.
2. Sanctum is useful but still experimental and not yet button-test trustworthy.
3. The visual factory is not yet implemented; only advisory direction exists.
4. Advisory ideas are preserved, but promotion into TASK_ID structures is not yet fully mechanized.
5. READY_FOR_AGENT is correctly blocked for the Inquisition candidate until review, modernization, stage approval, and Owner approval.
6. Long Servitor work-session continuation is not yet implemented.
7. Inquisition cleanup must be quarantine-first, not delete-first.
8. Current-state continuity may still have stale entrypoints and must be checked before self-build.

## 5. P0 blockers before Arc 5 self-build

P0 means Arc 5 should not start without resolving or explicitly accepting risk.

- P0-1: Kiro / Speculum style Act 5 readiness audit must be reviewed.
- P0-2: First 4 guide-organs need a unified minimal operational form.
- P0-3: Sanctum must show the self-build corridor clearly enough for Owner trust.
- P0-4: READY_FOR_AGENT semantics must remain strict and machine-checkable.
- P0-5: Advisory buffer promotion path must exist.
- P0-6: Inquisition v0.1 contract must define safe cleanup, quarantine, TTL, and non-goals.
- P0-7: Servitor partial progress report and Administratum ACK/continue path must be designed.
- P0-8: No-fake-green gates must define which warnings are allowed and which become blockers.

## 6. P1 preparation work

- Create ASSETS / DESIGN_SYSTEM / UI_LAB foundation from Kiro visual audit.
- Add accepted/rejected visual screenshots and manifests.
- Define Sanctum dashboard module boundaries.
- Define action registry for testable buttons.
- Define organ dashboard embedding rules.
- Define first Inquisition dashboard panel.
- Add Act 5 readiness checker concept.
- Refresh current-state entrypoints after major commits.

## 7. P2 preparation work

- Mature Playwright or equivalent UI test path.
- Expand visual regression / golden screenshots.
- Add stronger receipt verification later.
- Improve command gateway enforcement.
- Reduce warning flood and classify warnings by budget.
- Add richer Sanctum design system and component lab.

## 8. First four guide-organs

The intended first four guide-organs for Arc 5 preparation are:

1. Doctrinarium
   - doctrine, law, canon gates, no-fake-green doctrine.
2. Administratum
   - memory, archive, Git/local orientation, task continuity, work-session ACK.
3. Officio Agentis
   - agent role contracts, response contracts, authority limits, execution permissions.
4. Astronomicon
   - plans, advisory buffer, GENERAL_TASK/TASK/STAGE registration corridor, future direction.

Target unified organ form:

ORGANS/<ORGAN>/
  README.md
  ORGAN_CONTRACT.json
  ORGAN_STATUS.json
  ORGAN_SELF_REPORT.json
  PORTS/
  SCHEMAS/
  SCRIPTS/
  CHECKS/
  RECEIPTS/
  REPORTS/
  DASHBOARD/ or UTILITY/
  TESTS/

## 9. Advisory buffer rule

Astronomicon owns the advisory / idea buffer.

Purpose:

- preserve Kiro/Speculum/Logos reports;
- preserve Owner impulses and rough plans;
- preserve visual/design research;
- preserve architecture proposals;
- preserve rejected experiments and lessons;
- prevent useful ideas from disappearing before formal TASK_ID conversion.

Advisory buffer is not execution authority.

Target advisory lifecycle:

RAW_ADVISORY
-> REVIEWED
-> OWNER_MARKED_USEFUL
-> PROMOTION_CANDIDATE
-> PROMOTED_TO_GENERAL_TASK / PROMOTED_TO_TASK / REJECTED / ARCHIVED

## 10. Sanctum rule before Arc 5

Sanctum must become a serious dashboard, but not through another uncontrolled rewrite.

Accepted direction:

SANCTUM = dashboard/operator shell
RUNTIME = Python control core
ACTIONS = gated registered operations
ORGANS = dashboard modules / panels
RECEIPTS = proof layer
TESTS = button/action trust layer

Forbidden before explicit Owner approval:

- reviving EE/R1/R2;
- replacing working behavior with generic visual rewrite;
- calling empty HTML pages accepted Sanctum UI;
- touching runtime logic for visual-only experiments;
- adding dangerous buttons without receipts/checks;
- claiming a button works without a test or clear execution path.

## 11. Visual factory rule

Future UI work should read these zones before touching Sanctum runtime:

- ASSETS
- SANCTUM/DESIGN_SYSTEM
- SANCTUM/UI_LAB

Target visual workflow:

reference
-> token
-> component lab
-> screenshot
-> Owner review
-> integration
-> test
-> receipt

The goal is to stop large visual jumps and stop UI changes from breaking backend/runtime behavior.

## 12. Inquisition first self-build target

Inquisition v0.1 should start as a strict cleanup/filter organ.

Initial responsibilities:

- duplicate detection;
- temporary/generated artifact classification;
- stale bundle/rejected experiment detection;
- TTL zone policy;
- public/private boundary pressure;
- warning budget pressure;
- no-fake-green pressure;
- quarantine recommendations.

Hard rule:

Inquisition v0.1 must be quarantine-first and report-first.
It must not delete important files automatically.

## 13. Long Servitor session target

Arc 5 should prepare a model where a Servitor can continue long work without repeated manual restart.

Target flow:

WORK_SESSION
-> STAGE_PROGRESS_REPORT
-> ADMINISTRATUM_ACK
-> CONTINUE_ALLOWED / STOP_OWNER_REQUIRED
-> PARTIAL_RECEIPT
-> CONTINUE_EXECUTION

Servitor must not self-authorize continuation.
Administratum ACK is an operational continuity mechanism, not canon authority.

## 14. Required external review

Before Arc 5 launch, a hard Kiro/Speculum review should produce:

- Act 5 readiness verdict;
- stale truth map;
- task registration architecture review;
- first 4 organs readiness matrix;
- advisory buffer governance;
- Sanctum target architecture;
- visual factory integration plan;
- Servitor long-session model;
- Inquisition v0.1 contract/stage map;
- mandatory gate list;
- exact first safe steps.

## 15. Current prefire verdict

Arc 5 is not ready for blind launch.

Arc 5 may proceed only after the system has:

- reviewed the Kiro/Speculum readiness audit;
- converted useful findings into concrete files/tasks/stages;
- clarified first 4 organ readiness;
- defined Inquisition v0.1 non-goals and quarantine policy;
- prepared Sanctum visibility enough for Owner trust;
- preserved no-fake-green semantics.

## 16. Minimal safe next steps

1. Receive and store Kiro Act 5 readiness audit in Astronomicon advisory buffer.
2. Promote selected audit findings into formal preparation TASK candidates.
3. Build only the smallest safe pre-Arc 5 preparation slice before launching self-build.

## 17. Final rule

No self-build execution should start from vibes.

Arc 5 must start from:

- exact Git truth;
- explicit task registration;
- visible stage map;
- strict READY_FOR_AGENT gate;
- clear Owner approval;
- receipt-backed Servitor execution;
- quarantine-first Inquisition logic;
- no-fake-green review.
