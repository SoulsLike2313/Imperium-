param(
    [Parameter(Mandatory = $true)][string]$TaskId,
    [Parameter(Mandatory = $true)][string]$RunId,
    [string]$WorkSessionId = "",
    [string]$Actor = "PC_SERVITOR",
    [string]$LocalTaskId = "LTASK-001",
    [string]$StageId = "STAGE-001-SMOKE-VALIDATE-AND-WRITE",
    [string]$RepoRoot = "E:\IMPERIUM",
    [Parameter(Mandatory = $true)][string]$ArtifactRoot,
    [Parameter(Mandatory = $true)][string]$WorkPacketPath,
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
        [int]$Depth = 60
    )
    Ensure-Directory -Path $Path
    $json = $Object | ConvertTo-Json -Depth $Depth
    Set-Content -LiteralPath $Path -Encoding UTF8 -Value $json
}

if ([string]::IsNullOrWhiteSpace($WorkSessionId)) {
    $WorkSessionId = "WORKSESSION-{0}" -f ([guid]::NewGuid().ToString())
}

$head = (& git -C $RepoRoot rev-parse HEAD 2>$null | Out-String).Trim()
$branch = (& git -C $RepoRoot branch --show-current 2>$null | Out-String).Trim()
$gitStatus = (& git -C $RepoRoot status --short 2>$null | Out-String).Trim()

$knownDefectsPath = Join-Path $RepoRoot "REGISTRY/KNOWN_DEFECTS.json"
$knownDefects = @()
if (Test-Path -LiteralPath $knownDefectsPath) {
    try {
        $def = Get-Content -LiteralPath $knownDefectsPath -Raw | ConvertFrom-Json
        foreach ($item in $def.defects) {
            if ($item.status -eq "OPEN" -or $item.status -eq "PARTIAL") {
                $knownDefects += [string]$item.defect_id
            }
        }
    }
    catch {
        $knownDefects += "KNOWN_DEFECTS_PARSE_FAILED"
    }
}

$stageOutputPath = (Join-Path $ArtifactRoot "REPORTS/stage_smoke_output.md").Replace("\", "/")
$stageResultPath = (Join-Path $ArtifactRoot "OUTPUTS/e2e_stage_result.json").Replace("\", "/")
$finalReceiptPath = (Join-Path $ArtifactRoot "RECEIPTS/08_first_runtime_e2e_receipt.json").Replace("\", "/")

$workPacket = [ordered]@{
    work_session_id = $WorkSessionId
    run_id = $RunId
    task_id = $TaskId
    local_task_ids = @($LocalTaskId)
    allowed_stage_ids = @($StageId)
    actor = $Actor
    repo_reality = [ordered]@{
        head = $head
        branch = $branch
        git_status_short = $gitStatus
    }
    current_known_defects = $knownDefects
    read_zones = @(
        "REGISTRY/",
        "ORGANS/PORT_PROTOCOL/",
        "ORGANS/ASTRONOMICON/SCHEMAS/",
        "ORGANS/ADMINISTRATUM/SCHEMAS/",
        "ORGANS/DOCTRINARIUM/SCHEMAS/"
    )
    write_zones = @(
        ($ArtifactRoot.Replace("\", "/") + "/OUTPUTS/"),
        ($ArtifactRoot.Replace("\", "/") + "/REPORTS/"),
        ($ArtifactRoot.Replace("\", "/") + "/RECEIPTS/")
    )
    forbidden_zones = @(
        "THRONE/",
        "CURRENT_STATE/ADMINISTRATUM_ANALYZER_V0_3/",
        ".imperium_runtime/"
    )
    required_scripts = @(
        "TOOLS/imperium_doctrinarium_preflight_smoke.ps1",
        "TOOLS/imperium_astronomicon_get_task_map_smoke.ps1",
        "TOOLS/imperium_administratum_issue_work_packet_smoke.ps1",
        "TOOLS/imperium_register_stage_result_smoke.ps1"
    )
    stage_commands = @(
        "Validate REGISTRY JSON parse and write stage smoke report to " + $stageOutputPath
    )
    validation_commands = @(
        "PowerShell ConvertFrom-Json parse for registry files",
        "Test-Path on stage output and stage result"
    )
    required_outputs = @($stageOutputPath, $stageResultPath)
    required_receipts = @($finalReceiptPath)
    artifact_paths = @(
        ($ArtifactRoot.Replace("\", "/") + "/OUTPUTS"),
        ($ArtifactRoot.Replace("\", "/") + "/REPORTS"),
        ($ArtifactRoot.Replace("\", "/") + "/RECEIPTS")
    )
    current_state_update_policy = "No CURRENT_STATE writes in smoke run."
    recoverable_error_policy = "Record recoverable error in stage result and mark FAIL."
    nonrecoverable_blockers = @(
        "Preflight BLOCK status",
        "Cannot parse registry JSON",
        "Cannot write stage output"
    )
    commit_policy = "Commit only intentional task artifact and script updates after validation."
    push_policy = "Push only after final receipt and clean review of staged paths."
    return_protocol = "Return with first_runtime_e2e_report and 08_first_runtime_e2e_receipt.json"
}

$receipt = [ordered]@{
    schema = "IMPERIUM_PORT_RECEIPT_V1"
    receipt_id = "PORT-RECEIPT-{0}" -f ([guid]::NewGuid().ToString())
    message_id = "MSG-{0}" -f ([guid]::NewGuid().ToString())
    task_id = $TaskId
    local_task_id = $LocalTaskId
    stage_id = $StageId
    run_id = $RunId
    operation = "issue_work_packet"
    status = "OK"
    payload_path = $WorkPacketPath.Replace("\", "/")
    notes = @(
        "Administratum smoke work packet generated.",
        "This work packet is scoped to one safe stage."
    )
    created_at = (Get-Date).ToString("o")
}

Write-JsonFile -Path $WorkPacketPath -Object $workPacket -Depth 60
Write-JsonFile -Path $ReceiptPath -Object $receipt -Depth 60

Write-Host "Administratum smoke work packet generated."
Write-Host "Work packet: $WorkPacketPath"

