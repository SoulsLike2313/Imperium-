param(
    [Parameter(Mandatory = $true)]
    [string]$OutputRoot,

    [Parameter(Mandatory = $true)]
    [string]$LocalTaskId
)

$ErrorActionPreference = "Stop"
. "E:\IMPERIUM\TOOLS\astronomicon_pipeline_common_v0_2.ps1"

$stageMapRoot = Join-Path $OutputRoot "STAGE_MAPS\$LocalTaskId"
$stageMapPath = Join-Path $stageMapRoot "STAGE_MAP.json"
if (-not (Test-Path -LiteralPath $stageMapPath)) {
    throw "STAGE_MAP.json not found: $stageMapPath"
}

$stageMap = Read-JsonFile -Path $stageMapPath

$items = @()
foreach ($stage in $stageMap.stages) {
    $stageJsonPath = Join-Path $OutputRoot ($stage.path.Replace("/", "\") + "\STAGE.json")
    if (-not (Test-Path -LiteralPath $stageJsonPath)) {
        continue
    }
    $stageRecord = Read-JsonFile -Path $stageJsonPath
    $items += [ordered]@{
        stage_id = $stageRecord.stage_id
        parent_local_task_id = $stageRecord.parent_local_task_id
        title = $stageRecord.title
        purpose = $stageRecord.purpose
        execution_mode = $stageRecord.execution_mode
        assigned_organs = $stageRecord.assigned_organs
        inputs = $stageRecord.inputs
        expected_outputs = $stageRecord.expected_outputs
        pass_criteria = $stageRecord.pass_criteria
        fail_conditions = $stageRecord.fail_conditions
    }
}

$speculumRoot = Join-Path $OutputRoot "SPECULUM"
Ensure-Directory -Path $speculumRoot
$stageSpeculumRoot = Join-Path $speculumRoot "STAGE_REVIEW"
Ensure-Directory -Path $stageSpeculumRoot

$exportPath = Join-Path $stageSpeculumRoot "SPECULUM_STAGE_REVIEW_REQUEST_$LocalTaskId.json"
$instructionsPath = Join-Path $stageSpeculumRoot "SPECULUM_STAGE_REVIEW_INSTRUCTIONS_$LocalTaskId.md"
$receiptPath = Join-Path $stageSpeculumRoot "EXPORT_STAGE_REVIEW_RECEIPT_$LocalTaskId.json"

$payload = [ordered]@{
    schema_version = "ASTRONOMICON_SPECULUM_STAGE_REVIEW_REQUEST_V0_1"
    general_task_id = $stageMap.general_task_id
    local_task_id = $LocalTaskId
    instruction = "Review every stage for technical execution risk and return JSON only."
    expected_response_schema = "ASTRONOMICON_SPECULUM_STAGE_REFINEMENTS_V0_1"
    items = $items
    generated_at = (Get-Date).ToString("o")
}
Write-JsonFile -Path $exportPath -Object $payload -Depth 30

$instructions = @"
# Speculum Stage Review Instructions

Return JSON only.

Expected response schema:
ASTRONOMICON_SPECULUM_STAGE_REFINEMENTS_V0_1

Required item fields:
- stage_id
- execution_risks
- missing_inputs
- missing_tools_or_scripts
- required_evidence
- pass_criteria
- fail_conditions
- do_not_do
- manual_safety_notes
- should_split
- recommended_status

Input file:
$exportPath

Output file name:
SPECULUM_STAGE_REFINEMENTS_$LocalTaskId.json
"@
Write-Utf8Bom -Path $instructionsPath -Content $instructions

$receipt = [ordered]@{
    schema_version = "ASTRONOMICON_EXPORT_STAGE_MAP_FOR_SPECULUM_RECEIPT_V0_1"
    general_task_id = $stageMap.general_task_id
    local_task_id = $LocalTaskId
    stage_count = $items.Count
    export_path = $exportPath
    instructions_path = $instructionsPath
    status = "EXPORTED"
    generated_at = (Get-Date).ToString("o")
}
Write-JsonFile -Path $receiptPath -Object $receipt -Depth 20

Write-Host "Stage review export created."
Write-Host $exportPath
Write-Host $instructionsPath
Write-Host $receiptPath
