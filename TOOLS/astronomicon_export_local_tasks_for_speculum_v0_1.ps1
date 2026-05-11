param(
    [Parameter(Mandatory=$true)]
    [string]$OutputRoot
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

$RegistryPath = Join-Path $OutputRoot "LOCAL_TASK_REGISTRY.json"

if (!(Test-Path $RegistryPath)) {
    throw "LOCAL_TASK_REGISTRY.json not found: $RegistryPath"
}

$Registry = Get-Content -Encoding UTF8 $RegistryPath -Raw | ConvertFrom-Json

$ExportRoot = Join-Path $OutputRoot "SPECULUM"
New-Item -ItemType Directory -Force $ExportRoot | Out-Null

$ExportPath = Join-Path $ExportRoot "SPECULUM_LOCAL_TASK_REVIEW_REQUEST.json"
$InstructionsPath = Join-Path $ExportRoot "SPECULUM_LOCAL_TASK_REVIEW_INSTRUCTIONS.md"
$ReceiptPath = Join-Path $ExportRoot "EXPORT_LOCAL_TASKS_RECEIPT.json"

$Items = @()

foreach ($Task in $Registry.local_tasks) {
    $Items += [ordered]@{
        local_task_id = $Task.local_task_id
        source_plan_item_id = $Task.source_plan_item_id
        title = $Task.title
        execution_mode = $Task.execution_mode
        required_organs = $Task.required_organs
        expected_output = $Task.expected_output
        hash = $Task.hash
        review_questions = @(
            "Is this Local Task technically executable?",
            "What scope must be narrowed?",
            "What inputs are missing?",
            "What tools or scripts are required?",
            "What readiness questions must be answered before execution?",
            "What pass criteria are required?",
            "What fail conditions must stop execution?",
            "What must not be done?",
            "How should this Local Task be decomposed into stages?"
        )
    }
}

$Payload = [ordered]@{
    schema_version = "ASTRONOMICON_SPECULUM_LOCAL_TASK_REVIEW_REQUEST_V0_1"
    general_task_id = $Registry.general_task_id
    instruction = "Review every Local Task evenly. Return JSON only, matching ASTRONOMICON_SPECULUM_LOCAL_TASK_REFINEMENTS_V0_1."
    allocation_rule = "Distribute review effort evenly across all local tasks. Do not focus only on the first task."
    do_not_do = @(
        "Do not rewrite the task map.",
        "Do not return prose outside JSON.",
        "Do not invent missing task IDs.",
        "Do not declare green/canon/ready without pass criteria.",
        "Do not include raw secrets."
    )
    expected_response_schema = [ordered]@{
        schema_version = "ASTRONOMICON_SPECULUM_LOCAL_TASK_REFINEMENTS_V0_1"
        general_task_id = $Registry.general_task_id
        review_mode = "hard_red_team_scope_narrowing"
        allocation_rule = "Distribute review effort evenly across all local tasks."
        items = @(
            [ordered]@{
                local_task_id = "LTASK-001"
                scope_narrowing = @()
                technical_execution_risks = @()
                missing_inputs = @()
                required_tools_or_scripts = @()
                readiness_questions = @()
                pass_criteria = @()
                fail_conditions = @()
                do_not_do = @()
                decomposition_hints = @()
                should_split = $false
                recommended_status = "READY_FOR_STAGE_DECOMPOSITION"
            }
        )
    }
    local_tasks = $Items
    generated_at = (Get-Date).ToString("o")
}

Write-Utf8Bom $ExportPath ($Payload | ConvertTo-Json -Depth 20)

$Instructions = @"
# Speculum Local Task Review Instructions

Return JSON only.

Role:
Logos-Speculum

Mode:
Hard red-team technical execution review.

Rules:
- Review every Local Task evenly.
- Do not focus only on the first task.
- Do not rewrite tasks.
- Do not produce prose outside JSON.
- Do not invent task IDs.
- Do not declare green/canon/ready without pass criteria.
- Return only JSON matching schema: ASTRONOMICON_SPECULUM_LOCAL_TASK_REFINEMENTS_V0_1.
- All output must be in English.

Input file:
$ExportPath

Expected response file:
SPECULUM_LOCAL_TASK_REFINEMENTS.json
"@

Write-Utf8Bom $InstructionsPath $Instructions

$Receipt = [ordered]@{
    schema_version = "ASTRONOMICON_EXPORT_LOCAL_TASKS_FOR_SPECULUM_RECEIPT_V0_1"
    general_task_id = $Registry.general_task_id
    local_task_count = $Registry.local_task_count
    export_path = $ExportPath
    instructions_path = $InstructionsPath
    status = "PASS_WITH_LIMITATIONS"
    limitations = @(
        "Export only.",
        "Speculum response import is separate.",
        "No stage decomposition in this script."
    )
    generated_at = (Get-Date).ToString("o")
}

Write-Utf8Bom $ReceiptPath ($Receipt | ConvertTo-Json -Depth 10)

Write-Host "Speculum Local Task review export created:"
Write-Host $ExportPath
Write-Host $InstructionsPath
Write-Host $ReceiptPath