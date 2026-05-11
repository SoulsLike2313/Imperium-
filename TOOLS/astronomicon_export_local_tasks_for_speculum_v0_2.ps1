param(
    [Parameter(Mandatory = $true)]
    [string]$OutputRoot
)

$ErrorActionPreference = "Stop"
. "E:\IMPERIUM\TOOLS\astronomicon_pipeline_common_v0_2.ps1"

$registryPath = Join-Path $OutputRoot "LOCAL_TASK_REGISTRY.json"
if (-not (Test-Path -LiteralPath $registryPath)) {
    throw "LOCAL_TASK_REGISTRY.json not found: $registryPath"
}

$registry = Read-JsonFile -Path $registryPath

$exportRoot = Join-Path $OutputRoot "SPECULUM"
Ensure-Directory -Path $exportRoot

$exportPath = Join-Path $exportRoot "SPECULUM_LOCAL_TASK_REVIEW_REQUEST.json"
$instructionsPath = Join-Path $exportRoot "SPECULUM_LOCAL_TASK_REVIEW_INSTRUCTIONS.md"
$receiptPath = Join-Path $exportRoot "EXPORT_LOCAL_TASKS_RECEIPT.json"

$items = @()
foreach ($task in $registry.local_tasks) {
    $items += [ordered]@{
        local_task_id = $task.local_task_id
        source_plan_item_id = $task.source_plan_item_id
        title = $task.title
        execution_mode = $task.execution_mode
        required_organs = $task.required_organs
        expected_output = $task.expected_output
        hash = $task.hash
        review_questions = @(
            "Is this Local Task technically executable?"
            "What scope must be narrowed?"
            "What inputs are missing?"
            "What tools or scripts are required?"
            "What readiness questions must be answered before execution?"
            "What pass criteria are required?"
            "What fail conditions must stop execution?"
            "What must not be done?"
            "How should this Local Task be decomposed into stages?"
        )
    }
}

$payload = [ordered]@{
    schema_version = "ASTRONOMICON_SPECULUM_LOCAL_TASK_REVIEW_REQUEST_V0_2"
    general_task_id = $registry.general_task_id
    instruction = "Review every Local Task evenly and return JSON only."
    expected_response_schema = "ASTRONOMICON_SPECULUM_LOCAL_TASK_REFINEMENTS_V0_1"
    review_mode = "hard_red_team_scope_narrowing"
    allocation_rule = "Distribute review effort evenly across all local tasks."
    do_not_do = @(
        "Do not rewrite local task core records."
        "Do not return prose outside JSON."
        "Do not invent missing task IDs."
        "Do not include secrets."
    )
    local_tasks = $items
    generated_at = (Get-Date).ToString("o")
}
Write-JsonFile -Path $exportPath -Object $payload -Depth 25

$instructions = @"
# Speculum Local Task Review Instructions

Return JSON only.

Expected response schema:
ASTRONOMICON_SPECULUM_LOCAL_TASK_REFINEMENTS_V0_1

Required item fields:
- local_task_id
- scope_narrowing
- technical_execution_risks
- missing_inputs
- required_tools_or_scripts
- readiness_questions
- pass_criteria
- fail_conditions
- do_not_do
- decomposition_hints
- should_split
- recommended_status

Input file:
$exportPath

Output file name:
SPECULUM_LOCAL_TASK_REFINEMENTS.json
"@
Write-Utf8Bom -Path $instructionsPath -Content $instructions

$receipt = [ordered]@{
    schema_version = "ASTRONOMICON_EXPORT_LOCAL_TASKS_FOR_SPECULUM_RECEIPT_V0_2"
    general_task_id = $registry.general_task_id
    local_task_count = $registry.local_task_count
    export_path = $exportPath
    instructions_path = $instructionsPath
    status = "EXPORTED"
    generated_at = (Get-Date).ToString("o")
}
Write-JsonFile -Path $receiptPath -Object $receipt -Depth 20

Write-Host "Speculum Local Task review export created."
Write-Host $exportPath
Write-Host $instructionsPath
Write-Host $receiptPath
