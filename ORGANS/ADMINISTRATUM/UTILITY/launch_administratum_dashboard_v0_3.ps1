param(
    [string]$Root = "E:\IMPERIUM",
    [string]$HostIp = "127.0.0.1",
    [int]$Port = 8792
)

$ErrorActionPreference = "Stop"

$env:IMPERIUM_ROOT = $Root
$env:ADMINISTRATUM_HOST = $HostIp
$env:ADMINISTRATUM_PORT = "$Port"

$Server = Join-Path $Root "ORGANS\ADMINISTRATUM\UTILITY\WEB_DASHBOARD_V0_3\dashboard_server.py"

if (!(Test-Path $Server)) {
    throw "Missing dashboard server: $Server"
}

Write-Host "Starting Administratum Dashboard v0.3..." -ForegroundColor Cyan
Write-Host "URL: http://$HostIp`:$Port"
Write-Host "Root: $Root"
Write-Host ""

py -3 $Server