param(
    [Parameter(Mandatory = $true)][string]$TaskId,
    [string[]]$StageRange = @(),
    [string]$Actor = "PC_SERVITOR",
    [string]$RepoRoot = "E:\IMPERIUM",
    [string]$RequestedMode = "execute_without_stop_unless_blocked",
    [Parameter(Mandatory = $true)][string]$RequestPath,
    [Parameter(Mandatory = $true)][string]$ResponsePath,
    [Parameter(Mandatory = $true)][string]$ReceiptPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Ensure-Directory {
    param([Parameter(Mandatory = $true)][string]$Path)
    $parent = Split-Path -Parent $Path
    if ($parent -and -not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }
}

function Write-JsonFile {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)]$Object,
        [int]$Depth = 40
    )
    Ensure-Directory -Path $Path
    $json = $Object | ConvertTo-Json -Depth $Depth
    Set-Content -LiteralPath $Path -Encoding UTF8 -Value $json
}

if (-not $StageRange -or $StageRange.Count -eq 0) {
    $StageRange = @("STAGE-001-SMOKE-VALIDATE-AND-WRITE")
}

$messageId = "MSG-{0}" -f ([guid]::NewGuid().ToString())
$responseId = "RESP-{0}" -f ([guid]::NewGuid().ToString())
$receiptId = "PORT-RECEIPT-{0}" -f ([guid]::NewGuid().ToString())
$runId = "RUN-{0}" -f (Get-Date -Format "yyyyMMdd-HHmmss")

$requiredPaths = @(
    "ORGANS/DOCTRINARIUM/SCHEMAS/preflight_task_execution_v1.schema.json",
    "ORGANS/ASTRONOMICON/SCHEMAS/task_map_v1.schema.json",
    "ORGANS/ASTRONOMICON/SCHEMAS/stage_map_v1.schema.json",
    "ORGANS/ADMINISTRATUM/SCHEMAS/administratum_work_packet_v1.schema.json",
    "REGISTRY/KNOWN_DEFECTS.json"
)

$missing = @()
foreach ($path in $requiredPaths) {
    $full = Join-Path $RepoRoot $path
    if (-not (Test-Path -LiteralPath $full)) {
        $missing += $path
    }
}

$gitHead = (& git -C $RepoRoot rev-parse HEAD 2>$null | Out-String).Trim()
$gitStatus = (& git -C $RepoRoot status --short 2>$null | Out-String).Trim()

$warnings = @(
    "Smoke runner path only; production organ dispatch is not fully automated."
)
$blockers = @()
$status = "ALLOW_WITH_LIMITATIONS"
$blocked = $false

if ($missing.Count -gt 0) {
    $status = "BLOCK"
    $blocked = $true
    $blockers += ("Missing required files: " + ($missing -join ", "))
}

if ($gitStatus) {
    $warnings += "Worktree not clean; stage run should be controlled and evidence-only."
}

$request = [ordered]@{
    schema = "IMPERIUM_PORT_MESSAGE_V1"
    message_id = $messageId
    task_id = $TaskId
    local_task_id = $null
    stage_id = $null
    run_id = $runId
    from = "PC_SERVITOR"
    to = "DOCTRINARIUM"
    operation = "preflight_task_execution"
    payload = [ordered]@{
        stage_range = $StageRange
        actor = $Actor
        repo_head = $gitHead
        requested_mode = $RequestedMode
    }
    expected_response = "ALLOW|ALLOW_WITH_LIMITATIONS|BLOCK|ERROR"
    created_at = (Get-Date).ToString("o")
}

$payloadPath = [System.IO.Path]::ChangeExtension($ResponsePath, ".payload.json")
$payload = [ordered]@{
    operation = "preflight_task_execution"
    task_id = $TaskId
    stage_range = $StageRange
    actor = $Actor
    repo_head = $gitHead
    required_organs = @("DOCTRINARIUM", "ASTRONOMICON", "ADMINISTRATUM")
    organ_health = [ordered]@{
        doctrinarium = if ($missing -contains "ORGANS/DOCTRINARIUM/SCHEMAS/preflight_task_execution_v1.schema.json") { "MISSING_SCHEMA" } else { "SCHEMA_PRESENT" }
        astronomicon = if (($missing -contains "ORGANS/ASTRONOMICON/SCHEMAS/task_map_v1.schema.json") -or ($missing -contains "ORGANS/ASTRONOMICON/SCHEMAS/stage_map_v1.schema.json")) { "MISSING_SCHEMA" } else { "SCHEMA_PRESENT" }
        administratum = if ($missing -contains "ORGANS/ADMINISTRATUM/SCHEMAS/administratum_work_packet_v1.schema.json") { "MISSING_SCHEMA" } else { "SCHEMA_PRESENT" }
    }
    blocked = $blocked
    limitations = $warnings
    forbidden_actions = @(
        "No deletes",
        "No broad migration",
        "No THRONE writes",
        "No runtime output to tracked CURRENT_STATE"
    )
    required_receipts = @(
        "08_first_runtime_e2e_receipt.json",
        "10_validation_receipt.json"
    )
    blockers = $blockers
}

$response = [ordered]@{
    schema = "IMPERIUM_PORT_RESPONSE_V1"
    message_id = $messageId
    response_id = $responseId
    status = $status
    payload_path = $payloadPath.Replace("\", "/")
    receipt_path = $ReceiptPath.Replace("\", "/")
    warnings = $warnings
    blockers = $blockers
}

$receipt = [ordered]@{
    schema = "IMPERIUM_PORT_RECEIPT_V1"
    receipt_id = $receiptId
    message_id = $messageId
    task_id = $TaskId
    local_task_id = $null
    stage_id = $null
    run_id = $runId
    operation = "preflight_task_execution"
    status = $status
    payload_path = $payloadPath.Replace("\", "/")
    notes = @(
        "Smoke preflight runner executed.",
        "Result is safe-gated for minimal runtime E2E only."
    )
    created_at = (Get-Date).ToString("o")
}

Write-JsonFile -Path $RequestPath -Object $request -Depth 40
Write-JsonFile -Path $payloadPath -Object $payload -Depth 40
Write-JsonFile -Path $ResponsePath -Object $response -Depth 40
Write-JsonFile -Path $ReceiptPath -Object $receipt -Depth 40

Write-Host "Doctrinarium preflight smoke complete."
Write-Host "Status: $status"
Write-Host "Response: $ResponsePath"

if ($status -eq "BLOCK") {
    exit 2
}
exit 0

