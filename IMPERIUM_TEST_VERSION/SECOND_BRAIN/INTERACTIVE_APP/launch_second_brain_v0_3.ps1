# Second Brain V0.3 — PowerShell Launcher
# Mode: PROTOTYPE_INTERACTIVE | RULE_BASED_ONLY | NO_LOCAL_LLM | NO_AGENT_API
# Usage: powershell -ExecutionPolicy Bypass -File launch_second_brain_v0_3.ps1

$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Second Brain V0.3 — Interactive Launcher" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Mode:    PROTOTYPE_INTERACTIVE" -ForegroundColor Yellow
Write-Host "  Status:  RULE_BASED_ONLY | NO_LOCAL_LLM | NO_AGENT_API" -ForegroundColor Yellow
Write-Host "  NOT PRODUCTION READY — PROTOTYPE ONLY" -ForegroundColor Red
Write-Host ""

# Locate server.py relative to this script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ServerScript = Join-Path $ScriptDir "server.py"

if (-not (Test-Path $ServerScript)) {
    Write-Host "[ERROR] server.py not found at: $ServerScript" -ForegroundColor Red
    exit 1
}

Write-Host "  Server:  $ServerScript" -ForegroundColor Green
Write-Host "  URL:     http://localhost:8765/" -ForegroundColor Green
Write-Host ""
Write-Host "  Opening browser in 2 seconds..." -ForegroundColor Cyan
Write-Host "  Press Ctrl+C to stop the server." -ForegroundColor Cyan
Write-Host ""

# Start browser after short delay (background job)
Start-Job -ScriptBlock {
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:8765/"
} | Out-Null

# Run server (blocking)
try {
    py -3.12 $ServerScript
} catch {
    Write-Host "[ERROR] Failed to start server: $_" -ForegroundColor Red
    Write-Host "Make sure Python 3.12 is installed and accessible as 'py -3.12'" -ForegroundColor Yellow
    exit 1
}
