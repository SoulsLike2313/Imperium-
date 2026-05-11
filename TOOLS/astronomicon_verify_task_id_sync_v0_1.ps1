param(
    [Parameter(Mandatory = $true)]
    [string]$InputPath,

    [Parameter(Mandatory = $true)]
    [string]$TaskRoot,

    [Parameter(Mandatory = $true)]
    [string]$DashboardTaskId,

    [Parameter(Mandatory = $true)]
    [string]$ReceiptPath,

    [int]$RequireRegistry = 0
)

$ErrorActionPreference = "Stop"
. "E:\IMPERIUM\TOOLS\astronomicon_pipeline_common_v0_2.ps1"

$outputRoot = Join-Path $TaskRoot "OUTPUT"
$registryPath = Join-Path $outputRoot "LOCAL_TASK_REGISTRY.json"
$requireRegistryBool = ($RequireRegistry -ne 0)

$errors = @()
$warnings = @()

if (-not (Test-Path -LiteralPath $InputPath)) {
    $errors += "General Task input file not found: $InputPath"
}
if (-not (Test-Path -LiteralPath $TaskRoot)) {
    $errors += "Task root not found: $TaskRoot"
}
if ([string]::IsNullOrWhiteSpace($DashboardTaskId)) {
    $errors += "Dashboard task ID is empty."
}

$formTaskId = ""
$folderTaskId = ""
$registryTaskId = ""

if ($errors.Count -eq 0) {
    $formText = [System.IO.File]::ReadAllText($InputPath, [System.Text.Encoding]::UTF8)
    $formTaskId = Get-ScalarFieldFromStrictText -Text $formText -FieldName "GENERAL_TASK_ID"
    if ([string]::IsNullOrWhiteSpace($formTaskId)) {
        $errors += "GENERAL_TASK_ID is missing in General Task form."
    }

    $folderTaskId = Split-Path -Leaf $TaskRoot
    if ([string]::IsNullOrWhiteSpace($folderTaskId)) {
        $errors += "Task root folder name is empty."
    }

    if (Test-Path -LiteralPath $registryPath) {
        $registry = Read-JsonFile -Path $registryPath
        $registryTaskId = [string]$registry.general_task_id
        if ([string]::IsNullOrWhiteSpace($registryTaskId)) {
            $errors += "Registry general_task_id is empty."
        }
    }
    else {
        if ($requireRegistryBool) {
            $errors += "Registry not found but required: $registryPath"
        }
        else {
            $warnings += "Registry not found yet (pre-parse or first-pass state)."
        }
    }
}

if ($errors.Count -eq 0) {
    if ($formTaskId -ne $folderTaskId) {
        $errors += "Mismatch: form GENERAL_TASK_ID ($formTaskId) != task folder ($folderTaskId)"
    }
    if ($formTaskId -ne $DashboardTaskId) {
        $errors += "Mismatch: form GENERAL_TASK_ID ($formTaskId) != dashboard card ID ($DashboardTaskId)"
    }
    if ($registryTaskId -and $registryTaskId -ne $formTaskId) {
        $errors += "Mismatch: registry general_task_id ($registryTaskId) != form GENERAL_TASK_ID ($formTaskId)"
    }
}

$status = if ($errors.Count -eq 0) { "PASS" } else { "BLOCKED_MISMATCH" }
$receipt = [ordered]@{
    schema_version = "ASTRONOMICON_TASK_ID_SYNC_RECEIPT_V0_1"
    status = $status
    dashboard_task_id = $DashboardTaskId
    form_task_id = $formTaskId
    task_folder_name = $folderTaskId
    registry_task_id = $registryTaskId
    input_path = $InputPath
    task_root = $TaskRoot
    output_root = $outputRoot
    registry_path = $registryPath
    errors = $errors
    warnings = $warnings
    generated_at = (Get-Date).ToString("o")
}
Write-JsonFile -Path $ReceiptPath -Object $receipt -Depth 20

if ($status -ne "PASS") {
    throw "Task ID sync failed. See receipt: $ReceiptPath"
}

Write-Host "Task ID sync PASS."
Write-Host "Receipt: $ReceiptPath"
