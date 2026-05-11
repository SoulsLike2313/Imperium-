param(
    [Parameter(Mandatory = $true)]
    [string]$OutputRoot,

    [Parameter(Mandatory = $true)]
    [string]$LocalTaskId
)

$ErrorActionPreference = "Stop"
. "E:\IMPERIUM\TOOLS\astronomicon_pipeline_common_v0_2.ps1"

$localTaskRoot = Join-Path $OutputRoot "LOCAL_TASKS\$LocalTaskId"
$localTaskJsonPath = Join-Path $localTaskRoot "LOCAL_TASK.json"
$localTaskStatusPath = Join-Path $localTaskRoot "STATUS.json"
$speculumRefPath = Join-Path $localTaskRoot "SPECULUM_REFINEMENTS.json"

if (-not (Test-Path -LiteralPath $localTaskJsonPath)) {
    throw "LOCAL_TASK.json not found: $localTaskJsonPath"
}

$localTask = Read-JsonFile -Path $localTaskJsonPath
$localTaskHash = ""
if ($localTask.PSObject.Properties.Name -contains "hash") {
    $localTaskHash = [string]$localTask.hash
}
if ([string]::IsNullOrWhiteSpace($localTaskHash)) {
    $localTaskHash = Get-Sha256String -Text ($localTask | ConvertTo-Json -Depth 30)
}

$speculumStatus = "NOT_IMPORTED"
$hints = @()
if (Test-Path -LiteralPath $speculumRefPath) {
    $speculum = Read-JsonFile -Path $speculumRefPath
    if ($speculum.refinement -and $speculum.refinement.decomposition_hints) {
        $hints = @($speculum.refinement.decomposition_hints)
    }
    $speculumStatus = "IMPORTED"
}

if ($hints.Count -eq 0) {
    $hints = @(
        "Validate execution scope and missing inputs for this Local Task."
        "Implement technical changes and generate required evidence."
        "Verify pass criteria, validate fail conditions, and prepare closure receipt."
    )
}

$stageMapRoot = Join-Path $OutputRoot "STAGE_MAPS\$LocalTaskId"
$stagesRoot = Join-Path $stageMapRoot "STAGES"
Ensure-Directory -Path $stageMapRoot
Ensure-Directory -Path $stagesRoot

$stages = @()
$index = 1
foreach ($hint in $hints) {
    $stageId = "STAGE-{0:D3}" -f $index
    $stageRoot = Join-Path $stagesRoot $stageId
    Ensure-Directory -Path $stageRoot

    $title = $hint
    if ($title.Length -gt 90) {
        $title = $title.Substring(0, 90)
    }

    $stageRecord = [ordered]@{
        schema_version = "ASTRONOMICON_STAGE_RECORD_V0_2"
        stage_id = $stageId
        parent_local_task_id = $LocalTaskId
        parent_general_task_id = $localTask.parent_general_task_id
        title = $title
        purpose = $hint
        execution_mode = $localTask.execution_mode
        assigned_organs = $localTask.required_organs
        inputs = @(
            "LOCAL_TASKS/$LocalTaskId/LOCAL_TASK.json"
            "LOCAL_TASKS/$LocalTaskId/SPECULUM_REFINEMENTS.json if present"
        )
        expected_outputs = @(
            "Stage-specific evidence file."
            "Stage-specific receipt."
        )
        pass_criteria = @(
            "Output evidence exists."
            "Evidence can be verified by Owner."
        )
        fail_conditions = @(
            "Required input is missing."
            "Evidence is incomplete or unverifiable."
        )
        status = "PLANNED"
        speculum_stage_review_status = "NOT_REQUESTED"
        created_at = (Get-Date).ToString("o")
    }

    $stageJson = $stageRecord | ConvertTo-Json -Depth 30
    $stageHash = Get-Sha256String -Text $stageJson
    Write-Utf8Bom -Path (Join-Path $stageRoot "STAGE.json") -Content $stageJson

    $stageMd = @(
        "# Stage"
        ""
        "STAGE_ID:"
        $stageId
        ""
        "PARENT_LOCAL_TASK_ID:"
        $LocalTaskId
        ""
        "PARENT_GENERAL_TASK_ID:"
        $localTask.parent_general_task_id
        ""
        "TITLE:"
        $title
        ""
        "PURPOSE:"
        $hint
        ""
        "STATUS:"
        "PLANNED"
        ""
        "HASH:"
        $stageHash
    ) -join "`n"
    Write-Utf8Bom -Path (Join-Path $stageRoot "STAGE.md") -Content $stageMd

    $stageStatus = [ordered]@{
        stage_id = $stageId
        parent_local_task_id = $LocalTaskId
        status = "PLANNED"
        speculum_stage_review_status = "NOT_REQUESTED"
        ready_for_execution = $false
        updated_at = (Get-Date).ToString("o")
    }
    Write-JsonFile -Path (Join-Path $stageRoot "STATUS.json") -Object $stageStatus -Depth 20

    $stages += [ordered]@{
        stage_id = $stageId
        title = $title
        purpose = $hint
        status = "PLANNED"
        hash = $stageHash
        path = "STAGE_MAPS/$LocalTaskId/STAGES/$stageId"
    }

    $index++
}

$stageMap = [ordered]@{
    schema_version = "ASTRONOMICON_STAGE_MAP_V0_2"
    general_task_id = $localTask.parent_general_task_id
    local_task_id = $LocalTaskId
    local_task_title = $localTask.title
    local_task_hash = $localTaskHash
    speculum_local_refinement_status = $speculumStatus
    stage_count = $stages.Count
    stages = $stages
    status = "STAGE_MAP_CREATED"
    generated_at = (Get-Date).ToString("o")
}
Write-JsonFile -Path (Join-Path $stageMapRoot "STAGE_MAP.json") -Object $stageMap -Depth 30

$stageMapMd = @(
    "# Stage Map"
    ""
    "GENERAL_TASK_ID:"
    $localTask.parent_general_task_id
    ""
    "LOCAL_TASK_ID:"
    $LocalTaskId
    ""
    "LOCAL_TASK_TITLE:"
    $localTask.title
    ""
    "STAGE_COUNT:"
    "$($stages.Count)"
    ""
    "STATUS:"
    "STAGE_MAP_CREATED"
    ""
    "## Stages"
)
foreach ($stage in $stages) {
    $stageMapMd += "- $($stage.stage_id): $($stage.title)"
}
Write-Utf8Bom -Path (Join-Path $stageMapRoot "STAGE_MAP.md") -Content ($stageMapMd -join "`n")

$receipt = [ordered]@{
    schema_version = "ASTRONOMICON_DECOMPOSE_LOCAL_TASK_TO_STAGES_RECEIPT_V0_2"
    general_task_id = $localTask.parent_general_task_id
    local_task_id = $LocalTaskId
    output_root = $OutputRoot
    stage_map_root = $stageMapRoot
    stage_count = $stages.Count
    speculum_local_refinement_used = (Test-Path -LiteralPath $speculumRefPath)
    status = "DECOMPOSED"
    generated_at = (Get-Date).ToString("o")
}
Write-JsonFile -Path (Join-Path $stageMapRoot "DECOMPOSE_RECEIPT.json") -Object $receipt -Depth 30

Update-StatusFile -StatusPath $localTaskStatusPath -Patch @{
    local_task_id = $LocalTaskId
    status = "STAGE_DECOMPOSED"
    speculum_review_status = $speculumStatus
    stage_decomposition_status = "DONE"
    stage_map_path = "STAGE_MAPS/$LocalTaskId/STAGE_MAP.json"
    stage_count = $stages.Count
}

Write-Host "Local Task decomposed to stages."
Write-Host "LOCAL_TASK_ID: $LocalTaskId"
Write-Host "STAGES: $($stages.Count)"
Write-Host "STAGE_MAP_ROOT: $stageMapRoot"
