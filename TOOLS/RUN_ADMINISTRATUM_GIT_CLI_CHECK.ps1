Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-PythonExe {
    if (Get-Command py -ErrorAction SilentlyContinue) { return @("py", "-3") }
    if (Get-Command python -ErrorAction SilentlyContinue) { return @("python") }
    if (Get-Command python3 -ErrorAction SilentlyContinue) { return @("python3") }
    throw "Python executable not found (tried py, python, python3)."
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$fallbackRoot = (Resolve-Path -LiteralPath (Join-Path $scriptDir "..")).Path

try {
    $repoRoot = (& git -C $fallbackRoot rev-parse --show-toplevel 2>$null | Out-String).Trim()
} catch {
    $repoRoot = ""
}

if ([string]::IsNullOrWhiteSpace($repoRoot)) {
    $repoRoot = $fallbackRoot
}

Set-Location -LiteralPath $repoRoot

$pythonCommand = Resolve-PythonExe
$pyExe = $pythonCommand[0]
$pyArgs = @()

if ($pythonCommand.Count -gt 1) {
    $pyArgs += $pythonCommand[1..($pythonCommand.Count - 1)]
}

$pyArgs += "TOOLS/administratum_git_cli_check_v0_1.py"

if (-not [string]::IsNullOrWhiteSpace($env:IMPERIUM_EXPECTED_HEAD)) {
    $pyArgs += @("--expected-head", $env:IMPERIUM_EXPECTED_HEAD)
}

if (-not [string]::IsNullOrWhiteSpace($env:IMPERIUM_EXPECTED_COMMIT_COUNT)) {
    $pyArgs += @("--expected-commit-count", $env:IMPERIUM_EXPECTED_COMMIT_COUNT)
}

& $pyExe @pyArgs
exit $LASTEXITCODE
