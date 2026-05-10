# COMMANDS

## Baseline Git Commands
```powershell
git status --short
git remote -v
git branch --show-current
git pull --rebase
git push origin master
```

## Orientation Commands
```powershell
Get-Content START_HERE.md
Get-Content CURRENT_STATE\LAST_POINT_STATE.json
Get-Content DOCS\REPO_MAP.md
Get-Content DOCS\CHAT_ENTRY_PROTOCOL.md
```

## Administratum Analyzer / Bundle Commands
```powershell
powershell -ExecutionPolicy Bypass -File E:\IMPERIUM\TOOLS\administratum_analyze_git_local_context.ps1 -Root E:\IMPERIUM -Target FULL_IMPERIUM_SUMMARY

powershell -ExecutionPolicy Bypass -File E:\IMPERIUM\TOOLS\administratum_analyze_git_local_context.ps1 -Root E:\IMPERIUM -Target VM2_WORK -ForVM2

powershell -ExecutionPolicy Bypass -File E:\IMPERIUM\TOOLS\build_chat_compilation_from_analysis.ps1 -Root E:\IMPERIUM -TaskId FULL_IMPERIUM_CONTEXT

powershell -ExecutionPolicy Bypass -File E:\IMPERIUM\ORGANS\ADMINISTRATUM\UTILITY\run_administratum_context_bundle_workflow.ps1 -Root E:\IMPERIUM -Target FULL_IMPERIUM_SUMMARY
```

## Output
- Generated chat bundle zip is written under `E:\IMPERIUM\CHAT_COMPILATIONS_LOCAL\`.

## Notes
- Do not include secret SSH commands in repo docs.
- Any unverified command should be marked as requiring local check.
