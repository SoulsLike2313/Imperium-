param(
    [string]$Root = "E:\IMPERIUM",
    [string]$Remote = "https://github.com/SoulsLike2313/Imperium-.git",
    [string]$Target = "FULL_IMPERIUM_SUMMARY",
    [switch]$ForVM2,
    [switch]$JsonOnly
)

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $Root

$outputDir = Join-Path $Root "CURRENT_STATE\ADMINISTRATUM_ANALYZER"
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

function Write-JsonFile {
    param([string]$Path, $Data)
    $Data | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $Path -Encoding UTF8
}

function Get-DirStats {
    param([string]$Path, [bool]$SkipRecursive = $false)
    if (-not (Test-Path -LiteralPath $Path)) {
        return [ordered]@{
            path = $Path
            exists = $false
            file_count = 0
            total_mb = 0
            note = "NOT_FOUND"
        }
    }

    if ($SkipRecursive) {
        $topFiles = Get-ChildItem -LiteralPath $Path -File -ErrorAction SilentlyContinue
        $bytes = 0
        if ($topFiles) { $bytes = ($topFiles | Measure-Object -Property Length -Sum).Sum }
        return [ordered]@{
            path = $Path
            exists = $true
            file_count = [int]($topFiles.Count)
            total_mb = [math]::Round(($bytes / 1MB), 3)
            note = "TOP_LEVEL_ONLY"
        }
    }

    $files = Get-ChildItem -LiteralPath $Path -Recurse -File -ErrorAction SilentlyContinue
    $bytes = 0
    if ($files) { $bytes = ($files | Measure-Object -Property Length -Sum).Sum }

    return [ordered]@{
        path = $Path
        exists = $true
        file_count = [int]($files.Count)
        total_mb = [math]::Round(($bytes / 1MB), 3)
        note = "RECURSIVE_FILE_COUNT"
    }
}

function Test-IgnoreRule {
    param([string]$Path)
    $out = git check-ignore -v -- $Path 2>$null
    return [ordered]@{
        path = $Path
        ignored = ($LASTEXITCODE -eq 0)
        detail = if ($LASTEXITCODE -eq 0) { $out } else { "NOT_IGNORED" }
    }
}

$targetMode = if ($ForVM2 -or $Target -eq "VM2_WORK") { "VM2_WORK" } else { "FULL_IMPERIUM_SUMMARY" }
$timestamp = (Get-Date).ToString("o")

$branch = (git branch --show-current).Trim()
$head = (git rev-parse HEAD).Trim()
$remoteActual = (git remote get-url origin 2>$null)
if ([string]::IsNullOrWhiteSpace($remoteActual)) { $remoteActual = $Remote }
$remoteActual = $remoteActual.Trim()
$statusShort = @(git status --short)
$trackedFiles = @(git ls-files)
$trackedFileCount = $trackedFiles.Count

$requiredPublic = @(
    "README.md",
    "START_HERE.md",
    "CURRENT_STATE/LAST_POINT_STATE.json",
    "CURRENT_STATE/NEXT_ATOMIC_STEP.md",
    "CURRENT_STATE/DO_NOT_DO.md",
    "DOCS/REPO_MAP.md",
    "DOCS/COMMANDS.md",
    "DOCS/BUNDLE_SYSTEM.md",
    "DOCS/CHAT_ENTRY_PROTOCOL.md",
    "DOCS/PUBLIC_PRIVATE_BOUNDARY.md",
    "DOCS/ADMINISTRATUM_OPERATIONAL_AUTHORITY.md",
    "ORGANS/ADMINISTRATUM/ORGAN_CONTRACT.json"
)

$recommendedOrientation = @(
    "DOCS/VM2_BOOTSTRAP_PROTOCOL.md"
)

$fileChecks = @()
foreach ($p in ($requiredPublic + $recommendedOrientation | Select-Object -Unique)) {
    $full = Join-Path $Root ($p -replace "/", "\\")
    $fileChecks += [ordered]@{
        path = $p
        exists = (Test-Path -LiteralPath $full)
    }
}

$keyArtifacts = @(
    "ARTIFACTS/TASK-20260510-GIT-SANITIZE-PRIVATE-SOURCES-AND-CLEAN-HISTORY-V0_1/04_RECEIPTS/FINAL_RECEIPT.json",
    "ARTIFACTS/TASK-20260510-ADMINISTRATUM-REPO-LOCAL-ENGINEERING-CLEAN-POINT-V0_1/06_RECEIPTS/FINAL_RECEIPT.json",
    "ARTIFACTS/TASK-20260510-REPO-FORMATTING-AND-IGNORE-RULES-REPAIR-V0_1/06_RECEIPTS/FINAL_RECEIPT.json"
)

$artifactChecks = @()
foreach ($p in $keyArtifacts) {
    $full = Join-Path $Root ($p -replace "/", "\\")
    $artifactChecks += [ordered]@{ path = $p; exists = (Test-Path -LiteralPath $full) }
}

$localRoots = @(
    [ordered]@{ name = "SSH_COMMAND_LIBRARY"; path = "SSH_COMMAND_LIBRARY"; skip_recursive = $false },
    [ordered]@{ name = "ARCHIVE"; path = "ARCHIVE"; skip_recursive = $true },
    [ordered]@{ name = "BUNDLES_LOCAL"; path = "BUNDLES_LOCAL"; skip_recursive = $false },
    [ordered]@{ name = "PRIVATE_CONTEXT_LOCAL"; path = "PRIVATE_CONTEXT_LOCAL"; skip_recursive = $false },
    [ordered]@{ name = "RUNTIME_LOCAL"; path = "RUNTIME_LOCAL"; skip_recursive = $false }
)

$localStats = @()
foreach ($r in $localRoots) {
    $full = Join-Path $Root $r.path
    $s = Get-DirStats -Path $full -SkipRecursive:$r.skip_recursive
    $localStats += [ordered]@{
        root = $r.name
        path = $r.path
        exists = $s.exists
        file_count = $s.file_count
        total_mb = $s.total_mb
        note = $s.note
    }
}

$observedChecks = @(
    [ordered]@{ path = "OBSERVED/THRONE_REPO_COPY"; exists = (Test-Path -LiteralPath (Join-Path $Root "OBSERVED\THRONE_REPO_COPY")) },
    [ordered]@{ path = "OBSERVED/VM3_REPO_COPY"; exists = (Test-Path -LiteralPath (Join-Path $Root "OBSERVED\VM3_REPO_COPY")) },
    [ordered]@{ path = "CHAT_COMPILATIONS_LOCAL"; exists = (Test-Path -LiteralPath (Join-Path $Root "CHAT_COMPILATIONS_LOCAL")) }
)

$ignoreChecks = @(
    (Test-IgnoreRule -Path "SSH_COMMAND_LIBRARY"),
    (Test-IgnoreRule -Path "ARCHIVE"),
    (Test-IgnoreRule -Path "BUNDLES_LOCAL"),
    (Test-IgnoreRule -Path "PRIVATE_CONTEXT_LOCAL"),
    (Test-IgnoreRule -Path "RUNTIME_LOCAL"),
    (Test-IgnoreRule -Path "CHAT_COMPILATIONS_LOCAL")
)

$suspiciousRegexTracked = "(^|/)SSH_COMMAND_LIBRARY(/|$)|(^|/)ARCHIVE(/|$)|(^|/)BUNDLES_LOCAL(/|$)|(^|/)PRIVATE_CONTEXT_LOCAL(/|$)|(^|/)RUNTIME_LOCAL(/|$)|(^|/)(id_rsa(\\..*)?|id_ed25519(\\..*)?|known_hosts|authorized_keys)$|\\.pem$|\\.ppk$|\\.key$|(^|/)\\.env(\\.|$)"
$suspiciousRegexHistory = "(^|/)SSH_COMMAND_LIBRARY(/|$)|(^|/)(id_rsa(\\..*)?|id_ed25519(\\..*)?|known_hosts|authorized_keys)$|\\.pem$|\\.ppk$|\\.key$|(^|/)\\.env(\\.|$)"

$trackedSuspicious = @($trackedFiles | Where-Object { $_ -match $suspiciousRegexTracked })
$historyPaths = @(git log --all --name-only --pretty=format: | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
$historySuspicious = @($historyPaths | Where-Object { $_ -match $suspiciousRegexHistory })

$untrackedLines = @($statusShort | Where-Object { $_ -like "?? *" })
$untrackedPaths = @()
foreach ($line in $untrackedLines) {
    $p = $line.Substring(3).Trim()
    if ($p) { $untrackedPaths += $p }
}

$largeUntracked = @()
foreach ($rel in $untrackedPaths) {
    $full = Join-Path $Root ($rel -replace "/", "\\")
    if (Test-Path -LiteralPath $full -PathType Leaf) {
        $fi = Get-Item -LiteralPath $full
        if ($fi.Length -ge 5MB) {
            $largeUntracked += [ordered]@{
                path = $rel
                size_mb = [math]::Round(($fi.Length / 1MB), 3)
            }
        }
    } elseif (Test-Path -LiteralPath $full -PathType Container) {
        $largeUntracked += [ordered]@{
            path = $rel
            size_mb = "DIR_UNTRACKED"
        }
    }
}

$missingPublic = @($requiredPublic | Where-Object { -not (Test-Path -LiteralPath (Join-Path $Root ($_ -replace "/", "\\"))) })

$vm2Checks = [ordered]@{
    vm2_bootstrap_protocol_exists = (Test-Path -LiteralPath (Join-Path $Root "DOCS\VM2_BOOTSTRAP_PROTOCOL.md"))
    private_vm2_connection_index_known = (Test-Path -LiteralPath (Join-Path $Root "PRIVATE_CONTEXT_LOCAL\VM2_CONNECTION_INDEX.json"))
    vm2_target_path_known = (Test-Path -LiteralPath (Join-Path $Root "PRIVATE_CONTEXT_LOCAL\VM2_TARGET_PATH.txt"))
    private_bundle_policy_known = (Test-Path -LiteralPath (Join-Path $Root "DOCS\BUNDLE_SYSTEM.md"))
    clone_setup_commands_available = (Test-Path -LiteralPath (Join-Path $Root "DOCS\COMMANDS.md"))
}

$includePublicPaths = @($requiredPublic | Where-Object { Test-Path -LiteralPath (Join-Path $Root ($_ -replace "/", "\\")) })
$includeArtifactPaths = @($keyArtifacts | Where-Object { Test-Path -LiteralPath (Join-Path $Root ($_ -replace "/", "\\")) })
$includeLocalSafe = @()
$localSafeCandidates = @(
    "CURRENT_STATE/LOCAL_ONLY_SOURCES_INDEX.md",
    "CURRENT_STATE/LOCAL_ONLY_SOURCES_INDEX.json",
    "CURRENT_STATE/EXCLUDED_LOCAL_SOURCES.md",
    "CURRENT_STATE/ADMINISTRATUM_ANALYZER/GIT_LOCAL_ANALYSIS.json",
    "CURRENT_STATE/ADMINISTRATUM_ANALYZER/CONTEXT_GAP_REPORT.md"
)
foreach ($p in $localSafeCandidates) {
    if (Test-Path -LiteralPath (Join-Path $Root ($p -replace "/", "\\"))) { $includeLocalSafe += $p }
}

$privateCandidates = @(
    "SSH_COMMAND_LIBRARY inventory (filenames/sizes only)",
    "BUNDLES_LOCAL inventory (filenames/sizes only)",
    "PRIVATE_CONTEXT_LOCAL inventory (filenames/sizes only)",
    "ARCHIVE top-level inventory only",
    "Selected recent local artifact/bundle indexes"
)

$recommendedCompilation = [ordered]@{
    bundle_type = "CHAT_COMPILATION_SAFE_V0_1"
    target = $targetMode
    timestamp = $timestamp
    output_root = "CHAT_COMPILATIONS_LOCAL"
    include_public_paths = $includePublicPaths
    include_artifact_paths = $includeArtifactPaths
    include_local_safe_indexes = $includeLocalSafe
    include_private_candidates = $privateCandidates
    exclude_always = @(
        "raw private keys",
        ".env values",
        "tokens",
        "passwords",
        "cookies",
        "sessions",
        "full ARCHIVE",
        "full SSH_COMMAND_LIBRARY content",
        "unselected heavy tar/zip bases",
        "THRONE sync material"
    )
    owner_approval_required_for = @(
        "Any private raw content beyond safe indexes",
        "Any VM2 connection/address details",
        "Any file classes that may include credentials"
    )
    reasons = @(
        "Git alone may not contain local/private operational context",
        "Safe bundle improves handoff completeness without exposing raw secrets",
        "Supports Owner-driven upload to chat"
    )
}

$analysis = [ordered]@{
    schema_version = "ADMINISTRATUM_GIT_LOCAL_ANALYSIS_V0_1"
    analyzed_at = $timestamp
    root = $Root
    remote_expected = $Remote
    remote_actual = $remoteActual
    branch = $branch
    head = $head
    target = $targetMode
    git_public = [ordered]@{
        status_short = $statusShort
        tracked_file_count = $trackedFileCount
        required_file_checks = $fileChecks
        key_artifact_receipt_checks = $artifactChecks
    }
    local_private = [ordered]@{
        roots = $localStats
        observed_presence = $observedChecks
    }
    boundary = [ordered]@{
        ignore_checks = $ignoreChecks
        suspicious_tracked_paths_count = $trackedSuspicious.Count
        suspicious_history_paths_count = $historySuspicious.Count
        suspicious_tracked_paths = $trackedSuspicious
        suspicious_history_paths = $historySuspicious
        untracked_files_count = $untrackedPaths.Count
        large_untracked_candidates = $largeUntracked
    }
    context_gaps = [ordered]@{
        missing_required_public_paths = $missingPublic
        vm2_checks = $vm2Checks
    }
    recommended_bundle_plan = $recommendedCompilation
}

$safeInventory = [ordered]@{
    schema_version = "LOCAL_ONLY_SAFE_INVENTORY_V0_1"
    generated_at = $timestamp
    root = $Root
    private_roots = $localStats
    observed_presence = $observedChecks
    notes = @(
        "Inventory contains only path-level and size/count metadata.",
        "No file content is extracted."
    )
}

$analysisJsonPath = Join-Path $outputDir "GIT_LOCAL_ANALYSIS.json"
$gapMdPath = Join-Path $outputDir "CONTEXT_GAP_REPORT.md"
$recommendedPath = Join-Path $outputDir "RECOMMENDED_CHAT_COMPILATION.json"
$safeInventoryPath = Join-Path $outputDir "LOCAL_ONLY_SAFE_INVENTORY.json"
$gitSummaryMdPath = Join-Path $outputDir "GIT_PUBLIC_MEMORY_SUMMARY.md"
$receiptPath = Join-Path $outputDir "ANALYZER_RECEIPT.json"

Write-JsonFile -Path $analysisJsonPath -Data $analysis
Write-JsonFile -Path $recommendedPath -Data $recommendedCompilation
Write-JsonFile -Path $safeInventoryPath -Data $safeInventory

if (-not $JsonOnly) {
    $gitSummary = @()
    $gitSummary += "# GIT PUBLIC MEMORY SUMMARY"
    $gitSummary += ""
    $gitSummary += "- analyzed_at: $timestamp"
    $gitSummary += "- branch: $branch"
    $gitSummary += "- head: $head"
    $gitSummary += "- remote_actual: $remoteActual"
    $gitSummary += "- tracked_file_count: $trackedFileCount"
    $gitSummary += ""
    $gitSummary += "## Required Orientation Files"
    foreach ($c in $fileChecks) {
        $gitSummary += "- $($c.path): $(if($c.exists){'present'}else{'missing'})"
    }
    $gitSummary | Set-Content -LiteralPath $gitSummaryMdPath -Encoding UTF8

    $gap = @()
    $gap += "# CONTEXT GAP REPORT"
    $gap += ""
    $gap += "- target: $targetMode"
    $gap += "- analyzed_at: $timestamp"
    $gap += ""
    $gap += "## Missing Required Public Paths"
    if ($missingPublic.Count -eq 0) {
        $gap += "- none"
    } else {
        foreach ($m in $missingPublic) { $gap += "- $m" }
    }
    $gap += ""
    $gap += "## Boundary Signals"
    $gap += "- suspicious_tracked_paths_count: $($trackedSuspicious.Count)"
    $gap += "- suspicious_history_paths_count: $($historySuspicious.Count)"
    $gap += "- untracked_files_count: $($untrackedPaths.Count)"
    $gap += ""
    $gap += "## Local/Private Roots"
    foreach ($r in $localStats) {
        $gap += "- $($r.root): exists=$($r.exists); file_count=$($r.file_count); total_mb=$($r.total_mb); note=$($r.note)"
    }
    if ($targetMode -eq "VM2_WORK") {
        $gap += ""
        $gap += "## VM2-Specific Checks"
        foreach ($k in $vm2Checks.Keys) {
            $gap += "- ${k}: $($vm2Checks[$k])"
        }
    }
    $gap += ""
    $gap += "## Recommendation"
    $gap += "- Build safe chat compilation from RECOMMENDED_CHAT_COMPILATION.json"
    $gap += "- Include private raw content only with Owner approval and explicit allowlists"

    $gap | Set-Content -LiteralPath $gapMdPath -Encoding UTF8
}

$receipt = [ordered]@{
    schema_version = "ADMINISTRATUM_ANALYZER_RECEIPT_V0_1"
    analyzed_at = $timestamp
    root = $Root
    target = $targetMode
    branch = $branch
    head = $head
    remote = $remoteActual
    outputs = @(
        $analysisJsonPath,
        $recommendedPath,
        $safeInventoryPath,
        $gapMdPath,
        $gitSummaryMdPath
    )
    suspicious_tracked_paths_count = $trackedSuspicious.Count
    suspicious_history_paths_count = $historySuspicious.Count
    raw_secrets_copied = $false
    status = "PASS_WITH_LIMITATIONS"
    limitations = @(
        "Path/metadata analysis only; no secret content extraction.",
        "Context completeness depends on local private sources and Owner approval.",
        "No VM2 execution and no THRONE sync."
    )
}
Write-JsonFile -Path $receiptPath -Data $receipt

Write-Output $analysisJsonPath
