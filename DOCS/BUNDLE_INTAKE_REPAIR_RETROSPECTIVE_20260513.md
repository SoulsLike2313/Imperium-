# Bundle Intake Repair Retrospective — 2026-05-13

## Scope

This document closes the Support Interlude repair chain for the Tooling Spin-Off SCRIPTORIUM / ARSENAL intake.

The goal is not to hide the repair history. The goal is to preserve provenance and add a regression gate so the PC-side bundle intake launcher does not fail the same way again.

## Final Git Truth Before Rollup

- Previous verified HEAD: `c77cb7a317142ccf295aa01928586525685b2077`
- Previous latest commit: `TASK-20260513: register administratum git cli checker`
- VM2 final receipt: `ADMINISTRATUM-GIT-CLI-CHECK-V0_1`
- VM2 verdict: `PASS`
- VM2 worktree clean: `true`

## Incident Summary

During Tooling Spin-Off intake, the PC-side launcher `TOOLS/review_worker_bundle_intake.ps1` exposed two real script defects:

1. Reserved PowerShell argument name defect.
   - Function parameter used `[string[]]$Args`.
   - PowerShell also has automatic `$Args`.
   - The launcher called bare `git` instead of `git status --short`.
   - Result: preflight failed before bundle verification.

2. `TrimStart` character-array defect.
   - Launcher used `.TrimStart('\\','/')`.
   - PowerShell treated `\\` as a string with length 2, not a single `System.Char`.
   - Result: controlled unpack failed after verification.

A third operational defect was exposed by clean VM2 sync:

3. VM2 receipt checker was local/untracked.
   - `TOOLS/run_administratum_git_cli_check.sh` existed locally before.
   - `git clean -fd` removed it.
   - The checker was then registered as a tracked executable.

## Repair Commits Kept as Provenance

The commits are intentionally not squashed.

Reason:

- exact SHA tree URLs are used as truth anchors;
- VM2 receipts reference real commit history;
- force-push would weaken provenance;
- keeping the repair chain proves that the gates found real defects and were hardened.

## Regression Rules

The bundle intake launcher must satisfy these rules:

1. It must not use `[string[]]$Args` for command forwarding.
2. It must use `$CommandArgs` or another non-reserved name.
3. It must not call external commands with an empty arg array when args were requested.
4. It must not use `.TrimStart('\\','/')`.
5. It must use `.TrimStart([char[]]@('\','/'))` or an equivalent char-array-safe expression.
6. It must remain parseable by PowerShell.
7. It must continue to support the checked Tooling Spin-Off intake path.

## New Regression Gate

`TOOLS/test_bundle_intake_regression.ps1`

This test is PC/Windows PowerShell-oriented. It writes runtime-only evidence under:

`.imperium_runtime/bundle_intake_regression/`

Expected result:

- verdict: `PASS`
- no reserved `$Args` parameter marker;
- command args forwarding probe passes;
- bad `TrimStart` marker absent;
- char-array `TrimStart` marker present;
- target intake launcher parses successfully.

## Owner Decision

Do not squash the repair chain.

Add this rollup hardening commit and proceed to Act 3 only after:

1. PC regression test passes.
2. SCRIPTORIUM registry check passes.
3. PC commit/push succeeds.
4. VM2 sync reaches the same HEAD.
5. VM2 Git CLI receipt returns `PASS`.