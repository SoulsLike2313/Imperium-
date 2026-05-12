# AGENT_NAVIGATION_AND_REPO_BOUNDARY_V0_1

## Purpose
This guide gives agents a strict navigation layer for entering IMPERIUM safely. It separates active source from runtime/evidence/legacy areas and provides a low-risk way to produce reviewable patch bundles without fake green claims.

## Zone Model: Source vs Runtime vs Evidence vs Artifact vs Legacy
Active source zones:
- `src/imperium/`
- `scripts/`
- `tests/`
- `schemas/`
- `REGISTRY/`
- `TOOLS/`
- `SANCTUM/sanctum_v0_29_qt.py`
- `SANCTUM/sanctum_git_cli_check_service_v0_1.py`
- `ORGANS/`

Runtime/generated zones (local outputs, not product source):
- `.imperium_runtime/`
- runtime receipts/verdicts/reports

Evidence zones (task proof and diagnostic context):
- `CURRENT_STATE/`
- selected generated logs for validation

Artifact zones (transfer/review packages):
- `ARTIFACTS/`
- local bundle output directories (for VM2/PC transfer)

Legacy/caution zones (continuity and historical context, not deletion targets):
- older Sanctum versions before `v0_29_qt`
- `ORGANS/ADMINISTRATUM/CONTINUITY/PACKS/`
- `PC_ENGINEERING_ROOM/`

## Fast Navigation Commands
Tracked file truth:
- `git ls-files`
- `git ls-files | rg "<pattern>"` (if `rg` is available)

Find active references:
- `git grep "<symbol_or_path_fragment>"`
- `rg "<symbol_or_path_fragment>"` (if available)
- `fd "<name>"` (if available)

Read current git state:
- `git status --short`
- `git log -1 --oneline`
- `git rev-parse HEAD`

## How To Find Active Code Reliably
1. Start from tracked files (`git ls-files`) and current entrypoints.
2. Cross-check with active scripts in `scripts/` and current Sanctum entrypoint.
3. Confirm schema/registry references from `schemas/schema_registry.json` and `REGISTRY/*.json`.
4. Treat older versioned files as caution unless explicitly assigned.

## How To Avoid Legacy Traps
- Do not assume newest-looking folder name is active; verify through entrypoints and registries.
- Do not treat continuity packs or historical snapshots as refactor targets in unrelated tasks.
- Do not mass-delete legacy trees to reduce warning count unless assigned a dedicated cleanup task.

## How To Inspect Current Task State
Run preflight truth checks:
- `git fetch origin`
- `git rev-parse HEAD`
- `git rev-parse origin/master`
- `git ls-remote origin refs/heads/master`
- `git log -1 --oneline`
- `./TOOLS/run_administratum_git_cli_check.sh`
- `python3 scripts/verify_repo.py`

Interpretation baseline:
- matching heads confirm VM2 is on current public baseline
- `verify_repo` may be `PASS_WITH_WARNINGS` with blockers `0`
- warning flood is known debt until dedicated cleanup task lands

## How To Propose Patch Bundles Safely
1. Preflight and confirm clean starting worktree.
2. Apply narrow, scoped edits only for assigned blocker/task.
3. Run syntax/tests/checkers relevant to the touched files.
4. Re-run `verify_repo` and Git CLI checker.
5. Capture `git status`, `git diff --stat`, focused `git diff`.
6. Package source files + runtime verdicts + evidence text + summary markdown.
7. Hand off for PC review and commit on PC only.

## PASS_WITH_WARNINGS Interpretation
`PASS_WITH_WARNINGS` is acceptable only when blockers are zero and warnings are explained honestly. It is not equivalent to full green.

## Warning Flood Reality
The current warning flood is known legacy debt driven by continuity/legacy/version sprawl. It does not mean product-ready health, and it must not be rebranded as full pass/stability.
