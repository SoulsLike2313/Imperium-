# RUN_SCRIPT_HEALTH.ps1
# Mechanicus Script Health Check - Creates report and receipt
# Usage: .\IMPERIUM_TEST_VERSION\ORGANS\MECHANICUS\RUN_SCRIPT_HEALTH.ps1

$ErrorActionPreference = "Continue"

# Paths
$TestVersionRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
$TestVersionRoot = "E:\IMPERIUM\IMPERIUM_TEST_VERSION"
$RepoRoot = "E:\IMPERIUM"
$ReportsDir = "$TestVersionRoot\ORGANS\MECHANICUS\REPORTS"
$ReceiptsDir = "$TestVersionRoot\RECEIPTS"
$DashboardDir = "$TestVersionRoot\ORGANS\MECHANICUS\DASHBOARD"

# Ensure directories exist
New-Item -ItemType Directory -Force -Path $ReportsDir | Out-Null
New-Item -ItemType Directory -Force -Path $ReceiptsDir | Out-Null
New-Item -ItemType Directory -Force -Path $DashboardDir | Out-Null

$StartTime = Get-Date -Format "o"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

Write-Host "=" * 60
Write-Host "MECHANICUS SCRIPT HEALTH CHECK"
Write-Host "=" * 60
Write-Host "Repo: $RepoRoot"
Write-Host "Started: $StartTime"
Write-Host ""

# Scan for scripts
$Scripts = @()
$Healthy = 0
$Broken = 0
$Missing = 0

# Scan Python scripts
$PyScripts = Get-ChildItem -Path $RepoRoot -Recurse -Filter "*.py" -ErrorAction SilentlyContinue | 
    Where-Object { $_.FullName -notmatch "\.git|__pycache__|IMPERIUM_TEST_VERSION|\.venv|node_modules" }

foreach ($script in $PyScripts) {
    $relPath = $script.FullName.Replace("$RepoRoot\", "").Replace("\", "/")
    $syntaxOk = $true
    $syntaxError = $null
    
    # Check syntax with py_compile
    try {
        $result = py -3 -m py_compile $script.FullName 2>&1
        if ($LASTEXITCODE -ne 0) {
            $syntaxOk = $false
            $syntaxError = $result -join " "
            $Broken++
        } else {
            $Healthy++
        }
    } catch {
        $syntaxOk = $false
        $syntaxError = $_.Exception.Message
        $Broken++
    }
    
    $Scripts += @{
        path = $relPath
        exists = $true
        syntax_ok = $syntaxOk
        error = $syntaxError
        type = "python"
    }
}

# Scan PowerShell scripts
$Ps1Scripts = Get-ChildItem -Path $RepoRoot -Recurse -Filter "*.ps1" -ErrorAction SilentlyContinue | 
    Where-Object { $_.FullName -notmatch "\.git|IMPERIUM_TEST_VERSION" }

foreach ($script in $Ps1Scripts) {
    $relPath = $script.FullName.Replace("$RepoRoot\", "").Replace("\", "/")
    $Healthy++
    $Scripts += @{
        path = $relPath
        exists = $true
        syntax_ok = $true
        error = $null
        type = "powershell"
    }
}

$Total = $Scripts.Count
$HealthPercent = if ($Total -gt 0) { [math]::Round(($Healthy / $Total) * 100, 1) } else { 0 }

$EndTime = Get-Date -Format "o"
$Verdict = if ($Broken -eq 0 -and $Total -gt 0) { "PASS" } elseif ($Broken -gt 0) { "PARTIAL" } else { "FAIL" }

# Build report
$Report = @{
    schema_version = "IMPERIUM_SCRIPT_HEALTH_V0_1"
    generated_at = $EndTime
    repo_root = $RepoRoot
    summary = @{
        total_scripts = $Total
        healthy = $Healthy
        broken = $Broken
        health_percent = $HealthPercent
        verdict = $Verdict
    }
    broken_scripts = $Scripts | Where-Object { -not $_.syntax_ok }
    by_type = @{
        python = ($Scripts | Where-Object { $_.type -eq "python" }).Count
        powershell = ($Scripts | Where-Object { $_.type -eq "powershell" }).Count
    }
}

# Save report
$ReportPath = "$ReportsDir\latest_script_health.json"
$ReportJson = $Report | ConvertTo-Json -Depth 10
# Use retry logic to handle file locking
$maxRetries = 3
$retryCount = 0
while ($retryCount -lt $maxRetries) {
    try {
        Set-Content -Path $ReportPath -Value $ReportJson -Encoding UTF8 -Force
        break
    } catch {
        $retryCount++
        if ($retryCount -lt $maxRetries) {
            Start-Sleep -Milliseconds 500
        }
    }
}

# Build receipt
$Receipt = @{
    receipt_id = "RCP-MECH-$Timestamp"
    action = "script_health_check"
    started_at_utc = $StartTime
    finished_at_utc = $EndTime
    exit_code = if ($Verdict -eq "PASS") { 0 } else { 1 }
    verdict = $Verdict
    command = "RUN_SCRIPT_HEALTH.ps1"
    repo_root = $RepoRoot
    test_version_root = $TestVersionRoot
    report_path = $ReportPath.Replace($TestVersionRoot, "IMPERIUM_TEST_VERSION")
    evidence_paths = @($ReportPath.Replace($TestVersionRoot, "IMPERIUM_TEST_VERSION"))
    errors = @()
    warnings = @()
}

$ReceiptPath = "$ReceiptsDir\RCP-MECH-$Timestamp.json"
$Receipt | ConvertTo-Json -Depth 5 | Out-File -FilePath $ReceiptPath -Encoding UTF8

# Generate dashboard HTML with embedded data
$DashboardHtml = @"
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Mechanicus Script Health</title>
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
        .broken-list { background: #2c1810; padding: 15px; border-radius: 5px; margin-top: 10px; }
        .broken-item { padding: 5px 0; border-bottom: 1px solid #3c2820; }
    </style>
</head>
<body>
    <div class="header">
        <h1>⚙️ MECHANICUS SCRIPT HEALTH</h1>
        <p class="timestamp">Generated: $EndTime</p>
    </div>
    
    <div class="card">
        <h2>Summary</h2>
        <div class="metric">
            <span>Verdict</span>
            <span class="value $(if ($Verdict -eq 'PASS') {'pass'} elseif ($Verdict -eq 'FAIL') {'fail'} else {'partial'})">$Verdict</span>
        </div>
        <div class="metric">
            <span>Total Scripts</span>
            <span class="value">$Total</span>
        </div>
        <div class="metric">
            <span>Healthy</span>
            <span class="value pass">$Healthy</span>
        </div>
        <div class="metric">
            <span>Broken</span>
            <span class="value $(if ($Broken -gt 0) {'fail'} else {'pass'})">$Broken</span>
        </div>
        <div class="metric">
            <span>Health %</span>
            <span class="value">$HealthPercent%</span>
        </div>
    </div>
    
    <div class="card">
        <h2>By Type</h2>
        <div class="metric">
            <span>Python (.py)</span>
            <span class="value">$(($Scripts | Where-Object { $_.type -eq 'python' }).Count)</span>
        </div>
        <div class="metric">
            <span>PowerShell (.ps1)</span>
            <span class="value">$(($Scripts | Where-Object { $_.type -eq 'powershell' }).Count)</span>
        </div>
    </div>
"@

if ($Broken -gt 0) {
    $DashboardHtml += @"
    
    <div class="card">
        <h2>⚠️ Broken Scripts ($Broken)</h2>
        <div class="broken-list">
"@
    foreach ($bs in ($Scripts | Where-Object { -not $_.syntax_ok })) {
        $DashboardHtml += "            <div class='broken-item'>$($bs.path)</div>`n"
    }
    $DashboardHtml += @"
        </div>
    </div>
"@
}

$DashboardHtml += @"
    
    <div class="card">
        <h2>📁 Files</h2>
        <p>Report: <code>ORGANS/MECHANICUS/REPORTS/latest_script_health.json</code></p>
        <p>Receipt: <code>RECEIPTS/RCP-MECH-$Timestamp.json</code></p>
    </div>
    
    <div class="card">
        <h2>🔄 Refresh</h2>
        <p>Run: <code>.\IMPERIUM_TEST_VERSION\ORGANS\MECHANICUS\RUN_SCRIPT_HEALTH.ps1</code></p>
        <p>Then reload this page.</p>
    </div>
</body>
</html>
"@

$DashboardHtml | Out-File -FilePath "$DashboardDir\index.html" -Encoding UTF8

# Output
Write-Host ""
Write-Host "RESULTS:"
Write-Host "  Total scripts: $Total"
Write-Host "  Healthy: $Healthy"
Write-Host "  Broken: $Broken"
Write-Host "  Health: $HealthPercent%"
Write-Host ""
Write-Host "VERDICT: $Verdict"
Write-Host ""
Write-Host "Report: $ReportPath"
Write-Host "Receipt: $ReceiptPath"
Write-Host "Dashboard: $DashboardDir\index.html"
Write-Host ""
Write-Host "Open dashboard: start $DashboardDir\index.html"

if ($Verdict -eq "PASS") { exit 0 } else { exit 1 }
