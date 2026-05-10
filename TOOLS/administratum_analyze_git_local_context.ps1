param(
    [string]$Root = "E:\IMPERIUM",
    [string]$Remote = "https://github.com/SoulsLike2313/Imperium-.git",
    [string]$Target = "FULL_IMPERIUM_SUMMARY",
    [switch]$ForVM2,
    [switch]$JsonOnly,
    [switch]$PostPushRealityCheck
)

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $Root

$outputDir = Join-Path $Root "CURRENT_STATE\ADMINISTRATUM_ANALYZER"
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

function Write-JsonFile {
    param(
        [string]$Path,
        $Data
    )
    $Data | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $Path -Encoding UTF8
}

function Get-DirStats {
    param(
        [string]$Path,
        [bool]$SkipRecursive = $false
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return [ordered]@{
            exists = $false
            file_count = 0
            total_mb = 0
            note = "NOT_FOUND"
        }
    }

    if ($SkipRecursive) {
        $topFiles = Get-ChildItem -LiteralPath $Path -File -ErrorAction SilentlyContinue
        $bytes = 0
        if ($topFiles) {
            $bytes = ($topFiles | Measure-Object -Property Length -Sum).Sum
        }
        return [ordered]@{
            exists = $true
            file_count = [int]$topFiles.Count
            total_mb = [math]::Round(($bytes / 1MB), 3)
            note = "TOP_LEVEL_ONLY"
        }
    }

    $files = Get-ChildItem -LiteralPath $Path -Recurse -File -ErrorAction SilentlyContinue
    $bytes = 0
    if ($files) {
        $bytes = ($files | Measure-Object -Property Length -Sum).Sum
    }

    return [ordered]@{
        exists = $true
        file_count = [int]$files.Count
        total_mb = [math]::Round(($bytes / 1MB), 3)
        note = "RECURSIVE_FILE_COUNT"
    }
}

function Test-Ignore {
    param([string]$Path)
    $out = git check-ignore -v -- $Path 2>$null
    return [ordered]@{
        path = $Path
        ignored = ($LASTEXITCODE -eq 0)
        detail = if ($LASTEXITCODE -eq 0) { $out } else { "NOT_IGNORED" }
    }
}

function Test-InGitTracking {
    param([string]$Path)
    $escaped = $Path -replace '\\','/'
    $items = @(git ls-files -- "$escaped" 2>$null)
    return ($items.Count -gt 0)
}

function Test-ExistsRel {
    param([string]$RelPath)
    $full = Join-Path $Root ($RelPath -replace '/', '\\')
    return (Test-Path -LiteralPath $full)
}

$analysisTime = (Get-Date).ToString("o")
$targetMode = if ($ForVM2 -or $Target -eq "VM2_WORK") { "VM2_WORK" } else { "FULL_IMPERIUM_SUMMARY" }

# Git reality core
$branch = (git branch --show-current).Trim()
$localHead = (git rev-parse HEAD 2>$null).Trim()
$originMasterHead = (git rev-parse origin/master 2>$null).Trim()
$upstreamHead = $null
$upstreamWarning = $null
$uOut = git rev-parse '@{u}' 2>$null
if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($uOut)) {
    $upstreamHead = $uOut.Trim()
} else {
    $upstreamWarning = "NO_UPSTREAM_CONFIGURED"
}

$lsRemoteRaw = (git ls-remote origin refs/heads/master 2>$null)
$lsRemoteMasterHead = $null
if (-not [string]::IsNullOrWhiteSpace($lsRemoteRaw)) {
    $lsRemoteMasterHead = ($lsRemoteRaw -split "\s+")[0].Trim()
}

$statusShort = @(git status --short)
$workingTreeClean = ($statusShort.Count -eq 0)

$headMatchesOrigin = ($localHead -and $originMasterHead -and ($localHead -eq $originMasterHead))
$headMatchesLsRemote = ($localHead -and $lsRemoteMasterHead -and ($localHead -eq $lsRemoteMasterHead))
$originMatchesLsRemote = ($originMasterHead -and $lsRemoteMasterHead -and ($originMasterHead -eq $lsRemoteMasterHead))

$postPushRealityPassed = ($headMatchesOrigin -and $headMatchesLsRemote -and $originMatchesLsRemote)

$gitRealityVerdict = "UNKNOWN"
if (-not $workingTreeClean) {
    $gitRealityVerdict = "LOCAL_CHANGES_PRESENT"
} elseif (-not $headMatchesOrigin) {
    $gitRealityVerdict = "LOCAL_HEAD_NOT_PUSHED"
} elseif (-not $originMatchesLsRemote) {
    $gitRealityVerdict = "ORIGIN_NOT_FETCHED_OR_STALE"
} elseif (-not $headMatchesLsRemote) {
    $gitRealityVerdict = "REMOTE_MISMATCH"
} elseif ($postPushRealityPassed) {
    $gitRealityVerdict = "CLEAN_SYNCED"
}

# Public memory checks
$requiredDocs = @(
    "README.md",
    "START_HERE.md",
    "CURRENT_STATE/LAST_POINT_STATE.json",
    "DOCS/REPO_MAP.md",
    "DOCS/COMMANDS.md",
    "DOCS/BUNDLE_SYSTEM.md",
    "DOCS/CHAT_ENTRY_PROTOCOL.md",
    "DOCS/PUBLIC_PRIVATE_BOUNDARY.md",
    "DOCS/ADMINISTRATUM_OPERATIONAL_AUTHORITY.md"
)
$requiredForTarget = @(
    "CURRENT_STATE/NEXT_ATOMIC_STEP.md",
    "CURRENT_STATE/DO_NOT_DO.md",
    "ORGANS/ADMINISTRATUM/ORGAN_CONTRACT.json"
)

$requiredChecks = @{}
foreach ($r in ($requiredDocs + $requiredForTarget | Select-Object -Unique)) {
    $requiredChecks[$r] = (Test-ExistsRel -RelPath $r)
}

$readmeExists = $requiredChecks["README.md"]
$startHereExists = $requiredChecks["START_HERE.md"]
$currentStateExists = (Test-Path -LiteralPath (Join-Path $Root "CURRENT_STATE"))
$lastPointExists = $requiredChecks["CURRENT_STATE/LAST_POINT_STATE.json"]
$docsRequiredExists = @($requiredDocs | Where-Object { -not $requiredChecks[$_] }).Count -eq 0
$administratumContractExists = $requiredChecks["ORGANS/ADMINISTRATUM/ORGAN_CONTRACT.json"]
$toolsAnalyzerExists = Test-ExistsRel -RelPath "TOOLS/administratum_analyze_git_local_context.ps1"
$toolsBuilderExists = Test-ExistsRel -RelPath "TOOLS/build_chat_compilation_from_analysis.ps1"
$workflowLauncherExists = Test-ExistsRel -RelPath "ORGANS/ADMINISTRATUM/UTILITY/run_administratum_context_bundle_workflow.ps1"

# Boundary scans
$trackedFiles = @(git ls-files)
$historyPaths = @(git log --all --name-only --pretty=format: | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

$suspTrackedRegex = "(^|/)SSH_COMMAND_LIBRARY(/|$)|(^|/)ARCHIVE(/|$)|(^|/)BUNDLES_LOCAL(/|$)|(^|/)PRIVATE_CONTEXT_LOCAL(/|$)|(^|/)RUNTIME_LOCAL(/|$)|(^|/)CHAT_COMPILATIONS_LOCAL(/|$)|(^|/)(id_rsa(\\..*)?|id_ed25519(\\..*)?|known_hosts|authorized_keys)$|\\.pem$|\\.ppk$|\\.key$|(^|/)\\.env(\\.|$)"
$suspHistoryRegex = "(^|/)SSH_COMMAND_LIBRARY(/|$)|(^|/)(id_rsa(\\..*)?|id_ed25519(\\..*)?|known_hosts|authorized_keys)$|\\.pem$|\\.ppk$|\\.key$|(^|/)\\.env(\\.|$)"

$trackedSuspicious = @($trackedFiles | Where-Object { $_ -match $suspTrackedRegex })
$historySuspicious = @($historyPaths | Where-Object { $_ -match $suspHistoryRegex })

$trackedSuspiciousFile = Join-Path $outputDir "TRACKED_SUSPICIOUS_PATHS_V0_2.txt"
$historySuspiciousFile = Join-Path $outputDir "HISTORY_SUSPICIOUS_PATHS_V0_2.txt"
if ($trackedSuspicious.Count -eq 0) { "NO_MATCHES" | Set-Content -LiteralPath $trackedSuspiciousFile -Encoding UTF8 } else { $trackedSuspicious | Set-Content -LiteralPath $trackedSuspiciousFile -Encoding UTF8 }
if ($historySuspicious.Count -eq 0) { "NO_MATCHES" | Set-Content -LiteralPath $historySuspiciousFile -Encoding UTF8 } else { $historySuspicious | Set-Content -LiteralPath $historySuspiciousFile -Encoding UTF8 }

# Untracked state
$untrackedLines = @($statusShort | Where-Object { $_ -like "?? *" })
$untrackedPaths = @()
foreach ($line in $untrackedLines) {
    $p = $line.Substring(3).Trim()
    if ($p) { $untrackedPaths += $p }
}

$untrackedSummaryFile = Join-Path $outputDir "UNTRACKED_PATHS_SUMMARY_V0_2.txt"
if ($untrackedPaths.Count -eq 0) {
    "NO_UNTRACKED" | Set-Content -LiteralPath $untrackedSummaryFile -Encoding UTF8
} else {
    $untrackedPaths | Set-Content -LiteralPath $untrackedSummaryFile -Encoding UTF8
}

$untrackedSuspiciousRegex = "id_rsa|id_ed25519|\\.pem$|\\.ppk$|\\.key$|\\.env|token|secret|password|credential|cookie|session|known_hosts|authorized_keys"
$untrackedSuspicious = @($untrackedPaths | Where-Object { $_ -match $untrackedSuspiciousRegex })

$untrackedHeavy = @()
foreach ($rel in $untrackedPaths) {
    $full = Join-Path $Root ($rel -replace '/', '\\')
    if (Test-Path -LiteralPath $full -PathType Leaf) {
        $fi = Get-Item -LiteralPath $full
        if ($fi.Length -ge 10MB) {
            $untrackedHeavy += $rel
        }
    } elseif (Test-Path -LiteralPath $full -PathType Container) {
        $untrackedHeavy += "$rel [DIR]"
    }
}

# Local/private memory matrix
$privateRoots = @(
    [ordered]@{ key = "SSH_COMMAND_LIBRARY"; rel = "SSH_COMMAND_LIBRARY"; skip_recursive = $false; include_policy = "SAFE_INDEX_ONLY"; needed_full = $true; needed_vm2 = $true },
    [ordered]@{ key = "ARCHIVE"; rel = "ARCHIVE"; skip_recursive = $true; include_policy = "TOP_LEVEL_INVENTORY_ONLY"; needed_full = $false; needed_vm2 = $false },
    [ordered]@{ key = "BUNDLES_LOCAL"; rel = "BUNDLES_LOCAL"; skip_recursive = $false; include_policy = "SAFE_INDEX_ONLY"; needed_full = $true; needed_vm2 = $true },
    [ordered]@{ key = "PRIVATE_CONTEXT_LOCAL"; rel = "PRIVATE_CONTEXT_LOCAL"; skip_recursive = $false; include_policy = "OWNER_APPROVAL_REQUIRED"; needed_full = $true; needed_vm2 = $true },
    [ordered]@{ key = "RUNTIME_LOCAL"; rel = "RUNTIME_LOCAL"; skip_recursive = $false; include_policy = "EXCLUDE_BY_DEFAULT"; needed_full = $false; needed_vm2 = $false },
    [ordered]@{ key = "CHAT_COMPILATIONS_LOCAL"; rel = "CHAT_COMPILATIONS_LOCAL"; skip_recursive = $false; include_policy = "LOCAL_BUNDLE_OUTPUT"; needed_full = $true; needed_vm2 = $true },
    [ordered]@{ key = "OBSERVED/THRONE_REPO_COPY"; rel = "OBSERVED\\THRONE_REPO_COPY"; skip_recursive = $true; include_policy = "INDEX_ONLY_NEVER_SYNC"; needed_full = $false; needed_vm2 = $false },
    [ordered]@{ key = "OBSERVED/VM3_REPO_COPY"; rel = "OBSERVED\\VM3_REPO_COPY"; skip_recursive = $true; include_policy = "INDEX_ONLY"; needed_full = $false; needed_vm2 = $true }
)

$localPrivateMemory = [ordered]@{}
$ignoredPrivateRoots = @()
$notIgnoredPrivateRoots = @()
foreach ($pr in $privateRoots) {
    $full = Join-Path $Root $pr.rel
    $stats = Get-DirStats -Path $full -SkipRecursive:$pr.skip_recursive
    $ignoredCheck = Test-Ignore -Path ($pr.rel -replace '\\', '/')
    $inTracking = Test-InGitTracking -Path ($pr.rel -replace '\\', '/')

    if ($ignoredCheck.ignored) {
        $ignoredPrivateRoots += $pr.key
    } else {
        $notIgnoredPrivateRoots += $pr.key
    }

    $localPrivateMemory[$pr.key] = [ordered]@{
        exists = $stats.exists
        file_count = $stats.file_count
        total_mb = $stats.total_mb
        in_git_tracking = $inTracking
        ignored_by_git = $ignoredCheck.ignored
        include_policy = $pr.include_policy
        needed_for_full_summary = $pr.needed_full
        needed_for_vm2 = $pr.needed_vm2
        note = $stats.note
    }
}

# Public memory readiness
$requiredPublicMissing = @($requiredDocs | Where-Object { -not $requiredChecks[$_] })
$requiredTargetMissing = @($requiredForTarget | Where-Object { -not $requiredChecks[$_] })

$publicMemoryReady = (
    $readmeExists -and
    $startHereExists -and
    $lastPointExists -and
    $docsRequiredExists -and
    $headMatchesOrigin -and
    $originMatchesLsRemote -and
    ($trackedSuspicious.Count -eq 0)
)

# Context gap logic
$missingPublicContext = @($requiredPublicMissing + $requiredTargetMissing | Select-Object -Unique)
$missingLocalSafeContext = @()
$missingPrivateOwnerApproved = @()
$missingForVm2 = @()

if (-not (Test-ExistsRel -RelPath "CURRENT_STATE/LOCAL_ONLY_SOURCES_INDEX.json")) {
    $missingLocalSafeContext += "CURRENT_STATE/LOCAL_ONLY_SOURCES_INDEX.json"
}
if (-not (Test-ExistsRel -RelPath "CURRENT_STATE/EXCLUDED_LOCAL_SOURCES.md")) {
    $missingLocalSafeContext += "CURRENT_STATE/EXCLUDED_LOCAL_SOURCES.md"
}
if (-not (Test-ExistsRel -RelPath "DOCS/CHAT_COMPILATION_PROTOCOL.md")) {
    $missingLocalSafeContext += "DOCS/CHAT_COMPILATION_PROTOCOL.md"
}

if ($localPrivateMemory["PRIVATE_CONTEXT_LOCAL"].exists -and $targetMode -eq "FULL_IMPERIUM_SUMMARY") {
    $missingPrivateOwnerApproved += "Owner decision on PRIVATE_CONTEXT_LOCAL allowlist"
}

if ($targetMode -eq "VM2_WORK") {
    if (-not (Test-ExistsRel -RelPath "DOCS/VM2_BOOTSTRAP_PROTOCOL.md")) { $missingForVm2 += "DOCS/VM2_BOOTSTRAP_PROTOCOL.md" }
    if (-not $localPrivateMemory["PRIVATE_CONTEXT_LOCAL"].exists) { $missingForVm2 += "PRIVATE_CONTEXT_LOCAL" }
}

$enoughForFullSummary = ($missingPublicContext.Count -eq 0)
$enoughForVm2 = ($missingForVm2.Count -eq 0)

$needsBundle = $false
if ($targetMode -eq "FULL_IMPERIUM_SUMMARY") {
    if (-not $publicMemoryReady) { $needsBundle = $true }
    elseif ($localPrivateMemory["SSH_COMMAND_LIBRARY"].exists -or $localPrivateMemory["BUNDLES_LOCAL"].exists -or $localPrivateMemory["PRIVATE_CONTEXT_LOCAL"].exists) { $needsBundle = $true }
    elseif ($untrackedPaths.Count -gt 0) { $needsBundle = $true }
}
if ($targetMode -eq "VM2_WORK") {
    if (-not $enoughForVm2) { $needsBundle = $true }
}

$canContinueGitOnly = ($publicMemoryReady -and $missingPublicContext.Count -eq 0 -and -not $needsBundle)

# Recommendations
$includePublicPaths = @()
foreach ($p in ($requiredDocs + $requiredForTarget | Select-Object -Unique)) {
    if (Test-ExistsRel -RelPath $p) { $includePublicPaths += $p }
}

$includeArtifactPaths = @()
$artifactCandidates = @(
    "ARTIFACTS/TASK-20260510-GIT-SANITIZE-PRIVATE-SOURCES-AND-CLEAN-HISTORY-V0_1/04_RECEIPTS/FINAL_RECEIPT.json",
    "ARTIFACTS/TASK-20260510-ADMINISTRATUM-REPO-LOCAL-ENGINEERING-CLEAN-POINT-V0_1/06_RECEIPTS/FINAL_RECEIPT.json",
    "ARTIFACTS/TASK-20260510-REPO-FORMATTING-AND-IGNORE-RULES-REPAIR-V0_1/06_RECEIPTS/FINAL_RECEIPT.json",
    "ARTIFACTS/TASK-20260510-ADMINISTRATUM-GIT-LOCAL-ANALYZER-AND-CONTEXT-BUNDLE-BUTTON-V0_1/06_RECEIPTS/FINAL_RECEIPT.json"
)
foreach ($a in $artifactCandidates) {
    if (Test-ExistsRel -RelPath $a) { $includeArtifactPaths += $a }
}

$includeLocalSafeIndexes = @()
foreach ($p in @(
    "CURRENT_STATE/LOCAL_ONLY_SOURCES_INDEX.md",
    "CURRENT_STATE/LOCAL_ONLY_SOURCES_INDEX.json",
    "CURRENT_STATE/EXCLUDED_LOCAL_SOURCES.md",
    "CURRENT_STATE/ADMINISTRATUM_ANALYZER/GIT_LOCAL_ANALYSIS.json",
    "CURRENT_STATE/ADMINISTRATUM_ANALYZER/GIT_REALITY_REPORT.md",
    "CURRENT_STATE/ADMINISTRATUM_ANALYZER/CONTEXT_GAP_REPORT.md",
    "CURRENT_STATE/ADMINISTRATUM_ANALYZER/PUBLIC_PRIVATE_BOUNDARY_REPORT.md",
    "CURRENT_STATE/ADMINISTRATUM_ANALYZER/OWNER_NEXT_ACTION.md"
)) {
    if (Test-ExistsRel -RelPath $p) { $includeLocalSafeIndexes += $p }
}

$recommendedCompilation = [ordered]@{
    needed = $needsBundle
    bundle_type = if ($targetMode -eq "VM2_WORK") { "CHAT_COMPILATION_VM2_SAFE_V0_2" } else { "CHAT_COMPILATION_SAFE_V0_2" }
    output_root = "CHAT_COMPILATIONS_LOCAL"
    include_public_paths = $includePublicPaths
    include_artifact_paths = $includeArtifactPaths
    include_local_safe_indexes = $includeLocalSafeIndexes
    include_private_candidates = @(
        "SSH_COMMAND_LIBRARY inventory (filenames/sizes only)",
        "BUNDLES_LOCAL inventory (filenames/sizes only)",
        "PRIVATE_CONTEXT_LOCAL inventory (filenames/sizes only)",
        "ARCHIVE top-level inventory only"
    )
    owner_approval_required_for = @(
        "Any raw private file content",
        "Any VM2 connection/address details",
        "Any file class potentially containing secrets"
    )
    exclude_always = @(
        "raw private keys",
        ".env values",
        "tokens",
        "passwords",
        "cookies",
        "sessions",
        "full ARCHIVE",
        "full SSH_COMMAND_LIBRARY content",
        "THRONE sync material"
    )
    reasons = @(
        "Use analyzer-driven selection instead of manual guessing.",
        "Keep default output safe and secret-free.",
        "Support Owner-uploaded chat context workflow."
    )
}

$boundaryVerdict = "CLEAN"
if ($notIgnoredPrivateRoots.Count -gt 0) {
    $boundaryVerdict = "NEEDS_IGNORE_REPAIR"
}
if ($trackedSuspicious.Count -gt 0) {
    $boundaryVerdict = "SUSPICIOUS_TRACKED_PATHS"
}
if ($historySuspicious.Count -gt 0) {
    $boundaryVerdict = "SUSPICIOUS_HISTORY_PATHS"
}
if ($trackedSuspicious.Count -gt 0 -and $historySuspicious.Count -gt 0) {
    $boundaryVerdict = "MANUAL_REVIEW_REQUIRED"
}

$untrackedRecommendation = "NONE"
if ($untrackedPaths.Count -gt 0) {
    $untrackedRecommendation = "REVIEW_UNTRACKED_BEFORE_TRUSTING_GIT_ONLY"
}
if ($untrackedSuspicious.Count -gt 0) {
    $untrackedRecommendation = "REVIEW_SUSPICIOUS_UNTRACKED_PATHS"
}
if ($untrackedHeavy.Count -gt 0) {
    $untrackedRecommendation = "REVIEW_HEAVY_UNTRACKED_ARTIFACTS"
}

$recommendedOwnerAction = "MANUAL_REVIEW_REQUIRED"
$ownerActionReason = "Default fallback."
if ($gitRealityVerdict -ne "CLEAN_SYNCED") {
    $recommendedOwnerAction = "FIX_GIT_SYNC_FIRST"
    $ownerActionReason = "Git reality mismatch or local changes detected."
} elseif (-not $publicMemoryReady) {
    $recommendedOwnerAction = "FIX_PUBLIC_ENTRYPOINTS_FIRST"
    $ownerActionReason = "Required public entrypoint/docs/contract context is incomplete."
} elseif ($needsBundle -and $missingPrivateOwnerApproved.Count -gt 0) {
    $recommendedOwnerAction = "RUN_CHAT_COMPILATION_WITH_OWNER_APPROVED_PRIVATE_CONTEXT"
    $ownerActionReason = "Full target likely needs Owner-approved private local context."
} elseif ($needsBundle) {
    $recommendedOwnerAction = "RUN_CHAT_COMPILATION_SAFE"
    $ownerActionReason = "Git-only context is insufficient for requested target; safe local indexes needed."
} elseif ($canContinueGitOnly) {
    $recommendedOwnerAction = "READ_GIT_ONLY"
    $ownerActionReason = "Public memory is complete and synchronized for requested target."
}

$ownerCommand = "powershell -ExecutionPolicy Bypass -File E:\\IMPERIUM\\ORGANS\\ADMINISTRATUM\\UTILITY\\run_administratum_context_bundle_workflow.ps1 -Target $targetMode -BuildBundle"
if ($recommendedOwnerAction -eq "READ_GIT_ONLY") {
    $ownerCommand = "Read README.md -> START_HERE.md -> CURRENT_STATE/LAST_POINT_STATE.json -> DOCS/REPO_MAP.md"
}
if ($recommendedOwnerAction -eq "FIX_GIT_SYNC_FIRST") {
    $ownerCommand = "git status --short ; git fetch origin ; git rev-parse HEAD ; git rev-parse origin/master ; git ls-remote origin refs/heads/master"
}
if ($recommendedOwnerAction -eq "FIX_PUBLIC_ENTRYPOINTS_FIRST") {
    $ownerCommand = "Fix missing public entrypoint files, then rerun analyzer"
}

$expectedZipLocation = "E:\\IMPERIUM\\CHAT_COMPILATIONS_LOCAL\\FULL_IMPERIUM_CONTEXT_<timestamp>.zip"
if ($targetMode -eq "VM2_WORK") {
    $expectedZipLocation = "E:\\IMPERIUM\\CHAT_COMPILATIONS_LOCAL\\VM2_CONTEXT_<timestamp>.zip"
}

$analysis = [ordered]@{
    schema_version = "IMPERIUM_ADMINISTRATUM_GIT_LOCAL_ANALYSIS_V0_2"
    task_id = "TASK-20260510-ADMINISTRATUM-ANALYZER-POST-PUSH-REALITY-CHECK-V0_1"
    generated_at = $analysisTime
    target = $targetMode
    git_reality = [ordered]@{
        root = $Root
        remote = $remote
        branch = $branch
        local_head = $localHead
        origin_master_head = $originMasterHead
        upstream_head = $upstreamHead
        ls_remote_master_head = $lsRemoteMasterHead
        working_tree_clean = $workingTreeClean
        status_short_count = $statusShort.Count
        head_matches_origin_master = $headMatchesOrigin
        head_matches_ls_remote = $headMatchesLsRemote
        origin_matches_ls_remote = $originMatchesLsRemote
        post_push_reality_check_passed = if ($PostPushRealityCheck) { $postPushRealityPassed } else { $null }
        analyzer_report_commit = $localHead
        git_reality_verdict = $gitRealityVerdict
        warnings = @($upstreamWarning | Where-Object { $_ })
    }
    public_memory = [ordered]@{
        readme_exists = $readmeExists
        start_here_exists = $startHereExists
        current_state_exists = $currentStateExists
        last_point_state_exists = $lastPointExists
        docs_required_exists = $docsRequiredExists
        administratum_contract_exists = $administratumContractExists
        tools_analyzer_exists = $toolsAnalyzerExists
        tools_bundle_builder_exists = $toolsBuilderExists
        workflow_launcher_exists = $workflowLauncherExists
        public_memory_ready_for_chat = $publicMemoryReady
    }
    local_private_memory = $localPrivateMemory
    public_private_boundary = [ordered]@{
        suspicious_tracked_paths_count = $trackedSuspicious.Count
        suspicious_history_paths_count = $historySuspicious.Count
        suspicious_tracked_paths_file = $trackedSuspiciousFile
        suspicious_history_paths_file = $historySuspiciousFile
        ignored_private_roots = $ignoredPrivateRoots
        not_ignored_private_roots = $notIgnoredPrivateRoots
        boundary_verdict = $boundaryVerdict
    }
    untracked_state = [ordered]@{
        untracked_count = $untrackedPaths.Count
        untracked_paths_summary_file = $untrackedSummaryFile
        untracked_suspicious_count = $untrackedSuspicious.Count
        untracked_heavy_count = $untrackedHeavy.Count
        untracked_recommendation = $untrackedRecommendation
    }
    context_gap = [ordered]@{
        target = $targetMode
        missing_public_context = $missingPublicContext
        missing_local_safe_context = $missingLocalSafeContext
        missing_private_owner_approved_context = $missingPrivateOwnerApproved
        missing_for_vm2 = $missingForVm2
        enough_for_full_summary = $enoughForFullSummary
        enough_for_vm2 = $enoughForVm2
        can_continue_from_git_only = $canContinueGitOnly
    }
    recommended_compilation = $recommendedCompilation
    owner_action = [ordered]@{
        recommended_owner_action = $recommendedOwnerAction
        reason = $ownerActionReason
        command_to_run_if_bundle_needed = $ownerCommand
        expected_zip_location = $expectedZipLocation
    }
    limitations = @(
        "Analyzer is metadata/path based; no secret content extraction.",
        "Bundle safety defaults exclude raw private credentials/secrets.",
        "VM2 flow is advisory only in this task.",
        "Analyzer status remains PASS_WITH_LIMITATIONS."
    )
}

$analysisJsonPath = Join-Path $outputDir "GIT_LOCAL_ANALYSIS.json"
$recommendedPath = Join-Path $outputDir "RECOMMENDED_CHAT_COMPILATION.json"
$receiptPath = Join-Path $outputDir "ANALYZER_RECEIPT.json"
$safeInventoryPath = Join-Path $outputDir "LOCAL_ONLY_SAFE_INVENTORY.json"
$gitSummaryPath = Join-Path $outputDir "GIT_PUBLIC_MEMORY_SUMMARY.md"
$gitRealityPath = Join-Path $outputDir "GIT_REALITY_REPORT.md"
$boundaryReportPath = Join-Path $outputDir "PUBLIC_PRIVATE_BOUNDARY_REPORT.md"
$contextGapPath = Join-Path $outputDir "CONTEXT_GAP_REPORT.md"
$ownerNextActionPath = Join-Path $outputDir "OWNER_NEXT_ACTION.md"
$lastVerifiedHeadPath = Join-Path $outputDir "LAST_VERIFIED_PUBLIC_HEAD.json"

Write-JsonFile -Path $analysisJsonPath -Data $analysis
Write-JsonFile -Path $recommendedPath -Data $recommendedCompilation
Write-JsonFile -Path $safeInventoryPath -Data ([ordered]@{
    schema_version = "LOCAL_ONLY_SAFE_INVENTORY_V0_2"
    generated_at = $analysisTime
    local_private_memory = $localPrivateMemory
    ignored_private_roots = $ignoredPrivateRoots
    not_ignored_private_roots = $notIgnoredPrivateRoots
})

if (-not $JsonOnly) {
    @(
        "# GIT PUBLIC MEMORY SUMMARY",
        "",
        "- generated_at: $analysisTime",
        "- branch: $branch",
        "- local_head: $localHead",
        "- remote: $remote",
        "- docs_required_exists: $docsRequiredExists",
        "- public_memory_ready_for_chat: $publicMemoryReady"
    ) | Set-Content -LiteralPath $gitSummaryPath -Encoding UTF8

    @(
        "# GIT REALITY REPORT",
        "",
        "- local_head: $localHead",
        "- origin_master_head: $originMasterHead",
        "- ls_remote_master_head: $lsRemoteMasterHead",
        "- head_matches_origin_master: $headMatchesOrigin",
        "- head_matches_ls_remote: $headMatchesLsRemote",
        "- origin_matches_ls_remote: $originMatchesLsRemote",
        "- working_tree_clean: $workingTreeClean",
        "- status_short_count: $($statusShort.Count)",
        "- analyzer_report_commit: $localHead",
        "- git_reality_verdict: $gitRealityVerdict",
        "- post_push_reality_check_passed: $(if($PostPushRealityCheck){$postPushRealityPassed}else{'NOT_REQUESTED'})",
        "",
        "Analyzer trust condition: local/origin/ls-remote heads must match and working tree should be clean for strict public-memory trust."
    ) | Set-Content -LiteralPath $gitRealityPath -Encoding UTF8

    $boundaryLines = @(
        "# PUBLIC PRIVATE BOUNDARY REPORT",
        "",
        "## Public in Git",
        "- Source, docs, receipts, safe indexes, analyzer outputs.",
        "",
        "## Local-only roots",
        "- SSH_COMMAND_LIBRARY",
        "- ARCHIVE",
        "- BUNDLES_LOCAL",
        "- PRIVATE_CONTEXT_LOCAL",
        "- RUNTIME_LOCAL",
        "- CHAT_COMPILATIONS_LOCAL",
        "",
        "## Ignore state",
        "- ignored_private_roots: $($ignoredPrivateRoots -join ', ')",
        "- not_ignored_private_roots: $($notIgnoredPrivateRoots -join ', ')",
        "",
        "## Suspicious scans",
        "- suspicious_tracked_paths_count: $($trackedSuspicious.Count)",
        "- suspicious_history_paths_count: $($historySuspicious.Count)",
        "- boundary_verdict: $boundaryVerdict",
        "",
        "## Never commit",
        "- raw keys/tokens/passwords/.env values/private command bodies",
        "- full ARCHIVE and full SSH_COMMAND_LIBRARY content"
    )
    $boundaryLines | Set-Content -LiteralPath $boundaryReportPath -Encoding UTF8

    $contextLines = @(
        "# CONTEXT GAP REPORT",
        "",
        "- target: $targetMode",
        "- enough_for_full_summary: $enoughForFullSummary",
        "- enough_for_vm2: $enoughForVm2",
        "- can_continue_from_git_only: $canContinueGitOnly",
        "- needs_chat_compilation_bundle: $needsBundle",
        "",
        "## Missing Public Context"
    )
    if ($missingPublicContext.Count -eq 0) {
        $contextLines += "- none"
    } else {
        foreach ($m in $missingPublicContext) { $contextLines += "- $m" }
    }
    $contextLines += ""
    $contextLines += "## Missing Local Safe Context"
    if ($missingLocalSafeContext.Count -eq 0) {
        $contextLines += "- none"
    } else {
        foreach ($m in $missingLocalSafeContext) { $contextLines += "- $m" }
    }
    $contextLines += ""
    $contextLines += "## Missing Private Owner-Approved Context"
    if ($missingPrivateOwnerApproved.Count -eq 0) {
        $contextLines += "- none"
    } else {
        foreach ($m in $missingPrivateOwnerApproved) { $contextLines += "- $m" }
    }
    if ($targetMode -eq "VM2_WORK") {
        $contextLines += ""
        $contextLines += "## Missing For VM2"
        if ($missingForVm2.Count -eq 0) { $contextLines += "- none" } else { foreach ($m in $missingForVm2) { $contextLines += "- $m" } }
    }
    $contextLines += ""
    $contextLines += "## Recommendation"
    $contextLines += "- $recommendedOwnerAction"
    $contextLines | Set-Content -LiteralPath $contextGapPath -Encoding UTF8

    @(
        "# OWNER NEXT ACTION",
        "",
        "- recommended_owner_action: $recommendedOwnerAction",
        "- reason: $ownerActionReason",
        "- command: $ownerCommand",
        "- expected_zip_location: $expectedZipLocation"
    ) | Set-Content -LiteralPath $ownerNextActionPath -Encoding UTF8
}

$commitUrlGuess = "https://github.com/SoulsLike2313/Imperium-/commit/$localHead"
$lastVerified = [ordered]@{
    local_head = $localHead
    origin_master_head = $originMasterHead
    ls_remote_master_head = $lsRemoteMasterHead
    verified_at = $analysisTime
    verified_result = if ($postPushRealityPassed) { "MATCHED" } else { "MISMATCH_OR_STALE" }
    commit_url_guess = $commitUrlGuess
    can_use_github_as_public_memory = ($publicMemoryReady -and $postPushRealityPassed)
}
Write-JsonFile -Path $lastVerifiedHeadPath -Data $lastVerified

$receipt = [ordered]@{
    schema_version = "ADMINISTRATUM_ANALYZER_RECEIPT_V0_2"
    generated_at = $analysisTime
    root = $Root
    target = $targetMode
    analyzer_report_commit = $localHead
    git_reality_verdict = $gitRealityVerdict
    public_memory_ready_for_chat = $publicMemoryReady
    can_continue_from_git_only = $canContinueGitOnly
    needs_chat_compilation_bundle = $needsBundle
    recommended_owner_action = $recommendedOwnerAction
    suspicious_tracked_paths_count = $trackedSuspicious.Count
    suspicious_history_paths_count = $historySuspicious.Count
    raw_secrets_copied = $false
    outputs = @(
        $analysisJsonPath,
        $recommendedPath,
        $safeInventoryPath,
        $gitSummaryPath,
        $gitRealityPath,
        $boundaryReportPath,
        $contextGapPath,
        $ownerNextActionPath,
        $lastVerifiedHeadPath
    )
    status = "PASS_WITH_LIMITATIONS"
}
Write-JsonFile -Path $receiptPath -Data $receipt

Write-Output $analysisJsonPath
