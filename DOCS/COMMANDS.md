# COMMANDS

## Safe Git Commands
`powershell
git status --short
git remote -v
git branch --show-current
git pull --rebase
git push origin master
`

## Validation/Orientation Commands
`powershell
Get-Content CURRENT_STATE\LAST_POINT_STATE.json
Get-Content DOCS\REPO_MAP.md
Get-Content DOCS\CHAT_ENTRY_PROTOCOL.md
`

## Dashboard Launch (if already present)
`powershell
powershell -ExecutionPolicy Bypass -File ORGANS\DOCTRINARIUM\UTILITY\launch_doctrinarium_dashboard_v0_8.ps1
powershell -ExecutionPolicy Bypass -File ORGANS\ADMINISTRATUM\UTILITY\launch_administratum_dashboard_v0_1.ps1
`

If a command is unavailable locally, treat it as environment-dependent and verify path first.
