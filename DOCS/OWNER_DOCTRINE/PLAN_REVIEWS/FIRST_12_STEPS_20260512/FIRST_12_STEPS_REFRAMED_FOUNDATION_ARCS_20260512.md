# FIRST 12 STEPS — Reframed as Foundation Arcs

Status: active planning update  
Source point before this file: `142d4bdf0c00c6d98b320d3e16047b3f4b7ce05a`  
Purpose: preserve the original 12-step direction, but reframe execution around dependency-safe foundation arcs.

This file does not replace Owner doctrine.
This file does not make Kiro advisory canon by itself.
This file is a Logos-Prime synthesis after:
- Doctrinarium preflight v0.1;
- Administratum route / UTF-8 / Git truth fix;
- Kiro external research preservation;
- Officio Agentis Servitor response contract;
- FIRST_12_STEPS UTF-8 normalization;
- Logos-Speculum hard red-team review.

No fake green.

---

## 1. Current position

The old 12-step plan remains valid as direction, but it should not be executed as a simple linear checklist.

Current reality:

- Manual VM2 → PC review → commit/push → VM2 sync loop is working.
- PC-driven VM2 sync is working through `127.0.0.1:2223`.
- Git truth now uses exact SHA tree URLs.
- Administratum route truth exists.
- Doctrinarium preflight v0.1 exists.
- Officio response contract exists.
- FIRST_12_STEPS files are normalized to UTF-8.
- Kiro external research is preserved as advisory input.
- Sanctum exists as early UI/HUD work, but must not become source of truth.

Main gap:

The system still lacks the contract spine required to run a real organ-guided task cycle.

Missing or incomplete core contracts:

- TASK schema
- STAGE schema
- RUN schema
- BUNDLE_MANIFEST schema
- unified RECEIPT schema
- GIT_TRUTH schema
- ROUTE_TRUTH schema validator
- STALE_STATUS model
- WARNING_BASELINE model
- PC bundle verifier

---

## 2. Main conclusion

We should not rush into Sanctum buttons, graph UI, automatic orchestration, or a large “all organs operational” effort.

The next phase should formalize the manual workflow that already works.

Target:

Owner goal  
→ registered task  
→ stage map  
→ run identity  
→ VM2 worker bundle  
→ PC verifier  
→ receipts  
→ commit/push  
→ VM2 sync  
→ Owner-readable summary

---

## 3. Foundation Arc 1 — Contract Spine

Priority: highest.

Goal:

Make a task a real object, not just a prompt in chat.

Required artifacts:

- `schemas/task.schema.json`
- `schemas/stage.schema.json`
- `schemas/run.schema.json`
- `schemas/stage_pass_criteria.schema.json`
- `DOCS/TASK_STAGE_RUN_CONTRACT_V0_1.md`
- minimal valid and invalid fixtures
- small validator script

Acceptance criteria:

- `TASK_ID`, `STAGE_ID`, and `RUN_ID` are defined.
- A task can have stages.
- A stage has dependencies, allowed paths, forbidden paths, pass criteria, and owner gate flags.
- A run records contour, commands, git truth before/after, outputs, receipts, warnings, blockers, and verdict.
- No automatic execution is introduced.
- No Sanctum button depends on this yet.

Why this comes first:

Astronomicon cannot produce meaningful stage maps without TASK/STAGE/RUN contracts.
Administratum cannot register tasks cleanly without a task schema.
VM2 bundles cannot prove what stage/run they belong to without run identity.

---

## 4. Foundation Arc 2 — Bundle / Receipt / Provenance Spine

Priority: highest.

Goal:

Make VM2 worker bundles mechanically reviewable by PC.

Required artifacts:

- `schemas/bundle_manifest.schema.json`
- `schemas/receipt.schema.json`
- `schemas/git_truth.schema.json`
- `schemas/route_truth.schema.json`
- `DOCS/BUNDLE_AND_RECEIPT_CONTRACT_V0_1.md`
- `TOOLS/verify_worker_bundle.py` or equivalent existing convention
- sha256 verification rules
- scope verification rules

Acceptance criteria:

- Every worker bundle declares:
  - task id;
  - stage id;
  - run id;
  - builder;
  - source git truth;
  - target git truth if applicable;
  - changed files;
  - evidence files;
  - command logs;
  - receipts;
  - sha256 values.
- PC can reject a bundle if manifest is missing, sha mismatch exists, git truth is stale, scope is too broad, or required evidence is absent.
- Bundle verification is separate from human acceptance.
- PASS does not mean “system complete”; it means the bundle meets the specific acceptance criteria.

Why this comes second:

The existing VM2 → PC workflow already works manually.
This arc turns that workflow into a verifiable interface.

---

## 5. Foundation Arc 3 — Warning / Encoding / Stale Baseline

Priority: high.

Goal:

Stop false confidence caused by warning flood, mojibake, and stale dashboard state.

Required artifacts:

- `REGISTRY/WARNING_BASELINE.json`
- `scripts/check_warning_baseline.py`
- `scripts/check_utf8_owner_docs.py` or equivalent
- `schemas/stale_status.schema.json`
- `SANCTUM/HUD_STATE_CONTRACT_V0_1.md`
- dashboard/HUD rule: every shown status needs `last_checked_at`, exact SHA, source path, evidence path, and stale state

Acceptance criteria:

- Current warning debt is baselined against exact SHA.
- New warning regressions can be detected.
- Owner-facing operational docs decode as UTF-8 without BOM.
- cp1251 is allowed only as legacy source for conversion, never as target.
- Sanctum/HUD must not display stale values as live values.
- Dashboard is not source of truth.

Why this comes third:

Without this layer, the UI and reports can look correct while being stale, noisy, or unreadable.

---

## 6. Foundation Arc 4 — First Organ-Guided Task Registration

Priority: after Arcs 1–3.

Goal:

Register the first task through the first organs rather than through chat alone.

Minimum organ chain:

- Doctrinarium: preflight / doctrine status
- Administratum: task address packet / ledger entry
- Officio Agentis: agent corridor packet
- Astronomicon: stage map draft
- Inquisition: review checklist

Required artifacts:

- Administratum task registration packet
- Officio agent corridor packet
- Astronomicon stage map draft
- Inquisition review checklist
- Owner decision receipt

Acceptance criteria:

- Task is registered with TASK_ID.
- Stage map exists with STAGE_IDs.
- Owner can approve or block.
- VM2 receives a stage-specific corridor, not a vague prompt.
- No automatic next-stage execution.

---

## 7. Foundation Arc 5 — First Contract-Backed Dry Run

Priority: after Arc 4.

Goal:

Run one small task through the new foundation without relying on Sanctum buttons.

Flow:

Owner goal  
→ TASK_ID  
→ STAGE_ID map  
→ RUN_ID  
→ VM2 bundle  
→ PC bundle verifier  
→ PC review  
→ commit/push  
→ VM2 sync  
→ receipts  
→ Owner summary

Acceptance criteria:

- Every stage has evidence.
- Bundle verifier runs.
- PC Git CLI check runs.
- VM2 Git CLI check runs after sync.
- Owner gets fixed response form.
- Verdict is honest: PASS, PASS_WITH_WARNINGS, DEGRADED, BLOCKED, or FAIL.

---

## 8. Sanctum position

Sanctum is not canceled.
Sanctum is delayed until the foundation can feed it real state.

Allowed now:

- read-only HUD experiments;
- visual design experiments;
- local dashboard display of existing receipts;
- stale warnings;
- evidence links.

Blocked now:

- task-start buttons;
- auto-next-stage buttons;
- graph UI as source of truth;
- green status without evidence;
- hidden execution behind UI.

Sanctum should eventually become a control surface over contracts, receipts, and gates.
It must not become the source of truth.

---

## 9. Updated near-term execution order

Recommended order from this point:

1. TASK/STAGE/RUN contracts v0.1.
2. Bundle manifest + receipt/provenance contracts v0.1.
3. Git/Route truth schemas and validators v0.1.
4. Warning baseline refresh v0.1, PC-only.
5. Stale status + HUD state contract v0.1.
6. Administratum task registration/address packet v0.1.
7. Officio agent corridor packet v0.1.
8. Astronomicon general task registration and stage map draft v0.1.
9. First-four-organs work packet generator v0.1.
10. First contract-backed dry run.
11. Sanctum minimal integration over real receipts and state.
12. Sanctum safe buttons only after repeated verified manual E2E.

---

## 10. What is considered blocked

Blocked until contracts exist:

- Sanctum task buttons.
- Graph UI as operational state.
- Auto-run next stage.
- Broad warning cleanup.
- Full organ operationalization.
- VM2 commit/push.
- Bundle acceptance without manifest and sha256.
- Claiming an organ is operational because a folder exists.
- Treating Kiro advice as canon without reconciliation.
- Treating dashboard output as truth without stale/evidence model.

---

## 11. Relation to original 12 steps

The original 12 steps remain the historical planning source.

This file reframes them by dependency:

- Step 6 is accepted as Doctrinarium preflight v0.1, not full doctrine gate.
- Step 7 must be strengthened by TASK schema and address packet.
- Step 8 must be strengthened by Officio corridor and response contract.
- Step 9a and 9b require TASK/STAGE/RUN contracts first.
- Step 10 requires bundle manifest and receipt/provenance rules.
- Step 11 requires stale-status and evidence-linked HUD state.
- Step 12 must be a contract-backed dry run, not a visual demo.

---

## 12. Immediate next task

Recommended next task:

`TASK-20260512-TASK-STAGE-RUN-CONTRACTS-V0_1`

Purpose:

Create the minimal contract layer for task, stage, run, and pass criteria.

Expected executor:

VM2 prepares bundle.
PC reviews, runs checks, commits, pushes, and syncs VM2.

Expected verdict:

`PASS_WITH_WARNINGS` is acceptable if contracts and validators exist but broader warning debt remains.

No fake green.