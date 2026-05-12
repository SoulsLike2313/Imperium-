param(
  [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

$TaskId = "BUNDLE-INTAKE-REGRESSION-CHECK-V0_1"
$TimestampUtc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$TargetRel = "TOOLS/review_worker_bundle_intake.ps1"
$TargetPath = Join-Path $RepoRoot $TargetRel

$OutDir = Join-Path $RepoRoot ".imperium_runtime\bundle_intake_regression"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$ResultJson = Join-Path $OutDir "BUNDLE_INTAKE_REGRESSION_RESULT.json"
$VerdictMd = Join-Path $OutDir "BUNDLE_INTAKE_REGRESSION_VERDICT.md"
$ReceiptJson = Join-Path $OutDir "BUNDLE_INTAKE_REGRESSION_RECEIPT.json"

$Checks = New-Object System.Collections.Generic.List[object]
$Blockers = New-Object System.Collections.Generic.List[string]
$Warnings = New-Object System.Collections.Generic.List[string]

function Add-Check {
  param(
    [string]$Name,
    [bool]$Pass,
    [string]$Detail
  )

  $Checks.Add([ordered]@{
    name = $Name
    pass = $Pass
    detail = $Detail
  }) | Out-Null

  if (-not $Pass) {
    $Blockers.Add(($Name + ": " + $Detail)) | Out-Null
  }
}

function Invoke-RegressionCommandCapture {
  param(
    [string]$Exe,
    [string[]]$CommandArgs,
    [string]$Label
  )

  $out = & $Exe @CommandArgs 2>&1
  $code = $LASTEXITCODE

  [PSCustomObject]@{
    label = $Label
    exe = $Exe
    args = $CommandArgs
    exit_code = $code
    output = ($out | Out-String)
  }
}

if (-not (Test-Path -LiteralPath $TargetPath)) {
  Add-Check -Name "target_exists" -Pass $false -Detail ("missing " + $TargetRel)
} else {
  Add-Check -Name "target_exists" -Pass $true -Detail $TargetRel

  $Text = [System.IO.File]::ReadAllText($TargetPath, [System.Text.UTF8Encoding]::new($false, $true))

  Add-Check -Name "no_reserved_args_parameter" -Pass (-not ($Text -match '\[string\[\]\]\$Args')) -Detail "no [string[]] Args parameter"
  Add-Check -Name "has_command_args_parameter" -Pass ($Text -match '\[string\[\]\]\$CommandArgs') -Detail "has [string[]] CommandArgs parameter"
  Add-Check -Name "no_at_args_forwarding" -Pass (-not ($Text -match '(?<![A-Za-z0-9_])@Args(?![A-Za-z0-9_])')) -Detail "no automatic Args splat"
  Add-Check -Name "no_args_property_assignment" -Pass (-not ($Text -match 'args\s*=\s*\$Args\b')) -Detail "no automatic Args report assignment"
  Add-Check -Name "no_cmdargs_plus_args" -Pass (-not ($Text -match '\$cmdArgs\s*\+=\s*\$Args\b')) -Detail "no automatic Args append"

  $BadTrimMarker = ".TrimStart('\\','/')"
  $GoodTrimMarker = ".TrimStart([char[]]@('\','/'))"

  Add-Check -Name "no_bad_trimstart_string" -Pass (-not $Text.Contains($BadTrimMarker)) -Detail "bad TrimStart marker absent"
  Add-Check -Name "has_char_array_trimstart" -Pass ($Text.Contains($GoodTrimMarker)) -Detail "char-array TrimStart marker present"

  $tokens = $null
  $parseErrors = $null
  [System.Management.Automation.Language.Parser]::ParseFile($TargetPath, [ref]$tokens, [ref]$parseErrors) | Out-Null
  Add-Check -Name "powershell_parse_ok" -Pass ($parseErrors.Count -eq 0) -Detail ("parse_errors=" + $parseErrors.Count)

  $Probe = Invoke-RegressionCommandCapture -Exe "git" -CommandArgs @("status", "--short") -Label "git_status_before"
  $ProbeDetail = "exit=" + $Probe.exit_code + "; args=" + ($Probe.args -join ",")
  $ProbePass = (($Probe.exit_code -eq 0) -and ($Probe.args.Count -eq 2) -and ($Probe.args[0] -eq "status") -and ($Probe.args[1] -eq "--short"))
  Add-Check -Name "command_capture_keeps_args" -Pass $ProbePass -Detail $ProbeDetail

  $ProbeA = "\DOCS\ARSENAL\x.md".TrimStart([char[]]@('\','/'))
  $ProbeB = "/DOCS/SCRIPTORIUM/x.md".TrimStart([char[]]@('\','/'))

  Add-Check -Name "trimstart_probe_backslash" -Pass ($ProbeA -eq "DOCS\ARSENAL\x.md") -Detail $ProbeA
  Add-Check -Name "trimstart_probe_slash" -Pass ($ProbeB -eq "DOCS/SCRIPTORIUM/x.md") -Detail $ProbeB
}

$Verdict = "PASS"
if ($Blockers.Count -gt 0) {
  $Verdict = "BLOCKED"
} elseif ($Warnings.Count -gt 0) {
  $Verdict = "PASS_WITH_WARNINGS"
}

$Report = [ordered]@{
  schema_version = "imperium.bundle_intake_regression.v0_1"
  task_id = $TaskId
  timestamp_utc = $TimestampUtc
  repo_root = $RepoRoot
  target = $TargetRel
  verdict = $Verdict
  checks = $Checks
  blockers = $Blockers
  warnings = $Warnings
  outputs = [ordered]@{
    result_json = $ResultJson
    verdict_md = $VerdictMd
    receipt_json = $ReceiptJson
  }
}

$Report | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $ResultJson -Encoding UTF8

$Md = New-Object System.Collections.Generic.List[string]
$Md.Add("# Bundle Intake Regression Verdict") | Out-Null
$Md.Add("") | Out-Null
$Md.Add(("- task_id: {0}" -f $TaskId)) | Out-Null
$Md.Add(("- timestamp_utc: {0}" -f $TimestampUtc)) | Out-Null
$Md.Add(("- repo_root: {0}" -f $RepoRoot)) | Out-Null
$Md.Add(("- target: {0}" -f $TargetRel)) | Out-Null
$Md.Add(("- verdict: {0}" -f $Verdict)) | Out-Null
$Md.Add(("- blockers: {0}" -f $Blockers.Count)) | Out-Null
$Md.Add(("- warnings: {0}" -f $Warnings.Count)) | Out-Null
$Md.Add("") | Out-Null
$Md.Add("## Checks") | Out-Null

foreach ($Check in $Checks) {
  if ($Check.pass) {
    $Mark = "PASS"
  } else {
    $Mark = "BLOCKED"
  }

  $Line = "- {0}: {1} - {2}" -f $Mark, $Check.name, $Check.detail
  $Md.Add($Line) | Out-Null
}

$Md.Add("") | Out-Null
$Md.Add(("=== DONE: BUNDLE INTAKE REGRESSION {0} ===" -f $Verdict)) | Out-Null

($Md -join "`n") | Set-Content -LiteralPath $VerdictMd -Encoding UTF8

$Receipt = [ordered]@{
  task_id = $TaskId
  timestamp_utc = $TimestampUtc
  result_json = $ResultJson
  verdict_md = $VerdictMd
  verdict = $Verdict
}
$Receipt | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $ReceiptJson -Encoding UTF8

Get-Content -LiteralPath $VerdictMd -Encoding UTF8

if ($Verdict -ne "PASS") {
  exit 10
}