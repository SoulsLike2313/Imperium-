Set-Location E:\IMPERIUM

$DashboardPath = "E:\IMPERIUM\ORGANS\ASTRONOMICON\UTILITY\astronomicon_dashboard_v0_1.ps1"

if (!(Test-Path $DashboardPath)) {
    throw "Dashboard script not found: $DashboardPath"
}

powershell.exe -ExecutionPolicy Bypass -File $DashboardPath