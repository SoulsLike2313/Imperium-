# Second Brain Neural Map V0.5 — Launcher
# PROTOTYPE_INTERACTIVE | RULE_BASED_ONLY | NO_LOCAL_LLM | NO_AGENT_API
# NOT PRODUCTION READY

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$V05Root   = Split-Path -Parent $ScriptDir
$SBRoot    = Split-Path -Parent $V05Root
$TVRoot    = Split-Path -Parent $SBRoot

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Second Brain Neural Map V0.5 — Launcher" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Mode:        PROTOTYPE_INTERACTIVE" -ForegroundColor Yellow
Write-Host "Rule-based:  YES (no LLM, no agent API)" -ForegroundColor Yellow
Write-Host "Port:        8766" -ForegroundColor Green
Write-Host ""
Write-Host "Step 1: Building snapshot..." -ForegroundColor Cyan

try {
    $snapshotScript = Join-Path $V05Root "tools\snapshot_builder_v0_5.py"
    py -3.12 $snapshotScript
    Write-Host "Snapshot built OK" -ForegroundColor Green
} catch {
    Write-Host "Snapshot build failed (non-fatal): $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 2: Starting server on http://localhost:8766/" -ForegroundColor Cyan
Write-Host "Open browser manually: http://localhost:8766/" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop." -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan

$serverScript = Join-Path $ScriptDir "server_v0_5.py"
py -3.12 $serverScript
