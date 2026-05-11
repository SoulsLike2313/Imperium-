param(
    [Parameter(Mandatory=$true)]
    [string]$TaskId,
    [string]$Root = "E:\IMPERIUM",
    [string]$CheckpointId = "",
    [string]$RuntimeAnalyzerDir = ""
)

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $Root

$runtimeDir = if ([string]::IsNullOrWhiteSpace($RuntimeAnalyzerDir)) {
    Join-Path $Root ".imperium_runtime\administratum_analyzer\latest"
} else {
    $RuntimeAnalyzerDir
}

if ([string]::IsNullOrWhiteSpace($CheckpointId)) {
    $CheckpointId = "CHECKPOINT_" + (Get-Date -Format "yyyyMMdd_HHmmss")
}

if (-not (Test-Path -LiteralPath $runtimeDir)) {
    throw "Runtime analyzer directory not found: $runtimeDir"
}

$checkpointRoot = Join-Path $Root ("ARTIFACTS\" + $TaskId + "\CHECKPOINTS\" + $CheckpointId)
New-Item -ItemType Directory -Force -Path $checkpointRoot | Out-Null

$filesToCopy = @(
    "GIT_LOCAL_ANALYSIS.json",
    "RECOMMENDED_CHAT_COMPILATION.json",
    "WORKTREE_CLASSIFICATION.json",
    "WORKTREE_CLASSIFICATION_REPORT.md",
    "OWNER_NEXT_ACTION.md",
    "GIT_REALITY_REPORT.md",
    "LATEST_CONTEXT_BUNDLE_RECEIPT.json",
    "runtime_receipt.json",
    "LAST_CHAT_COMPILATION_PATH.txt",
    "VERDICT.md"
)

$copied = @()
$missing = @()
foreach ($name in $filesToCopy) {
    $src = Join-Path $runtimeDir $name
    if (Test-Path -LiteralPath $src) {
        $dst = Join-Path $checkpointRoot $name
        Copy-Item -LiteralPath $src -Destination $dst -Force
        $copied += $name
    } else {
        $missing += $name
    }
}

$hashes = @()
foreach ($name in $copied) {
    $filePath = Join-Path $checkpointRoot $name
    $hashes += [ordered]@{
        path = $filePath
        sha256 = (Get-FileHash -LiteralPath $filePath -Algorithm SHA256).Hash.ToLower()
        size_bytes = (Get-Item -LiteralPath $filePath).Length
    }
}

$receipt = [ordered]@{
    schema_version = "ADMINISTRATUM_ANALYZER_CHECKPOINT_RECEIPT_V0_1"
    task_id = $TaskId
    checkpoint_id = $CheckpointId
    created_at = (Get-Date).ToString("o")
    runtime_analyzer_dir = $runtimeDir
    checkpoint_root = $checkpointRoot
    copied_files = $copied
    missing_files = $missing
    file_hashes = $hashes
    source_head = (git rev-parse HEAD 2>$null).Trim()
    source_commit_count = (git rev-list --count HEAD 2>$null).Trim()
}

$receiptPath = Join-Path $checkpointRoot "CHECKPOINT_RECEIPT.json"
$receipt | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $receiptPath -Encoding UTF8

Write-Output $receiptPath
