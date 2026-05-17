# FULL RUNTIME AUDIT SAFETY CONTRACT V0.1

## Purpose
Define strict safety law for a future full runtime performance audit of Second Brain V0.6 without polluting canon truth.

## Current Static Audit Truth
- Browser target/path fix is complete.
- Required CSS/JS load succeeds in static local server mode.
- FPS was measured only as `STATIC_FRONTEND_FPS_ESTIMATE`.
- `FULL_RUNTIME_AUDIT_NOT_RUN` remains true.

## Why Full Runtime Audit Needs This Contract
- Runtime server code includes mutating endpoints and write paths into `MEMORY_ZONES` and `RUNTIME`.
- Full runtime performance evidence is invalid unless side effects are isolated, receipted, and auditable.

## Allowed Future Audit Modes
- `DISPOSABLE_LOCAL_RUNTIME_SERVER_WITH_QUARANTINE_WRITES` (preferred).
- `LOCALHOST_RUNTIME_SERVER_WITH_EXPLICIT_QUARANTINE_ROOT_AND_RECEIPTS`.
- `READ_ONLY_STATIC_FRONTEND_AUDIT` (allowed only for static metrics, never full runtime verdict).

## Forbidden Future Audit Modes
- Running runtime server directly against canonical repo state without write isolation.
- Accepting static-only FPS as full runtime performance truth.
- Committing raw traces/HAR/screenshots by default.
- Silent cleanup that removes evidence of side effects.

## Runtime Side Effect Risks
- Writes to task/comment/link runtime JSON files.
- Creation of runtime receipts, task packages, exports.
- Snapshot rebuild subprocess generating refreshed artifacts.
- Potential state drift during mutating API calls.

## Allowed Runtime Writes (Future Task Only, Under Explicit Quarantine)
- Quarantine root only, e.g. disposable clone/worktree or dedicated isolated runtime mirror.
- Receipts for every write, including write count and target paths.
- Temporary logs strictly outside tracked source unless Owner gate approves import.

## Forbidden Runtime Writes
- Direct writes into canonical repo `IMPERIUM_TEST_VERSION/SECOND_BRAIN/MEMORY_ZONES/**` during audit run.
- Direct writes into canonical repo `IMPERIUM_TEST_VERSION/SECOND_BRAIN/RUNTIME/**` during audit run.
- Untracked side effects without receipt binding.

## Required Pre-Run Checks
- Git truth lock and clean worktree check.
- Quarantine path existence and isolation proof.
- Server shutdown plan and process cleanup plan.
- Gate receipt skeleton with expected evidence paths.
- Report output budget limits loaded from `GATE-U12` contract.

## Required Post-Run Checks
- Server process terminated and verified not running.
- Runtime write manifest generated (path + size + checksum summary).
- Quarantine cleanup report generated (what preserved, what removed, why).
- Forbidden path diff check against canonical repo.
- No raw traces committed.

## Required API/Backend Truth Checks
- GET `/api/status` returns runtime state and counts.
- GET `/api/snapshot` returns snapshot freshness fields.
- GET `/api/tasks`, `/api/comments`, `/api/links` accessible.
- GET `/api/receipts`, `/api/export/status` accessible.
- If mutating endpoints are exercised, each write must produce matching receipt evidence.

## Required Asset Load Checks
- `neural_map_v0_6.css` loaded successfully.
- `neural_map_v0_6.js` loaded successfully.
- Failed required requests count recorded.
- Console error count recorded with compact samples.

## Required Performance Metrics
- load_to_domcontentloaded_ms
- load_to_load_event_ms
- dom_nodes
- svg_elements
- average_fps
- fps_1pct_low
- long_task_count (if measurable)
- console_errors / failed_requests

## Required Report Output Budget Rules
- Obey `GATE-U12-REPORT-OUTPUT-BUDGET` limits.
- Reports must remain compact (counts + top samples, no unlimited dumps).
- Evidence > verbosity; actionable summaries only.

## Raw Trace Policy
- Default: no raw trace/HAR/video/screenshot commit.
- Raw traces allowed only with explicit Owner gate and quarantined storage policy.

## Cleanup / Quarantine Policy
- Quarantine artifacts remain outside canonical source paths by default.
- Cleanup must be receipted; no silent deletion of audit evidence.
- If cleanup modifies any tracked path, Owner gate is mandatory.

## Owner Gate Requirements
- Required for any raw trace commit.
- Required for any audit mode that can touch canonical runtime paths.
- Required for any exception to output budget.

## STOP Conditions
- Quarantine isolation cannot be proven.
- Runtime writes appear outside declared quarantine.
- Required APIs/assets fail and report attempts to claim PASS.
- Raw trace artifact appears in staged diff without Owner gate.
- Report output budget exceeded.

## Validity Law
No full runtime performance verdict is valid unless:
- server/runtime launched safely;
- runtime writes are known, isolated, and receipted;
- required APIs respond;
- required CSS/JS/assets load;
- failed requests are recorded;
- console errors are recorded;
- FPS/load evidence is measured;
- report output budget is obeyed;
- no raw traces are committed without Owner gate.
