# DELTA WINDOW - RUN DELTA CHECK
# Main entry point for Delta Window MVP
#
# Usage:
#   cd E:\IMPERIUM\IMPERIUM_TEST_VERSION
#   .\TESTING_FIELD\DELTA_WINDOW\run_delta_check.ps1

param(
    [string]$Mode = "precommit",
    [string]$OldCommit = "",
    [string]$NewCommit = ""
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
Write-Host "DELTA WINDOW - RUN DELTA CHECK"
Write-Host "=" * 60
Write-Host "Mode: $Mode"
Write-Host "Test Version: $TestVersionRoot"
Write-Host "Repo Root: $RepoRoot"
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
$SnapshotResult = py -3 "$ScriptDir\snapshot_collector.py" --test-version $TestVersionRoot --repo-root $RepoRoot 2>&1
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
    "--mode", $Mode,
    "--test-version", $TestVersionRoot,
    "--repo-root", $RepoRoot
)

if ($Mode -eq "historical" -and $OldCommit -and $NewCommit) {
    $DeltaArgs += "--old-commit", $OldCommit, "--new-commit", $NewCommit
}

$DeltaResult = py -3 @DeltaArgs 2>&1
$DeltaExitCode = $LASTEXITCODE
Log-Command "delta_analyzer.py" ($DeltaResult -join "`n") $DeltaExitCode

Write-Host ($DeltaResult | Out-String)

# STAGE 3: Screenshot Collector (optional)
Write-Host ""
Write-Host "[STAGE 3] Collecting screenshots..."
$ScreenshotResult = py -3 "$ScriptDir\dashboard_screenshot_collector.py" --test-version $TestVersionRoot 2>&1
$ScreenshotExitCode = $LASTEXITCODE
Log-Command "dashboard_screenshot_collector.py" ($ScreenshotResult -join "`n") $ScreenshotExitCode

Write-Host ($ScreenshotResult | Out-String)

# STAGE 4: Generate HTML
Write-Host ""
Write-Host "[STAGE 4] Generating Delta Window HTML..."
$HtmlResult = py -3 "$ScriptDir\generate_delta_window.py" --test-version $TestVersionRoot 2>&1
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
    mode = $Mode
    test_version_root = $TestVersionRoot
    repo_root = $RepoRoot
    git_head = $GitHead
    stages = @{
        source_lock = @{ status = "PASS"; git_head = $GitHead }
        snapshot = @{ status = if ($SnapshotExitCode -eq 0) { "PASS" } else { "PARTIAL" }; exit_code = $SnapshotExitCode }
        delta_analyzer = @{ status = if ($DeltaExitCode -eq 0) { "PASS" } else { "PARTIAL" }; exit_code = $DeltaExitCode }
        screenshots = @{ status = if ($ScreenshotExitCode -eq 0) { "PASS" } else { "PARTIAL" }; exit_code = $ScreenshotExitCode }
        html_generator = @{ status = if ($HtmlExitCode -eq 0) { "PASS" } else { "FAIL" }; exit_code = $HtmlExitCode }
    }
    overall_verdict = if ($HtmlExitCode -eq 0) { "PASS" } else { "FAIL" }
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
    mode = $Mode
    verdict = $Verdict
    safe_to_commit = ($Verdict -eq "COMMIT_OK")
    delta_report_path = $DeltaReportPath
    html_path = (Join-Path $ScriptDir "delta_window.html")
} | ConvertTo-Json | Out-File -FilePath $PrecommitVerdictPath -Encoding UTF8

# Final output
$HtmlPath = Join-Path $ScriptDir "delta_window.html"

Write-Host ""
Write-Host "=" * 60
Write-Host "DELTA WINDOW COMPLETE"
Write-Host "=" * 60
Write-Host ""
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
