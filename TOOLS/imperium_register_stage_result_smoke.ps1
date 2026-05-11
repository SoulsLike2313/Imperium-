param(
    [Parameter(Mandatory = $true)][string]$TaskId,
    [Parameter(Mandatory = $true)][string]$RunId,
    [Parameter(Mandatory = $true)][string]$WorkSessionId,
    [Parameter(Mandatory = $true)][string]$StageId,
    [string]$LocalTaskId = "LTASK-001",
    [string]$Actor = "PC_SERVITOR",
    [string]$StageStatus = "PASS_WITH_LIMITATIONS",
    [Parameter(Mandatory = $true)][string]$StageOutputPath,
    [Parameter(Mandatory = $true)][string]$ResultPath,
    [Parameter(Mandatory = $true)][string]$ReceiptPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Ensure-Directory {
    param([Parameter(Mandatory = $true)][string]$Path)
    $parent = Split-Path -Parent $Path
    if ($parent -and -not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }
}

function Write-JsonFile {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)]$Object,
        [int]$Depth = 40
    )
    Ensure-Directory -Path $Path
    $json = $Object | ConvertTo-Json -Depth $Depth
    Set-Content -LiteralPath $Path -Encoding UTF8 -Value $json
}

$stageOutputExists = Test-Path -LiteralPath $StageOutputPath
$finalStatus = $StageStatus
$warnings = @()

if (-not $stageOutputExists) {
    $finalStatus = "FAIL"
    $warnings += "Stage output path missing."
}

$result = [ordered]@{
    schema = "IMPERIUM_STAGE_RESULT_V1"
    task_id = $TaskId
    local_task_id = $LocalTaskId
    stage_id = $StageId
    run_id = $RunId
    work_session_id = $WorkSessionId
    actor = $Actor
    status = $finalStatus
    stage_output_path = $StageOutputPath.Replace("\", "/")
    stage_output_exists = $stageOutputExists
    warnings = $warnings
    created_at = (Get-Date).ToString("o")
}

$receipt = [ordered]@{
    schema = "IMPERIUM_PORT_RECEIPT_V1"
    receipt_id = "PORT-RECEIPT-{0}" -f ([guid]::NewGuid().ToString())
    message_id = "MSG-{0}" -f ([guid]::NewGuid().ToString())
    task_id = $TaskId
    local_task_id = $LocalTaskId
    stage_id = $StageId
    run_id = $RunId
    operation = "register_stage_result"
    status = if ($finalStatus -like "PASS*") { "OK" } else { "ERROR" }
    payload_path = $ResultPath.Replace("\", "/")
    notes = @(
        "Stage result registration smoke runner executed."
    )
    created_at = (Get-Date).ToString("o")
}

Write-JsonFile -Path $ResultPath -Object $result -Depth 40
Write-JsonFile -Path $ReceiptPath -Object $receipt -Depth 40

Write-Host "Stage result registered."
Write-Host "Status: $finalStatus"
Write-Host "Result: $ResultPath"

if ($finalStatus -like "PASS*") {
    exit 0
}
exit 2

