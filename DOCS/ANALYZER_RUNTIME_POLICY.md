# Analyzer Runtime Policy

## Scope
This policy controls how Administratum analyzer and bundle scripts write outputs.

## Modes
1. Analyze mode
- Command examples:
  - `powershell -ExecutionPolicy Bypass -File E:\IMPERIUM\TOOLS\administratum_analyze_git_local_context.ps1 -Root E:\IMPERIUM -Target FULL_IMPERIUM_SUMMARY -PostPushRealityCheck`
  - Dashboard v0.3 button `POST /api/analyze`
- Allowed writes:
  - `.imperium_runtime/administratum_analyzer/latest/*`
- Forbidden writes:
  - `CURRENT_STATE/ADMINISTRATUM_ANALYZER/*`
  - `CURRENT_STATE/ADMINISTRATUM_ANALYZER_V0_3/*`

2. Bundle mode
- Command examples:
  - `powershell -ExecutionPolicy Bypass -File E:\IMPERIUM\TOOLS\build_chat_compilation_from_analysis.ps1 -Root E:\IMPERIUM`
  - Dashboard v0.3 button `POST /api/build`
- Allowed writes:
  - `.imperium_runtime/bundles/*`
  - `.imperium_runtime/administratum_analyzer/latest/LATEST_CONTEXT_BUNDLE_RECEIPT.json`
  - `.imperium_runtime/administratum_analyzer/latest/runtime_receipt.json`
  - `.imperium_runtime/administratum_analyzer/latest/LAST_CHAT_COMPILATION_PATH.txt`
- Forbidden writes:
  - `CURRENT_STATE/ADMINISTRATUM_ANALYZER/*`
  - `CURRENT_STATE/ADMINISTRATUM_ANALYZER_V0_3/*`

3. Record/checkpoint mode
- Command example:
  - `powershell -ExecutionPolicy Bypass -File E:\IMPERIUM\TOOLS\administratum_record_analyzer_checkpoint.ps1 -TaskId TASK-...`
- Allowed writes:
  - `ARTIFACTS/<TASK_ID>/CHECKPOINTS/<CHECKPOINT_ID>/*`
- Forbidden writes:
  - Runtime files must not be rewritten as tracked CURRENT_STATE.
- Purpose:
  - Create intentional, commit-ready evidence snapshot with receipt.

## Core rules
- Normal analyzer and bundle runs are runtime operations and must leave Git-tracked state unchanged.
- Tracked `CURRENT_STATE/ADMINISTRATUM_ANALYZER*` files are legacy references, not live runtime targets.
- Any commit-ready snapshot must be explicit and receipt-backed.

## Why this policy exists
- Analyzer outputs are dynamic and timestamp-sensitive.
- Writing dynamic output into tracked files creates false dirty worktree states.
- Clean handoff requires repeatable verification without accidental tracked modifications.
