param(
    [Parameter(Mandatory = $true)]
    [string]$OutputRoot,

    [Parameter(Mandatory = $true)]
    [string]$LocalTaskId,

    [Parameter(Mandatory = $true)]
    [string]$RefinementsPath
)

$ErrorActionPreference = "Stop"
. "E:\IMPERIUM\TOOLS\astronomicon_pipeline_common_v0_2.ps1"

$stageMapRoot = Join-Path $OutputRoot "STAGE_MAPS\$LocalTaskId"
$stageMapPath = Join-Path $stageMapRoot "STAGE_MAP.json"
if (-not (Test-Path -LiteralPath $stageMapPath)) {
    throw "STAGE_MAP.json not found: $stageMapPath"
}
if (-not (Test-Path -LiteralPath $RefinementsPath)) {
    throw "Refinements file not found: $RefinementsPath"
}

$stageMap = Read-JsonFile -Path $stageMapPath
$refinements = Read-JsonFile -Path $RefinementsPath

if ($refinements.schema_version -ne "ASTRONOMICON_SPECULUM_STAGE_REFINEMENTS_V0_1") {
    throw "Invalid schema_version: $($refinements.schema_version). Expected ASTRONOMICON_SPECULUM_STAGE_REFINEMENTS_V0_1."
}
if ($refinements.general_task_id -ne $stageMap.general_task_id) {
    throw "general_task_id mismatch. StageMap=$($stageMap.general_task_id); Refinements=$($refinements.general_task_id)"
}

$knownStages = @{}
foreach ($stage in $stageMap.stages) {
    $knownStages[$stage.stage_id] = $stage.path
}

$importRoot = Join-Path $OutputRoot "SPECULUM\IMPORTS\STAGE_REFINEMENTS\$LocalTaskId"
Ensure-Directory -Path $importRoot

$imported = @()
$orphans = @()

foreach ($item in $refinements.items) {
    $stageId = [string]$item.stage_id
    if ([string]::IsNullOrWhiteSpace($stageId)) {
        $orphans += Get-OrphanRefinementRecord -RefinementItem $item -Reason "MISSING_stage_id"
        continue
    }
    if (-not $knownStages.ContainsKey($stageId)) {
        $orphans += Get-OrphanRefinementRecord -RefinementItem $item -Reason "UNKNOWN_stage_id"
        continue
    }

    $stagePath = $knownStages[$stageId]
    $stageRoot = Join-Path $OutputRoot ($stagePath.Replace("/", "\"))
    if (-not (Test-Path -LiteralPath $stageRoot)) {
        $orphans += Get-OrphanRefinementRecord -RefinementItem $item -Reason "STAGE_ROOT_NOT_FOUND"
        continue
    }

    $attachedJsonPath = Join-Path $stageRoot "SPECULUM_STAGE_REFINEMENTS.json"
    $attachedMdPath = Join-Path $stageRoot "SPECULUM_STAGE_REFINEMENTS.md"
    $statusPath = Join-Path $stageRoot "STATUS.json"

    $record = [ordered]@{
        schema_version = "ASTRONOMICON_STAGE_ATTACHED_SPECULUM_REFINEMENT_V0_1"
        general_task_id = $stageMap.general_task_id
        local_task_id = $LocalTaskId
        stage_id = $stageId
        imported_from = $RefinementsPath
        refinement = $item
        imported_at = (Get-Date).ToString("o")
    }
    Write-JsonFile -Path $attachedJsonPath -Object $record -Depth 30

    $md = @(
        "# Speculum Stage Refinements"
        ""
        "STAGE_ID:"
        $stageId
        ""
        "GENERAL_TASK_ID:"
        $stageMap.general_task_id
        ""
        "LOCAL_TASK_ID:"
        $LocalTaskId
        ""
        "RECOMMENDED_STATUS:"
        [string]$item.recommended_status
        ""
        "## Execution Risks"
    )
    foreach ($line in @($item.execution_risks)) { $md += "- $line" }
    $md += ""
    $md += "## Missing Inputs"
    foreach ($line in @($item.missing_inputs)) { $md += "- $line" }
    $md += ""
    $md += "## Missing Tools Or Scripts"
    foreach ($line in @($item.missing_tools_or_scripts)) { $md += "- $line" }
    $md += ""
    $md += "## Required Evidence"
    foreach ($line in @($item.required_evidence)) { $md += "- $line" }
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
    $md += "## Manual Safety Notes"
    foreach ($line in @($item.manual_safety_notes)) { $md += "- $line" }
    $md += ""
    $md += "SHOULD_SPLIT:"
    $md += [string]$item.should_split

    Write-Utf8Bom -Path $attachedMdPath -Content ($md -join "`n")

    Update-StatusFile -StatusPath $statusPath -Patch @{
        stage_id = $stageId
        speculum_stage_review_status = "IMPORTED"
        status = "SPECULUM_STAGE_REFINED"
        recommended_status = [string]$item.recommended_status
        ready_for_execution = ([string]$item.recommended_status -eq "READY_FOR_EXECUTION")
    }

    $imported += [ordered]@{
        stage_id = $stageId
        stage_root = $stageRoot
        attached_json_path = $attachedJsonPath
        attached_md_path = $attachedMdPath
        status_path = $statusPath
        recommended_status = [string]$item.recommended_status
    }
}

$orphansPath = Join-Path $importRoot "ORPHAN_REFINEMENTS.json"
$orphansRecord = [ordered]@{
    schema_version = "ASTRONOMICON_ORPHAN_STAGE_REFINEMENTS_V0_1"
    general_task_id = $stageMap.general_task_id
    local_task_id = $LocalTaskId
    orphan_count = $orphans.Count
    orphans = $orphans
    generated_at = (Get-Date).ToString("o")
}
Write-JsonFile -Path $orphansPath -Object $orphansRecord -Depth 40

$receipt = [ordered]@{
    schema_version = "ASTRONOMICON_IMPORT_STAGE_REFINEMENTS_RECEIPT_V0_1"
    general_task_id = $stageMap.general_task_id
    local_task_id = $LocalTaskId
    refinements_path = $RefinementsPath
    imported_count = $imported.Count
    orphan_count = $orphans.Count
    imported = $imported
    orphan_refinements_path = $orphansPath
    status = $(if ($orphans.Count -eq 0) { "IMPORTED" } else { "IMPORTED_WITH_ORPHANS" })
    generated_at = (Get-Date).ToString("o")
}
$receiptPath = Join-Path $importRoot "IMPORT_STAGE_REFINEMENTS_RECEIPT.json"
Write-JsonFile -Path $receiptPath -Object $receipt -Depth 40

Write-Host "Speculum Stage refinements imported."
Write-Host "Imported: $($imported.Count)"
Write-Host "Orphans: $($orphans.Count)"
Write-Host "Receipt: $receiptPath"
