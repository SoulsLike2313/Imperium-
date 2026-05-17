# SCRIPT PAIN CHRONICLE V0.1

## Purpose
This chronicle records recent script/tool pain so repeated failure patterns become enforceable discipline instead of forgotten incidents.

## Foundational Principle
"Every repeated pain becomes a gate, policy, backlog, or checker."

## A. DIRTY_START_PARTIAL_ARTIFACTS
- What happened:
  - Work attempts started from dirty or partial local artifacts, risking mixed-truth outcomes and half-written evidence.
- How it was detected:
  - Gate Spine truth checks (`git status`, HEAD checks, scope checks) surfaced mismatch risk before acceptance.
- Correct response:
  - Quarantine partial attempt, return to clean truth baseline, then retry with explicit gate acknowledgment.
- Lesson:
  - No script-hardening claim is valid if start-state truth is uncertain.

## B. FAKE_GREEN_SCANNER_REPORT_AVALANCHE
- What happened:
  - `VISUAL_FAKE_GREEN_SCAN_V0_1.json` expanded to `164,480` lines.
- How it was diagnosed:
  - `SCANNER_OUTPUT_BLOAT_DIAGNOSIS_V0_1.json` traced root cause to near-full finding payload persistence without budget controls.
- How it was fixed/contained:
  - `GATE-U12-REPORT-OUTPUT-BUDGET` was introduced and scanner output was regenerated in compact, capped form.
- Lesson:
  - A giant report is not stronger evidence; it is often weaker governance.

## C. STATIC_BROWSER_AUDIT_INVALID_FPS
- What happened:
  - Browser FPS was measured while required CSS/JS failed to load (`net::ERR_FILE_NOT_FOUND`), so the frame metric represented incomplete UI state.
- Why FPS was invalid:
  - Without required assets loaded, DOM/render conditions are non-representative and cannot certify real UI performance truth.
- How path/target correction improved audit quality:
  - Target/path discipline moved audits toward asset-complete static verification and blocked acceptance until CSS/JS load truth was proven.
- Lesson:
  - Metric collection without preconditions is measurement theater.

## D. FULL_RUNTIME_AUDIT_STATIC_ASSET_ROUTE_BLOCKER
- What happened:
  - Full runtime audit launched safely and API checks passed, but browser target returned `404` and required CSS/JS were missing.
- Why API truth alone is not UI performance truth:
  - Backend endpoint health confirms service availability, not front-end route correctness or render-path completeness.
- Next fix required:
  - Route/static mount alignment plus mandatory `HTTP 200` checks for HTML/CSS/JS before FPS acceptance.
- Lesson:
  - Runtime PASS cannot be claimed from API-only success when UI route truth is broken.

## E. PYTHON_STRICT_TYPE_SENSOR
- What happened:
  - VS Code/Pylance strict mode exposed red zones in Python tool surfaces used for audits, gates, and receipts.
- Why this is useful:
  - Strict typing pressure reveals hidden shape drift, optional handling risks, and weak contracts before they become gate failures.
- Why full typing fix is not done in this task:
  - This task is foundational law/backlog hardening, not mass refactor of all legacy and active scripts.
- Lesson:
  - Reusable tools require type discipline before promotion; "it ran once" is not enough.

## Doctrine Conversion Outcome
- Pain has been converted into:
  - Gate law (`GATE-U13-PYTHON-TYPE-SAFETY`);
  - Type-safety policy (human + machine form);
  - Inquisition audit rules;
  - Backlog for staged hardening.
