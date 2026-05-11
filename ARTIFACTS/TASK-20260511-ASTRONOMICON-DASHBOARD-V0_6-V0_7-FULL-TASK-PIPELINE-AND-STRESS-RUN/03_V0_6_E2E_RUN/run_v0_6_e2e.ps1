$ErrorActionPreference = "Stop"
$repoRoot = "E:\IMPERIUM"
$artifactRoot = "E:\IMPERIUM\ARTIFACTS\TASK-20260511-ASTRONOMICON-DASHBOARD-V0_6-V0_7-FULL-TASK-PIPELINE-AND-STRESS-RUN"
$runRoot = Join-Path $artifactRoot "03_V0_6_E2E_RUN"
New-Item -ItemType Directory -Force -Path $runRoot | Out-Null
$utf8Bom = New-Object System.Text.UTF8Encoding($true)
$logPath = Join-Path $runRoot "V0_6_E2E_LOG_RERUN.txt"
[System.IO.File]::WriteAllText($logPath, "", $utf8Bom)

function Log([string]$m) {
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $m
    Add-Content -LiteralPath $logPath -Value $line -Encoding UTF8
    Write-Host $line
}

function RunPs([string]$scriptPath, [string[]]$scriptArgs) {
    $psArgs = @("-ExecutionPolicy", "Bypass", "-File", $scriptPath) + $scriptArgs
    $output = & powershell.exe @psArgs 2>&1 | Out-String
    $exitCode = $LASTEXITCODE
    return [ordered]@{ script = $scriptPath; args = $scriptArgs; exit_code = $exitCode; output = $output.Trim() }
}

$taskId = "GTASK-20260511-ASTRONOMICON-DASHBOARD-V0_6-REALRUN"
$taskRoot = Join-Path "E:\IMPERIUM\ASTRONOMICON\GENERAL_TASKS" $taskId
if (Test-Path -LiteralPath $taskRoot) {
    Remove-Item -LiteralPath $taskRoot -Recurse -Force
}
$inputRoot = Join-Path $taskRoot "INPUT"
$outputRoot = Join-Path $taskRoot "OUTPUT"
$stateRoot = Join-Path $taskRoot "STATE"
New-Item -ItemType Directory -Force -Path $taskRoot, $inputRoot, $outputRoot, $stateRoot | Out-Null

$inputPath = Join-Path $inputRoot "GENERAL_TASK_INPUT.txt"
$formText = @"
ASTRONOMICON_GENERAL_TASK_V0_1
ENCODING: UTF-8-BOM
LINE_ENDINGS: CRLF

GENERAL_TASK_ID:
$taskId

GENERAL_TASK_TITLE:
Astronomicon Dashboard v0.6 Real Pipeline Run

GENERAL_TASK_CODE:
ASTRONOMICON-DASHBOARD-V0_6-REALRUN

AUTHOR:
Owner

EXECUTION_INTENT:
manual

PRIORITY:
high

BEGIN_GOAL
Execute one full planning path through local and stage refinement loops.
END_GOAL

BEGIN_CONTEXT
Dashboard v0.6 hardening needs a single complete task path backed by receipts.
END_CONTEXT

BEGIN_CURRENT_PROBLEM
Need end-to-end proof that fragile v0.5 behavior is replaced by reliable pipeline calls.
END_CURRENT_PROBLEM

BEGIN_EXPECTED_FINAL_STATE
- Local Tasks parsed and exported for Speculum.
- Local refinements imported by ID.
- Selected Local Task decomposed to stages.
- Stage review exported and imported by stage_id.
END_EXPECTED_FINAL_STATE

BEGIN_HARD_CONSTRAINTS
- No secret leakage.
- No fake green.
- Receipts required.
END_HARD_CONSTRAINTS

BEGIN_DO_NOT_DO
- Do not overwrite core records from Speculum payloads.
- Do not silently drop unknown IDs.
END_DO_NOT_DO

BEGIN_PLAN_ITEMS

ITEM_ID: PI-001
TITLE: Create robust parser pipeline evidence
TEXT:
Generate parse and Local Task outputs with deterministic IDs.
EXPECTED_OUTPUT:
Registry and Local Task records.
REQUIRED_ORGANS:
Astronomicon, Administratum
EXECUTION_MODE:
manual
DEPENDS_ON:
none
END_ITEM

ITEM_ID: PI-002
TITLE: Run Local Task Speculum exchange
TEXT:
Export and import Local Task refinements with orphan capture.
EXPECTED_OUTPUT:
Local refinement receipts and attachments.
REQUIRED_ORGANS:
Astronomicon, Speculum
EXECUTION_MODE:
scripted
DEPENDS_ON:
PI-001
END_ITEM

ITEM_ID: PI-003
TITLE: Run Stage Speculum exchange
TEXT:
Decompose one Local Task, export stage review, import stage refinements.
EXPECTED_OUTPUT:
Stage map and stage refinement receipts.
REQUIRED_ORGANS:
Astronomicon, Speculum
EXECUTION_MODE:
scripted
DEPENDS_ON:
PI-002
END_ITEM

END_PLAN_ITEMS

BEGIN_KNOWN_RISKS
- Payload schema mismatch.
- Unknown refinement IDs.
END_KNOWN_RISKS

BEGIN_REQUIRED_ORGANS
- Astronomicon
- Speculum
END_REQUIRED_ORGANS

BEGIN_REQUIRED_INPUTS
- Strict General Task form.
END_REQUIRED_INPUTS

BEGIN_EXPECTED_ARTIFACTS
- Parse receipt.
- Local import receipt.
- Stage import receipt.
END_EXPECTED_ARTIFACTS

BEGIN_OWNER_NOTES
Real one-task pipeline run for v0.6 validation.
END_OWNER_NOTES
"@
[System.IO.File]::WriteAllText($inputPath, ($formText -replace "`r`n", "`n" -replace "`r", "`n").Replace("`n", "`r`n"), $utf8Bom)
Log "Input form created: $inputPath"

$receipts = @()

$verifyScript = "E:\IMPERIUM\TOOLS\astronomicon_verify_task_id_sync_v0_1.ps1"
$parseScript = "E:\IMPERIUM\TOOLS\astronomicon_parse_general_task_v0_2.ps1"
$exportLocalScript = "E:\IMPERIUM\TOOLS\astronomicon_export_local_tasks_for_speculum_v0_2.ps1"
$importLocalScript = "E:\IMPERIUM\TOOLS\astronomicon_import_local_task_refinements_v0_2.ps1"
$decomposeScript = "E:\IMPERIUM\TOOLS\astronomicon_decompose_local_task_to_stages_v0_2.ps1"
$exportStageScript = "E:\IMPERIUM\TOOLS\astronomicon_export_stage_map_for_speculum_v0_1.ps1"
$importStageScript = "E:\IMPERIUM\TOOLS\astronomicon_import_stage_refinements_v0_1.ps1"

$preParseSyncReceipt = Join-Path $outputRoot "RECEIPTS\ID_SYNC\PRE_PARSE.json"
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $preParseSyncReceipt) | Out-Null
$r = RunPs $verifyScript @("-InputPath", $inputPath, "-TaskRoot", $taskRoot, "-DashboardTaskId", $taskId, "-ReceiptPath", $preParseSyncReceipt, "-RequireRegistry", "0")
Add-Content -LiteralPath $logPath -Value $r.output -Encoding UTF8
if ($r.exit_code -ne 0) { throw "PRE_PARSE ID sync failed" }
$receipts += $preParseSyncReceipt
Log "Pre-parse ID sync PASS"

$r = RunPs $parseScript @("-InputPath", $inputPath, "-OutputRoot", $outputRoot)
Add-Content -LiteralPath $logPath -Value $r.output -Encoding UTF8
if ($r.exit_code -ne 0) { throw "Parse failed" }
$receipts += (Join-Path $outputRoot "PARSE_RECEIPT.json")
Log "Parse PASS"

$postParseSyncReceipt = Join-Path $outputRoot "RECEIPTS\ID_SYNC\POST_PARSE.json"
$r = RunPs $verifyScript @("-InputPath", $inputPath, "-TaskRoot", $taskRoot, "-DashboardTaskId", $taskId, "-ReceiptPath", $postParseSyncReceipt, "-RequireRegistry", "1")
Add-Content -LiteralPath $logPath -Value $r.output -Encoding UTF8
if ($r.exit_code -ne 0) { throw "POST_PARSE ID sync failed" }
$receipts += $postParseSyncReceipt
Log "Post-parse ID sync PASS"

$r = RunPs $exportLocalScript @("-OutputRoot", $outputRoot)
Add-Content -LiteralPath $logPath -Value $r.output -Encoding UTF8
if ($r.exit_code -ne 0) { throw "Export Local failed" }
$receipts += (Join-Path $outputRoot "SPECULUM\EXPORT_LOCAL_TASKS_RECEIPT.json")
Log "Export Local PASS"

$registryPath = Join-Path $outputRoot "LOCAL_TASK_REGISTRY.json"
$registry = Get-Content -LiteralPath $registryPath -Encoding UTF8 -Raw | ConvertFrom-Json

$localRefItems = @()
foreach ($lt in $registry.local_tasks) {
    $localRefItems += [ordered]@{
        local_task_id = $lt.local_task_id
        scope_narrowing = @("Keep execution scope aligned with $($lt.local_task_id).")
        technical_execution_risks = @("Parser schema drift can break consistency.")
        missing_inputs = @("Confirm destination files before execution.")
        required_tools_or_scripts = @("PowerShell 5+", "astronomicon_decompose_local_task_to_stages_v0_2.ps1")
        readiness_questions = @("Are pass criteria and fail conditions explicit?")
        pass_criteria = @("All expected outputs exist and are inspectable.")
        fail_conditions = @("Any required artifact is missing.")
        do_not_do = @("Do not modify unrelated task records.")
        decomposition_hints = @("Prepare inputs and constraints.", "Apply change and produce evidence.", "Verify outputs and finalize.")
        should_split = $false
        recommended_status = "READY_FOR_STAGE_DECOMPOSITION"
    }
}
$localRefItems += [ordered]@{
    local_task_id = "LTASK-999"
    scope_narrowing = @("orphan test")
    technical_execution_risks = @("orphan test")
    missing_inputs = @("orphan test")
    required_tools_or_scripts = @("orphan test")
    readiness_questions = @("orphan test")
    pass_criteria = @("orphan test")
    fail_conditions = @("orphan test")
    do_not_do = @("orphan test")
    decomposition_hints = @("orphan test")
    should_split = $false
    recommended_status = "BLOCKED"
}
$localRef = [ordered]@{
    schema_version = "ASTRONOMICON_SPECULUM_LOCAL_TASK_REFINEMENTS_V0_1"
    general_task_id = $taskId
    review_mode = "hard_red_team_scope_narrowing"
    allocation_rule = "Distribute review effort evenly across all local tasks."
    items = $localRefItems
}
$localRefPath = Join-Path $outputRoot "SPECULUM\SPECULUM_LOCAL_TASK_REFINEMENTS.json"
[System.IO.File]::WriteAllText($localRefPath, ($localRef | ConvertTo-Json -Depth 40), $utf8Bom)
Log "Local refinements JSON generated: $localRefPath"

$preImportLocalSyncReceipt = Join-Path $outputRoot "RECEIPTS\ID_SYNC\PRE_IMPORT_LOCAL.json"
$r = RunPs $verifyScript @("-InputPath", $inputPath, "-TaskRoot", $taskRoot, "-DashboardTaskId", $taskId, "-ReceiptPath", $preImportLocalSyncReceipt, "-RequireRegistry", "1")
Add-Content -LiteralPath $logPath -Value $r.output -Encoding UTF8
if ($r.exit_code -ne 0) { throw "PRE_IMPORT_LOCAL ID sync failed" }
$receipts += $preImportLocalSyncReceipt

$r = RunPs $importLocalScript @("-OutputRoot", $outputRoot, "-RefinementsPath", $localRefPath)
Add-Content -LiteralPath $logPath -Value $r.output -Encoding UTF8
if ($r.exit_code -ne 0) { throw "Import Local failed" }
$localImportReceipt = Join-Path $outputRoot "SPECULUM\IMPORTS\LOCAL_TASK_REFINEMENTS\IMPORT_LOCAL_TASK_REFINEMENTS_RECEIPT.json"
$receipts += $localImportReceipt
$receipts += (Join-Path $outputRoot "SPECULUM\IMPORTS\LOCAL_TASK_REFINEMENTS\ORPHAN_REFINEMENTS.json")
Log "Import Local PASS"

$selectedLocalTaskId = [string]$registry.local_tasks[0].local_task_id
$preDecomposeSyncReceipt = Join-Path $outputRoot "RECEIPTS\ID_SYNC\PRE_DECOMPOSE.json"
$r = RunPs $verifyScript @("-InputPath", $inputPath, "-TaskRoot", $taskRoot, "-DashboardTaskId", $taskId, "-ReceiptPath", $preDecomposeSyncReceipt, "-RequireRegistry", "1")
Add-Content -LiteralPath $logPath -Value $r.output -Encoding UTF8
if ($r.exit_code -ne 0) { throw "PRE_DECOMPOSE ID sync failed" }
$receipts += $preDecomposeSyncReceipt

$r = RunPs $decomposeScript @("-OutputRoot", $outputRoot, "-LocalTaskId", $selectedLocalTaskId)
Add-Content -LiteralPath $logPath -Value $r.output -Encoding UTF8
if ($r.exit_code -ne 0) { throw "Decompose failed" }
$receipts += (Join-Path $outputRoot "STAGE_MAPS\$selectedLocalTaskId\DECOMPOSE_RECEIPT.json")
Log "Decompose PASS for $selectedLocalTaskId"

$preExportStageSyncReceipt = Join-Path $outputRoot "RECEIPTS\ID_SYNC\PRE_EXPORT_STAGE.json"
$r = RunPs $verifyScript @("-InputPath", $inputPath, "-TaskRoot", $taskRoot, "-DashboardTaskId", $taskId, "-ReceiptPath", $preExportStageSyncReceipt, "-RequireRegistry", "1")
Add-Content -LiteralPath $logPath -Value $r.output -Encoding UTF8
if ($r.exit_code -ne 0) { throw "PRE_EXPORT_STAGE ID sync failed" }
$receipts += $preExportStageSyncReceipt

$r = RunPs $exportStageScript @("-OutputRoot", $outputRoot, "-LocalTaskId", $selectedLocalTaskId)
Add-Content -LiteralPath $logPath -Value $r.output -Encoding UTF8
if ($r.exit_code -ne 0) { throw "Export Stage failed" }
$receipts += (Join-Path $outputRoot "SPECULUM\STAGE_REVIEW\EXPORT_STAGE_REVIEW_RECEIPT_$selectedLocalTaskId.json")
Log "Export Stage PASS"

$stageMapPath = Join-Path $outputRoot "STAGE_MAPS\$selectedLocalTaskId\STAGE_MAP.json"
$stageMap = Get-Content -LiteralPath $stageMapPath -Encoding UTF8 -Raw | ConvertFrom-Json
$stageRefItems = @()
foreach ($st in $stageMap.stages) {
    $stageRefItems += [ordered]@{
        stage_id = $st.stage_id
        execution_risks = @("Evidence can be incomplete without checklist.")
        missing_inputs = @("Confirm stage input files exist.")
        missing_tools_or_scripts = @("No additional tools required for this run.")
        required_evidence = @("Stage output", "Stage receipt")
        pass_criteria = @("Output and receipt are present.")
        fail_conditions = @("Output missing or receipt missing.")
        do_not_do = @("Do not mutate unrelated stage records.")
        manual_safety_notes = @("Validate before declaring ready.")
        should_split = $false
        recommended_status = "READY_FOR_EXECUTION"
    }
}
$stageRefItems += [ordered]@{
    stage_id = "STAGE-999"
    execution_risks = @("orphan stage test")
    missing_inputs = @("orphan stage test")
    missing_tools_or_scripts = @("orphan stage test")
    required_evidence = @("orphan stage test")
    pass_criteria = @("orphan stage test")
    fail_conditions = @("orphan stage test")
    do_not_do = @("orphan stage test")
    manual_safety_notes = @("orphan stage test")
    should_split = $false
    recommended_status = "BLOCKED"
}
$stageRef = [ordered]@{
    schema_version = "ASTRONOMICON_SPECULUM_STAGE_REFINEMENTS_V0_1"
    general_task_id = $taskId
    local_task_id = $selectedLocalTaskId
    review_mode = "hard_red_team_stage_readiness"
    items = $stageRefItems
}
$stageRefPath = Join-Path $outputRoot "SPECULUM\STAGE_REVIEW\SPECULUM_STAGE_REFINEMENTS_$selectedLocalTaskId.json"
[System.IO.File]::WriteAllText($stageRefPath, ($stageRef | ConvertTo-Json -Depth 40), $utf8Bom)
Log "Stage refinements JSON generated: $stageRefPath"

$preImportStageSyncReceipt = Join-Path $outputRoot "RECEIPTS\ID_SYNC\PRE_IMPORT_STAGE.json"
$r = RunPs $verifyScript @("-InputPath", $inputPath, "-TaskRoot", $taskRoot, "-DashboardTaskId", $taskId, "-ReceiptPath", $preImportStageSyncReceipt, "-RequireRegistry", "1")
Add-Content -LiteralPath $logPath -Value $r.output -Encoding UTF8
if ($r.exit_code -ne 0) { throw "PRE_IMPORT_STAGE ID sync failed" }
$receipts += $preImportStageSyncReceipt

$r = RunPs $importStageScript @("-OutputRoot", $outputRoot, "-LocalTaskId", $selectedLocalTaskId, "-RefinementsPath", $stageRefPath)
Add-Content -LiteralPath $logPath -Value $r.output -Encoding UTF8
if ($r.exit_code -ne 0) { throw "Import Stage failed" }
$stageImportReceipt = Join-Path $outputRoot "SPECULUM\IMPORTS\STAGE_REFINEMENTS\$selectedLocalTaskId\IMPORT_STAGE_REFINEMENTS_RECEIPT.json"
$receipts += $stageImportReceipt
$receipts += (Join-Path $outputRoot "SPECULUM\IMPORTS\STAGE_REFINEMENTS\$selectedLocalTaskId\ORPHAN_REFINEMENTS.json")
Log "Import Stage PASS"

$summary = [ordered]@{
    schema_version = "ASTRONOMICON_V0_6_E2E_SUMMARY_V0_1"
    general_task_id = $taskId
    task_root = $taskRoot
    input_path = $inputPath
    output_root = $outputRoot
    selected_local_task_id = $selectedLocalTaskId
    local_task_count = [int]$registry.local_task_count
    stage_count = [int]$stageMap.stage_count
    receipts = $receipts
    status = "PASS_WITH_ORPHAN_TESTS"
    generated_at = (Get-Date).ToString("o")
}
$summaryPath = Join-Path $runRoot "V0_6_E2E_SUMMARY.json"
[System.IO.File]::WriteAllText($summaryPath, ($summary | ConvertTo-Json -Depth 50), $utf8Bom)

$receiptIndexPath = Join-Path $runRoot "RECEIPT_INDEX.txt"
[System.IO.File]::WriteAllText($receiptIndexPath, ($receipts -join "`r`n"), $utf8Bom)

Copy-Item -LiteralPath $inputPath -Destination (Join-Path $runRoot "GENERAL_TASK_INPUT.txt") -Force
Copy-Item -LiteralPath $summaryPath -Destination (Join-Path $runRoot "SUMMARY_COPY.json") -Force

Log "V0.6 E2E run complete."
