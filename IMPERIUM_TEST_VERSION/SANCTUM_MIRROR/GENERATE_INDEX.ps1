# GENERATE_INDEX.ps1
# Generates Sanctum Mirror index.html from latest reports
# Usage: .\IMPERIUM_TEST_VERSION\SANCTUM_MIRROR\GENERATE_INDEX.ps1

$ErrorActionPreference = "Continue"

$TestVersionRoot = "E:\IMPERIUM\IMPERIUM_TEST_VERSION"
$OutputPath = "$TestVersionRoot\SANCTUM_MIRROR\index.html"

$Timestamp = Get-Date -Format "o"

Write-Host "Generating Sanctum Mirror index..."

# Load latest reports
$SmokeReport = $null
$MechReport = $null
$AuditReport = $null
$MemoryReport = $null
$WorkbenchReport = $null

$SmokePath = "$TestVersionRoot\TESTING_FIELD\SMOKE_RESULTS\latest_smoke_report.json"
$MechPath = "$TestVersionRoot\ORGANS\MECHANICUS\REPORTS\latest_script_health.json"
$AuditPath = "$TestVersionRoot\ORGANS\INQUISITION\REPORTS\latest_audit.json"
$MemoryPath = "$TestVersionRoot\SECOND_BRAIN\REPORTS\latest_memory_summary.json"
$WorkbenchPath = "$TestVersionRoot\LIVE_WORKBENCH\REPORTS\latest_workbench_status.json"
$HandshakePath = "$TestVersionRoot\AGENT_MEMORY_PROTOCOL\REPORTS\latest_handshake.json"

if (Test-Path $SmokePath) {
    $SmokeReport = Get-Content $SmokePath -Raw | ConvertFrom-Json
    Write-Host "  Loaded smoke report"
}
if (Test-Path $MechPath) {
    $MechReport = Get-Content $MechPath -Raw | ConvertFrom-Json
    Write-Host "  Loaded mechanicus report"
}
if (Test-Path $AuditPath) {
    $AuditReport = Get-Content $AuditPath -Raw | ConvertFrom-Json
    Write-Host "  Loaded audit report"
}
if (Test-Path $MemoryPath) {
    $MemoryReport = Get-Content $MemoryPath -Raw | ConvertFrom-Json
    Write-Host "  Loaded memory summary"
}
if (Test-Path $WorkbenchPath) {
    $WorkbenchReport = Get-Content $WorkbenchPath -Raw | ConvertFrom-Json
    Write-Host "  Loaded workbench status"
}
if (Test-Path $HandshakePath) {
    $HandshakeReport = Get-Content $HandshakePath -Raw | ConvertFrom-Json
    Write-Host "  Loaded handshake report"
}

# Helper function for verdict class
function Get-VerdictClass($verdict) {
    switch ($verdict) {
        "PASS" { return "pass" }
        "FAIL" { return "fail" }
        "PARTIAL" { return "partial" }
        "NO_DATA" { return "nodata" }
        "READY" { return "pass" }
        default { return "unknown" }
    }
}

# Extract data - Core Systems
$SmokeVerdict = if ($SmokeReport) { $SmokeReport.summary.verdict } else { "NO_DATA" }
$SmokePassed = if ($SmokeReport) { $SmokeReport.summary.passed } else { 0 }
$SmokeTotal = if ($SmokeReport) { $SmokeReport.summary.total_checks } else { 0 }
$SmokeTime = if ($SmokeReport) { $SmokeReport.generated_at } else { "N/A" }
$SmokeHead = if ($SmokeReport) { $SmokeReport.summary.git_head } else { "N/A" }

$MechVerdict = if ($MechReport) { $MechReport.summary.verdict } else { "NO_DATA" }
$MechHealthy = if ($MechReport) { $MechReport.summary.healthy } else { 0 }
$MechTotal = if ($MechReport) { $MechReport.summary.total_scripts } else { 0 }
$MechPercent = if ($MechReport) { $MechReport.summary.health_percent } else { 0 }
$MechTime = if ($MechReport) { $MechReport.generated_at } else { "N/A" }

$AuditVerdict = if ($AuditReport) { $AuditReport.summary.verdict } else { "NO_DATA" }
$AuditScanned = if ($AuditReport) { $AuditReport.summary.total_scanned } else { 0 }
$AuditIssues = if ($AuditReport) { $AuditReport.summary.total_issues } else { 0 }
$AuditFakeGreen = if ($AuditReport) { $AuditReport.summary.fake_green_count } else { 0 }
$AuditStale = if ($AuditReport) { $AuditReport.summary.stale_truth_count } else { 0 }
$AuditTime = if ($AuditReport) { $AuditReport.generated_at } else { "N/A" }

# Extract data - New Components
$MemoryVerdict = if ($MemoryReport) { $MemoryReport.verdict } else { "NO_DATA" }
$MemoryGoals = if ($MemoryReport) { $MemoryReport.goals_count } else { 0 }
$MemoryRules = if ($MemoryReport) { $MemoryReport.rules_count } else { 0 }
$MemoryErrors = if ($MemoryReport) { $MemoryReport.known_errors_count } else { 0 }
$MemoryTime = if ($MemoryReport) { $MemoryReport.generated_at } else { "N/A" }

$WorkbenchVerdict = if ($WorkbenchReport) { $WorkbenchReport.verdict } else { "NO_DATA" }
$WorkbenchTests = if ($WorkbenchReport) { $WorkbenchReport.tests_total } else { 0 }
$WorkbenchPassed = if ($WorkbenchReport) { $WorkbenchReport.tests_passed } else { 0 }
$WorkbenchFailed = if ($WorkbenchReport) { $WorkbenchReport.tests_failed } else { 0 }
$WorkbenchTime = if ($WorkbenchReport) { $WorkbenchReport.generated_at } else { "N/A" }

$HandshakeVerdict = if ($HandshakeReport) { $HandshakeReport.verdict } else { "NO_DATA" }
$HandshakeQueries = if ($HandshakeReport) { $HandshakeReport.queries_answered } else { 0 }
$HandshakeTime = if ($HandshakeReport) { $HandshakeReport.generated_at } else { "N/A" }

# Overall status
$OverallVerdict = "PASS"
if ($SmokeVerdict -eq "FAIL" -or $MechVerdict -eq "FAIL" -or $AuditVerdict -eq "FAIL") {
    $OverallVerdict = "FAIL"
} elseif ($SmokeVerdict -eq "PARTIAL" -or $MechVerdict -eq "PARTIAL" -or $AuditVerdict -eq "PARTIAL") {
    $OverallVerdict = "PARTIAL"
} elseif ($SmokeVerdict -eq "NO_DATA" -and $MechVerdict -eq "NO_DATA" -and $AuditVerdict -eq "NO_DATA") {
    $OverallVerdict = "NO_DATA"
}

$Html = @"
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IMPERIUM Test Version - Sanctum Mirror</title>
    <style>
        :root {
            --bg-dark: #1a1a2e;
            --bg-card: #16213e;
            --accent-gold: #d4af37;
            --accent-red: #e74c3c;
            --accent-green: #27ae60;
            --accent-yellow: #f39c12;
            --accent-blue: #3498db;
            --accent-purple: #9b59b6;
            --text-light: #ecf0f1;
            --text-muted: #95a5a6;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--bg-dark);
            color: var(--text-light);
            min-height: 100vh;
            padding: 20px;
        }
        .header {
            text-align: center;
            padding: 20px;
            border-bottom: 2px solid var(--accent-gold);
            margin-bottom: 30px;
        }
        .header h1 { color: var(--accent-gold); font-size: 2em; margin-bottom: 10px; }
        .header .subtitle { color: var(--text-muted); font-size: 0.9em; }
        .warning-banner {
            background: var(--accent-yellow);
            color: #000;
            padding: 10px 20px;
            text-align: center;
            font-weight: bold;
            margin-bottom: 20px;
            border-radius: 5px;
        }
        .overall-status {
            text-align: center;
            padding: 30px;
            margin-bottom: 30px;
            border-radius: 10px;
            background: var(--bg-card);
        }
        .overall-status h2 { font-size: 1.2em; margin-bottom: 15px; color: var(--text-muted); }
        .overall-status .verdict { font-size: 3em; font-weight: bold; }
        .overall-status .git-head { color: var(--text-muted); margin-top: 10px; }
        .section-title {
            color: var(--accent-gold);
            font-size: 1.3em;
            margin: 30px 0 20px 0;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--accent-gold);
            max-width: 1400px;
            margin-left: auto;
            margin-right: auto;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        .card {
            background: var(--bg-card);
            border-radius: 10px;
            padding: 20px;
            border-left: 4px solid var(--accent-gold);
        }
        .card.new-component { border-left-color: var(--accent-blue); }
        .card.memory { border-left-color: var(--accent-purple); }
        .card h3 { color: var(--accent-gold); margin-bottom: 15px; display: flex; align-items: center; gap: 10px; }
        .card.new-component h3 { color: var(--accent-blue); }
        .card.memory h3 { color: var(--accent-purple); }
        .metric { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }
        .metric:last-child { border-bottom: none; }
        .metric .label { color: var(--text-muted); }
        .metric .value { font-weight: bold; font-size: 1.2em; }
        .pass { color: var(--accent-green); }
        .fail { color: var(--accent-red); }
        .partial { color: var(--accent-yellow); }
        .nodata { color: var(--text-muted); }
        .unknown { color: var(--text-muted); }
        .timestamp { color: var(--text-muted); font-size: 0.8em; margin-top: 15px; }
        .commands {
            background: var(--bg-card);
            border-radius: 10px;
            padding: 20px;
            margin-top: 30px;
            max-width: 1400px;
            margin-left: auto;
            margin-right: auto;
        }
        .commands h3 { color: var(--accent-gold); margin-bottom: 15px; }
        .command-item { background: #0d1117; padding: 10px 15px; border-radius: 5px; margin: 10px 0; font-family: 'Consolas', monospace; font-size: 0.9em; }
        .command-label { color: var(--text-muted); font-size: 0.8em; margin-bottom: 5px; }
        .footer { text-align: center; margin-top: 30px; color: var(--text-muted); font-size: 0.8em; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 3px; font-size: 0.7em; margin-left: 10px; }
        .badge.new { background: var(--accent-blue); color: white; }
    </style>
</head>
<body>
    <div class="header">
        <h1>IMPERIUM TEST VERSION</h1>
        <p class="subtitle">Sanctum Mirror Dashboard v2.0</p>
    </div>
    
    <div class="warning-banner">
        EXPERIMENTAL - This is a test version, not production
    </div>
    
    <div class="overall-status">
        <h2>OVERALL STATUS</h2>
        <div class="verdict $(Get-VerdictClass $OverallVerdict)">$OverallVerdict</div>
        <div class="git-head">Git HEAD: $SmokeHead</div>
    </div>
    
    <h2 class="section-title">🔧 Core Systems</h2>
    <div class="grid">
        <div class="card">
            <h3><span class="icon">🧪</span> Testing Field - Smoke Test</h3>
            <div class="metric">
                <span class="label">Verdict</span>
                <span class="value $(Get-VerdictClass $SmokeVerdict)">$SmokeVerdict</span>
            </div>
            <div class="metric">
                <span class="label">Checks Passed</span>
                <span class="value">$SmokePassed / $SmokeTotal</span>
            </div>
            <div class="timestamp">Last run: $SmokeTime</div>
        </div>
        
        <div class="card">
            <h3><span class="icon">⚙️</span> Mechanicus - Script Health</h3>
            <div class="metric">
                <span class="label">Verdict</span>
                <span class="value $(Get-VerdictClass $MechVerdict)">$MechVerdict</span>
            </div>
            <div class="metric">
                <span class="label">Healthy Scripts</span>
                <span class="value">$MechHealthy / $MechTotal</span>
            </div>
            <div class="metric">
                <span class="label">Health %</span>
                <span class="value">$MechPercent%</span>
            </div>
            <div class="timestamp">Last run: $MechTime</div>
        </div>
        
        <div class="card">
            <h3><span class="icon">🔍</span> Inquisition - Audit</h3>
            <div class="metric">
                <span class="label">Verdict</span>
                <span class="value $(Get-VerdictClass $AuditVerdict)">$AuditVerdict</span>
            </div>
            <div class="metric">
                <span class="label">Files Scanned</span>
                <span class="value">$AuditScanned</span>
            </div>
            <div class="metric">
                <span class="label">Issues Found</span>
                <span class="value $(if ($AuditIssues -gt 0) {'fail'} else {'pass'})">$AuditIssues</span>
            </div>
            <div class="metric">
                <span class="label">Fake Green</span>
                <span class="value $(if ($AuditFakeGreen -gt 0) {'fail'} else {'pass'})">$AuditFakeGreen</span>
            </div>
            <div class="metric">
                <span class="label">Stale Truth</span>
                <span class="value $(if ($AuditStale -gt 0) {'fail'} else {'pass'})">$AuditStale</span>
            </div>
            <div class="timestamp">Last run: $AuditTime</div>
        </div>
    </div>
    
    <h2 class="section-title">🧠 Agent Intelligence <span class="badge new">NEW</span></h2>
    <div class="grid">
        <div class="card memory">
            <h3><span class="icon">🧠</span> Second Brain - Memory</h3>
            <div class="metric">
                <span class="label">Status</span>
                <span class="value $(Get-VerdictClass $MemoryVerdict)">$MemoryVerdict</span>
            </div>
            <div class="metric">
                <span class="label">Goals Loaded</span>
                <span class="value">$MemoryGoals</span>
            </div>
            <div class="metric">
                <span class="label">Rules Loaded</span>
                <span class="value">$MemoryRules</span>
            </div>
            <div class="metric">
                <span class="label">Known Errors</span>
                <span class="value">$MemoryErrors</span>
            </div>
            <div class="timestamp">Last run: $MemoryTime</div>
        </div>
        
        <div class="card memory">
            <h3><span class="icon">🤝</span> Agent Memory Protocol</h3>
            <div class="metric">
                <span class="label">Handshake Status</span>
                <span class="value $(Get-VerdictClass $HandshakeVerdict)">$HandshakeVerdict</span>
            </div>
            <div class="metric">
                <span class="label">Queries Answered</span>
                <span class="value">$HandshakeQueries</span>
            </div>
            <div class="timestamp">Last run: $HandshakeTime</div>
        </div>
    </div>
    
    <h2 class="section-title">🔬 Development Tools <span class="badge new">NEW</span></h2>
    <div class="grid">
        <div class="card new-component">
            <h3><span class="icon">🔬</span> Live Workbench - Sandbox</h3>
            <div class="metric">
                <span class="label">Status</span>
                <span class="value $(Get-VerdictClass $WorkbenchVerdict)">$WorkbenchVerdict</span>
            </div>
            <div class="metric">
                <span class="label">Tests Total</span>
                <span class="value">$WorkbenchTests</span>
            </div>
            <div class="metric">
                <span class="label">Tests Passed</span>
                <span class="value pass">$WorkbenchPassed</span>
            </div>
            <div class="metric">
                <span class="label">Tests Failed</span>
                <span class="value $(if ($WorkbenchFailed -gt 0) {'fail'} else {'pass'})">$WorkbenchFailed</span>
            </div>
            <div class="timestamp">Last run: $WorkbenchTime</div>
        </div>
        
        <div class="card new-component">
            <h3><span class="icon">📝</span> UF99 Prompt Standard</h3>
            <div class="metric">
                <span class="label">Templates</span>
                <span class="value">7</span>
            </div>
            <div class="metric">
                <span class="label">Core</span>
                <span class="value pass">UF99_CORE.md</span>
            </div>
            <div class="metric">
                <span class="label">Validator</span>
                <span class="value pass">validate_uf99_prompt.py</span>
            </div>
        </div>
        
        <div class="card new-component">
            <h3><span class="icon">📡</span> Communication Protocol</h3>
            <div class="metric">
                <span class="label">Message Types</span>
                <span class="value">Defined</span>
            </div>
            <div class="metric">
                <span class="label">Status Formats</span>
                <span class="value">Defined</span>
            </div>
            <div class="metric">
                <span class="label">Escalation Rules</span>
                <span class="value pass">Active</span>
            </div>
        </div>
    </div>
    
    <div class="commands">
        <h3>Commands</h3>
        <div class="command-label">Run all checks:</div>
        <div class="command-item">.\IMPERIUM_TEST_VERSION\RUN_ALL.ps1</div>
        <div class="command-label">Run smoke test:</div>
        <div class="command-item">.\IMPERIUM_TEST_VERSION\TESTING_FIELD\RUN_SMOKE.ps1</div>
        <div class="command-label">Run script health:</div>
        <div class="command-item">.\IMPERIUM_TEST_VERSION\ORGANS\MECHANICUS\RUN_SCRIPT_HEALTH.ps1</div>
        <div class="command-label">Run audit:</div>
        <div class="command-item">.\IMPERIUM_TEST_VERSION\ORGANS\INQUISITION\RUN_AUDIT.ps1</div>
        <div class="command-label">Build memory summary:</div>
        <div class="command-item">py -3 .\IMPERIUM_TEST_VERSION\SECOND_BRAIN\SCRIPTS\build_memory_summary.py</div>
        <div class="command-label">Run sandbox tests:</div>
        <div class="command-item">py -3 .\IMPERIUM_TEST_VERSION\LIVE_WORKBENCH\SCRIPTS\run_sandbox_tests.py</div>
        <div class="command-label">Agent handshake:</div>
        <div class="command-item">py -3 .\IMPERIUM_TEST_VERSION\AGENT_MEMORY_PROTOCOL\SCRIPTS\agent_context_handshake.py</div>
        <div class="command-label">Regenerate this dashboard:</div>
        <div class="command-item">.\IMPERIUM_TEST_VERSION\SANCTUM_MIRROR\GENERATE_INDEX.ps1</div>
    </div>
    
    <div class="footer">
        <p>Generated: $Timestamp</p>
        <p>IMPERIUM Test Version v2.0 - Experimental Sandbox</p>
    </div>
</body>
</html>
"@

$Html | Out-File -FilePath $OutputPath -Encoding UTF8

Write-Host ""
Write-Host "Dashboard generated: $OutputPath"
Write-Host "Open: start $OutputPath"
