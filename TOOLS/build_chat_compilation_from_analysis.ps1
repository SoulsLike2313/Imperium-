param(
    [string]$Root = "E:\IMPERIUM",
    [string]$AnalysisPath = "E:\IMPERIUM\CURRENT_STATE\ADMINISTRATUM_ANALYZER\RECOMMENDED_CHAT_COMPILATION.json",
    [string]$TaskId = "FULL_IMPERIUM_CONTEXT",
    [switch]$IncludePrivateApproved,
    [switch]$ForVM2
)

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $Root

function Write-JsonFile {
    param([string]$Path, $Data)
    $Data | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $Path -Encoding UTF8
}

function Copy-IfExists {
    param([string]$Source,[string]$Destination)
    if (Test-Path -LiteralPath $Source) {
        $destParent = Split-Path -Parent $Destination
        if ($destParent -and -not (Test-Path -LiteralPath $destParent)) {
            New-Item -ItemType Directory -Force -Path $destParent | Out-Null
        }
        Copy-Item -LiteralPath $Source -Destination $Destination -Force
        return $true
    }
    return $false
}

function Add-FileInventoryCsv {
    param([string]$SourceDir,[string]$CsvPath)
    if (-not (Test-Path -LiteralPath $SourceDir)) {
        @([pscustomobject]@{relative_path="NOT_FOUND";size_bytes=0;last_write_utc=""}) |
            Export-Csv -LiteralPath $CsvPath -NoTypeInformation -Encoding UTF8
        return
    }

    $items = Get-ChildItem -LiteralPath $SourceDir -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
        [pscustomobject]@{
            relative_path = $_.FullName.Substring($SourceDir.Length).TrimStart('\\')
            size_bytes = $_.Length
            last_write_utc = $_.LastWriteTimeUtc.ToString("o")
        }
    }

    if ($items.Count -eq 0) {
        $items = @([pscustomobject]@{relative_path="EMPTY";size_bytes=0;last_write_utc=""})
    }

    $items | Export-Csv -LiteralPath $CsvPath -NoTypeInformation -Encoding UTF8
}

if (-not (Test-Path -LiteralPath $AnalysisPath)) {
    throw "Analysis file not found: $AnalysisPath"
}

$analysis = Get-Content -LiteralPath $AnalysisPath -Raw | ConvertFrom-Json
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$packName = "${TaskId}_${timestamp}"
$chatRoot = Join-Path $Root "CHAT_COMPILATIONS_LOCAL"
New-Item -ItemType Directory -Force -Path $chatRoot | Out-Null

$packDir = Join-Path $chatRoot $packName
New-Item -ItemType Directory -Force -Path $packDir | Out-Null

$subdirs = @(
    "00_ANALYZER_REPORT",
    "01_GIT_STATE",
    "02_ROOT_ORIENTATION",
    "03_CURRENT_STATE",
    "04_DOCS",
    "05_ORGANS_SELECTED",
    "06_ARTIFACTS_SELECTED",
    "07_LOCAL_ONLY_SAFE_INDEXES",
    "08_PRIVATE_CONTEXT_SELECTED",
    "09_RECEIPTS"
)
foreach ($sd in $subdirs) {
    New-Item -ItemType Directory -Force -Path (Join-Path $packDir $sd) | Out-Null
}

# 1) analyzer reports
$analyzerDir = Join-Path $Root "CURRENT_STATE\ADMINISTRATUM_ANALYZER"
$analyzerFiles = @(
    "GIT_LOCAL_ANALYSIS.json",
    "CONTEXT_GAP_REPORT.md",
    "RECOMMENDED_CHAT_COMPILATION.json",
    "LOCAL_ONLY_SAFE_INVENTORY.json",
    "GIT_PUBLIC_MEMORY_SUMMARY.md",
    "ANALYZER_RECEIPT.json"
)
$copied = New-Object System.Collections.Generic.List[string]
foreach ($f in $analyzerFiles) {
    $src = Join-Path $analyzerDir $f
    $dst = Join-Path $packDir "00_ANALYZER_REPORT\$f"
    if (Copy-IfExists -Source $src -Destination $dst) { $copied.Add("00_ANALYZER_REPORT/$f") }
}

# 2) git state snapshots
$gitStateFiles = @(
    "BASELINE_GIT_STATUS.txt",
    "BASELINE_GIT_REMOTE.txt",
    "BASELINE_GIT_LOG.txt",
    "BASELINE_GIT_HEAD.txt"
)
foreach ($f in $gitStateFiles) {
    $src = Join-Path $analyzerDir $f
    $dst = Join-Path $packDir "01_GIT_STATE\$f"
    if (Copy-IfExists -Source $src -Destination $dst) { $copied.Add("01_GIT_STATE/$f") }
}

# 3) root orientation
$rootFiles = @("README.md","START_HERE.md",".gitignore")
foreach ($rf in $rootFiles) {
    $src = Join-Path $Root $rf
    $dst = Join-Path $packDir "02_ROOT_ORIENTATION\$rf"
    if (Copy-IfExists -Source $src -Destination $dst) { $copied.Add("02_ROOT_ORIENTATION/$rf") }
}

# 4) current state safe files
$currentStateFiles = @(
    "CURRENT_STATE\LAST_POINT_STATE.json",
    "CURRENT_STATE\NEXT_ATOMIC_STEP.md",
    "CURRENT_STATE\DO_NOT_DO.md",
    "CURRENT_STATE\LOCAL_ONLY_SOURCES_INDEX.md",
    "CURRENT_STATE\LOCAL_ONLY_SOURCES_INDEX.json",
    "CURRENT_STATE\EXCLUDED_LOCAL_SOURCES.md"
)
foreach ($cf in $currentStateFiles) {
    $src = Join-Path $Root $cf
    $dst = Join-Path $packDir ("03_CURRENT_STATE\" + ($cf -replace "^CURRENT_STATE\\", ""))
    if (Copy-IfExists -Source $src -Destination $dst) { $copied.Add("03_CURRENT_STATE/" + ($cf -replace "^CURRENT_STATE\\", "")) }
}

# 5) docs (selected)
$docFiles = @(
    "DOCS\REPO_MAP.md",
    "DOCS\COMMANDS.md",
    "DOCS\BUNDLE_SYSTEM.md",
    "DOCS\CHAT_ENTRY_PROTOCOL.md",
    "DOCS\PUBLIC_PRIVATE_BOUNDARY.md",
    "DOCS\VM2_BOOTSTRAP_PROTOCOL.md",
    "DOCS\ADMINISTRATUM_OPERATIONAL_AUTHORITY.md",
    "DOCS\CHAT_COMPILATION_PROTOCOL.md"
)
foreach ($df in $docFiles) {
    $src = Join-Path $Root $df
    $dst = Join-Path $packDir ("04_DOCS\" + ($df -replace "^DOCS\\", ""))
    if (Copy-IfExists -Source $src -Destination $dst) { $copied.Add("04_DOCS/" + ($df -replace "^DOCS\\", "")) }
}

# 6) organs selected
$organFiles = @(
    "ORGANS\ADMINISTRATUM\ORGAN_CONTRACT.json",
    "ORGANS\ADMINISTRATUM\ORGAN_STATUS.json",
    "ORGANS\ADMINISTRATUM\SELF_REPORT.json",
    "ORGANS\ADMINISTRATUM\UTILITY\run_administratum_context_bundle_workflow.ps1"
)
foreach ($of in $organFiles) {
    $src = Join-Path $Root $of
    $dst = Join-Path $packDir ("05_ORGANS_SELECTED\" + ($of -replace "^ORGANS\\ADMINISTRATUM\\", "ADMINISTRATUM\\"))
    if (Copy-IfExists -Source $src -Destination $dst) { $copied.Add("05_ORGANS_SELECTED/" + ($of -replace "^ORGANS\\ADMINISTRATUM\\", "ADMINISTRATUM/" -replace "\\","/")) }
}

# 7) selected artifact receipts
$artifactPaths = @(
    "ARTIFACTS\TASK-20260510-GIT-SANITIZE-PRIVATE-SOURCES-AND-CLEAN-HISTORY-V0_1\04_RECEIPTS\FINAL_RECEIPT.json",
    "ARTIFACTS\TASK-20260510-ADMINISTRATUM-REPO-LOCAL-ENGINEERING-CLEAN-POINT-V0_1\06_RECEIPTS\FINAL_RECEIPT.json",
    "ARTIFACTS\TASK-20260510-REPO-FORMATTING-AND-IGNORE-RULES-REPAIR-V0_1\06_RECEIPTS\FINAL_RECEIPT.json"
)
foreach ($ap in $artifactPaths) {
    $src = Join-Path $Root $ap
    $rel = $ap -replace "^ARTIFACTS\\", ""
    $dst = Join-Path $packDir ("06_ARTIFACTS_SELECTED\" + $rel)
    if (Copy-IfExists -Source $src -Destination $dst) { $copied.Add("06_ARTIFACTS_SELECTED/" + ($rel -replace "\\","/")) }
}

# 8) safe private inventories (metadata only)
$privateInventoryPath = Join-Path $packDir "07_LOCAL_ONLY_SAFE_INDEXES\private_roots_inventory.json"
$roots = @("SSH_COMMAND_LIBRARY","ARCHIVE","BUNDLES_LOCAL","PRIVATE_CONTEXT_LOCAL","RUNTIME_LOCAL")
$inv = @()
foreach ($r in $roots) {
    $full = Join-Path $Root $r
    if (Test-Path -LiteralPath $full) {
        if ($r -eq "ARCHIVE") {
            $topFiles = Get-ChildItem -LiteralPath $full -File -ErrorAction SilentlyContinue
            $bytes = 0
            if ($topFiles) { $bytes = ($topFiles | Measure-Object -Property Length -Sum).Sum }
            $inv += [ordered]@{ root=$r; exists=$true; file_count=[int]$topFiles.Count; total_mb=[math]::Round(($bytes/1MB),3); note="TOP_LEVEL_ONLY" }
        } else {
            $files = Get-ChildItem -LiteralPath $full -Recurse -File -ErrorAction SilentlyContinue
            $bytes = 0
            if ($files) { $bytes = ($files | Measure-Object -Property Length -Sum).Sum }
            $inv += [ordered]@{ root=$r; exists=$true; file_count=[int]$files.Count; total_mb=[math]::Round(($bytes/1MB),3); note="RECURSIVE_FILE_COUNT" }
        }
    } else {
        $inv += [ordered]@{ root=$r; exists=$false; file_count=0; total_mb=0; note="NOT_FOUND" }
    }
}
Write-JsonFile -Path $privateInventoryPath -Data ([ordered]@{schema_version="PRIVATE_ROOTS_INVENTORY_V0_1";generated_at=(Get-Date).ToString("o");items=$inv})
$copied.Add("07_LOCAL_ONLY_SAFE_INDEXES/private_roots_inventory.json")

Add-FileInventoryCsv -SourceDir (Join-Path $Root "SSH_COMMAND_LIBRARY") -CsvPath (Join-Path $packDir "07_LOCAL_ONLY_SAFE_INDEXES\ssh_command_library_file_index.csv")
Add-FileInventoryCsv -SourceDir (Join-Path $Root "BUNDLES_LOCAL") -CsvPath (Join-Path $packDir "07_LOCAL_ONLY_SAFE_INDEXES\bundles_local_file_index.csv")
Add-FileInventoryCsv -SourceDir (Join-Path $Root "PRIVATE_CONTEXT_LOCAL") -CsvPath (Join-Path $packDir "07_LOCAL_ONLY_SAFE_INDEXES\private_context_local_file_index.csv")
$copied.Add("07_LOCAL_ONLY_SAFE_INDEXES/ssh_command_library_file_index.csv")
$copied.Add("07_LOCAL_ONLY_SAFE_INDEXES/bundles_local_file_index.csv")
$copied.Add("07_LOCAL_ONLY_SAFE_INDEXES/private_context_local_file_index.csv")

$archiveTopPath = Join-Path $packDir "07_LOCAL_ONLY_SAFE_INDEXES\archive_top_inventory.json"
$archiveRoot = Join-Path $Root "ARCHIVE"
$archiveItems = @()
if (Test-Path -LiteralPath $archiveRoot) {
    $top = Get-ChildItem -LiteralPath $archiveRoot -ErrorAction SilentlyContinue
    foreach ($t in $top) {
        $archiveItems += [ordered]@{ name=$t.Name; type=if($t.PSIsContainer){"dir"}else{"file"}; size_bytes=if($t.PSIsContainer){0}else{$t.Length} }
    }
}
Write-JsonFile -Path $archiveTopPath -Data ([ordered]@{schema_version="ARCHIVE_TOP_INVENTORY_V0_1";generated_at=(Get-Date).ToString("o");items=$archiveItems;note="Top-level only; full archive not copied."})
$copied.Add("07_LOCAL_ONLY_SAFE_INDEXES/archive_top_inventory.json")

# 9) optional private approved copy (safe allowlist only)
$privateNotePath = Join-Path $packDir "08_PRIVATE_CONTEXT_SELECTED\PRIVATE_COPY_POLICY.md"
if (-not $IncludePrivateApproved) {
    @(
        "# PRIVATE COPY POLICY",
        "",
        "IncludePrivateApproved is OFF.",
        "No raw private files were copied.",
        "Only safe metadata inventories are included in 07_LOCAL_ONLY_SAFE_INDEXES."
    ) | Set-Content -LiteralPath $privateNotePath -Encoding UTF8
} else {
    @(
        "# PRIVATE COPY POLICY",
        "",
        "IncludePrivateApproved is ON.",
        "Safe allowlist copy mode: .md/.txt/.json only from PRIVATE_CONTEXT_LOCAL, excluding credential-like names."
    ) | Set-Content -LiteralPath $privateNotePath -Encoding UTF8

    $pcRoot = Join-Path $Root "PRIVATE_CONTEXT_LOCAL"
    if (Test-Path -LiteralPath $pcRoot) {
        $safeFiles = Get-ChildItem -LiteralPath $pcRoot -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object {
                $_.Extension -in @('.md','.txt','.json') -and
                $_.Name -notmatch 'token|secret|password|credential|cookie|session|key|id_rsa|id_ed25519|\.env'
            }
        foreach ($sf in $safeFiles) {
            $rel = $sf.FullName.Substring($pcRoot.Length).TrimStart('\\')
            $dst = Join-Path $packDir ("08_PRIVATE_CONTEXT_SELECTED\" + $rel)
            $parent = Split-Path -Parent $dst
            if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
            Copy-Item -LiteralPath $sf.FullName -Destination $dst -Force
            $copied.Add("08_PRIVATE_CONTEXT_SELECTED/" + ($rel -replace "\\","/"))
        }
    }
}
$copied.Add("08_PRIVATE_CONTEXT_SELECTED/PRIVATE_COPY_POLICY.md")

# 10) manifest and hashes
$allFiles = Get-ChildItem -LiteralPath $packDir -Recurse -File
$manifestCsvPath = Join-Path $packDir "MANIFEST.csv"
$hashPath = Join-Path $packDir "SHA256SUMS.txt"

$manifestRows = foreach ($f in $allFiles) {
    $rel = $f.FullName.Substring($packDir.Length).TrimStart('\\')
    $sha = (Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256).Hash.ToLower()
    [pscustomobject]@{
        relative_path = ($rel -replace "\\","/")
        size_bytes = $f.Length
        sha256 = $sha
    }
}
$manifestRows | Export-Csv -LiteralPath $manifestCsvPath -NoTypeInformation -Encoding UTF8

$hashLines = foreach ($row in $manifestRows) {
    "$($row.sha256) *$($row.relative_path)"
}
$hashLines | Set-Content -LiteralPath $hashPath -Encoding UTF8

# 11) receipt
$receiptPath = Join-Path $packDir "09_RECEIPTS\CHAT_COMPILATION_RECEIPT.json"
$receipt = [ordered]@{
    schema_version = "CHAT_COMPILATION_RECEIPT_V0_1"
    task_id = $TaskId
    generated_at = (Get-Date).ToString("o")
    root = $Root
    analysis_path = $AnalysisPath
    output_dir = $packDir
    include_private_approved = [bool]$IncludePrivateApproved
    for_vm2 = [bool]$ForVM2
    raw_secrets_copied = $false
    copied_entries_count = $copied.Count
    notes = @(
        "Default mode copies safe docs/state/evidence and metadata inventories.",
        "Raw keys/tokens/passwords/.env/private command bodies are excluded."
    )
}
Write-JsonFile -Path $receiptPath -Data $receipt

# refresh manifest/hash after receipt creation
$allFiles = Get-ChildItem -LiteralPath $packDir -Recurse -File
$manifestRows = foreach ($f in $allFiles) {
    $rel = $f.FullName.Substring($packDir.Length).TrimStart('\\')
    $sha = (Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256).Hash.ToLower()
    [pscustomobject]@{
        relative_path = ($rel -replace "\\","/")
        size_bytes = $f.Length
        sha256 = $sha
    }
}
$manifestRows | Export-Csv -LiteralPath $manifestCsvPath -NoTypeInformation -Encoding UTF8
$hashLines = foreach ($row in $manifestRows) { "$($row.sha256) *$($row.relative_path)" }
$hashLines | Set-Content -LiteralPath $hashPath -Encoding UTF8

# 12) zip
$zipPath = Join-Path $chatRoot ($packName + ".zip")
if (Test-Path -LiteralPath $zipPath) { Remove-Item -LiteralPath $zipPath -Force }
Compress-Archive -Path (Join-Path $packDir "*") -DestinationPath $zipPath -Force

$lastPathFile = Join-Path $Root "CURRENT_STATE\ADMINISTRATUM_ANALYZER\LAST_CHAT_COMPILATION_PATH.txt"
$zipPath | Set-Content -LiteralPath $lastPathFile -Encoding UTF8

Write-Output $zipPath
