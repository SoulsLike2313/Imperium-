# Analyzer Patch Report

TASK_ID: TASK-20260511-ADMINISTRATUM-ANALYZER-PURITY-AND-CLEAN-HANDOFF-V0_1

## Patch intent
- Stop normal analyze/bundle operations from writing tracked `CURRENT_STATE` analyzer files.
- Redirect runtime outputs to ignored `.imperium_runtime` paths.
- Keep explicit checkpointing separate via dedicated command.

## Patched files
- `.gitignore`
- `ORGANS/ADMINISTRATUM/UTILITY/launch_administratum_dashboard_v0_3.ps1`
- `TOOLS/administratum_analyze_git_local_context.ps1`
- `TOOLS/build_chat_compilation_from_analysis.ps1`
- `ORGANS/ADMINISTRATUM/UTILITY/run_administratum_context_bundle_workflow.ps1`
- `TOOLS/administratum_record_analyzer_checkpoint.ps1` (new explicit checkpoint command)
- `DOCS/ANALYZER_RUNTIME_POLICY.md` (new policy)

## Behavior changes
- Dashboard v0.3 analyze/build now writes runtime output to `.imperium_runtime/administratum_analyzer/latest/`.
- Bundle output default path changed to `.imperium_runtime/bundles/`.
- Builder now writes runtime receipts with required bundle hash/size/filename/source metadata after zip creation.
- Workflow launcher now reads runtime analyzer outputs first with legacy read fallback only.
- Analyzer script output root moved to runtime path and no longer targets tracked CURRENT_STATE by default.

## Required runtime receipt fields implemented
- `actual_bundle_filename`
- `actual_bundle_sha256`
- `actual_bundle_size`
- `created_at`
- `builder_script_version`
- `source_head`
- `source_commit_count`
- `runtime_output_dir`
- `git_status_before`
- `git_status_after`

## Safety notes
- Legacy tracked analyzer files were not deleted or moved.
- Runtime redirection is localized and non-destructive.
- Script parse checks passed for all patched/new PowerShell scripts.
