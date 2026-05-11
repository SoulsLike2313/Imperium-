Set-Location E:\IMPERIUM

$dashboardPath = "E:\IMPERIUM\ORGANS\ASTRONOMICON\UTILITY\astronomicon_dashboard_v0_6.ps1"
if (-not (Test-Path -LiteralPath $dashboardPath)) {
    throw "Dashboard script not found: $dashboardPath"
}

powershell.exe -ExecutionPolicy Bypass -File $dashboardPath
