# RUN_SMOKE.ps1
# Testing Field Smoke Test - Creates report and receipt
# Usage: .\IMPERIUM_TEST_VERSION\TESTING_FIELD\RUN_SMOKE.ps1

$ErrorActionPreference = "Continue"

# Paths
$TestVersionRoot = "E:\IMPERIUM\IMPERIUM_TEST_VERSION"
$RepoRoot = "E:\IMPERIUM"
$ReportsDir = "$TestVersionRoot\TESTING_FIELD\SMOKE_RESULTS"
$ReceiptsDir = "$TestVersionRoot\RECEIPTS"

# Ensure directories exist
New-Item -ItemType Directory -Force -Path $ReportsDir | Out-Null
New-Item -ItemType Directory -Force -Path $ReceiptsDir | Out-Null

$StartTime = Get-Date -Format "o"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

Write-Host "=" * 60
Write-Host "TESTING FIELD SMOKE TEST"
Write-Host "=" * 60
Write-Host "Repo: $RepoRoot"
Write-Host "Started: $StartTime"
Write-Host ""

$Checks = @()
$PassCount = 0
$FailCount = 0

# Check 1: Sanctum script exists
Write-Host "[1/5] Checking Sanctum script exists..."
$SanctumPath = "$RepoRoot\SANCTUM\sanctum_v0_29_qt.py"
$SanctumExists = Test-Path $SanctumPath
$Checks += @{
    name = "sanctum_exists"
    description = "Sanctum main script exists"
    path = "SANCTUM/sanctum_v0_29_qt.py"
    passed = $SanctumExists
    error = if (-not $SanctumExists) { "File not found" } else { $null }
}
if ($SanctumExists) { $PassCount++ } else { $FailCount++ }
Write-Host "  $(if ($SanctumExists) {'PASS'} else {'FAIL'}): Sanctum script"

# Check 2: Sanctum syntax valid
Write-Host "[2/5] Checking Sanctum syntax..."
$SyntaxOk = $false
$SyntaxError = $null
if ($SanctumExists) {
    try {
        $result = py -3 -m py_compile $SanctumPath 2>&1
        if ($LASTEXITCODE -eq 0) {
            $SyntaxOk = $true
        } else {
            $SyntaxError = $result -join " "
        }
    } catch {
        $SyntaxError = $_.Exception.Message
    }
}
$Checks += @{
    name = "sanctum_syntax"
    description = "Sanctum script has valid Python syntax"
    passed = $SyntaxOk
    error = $SyntaxError
}
if ($SyntaxOk) { $PassCount++ } else { $FailCount++ }
Write-Host "  $(if ($SyntaxOk) {'PASS'} else {'FAIL'}): Sanctum syntax"

# Check 3: PyQt6 importable
Write-Host "[3/5] Checking PyQt6 import..."
$PyQt6Ok = $false
$PyQt6Error = $null
try {
    $result = py -3 -c "import PyQt6; print('OK')" 2>&1
    if ($result -match "OK") {
        $PyQt6Ok = $true
    } else {
        $PyQt6Error = $result -join " "
    }
} catch {
    $PyQt6Error = $_.Exception.Message
}
$Checks += @{
    name = "pyqt6_import"
    description = "PyQt6 can be imported"
    passed = $PyQt6Ok
    error = $PyQt6Error
}
if ($PyQt6Ok) { $PassCount++ } else { $FailCount++ }
Write-Host "  $(if ($PyQt6Ok) {'PASS'} else {'FAIL'}): PyQt6 import"

# Check 4: AGENTS.md exists
Write-Host "[4/5] Checking AGENTS.md exists..."
$AgentsExists = Test-Path "$RepoRoot\AGENTS.md"
$Checks += @{
    name = "agents_md_exists"
    description = "AGENTS.md workspace rules file exists"
    path = "AGENTS.md"
    passed = $AgentsExists
    error = if (-not $AgentsExists) { "File not found" } else { $null }
}
if ($AgentsExists) { $PassCount++ } else { $FailCount++ }
Write-Host "  $(if ($AgentsExists) {'PASS'} else {'FAIL'}): AGENTS.md"

# Check 5: Git status
Write-Host "[5/5] Checking git status..."
$GitClean = $false
$GitHead = "unknown"
try {
    Push-Location $RepoRoot
    $status = git status --short 2>&1
    $GitClean = [string]::IsNullOrWhiteSpace($status) -or ($status -match "^\s*M\s+\.gitignore\s*$") -or ($status -match "^\?\?\s+\.vscode")
    $GitHead = (git rev-parse --short HEAD 2>&1)
    Pop-Location
} catch {
    Pop-Location
}
$Checks += @{
    name = "git_status"
    description = "Git working directory is clean (or only .gitignore/.vscode modified)"
    passed = $GitClean
    git_head = $GitHead
    error = if (-not $GitClean) { "Uncommitted changes" } else { $null }
}
if ($GitClean) { $PassCount++ } else { $FailCount++ }
Write-Host "  $(if ($GitClean) {'PASS'} else {'FAIL'}): Git clean (HEAD: $GitHead)"

$TotalChecks = $Checks.Count
$EndTime = Get-Date -Format "o"

# Determine verdict
$Verdict = "PASS"
if ($FailCount -gt 0) {
    $Verdict = if ($PassCount -gt 0) { "PARTIAL" } else { "FAIL" }
}

# Build report
$Report = @{
    schema_version = "IMPERIUM_SMOKE_V0_1"
    generated_at = $EndTime
    repo_root = $RepoRoot
    summary = @{
        total_checks = $TotalChecks
        passed = $PassCount
        failed = $FailCount
        pass_percent = [math]::Round(($PassCount / $TotalChecks) * 100, 1)
        verdict = $Verdict
        git_head = $GitHead
    }
    checks = $Checks
}

# Save report
$ReportPath = "$ReportsDir\latest_smoke_report.json"
$Report | ConvertTo-Json -Depth 10 | Out-File -FilePath $ReportPath -Encoding UTF8

# Build receipt
$Receipt = @{
    receipt_id = "RCP-SMOKE-$Timestamp"
    action = "smoke_test"
    started_at_utc = $StartTime
    finished_at_utc = $EndTime
    exit_code = if ($Verdict -eq "PASS") { 0 } else { 1 }
    verdict = $Verdict
    command = "RUN_SMOKE.ps1"
    repo_root = $RepoRoot
    test_version_root = $TestVersionRoot
    report_path = "IMPERIUM_TEST_VERSION/TESTING_FIELD/SMOKE_RESULTS/latest_smoke_report.json"
    evidence_paths = @("IMPERIUM_TEST_VERSION/TESTING_FIELD/SMOKE_RESULTS/latest_smoke_report.json")
    errors = @()
    warnings = @()
}

$ReceiptPath = "$ReceiptsDir\RCP-SMOKE-$Timestamp.json"
$Receipt | ConvertTo-Json -Depth 5 | Out-File -FilePath $ReceiptPath -Encoding UTF8

# Output
Write-Host ""
Write-Host "RESULTS:"
Write-Host "  Total checks: $TotalChecks"
Write-Host "  Passed: $PassCount"
Write-Host "  Failed: $FailCount"
Write-Host "  Pass rate: $([math]::Round(($PassCount / $TotalChecks) * 100, 1))%"
Write-Host ""
Write-Host "VERDICT: $Verdict"
Write-Host ""
Write-Host "Report: $ReportPath"
Write-Host "Receipt: $ReceiptPath"

if ($Verdict -eq "PASS") { exit 0 } else { exit 1 }
