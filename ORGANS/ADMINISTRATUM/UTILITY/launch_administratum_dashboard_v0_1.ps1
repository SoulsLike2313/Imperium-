param(
  [switch]$NoOpen
)

$ErrorActionPreference = "Stop"
$server = "E:\IMPERIUM\ORGANS\ADMINISTRATUM\UTILITY\WEB_DASHBOARD_V0_1\dashboard_server.py"

if (-not (Test-Path -LiteralPath $server)) {
  Write-Error "Dashboard server not found: $server"
  exit 1
}

$python = "python"
& $python $server
