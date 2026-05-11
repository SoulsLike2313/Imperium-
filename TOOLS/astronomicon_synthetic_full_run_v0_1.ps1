param(
    [string]$RepoRoot = "E:\IMPERIUM",
    [string]$GeneralTasksRoot = "E:\IMPERIUM\ASTRONOMICON\GENERAL_TASKS",
    [string]$SyntheticPrefix = "GTASK-SYNTH",
    [string]$OutputRoot = "E:\IMPERIUM\ARTIFACTS\ASTRONOMICON_SYNTHETIC_RUN",
    [int]$TaskCount = 3
)

$ErrorActionPreference = "Stop"
. "E:\IMPERIUM\TOOLS\astronomicon_pipeline_common_v0_2.ps1"

if ($TaskCount -lt 1) {
    throw "TaskCount must be >= 1"
}

Ensure-Directory -Path $OutputRoot
Ensure-Directory -Path $GeneralTasksRoot

$logPath = Join-Path $OutputRoot "SYNTHETIC_RUN_LOG.txt"
Write-Utf8Bom -Path $logPath -Content ""

function Write-RunLog {
    param([string]$Message)
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message
    Add-Content -LiteralPath $logPath -Value $line -Encoding UTF8
    Write-Host $line
}

function Invoke-ScriptSafe {
    param(
        [Parameter(Mandatory = $true)][string]$ScriptPath,
        [Parameter(Mandatory = $true)][string[]]$Arguments
    )
    $psArgs = @("-ExecutionPolicy", "Bypass", "-File", $ScriptPath) + $Arguments
    $result = & powershell.exe @psArgs 2>&1 | Out-String
    $exit = $LASTEXITCODE
    return [ordered]@{
        script = $ScriptPath
        arguments = $Arguments
        exit_code = $exit
        output = $result.Trim()
    }
}

function New-SyntheticGeneralTaskText {
    param(
        [Parameter(Mandatory = $true)][string]$GeneralTaskId,
        [Parameter(Mandatory = $true)][string]$Code,
        [Parameter(Mandatory = $true)][string]$Title
    )
    return @"
ASTRONOMICON_GENERAL_TASK_V0_1
ENCODING: UTF-8-BOM
LINE_ENDINGS: CRLF

GENERAL_TASK_ID:
$GeneralTaskId

GENERAL_TASK_TITLE:
$Title

GENERAL_TASK_CODE:
$Code

AUTHOR:
SyntheticRunner

EXECUTION_INTENT:
scripted

PRIORITY:
high

BEGIN_GOAL
Build a complete synthetic planning run with evidence artifacts.
END_GOAL

BEGIN_CONTEXT
This synthetic task validates parser, Speculum exchange, decomposition, and stage refinement import.
END_CONTEXT

BEGIN_CURRENT_PROBLEM
Need an automated full-run verification path to expose hidden fragility.
END_CURRENT_PROBLEM

BEGIN_EXPECTED_FINAL_STATE
- Local tasks are parsed.
- Local and stage Speculum refinements are imported.
- Receipts are present.
END_EXPECTED_FINAL_STATE

BEGIN_HARD_CONSTRAINTS
- No fake green signals.
- No secret leakage.
- Evidence-first execution.
END_HARD_CONSTRAINTS

BEGIN_DO_NOT_DO
- Do not modify core records during Speculum import.
- Do not drop unknown IDs silently.
END_DO_NOT_DO

BEGIN_PLAN_ITEMS

ITEM_ID: PI-001
TITLE: Build synthetic local task one
TEXT:
Generate first synthetic local task for pipeline validation.
EXPECTED_OUTPUT:
Local Task record and readiness fields.
REQUIRED_ORGANS:
Astronomicon, Administratum
EXECUTION_MODE:
scripted
DEPENDS_ON:
none
END_ITEM

ITEM_ID: PI-002
TITLE: Build synthetic local task two
TEXT:
Generate second synthetic local task for pipeline validation.
EXPECTED_OUTPUT:
Local Task record and readiness fields.
REQUIRED_ORGANS:
Astronomicon, Mechanicus
EXECUTION_MODE:
scripted
DEPENDS_ON:
PI-001
END_ITEM

ITEM_ID: PI-003
TITLE: Build synthetic local task three
TEXT:
Generate third synthetic local task for pipeline validation.
EXPECTED_OUTPUT:
Local Task record and readiness fields.
REQUIRED_ORGANS:
Astronomicon, Speculum
EXECUTION_MODE:
manual
DEPENDS_ON:
PI-002
END_ITEM

END_PLAN_ITEMS

BEGIN_KNOWN_RISKS
- Schema mismatch in simulated reviews.
- Unknown refinement IDs.
END_KNOWN_RISKS

BEGIN_REQUIRED_ORGANS
- Astronomicon
- Speculum
END_REQUIRED_ORGANS

BEGIN_REQUIRED_INPUTS
- Synthetic strict task input text.
END_REQUIRED_INPUTS

BEGIN_EXPECTED_ARTIFACTS
- Parse receipts.
- Import receipts.
- Stage map receipts.
END_EXPECTED_ARTIFACTS

BEGIN_OWNER_NOTES
Synthetic run for automated stress validation.
END_OWNER_NOTES
"@
}

function New-SimulatedLocalRefinements {
    param(
        [Parameter(Mandatory = $true)][string]$GeneralTaskId,
        [Parameter(Mandatory = $true)]$Registry,
        [bool]$IncludeOrphan = $false
    )
    $items = @()
    foreach ($task in $Registry.local_tasks) {
        $items += [ordered]@{
            local_task_id = $task.local_task_id
            scope_narrowing = @("Keep scope restricted to $($task.local_task_id).")
            technical_execution_risks = @("Dependency drift can break reproducibility.")
            missing_inputs = @("Confirm target output directory exists.")
            required_tools_or_scripts = @("PowerShell 5+", "astronomicon_decompose_local_task_to_stages_v0_2.ps1")
            readiness_questions = @("Is evidence path defined?")
            pass_criteria = @("Outputs exist and hashes are verifiable.")
            fail_conditions = @("Any required file is missing.")
            do_not_do = @("Do not alter unrelated tasks.")
            decomposition_hints = @(
                "Prepare inputs and guardrails."
                "Apply technical change and collect evidence."
                "Finalize and verify evidence."
            )
            should_split = $false
            recommended_status = "READY_FOR_STAGE_DECOMPOSITION"
        }
    }
    if ($IncludeOrphan) {
        $items += [ordered]@{
            local_task_id = "LTASK-999"
            scope_narrowing = @("Orphan test")
            technical_execution_risks = @("Orphan test")
            missing_inputs = @("Orphan test")
            required_tools_or_scripts = @("Orphan test")
            readiness_questions = @("Orphan test")
            pass_criteria = @("Orphan test")
            fail_conditions = @("Orphan test")
            do_not_do = @("Orphan test")
            decomposition_hints = @("Orphan test")
            should_split = $false
            recommended_status = "BLOCKED"
        }
    }

    return [ordered]@{
        schema_version = "ASTRONOMICON_SPECULUM_LOCAL_TASK_REFINEMENTS_V0_1"
        general_task_id = $GeneralTaskId
        review_mode = "hard_red_team_scope_narrowing"
        allocation_rule = "Distribute review effort evenly across all local tasks."
        items = $items
    }
}

function New-SimulatedStageRefinements {
    param(
        [Parameter(Mandatory = $true)][string]$GeneralTaskId,
        [Parameter(Mandatory = $true)][string]$LocalTaskId,
        [Parameter(Mandatory = $true)]$StageMap,
        [bool]$IncludeOrphan = $false
    )
    $items = @()
    foreach ($stage in $StageMap.stages) {
        $items += [ordered]@{
            stage_id = $stage.stage_id
            execution_risks = @("Evidence may be incomplete without explicit checklist.")
            missing_inputs = @("Confirm stage input files exist before execution.")
            missing_tools_or_scripts = @("No extra tools required for synthetic run.")
            required_evidence = @("Stage output file", "Stage receipt")
            pass_criteria = @("Stage output and receipt exist.")
            fail_conditions = @("Missing output or missing receipt.")
            do_not_do = @("Do not mutate unrelated stage records.")
            manual_safety_notes = @("Validate before declaring ready.")
            should_split = $false
            recommended_status = "READY_FOR_EXECUTION"
        }
    }
    if ($IncludeOrphan) {
        $items += [ordered]@{
            stage_id = "STAGE-999"
            execution_risks = @("Orphan stage test")
            missing_inputs = @("Orphan stage test")
            missing_tools_or_scripts = @("Orphan stage test")
            required_evidence = @("Orphan stage test")
            pass_criteria = @("Orphan stage test")
            fail_conditions = @("Orphan stage test")
            do_not_do = @("Orphan stage test")
            manual_safety_notes = @("Orphan stage test")
            should_split = $false
            recommended_status = "BLOCKED"
        }
    }

    return [ordered]@{
        schema_version = "ASTRONOMICON_SPECULUM_STAGE_REFINEMENTS_V0_1"
        general_task_id = $GeneralTaskId
        local_task_id = $LocalTaskId
        review_mode = "hard_red_team_stage_readiness"
        items = $items
    }
}

$summary = [ordered]@{
    schema_version = "ASTRONOMICON_SYNTHETIC_FULL_RUN_SUMMARY_V0_1"
    total_synthetic_general_tasks = 0
    total_local_tasks = 0
    total_stage_maps = 0
    total_stages = 0
    imports_passed = 0
    orphans = 0
    blocked_states = 0
    errors = 0
    tasks = @()
    generated_at = (Get-Date).ToString("o")
}

$parseScript = "E:\IMPERIUM\TOOLS\astronomicon_parse_general_task_v0_2.ps1"
$exportLocalScript = "E:\IMPERIUM\TOOLS\astronomicon_export_local_tasks_for_speculum_v0_2.ps1"
$importLocalScript = "E:\IMPERIUM\TOOLS\astronomicon_import_local_task_refinements_v0_2.ps1"
$decomposeScript = "E:\IMPERIUM\TOOLS\astronomicon_decompose_local_task_to_stages_v0_2.ps1"
$exportStageScript = "E:\IMPERIUM\TOOLS\astronomicon_export_stage_map_for_speculum_v0_1.ps1"
$importStageScript = "E:\IMPERIUM\TOOLS\astronomicon_import_stage_refinements_v0_1.ps1"

for ($i = 1; $i -le $TaskCount; $i++) {
    $taskIndex = "{0:D3}" -f $i
    $taskId = "{0}-{1}-{2}" -f $SyntheticPrefix, (Get-Date -Format "yyyyMMdd"), $taskIndex
    $taskCode = "SYNTHETIC-PIPELINE-$taskIndex"
    $taskTitle = "Synthetic Pipeline Task $taskIndex"

    $taskRoot = Join-Path $GeneralTasksRoot $taskId
    $inputRoot = Join-Path $taskRoot "INPUT"
    $outputTaskRoot = Join-Path $taskRoot "OUTPUT"
    $stateRoot = Join-Path $taskRoot "STATE"
    Ensure-Directory -Path $taskRoot
    Ensure-Directory -Path $inputRoot
    Ensure-Directory -Path $outputTaskRoot
    Ensure-Directory -Path $stateRoot

    $inputPath = Join-Path $inputRoot "GENERAL_TASK_INPUT.txt"
    $taskLogPath = Join-Path $OutputRoot "$taskId.log"
    Write-Utf8Bom -Path $taskLogPath -Content ""

    $taskRecord = [ordered]@{
        general_task_id = $taskId
        task_root = $taskRoot
        output_root = $outputTaskRoot
        local_task_count = 0
        stage_count = 0
        stage_maps = 0
        orphan_count = 0
        blocked_states = 0
        steps = @()
        status = "RUNNING"
    }

    try {
        $formText = New-SyntheticGeneralTaskText -GeneralTaskId $taskId -Code $taskCode -Title $taskTitle
        Write-Utf8Bom -Path $inputPath -Content $formText
        Write-RunLog "[$taskId] General Task form created."

        $parseResult = Invoke-ScriptSafe -ScriptPath $parseScript -Arguments @("-InputPath", $inputPath, "-OutputRoot", $outputTaskRoot)
        Add-Content -LiteralPath $taskLogPath -Value $parseResult.output -Encoding UTF8
        $taskRecord.steps += [ordered]@{ step = "parse"; exit_code = $parseResult.exit_code; output = $parseResult.output }
        if ($parseResult.exit_code -ne 0) { throw "Parse failed for $taskId." }

        $registryPath = Join-Path $outputTaskRoot "LOCAL_TASK_REGISTRY.json"
        $registry = Read-JsonFile -Path $registryPath
        $taskRecord.local_task_count = [int]$registry.local_task_count
        $summary.total_local_tasks += [int]$registry.local_task_count

        $exportLocalResult = Invoke-ScriptSafe -ScriptPath $exportLocalScript -Arguments @("-OutputRoot", $outputTaskRoot)
        Add-Content -LiteralPath $taskLogPath -Value $exportLocalResult.output -Encoding UTF8
        $taskRecord.steps += [ordered]@{ step = "export_local"; exit_code = $exportLocalResult.exit_code; output = $exportLocalResult.output }
        if ($exportLocalResult.exit_code -ne 0) { throw "Export local failed for $taskId." }

        $includeLocalOrphan = ($i -eq 2)
        $localRefinements = New-SimulatedLocalRefinements -GeneralTaskId $taskId -Registry $registry -IncludeOrphan:$includeLocalOrphan
        $localRefPath = Join-Path $outputTaskRoot "SPECULUM\SPECULUM_LOCAL_TASK_REFINEMENTS.json"
        Write-JsonFile -Path $localRefPath -Object $localRefinements -Depth 40

        $importLocalResult = Invoke-ScriptSafe -ScriptPath $importLocalScript -Arguments @("-OutputRoot", $outputTaskRoot, "-RefinementsPath", $localRefPath)
        Add-Content -LiteralPath $taskLogPath -Value $importLocalResult.output -Encoding UTF8
        $taskRecord.steps += [ordered]@{ step = "import_local"; exit_code = $importLocalResult.exit_code; output = $importLocalResult.output }
        if ($importLocalResult.exit_code -ne 0) { throw "Import local failed for $taskId." }
        $summary.imports_passed++

        $firstLocalTaskId = [string]$registry.local_tasks[0].local_task_id
        $decomposeResult = Invoke-ScriptSafe -ScriptPath $decomposeScript -Arguments @("-OutputRoot", $outputTaskRoot, "-LocalTaskId", $firstLocalTaskId)
        Add-Content -LiteralPath $taskLogPath -Value $decomposeResult.output -Encoding UTF8
        $taskRecord.steps += [ordered]@{ step = "decompose"; exit_code = $decomposeResult.exit_code; output = $decomposeResult.output }
        if ($decomposeResult.exit_code -ne 0) { throw "Decompose failed for $taskId." }

        $summary.total_stage_maps++
        $taskRecord.stage_maps = 1

        $exportStageResult = Invoke-ScriptSafe -ScriptPath $exportStageScript -Arguments @("-OutputRoot", $outputTaskRoot, "-LocalTaskId", $firstLocalTaskId)
        Add-Content -LiteralPath $taskLogPath -Value $exportStageResult.output -Encoding UTF8
        $taskRecord.steps += [ordered]@{ step = "export_stage"; exit_code = $exportStageResult.exit_code; output = $exportStageResult.output }
        if ($exportStageResult.exit_code -ne 0) { throw "Export stage failed for $taskId." }

        $stageMapPath = Join-Path $outputTaskRoot "STAGE_MAPS\$firstLocalTaskId\STAGE_MAP.json"
        $stageMap = Read-JsonFile -Path $stageMapPath
        $taskRecord.stage_count = [int]$stageMap.stage_count
        $summary.total_stages += [int]$stageMap.stage_count

        $includeStageOrphan = ($i -eq 3)
        $stageRefinements = New-SimulatedStageRefinements -GeneralTaskId $taskId -LocalTaskId $firstLocalTaskId -StageMap $stageMap -IncludeOrphan:$includeStageOrphan
        $stageRefPath = Join-Path $outputTaskRoot "SPECULUM\STAGE_REVIEW\SPECULUM_STAGE_REFINEMENTS_$firstLocalTaskId.json"
        Write-JsonFile -Path $stageRefPath -Object $stageRefinements -Depth 40

        $importStageResult = Invoke-ScriptSafe -ScriptPath $importStageScript -Arguments @("-OutputRoot", $outputTaskRoot, "-LocalTaskId", $firstLocalTaskId, "-RefinementsPath", $stageRefPath)
        Add-Content -LiteralPath $taskLogPath -Value $importStageResult.output -Encoding UTF8
        $taskRecord.steps += [ordered]@{ step = "import_stage"; exit_code = $importStageResult.exit_code; output = $importStageResult.output }
        if ($importStageResult.exit_code -ne 0) { throw "Import stage failed for $taskId." }
        $summary.imports_passed++

        $localImportReceiptPath = Join-Path $outputTaskRoot "SPECULUM\IMPORTS\LOCAL_TASK_REFINEMENTS\IMPORT_LOCAL_TASK_REFINEMENTS_RECEIPT.json"
        $stageImportReceiptPath = Join-Path $outputTaskRoot "SPECULUM\IMPORTS\STAGE_REFINEMENTS\$firstLocalTaskId\IMPORT_STAGE_REFINEMENTS_RECEIPT.json"
        $localImportReceipt = Read-JsonFile -Path $localImportReceiptPath
        $stageImportReceipt = Read-JsonFile -Path $stageImportReceiptPath

        $taskOrphans = [int]$localImportReceipt.orphan_count + [int]$stageImportReceipt.orphan_count
        $taskRecord.orphan_count = $taskOrphans
        $summary.orphans += $taskOrphans

        if ($taskOrphans -gt 0) {
            $taskRecord.blocked_states++
            $summary.blocked_states++
        }

        $taskRecord.status = "PASS"
        Write-RunLog "[$taskId] Synthetic full run completed."
    }
    catch {
        $taskRecord.status = "FAIL"
        $taskRecord.error = $_.Exception.Message
        $summary.errors++
        Write-RunLog "[$taskId] ERROR: $($_.Exception.Message)"
    }

    $summary.tasks += $taskRecord
    $summary.total_synthetic_general_tasks++
}

$summaryPath = Join-Path $OutputRoot "SYNTHETIC_SUMMARY.json"
Write-JsonFile -Path $summaryPath -Object $summary -Depth 60

$summaryMd = @(
    "# Synthetic Full Run Summary"
    ""
    "total synthetic General Tasks: $($summary.total_synthetic_general_tasks)"
    "total Local Tasks: $($summary.total_local_tasks)"
    "total Stage Maps: $($summary.total_stage_maps)"
    "total Stages: $($summary.total_stages)"
    "imports passed: $($summary.imports_passed)"
    "orphans: $($summary.orphans)"
    "blocked states: $($summary.blocked_states)"
    "errors: $($summary.errors)"
)
Write-Utf8Bom -Path (Join-Path $OutputRoot "SYNTHETIC_SUMMARY.md") -Content ($summaryMd -join "`n")

Write-Host "Synthetic full run complete."
Write-Host "Summary: $summaryPath"
