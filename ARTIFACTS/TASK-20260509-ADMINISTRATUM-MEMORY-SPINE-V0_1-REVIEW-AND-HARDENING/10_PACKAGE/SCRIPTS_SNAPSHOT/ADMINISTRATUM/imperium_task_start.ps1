param(
  [Parameter(Mandatory = $true)][string]$TaskId,
  [Parameter(Mandatory = $true)][string]$TaskName,
  [Parameter(Mandatory = $true)][string]$RecipePath
)

$ErrorActionPreference = 'Stop'
$Root = 'E:\IMPERIUM'
$Artifact = Join-Path $Root ("ARTIFACTS\" + $TaskId)
$Receipts = Join-Path $Artifact '03_RECEIPTS'
$RunLogs = Join-Path $Artifact '10_RUN_LOGS'
if (-not (Test-Path -LiteralPath $RunLogs)) {
  New-Item -ItemType Directory -Path $RunLogs | Out-Null
}
$RunId = "RUN-$(Get-Date -Format 'yyyyMMdd-HHmmss')-" + ([guid]::NewGuid().ToString('N').Substring(0,8))
$LogPath = Join-Path $RunLogs ("run_" + $RunId + ".log")

function Write-RunLog {
  param([string]$Message)
  $line = "[$(Get-Date -Format o)] $Message"
  Add-Content -LiteralPath $LogPath -Value $line -Encoding UTF8
  Write-Host $line
}

function Get-PythonCommand {
  if (Get-Command py -ErrorAction SilentlyContinue) {
    return @('py', '-3')
  }
  if (Get-Command python -ErrorAction SilentlyContinue) {
    return @('python')
  }
  throw 'Python interpreter not found (py/python).'
}

function Test-ReceiptVerdict {
  param([string]$ReceiptPath)
  if (-not (Test-Path -LiteralPath $ReceiptPath)) {
    throw "Required receipt missing: $ReceiptPath"
  }
  $raw = Get-Content -LiteralPath $ReceiptPath -Raw -Encoding UTF8
  $receipt = $raw | ConvertFrom-Json
  $verdict = [string]$receipt.verdict
  if ($verdict -like 'BLOCKED*' -or $verdict -like 'FAIL*') {
    throw "Receipt verdict blocked/fail at $ReceiptPath : $verdict"
  }
}

function Invoke-PythonGate {
  param(
    [string]$Label,
    [string]$ScriptPath,
    [string[]]$ExtraArgs,
    [string]$ExpectedReceipt
  )

  $py = Get-PythonCommand
  $cmdParts = @() + $py + @($ScriptPath, '--task-id', $TaskId, '--run-id', $RunId, '--root', $Root) + $ExtraArgs
  Write-RunLog ("START_GATE " + $Label)
  Write-RunLog ("CMD " + ($cmdParts -join ' '))

  & $cmdParts[0] $cmdParts[1..($cmdParts.Length-1)] 2>&1 | Tee-Object -FilePath $LogPath -Append
  $exitCode = $LASTEXITCODE
  if ($exitCode -ne 0) {
    throw "Gate failed: $Label (exit=$exitCode)"
  }

  if ($ExpectedReceipt -and $ExpectedReceipt.Length -gt 0) {
    Test-ReceiptVerdict -ReceiptPath $ExpectedReceipt
  }
  Write-RunLog ("END_GATE " + $Label)
}

Write-RunLog "TASK_START $TaskId"
Write-RunLog "TASK_NAME $TaskName"
Write-RunLog "RECIPE $RecipePath"
Write-RunLog "RUN_ID $RunId"

try {
  Invoke-PythonGate -Label '01_DOCTRINARIUM_PREFLIGHT' `
    -ScriptPath 'E:\IMPERIUM\ORGANS\DOCTRINARIUM\SCRIPTS\doctrinarium_preflight.py' `
    -ExtraArgs @('--recipe-path', $RecipePath) `
    -ExpectedReceipt (Join-Path $Receipts '00_doctrinarium_preflight_receipt.json')

  Invoke-PythonGate -Label '02_OFFICIO_AGENTIS_SCOPE' `
    -ScriptPath 'E:\IMPERIUM\ORGANS\OFFICIO_AGENTIS\SCRIPTS\officio_agentis_scope.py' `
    -ExtraArgs @('--recipe-path', $RecipePath) `
    -ExpectedReceipt (Join-Path $Receipts '01_officio_agentis_scope_receipt.json')

  Invoke-PythonGate -Label '03_ADMINISTRATUM_CONTEXT' `
    -ScriptPath 'E:\IMPERIUM\ORGANS\ADMINISTRATUM\SCRIPTS\administratum_record_event.py' `
    -ExtraArgs @(
      '--organ','ADMINISTRATUM',
      '--actor','PC_SERVITOR',
      '--event-type','CONTEXT_LOADED',
      '--summary-ru','Контекст задачи загружен и подтвержден перед запуском маршрута.',
      '--verdict','PASS_CONTEXT_RECORDED',
      '--receipt-paths',
      (Join-Path $Receipts '00_doctrinarium_preflight_receipt.json'),
      (Join-Path $Receipts '01_officio_agentis_scope_receipt.json')
    ) `
    -ExpectedReceipt (Join-Path $Receipts '02_administratum_context_receipt.json')

  Invoke-PythonGate -Label '04_ASTRONOMICON_LOAD_ROUTE' `
    -ScriptPath 'E:\IMPERIUM\ORGANS\ASTRONOMICON\SCRIPTS\astronomicon_load_route.py' `
    -ExtraArgs @() `
    -ExpectedReceipt (Join-Path $Receipts '03_astronomicon_route_receipt.json')

  Invoke-PythonGate -Label '05_MECHANICUS_RESOLVE' `
    -ScriptPath 'E:\IMPERIUM\ORGANS\MECHANICUS\SCRIPTS\mechanicus_resolve_scripts.py' `
    -ExtraArgs @() `
    -ExpectedReceipt (Join-Path $Receipts '04_mechanicus_script_resolution_receipt.json')

  Invoke-PythonGate -Label '06_MECHANICUS_DUMMY_STAGE' `
    -ScriptPath 'E:\IMPERIUM\ORGANS\MECHANICUS\SCRIPTS\mechanicus_dummy_stage.py' `
    -ExtraArgs @('--stage-id','STAGE-001') `
    -ExpectedReceipt (Join-Path $Receipts '05_stage_001_receipt.json')

  Invoke-PythonGate -Label '07_INQUISITION_AUDIT' `
    -ScriptPath 'E:\IMPERIUM\ORGANS\INQUISITION\SCRIPTS\inquisition_post_stage_audit.py' `
    -ExtraArgs @() `
    -ExpectedReceipt (Join-Path $Receipts '06_inquisition_post_stage_receipt.json')

  Invoke-PythonGate -Label '08_ADMINISTRATUM_BUILD_CURRENT_STATE' `
    -ScriptPath 'E:\IMPERIUM\ORGANS\ADMINISTRATUM\SCRIPTS\administratum_build_current_state.py' `
    -ExtraArgs @() `
    -ExpectedReceipt (Join-Path $Receipts '07_task_summary_receipt.json')

  Invoke-PythonGate -Label '09_ADMINISTRATUM_BUILD_CONTINUITY' `
    -ScriptPath 'E:\IMPERIUM\ORGANS\ADMINISTRATUM\SCRIPTS\administratum_build_continuity_candidate.py' `
    -ExtraArgs @() `
    -ExpectedReceipt (Join-Path $Receipts '08_continuity_candidate_receipt.json')

  Write-RunLog 'TASK_END PASS_ORGAN_CYCLE_SMOKE_TEST_V0_1'
  exit 0
}
catch {
  Write-RunLog ("TASK_END FAIL " + $_.Exception.Message)
  exit 2
}
