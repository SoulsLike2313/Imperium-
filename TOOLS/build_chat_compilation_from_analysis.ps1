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
    $Data | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $Path -Encoding UTF8
}

function Copy-IfExists {
    param([string]$Source, [string]$Destination)
    if (Test-Path -LiteralPath $Source) {
        $parent = Split-Path -Parent $Destination
        if ($parent -and -not (Test-Path -LiteralPath $parent)) {
            New-Item -ItemType Directory -Force -Path $parent | Out-Null
        }
        Copy-Item -LiteralPath $Source -Destination $Destination -Force
        return $true
    }
    return $false
}

function Add-FileInventoryCsv {
    param([string]$SourceDir, [string]$CsvPath)
    if (-not (Test-Path -LiteralPath $SourceDir)) {
        @([pscustomobject]@{ relative_path = "NOT_FOUND"; size_bytes = 0; last_write_utc = "" }) |
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
        $items = @([pscustomobject]@{ relative_path = "EMPTY"; size_bytes = 0; last_write_utc = "" })
    }

    $items | Export-Csv -LiteralPath $CsvPath -NoTypeInformation -Encoding UTF8
}

if (-not (Test-Path -LiteralPath $AnalysisPath)) {
    throw "Analysis file not found: $AnalysisPath"
}

$recommended = Get-Content -LiteralPath $AnalysisPath -Raw | ConvertFrom-Json
$analysisJsonPath = Join-Path $Root "CURRENT_STATE\ADMINISTRATUM_ANALYZER\GIT_LOCAL_ANALYSIS.json"
$analysis = $null
if (Test-Path -LiteralPath $analysisJsonPath) {
    $analysis = Get-Content -LiteralPath $analysisJsonPath -Raw | ConvertFrom-Json
}

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

$copied = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]

# Analyzer outputs must always be included
$analyzerFiles = @(
    "GIT_LOCAL_ANALYSIS.json",
    "CONTEXT_GAP_REPORT.md",
    "RECOMMENDED_CHAT_COMPILATION.json",
    "LOCAL_ONLY_SAFE_INVENTORY.json",
    "GIT_PUBLIC_MEMORY_SUMMARY.md",
    "GIT_REALITY_REPORT.md",
    "PUBLIC_PRIVATE_BOUNDARY_REPORT.md",
    "WORKTREE_CLASSIFICATION_REPORT.md",
    "WORKTREE_CLASSIFICATION.json",
    "OWNER_NEXT_ACTION.md",
    "LAST_VERIFIED_PUBLIC_HEAD.json",
    "ANALYZER_RECEIPT.json"
)
foreach ($f in $analyzerFiles) {
    $src = Join-Path $Root "CURRENT_STATE\ADMINISTRATUM_ANALYZER\$f"
    $dst = Join-Path $packDir "00_ANALYZER_REPORT\$f"
    if (Copy-IfExists -Source $src -Destination $dst) { $copied.Add("00_ANALYZER_REPORT/$f") }
}

# Git state snapshots
$gitStateFiles = @(
    "BASELINE_GIT_STATUS.txt",
    "BASELINE_GIT_REMOTE.txt",
    "BASELINE_GIT_LOG.txt",
    "BASELINE_GIT_HEAD.txt",
    "BASELINE_GIT_BRANCH.txt"
)
foreach ($f in $gitStateFiles) {
    $src = Join-Path $Root "CURRENT_STATE\ADMINISTRATUM_ANALYZER\$f"
    $dst = Join-Path $packDir "01_GIT_STATE\$f"
    if (Copy-IfExists -Source $src -Destination $dst) { $copied.Add("01_GIT_STATE/$f") }
}

# Root orientation
foreach ($rf in @("README.md", "START_HERE.md", ".gitignore")) {
    $src = Join-Path $Root $rf
    $dst = Join-Path $packDir "02_ROOT_ORIENTATION\$rf"
    if (Copy-IfExists -Source $src -Destination $dst) { $copied.Add("02_ROOT_ORIENTATION/$rf") }
}

# Current state safe set
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
    $rel = $cf -replace "^CURRENT_STATE\\", ""
    $dst = Join-Path $packDir "03_CURRENT_STATE\$rel"
    if (Copy-IfExists -Source $src -Destination $dst) { $copied.Add("03_CURRENT_STATE/" + ($rel -replace "\\", "/")) }
}

# Docs set
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
    $rel = $df -replace "^DOCS\\", ""
    $dst = Join-Path $packDir "04_DOCS\$rel"
    if (Copy-IfExists -Source $src -Destination $dst) { $copied.Add("04_DOCS/" + ($rel -replace "\\", "/")) }
}

# Organs selected
$organFiles = @(
    "ORGANS\ADMINISTRATUM\ORGAN_CONTRACT.json",
    "ORGANS\ADMINISTRATUM\ORGAN_STATUS.json",
    "ORGANS\ADMINISTRATUM\SELF_REPORT.json",
    "ORGANS\ADMINISTRATUM\UTILITY\run_administratum_context_bundle_workflow.ps1"
)
foreach ($of in $organFiles) {
    $src = Join-Path $Root $of
    $rel = $of -replace "^ORGANS\\ADMINISTRATUM\\", "ADMINISTRATUM\\"
    $dst = Join-Path $packDir "05_ORGANS_SELECTED\$rel"
    if (Copy-IfExists -Source $src -Destination $dst) { $copied.Add("05_ORGANS_SELECTED/" + ($rel -replace "\\", "/")) }
}

# Artifact receipts selected
$artifactReceipts = @(
    "ARTIFACTS\TASK-20260510-GIT-SANITIZE-PRIVATE-SOURCES-AND-CLEAN-HISTORY-V0_1\04_RECEIPTS\FINAL_RECEIPT.json",
    "ARTIFACTS\TASK-20260510-ADMINISTRATUM-REPO-LOCAL-ENGINEERING-CLEAN-POINT-V0_1\06_RECEIPTS\FINAL_RECEIPT.json",
    "ARTIFACTS\TASK-20260510-REPO-FORMATTING-AND-IGNORE-RULES-REPAIR-V0_1\06_RECEIPTS\FINAL_RECEIPT.json",
    "ARTIFACTS\TASK-20260510-ADMINISTRATUM-GIT-LOCAL-ANALYZER-AND-CONTEXT-BUNDLE-BUTTON-V0_1\06_RECEIPTS\FINAL_RECEIPT.json"
)
foreach ($ar in $artifactReceipts) {
    $src = Join-Path $Root $ar
    $rel = $ar -replace "^ARTIFACTS\\", ""
    $dst = Join-Path $packDir "06_ARTIFACTS_SELECTED\$rel"
    if (Copy-IfExists -Source $src -Destination $dst) { $copied.Add("06_ARTIFACTS_SELECTED/" + ($rel -replace "\\", "/")) }
}

# Safe local inventories
$privateRootsInventoryPath = Join-Path $packDir "07_LOCAL_ONLY_SAFE_INDEXES\private_roots_inventory.json"
$roots = @("SSH_COMMAND_LIBRARY", "ARCHIVE", "BUNDLES_LOCAL", "PRIVATE_CONTEXT_LOCAL", "RUNTIME_LOCAL")
$inv = @()
foreach ($r in $roots) {
    $full = Join-Path $Root $r
    if (Test-Path -LiteralPath $full) {
        if ($r -eq "ARCHIVE") {
            $topFiles = Get-ChildItem -LiteralPath $full -File -ErrorAction SilentlyContinue
            $bytes = 0
            if ($topFiles) { $bytes = ($topFiles | Measure-Object -Property Length -Sum).Sum }
            $inv += [ordered]@{ root = $r; exists = $true; file_count = [int]$topFiles.Count; total_mb = [math]::Round(($bytes / 1MB), 3); note = "TOP_LEVEL_ONLY" }
        } else {
            $files = Get-ChildItem -LiteralPath $full -Recurse -File -ErrorAction SilentlyContinue
            $bytes = 0
            if ($files) { $bytes = ($files | Measure-Object -Property Length -Sum).Sum }
            $inv += [ordered]@{ root = $r; exists = $true; file_count = [int]$files.Count; total_mb = [math]::Round(($bytes / 1MB), 3); note = "RECURSIVE_FILE_COUNT" }
        }
    } else {
        $inv += [ordered]@{ root = $r; exists = $false; file_count = 0; total_mb = 0; note = "NOT_FOUND" }
    }
}
Write-JsonFile -Path $privateRootsInventoryPath -Data ([ordered]@{ schema_version = "PRIVATE_ROOTS_INVENTORY_V0_2"; generated_at = (Get-Date).ToString("o"); items = $inv })
$copied.Add("07_LOCAL_ONLY_SAFE_INDEXES/private_roots_inventory.json")

Add-FileInventoryCsv -SourceDir (Join-Path $Root "SSH_COMMAND_LIBRARY") -CsvPath (Join-Path $packDir "07_LOCAL_ONLY_SAFE_INDEXES\ssh_command_library_file_index.csv")
Add-FileInventoryCsv -SourceDir (Join-Path $Root "BUNDLES_LOCAL") -CsvPath (Join-Path $packDir "07_LOCAL_ONLY_SAFE_INDEXES\bundles_local_file_index.csv")
Add-FileInventoryCsv -SourceDir (Join-Path $Root "PRIVATE_CONTEXT_LOCAL") -CsvPath (Join-Path $packDir "07_LOCAL_ONLY_SAFE_INDEXES\private_context_local_file_index.csv")
$copied.Add("07_LOCAL_ONLY_SAFE_INDEXES/ssh_command_library_file_index.csv")
$copied.Add("07_LOCAL_ONLY_SAFE_INDEXES/bundles_local_file_index.csv")
$copied.Add("07_LOCAL_ONLY_SAFE_INDEXES/private_context_local_file_index.csv")

$archiveTopPath = Join-Path $packDir "07_LOCAL_ONLY_SAFE_INDEXES\archive_top_inventory.json"
$archiveItems = @()
$archiveRoot = Join-Path $Root "ARCHIVE"
if (Test-Path -LiteralPath $archiveRoot) {
    foreach ($entry in (Get-ChildItem -LiteralPath $archiveRoot -ErrorAction SilentlyContinue)) {
        $archiveItems += [ordered]@{ name = $entry.Name; type = if ($entry.PSIsContainer) { "dir" } else { "file" }; size_bytes = if ($entry.PSIsContainer) { 0 } else { $entry.Length } }
    }
}
Write-JsonFile -Path $archiveTopPath -Data ([ordered]@{ schema_version = "ARCHIVE_TOP_INVENTORY_V0_2"; generated_at = (Get-Date).ToString("o"); items = $archiveItems; note = "Top-level only; full archive never copied." })
$copied.Add("07_LOCAL_ONLY_SAFE_INDEXES/archive_top_inventory.json")

# Private context selected
$policyPath = Join-Path $packDir "08_PRIVATE_CONTEXT_SELECTED\PRIVATE_COPY_POLICY.md"
if (-not $IncludePrivateApproved) {
    @(
        "# PRIVATE COPY POLICY",
        "",
        "IncludePrivateApproved is OFF.",
        "No raw private files copied.",
        "Only safe metadata inventories included."
    ) | Set-Content -LiteralPath $policyPath -Encoding UTF8
} else {
    @(
        "# PRIVATE COPY POLICY",
        "",
        "IncludePrivateApproved is ON.",
        "Safe allowlist copy mode: .md/.txt/.json only from PRIVATE_CONTEXT_LOCAL (credential-like filenames blocked)."
    ) | Set-Content -LiteralPath $policyPath -Encoding UTF8

    $pcRoot = Join-Path $Root "PRIVATE_CONTEXT_LOCAL"
    if (Test-Path -LiteralPath $pcRoot) {
        $safeFiles = Get-ChildItem -LiteralPath $pcRoot -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object {
                $_.Extension -in @('.md', '.txt', '.json') -and
                $_.Name -notmatch 'token|secret|password|credential|cookie|session|key|id_rsa|id_ed25519|\.env'
            }
        foreach ($sf in $safeFiles) {
            $rel = $sf.FullName.Substring($pcRoot.Length).TrimStart('\\')
            $dst = Join-Path $packDir "08_PRIVATE_CONTEXT_SELECTED\$rel"
            $parent = Split-Path -Parent $dst
            if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
            Copy-Item -LiteralPath $sf.FullName -Destination $dst -Force
            $copied.Add("08_PRIVATE_CONTEXT_SELECTED/" + ($rel -replace "\\", "/"))
        }
    }
}
$copied.Add("08_PRIVATE_CONTEXT_SELECTED/PRIVATE_COPY_POLICY.md")

# Guidance warnings from analyzer v0.2
$bundleOptional = $false
if ($analysis -and $analysis.recommended_compilation -and ($analysis.recommended_compilation.needed -eq $false)) {
    $bundleOptional = $true
    $warnings.Add("Analyzer indicates bundle is optional for current target.")
}
if ($analysis -and $analysis.git_reality -and $analysis.git_reality.git_reality_verdict -ne "CLEAN_SYNCED") {
    $warnings.Add("Git reality verdict is '$($analysis.git_reality.git_reality_verdict)'; review sync state before trusting output.")
}
if ($analysis -and $analysis.git_reality -and $analysis.git_reality.working_tree_clean -eq $false) {
    $warnings.Add("Working tree is dirty at analysis time; verify change classification before using bundle as final source.")
}
if ($analysis -and $analysis.public_private_boundary -and $analysis.public_private_boundary.boundary_verdict -ne "CLEAN") {
    $warnings.Add("Boundary verdict is '$($analysis.public_private_boundary.boundary_verdict)'; review boundary warnings.")
}
if ($analysis -and $analysis.owner_action -and $analysis.owner_action.recommended_owner_action -eq "MANUAL_REVIEW_REQUIRED") {
    $warnings.Add("Analyzer owner action is MANUAL_REVIEW_REQUIRED; bundle built only as technical output and requires explicit human review.")
}

# Manifest + hashes
$manifestCsvPath = Join-Path $packDir "MANIFEST.csv"
$hashPath = Join-Path $packDir "SHA256SUMS.txt"

$fileRows = Get-ChildItem -LiteralPath $packDir -Recurse -File | ForEach-Object {
    $rel = $_.FullName.Substring($packDir.Length).TrimStart('\\') -replace "\\", "/"
    [pscustomobject]@{
        relative_path = $rel
        size_bytes = $_.Length
        sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLower()
    }
}
$fileRows | Export-Csv -LiteralPath $manifestCsvPath -NoTypeInformation -Encoding UTF8
($fileRows | ForEach-Object { "$($_.sha256) *$($_.relative_path)" }) | Set-Content -LiteralPath $hashPath -Encoding UTF8

# Receipt
$receiptPath = Join-Path $packDir "09_RECEIPTS\CHAT_COMPILATION_RECEIPT.json"
$receipt = [ordered]@{
    schema_version = "CHAT_COMPILATION_RECEIPT_V0_2"
    task_id = $TaskId
    generated_at = (Get-Date).ToString("o")
    root = $Root
    analysis_path = $AnalysisPath
    analysis_json_path = if ($analysis) { $analysisJsonPath } else { $null }
    output_dir = $packDir
    include_private_approved = [bool]$IncludePrivateApproved
    for_vm2 = [bool]$ForVM2
    bundle_optional = $bundleOptional
    warnings = @($warnings)
    raw_secrets_copied = $false
    copied_entries_count = $copied.Count
}
Write-JsonFile -Path $receiptPath -Data $receipt

# Refresh manifest/hash after receipt write
$fileRows = Get-ChildItem -LiteralPath $packDir -Recurse -File | ForEach-Object {
    $rel = $_.FullName.Substring($packDir.Length).TrimStart('\\') -replace "\\", "/"
    [pscustomobject]@{
        relative_path = $rel
        size_bytes = $_.Length
        sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLower()
    }
}
$fileRows | Export-Csv -LiteralPath $manifestCsvPath -NoTypeInformation -Encoding UTF8
($fileRows | ForEach-Object { "$($_.sha256) *$($_.relative_path)" }) | Set-Content -LiteralPath $hashPath -Encoding UTF8

# Zip output
$zipPath = Join-Path $chatRoot ($packName + ".zip")
if (Test-Path -LiteralPath $zipPath) {
    Remove-Item -LiteralPath $zipPath -Force
}
Compress-Archive -Path (Join-Path $packDir "*") -DestinationPath $zipPath -Force

$zipPath | Set-Content -LiteralPath (Join-Path $Root "CURRENT_STATE\ADMINISTRATUM_ANALYZER\LAST_CHAT_COMPILATION_PATH.txt") -Encoding UTF8

Write-Output $zipPath
