param(
    [Parameter(Mandatory=$true)]
    [string]$OutputRoot,

    [Parameter(Mandatory=$true)]
    [string]$LocalTaskId
)

$ErrorActionPreference = "Stop"

function Write-Utf8Bom {
    param(
        [Parameter(Mandatory=$true)][string]$Path,
        [Parameter(Mandatory=$true)][string]$Content
    )

    $Dir = Split-Path -Parent $Path
    if ($Dir -and !(Test-Path $Dir)) {
        New-Item -ItemType Directory -Force $Dir | Out-Null
    }

    $Utf8Bom = New-Object System.Text.UTF8Encoding($true)
    [System.IO.File]::WriteAllText($Path, $Content.Replace("`n","`r`n"), $Utf8Bom)
}

function Get-Sha256String {
    param([Parameter(Mandatory=$true)][string]$Text)

    $Sha = [System.Security.Cryptography.SHA256]::Create()
    $Bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
    $HashBytes = $Sha.ComputeHash($Bytes)
    return ([System.BitConverter]::ToString($HashBytes)).Replace("-", "").ToLowerInvariant()
}

$LocalTaskRoot = Join-Path $OutputRoot "LOCAL_TASKS\$LocalTaskId"
$LocalTaskJsonPath = Join-Path $LocalTaskRoot "LOCAL_TASK.json"
$LocalTaskStatusPath = Join-Path $LocalTaskRoot "STATUS.json"
$SpeculumRefPath = Join-Path $LocalTaskRoot "SPECULUM_REFINEMENTS.json"

if (!(Test-Path $LocalTaskJsonPath)) {
    throw "LOCAL_TASK.json not found: $LocalTaskJsonPath"
}

$LocalTask = Get-Content -Encoding UTF8 $LocalTaskJsonPath -Raw | ConvertFrom-Json

$Speculum = $null
$SpeculumItem = $null
$SpeculumStatus = "NOT_IMPORTED"
$Hints = @()

if (Test-Path $SpeculumRefPath) {
    $Speculum = Get-Content -Encoding UTF8 $SpeculumRefPath -Raw | ConvertFrom-Json
    $SpeculumItem = $Speculum.refinement
    $SpeculumStatus = "IMPORTED"

    if ($SpeculumItem.decomposition_hints) {
        $Hints = @($SpeculumItem.decomposition_hints)
    }
}

if ($Hints.Count -eq 0) {
    $Hints = @(
        "Validate scope, required inputs, and pass criteria before execution.",
        "Create or update the required files/scripts for the Local Task.",
        "Verify outputs, create receipts, and prepare the task for artifact/commit."
    )
}

$StageMapRoot = Join-Path $OutputRoot "STAGE_MAPS\$LocalTaskId"
$StagesRoot = Join-Path $StageMapRoot "STAGES"
New-Item -ItemType Directory -Force $StageMapRoot, $StagesRoot | Out-Null

$Stages = @()
$Index = 1

foreach ($Hint in $Hints) {
    $StageNum = "{0:D3}" -f $Index
    $StageId = "STAGE-$StageNum"
    $StageRoot = Join-Path $StagesRoot $StageId
    New-Item -ItemType Directory -Force $StageRoot | Out-Null

    $Title = $Hint
    if ($Title.Length -gt 90) {
        $Title = $Title.Substring(0, 90)
    }

    $StageRecord = [ordered]@{
        schema_version = "ASTRONOMICON_STAGE_RECORD_V0_1"
        stage_id = $StageId
        parent_local_task_id = $LocalTaskId
        parent_general_task_id = $LocalTask.parent_general_task_id
        title = $Title
        purpose = $Hint
        execution_mode = $LocalTask.execution_mode
        assigned_organs = $LocalTask.required_organs
        inputs = @(
            "LOCAL_TASKS/$LocalTaskId/LOCAL_TASK.json",
            "LOCAL_TASKS/$LocalTaskId/SPECULUM_REFINEMENTS.json if present"
        )
        expected_outputs = @(
            "Stage-specific evidence or updated task files.",
            "Stage receipt."
        )
        pass_criteria = @(
            "Stage output exists.",
            "Stage receipt exists.",
            "No raw secrets are committed.",
            "Owner can verify what changed."
        )
        fail_conditions = @(
            "Required input is missing.",
            "Output cannot be verified.",
            "Scope expands beyond Local Task without Owner approval."
        )
        status = "PLANNED"
        created_at = (Get-Date).ToString("o")
    }

    $StageJson = $StageRecord | ConvertTo-Json -Depth 20
    $StageHash = Get-Sha256String $StageJson

    Write-Utf8Bom (Join-Path $StageRoot "STAGE.json") $StageJson

    $StageMd = @"
# Stage

STAGE_ID:
$StageId

PARENT_LOCAL_TASK_ID:
$LocalTaskId

PARENT_GENERAL_TASK_ID:
$($LocalTask.parent_general_task_id)

TITLE:
$Title

PURPOSE:
$Hint

EXECUTION_MODE:
$($LocalTask.execution_mode)

ASSIGNED_ORGANS:
$($LocalTask.required_organs -join ", ")

STATUS:
PLANNED

HASH:
$StageHash
"@

    Write-Utf8Bom (Join-Path $StageRoot "STAGE.md") $StageMd

    $StageStatus = [ordered]@{
        stage_id = $StageId
        parent_local_task_id = $LocalTaskId
        status = "PLANNED"
        speculum_stage_review_status = "NOT_REQUESTED"
        ready_for_execution = $false
        updated_at = (Get-Date).ToString("o")
    }

    Write-Utf8Bom (Join-Path $StageRoot "STATUS.json") ($StageStatus | ConvertTo-Json -Depth 10)

    $Stages += [ordered]@{
        stage_id = $StageId
        title = $Title
        purpose = $Hint
        status = "PLANNED"
        hash = $StageHash
        path = "STAGE_MAPS/$LocalTaskId/STAGES/$StageId"
    }

    $Index++
}

$StageMap = [ordered]@{
    schema_version = "ASTRONOMICON_STAGE_MAP_V0_1"
    general_task_id = $LocalTask.parent_general_task_id
    local_task_id = $LocalTaskId
    local_task_title = $LocalTask.title
    local_task_hash = $LocalTask.hash
    speculum_local_refinement_status = $SpeculumStatus
    stage_count = $Stages.Count
    stages = $Stages
    status = "STAGE_MAP_CREATED"
    generated_at = (Get-Date).ToString("o")
}

$StageMapJson = $StageMap | ConvertTo-Json -Depth 20
Write-Utf8Bom (Join-Path $StageMapRoot "STAGE_MAP.json") $StageMapJson

$StageMapMd = @(
    "# Stage Map",
    "",
    "GENERAL_TASK_ID:",
    $LocalTask.parent_general_task_id,
    "",
    "LOCAL_TASK_ID:",
    $LocalTaskId,
    "",
    "LOCAL_TASK_TITLE:",
    $LocalTask.title,
    "",
    "STAGE_COUNT:",
    "$($Stages.Count)",
    "",
    "STATUS:",
    "STAGE_MAP_CREATED",
    "",
    "## Stages",
    ""
)

foreach ($Stage in $Stages) {
    $StageMapMd += "- $($Stage.stage_id): $($Stage.title)"
}

Write-Utf8Bom (Join-Path $StageMapRoot "STAGE_MAP.md") ($StageMapMd -join "`n")

$Receipt = [ordered]@{
    schema_version = "ASTRONOMICON_DECOMPOSE_LOCAL_TASK_TO_STAGES_RECEIPT_V0_1"
    general_task_id = $LocalTask.parent_general_task_id
    local_task_id = $LocalTaskId
    output_root = $OutputRoot
    stage_map_root = $StageMapRoot
    stage_count = $Stages.Count
    speculum_local_refinement_used = (Test-Path $SpeculumRefPath)
    status = "PASS_WITH_LIMITATIONS"
    limitations = @(
        "Simple decomposition script.",
        "Stage review by Speculum is not imported yet.",
        "Administratum readiness is not executed yet.",
        "Stages are planned, not executed."
    )
    generated_at = (Get-Date).ToString("o")
}

Write-Utf8Bom (Join-Path $StageMapRoot "DECOMPOSE_RECEIPT.json") ($Receipt | ConvertTo-Json -Depth 20)

# Update Local Task status
$LocalTaskStatus = [ordered]@{
    local_task_id = $LocalTaskId
    status = "STAGE_DECOMPOSED"
    speculum_review_status = $SpeculumStatus
    stage_decomposition_status = "DONE"
    stage_map_path = "STAGE_MAPS/$LocalTaskId/STAGE_MAP.json"
    stage_count = $Stages.Count
    updated_at = (Get-Date).ToString("o")
}

Write-Utf8Bom $LocalTaskStatusPath ($LocalTaskStatus | ConvertTo-Json -Depth 10)

Write-Host "Local Task decomposed to stages."
Write-Host "LOCAL_TASK_ID: $LocalTaskId"
Write-Host "STAGES: $($Stages.Count)"
Write-Host "STAGE_MAP_ROOT: $StageMapRoot"