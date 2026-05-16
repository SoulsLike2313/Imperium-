from pathlib import Path
import re

root = Path(".")
smoke = root / "TESTING_FIELD" / "RUN_SMOKE.ps1"
run_all = root / "RUN_ALL.ps1"

# ---------- patch RUN_SMOKE.ps1 ----------
s = smoke.read_text(encoding="utf-8-sig")

if "[switch]$CandidateMode" not in s:
    s = "param(\n    [switch]$CandidateMode\n)\n\n" + s

old_git = '''    Push-Location $RepoRoot
    $status = git status --short 2>&1
    $GitClean = [string]::IsNullOrWhiteSpace($status) -or ($status -match "^\\s*M\\s+\\.gitignore\\s*$") -or ($status -match "^\\?\\?\\s+\\.vscode")
    $GitHead = (git rev-parse --short HEAD 2>&1)
    Pop-Location'''

new_git = '''    Push-Location $RepoRoot
    $status = @(git status --short 2>&1)
    $GitHead = (git rev-parse --short HEAD 2>&1)

    $NonTestVersionChanges = @()
    foreach ($line in $status) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }

        $isTestVersionChange = ($line -match "IMPERIUM_TEST_VERSION[\\\\/]")
        $isAllowedRootChange = ($line -match "^\\\\s*M\\\\s+\\\\.gitignore\\\\s*$") -or ($line -match "^\\\\?\\\\?\\\\s+\\\\.vscode")

        if ((-not $isTestVersionChange) -and (-not $isAllowedRootChange)) {
            $NonTestVersionChanges += $line
        }
    }

    if ($CandidateMode) {
        $GitClean = ($NonTestVersionChanges.Count -eq 0)
    } else {
        $joinedStatus = ($status -join "`n")
        $GitClean = [string]::IsNullOrWhiteSpace($joinedStatus) -or ($joinedStatus -match "^\\\\s*M\\\\s+\\\\.gitignore\\\\s*$") -or ($joinedStatus -match "^\\\\?\\\\?\\\\s+\\\\.vscode")
    }

    Pop-Location'''

if old_git not in s:
    raise SystemExit("RUN_SMOKE patch failed: git block not found")

s = s.replace(old_git, new_git)

s = s.replace(
'''    description = "Git working directory is clean (or only .gitignore/.vscode modified)"
    passed = $GitClean
    git_head = $GitHead
    error = if (-not $GitClean) { "Uncommitted changes" } else { $null }''',
'''    description = if ($CandidateMode) { "Git scope is safe for candidate mode: dirty allowed only inside IMPERIUM_TEST_VERSION" } else { "Git working directory is clean (or only .gitignore/.vscode modified)" }
    passed = $GitClean
    git_head = $GitHead
    candidate_mode = [bool]$CandidateMode
    dirty_count = @($status).Count
    non_test_version_changes = $NonTestVersionChanges
    error = if (-not $GitClean) { "Uncommitted changes outside IMPERIUM_TEST_VERSION or disallowed root changes" } elseif ($CandidateMode -and @($status).Count -gt 0) { "Candidate dirty state is scoped to IMPERIUM_TEST_VERSION" } else { $null }'''
)

s = s.replace(
'''    summary = @{
        total_checks = $TotalChecks''',
'''    summary = @{
        candidate_mode = [bool]$CandidateMode
        total_checks = $TotalChecks'''
)

s = s.replace(
'''    command = "RUN_SMOKE.ps1"''',
'''    command = if ($CandidateMode) { "RUN_SMOKE.ps1 -CandidateMode" } else { "RUN_SMOKE.ps1" }'''
)

smoke.write_text(s, encoding="utf-8")

# ---------- patch RUN_ALL.ps1 ----------
r = run_all.read_text(encoding="utf-8-sig")

if "[switch]$CandidateMode" not in r:
    if "param(" in r[:500]:
        r = re.sub(r"param\\((.*?)\\)", lambda m: "param(" + m.group(1).rstrip() + ",\n    [switch]$CandidateMode\n)", r, count=1, flags=re.S)
    else:
        r = "param(\n    [switch]$OnlyCore,\n    [switch]$CandidateMode\n)\n\n" + r

old_smoke = '''if (Test-Path $smokeScript) {
    & powershell -ExecutionPolicy Bypass -File $smokeScript
    $smokeExit = $LASTEXITCODE
    $Results += @{ name = "Smoke Test"; exit_code = $smokeExit; verdict = if ($smokeExit -eq 0) { "PASS" } else { "FAIL" }; category = "core" }
} else {'''

new_smoke = '''if (Test-Path $smokeScript) {
    if ($CandidateMode) {
        & powershell -ExecutionPolicy Bypass -File $smokeScript -CandidateMode
    } else {
        & powershell -ExecutionPolicy Bypass -File $smokeScript
    }
    $smokeExit = $LASTEXITCODE
    $Results += @{ name = "Smoke Test"; exit_code = $smokeExit; verdict = if ($smokeExit -eq 0) { "PASS" } else { "FAIL" }; category = "core"; candidate_mode = [bool]$CandidateMode }
} else {'''

if old_smoke not in r:
    raise SystemExit("RUN_ALL patch failed: smoke block not found")

r = r.replace(old_smoke, new_smoke)
r = r.replace("py -3 ", "py -3.12 ")

run_all.write_text(r, encoding="utf-8")

print("PATCH_OK")
print(smoke)
print(run_all)
