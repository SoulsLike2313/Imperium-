$ErrorActionPreference = "Stop"
$env:IMPERIUM_ROOT = "E:\IMPERIUM"
$env:ADMINISTRATUM_HOST = "127.0.0.1"
$env:ADMINISTRATUM_PORT = "8792"
$Server = Join-Path $env:IMPERIUM_ROOT "ORGANS\ADMINISTRATUM\UTILITY\WEB_DASHBOARD_V0_2\dashboard_server.py"
$py = Get-Command py -ErrorAction SilentlyContinue
if ($py) {
    & py -3 $Server
} else {
    & python $Server
}