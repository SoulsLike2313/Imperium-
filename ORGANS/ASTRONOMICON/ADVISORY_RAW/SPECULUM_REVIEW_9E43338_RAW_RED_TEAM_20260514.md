# SPECULUM RAW RED-TEAM ADVISORY REGISTRATION — 2026-05-14

- advisory_id: SPECULUM_REVIEW_9E43338_RAW_RED_TEAM_20260514
- source_pdf_path: E:\IMPERIUM_CONTEXT\LOCAL\ADVISORY_INBOX\imperium_red_team_review_9e43338_with_kiro_plan.pdf
- source_pdf_exists: true
- source_status: RAW_RED_TEAM_ADVISORY
- canon_status: NOT_CANON
- reviewed_against_head: 9e43338106219929d0232bb2397e6c63d1fe5765
- relation_to_kiro: Kiro plan remains advisory_not_canon
- red_team_verdict: PROCEED_BUT_SPLIT_PLAN
- vm2_status: DEFERRED_OFFLINE
- extraction_artifact: E:\IMPERIUM\OUTBOX\PC_SERVITOR_BUNDLES\TASK-20260514-SPECULUM-OFFICIO-SEED-V0_1\SPECULUM_PDF_EXTRACT_STAGE02.txt

## Key blockers

- no green after shell error
- no VM2 commit/push
- no commit/push automation yet
- no Sanctum write buttons before backend truth
- no Kiro-as-canon
- response contract gap must be closed
- stale dashboard truth must not show green
- warning flood must be classified

## Evidence map by section/page

- evidence_map_status: EXTRACTED_FROM_CANONICAL_PDF
- evidence_source: Speculum PDF at canonical advisory inbox path

### EVID-01 Review baseline

- evidence_id: EVID-01-BASELINE-9E43338
- source: Speculum PDF
- page_or_section: page 1, section `0. Основание и границы проверки`
- summary: latest visible Git reality is exact SHA `9e43338106219929d0232bb2397e6c63d1fe5765`; handoff ZIP shows `9307...` and commit count `80` as pre-commit context.
- implication_for_imperium: `9e43338` is the review baseline; old handoff HEAD is stale context only.
- status: RAW_RED_TEAM_ADVISORY_NOT_CANON
- related_future_task: TASK-20260514-GIT-TRUTH-FAIL-CLOSED-RECEIPT-V0_1

### EVID-02 Red-team verdict

- evidence_id: EVID-02-PROCEED-BUT-SPLIT
- source: Speculum PDF
- page_or_section: page 1 (`Вердикт документа`) and page 4 (`Kiro San-Cleaning should insert as Foundation Stabilization Arc`)
- summary: review verdict is `PROCEED_BUT_SPLIT_PLAN`.
- implication_for_imperium: continue execution but split Kiro plan into foundation stabilization tasks before deeper corridor expansion.
- status: RAW_RED_TEAM_ADVISORY_NOT_CANON
- related_future_task: TASK-20260514-SERVITOR-RESPONSE-CONTRACT-V0_1

### EVID-03 Kiro advisory status

- evidence_id: EVID-03-KIRO-ADVISORY-NOT-CANON
- source: Speculum PDF
- page_or_section: pages 2, 3, 10
- summary: `KIRO_PLAN_ADVISOR/SAN_CLEAN_PLAN` is explicitly `advisory_not_canon` and must not be treated as approved runtime route.
- implication_for_imperium: Kiro input stays advisory until formalized by Owner/Astronomicon gates.
- status: RAW_RED_TEAM_ADVISORY_NOT_CANON
- related_future_task: TASK-20260514-ASTRONOMICON-KIRO-ADVISORY-NOT-CANON-V0_1

### EVID-04 Fake green blocker

- evidence_id: EVID-04-FAKE-GREEN-UNARY
- source: Speculum PDF
- page_or_section: pages 1, 5, 10
- summary: pattern `unary operator expected` followed by `VM2 EXACT SYNC OK` is explicitly identified as invalid and must be blocked.
- implication_for_imperium: fail-closed receipts are mandatory; no success verdict after shell/stderr/parse failures.
- status: RAW_RED_TEAM_ADVISORY_NOT_CANON
- related_future_task: TASK-20260514-GIT-TRUTH-FAIL-CLOSED-RECEIPT-V0_1

### EVID-05 VM2 rule

- evidence_id: EVID-05-VM2-NO-COMMIT-PUSH
- source: Speculum PDF
- page_or_section: pages 8 and 10
- summary: VM2 must not commit/push; VM2 is bundle-draft contour only.
- implication_for_imperium: keep this task in PC-only execution; current VM2 status remains `DEFERRED_OFFLINE`.
- status: RAW_RED_TEAM_ADVISORY_NOT_CANON
- related_future_task: TASK-20260514-GIT-TRUTH-FAIL-CLOSED-RECEIPT-V0_1

### EVID-06 Officio response contract gap

- evidence_id: EVID-06-OFFICIO-CONTRACT-GAP
- source: Speculum PDF
- page_or_section: pages 2, 4, 7, 9, 10
- summary: no accepted `SERVITOR_RESPONSE_CONTRACT` exists yet; review marks this as blocker for corridor continuity.
- implication_for_imperium: seed/checkable contract in Officio is required before claiming stable stage execution.
- status: RAW_RED_TEAM_ADVISORY_NOT_CANON
- related_future_task: TASK-20260514-SERVITOR-RESPONSE-CONTRACT-V0_1

### EVID-07 Dashboard stale truth risk

- evidence_id: EVID-07-DASHBOARD-STALE-TRUTH
- source: Speculum PDF
- page_or_section: pages 2, 3, 5, 10
- summary: dashboard green must not be shown without `last_checked_at`, exact SHA, source receipt, and stale status.
- implication_for_imperium: stale/current-state model is required to prevent false green visualization.
- status: RAW_RED_TEAM_ADVISORY_NOT_CANON
- related_future_task: TASK-20260514-SANCTUM-BACKEND-TRUTH-MODEL-V0_1

### EVID-08 Warning flood risk

- evidence_id: EVID-08-WARNING-FLOOD-CLASSIFY
- source: Speculum PDF
- page_or_section: pages 4, 7, 10
- summary: warning flood must be classified into legacy/new/blocker classes, never hidden under green.
- implication_for_imperium: warning baseline classifier becomes prerequisite for honest pass/warn reporting.
- status: RAW_RED_TEAM_ADVISORY_NOT_CANON
- related_future_task: TASK-20260514-WARNING-BASELINE-CLASSIFICATION-V0_1

### EVID-09 Automation boundary

- evidence_id: EVID-09-AUTOMATION-BOUNDARY
- source: Speculum PDF
- page_or_section: pages 5, 8, 10
- summary: commit/push automation is not allowed yet; read-only and fail-closed gates must be built first.
- implication_for_imperium: retain manual PC commit/push gate and postpone write launchers/buttons.
- status: RAW_RED_TEAM_ADVISORY_NOT_CANON
- related_future_task: TASK-20260514-LAUNCHER-READ-ONLY-GATES-FIRST-V0_1

### EVID-10 UTF-8/mojibake risk

- evidence_id: EVID-10-UTF8-MOJIBAKE
- source: Speculum PDF
- page_or_section: pages 2, 7, 9, 10
- summary: Owner-facing artifacts must remain readable; UTF-8/mojibake risk is explicitly called out.
- implication_for_imperium: introduce encoding gate and keep explicit `ENCODING_GATE_PENDING` warning until enforced.
- status: RAW_RED_TEAM_ADVISORY_NOT_CANON
- related_future_task: TASK-20260514-OWNER-FACING-UTF8-MOJIBAKE-GATE-V0_1

## Execution note

This registration records raw advisory intake only. It does not approve execution, canonization, readiness, or green claims.
