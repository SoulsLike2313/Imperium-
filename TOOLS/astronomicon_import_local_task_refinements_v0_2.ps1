param(
    [Parameter(Mandatory = $true)]
    [string]$OutputRoot,

    [Parameter(Mandatory = $true)]
    [string]$RefinementsPath
)

$ErrorActionPreference = "Stop"
. "E:\IMPERIUM\TOOLS\astronomicon_pipeline_common_v0_2.ps1"

$registryPath = Join-Path $OutputRoot "LOCAL_TASK_REGISTRY.json"
if (-not (Test-Path -LiteralPath $registryPath)) {
    throw "LOCAL_TASK_REGISTRY.json not found: $registryPath"
}
if (-not (Test-Path -LiteralPath $RefinementsPath)) {
    throw "Refinements file not found: $RefinementsPath"
}

$registry = Read-JsonFile -Path $registryPath
$refinements = Read-JsonFile -Path $RefinementsPath

if ($refinements.schema_version -ne "ASTRONOMICON_SPECULUM_LOCAL_TASK_REFINEMENTS_V0_1") {
    throw "Invalid schema_version: $($refinements.schema_version). Expected ASTRONOMICON_SPECULUM_LOCAL_TASK_REFINEMENTS_V0_1."
}
if ($refinements.general_task_id -ne $registry.general_task_id) {
    throw "general_task_id mismatch. Registry=$($registry.general_task_id); Refinements=$($refinements.general_task_id)"
}

$known = @{}
foreach ($task in $registry.local_tasks) {
    $known[$task.local_task_id] = $true
}

$importRoot = Join-Path $OutputRoot "SPECULUM\IMPORTS\LOCAL_TASK_REFINEMENTS"
Ensure-Directory -Path $importRoot

$imported = @()
$orphans = @()

foreach ($item in $refinements.items) {
    $localTaskId = [string]$item.local_task_id
    if ([string]::IsNullOrWhiteSpace($localTaskId)) {
        $orphans += Get-OrphanRefinementRecord -RefinementItem $item -Reason "MISSING_local_task_id"
        continue
    }
    if (-not $known.ContainsKey($localTaskId)) {
        $orphans += Get-OrphanRefinementRecord -RefinementItem $item -Reason "UNKNOWN_local_task_id"
        continue
    }

    $taskRoot = Join-Path $OutputRoot "LOCAL_TASKS\$localTaskId"
    if (-not (Test-Path -LiteralPath $taskRoot)) {
        $orphans += Get-OrphanRefinementRecord -RefinementItem $item -Reason "TASK_ROOT_NOT_FOUND"
        continue
    }

    $refPath = Join-Path $taskRoot "SPECULUM_REFINEMENTS.json"
    $refMdPath = Join-Path $taskRoot "SPECULUM_REFINEMENTS.md"
    $statusPath = Join-Path $taskRoot "STATUS.json"

    $refRecord = [ordered]@{
        schema_version = "ASTRONOMICON_LOCAL_TASK_ATTACHED_SPECULUM_REFINEMENT_V0_2"
        general_task_id = $registry.general_task_id
        local_task_id = $localTaskId
        imported_from = $RefinementsPath
        review_mode = $refinements.review_mode
        allocation_rule = $refinements.allocation_rule
        refinement = $item
        imported_at = (Get-Date).ToString("o")
    }
    Write-JsonFile -Path $refPath -Object $refRecord -Depth 30

    $md = @(
        "# Speculum Local Task Refinements"
        ""
        "LOCAL_TASK_ID:"
        $localTaskId
        ""
        "GENERAL_TASK_ID:"
        $registry.general_task_id
        ""
        "RECOMMENDED_STATUS:"
        [string]$item.recommended_status
        ""
        "## Scope Narrowing"
    )
    foreach ($line in @($item.scope_narrowing)) { $md += "- $line" }
    $md += ""
    $md += "## Technical Execution Risks"
    foreach ($line in @($item.technical_execution_risks)) { $md += "- $line" }
    $md += ""
    $md += "## Missing Inputs"
    foreach ($line in @($item.missing_inputs)) { $md += "- $line" }
    $md += ""
    $md += "## Required Tools Or Scripts"
    foreach ($line in @($item.required_tools_or_scripts)) { $md += "- $line" }
    $md += ""
    $md += "## Readiness Questions"
    foreach ($line in @($item.readiness_questions)) { $md += "- $line" }
    $md += ""
    $md += "## Pass Criteria"
    foreach ($line in @($item.pass_criteria)) { $md += "- $line" }
    $md += ""
    $md += "## Fail Conditions"
    foreach ($line in @($item.fail_conditions)) { $md += "- $line" }
    $md += ""
    $md += "## Do Not Do"
    foreach ($line in @($item.do_not_do)) { $md += "- $line" }
    $md += ""
    $md += "## Decomposition Hints"
    foreach ($line in @($item.decomposition_hints)) { $md += "- $line" }
    $md += ""
    $md += "SHOULD_SPLIT:"
    $md += [string]$item.should_split

    Write-Utf8Bom -Path $refMdPath -Content ($md -join "`n")

    Update-StatusFile -StatusPath $statusPath -Patch @{
        local_task_id = $localTaskId
        speculum_review_status = "IMPORTED"
        speculum_local_refinement_status = "IMPORTED"
        recommended_status = [string]$item.recommended_status
        status = "SPECULUM_REFINED"
        ready_for_stage_decomposition = ([string]$item.recommended_status -eq "READY_FOR_STAGE_DECOMPOSITION")
    }

    $imported += [ordered]@{
        local_task_id = $localTaskId
        refinement_path = $refPath
        refinement_md_path = $refMdPath
        status_path = $statusPath
        recommended_status = [string]$item.recommended_status
    }
}

$orphansPath = Join-Path $importRoot "ORPHAN_REFINEMENTS.json"
$orphansRecord = [ordered]@{
    schema_version = "ASTRONOMICON_ORPHAN_LOCAL_TASK_REFINEMENTS_V0_2"
    general_task_id = $registry.general_task_id
    orphans = $orphans
    orphan_count = $orphans.Count
    generated_at = (Get-Date).ToString("o")
}
Write-JsonFile -Path $orphansPath -Object $orphansRecord -Depth 40

$receipt = [ordered]@{
    schema_version = "ASTRONOMICON_IMPORT_LOCAL_TASK_REFINEMENTS_RECEIPT_V0_2"
    general_task_id = $registry.general_task_id
    refinements_path = $RefinementsPath
    imported_count = $imported.Count
    orphan_count = $orphans.Count
    imported = $imported
    orphan_refinements_path = $orphansPath
    status = $(if ($orphans.Count -eq 0) { "IMPORTED" } else { "IMPORTED_WITH_ORPHANS" })
    generated_at = (Get-Date).ToString("o")
}
$receiptPath = Join-Path $importRoot "IMPORT_LOCAL_TASK_REFINEMENTS_RECEIPT.json"
Write-JsonFile -Path $receiptPath -Object $receipt -Depth 40

Write-Host "Speculum Local Task refinements imported."
Write-Host "Imported: $($imported.Count)"
Write-Host "Orphans: $($orphans.Count)"
Write-Host "Receipt: $receiptPath"
