param(
    [Parameter(Mandatory = $true)][string]$TaskId,
    [string]$LocalTaskId = "LTASK-001",
    [string]$StageId = "STAGE-001-SMOKE-VALIDATE-AND-WRITE",
    [Parameter(Mandatory = $true)][string]$ArtifactRoot,
    [Parameter(Mandatory = $true)][string]$TaskMapPath,
    [Parameter(Mandatory = $true)][string]$StageMapPath,
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

$stageOutput = (Join-Path $ArtifactRoot "REPORTS/stage_smoke_output.md").Replace("\", "/")
$stageResult = (Join-Path $ArtifactRoot "OUTPUTS/e2e_stage_result.json").Replace("\", "/")

$taskMap = [ordered]@{
    task_id = $TaskId
    local_tasks = @(
        [ordered]@{
            local_task_id = $LocalTaskId
            title = "First runtime E2E smoke stage"
            purpose = "Validate minimal Doctrinarium->Astronomicon->Administratum flow with safe output."
            status = "READY_FOR_SMOKE_EXECUTION"
        }
    )
    allowed_stage_range = @($StageId)
    expected_outputs = @(
        $stageOutput,
        $stageResult
    )
    validation_rules = @(
        "REGISTRY JSON files parse.",
        "Stage output markdown exists.",
        "Stage result registration JSON exists."
    )
    stop_conditions = @(
        "Preflight returns BLOCK.",
        "Stage execution exits non-zero.",
        "Required output files missing."
    )
    recoverable_error_policy = "Record error in stage result and return FAIL."
    nonrecoverable_blockers = @(
        "Missing registry files.",
        "Missing required schemas."
    )
    required_organs = @("DOCTRINARIUM", "ASTRONOMICON", "ADMINISTRATUM")
    required_scripts = @(
        "TOOLS/imperium_doctrinarium_preflight_smoke.ps1",
        "TOOLS/imperium_astronomicon_get_task_map_smoke.ps1",
        "TOOLS/imperium_administratum_issue_work_packet_smoke.ps1",
        "TOOLS/imperium_register_stage_result_smoke.ps1"
    )
}

$stageMap = [ordered]@{
    task_id = $TaskId
    local_task_id = $LocalTaskId
    stages = @(
        [ordered]@{
            stage_id = $StageId
            depends_on = @()
            outputs = @($stageOutput, $stageResult)
            validation = @(
                "Output file exists.",
                "Known registry JSON files parse."
            )
            stop_rules = @(
                "Fail stage if JSON parse fails.",
                "Fail stage if output file cannot be written."
            )
        }
    )
}

$receipt = [ordered]@{
    schema = "IMPERIUM_PORT_RECEIPT_V1"
    receipt_id = "PORT-RECEIPT-{0}" -f ([guid]::NewGuid().ToString())
    message_id = "MSG-{0}" -f ([guid]::NewGuid().ToString())
    task_id = $TaskId
    local_task_id = $LocalTaskId
    stage_id = $StageId
    run_id = $null
    operation = "get_task_map|get_stage_map"
    status = "OK"
    payload_path = $TaskMapPath.Replace("\", "/")
    notes = @(
        "Smoke task and stage maps generated.",
        "Maps are scaffold runtime proof, not full production planning."
    )
    created_at = (Get-Date).ToString("o")
}

Write-JsonFile -Path $TaskMapPath -Object $taskMap -Depth 40
Write-JsonFile -Path $StageMapPath -Object $stageMap -Depth 40
Write-JsonFile -Path $ReceiptPath -Object $receipt -Depth 40

Write-Host "Astronomicon smoke task/stage maps generated."
Write-Host "Task map: $TaskMapPath"
Write-Host "Stage map: $StageMapPath"

