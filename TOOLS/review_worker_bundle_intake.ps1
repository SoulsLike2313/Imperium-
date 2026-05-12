[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Bundle,

    [string]$RepoRoot = "E:\IMPERIUM",

    [string]$IncomingRoot = "E:\IMPERIUM_LOCAL_HANDOFF\BUNDLE_INTAKE",

    [switch]$Apply,
    [switch]$NoApply
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-ColorLine {
    param(
        [Parameter(Mandatory = $true)][string]$Text,
        [ConsoleColor]$Color = [ConsoleColor]::Gray
    )
    try {
        Write-Host $Text -ForegroundColor $Color
    }
    catch {
        Write-Output $Text
    }
}

function Write-Section {
    param([string]$Text)
    Write-ColorLine "`n=== $Text ===" ([ConsoleColor]::Cyan)
}

function Find-Python {
    $candidates = @(
        @{ Cmd = "py"; Args = @("-3") },
        @{ Cmd = "python"; Args = @() },
        @{ Cmd = "python3"; Args = @() }
    )
    foreach ($candidate in $candidates) {
        try {
            $null = & $candidate.Cmd @($candidate.Args + @("-c", "print('ok')")) 2>$null
            if ($LASTEXITCODE -eq 0) {
                return $candidate
            }
        }
        catch {
            continue
        }
    }
    throw "Python runtime not found (tried py -3, python, python3)."
}

function Run-CommandCapture {
    param(
        [string]$Exe,
        [string[]]$Args,
        [string]$Label
    )
    $out = & $Exe @Args 2>&1
    $code = $LASTEXITCODE
    [PSCustomObject]@{
        label = $Label
        exe = $Exe
        args = $Args
        exit_code = $code
        output = ($out | Out-String)
    }
}

function Run-PythonFile {
    param(
        [hashtable]$Python,
        [string]$ScriptPath,
        [string[]]$Args,
        [string]$Label
    )
    $exe = [string]$Python.Cmd
    $cmdArgs = @()
    if ($Python.Args.Count -gt 0) {
        $cmdArgs += $Python.Args
    }
    $cmdArgs += $ScriptPath
    $cmdArgs += $Args
    return Run-CommandCapture -Exe $exe -Args $cmdArgs -Label $Label
}

function Ensure-Dir {
    param([string]$PathText)
    if (-not (Test-Path -LiteralPath $PathText)) {
        New-Item -ItemType Directory -Path $PathText -Force | Out-Null
    }
}

function Copy-BundleToQuarantine {
    param(
        [string]$BundlePath,
        [string]$QuarantineDir,
        [string]$ReportPath
    )
    Ensure-Dir -PathText $QuarantineDir
    Copy-Item -LiteralPath $BundlePath -Destination (Join-Path $QuarantineDir (Split-Path -Leaf $BundlePath)) -Force

    $shaPath = "$BundlePath.sha256"
    if (Test-Path -LiteralPath $shaPath) {
        Copy-Item -LiteralPath $shaPath -Destination (Join-Path $QuarantineDir (Split-Path -Leaf $shaPath)) -Force
    }
    if (Test-Path -LiteralPath $ReportPath) {
        Copy-Item -LiteralPath $ReportPath -Destination (Join-Path $QuarantineDir (Split-Path -Leaf $ReportPath)) -Force
    }
}

$applyMode = $false
if ($Apply.IsPresent) { $applyMode = $true }
if ($NoApply.IsPresent) { $applyMode = $false }

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$reviewRoot = Join-Path $RepoRoot ".imperium_runtime\bundle_intake_review\$timestamp"
$reviewJson = Join-Path $reviewRoot "INTAKE_REVIEW_REPORT.json"
$reviewMd = Join-Path $reviewRoot "INTAKE_REVIEW_VERDICT.md"
$verifyJson = Join-Path $reviewRoot "VERIFY_WORKER_BUNDLE_REPORT.json"

$summary = [ordered]@{
    schema_version = "imperium.bundle_intake_review.v0_1"
    checked_at = (Get-Date).ToUniversalTime().ToString("o")
    bundle = $Bundle
    repo_root = $RepoRoot
    incoming_root = $IncomingRoot
    apply_mode = $applyMode
    preflight = [ordered]@{}
    checks = @()
    warnings = @()
    blockers = @()
    final_verdict = "BLOCKED"
    next_action = ""
}

Write-ColorLine "IMPERIUM PC Bundle Intake Review v0.1" ([ConsoleColor]::Green)
Write-ColorLine "Bundle: $Bundle" ([ConsoleColor]::Cyan)
Write-ColorLine "RepoRoot: $RepoRoot" ([ConsoleColor]::Cyan)
Write-ColorLine "Apply mode: $applyMode" ([ConsoleColor]::Yellow)

try {
    Ensure-Dir -PathText $reviewRoot

    Write-Section "PREFLIGHT"

    if (-not (Test-Path -LiteralPath $RepoRoot)) {
        throw "RepoRoot not found: $RepoRoot"
    }
    if (-not (Test-Path -LiteralPath $Bundle)) {
        throw "Bundle not found: $Bundle"
    }

    Push-Location $RepoRoot

    $gitStatus = Run-CommandCapture -Exe "git" -Args @("status", "--short") -Label "git_status_before"
    $summary.preflight.git_status_exit = $gitStatus.exit_code
    $summary.preflight.git_status_before = $gitStatus.output
    if ($gitStatus.exit_code -ne 0) {
        throw "git status failed before intake"
    }

    $dirtyBefore = -not [string]::IsNullOrWhiteSpace($gitStatus.output)
    $summary.preflight.worktree_dirty_before = $dirtyBefore
    if ($dirtyBefore -and $applyMode) {
        $summary.blockers += "dirty_worktree_before_apply"
        $summary.final_verdict = "BLOCKED"
    }

    $shaPath = "$Bundle.sha256"
    $summary.preflight.sibling_sha256_present = (Test-Path -LiteralPath $shaPath)

    $python = Find-Python
    $verifyScript = Join-Path $RepoRoot "TOOLS\verify_worker_bundle.py"
    if (-not (Test-Path -LiteralPath $verifyScript)) {
        throw "Verifier script not found: $verifyScript"
    }

    Write-Section "VERIFY BUNDLE"
    $verifyResult = Run-PythonFile -Python $python -ScriptPath $verifyScript -Args @("--bundle", $Bundle, "--repo-root", $RepoRoot, "--json-out", $verifyJson, "--human") -Label "verify_worker_bundle"
    $summary.checks += $verifyResult

    if (-not (Test-Path -LiteralPath $verifyJson)) {
        throw "Verifier JSON report not produced: $verifyJson"
    }

    $verifyPayload = Get-Content -LiteralPath $verifyJson -Encoding UTF8 -Raw | ConvertFrom-Json
    $verifyBlockers = @($verifyPayload.blockers)
    if ($verifyResult.exit_code -ne 0 -or $verifyBlockers.Count -gt 0) {
        Write-Section "QUARANTINE"
        $quarantineDir = Join-Path $IncomingRoot "quarantine\rejected\$timestamp"
        Copy-BundleToQuarantine -BundlePath $Bundle -QuarantineDir $quarantineDir -ReportPath $verifyJson
        $summary.blockers += "bundle_verifier_rejected"
        $summary.final_verdict = "CANNOT_COMMIT"
        $summary.next_action = "Review quarantine report and fix bundle on VM2 before retry."
    }
    else {
        Write-Section "CONTROLLED UNPACK"
        $incomingDir = Join-Path $IncomingRoot "incoming\$timestamp"
        Ensure-Dir -PathText $incomingDir

        if ((Get-Item -LiteralPath $Bundle).PSIsContainer) {
            Copy-Item -LiteralPath $Bundle -Destination (Join-Path $incomingDir "bundle") -Recurse -Force
        }
        else {
            Expand-Archive -LiteralPath $Bundle -DestinationPath $incomingDir -Force
        }

        $repoDir = Join-Path $incomingDir "repo"
        if (-not (Test-Path -LiteralPath $repoDir)) {
            $summary.blockers += "incoming_repo_folder_missing"
            $summary.final_verdict = "CANNOT_COMMIT"
        }
        else {
            Write-ColorLine "Incoming repo files:" ([ConsoleColor]::Yellow)
            Get-ChildItem -LiteralPath $repoDir -Recurse -File |
                ForEach-Object {
                    $rp = $_.FullName.Substring($repoDir.Length).TrimStart('\\','/')
                    Write-ColorLine "  - $rp" ([ConsoleColor]::Cyan)
                }

            if ($applyMode) {
                Write-Section "APPLY TO WORKTREE"

                Get-ChildItem -LiteralPath $repoDir -Recurse -File | ForEach-Object {
                    $rel = $_.FullName.Substring($repoDir.Length).TrimStart('\\','/')
                    $dest = Join-Path $RepoRoot $rel
                    $destParent = Split-Path -Parent $dest
                    if (-not (Test-Path -LiteralPath $destParent)) {
                        New-Item -ItemType Directory -Path $destParent -Force | Out-Null
                    }
                    Copy-Item -LiteralPath $_.FullName -Destination $dest -Force
                }

                Write-Section "PRE-COMMIT CHECKS"

                $diffCheck = Run-CommandCapture -Exe "git" -Args @("diff", "--check") -Label "git_diff_check"
                $summary.checks += $diffCheck
                if ($diffCheck.exit_code -ne 0) {
                    $summary.blockers += "git_diff_check_failed"
                }

                $changedPy = & git diff --name-only -- "*.py"
                if ($LASTEXITCODE -eq 0 -and $changedPy) {
                    foreach ($pyPath in $changedPy) {
                        $compile = Run-PythonFile -Python $python -ScriptPath "-m" -Args @("py_compile", $pyPath) -Label "py_compile:$pyPath"
                        $summary.checks += $compile
                        if ($compile.exit_code -ne 0) {
                            $summary.blockers += "py_compile_failed:$pyPath"
                        }
                    }
                }

                $checkAgentPath = Join-Path $RepoRoot "scripts\check_agent_entrypoint.py"
                if (Test-Path -LiteralPath $checkAgentPath) {
                    $agentCheck = Run-PythonFile -Python $python -ScriptPath $checkAgentPath -Args @() -Label "check_agent_entrypoint"
                    $summary.checks += $agentCheck
                    if ($agentCheck.exit_code -ne 0) {
                        $summary.blockers += "check_agent_entrypoint_failed"
                    }
                }

                $verifyRepoPath = Join-Path $RepoRoot "scripts\verify_repo.py"
                if (Test-Path -LiteralPath $verifyRepoPath) {
                    $repoCheck = Run-PythonFile -Python $python -ScriptPath $verifyRepoPath -Args @() -Label "verify_repo"
                    $summary.checks += $repoCheck
                    if ($repoCheck.exit_code -ne 0) {
                        $summary.blockers += "verify_repo_failed"
                    }
                }

                $adminCheckPs1 = Join-Path $RepoRoot "TOOLS\RUN_ADMINISTRATUM_GIT_CLI_CHECK.ps1"
                if (Test-Path -LiteralPath $adminCheckPs1) {
                    $adminCheck = Run-CommandCapture -Exe "powershell" -Args @("-ExecutionPolicy", "Bypass", "-NoProfile", "-File", $adminCheckPs1) -Label "administratum_git_cli_check"
                    $summary.checks += $adminCheck
                    if ($adminCheck.exit_code -ne 0) {
                        $summary.blockers += "administratum_git_cli_check_failed"
                    }
                }

                $statusAfter = Run-CommandCapture -Exe "git" -Args @("status", "--short") -Label "git_status_after_apply"
                $summary.checks += $statusAfter
                if ($statusAfter.exit_code -ne 0) {
                    $summary.blockers += "git_status_after_apply_failed"
                }

                if ($summary.blockers.Count -gt 0) {
                    $summary.final_verdict = "CANNOT_COMMIT"
                    $summary.next_action = "Fix blockers and re-run intake review."
                }
                else {
                    $summary.final_verdict = "CAN_COMMIT"
                    $summary.next_action = "Owner may run manual review then git add/commit on PC if accepted."
                }
            }
            else {
                $summary.final_verdict = "NEEDS_OWNER_DECISION"
                $summary.next_action = "Run again with -Apply after owner confirms bundle content."
            }
        }
    }
}
catch {
    $summary.blockers += "exception:$($_.Exception.Message)"
    if ($summary.final_verdict -ne "CANNOT_COMMIT") {
        $summary.final_verdict = "BLOCKED"
    }
    $summary.next_action = "Inspect intake report and correct environment or bundle."
}
finally {
    try { Pop-Location } catch { }
}

$summary.checked_at_done = (Get-Date).ToUniversalTime().ToString("o")
$summaryJson = $summary | ConvertTo-Json -Depth 8
$summaryJson | Set-Content -LiteralPath $reviewJson -Encoding UTF8

$md = @()
$md += "# BUNDLE INTAKE REVIEW VERDICT"
$md += ""
$md += "- bundle: $Bundle"
$md += "- repo_root: $RepoRoot"
$md += "- apply_mode: $applyMode"
$md += "- final_verdict: $($summary.final_verdict)"
$md += "- blockers: $($summary.blockers.Count)"
$md += "- warnings: $($summary.warnings.Count)"
$md += ""
if ($summary.blockers.Count -gt 0) {
    $md += "## Blockers"
    foreach ($b in $summary.blockers) { $md += "- $b" }
    $md += ""
}
$md += "## Next Action"
$md += "- $($summary.next_action)"
$mdText = $md -join "`n"
$mdText | Set-Content -LiteralPath $reviewMd -Encoding UTF8

Write-Section "FINAL VERDICT"
switch ($summary.final_verdict) {
    "CAN_COMMIT" { Write-ColorLine "CAN_COMMIT" ([ConsoleColor]::Green) }
    "NEEDS_OWNER_DECISION" { Write-ColorLine "NEEDS_OWNER_DECISION" ([ConsoleColor]::Yellow) }
    "CANNOT_COMMIT" { Write-ColorLine "CANNOT_COMMIT" ([ConsoleColor]::Red) }
    default { Write-ColorLine "BLOCKED" ([ConsoleColor]::Red) }
}
Write-ColorLine "Report JSON: $reviewJson" ([ConsoleColor]::Cyan)
Write-ColorLine "Report MD:   $reviewMd" ([ConsoleColor]::Cyan)

if ($summary.final_verdict -eq "CAN_COMMIT") {
    Write-ColorLine "Next: git add -A && git status --short && git commit -m '<message>'" ([ConsoleColor]::Green)
    exit 0
}
if ($summary.final_verdict -eq "NEEDS_OWNER_DECISION") {
    exit 3
}
if ($summary.final_verdict -eq "CANNOT_COMMIT") {
    exit 2
}
exit 4
