# AGENTS.md

## Purpose
This is the first file every agent should read before editing anything in this repository. It defines what is active, what is legacy/caution, what is local/runtime-only, and how to avoid fake green.

## Current Truth Check
Run these checks before any patch and before handing work back.

Linux / VM2:
- `git status --short`
- `git fetch origin`
- `git rev-parse HEAD`
- `git rev-parse origin/master`
- `git ls-remote origin refs/heads/master`
- `git rev-list --count HEAD`
- `git log -1 --oneline`
- `./TOOLS/run_administratum_git_cli_check.sh`
- `python3 scripts/verify_repo.py`

Windows / PC:
- `git status --short`
- `git fetch origin`
- `git rev-parse HEAD`
- `git rev-parse origin/master`
- `git ls-remote origin refs/heads/master`
- `git rev-list --count HEAD`
- `git log -1 --oneline`
- `powershell -ExecutionPolicy Bypass -NoProfile -File .\TOOLS\RUN_ADMINISTRATUM_GIT_CLI_CHECK.ps1`
- `py -3 .\scripts\verify_repo.py`

## Safe First Commands
Use read-only or low-risk commands first:
- `git status --short`
- `git log -1 --oneline`
- `git ls-files`
- `git grep "<pattern>"`
- `rg "<pattern>"` if available
- `fd "<name>"` if available
- `python3 scripts/verify_repo.py`
- `./TOOLS/run_administratum_git_cli_check.sh`

## Active Source Zones
- `src/imperium/`: active Python package source (config/security/receipts)
- `scripts/`: active verification and checker scripts
- `tests/`: active pytest coverage for current spine and checks
- `schemas/`: active JSON schema contracts
- `REGISTRY/`: active machine-readable registries
- `TOOLS/`: active operational wrappers/check tools
- `SANCTUM/sanctum_v0_29_qt.py`: current Sanctum UI runtime entry
- `SANCTUM/sanctum_git_cli_check_service_v0_1.py`: Sanctum Git CLI check service
- `ORGANS/`: organ definitions, continuity, and organ-specific scripts/docs

## Current Active Entrypoints
- `SANCTUM/RUN_SANCTUM_V0_29_QT.ps1`
- `SANCTUM/sanctum_v0_29_qt.py`
- `TOOLS/RUN_ADMINISTRATUM_GIT_CLI_CHECK.ps1`
- `TOOLS/run_administratum_git_cli_check.sh`
- `scripts/verify_repo.py`

## Registries
- `REGISTRY/ORGAN_REGISTRY.json`: organ ownership/status map (may drift from current reality)
- `REGISTRY/SCRIPT_REGISTRY.json`: script inventory and metadata (may drift from current reality)
- `REGISTRY/COMMAND_ALLOWLIST.json`: command policy allowlist
- `schemas/schema_registry.json`: schema inventory for active JSON contracts

## Runtime / Generated / Local-Only Zones
These are not active product source and should not be treated as canonical implementation:
- `.imperium_runtime/` runtime reports, verdicts, receipts
- `INBOX/` inbound local transfer area
- `OUTBOX/` outbound local transfer area
- local bundle folders (including VM2 bundle staging)
- VM2 private folders outside repo root
- runtime receipts and generated evidence files

## Legacy / Caution Zones
Caution zones are continuity/history context. Do not mass-delete:
- older Sanctum files before `SANCTUM/sanctum_v0_29_qt.py`
- `ORGANS/ADMINISTRATUM/CONTINUITY/PACKS/`
- `CURRENT_STATE/`
- `ARTIFACTS/`
- older organ dashboard variants
- `PC_ENGINEERING_ROOM/`

## Known Current Debt
- warning flood from legacy/continuity packs creates noisy `PASS_WITH_WARNINGS`
- Sanctum raw subprocess usage is not yet migrated to command gateway
- missing 4 organs: Custodes, Strategium, Schola Imperialis, Throne
- registry drift between declared state and real active files
- version sprawl across Sanctum and historical operational scripts

## Do Not Touch Without Owner Approval
- mass deletion of files or folders
- moving legacy folders
- rewriting Sanctum architecture
- changing public/private boundary model
- editing private/local paths outside scoped VM2 workspace
- committing or pushing from VM2
- adding runtime outputs into tracked source
- declaring product-ready, fully green, or stable

## How To Prepare A Safe Patch
1. Run preflight truth checks and capture evidence.
2. Keep edits tightly scoped to the assigned task.
3. Run `py_compile` and task-specific tests.
4. Run `python3 scripts/verify_repo.py`.
5. Run `./TOOLS/run_administratum_git_cli_check.sh`.
6. Inspect `git status --short` and `git diff`.
7. Build an artifact bundle with source + runtime evidence.
8. Hand off to PC owner review and commit on PC only.

## Task Lifecycle Summary
Owner goal -> Doctrinarium preflight -> Officio Agentis role assignment -> Administratum work packet -> Astronomicon stage map -> Strategium scope/plan -> Mechanicus tools/scripts -> Servitor execution -> Inquisition audit -> Schola lessons learned -> Owner/Throne acceptance.

## Kiro Audit Follow-up Order
Do not execute these here; this is ordering guidance only:
1. warning flood / continuity packs cleanup
2. registry sync
3. Sanctum command gateway migration
4. missing organs scaffold
5. Sanctum legacy/archive cleanup
6. Arsenal/Scriptorium later
