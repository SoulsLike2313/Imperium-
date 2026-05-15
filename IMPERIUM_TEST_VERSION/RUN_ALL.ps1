# RUN_ALL.ps1
# Master script - runs all working loops and generates dashboard
# Version 2.0 - includes Second Brain, Live Workbench, Agent Memory Protocol
# Usage: .\IMPERIUM_TEST_VERSION\RUN_ALL.ps1

param(
    [switch]$SkipNewComponents,
    [switch]$OnlyCore,
    [switch]$Verbose
)

$ErrorActionPreference = "Continue"

$TestVersionRoot = "E:\IMPERIUM\IMPERIUM_TEST_VERSION"
$RepoRoot = "E:\IMPERIUM"

$StartTime = Get-Date -Format "o"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

Write-Host ""
Write-Host "=" * 70
Write-Host "  IMPERIUM TEST VERSION - FULL RUN v2.0"
Write-Host "=" * 70
Write-Host "Started: $StartTime"
Write-Host ""

$Results = @()

# ============================================
# CORE SYSTEMS
# ============================================
Write-Host ">>> CORE SYSTEMS"
Write-Host ""

# 1. Smoke Test
Write-Host "[1/7] Running Smoke Test..."
Write-Host "-" * 50
$smokeScript = "$TestVersionRoot\TESTING_FIELD\RUN_SMOKE.ps1"
if (Test-Path $smokeScript) {
    & powershell -ExecutionPolicy Bypass -File $smokeScript
    $smokeExit = $LASTEXITCODE
    $Results += @{ name = "Smoke Test"; exit_code = $smokeExit; verdict = if ($smokeExit -eq 0) { "PASS" } else { "FAIL" }; category = "core" }
} else {
    Write-Host "  SKIP: Script not found"
    $Results += @{ name = "Smoke Test"; exit_code = -1; verdict = "SKIP"; category = "core" }
}
Write-Host ""

# 2. Script Health
Write-Host "[2/7] Running Script Health Check..."
Write-Host "-" * 50
$mechScript = "$TestVersionRoot\ORGANS\MECHANICUS\RUN_SCRIPT_HEALTH.ps1"
if (Test-Path $mechScript) {
    & powershell -ExecutionPolicy Bypass -File $mechScript
    $mechExit = $LASTEXITCODE
    $Results += @{ name = "Script Health"; exit_code = $mechExit; verdict = if ($mechExit -eq 0) { "PASS" } else { "FAIL" }; category = "core" }
} else {
    Write-Host "  SKIP: Script not found"
    $Results += @{ name = "Script Health"; exit_code = -1; verdict = "SKIP"; category = "core" }
}
Write-Host ""

# 3. Audit
Write-Host "[3/7] Running Inquisition Audit..."
Write-Host "-" * 50
$auditScript = "$TestVersionRoot\ORGANS\INQUISITION\RUN_AUDIT.ps1"
if (Test-Path $auditScript) {
    & powershell -ExecutionPolicy Bypass -File $auditScript
    $auditExit = $LASTEXITCODE
    $Results += @{ name = "Audit"; exit_code = $auditExit; verdict = if ($auditExit -eq 0) { "PASS" } else { "FAIL" }; category = "core" }
} else {
    Write-Host "  SKIP: Script not found"
    $Results += @{ name = "Audit"; exit_code = -1; verdict = "SKIP"; category = "core" }
}
Write-Host ""

# ============================================
# NEW COMPONENTS (v2.0)
# ============================================
if (-not $OnlyCore) {
    Write-Host ">>> NEW COMPONENTS (v2.0)"
    Write-Host ""

    # 4. Second Brain - Memory Summary
    Write-Host "[4/7] Building Second Brain Memory Summary..."
    Write-Host "-" * 50
    $memoryScript = "$TestVersionRoot\SECOND_BRAIN\SCRIPTS\build_memory_summary.py"
    if (Test-Path $memoryScript) {
        py -3 $memoryScript
        $memoryExit = $LASTEXITCODE
        $Results += @{ name = "Second Brain"; exit_code = $memoryExit; verdict = if ($memoryExit -eq 0) { "PASS" } else { "FAIL" }; category = "new" }
    } else {
        Write-Host "  SKIP: Script not found"
        $Results += @{ name = "Second Brain"; exit_code = -1; verdict = "SKIP"; category = "new" }
    }
    Write-Host ""

    # 5. Live Workbench - Sandbox Tests
    Write-Host "[5/7] Running Live Workbench Sandbox Tests..."
    Write-Host "-" * 50
    $workbenchScript = "$TestVersionRoot\LIVE_WORKBENCH\SCRIPTS\run_sandbox_tests.py"
    if (Test-Path $workbenchScript) {
        py -3 $workbenchScript
        $workbenchExit = $LASTEXITCODE
        $Results += @{ name = "Live Workbench"; exit_code = $workbenchExit; verdict = if ($workbenchExit -eq 0) { "PASS" } else { "FAIL" }; category = "new" }
    } else {
        Write-Host "  SKIP: Script not found"
        $Results += @{ name = "Live Workbench"; exit_code = -1; verdict = "SKIP"; category = "new" }
    }
    Write-Host ""

    # 5b. Live Workbench - Generate Status
    Write-Host "[5b/7] Generating Workbench Status..."
    Write-Host "-" * 50
    $statusScript = "$TestVersionRoot\LIVE_WORKBENCH\SCRIPTS\generate_workbench_status.py"
    if (Test-Path $statusScript) {
        py -3 $statusScript
        $statusExit = $LASTEXITCODE
        # Don't add to results, just informational
    }
    Write-Host ""

    # 6. Agent Memory Protocol - Handshake
    Write-Host "[6/7] Running Agent Context Handshake..."
    Write-Host "-" * 50
    $handshakeScript = "$TestVersionRoot\AGENT_MEMORY_PROTOCOL\SCRIPTS\agent_context_handshake.py"
    if (Test-Path $handshakeScript) {
        py -3 $handshakeScript
        $handshakeExit = $LASTEXITCODE
        $Results += @{ name = "Agent Handshake"; exit_code = $handshakeExit; verdict = if ($handshakeExit -eq 0) { "PASS" } else { "FAIL" }; category = "new" }
    } else {
        Write-Host "  SKIP: Script not found"
        $Results += @{ name = "Agent Handshake"; exit_code = -1; verdict = "SKIP"; category = "new" }
    }
    Write-Host ""
}

# ============================================
# DASHBOARD GENERATION
# ============================================
Write-Host ">>> DASHBOARD"
Write-Host ""

# 7. Generate Dashboard
Write-Host "[7/7] Generating Sanctum Mirror Dashboard..."
Write-Host "-" * 50
$dashScript = "$TestVersionRoot\SANCTUM_MIRROR\GENERATE_INDEX.ps1"
if (Test-Path $dashScript) {
    & powershell -ExecutionPolicy Bypass -File $dashScript
    $dashExit = $LASTEXITCODE
    $Results += @{ name = "Dashboard"; exit_code = $dashExit; verdict = if ($dashExit -eq 0) { "PASS" } else { "FAIL" }; category = "dashboard" }
} else {
    Write-Host "  SKIP: Script not found"
    $Results += @{ name = "Dashboard"; exit_code = -1; verdict = "SKIP"; category = "dashboard" }
}
Write-Host ""

$EndTime = Get-Date -Format "o"

# ============================================
# SUMMARY
# ============================================
Write-Host "=" * 70
Write-Host "  SUMMARY"
Write-Host "=" * 70

$CoreResults = $Results | Where-Object { $_.category -eq "core" }
$NewResults = $Results | Where-Object { $_.category -eq "new" }

Write-Host ""
Write-Host "  CORE SYSTEMS:"
foreach ($r in $CoreResults) {
    $icon = switch ($r.verdict) {
        "PASS" { "[OK]" }
        "FAIL" { "[XX]" }
        "SKIP" { "[--]" }
    }
    Write-Host "    $icon $($r.name)"
}

if ($NewResults.Count -gt 0) {
    Write-Host ""
    Write-Host "  NEW COMPONENTS (v2.0):"
    foreach ($r in $NewResults) {
        $icon = switch ($r.verdict) {
            "PASS" { "[OK]" }
            "FAIL" { "[XX]" }
            "SKIP" { "[--]" }
        }
        Write-Host "    $icon $($r.name)"
    }
}

Write-Host ""
$PassCount = ($Results | Where-Object { $_.verdict -eq "PASS" }).Count
$FailCount = ($Results | Where-Object { $_.verdict -eq "FAIL" }).Count
$SkipCount = ($Results | Where-Object { $_.verdict -eq "SKIP" }).Count

Write-Host "  Passed: $PassCount"
Write-Host "  Failed: $FailCount"
Write-Host "  Skipped: $SkipCount"
Write-Host ""

$OverallVerdict = if ($FailCount -eq 0 -and $PassCount -gt 0) { "PASS" } elseif ($FailCount -gt 0) { "FAIL" } else { "NO_DATA" }
Write-Host "  OVERALL: $OverallVerdict"
Write-Host ""
Write-Host "Finished: $EndTime"
Write-Host ""

# Create master receipt
$MasterReceipt = @{
    receipt_id = "RCP-MASTER-$Timestamp"
    version = "2.0"
    action = "full_run"
    started_at_utc = $StartTime
    finished_at_utc = $EndTime
    overall_verdict = $OverallVerdict
    results = $Results
    dashboard_path = "IMPERIUM_TEST_VERSION/SANCTUM_MIRROR/index.html"
    components = @{
        core = @("smoke_test", "script_health", "audit")
        new = @("second_brain", "live_workbench", "agent_handshake")
    }
}

$ReceiptPath = "$TestVersionRoot\RECEIPTS\RCP-MASTER-$Timestamp.json"
$MasterReceipt | ConvertTo-Json -Depth 5 | Out-File -FilePath $ReceiptPath -Encoding UTF8

Write-Host "Master receipt: $ReceiptPath"
Write-Host ""
Write-Host "Open dashboard: start $TestVersionRoot\SANCTUM_MIRROR\index.html"

if ($OverallVerdict -eq "PASS") { exit 0 } else { exit 1 }
