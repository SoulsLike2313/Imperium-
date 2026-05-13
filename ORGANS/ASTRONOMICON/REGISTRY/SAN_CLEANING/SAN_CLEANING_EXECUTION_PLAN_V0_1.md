# SAN_CLEANING Execution Plan v0.1

Advisory input file:
`ORGANS/ASTRONOMICON/REGISTRY/ADVISORY_RESPONSES/ADVISORY-RESPONSE-20260513-KIRO-SAN-CLEANING-BACKEND-TRUTH-V0_1.md`

Advisory policy:
- Required input for decomposition and planning.
- Not canon until validated against current repository truth.

## Stage 0 - Entry Cleanup (Current Task)
- Advisory sections used: 1, 2, 11, 12, 15, 16.
- Files expected: `ORGANS/ASTRONOMICON/REGISTRY/SAN_CLEANING/*`, Mechanicus seed READMEs, current state entry report.
- Scripts/checkers expected: `TOOLS/check_san_cleaning_entry_v0_1.py`.
- Pass criteria: approved `ARCHIVE`/`OBSERVED` handling complete; registry seeds present; no unauthorized deletions.
- Risk: accidental broad cleanup or weak deletion evidence.

## Stage 1 - Current Truth Inventory
- Advisory sections used: 1, 2, 3, 11, 13, 14, 16.
- Files expected: inventory report(s), inventory registry snapshots, orphan/unknown candidate lists.
- Scripts/checkers expected: read-only inventory scanner (`inventory_repo_truth_v0_1.py` planned).
- Pass criteria: complete read-only inventory across scripts/files/tools/bundles/reports/warnings/orphans with no deletion.
- Risk: hidden runtime/generated drift misclassified as product source.

## Stage 2 - Folder Taxonomy Normalization
- Advisory sections used: 2, 11, 12, 15.
- Files expected: approved classification manifest, movement plan, zone definitions.
- Scripts/checkers expected: taxonomy classifier checker.
- Pass criteria: zones classified as tracked/local-only/generated/quarantine with no movement before manifest approval.
- Risk: moving active files before owner-approved plan.

## Stage 3 - MECHANICUS Formalization
- Advisory sections used: 6, 7, 10, 15, 16.
- Files expected: `ORGANS/MECHANICUS/ORGAN_CONTRACT.json`, `ORGAN_STATUS.json` update, `SELF_REPORT` baseline, bridge policies.
- Scripts/checkers expected: Mechanicus contract checker and policy validators.
- Pass criteria: formal Mechanicus contract, backend bridge policy, script repair policy, error learning policy documented and checked.
- Risk: ownership ambiguity between organs and support layers.

## Stage 4 - SCRIPTORIUM Under MECHANICUS
- Advisory sections used: 4, 9, 13, 14, 16.
- Files expected: expanded script registry entries with owner/purpose/status/reliability/side effects.
- Scripts/checkers expected: registry builder and completeness checker.
- Pass criteria: full script inventory registered with dashboard-ready data.
- Risk: partial registrations creating fake completeness.

## Stage 5 - ARSENAL Under MECHANICUS
- Advisory sections used: 5, 9, 13, 14, 16.
- Files expected: tool/capability registry with install and platform availability fields.
- Scripts/checkers expected: capability/install verifier for PC/VM2.
- Pass criteria: ARSENAL registry covers tools, capabilities, risks, approvals, and availability checks.
- Risk: false availability assumptions across platforms.

## Stage 6 - Error Registry
- Advisory sections used: 7, 15, 16.
- Files expected: error event registry, reliability history trail, remediation records.
- Scripts/checkers expected: error event recorder and regression fail-fast checkers.
- Pass criteria: failures are captured as learning events with regression linkage.
- Risk: untracked recurring failures reduce reliability growth.

## Stage 7 - Bundle/Artifact Policy
- Advisory sections used: 8, 10, 11, 15.
- Files expected: canonical bundle policy docs, changed_files standard, adapter handling notes.
- Scripts/checkers expected: bundle build/review/apply/commit wrappers.
- Pass criteria: canonical outbox/inbox flow and deletion-capable intake evidence.
- Risk: bundles that cannot represent deletions or receipts.

## Stage 8 - Backend Health Dashboard Data
- Advisory sections used: 3, 9, 13, 14, 16.
- Files expected: metric snapshots and dashboard data artifacts.
- Scripts/checkers expected: metrics collector and dashboard data builders.
- Pass criteria: truth metrics are generated and pass anti-fake-green checks.
- Risk: optimistic metrics not tied to checker truth.

## Stage 9 - Scriptorium/Arsenal/Sanctum Truth Dashboards
- Advisory sections used: 9, 15.
- Files expected: dashboard specs and generated data contracts.
- Scripts/checkers expected: viewer-first launchers and data validators.
- Pass criteria: viewer mode works with truthful data; active buttons only when backend bridges exist.
- Risk: UI actions that claim support without backend capability.

## Stage 10 - Reusable Launchers
- Advisory sections used: 10, 13, 15.
- Files expected: registered launcher scripts and command catalog.
- Scripts/checkers expected: launcher policy and registration validators.
- Pass criteria: replace large chat command blocks with short registered script commands.
- Risk: continued ad hoc execution causing drift and operator errors.

## Stage 11 - Clean Baseline Freeze
- Advisory sections used: 1, 3, 11, 15, 16.
- Files expected: freeze report, baseline receipts, and verified clean-state metadata.
- Scripts/checkers expected: final truth gate checker.
- Pass criteria: checks pass, state recorded, and clean baseline is reviewable.
- Risk: freezing with unresolved warnings treated as green.
