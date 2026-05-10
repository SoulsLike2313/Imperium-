# COMMANDS

## Baseline Git Commands
```powershell
git status --short
git remote -v
git branch --show-current
git pull --rebase
git push origin master
```

## Analyzer v0.2 Commands
```powershell
powershell -ExecutionPolicy Bypass -File E:\IMPERIUM\TOOLS\administratum_analyze_git_local_context.ps1 -Root E:\IMPERIUM -Target FULL_IMPERIUM_SUMMARY -PostPushRealityCheck

powershell -ExecutionPolicy Bypass -File E:\IMPERIUM\TOOLS\administratum_analyze_git_local_context.ps1 -Root E:\IMPERIUM -Target VM2_WORK -ForVM2 -PostPushRealityCheck
```

## Workflow Commands
```powershell
# Analyze only
powershell -ExecutionPolicy Bypass -File E:\IMPERIUM\ORGANS\ADMINISTRATUM\UTILITY\run_administratum_context_bundle_workflow.ps1 -Root E:\IMPERIUM -Target FULL_IMPERIUM_SUMMARY -AnalyzeOnly

# Analyze + build safe bundle
powershell -ExecutionPolicy Bypass -File E:\IMPERIUM\ORGANS\ADMINISTRATUM\UTILITY\run_administratum_context_bundle_workflow.ps1 -Root E:\IMPERIUM -Target FULL_IMPERIUM_SUMMARY -BuildBundle
```

## Builder Direct Command
```powershell
powershell -ExecutionPolicy Bypass -File E:\IMPERIUM\TOOLS\build_chat_compilation_from_analysis.ps1 -Root E:\IMPERIUM -TaskId FULL_IMPERIUM_CONTEXT
```

## Read Next Action
```powershell
Get-Content E:\IMPERIUM\CURRENT_STATE\ADMINISTRATUM_ANALYZER\OWNER_NEXT_ACTION.md
```

## Output Location
- Bundle zip location: `E:\IMPERIUM\CHAT_COMPILATIONS_LOCAL\`

Do not place secret SSH command bodies, tokens, passwords, or private keys in public docs.
