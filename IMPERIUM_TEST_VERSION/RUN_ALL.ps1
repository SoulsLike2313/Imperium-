# RUN_ALL.ps1
# Master script - runs all working loops and generates dashboard
# Version 2.2 - includes Truth Spine, Second Brain, Live Workbench, Agent Memory Protocol, Learning Loop
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
Write-Host "  IMPERIUM TEST VERSION - FULL RUN v2.2"
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

# 7. Generate Dashboard (Legacy index.html)
Write-Host "[7/12] Generating Sanctum Mirror Dashboard (Legacy)..."
Write-Host "-" * 50
$dashScript = "$TestVersionRoot\SANCTUM_MIRROR\GENERATE_INDEX.ps1"
if (Test-Path $dashScript) {
    & powershell -ExecutionPolicy Bypass -File $dashScript
    $dashExit = $LASTEXITCODE
    $Results += @{ name = "Dashboard (Legacy)"; exit_code = $dashExit; verdict = if ($dashExit -eq 0) { "PASS" } else { "FAIL" }; category = "dashboard" }
} else {
    Write-Host "  SKIP: Script not found"
    $Results += @{ name = "Dashboard (Legacy)"; exit_code = -1; verdict = "SKIP"; category = "dashboard" }
}
Write-Host ""

# 7b. Generate Master Dashboard + Organ Dashboards (New)
Write-Host "[7b/12] Generating Master Dashboard + Organ Dashboards..."
Write-Host "-" * 50
$dashGenScript = "$TestVersionRoot\SANCTUM_MIRROR\dashboard_generator.py"
if (Test-Path $dashGenScript) {
    py -3 $dashGenScript --all
    $dashGenExit = $LASTEXITCODE
    $Results += @{ name = "Dashboard Generator"; exit_code = $dashGenExit; verdict = if ($dashGenExit -eq 0) { "PASS" } else { "FAIL" }; category = "dashboard" }
} else {
    Write-Host "  SKIP: Script not found"
    $Results += @{ name = "Dashboard Generator"; exit_code = -1; verdict = "SKIP"; category = "dashboard" }
}
Write-Host ""

# 8. Truth Spine Aggregation
Write-Host "[8/12] Running Truth Spine Aggregation..."
Write-Host "-" * 50
$truthScript = "$TestVersionRoot\TRUTH_SPINE\truth_aggregator.py"
if (Test-Path $truthScript) {
    py -3 $truthScript --receipts-dir "$TestVersionRoot\RECEIPTS" --output "$TestVersionRoot\REPORTS\truth_aggregate.json"
    $truthExit = $LASTEXITCODE
    $Results += @{ name = "Truth Spine"; exit_code = $truthExit; verdict = if ($truthExit -eq 0) { "PASS" } else { "FAIL" }; category = "truth" }
} else {
    Write-Host "  SKIP: Script not found"
    $Results += @{ name = "Truth Spine"; exit_code = -1; verdict = "SKIP"; category = "truth" }
}
Write-Host ""

# 9. Registry Auto-Sync
Write-Host "[9/12] Running Registry Auto-Sync..."
Write-Host "-" * 50
$registryScript = "$TestVersionRoot\REGISTRY\auto_sync.py"
if (Test-Path $registryScript) {
    py -3 $registryScript
    $registryExit = $LASTEXITCODE
    $Results += @{ name = "Registry Sync"; exit_code = $registryExit; verdict = if ($registryExit -eq 0) { "PASS" } else { "FAIL" }; category = "registry" }
} else {
    Write-Host "  SKIP: Script not found"
    $Results += @{ name = "Registry Sync"; exit_code = -1; verdict = "SKIP"; category = "registry" }
}
Write-Host ""

# ============================================
# LEARNING LOOP (Phase 5)
# ============================================
Write-Host ">>> LEARNING LOOP"
Write-Host ""

# 10. Lesson Extractor
Write-Host "[10/12] Extracting Lessons..."
Write-Host "-" * 50
$lessonScript = "$TestVersionRoot\ORGANS\SCHOLA_IMPERIALIS\SCRIPTS\lesson_extractor.py"
if (Test-Path $lessonScript) {
    py -3 $lessonScript
    $lessonExit = $LASTEXITCODE
    $Results += @{ name = "Lesson Extractor"; exit_code = $lessonExit; verdict = if ($lessonExit -eq 0) { "PASS" } else { "FAIL" }; category = "learning" }
} else {
    Write-Host "  SKIP: Script not found"
    $Results += @{ name = "Lesson Extractor"; exit_code = -1; verdict = "SKIP"; category = "learning" }
}
Write-Host ""

# 11. Anti-Pattern Scanner
Write-Host "[11/12] Scanning for Anti-Patterns..."
Write-Host "-" * 50
$antiPatternScript = "$TestVersionRoot\ORGANS\SCHOLA_IMPERIALIS\SCRIPTS\anti_pattern_scanner.py"
if (Test-Path $antiPatternScript) {
    py -3 $antiPatternScript --path ORGANS
    $antiPatternExit = $LASTEXITCODE
    # Anti-pattern scanner returns 1 if violations found, but that's informational
    $Results += @{ name = "Anti-Pattern Scanner"; exit_code = $antiPatternExit; verdict = if ($antiPatternExit -eq 0) { "PASS" } else { "PARTIAL" }; category = "learning" }
} else {
    Write-Host "  SKIP: Script not found"
    $Results += @{ name = "Anti-Pattern Scanner"; exit_code = -1; verdict = "SKIP"; category = "learning" }
}
Write-Host ""

# 12. Rule Extractor
Write-Host "[12/12] Extracting Rules..."
Write-Host "-" * 50
$ruleScript = "$TestVersionRoot\ORGANS\SCHOLA_IMPERIALIS\SCRIPTS\rule_extractor.py"
if (Test-Path $ruleScript) {
    py -3 $ruleScript
    $ruleExit = $LASTEXITCODE
    $Results += @{ name = "Rule Extractor"; exit_code = $ruleExit; verdict = if ($ruleExit -eq 0) { "PASS" } else { "FAIL" }; category = "learning" }
} else {
    Write-Host "  SKIP: Script not found"
    $Results += @{ name = "Rule Extractor"; exit_code = -1; verdict = "SKIP"; category = "learning" }
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
$LearningResults = $Results | Where-Object { $_.category -eq "learning" }

Write-Host ""
Write-Host "  CORE SYSTEMS:"
foreach ($r in $CoreResults) {
    $icon = switch ($r.verdict) {
        "PASS" { "[OK]" }
        "FAIL" { "[XX]" }
        "PARTIAL" { "[~~]" }
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
            "PARTIAL" { "[~~]" }
            "SKIP" { "[--]" }
        }
        Write-Host "    $icon $($r.name)"
    }
}

if ($LearningResults.Count -gt 0) {
    Write-Host ""
    Write-Host "  LEARNING LOOP (v2.2):"
    foreach ($r in $LearningResults) {
        $icon = switch ($r.verdict) {
            "PASS" { "[OK]" }
            "FAIL" { "[XX]" }
            "PARTIAL" { "[~~]" }
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
    version = "2.2"
    action = "full_run"
    started_at_utc = $StartTime
    finished_at_utc = $EndTime
    overall_verdict = $OverallVerdict
    results = $Results
    dashboard_path = "IMPERIUM_TEST_VERSION/SANCTUM_MIRROR/master_dashboard.html"
    components = @{
        core = @("smoke_test", "script_health", "audit")
        new = @("second_brain", "live_workbench", "agent_handshake")
        dashboard = @("legacy_index", "master_dashboard", "organ_dashboards")
        registry = @("auto_sync")
        learning = @("lesson_extractor", "anti_pattern_scanner", "rule_extractor")
    }
}

$ReceiptPath = "$TestVersionRoot\RECEIPTS\RCP-MASTER-$Timestamp.json"
$MasterReceipt | ConvertTo-Json -Depth 5 | Out-File -FilePath $ReceiptPath -Encoding UTF8

Write-Host "Master receipt: $ReceiptPath"
Write-Host ""
Write-Host "Open dashboard: start $TestVersionRoot\SANCTUM_MIRROR\index.html"

if ($OverallVerdict -eq "PASS") { exit 0 } else { exit 1 }
