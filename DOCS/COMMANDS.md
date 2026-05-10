# COMMANDS

## Baseline Git Commands
```powershell
git status --short
git status --ignored --short
git remote -v
git branch --show-current
git log --oneline --decorate -10
git rev-parse HEAD
git rev-parse origin/master
git ls-remote origin refs/heads/master
```

## Analyzer v0.2 (Post-Push Reality Check)
```powershell
powershell -ExecutionPolicy Bypass -File E:\IMPERIUM\TOOLS\administratum_analyze_git_local_context.ps1 -Root E:\IMPERIUM -Target FULL_IMPERIUM_SUMMARY -PostPushRealityCheck

powershell -ExecutionPolicy Bypass -File E:\IMPERIUM\TOOLS\administratum_analyze_git_local_context.ps1 -Root E:\IMPERIUM -Target VM2_WORK -ForVM2 -PostPushRealityCheck
```

## Workflow Launcher
```powershell
# Analyze only
powershell -ExecutionPolicy Bypass -File E:\IMPERIUM\ORGANS\ADMINISTRATUM\UTILITY\run_administratum_context_bundle_workflow.ps1 -Target FULL_IMPERIUM_SUMMARY -AnalyzeOnly

# Build safe bundle if analyzer allows
powershell -ExecutionPolicy Bypass -File E:\IMPERIUM\ORGANS\ADMINISTRATUM\UTILITY\run_administratum_context_bundle_workflow.ps1 -Target FULL_IMPERIUM_SUMMARY -BuildBundle

# Override manual-review block only after human review
powershell -ExecutionPolicy Bypass -File E:\IMPERIUM\ORGANS\ADMINISTRATUM\UTILITY\run_administratum_context_bundle_workflow.ps1 -Target FULL_IMPERIUM_SUMMARY -BuildBundle -ForceAfterManualReview
```

## Read Decision Outputs
```powershell
Get-Content E:\IMPERIUM\CURRENT_STATE\ADMINISTRATUM_ANALYZER\OWNER_NEXT_ACTION.md
Get-Content E:\IMPERIUM\CURRENT_STATE\ADMINISTRATUM_ANALYZER\WORKTREE_CLASSIFICATION_REPORT.md
Get-Content E:\IMPERIUM\CURRENT_STATE\ADMINISTRATUM_ANALYZER\GIT_REALITY_REPORT.md
```

## Interpretation Note
Dirty working tree is not the same as git sync failure.
- HEAD mismatch => FIX_GIT_SYNC_FIRST.
- HEAD match + dirty worktree => use worktree classifier categories to decide commit/ignore/manual review/bundle.

Bundle zip output: `E:\IMPERIUM\CHAT_COMPILATIONS_LOCAL\`
