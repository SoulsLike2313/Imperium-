# Second Brain Neural Map V0.6 — Launch Script
# PROTOTYPE_INTERACTIVE | RULE_BASED_ONLY | NO_LOCAL_LLM | NO_AGENT_API

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ServerScript = Join-Path $ScriptDir "server_v0_6.py"
$SnapshotBuilder = Join-Path $ScriptDir "..\tools\snapshot_builder_v0_6.py"

Write-Host "============================================================"
Write-Host "Second Brain Neural Map V0.6"
Write-Host "============================================================"
Write-Host "Mode:    PROTOTYPE_INTERACTIVE"
Write-Host "Port:    8767"
Write-Host "URL:     http://localhost:8767/"
Write-Host ""
Write-Host "NOT PRODUCTION READY | RULE_BASED_ONLY | NO_LOCAL_LLM"
Write-Host "============================================================"

# Build snapshot first
Write-Host ""
Write-Host "Building snapshot..."
py -3 $SnapshotBuilder
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] Snapshot builder failed — server will start anyway"
}

Write-Host ""
Write-Host "Starting server..."
py -3 $ServerScript
