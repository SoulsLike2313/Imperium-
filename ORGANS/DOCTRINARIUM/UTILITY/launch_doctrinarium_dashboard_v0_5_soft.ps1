$ErrorActionPreference = "Stop"

$Root = "E:\IMPERIUM"
$Dashboard = Join-Path $Root "ORGANS\DOCTRINARIUM\UTILITY\WEB_DASHBOARD_SOFT"
$Server = Join-Path $Dashboard "dashboard_server.py"

if (!(Test-Path $Server)) {
    throw "Dashboard server not found: $Server"
}

Write-Host "Launching Doctrinarium Dashboard v0.5_soft..."
Write-Host "URL: http://127.0.0.1:8788"
Write-Host "Close this PowerShell window to stop the dashboard server."

python $Server
