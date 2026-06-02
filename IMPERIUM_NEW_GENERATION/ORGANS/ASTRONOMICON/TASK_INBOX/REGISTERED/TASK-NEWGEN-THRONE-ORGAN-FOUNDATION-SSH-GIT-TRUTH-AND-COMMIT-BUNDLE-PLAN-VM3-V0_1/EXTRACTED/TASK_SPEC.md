# Task Spec

## TASK_ID

`TASK-NEWGEN-THRONE-ORGAN-FOUNDATION-SSH-GIT-TRUTH-AND-COMMIT-BUNDLE-PLAN-VM3-V0_1`

## Mission

Birth the `THRONE` organ foundation in IMPERIUM New Generation as a local SSH-only, script-first agent/organ responsible for git/admission truth, commit indexing, task/commit grouping, and evidence bundle export.

This task must define Throne as an organ, not merely a loose git script. It must prepare the future path toward Custodes, but Custodes itself must not be implemented here.

## Strategic intent

GitHub web commit URLs can return 404 or be externally unavailable. That must never produce fake green or block review when local git truth is available. Throne becomes the local seal of git truth: commit objects, commit history, task groupings, closure receipts, and exportable evidence bundles.

## Current operating model before Custodes

1. Servitor completes a non-BLOCK task and commits/pushes to GitHub.
2. Throne syncs/fetches the accepted branch.
3. Throne proves the commit exists locally by git object hash.
4. Throne exports latest or selected commit evidence bundle.
5. Owner gives the bundle to Logos-Prime, Inquisitor, or Speculum.
6. GitHub URL success is useful but optional; Throne evidence bundle is authoritative if hashes and git object checks pass.

## Future operating model after Custodes

1. Commit candidate enters a supervision/admission zone.
2. Custodes applies strict admission criteria and can mark candidate dirty.
3. Inquisition, Speculum, and Logos-Prime explain the issue to Owner.
4. System learns to demand corrected output from Servitor.
5. Only admitted candidates become accepted truth.

Do not implement Custodes now. Define the handoff and future contracts only.

## Required deliverables in repository

Create or update a Throne organ area, preferably:

`IMPERIUM_NEW_GENERATION/ORGANS/THRONE/`

Required content:

1. `ORGAN_MANIFEST.json`
2. `README.md`
3. `DOCTRINE/THRONE_DOCTRINE.md`
4. `POLICIES/SSH_ONLY_LOCAL_NETWORK_POLICY.md`
5. `CONTRACTS/THRONE_GIT_TRUTH_CONTRACT.md`
6. `CONTRACTS/COMMIT_INDEX_CONTRACT.md`
7. `CONTRACTS/COMMIT_EVIDENCE_BUNDLE_CONTRACT.md`
8. `CONTRACTS/PRE_CUSTODES_FLOW.md`
9. `CONTRACTS/FUTURE_CUSTODES_ADMISSION_HANDOFF.md`
10. `SCHEMAS/commit_index.schema.json`
11. `SCHEMAS/commit_evidence_bundle_manifest.schema.json`
12. `SCHEMAS/task_commit_group.schema.json`
13. `SCHEMAS/admission_truth_record.schema.json`
14. `SKILLS/COMMIT_BUNDLE_SKILL/SKILL_MANIFEST.json`
15. `SKILLS/COMMIT_BUNDLE_SKILL/README.md`
16. `TUI/THRONE_TUI_V0_1_SPEC.md`
17. `CONFIG/throne_contour_profile.template.json`
18. `REPORTS/TASK-NEWGEN-THRONE-ORGAN-FOUNDATION-SSH-GIT-TRUTH-AND-COMMIT-BUNDLE-PLAN-VM3-V0_1/FINAL_REPORT.md`
19. Machine receipts under `REPORTS/TASK-NEWGEN-THRONE-ORGAN-FOUNDATION-SSH-GIT-TRUTH-AND-COMMIT-BUNDLE-PLAN-VM3-V0_1/`

Optional but preferred if safe and fast:
- A read-only prototype script that can index recent commits from the local repo and write a sample commit index receipt.
- The prototype must not require the laptop to exist yet.

## SSH and contour rules

Primary execution contour is VM3.

If PC access is needed, Servitor may use SSH to PC for focused read/probe actions or to fetch known current state. This is allowed operational freedom, but all SSH use must be recorded in a receipt.

Do not configure the laptop/Throne machine in this task unless the required access details are already present and safe. If not available, write the exact future commands/contracts instead.

## Required next-task candidates

Register these as next-task candidates, without implementing them here:

1. `TASK-NEWGEN-THRONE-SSH-GIT-MIRROR-AND-COMMIT-BUNDLE-SKILL-LAPTOP-V0_1`
2. `TASK-NEWGEN-SERVITOR-CODEX-CLI-BRIDGE-PC-ASTRONOMICON-START-TASK-HANDOFF-V0_1`
3. `TASK-NEWGEN-MATRIX-SPINE-HARD-MODE-STEP-VS-GLOBAL-CAPS-PC-V0_1`
4. `TASK-NEWGEN-DECLARATION-OF-ADMISSION-CAMPAIGN-PC-V0_1`
5. `TASK-NEWGEN-CUSTODES-ADMISSION-GUARDIAN-FOUNDATION-PC-V0_1`

## Required final answer contract

Use the strict Owner final response form:

1. Step name
2. Step verdict
3. Commit links list with short labels for every commit created in this task
4. Exactly 3-4 short Russian Owner comments

No long final prose. Put all evidence in repo reports.
