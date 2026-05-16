# DELTA WINDOW - RUN DELTA CHECK R2
# Main entry point for Delta Window with metric modes
#
# Usage:
#   cd E:\IMPERIUM\IMPERIUM_TEST_VERSION
#   .\TESTING_FIELD\DELTA_WINDOW\run_delta_check.ps1 -Mode QUICK
#   .\TESTING_FIELD\DELTA_WINDOW\run_delta_check.ps1 -Mode STANDARD
#   .\TESTING_FIELD\DELTA_WINDOW\run_delta_check.ps1 -Mode FULL
#   .\TESTING_FIELD\DELTA_WINDOW\run_delta_check.ps1 -Mode CUSTOM -Include "git,files,dashboards"
#   .\TESTING_FIELD\DELTA_WINDOW\run_delta_check.ps1 -CompareMode historical -OldCommit <sha> -NewCommit <sha>
#
# Metric Modes:
#   QUICK    - git status, file diff, key reports (fastest)
#   STANDARD - QUICK + dashboard list, link check, truth summary, agent exchange
#   FULL     - STANDARD + screenshots, repo scan, mojibake scan, generated artifacts
#   CUSTOM   - select components via -Include flag

param(
    [ValidateSet("QUICK", "STANDARD", "FULL", "CUSTOM")]
    [string]$Mode = "STANDARD",
    
    [ValidateSet("precommit", "historical")]
    [string]$CompareMode = "precommit",
    
    [string]$OldCommit = "",
    [string]$NewCommit = "",
    
    [string]$Include = "git,files,truth,dashboards,agent_exchange"
)

# Set encoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

$ErrorActionPreference = "Stop"

# Paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TestVersionRoot = (Get-Item $ScriptDir).Parent.Parent.FullName
$RepoRoot = (Get-Item $TestVersionRoot).Parent.FullName
$ReportsDir = Join-Path $ScriptDir "REPORTS"
$SnapshotsDir = Join-Path $ScriptDir "SNAPSHOTS"
$ScreenshotsDir = Join-Path $ScriptDir "SCREENSHOTS"

# Ensure directories exist
New-Item -ItemType Directory -Force -Path $ReportsDir | Out-Null
New-Item -ItemType Directory -Force -Path $SnapshotsDir | Out-Null
New-Item -ItemType Directory -Force -Path $ScreenshotsDir | Out-Null

# Command log
$CommandLog = @()
$StartTime = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"

function Log-Command {
    param([string]$Command, [string]$Result, [int]$ExitCode)
    $script:CommandLog += @{
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
        command = $Command
        result = $Result
        exit_code = $ExitCode
    }
}

Write-Host "=" * 60
Write-Host "DELTA WINDOW R2 - RUN DELTA CHECK"
Write-Host "=" * 60
Write-Host "Metric Mode: $Mode"
Write-Host "Compare Mode: $CompareMode"
if ($Mode -eq "CUSTOM") {
    Write-Host "Include: $Include"
}
Write-Host "Test Version: $TestVersionRoot"
Write-Host "Repo Root: $RepoRoot"
Write-Host ""

# Parse include components for CUSTOM mode
$Components = @{
    git = $true
    files = $true
    truth = $true
    dashboards = $false
    screenshots = $false
    agent_exchange = $false
    mojibake = $false
    generated_artifacts = $false
    repo_scan = $false
}

switch ($Mode) {
    "QUICK" {
        # Minimal: git, files, key reports
        $Components.git = $true
        $Components.files = $true
        $Components.truth = $true
    }
    "STANDARD" {
        # QUICK + dashboards, agent exchange
        $Components.git = $true
        $Components.files = $true
        $Components.truth = $true
        $Components.dashboards = $true
        $Components.agent_exchange = $true
    }
    "FULL" {
        # Everything
        $Components.git = $true
        $Components.files = $true
        $Components.truth = $true
        $Components.dashboards = $true
        $Components.screenshots = $true
        $Components.agent_exchange = $true
        $Components.mojibake = $true
        $Components.generated_artifacts = $true
        $Components.repo_scan = $true
    }
    "CUSTOM" {
        # Parse -Include flag
        $IncludeList = $Include -split ","
        foreach ($key in $Components.Keys) {
            $Components[$key] = $IncludeList -contains $key
        }
    }
}

Write-Host "Components enabled:"
foreach ($key in $Components.Keys) {
    if ($Components[$key]) {
        Write-Host "  [x] $key"
    } else {
        Write-Host "  [ ] $key"
    }
}
Write-Host ""

# STAGE 0: Source Lock
Write-Host "[STAGE 0] Source Lock..."
$GitHead = git -C $RepoRoot rev-parse HEAD 2>&1
$GitStatus = git -C $RepoRoot status --short 2>&1
$GitLog = git -C $RepoRoot log -1 --oneline 2>&1

Log-Command "git rev-parse HEAD" $GitHead $LASTEXITCODE
Log-Command "git status --short" ($GitStatus -join "`n") $LASTEXITCODE

Write-Host "  HEAD: $GitHead"
Write-Host "  Status: $(if ($GitStatus) { 'DIRTY' } else { 'CLEAN' })"

# STAGE 1: Snapshot Collector
Write-Host ""
Write-Host "[STAGE 1] Collecting snapshot..."
$SnapshotResult = py -3.12 "$ScriptDir\snapshot_collector.py" --test-version $TestVersionRoot --repo-root $RepoRoot 2>&1
$SnapshotExitCode = $LASTEXITCODE
Log-Command "snapshot_collector.py" ($SnapshotResult -join "`n") $SnapshotExitCode

if ($SnapshotExitCode -ne 0) {
    Write-Host "  WARNING: Snapshot collector returned non-zero exit code"
}
Write-Host "  Snapshot collected"

# STAGE 2: Delta Analyzer
Write-Host ""
Write-Host "[STAGE 2] Analyzing delta..."

$DeltaArgs = @(
    "$ScriptDir\delta_analyzer.py",
    "--mode", $CompareMode,
    "--test-version", $TestVersionRoot,
    "--repo-root", $RepoRoot
)

if ($CompareMode -eq "historical" -and $OldCommit -and $NewCommit) {
    $DeltaArgs += "--old-commit", $OldCommit, "--new-commit", $NewCommit
}

$DeltaResult = py -3.12 @DeltaArgs 2>&1
$DeltaExitCode = $LASTEXITCODE
Log-Command "delta_analyzer.py" ($DeltaResult -join "`n") $DeltaExitCode

Write-Host ($DeltaResult | Out-String)

# STAGE 3: Screenshot Collector (conditional)
$ScreenshotExitCode = 0
if ($Components.screenshots) {
    Write-Host ""
    Write-Host "[STAGE 3] Collecting screenshots..."
    $ScreenshotResult = py -3.12 "$ScriptDir\dashboard_screenshot_collector.py" --test-version $TestVersionRoot 2>&1
    $ScreenshotExitCode = $LASTEXITCODE
    Log-Command "dashboard_screenshot_collector.py" ($ScreenshotResult -join "`n") $ScreenshotExitCode
    Write-Host ($ScreenshotResult | Out-String)
} else {
    Write-Host ""
    Write-Host "[STAGE 3] Screenshots SKIPPED (Mode: $Mode)"
    Log-Command "screenshots" "SKIPPED" 0
}

# STAGE 3b: Mojibake Scan (conditional)
$MojibakeExitCode = 0
if ($Components.mojibake) {
    Write-Host ""
    Write-Host "[STAGE 3b] Running mojibake scan..."
    $MojibakeResult = py -3.12 "$TestVersionRoot\AGENT_EXCHANGE\TOOLS\mojibake_scan.py" --scope IMPERIUM_TEST_VERSION --root $TestVersionRoot 2>&1
    $MojibakeExitCode = $LASTEXITCODE
    Log-Command "mojibake_scan.py" ($MojibakeResult -join "`n") $MojibakeExitCode
    Write-Host ($MojibakeResult | Out-String)
} else {
    Write-Host ""
    Write-Host "[STAGE 3b] Mojibake scan SKIPPED (Mode: $Mode)"
}

# STAGE 3c: Candidate Model
Write-Host ""
Write-Host "[STAGE 3c] Building candidate model..."
$CandidateResult = py -3.12 "$ScriptDir\candidate_model.py" --repo-root $RepoRoot --scope $TestVersionRoot 2>&1
$CandidateExitCode = $LASTEXITCODE
Log-Command "candidate_model.py" ($CandidateResult -join "`n") $CandidateExitCode
Write-Host ($CandidateResult | Out-String)

# STAGE 4: Generate HTML
Write-Host ""
Write-Host "[STAGE 4] Generating Delta Window HTML..."
$HtmlResult = py -3.12 "$ScriptDir\generate_delta_window.py" --test-version $TestVersionRoot 2>&1
$HtmlExitCode = $LASTEXITCODE
Log-Command "generate_delta_window.py" ($HtmlResult -join "`n") $HtmlExitCode

Write-Host ($HtmlResult | Out-String)

# STAGE 5: Write command log
Write-Host ""
Write-Host "[STAGE 5] Writing reports..."

$CommandLogPath = Join-Path $ReportsDir "command_log.md"
$CommandLogContent = @"
# Delta Window Command Log

Generated: $StartTime
Mode: $Mode
Test Version: $TestVersionRoot

## Commands Executed

"@

foreach ($cmd in $CommandLog) {
    $CommandLogContent += @"

### $($cmd.timestamp)
``````
$($cmd.command)
``````
Exit Code: $($cmd.exit_code)

"@
}

$CommandLogContent | Out-File -FilePath $CommandLogPath -Encoding UTF8

# Write run receipt
$RunReceipt = @{
    receipt_id = "RCP-DELTA-$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    started_at = $StartTime
    finished_at = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
    metric_mode = $Mode
    compare_mode = $CompareMode
    components_enabled = $Components
    test_version_root = $TestVersionRoot
    repo_root = $RepoRoot
    git_head = $GitHead
    stages = @{
        source_lock = @{ status = "PASS"; git_head = $GitHead }
        snapshot = @{ status = if ($SnapshotExitCode -eq 0) { "PASS" } else { "PARTIAL" }; exit_code = $SnapshotExitCode }
        delta_analyzer = @{ status = if ($DeltaExitCode -eq 0) { "PASS" } else { "PARTIAL" }; exit_code = $DeltaExitCode }
        candidate_model = @{ status = if ($CandidateExitCode -eq 0) { "PASS" } else { "PARTIAL" }; exit_code = $CandidateExitCode }
        screenshots = @{ status = if (-not $Components.screenshots) { "SKIPPED" } elseif ($ScreenshotExitCode -eq 0) { "PASS" } else { "PARTIAL" }; exit_code = $ScreenshotExitCode }
        mojibake = @{ status = if (-not $Components.mojibake) { "SKIPPED" } elseif ($MojibakeExitCode -eq 0) { "PASS" } else { "PARTIAL" }; exit_code = $MojibakeExitCode }
        html_generator = @{ status = if ($HtmlExitCode -eq 0) { "PASS" } else { "FAIL" }; exit_code = $HtmlExitCode }
    }
    overall_verdict = $Verdict
}

$RunReceiptPath = Join-Path $ReportsDir "run_receipt.json"
$RunReceipt | ConvertTo-Json -Depth 10 | Out-File -FilePath $RunReceiptPath -Encoding UTF8

# Read verdict from delta report
$DeltaReportPath = Join-Path $ReportsDir "latest_delta_report.json"
$Verdict = "UNKNOWN"
if (Test-Path $DeltaReportPath) {
    $DeltaReport = Get-Content $DeltaReportPath -Raw | ConvertFrom-Json
    $Verdict = $DeltaReport.precommit_verdict.verdict
}

# Write precommit verdict
$PrecommitVerdictPath = Join-Path $ReportsDir "latest_precommit_verdict.json"
@{
    generated_at = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssK")
    metric_mode = $Mode
    compare_mode = $CompareMode
    verdict = $Verdict
    safe_to_commit = ($Verdict -eq "COMMIT_OK")
    delta_report_path = $DeltaReportPath
    html_path = (Join-Path $ScriptDir "delta_window.html")
} | ConvertTo-Json | Out-File -FilePath $PrecommitVerdictPath -Encoding UTF8

# Final output
$HtmlPath = Join-Path $ScriptDir "delta_window.html"

Write-Host ""
Write-Host "=" * 60
Write-Host "DELTA WINDOW R2 COMPLETE"
Write-Host "=" * 60
Write-Host ""
Write-Host "METRIC MODE: $Mode"
Write-Host "COMPARE MODE: $CompareMode"
Write-Host "VERDICT: $Verdict"
Write-Host ""
Write-Host "Delta Window HTML:"
Write-Host "  $HtmlPath"
Write-Host ""
Write-Host "Reports:"
Write-Host "  $DeltaReportPath"
Write-Host "  $CommandLogPath"
Write-Host "  $RunReceiptPath"
Write-Host ""

# Exit code based on verdict
if ($Verdict -eq "COMMIT_OK") {
    exit 0
} else {
    exit 1
}
