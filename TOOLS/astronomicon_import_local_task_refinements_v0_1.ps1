param(
    [Parameter(Mandatory=$true)]
    [string]$OutputRoot,

    [Parameter(Mandatory=$true)]
    [string]$RefinementsPath
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

if (!(Test-Path $RefinementsPath)) {
    throw "Refinements file not found: $RefinementsPath"
}

$Registry = Get-Content -Encoding UTF8 $RegistryPath -Raw | ConvertFrom-Json
$Refinements = Get-Content -Encoding UTF8 $RefinementsPath -Raw | ConvertFrom-Json

if ($Refinements.schema_version -ne "ASTRONOMICON_SPECULUM_LOCAL_TASK_REFINEMENTS_V0_1") {
    throw "Invalid schema_version: $($Refinements.schema_version)"
}

if ($Refinements.general_task_id -ne $Registry.general_task_id) {
    throw "general_task_id mismatch. Registry=$($Registry.general_task_id), Refinements=$($Refinements.general_task_id)"
}

$KnownIds = @{}
foreach ($Task in $Registry.local_tasks) {
    $KnownIds[$Task.local_task_id] = $true
}

$ImportRoot = Join-Path $OutputRoot "SPECULUM\IMPORTS\LOCAL_TASK_REFINEMENTS"
New-Item -ItemType Directory -Force $ImportRoot | Out-Null

$Imported = @()
$Orphans = @()

foreach ($Item in $Refinements.items) {
    $LocalTaskId = $Item.local_task_id

    if (!$KnownIds.ContainsKey($LocalTaskId)) {
        $Orphans += $Item
        continue
    }

    $TaskRoot = Join-Path $OutputRoot "LOCAL_TASKS\$LocalTaskId"
    if (!(Test-Path $TaskRoot)) {
        $Orphans += $Item
        continue
    }

    $RefPath = Join-Path $TaskRoot "SPECULUM_REFINEMENTS.json"
    $RefMdPath = Join-Path $TaskRoot "SPECULUM_REFINEMENTS.md"
    $StatusPath = Join-Path $TaskRoot "STATUS.json"

    $RefRecord = [ordered]@{
        schema_version = "ASTRONOMICON_LOCAL_TASK_ATTACHED_SPECULUM_REFINEMENT_V0_1"
        general_task_id = $Registry.general_task_id
        local_task_id = $LocalTaskId
        imported_from = $RefinementsPath
        review_mode = $Refinements.review_mode
        allocation_rule = $Refinements.allocation_rule
        refinement = $Item
        imported_at = (Get-Date).ToString("o")
    }

    Write-Utf8Bom $RefPath ($RefRecord | ConvertTo-Json -Depth 20)

    $Md = @"
# Speculum Refinements

LOCAL_TASK_ID:
$LocalTaskId

GENERAL_TASK_ID:
$($Registry.general_task_id)

RECOMMENDED_STATUS:
$($Item.recommended_status)

## Scope Narrowing
$($Item.scope_narrowing | ForEach-Object { "- $_" } | Out-String)

## Technical Execution Risks
$($Item.technical_execution_risks | ForEach-Object { "- $_" } | Out-String)

## Missing Inputs
$($Item.missing_inputs | ForEach-Object { "- $_" } | Out-String)

## Required Tools Or Scripts
$($Item.required_tools_or_scripts | ForEach-Object { "- $_" } | Out-String)

## Readiness Questions
$($Item.readiness_questions | ForEach-Object { "- $_" } | Out-String)

## Pass Criteria
$($Item.pass_criteria | ForEach-Object { "- $_" } | Out-String)

## Fail Conditions
$($Item.fail_conditions | ForEach-Object { "- $_" } | Out-String)

## Do Not Do
$($Item.do_not_do | ForEach-Object { "- $_" } | Out-String)

## Decomposition Hints
$($Item.decomposition_hints | ForEach-Object { "- $_" } | Out-String)

SHOULD_SPLIT:
$($Item.should_split)
"@

    Write-Utf8Bom $RefMdPath $Md

    $Status = [ordered]@{
        local_task_id = $LocalTaskId
        status = "SPECULUM_REFINED"
        speculum_review_status = "IMPORTED"
        recommended_status = $Item.recommended_status
        ready_for_stage_decomposition = ($Item.recommended_status -eq "READY_FOR_STAGE_DECOMPOSITION")
        updated_at = (Get-Date).ToString("o")
    }

    Write-Utf8Bom $StatusPath ($Status | ConvertTo-Json -Depth 10)

    $Imported += [ordered]@{
        local_task_id = $LocalTaskId
        refinement_path = $RefPath
        refinement_md_path = $RefMdPath
        status_path = $StatusPath
        recommended_status = $Item.recommended_status
    }
}

$ImportReceipt = [ordered]@{
    schema_version = "ASTRONOMICON_IMPORT_LOCAL_TASK_REFINEMENTS_RECEIPT_V0_1"
    general_task_id = $Registry.general_task_id
    refinements_path = $RefinementsPath
    imported_count = $Imported.Count
    orphan_count = $Orphans.Count
    imported = $Imported
    orphans = $Orphans
    status = $(if ($Orphans.Count -eq 0) { "PASS_WITH_LIMITATIONS" } else { "PASS_WITH_ORPHANS" })
    limitations = @(
        "Import only.",
        "Existing Local Task core records are not overwritten.",
        "Stage decomposition is separate.",
        "Dashboard integration is separate."
    )
    generated_at = (Get-Date).ToString("o")
}

$ReceiptPath = Join-Path $ImportRoot "IMPORT_LOCAL_TASK_REFINEMENTS_RECEIPT.json"
Write-Utf8Bom $ReceiptPath ($ImportReceipt | ConvertTo-Json -Depth 20)

Write-Host "Speculum Local Task refinements imported."
Write-Host "Imported: $($Imported.Count)"
Write-Host "Orphans: $($Orphans.Count)"
Write-Host "Receipt: $ReceiptPath"