param(
  [string]$ImperiumRoot = "E:\IMPERIUM",
  [string]$Mode = "manual-visible"
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $ScriptDir

Write-Host "[CONTINUITY] launcher start" -ForegroundColor Cyan
Write-Host "  script_dir: $ScriptDir"
Write-Host "  imperium_root: $ImperiumRoot"
Write-Host "  mode: $Mode"

python .\run_continuity_pack_executor.py --imperium-root $ImperiumRoot --mode $Mode
$rc = $LASTEXITCODE

Write-Host "[CONTINUITY] launcher finished with exit code $rc"
exit $rc
