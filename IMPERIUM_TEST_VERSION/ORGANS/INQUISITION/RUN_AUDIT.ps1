# RUN_AUDIT.ps1
# Inquisition Full Audit - Creates report and receipt
# Usage: .\IMPERIUM_TEST_VERSION\ORGANS\INQUISITION\RUN_AUDIT.ps1

$ErrorActionPreference = "Continue"

# Paths
$TestVersionRoot = "E:\IMPERIUM\IMPERIUM_TEST_VERSION"
$RepoRoot = $TestVersionRoot  # Scan only test version, not main repo
$ReportsDir = "$TestVersionRoot\ORGANS\INQUISITION\REPORTS"
$ReceiptsDir = "$TestVersionRoot\RECEIPTS"
$DashboardDir = "$TestVersionRoot\ORGANS\INQUISITION\DASHBOARD"

# Ensure directories exist
New-Item -ItemType Directory -Force -Path $ReportsDir | Out-Null
New-Item -ItemType Directory -Force -Path $ReceiptsDir | Out-Null
New-Item -ItemType Directory -Force -Path $DashboardDir | Out-Null

$StartTime = Get-Date -Format "o"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

Write-Host "=" * 60
Write-Host "INQUISITION FULL AUDIT"
Write-Host "=" * 60
Write-Host "Repo: $RepoRoot"
Write-Host "Started: $StartTime"
Write-Host ""

# Audit counters
$FakeGreenCount = 0
$StaleTruthCount = 0
$MissingEvidenceCount = 0
$TotalVerdictFiles = 0
$ScannedFiles = @()

# 1. Scan for verdict files (fake green detection)
Write-Host "[1/3] Scanning for verdict files..."
$VerdictFiles = Get-ChildItem -Path $RepoRoot -Recurse -Filter "*VERDICT*.json" -ErrorAction SilentlyContinue | 
    Where-Object { $_.FullName -notmatch "\.git" }

foreach ($vf in $VerdictFiles) {
    $TotalVerdictFiles++
    $relPath = $vf.FullName.Replace("$RepoRoot\", "").Replace("\", "/")
    
    try {
        $content = Get-Content $vf.FullName -Raw | ConvertFrom-Json
        
        # Check for PASS without evidence
        $verdict = $content.verdict
        if (-not $verdict) { $verdict = $content.status }
        if (-not $verdict) { $verdict = $content.passed }
        
        $hasEvidence = $false
        if ($content.evidence -or $content.evidence_path -or $content.report_path) {
            $hasEvidence = $true
        }
        
        $isPass = $false
        if ($verdict -eq $true -or $verdict -eq "PASS" -or $verdict -eq "SUCCESS" -or $verdict -eq "OK") {
            $isPass = $true
        }
        
        if ($isPass -and -not $hasEvidence) {
            $FakeGreenCount++
            $ScannedFiles += @{
                path = $relPath
                issue = "fake_green"
                detail = "PASS without evidence"
            }
        }
    } catch {
        # JSON parse error - skip
    }
}

# 2. Scan for stale truth (files older than 24h claiming current state)
Write-Host "[2/3] Scanning for stale truth..."
$StatusFiles = Get-ChildItem -Path $RepoRoot -Recurse -Filter "*STATUS*.json" -ErrorAction SilentlyContinue | 
    Where-Object { $_.FullName -notmatch "\.git" }

$Now = Get-Date
foreach ($sf in $StatusFiles) {
    $relPath = $sf.FullName.Replace("$RepoRoot\", "").Replace("\", "/")
    $age = ($Now - $sf.LastWriteTime).TotalHours
    
    if ($age -gt 24) {
        $StaleTruthCount++
        $ScannedFiles += @{
            path = $relPath
            issue = "stale_truth"
            detail = "File is $([math]::Round($age, 1)) hours old"
        }
    }
}

# 3. Check for missing evidence in reports
Write-Host "[3/3] Scanning for missing evidence..."
$ReportFiles = Get-ChildItem -Path $RepoRoot -Recurse -Filter "*_report*.json" -ErrorAction SilentlyContinue | 
    Where-Object { $_.FullName -notmatch "\.git" }

foreach ($rf in $ReportFiles) {
    $relPath = $rf.FullName.Replace("$RepoRoot\", "").Replace("\", "/")
    
    try {
        $content = Get-Content $rf.FullName -Raw | ConvertFrom-Json
        
        # Check if report claims evidence but path doesn't exist
        if ($content.evidence_path) {
            $evidencePath = Join-Path $RepoRoot $content.evidence_path
            if (-not (Test-Path $evidencePath)) {
                $MissingEvidenceCount++
                $ScannedFiles += @{
                    path = $relPath
                    issue = "missing_evidence"
                    detail = "Evidence path not found: $($content.evidence_path)"
                }
            }
        }
    } catch {
        # Skip parse errors
    }
}

$TotalScanned = $TotalVerdictFiles + $StatusFiles.Count + $ReportFiles.Count
$TotalIssues = $FakeGreenCount + $StaleTruthCount + $MissingEvidenceCount

$EndTime = Get-Date -Format "o"

# Determine verdict
$Verdict = "PASS"
if ($TotalScanned -eq 0) {
    $Verdict = "NO_DATA"
} elseif ($TotalIssues -gt 0) {
    $Verdict = "FAIL"
}

# Build report
$Report = @{
    schema_version = "IMPERIUM_AUDIT_V0_1"
    generated_at = $EndTime
    repo_root = $RepoRoot
    summary = @{
        total_scanned = $TotalScanned
        verdict_files = $TotalVerdictFiles
        status_files = $StatusFiles.Count
        report_files = $ReportFiles.Count
        fake_green_count = $FakeGreenCount
        stale_truth_count = $StaleTruthCount
        missing_evidence_count = $MissingEvidenceCount
        total_issues = $TotalIssues
        verdict = $Verdict
    }
    issues = $ScannedFiles
}

# Save report
$ReportPath = "$ReportsDir\latest_audit.json"
$Report | ConvertTo-Json -Depth 10 | Out-File -FilePath $ReportPath -Encoding UTF8

# Build receipt
$Receipt = @{
    receipt_id = "RCP-INQ-$Timestamp"
    action = "full_audit"
    started_at_utc = $StartTime
    finished_at_utc = $EndTime
    exit_code = if ($Verdict -eq "PASS") { 0 } else { 1 }
    verdict = $Verdict
    command = "RUN_AUDIT.ps1"
    repo_root = $RepoRoot
    test_version_root = $TestVersionRoot
    report_path = "IMPERIUM_TEST_VERSION/ORGANS/INQUISITION/REPORTS/latest_audit.json"
    evidence_paths = @("IMPERIUM_TEST_VERSION/ORGANS/INQUISITION/REPORTS/latest_audit.json")
    errors = @()
    warnings = @()
}

$ReceiptPath = "$ReceiptsDir\RCP-INQ-$Timestamp.json"
$Receipt | ConvertTo-Json -Depth 5 | Out-File -FilePath $ReceiptPath -Encoding UTF8

# Generate dashboard HTML
$VerdictClass = switch ($Verdict) {
    "PASS" { "pass" }
    "FAIL" { "fail" }
    default { "partial" }
}

$DashboardHtml = @"
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Inquisition Audit</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #1a1a2e; color: #ecf0f1; padding: 20px; }
        .header { text-align: center; border-bottom: 2px solid #d4af37; padding-bottom: 20px; margin-bottom: 20px; }
        .header h1 { color: #d4af37; }
        .card { background: #16213e; border-radius: 10px; padding: 20px; margin: 10px 0; }
        .metric { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #2c3e50; }
        .metric:last-child { border-bottom: none; }
        .value { font-size: 1.5em; font-weight: bold; }
        .pass { color: #27ae60; }
        .fail { color: #e74c3c; }
        .partial { color: #f39c12; }
        .timestamp { color: #7f8c8d; font-size: 0.9em; }
        .issue-list { background: #2c1810; padding: 15px; border-radius: 5px; margin-top: 10px; }
        .issue-item { padding: 8px 0; border-bottom: 1px solid #3c2820; }
        .issue-item:last-child { border-bottom: none; }
        .issue-type { color: #e74c3c; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>INQUISITION AUDIT</h1>
        <p class="timestamp">Generated: $EndTime</p>
    </div>
    
    <div class="card">
        <h2>Summary</h2>
        <div class="metric">
            <span>Verdict</span>
            <span class="value $VerdictClass">$Verdict</span>
        </div>
        <div class="metric">
            <span>Total Scanned</span>
            <span class="value">$TotalScanned</span>
        </div>
        <div class="metric">
            <span>Total Issues</span>
            <span class="value $(if ($TotalIssues -gt 0) {'fail'} else {'pass'})">$TotalIssues</span>
        </div>
    </div>
    
    <div class="card">
        <h2>Issue Breakdown</h2>
        <div class="metric">
            <span>Fake Green (PASS without evidence)</span>
            <span class="value $(if ($FakeGreenCount -gt 0) {'fail'} else {'pass'})">$FakeGreenCount</span>
        </div>
        <div class="metric">
            <span>Stale Truth (>24h old)</span>
            <span class="value $(if ($StaleTruthCount -gt 0) {'fail'} else {'pass'})">$StaleTruthCount</span>
        </div>
        <div class="metric">
            <span>Missing Evidence</span>
            <span class="value $(if ($MissingEvidenceCount -gt 0) {'fail'} else {'pass'})">$MissingEvidenceCount</span>
        </div>
    </div>
"@

if ($ScannedFiles.Count -gt 0) {
    $DashboardHtml += @"
    
    <div class="card">
        <h2>Issues Found</h2>
        <div class="issue-list">
"@
    foreach ($issue in $ScannedFiles | Select-Object -First 20) {
        $DashboardHtml += "            <div class='issue-item'><span class='issue-type'>[$($issue.issue)]</span> $($issue.path)<br><small>$($issue.detail)</small></div>`n"
    }
    if ($ScannedFiles.Count -gt 20) {
        $DashboardHtml += "            <div class='issue-item'><em>... and $($ScannedFiles.Count - 20) more issues</em></div>`n"
    }
    $DashboardHtml += @"
        </div>
    </div>
"@
}

$DashboardHtml += @"
    
    <div class="card">
        <h2>Files</h2>
        <p>Report: <code>ORGANS/INQUISITION/REPORTS/latest_audit.json</code></p>
        <p>Receipt: <code>RECEIPTS/RCP-INQ-$Timestamp.json</code></p>
    </div>
    
    <div class="card">
        <h2>Refresh</h2>
        <p>Run: <code>.\IMPERIUM_TEST_VERSION\ORGANS\INQUISITION\RUN_AUDIT.ps1</code></p>
        <p>Then reload this page.</p>
    </div>
</body>
</html>
"@

$DashboardHtml | Out-File -FilePath "$DashboardDir\index.html" -Encoding UTF8

# Output
Write-Host ""
Write-Host "RESULTS:"
Write-Host "  Total scanned: $TotalScanned"
Write-Host "  Fake green: $FakeGreenCount"
Write-Host "  Stale truth: $StaleTruthCount"
Write-Host "  Missing evidence: $MissingEvidenceCount"
Write-Host "  Total issues: $TotalIssues"
Write-Host ""
Write-Host "VERDICT: $Verdict"
Write-Host ""
Write-Host "Report: $ReportPath"
Write-Host "Receipt: $ReceiptPath"
Write-Host "Dashboard: $DashboardDir\index.html"
Write-Host ""
Write-Host "Open dashboard: start $DashboardDir\index.html"

if ($Verdict -eq "PASS") { exit 0 } else { exit 1 }
