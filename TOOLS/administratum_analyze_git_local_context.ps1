param(
    [string]$Root = "E:\IMPERIUM",
    [string]$Remote = "https://github.com/SoulsLike2313/Imperium-.git",
    [string]$Target = "FULL_IMPERIUM_SUMMARY",
    [switch]$ForVM2,
    [switch]$JsonOnly,
    [switch]$PostPushRealityCheck,
    [string]$RuntimeOutputDir = ""
)

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $Root

$outputDir = if ([string]::IsNullOrWhiteSpace($RuntimeOutputDir)) {
    Join-Path $Root ".imperium_runtime\administratum_analyzer\latest"
} else {
    $RuntimeOutputDir
}
$legacyOutputDir = Join-Path $Root "CURRENT_STATE\ADMINISTRATUM_ANALYZER"
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

function Write-JsonFile {
    param([string]$Path, $Data)
    $Data | ConvertTo-Json -Depth 40 | Set-Content -LiteralPath $Path -Encoding UTF8
}

function Normalize-PathRel {
    param([string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path)) { return "" }
    return ($Path -replace "\\", "/").Trim()
}

function Test-ExistsRel {
    param([string]$RelPath)
    $full = Join-Path $Root ($RelPath -replace "/", "\")
    return (Test-Path -LiteralPath $full)
}

function Test-InGitTracking {
    param([string]$RelPath)
    $norm = Normalize-PathRel $RelPath
    $items = @(git ls-files -- "$norm" 2>$null)
    return ($items.Count -gt 0)
}

function Test-IgnoreRule {
    param([string]$RelPath)
    $norm = Normalize-PathRel $RelPath
    $out = git check-ignore -v -- $norm 2>$null
    return [ordered]@{
        path = $norm
        ignored = ($LASTEXITCODE -eq 0)
        detail = if ($LASTEXITCODE -eq 0) { $out } else { "NOT_IGNORED" }
    }
}

function Get-DirStats {
    param([string]$Path, [bool]$SkipRecursive = $false)
    if (-not (Test-Path -LiteralPath $Path)) {
        return [ordered]@{ exists = $false; file_count = 0; total_mb = 0; note = "NOT_FOUND" }
    }
    if ($SkipRecursive) {
        $top = Get-ChildItem -LiteralPath $Path -File -ErrorAction SilentlyContinue
        $bytes = 0
        if ($top) { $bytes = ($top | Measure-Object -Property Length -Sum).Sum }
        return [ordered]@{
            exists = $true
            file_count = [int]$top.Count
            total_mb = [math]::Round(($bytes / 1MB), 3)
            note = "TOP_LEVEL_ONLY"
        }
    }
    $files = Get-ChildItem -LiteralPath $Path -Recurse -File -ErrorAction SilentlyContinue
    $bytes = 0
    if ($files) { $bytes = ($files | Measure-Object -Property Length -Sum).Sum }
    return [ordered]@{
        exists = $true
        file_count = [int]$files.Count
        total_mb = [math]::Round(($bytes / 1MB), 3)
        note = "RECURSIVE_FILE_COUNT"
    }
}

function Starts-WithAny {
    param([string]$Path, [string[]]$Prefixes)
    foreach ($p in $Prefixes) {
        if ($Path -eq $p -or $Path.StartsWith($p + "/")) { return $true }
    }
    return $false
}

function Parse-StatusLine {
    param([string]$Line)
    if ([string]::IsNullOrWhiteSpace($Line) -or $Line.Length -lt 3) { return $null }
    $code = $Line.Substring(0, 2)
    $raw = $Line.Substring(3).Trim()
    $path = $raw
    if ($raw -match " -> ") {
        $path = ($raw -split " -> ")[-1].Trim()
    }
    return [ordered]@{
        git_status_code = $code
        path = (Normalize-PathRel $path)
    }
}

$analysisTime = (Get-Date).ToString("o")
$targetMode = if ($ForVM2 -or $Target -eq "VM2_WORK") { "VM2_WORK" } else { "FULL_IMPERIUM_SUMMARY" }

# Git reality
$branch = (git branch --show-current).Trim()
$localHead = (git rev-parse HEAD 2>$null).Trim()
$originMasterHead = (git rev-parse origin/master 2>$null).Trim()
$u = (git rev-parse '@{u}' 2>$null)
$upstreamHead = $null
$upstreamWarning = $null
if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($u)) { $upstreamHead = $u.Trim() } else { $upstreamWarning = "NO_UPSTREAM_CONFIGURED" }
$lsRaw = (git ls-remote origin refs/heads/master 2>$null)
$lsRemoteMasterHead = $null
if (-not [string]::IsNullOrWhiteSpace($lsRaw)) { $lsRemoteMasterHead = ($lsRaw -split "\s+")[0].Trim() }

$statusShort = @(git status --short)
$statusShortCount = $statusShort.Count
$workingTreeClean = ($statusShortCount -eq 0)
$headMatchesOrigin = ($localHead -and $originMasterHead -and ($localHead -eq $originMasterHead))
$headMatchesLsRemote = ($localHead -and $lsRemoteMasterHead -and ($localHead -eq $lsRemoteMasterHead))
$originMatchesLsRemote = ($originMasterHead -and $lsRemoteMasterHead -and ($originMasterHead -eq $lsRemoteMasterHead))
$headsAllMatch = ($headMatchesOrigin -and $headMatchesLsRemote -and $originMatchesLsRemote)
$postPushRealityPassed = $headsAllMatch

$gitRealityVerdict = "UNKNOWN"
if (-not $headMatchesOrigin -or -not $headMatchesLsRemote) { $gitRealityVerdict = "LOCAL_HEAD_NOT_PUSHED" }
elseif (-not $originMatchesLsRemote) { $gitRealityVerdict = "ORIGIN_NOT_FETCHED_OR_STALE" }
elseif ($headsAllMatch -and -not $workingTreeClean) { $gitRealityVerdict = "LOCAL_CHANGES_PRESENT" }
elseif ($headsAllMatch -and $workingTreeClean) { $gitRealityVerdict = "CLEAN_SYNCED" }

# Required public memory files
$requiredPublicPaths = @(
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
$presence = @{}
foreach ($p in $requiredPublicPaths) { $presence[$p] = (Test-ExistsRel -RelPath $p) }
$missingPublicContext = @($requiredPublicPaths | Where-Object { -not $presence[$_] })

$readmeExists = $presence["README.md"]
$startHereExists = $presence["START_HERE.md"]
$currentStateExists = (Test-Path -LiteralPath (Join-Path $Root "CURRENT_STATE"))
$lastPointExists = $presence["CURRENT_STATE/LAST_POINT_STATE.json"]
$docsRequiredList = @(
    "DOCS/REPO_MAP.md",
    "DOCS/COMMANDS.md",
    "DOCS/BUNDLE_SYSTEM.md",
    "DOCS/CHAT_ENTRY_PROTOCOL.md",
    "DOCS/PUBLIC_PRIVATE_BOUNDARY.md",
    "DOCS/ADMINISTRATUM_OPERATIONAL_AUTHORITY.md"
)
$docsRequiredExists = (@($docsRequiredList | Where-Object { -not $presence[$_] }).Count -eq 0)
$administratumContractExists = $presence["ORGANS/ADMINISTRATUM/ORGAN_CONTRACT.json"]
$toolsAnalyzerExists = Test-ExistsRel -RelPath "TOOLS/administratum_analyze_git_local_context.ps1"
$toolsBundleBuilderExists = Test-ExistsRel -RelPath "TOOLS/build_chat_compilation_from_analysis.ps1"
$workflowLauncherExists = Test-ExistsRel -RelPath "ORGANS/ADMINISTRATUM/UTILITY/run_administratum_context_bundle_workflow.ps1"

# Boundary scans
$trackedFiles = @(git ls-files)
$historyPaths = @(git log --all --name-only --pretty=format: | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
$trackedRegex = "(^|/)SSH_COMMAND_LIBRARY(/|$)|(^|/)ARCHIVE(/|$)|(^|/)BUNDLES_LOCAL(/|$)|(^|/)PRIVATE_CONTEXT_LOCAL(/|$)|(^|/)RUNTIME_LOCAL(/|$)|(^|/)CHAT_COMPILATIONS_LOCAL(/|$)|(^|/)(id_rsa(\..*)?|id_ed25519(\..*)?|known_hosts|authorized_keys)$|\.pem$|\.ppk$|\.key$|(^|/)\.env(\.|$)"
$historyRegex = "(^|/)SSH_COMMAND_LIBRARY(/|$)|(^|/)(id_rsa(\..*)?|id_ed25519(\..*)?|known_hosts|authorized_keys)$|\.pem$|\.ppk$|\.key$|(^|/)\.env(\.|$)"
$trackedSuspicious = @($trackedFiles | Where-Object { $_ -match $trackedRegex })
$historySuspicious = @($historyPaths | Where-Object { $_ -match $historyRegex })

$trackedSuspiciousFile = Join-Path $outputDir "TRACKED_SUSPICIOUS_PATHS_V0_2.txt"
$historySuspiciousFile = Join-Path $outputDir "HISTORY_SUSPICIOUS_PATHS_V0_2.txt"
if ($trackedSuspicious.Count -eq 0) { "NO_MATCHES" | Set-Content -LiteralPath $trackedSuspiciousFile -Encoding UTF8 } else { $trackedSuspicious | Set-Content -LiteralPath $trackedSuspiciousFile -Encoding UTF8 }
if ($historySuspicious.Count -eq 0) { "NO_MATCHES" | Set-Content -LiteralPath $historySuspiciousFile -Encoding UTF8 } else { $historySuspicious | Set-Content -LiteralPath $historySuspiciousFile -Encoding UTF8 }

# Local private memory
$privateDefs = @(
    [ordered]@{ key = "SSH_COMMAND_LIBRARY"; rel = "SSH_COMMAND_LIBRARY"; skip = $false; include = "SAFE_INDEX_ONLY"; full = $true; vm2 = $true },
    [ordered]@{ key = "ARCHIVE"; rel = "ARCHIVE"; skip = $true; include = "TOP_LEVEL_INVENTORY_ONLY"; full = $false; vm2 = $false },
    [ordered]@{ key = "BUNDLES_LOCAL"; rel = "BUNDLES_LOCAL"; skip = $false; include = "SAFE_INDEX_ONLY"; full = $true; vm2 = $true },
    [ordered]@{ key = "PRIVATE_CONTEXT_LOCAL"; rel = "PRIVATE_CONTEXT_LOCAL"; skip = $false; include = "OWNER_APPROVAL_REQUIRED"; full = $true; vm2 = $true },
    [ordered]@{ key = "RUNTIME_LOCAL"; rel = "RUNTIME_LOCAL"; skip = $false; include = "EXCLUDE_BY_DEFAULT"; full = $false; vm2 = $false },
    [ordered]@{ key = "CHAT_COMPILATIONS_LOCAL"; rel = "CHAT_COMPILATIONS_LOCAL"; skip = $false; include = "LOCAL_BUNDLE_OUTPUT"; full = $true; vm2 = $true },
    [ordered]@{ key = "OBSERVED/THRONE_REPO_COPY"; rel = "OBSERVED\THRONE_REPO_COPY"; skip = $true; include = "INDEX_ONLY_NEVER_SYNC"; full = $false; vm2 = $false },
    [ordered]@{ key = "OBSERVED/VM3_REPO_COPY"; rel = "OBSERVED\VM3_REPO_COPY"; skip = $true; include = "INDEX_ONLY"; full = $false; vm2 = $true }
)

$localPrivateMemory = [ordered]@{}
$ignoredPrivateRoots = @()
$notIgnoredPrivateRoots = @()
foreach ($d in $privateDefs) {
    $full = Join-Path $Root $d.rel
    $stats = Get-DirStats -Path $full -SkipRecursive:$d.skip
    $inTracking = Test-InGitTracking -RelPath ($d.rel -replace "\\", "/")
    $ign = Test-IgnoreRule -RelPath ($d.rel -replace "\\", "/")
    if ($ign.ignored) { $ignoredPrivateRoots += $d.key } else { $notIgnoredPrivateRoots += $d.key }
    $localPrivateMemory[$d.key] = [ordered]@{
        exists = $stats.exists
        file_count = $stats.file_count
        total_mb = $stats.total_mb
        in_git_tracking = $inTracking
        ignored_by_git = $ign.ignored
        include_policy = $d.include
        needed_for_full_summary = $d.full
        needed_for_vm2 = $d.vm2
    }
}

# Worktree classifier
$publicRoots = @("DOCS", "CURRENT_STATE", "TOOLS", "ORGANS", "ARTIFACTS", "EXPLORER", "SANCTUM", "PC_ENGINEERING_ROOM")
$localOnlyRoots = @("SSH_COMMAND_LIBRARY", "ARCHIVE", "BUNDLES_LOCAL", "PRIVATE_CONTEXT_LOCAL", "RUNTIME_LOCAL", "CHAT_COMPILATIONS_LOCAL", "OBSERVED/THRONE_REPO_COPY", "OBSERVED/VM3_REPO_COPY", "ORGANS/ADMINISTRATUM/UTILITY/_BACKUPS")
$suspNameRegex = "ssh_command_library|id_rsa|id_ed25519|\.pem|\.ppk|\.key|\.env|token|secret|password|credential|cookie|session|known_hosts|authorized_keys"

$statusEntries = @()
foreach ($line in $statusShort) {
    $parsed = Parse-StatusLine -Line $line
    if (-not $parsed) { continue }
    $code = $parsed.git_status_code
    $path = $parsed.path
    $lower = $path.ToLowerInvariant()

    $category = "PRIVATE_RISK_CANDIDATE"
    $reason = "Default conservative classification"

    $isSuspicious = ($lower -match $suspNameRegex)
    $isLocalOnly = Starts-WithAny -Path $path -Prefixes $localOnlyRoots
    $isGenerated = (
        (Starts-WithAny -Path $path -Prefixes @("ARTIFACTS", "CURRENT_STATE/ADMINISTRATUM_ANALYZER", "CURRENT_STATE/ADMINISTRATUM_WORKTREE_CLASSIFIER")) -and
        ($lower -match "receipt|manifest|hash|report|validation|analysis|index|summary|check")
    )
    $isPublic = ($path -eq "README.md" -or $path -eq "START_HERE.md" -or (Starts-WithAny -Path $path -Prefixes $publicRoots))
    $isArchivePack = ($lower -match "\.zip$|\.tar\.gz$")
    $isScreenshotPrivate = ($lower -match "screenshot" -and $lower -match "ssh_command_library|private_context|token|secret")
    $isContour = ($lower -match "contour|address|private_command")
    $sizeRisk = $false
    $fullPath = Join-Path $Root ($path -replace "/", "\")
    if (Test-Path -LiteralPath $fullPath -PathType Leaf) {
        try {
            $fi = Get-Item -LiteralPath $fullPath
            if ($fi.Length -ge 20MB -and -not (Starts-WithAny -Path $path -Prefixes @("ARTIFACTS"))) { $sizeRisk = $true }
        } catch { }
    }

    if ($isSuspicious) {
        $category = "SUSPICIOUS_MANUAL_REVIEW"
        $reason = "Path contains sensitive keyword pattern"
    } elseif ($isLocalOnly) {
        $category = "LOCAL_ONLY_IGNORE_CANDIDATE"
        $reason = "Path belongs to local-only root"
    } elseif ($isArchivePack -or $isScreenshotPrivate -or $isContour -or $sizeRisk) {
        $category = "PRIVATE_RISK_CANDIDATE"
        $reason = "Potential private-risk artifact or oversized local file"
    } elseif ($isGenerated) {
        $category = "GENERATED_ARTIFACT_CANDIDATE"
        $reason = "Generated analyzer/artifact state output"
    } elseif ($code -eq "??" -and $isPublic) {
        $category = "SAFE_UNTRACKED_CANDIDATE"
        $reason = "Safe untracked public path"
    } elseif ($isPublic) {
        $category = "PUBLIC_COMMIT_CANDIDATE"
        $reason = "Public source/docs/state path"
    }

    $rec = "NO_ACTION"
    $mayCommit = "manual_review"
    $mayBundle = "manual_review"
    switch ($category) {
        "PUBLIC_COMMIT_CANDIDATE" {
            $rec = "COMMIT_PUBLIC_CHANGES"; $mayCommit = $true; $mayBundle = $true
        }
        "GENERATED_ARTIFACT_CANDIDATE" {
            $rec = "COMMIT_PUBLIC_CHANGES"; $mayCommit = $true; $mayBundle = $true
        }
        "LOCAL_ONLY_IGNORE_CANDIDATE" {
            $rec = "KEEP_LOCAL_ONLY"; $mayCommit = $false; $mayBundle = "manual_review"
        }
        "SAFE_UNTRACKED_CANDIDATE" {
            $rec = "COMMIT_PUBLIC_CHANGES"; $mayCommit = $true; $mayBundle = $true
        }
        "SUSPICIOUS_MANUAL_REVIEW" {
            $rec = "MANUAL_REVIEW_REQUIRED"; $mayCommit = "manual_review"; $mayBundle = "manual_review"
        }
        "PRIVATE_RISK_CANDIDATE" {
            $rec = "MANUAL_REVIEW_REQUIRED"; $mayCommit = "manual_review"; $mayBundle = "manual_review"
        }
    }

    $statusEntries += [ordered]@{
        git_status_code = $code
        path = $path
        category = $category
        reason = $reason
        recommended_action = $rec
        may_commit_to_git = $mayCommit
        may_include_in_chat_bundle = $mayBundle
    }
}

$modifiedCount = @($statusEntries | Where-Object { $_.git_status_code -ne "??" -and $_.git_status_code -notmatch "D" -and $_.git_status_code -notmatch "R" }).Count
$untrackedCount = @($statusEntries | Where-Object { $_.git_status_code -eq "??" }).Count
$deletedCount = @($statusEntries | Where-Object { $_.git_status_code -match "D" }).Count
$renamedCount = @($statusEntries | Where-Object { $_.git_status_code -match "R" }).Count

$publicCommitCandidates = @($statusEntries | Where-Object { $_.category -eq "PUBLIC_COMMIT_CANDIDATE" } | ForEach-Object { $_.path })
$localOnlyIgnoreCandidates = @($statusEntries | Where-Object { $_.category -eq "LOCAL_ONLY_IGNORE_CANDIDATE" } | ForEach-Object { $_.path })
$generatedArtifactCandidates = @($statusEntries | Where-Object { $_.category -eq "GENERATED_ARTIFACT_CANDIDATE" } | ForEach-Object { $_.path })
$safeUntrackedCandidates = @($statusEntries | Where-Object { $_.category -eq "SAFE_UNTRACKED_CANDIDATE" } | ForEach-Object { $_.path })
$suspiciousManualReviewCandidates = @($statusEntries | Where-Object { $_.category -eq "SUSPICIOUS_MANUAL_REVIEW" } | ForEach-Object { $_.path })
$privateRiskCandidates = @($statusEntries | Where-Object { $_.category -eq "PRIVATE_RISK_CANDIDATE" } | ForEach-Object { $_.path })

$allCategories = @($statusEntries | ForEach-Object { $_.category } | Select-Object -Unique)
$allDirtyArePublic = ($statusEntries.Count -gt 0 -and @($allCategories | Where-Object { $_ -ne "PUBLIC_COMMIT_CANDIDATE" }).Count -eq 0)
$allDirtyAreLocalOnly = ($statusEntries.Count -gt 0 -and @($allCategories | Where-Object { $_ -ne "LOCAL_ONLY_IGNORE_CANDIDATE" }).Count -eq 0)

$worktreeVerdict = "WORKTREE_CLEAN"
if ($statusEntries.Count -gt 0) { $worktreeVerdict = "WORKTREE_DIRTY" }
if ($suspiciousManualReviewCandidates.Count -gt 0 -or $privateRiskCandidates.Count -gt 0) { $worktreeVerdict = "WORKTREE_REVIEW_REQUIRED" }

$recommendedWorktreeAction = "NO_ACTION"
if ($statusEntries.Count -eq 0) { $recommendedWorktreeAction = "NO_ACTION" }
elseif ($suspiciousManualReviewCandidates.Count -gt 0 -or $privateRiskCandidates.Count -gt 0) { $recommendedWorktreeAction = "MANUAL_REVIEW_REQUIRED" }
elseif ($allDirtyArePublic) { $recommendedWorktreeAction = "COMMIT_PUBLIC_CHANGES" }
elseif ($allDirtyAreLocalOnly) { $recommendedWorktreeAction = "UPDATE_IGNORE_OR_KEEP_LOCAL_ONLY" }
elseif ($generatedArtifactCandidates.Count -gt 0) { $recommendedWorktreeAction = "COMMIT_ANALYZER_ARTIFACTS_OR_IGNORE_GENERATED" }
else { $recommendedWorktreeAction = "MANUAL_REVIEW_REQUIRED" }

$worktreeClassifier = [ordered]@{
    status_short_count = $statusShortCount
    modified_count = $modifiedCount
    untracked_count = $untrackedCount
    deleted_count = $deletedCount
    renamed_count = $renamedCount
    classified_changes = $statusEntries
    public_commit_candidates = $publicCommitCandidates
    local_only_ignore_candidates = $localOnlyIgnoreCandidates
    generated_artifact_candidates = $generatedArtifactCandidates
    safe_untracked_candidates = $safeUntrackedCandidates
    suspicious_manual_review_candidates = $suspiciousManualReviewCandidates
    private_risk_candidates = $privateRiskCandidates
    recommended_worktree_action = $recommendedWorktreeAction
    worktree_verdict = $worktreeVerdict
}

$untrackedSummaryPath = Join-Path $outputDir "UNTRACKED_PATHS_SUMMARY_V0_2.txt"
if ($statusEntries.Count -eq 0) { "NO_UNTRACKED" | Set-Content -LiteralPath $untrackedSummaryPath -Encoding UTF8 }
else { ($statusEntries | ForEach-Object { "$($_.git_status_code) $($_.path) [$($_.category)]" }) | Set-Content -LiteralPath $untrackedSummaryPath -Encoding UTF8 }

$boundaryVerdict = "CLEAN"
if ($notIgnoredPrivateRoots.Count -gt 0) { $boundaryVerdict = "NEEDS_IGNORE_REPAIR" }
if ($trackedSuspicious.Count -gt 0) { $boundaryVerdict = "SUSPICIOUS_TRACKED_PATHS" }
if ($historySuspicious.Count -gt 0) { $boundaryVerdict = "SUSPICIOUS_HISTORY_PATHS" }
if ($trackedSuspicious.Count -gt 0 -and $historySuspicious.Count -gt 0) { $boundaryVerdict = "MANUAL_REVIEW_REQUIRED" }

$publicMemoryReadyForChat = (
    $readmeExists -and
    $startHereExists -and
    $lastPointExists -and
    $docsRequiredExists -and
    $headMatchesOrigin -and
    $originMatchesLsRemote -and
    ($trackedSuspicious.Count -eq 0)
)

$missingLocalSafeContext = @()
if (-not (Test-ExistsRel -RelPath "CURRENT_STATE/LOCAL_ONLY_SOURCES_INDEX.json")) { $missingLocalSafeContext += "CURRENT_STATE/LOCAL_ONLY_SOURCES_INDEX.json" }
if (-not (Test-ExistsRel -RelPath "CURRENT_STATE/EXCLUDED_LOCAL_SOURCES.md")) { $missingLocalSafeContext += "CURRENT_STATE/EXCLUDED_LOCAL_SOURCES.md" }
if (-not (Test-ExistsRel -RelPath "DOCS/CHAT_COMPILATION_PROTOCOL.md")) { $missingLocalSafeContext += "DOCS/CHAT_COMPILATION_PROTOCOL.md" }

$missingPrivateOwnerApprovedContext = @()
if ($localPrivateMemory["PRIVATE_CONTEXT_LOCAL"].exists) { $missingPrivateOwnerApprovedContext += "Owner-approved PRIVATE_CONTEXT_LOCAL allowlist decision" }

$missingForVm2 = @()
if ($targetMode -eq "VM2_WORK") {
    if (-not (Test-ExistsRel -RelPath "DOCS/VM2_BOOTSTRAP_PROTOCOL.md")) { $missingForVm2 += "DOCS/VM2_BOOTSTRAP_PROTOCOL.md" }
    if (-not $localPrivateMemory["PRIVATE_CONTEXT_LOCAL"].exists) { $missingForVm2 += "PRIVATE_CONTEXT_LOCAL" }
}

$targetRequiresLocalPrivateData = $false
if ($targetMode -eq "FULL_IMPERIUM_SUMMARY") {
    $targetRequiresLocalPrivateData = (
        $localPrivateMemory["SSH_COMMAND_LIBRARY"].exists -or
        $localPrivateMemory["BUNDLES_LOCAL"].exists -or
        $localPrivateMemory["PRIVATE_CONTEXT_LOCAL"].exists
    )
} elseif ($targetMode -eq "VM2_WORK") {
    $targetRequiresLocalPrivateData = $true
}

$missingForTarget = @($missingPublicContext)
if ($targetMode -eq "VM2_WORK") { $missingForTarget += $missingForVm2 }

$canContinueFromGitOnly = ($publicMemoryReadyForChat -and $missingForTarget.Count -eq 0 -and -not $targetRequiresLocalPrivateData)
$needsBundle = (-not $canContinueFromGitOnly) -and ($targetRequiresLocalPrivateData -or $missingLocalSafeContext.Count -gt 0 -or $targetMode -eq "VM2_WORK")

$recommendedOwnerAction = "MANUAL_REVIEW_REQUIRED"
$ownerActionReason = "Conservative default"
if (-not $headsAllMatch) {
    $recommendedOwnerAction = "FIX_GIT_SYNC_FIRST"
    $ownerActionReason = "Local/origin/ls-remote HEAD mismatch detected."
} elseif ($headsAllMatch -and -not $workingTreeClean -and $allDirtyArePublic) {
    $recommendedOwnerAction = "COMMIT_PUBLIC_CHANGES"
    $ownerActionReason = "Heads match; dirty worktree contains only public commit candidates."
} elseif ($headsAllMatch -and -not $workingTreeClean -and $allDirtyAreLocalOnly) {
    $recommendedOwnerAction = "UPDATE_IGNORE_OR_KEEP_LOCAL_ONLY"
    $ownerActionReason = "Heads match; dirty worktree contains only local-only ignore candidates."
} elseif ($headsAllMatch -and -not $workingTreeClean -and $generatedArtifactCandidates.Count -gt 0 -and $suspiciousManualReviewCandidates.Count -eq 0 -and $privateRiskCandidates.Count -eq 0) {
    $recommendedOwnerAction = "COMMIT_ANALYZER_ARTIFACTS_OR_IGNORE_GENERATED"
    $ownerActionReason = "Heads match; generated artifact candidates present."
} elseif ($headsAllMatch -and ($suspiciousManualReviewCandidates.Count -gt 0 -or $privateRiskCandidates.Count -gt 0)) {
    $recommendedOwnerAction = "MANUAL_REVIEW_REQUIRED"
    $ownerActionReason = "Suspicious/manual/private-risk candidates detected."
} elseif ($headsAllMatch -and $workingTreeClean -and $publicMemoryReadyForChat -and $missingLocalSafeContext.Count -eq 0 -and -not $targetRequiresLocalPrivateData) {
    $recommendedOwnerAction = "READ_GIT_ONLY"
    $ownerActionReason = "Heads match, worktree clean, and public memory is sufficient."
} elseif ($headsAllMatch -and $publicMemoryReadyForChat -and $targetMode -eq "VM2_WORK" -and $missingPrivateOwnerApprovedContext.Count -gt 0) {
    $recommendedOwnerAction = "RUN_CHAT_COMPILATION_WITH_OWNER_APPROVED_PRIVATE_CONTEXT"
    $ownerActionReason = "VM2 target requires Owner-approved private context."
} elseif ($headsAllMatch -and $publicMemoryReadyForChat -and $targetRequiresLocalPrivateData) {
    $recommendedOwnerAction = "RUN_CHAT_COMPILATION_SAFE"
    $ownerActionReason = "Public memory is ready but target requires local/private context."
} elseif (-not $publicMemoryReadyForChat) {
    $recommendedOwnerAction = "FIX_PUBLIC_ENTRYPOINTS_FIRST"
    $ownerActionReason = "Public entrypoint set is incomplete."
}

$ownerCommand = "Manual review required"
switch ($recommendedOwnerAction) {
    "READ_GIT_ONLY" { $ownerCommand = "Read README.md -> START_HERE.md -> CURRENT_STATE/LAST_POINT_STATE.json -> DOCS/REPO_MAP.md" }
    "RUN_CHAT_COMPILATION_SAFE" { $ownerCommand = "powershell -ExecutionPolicy Bypass -File E:\\IMPERIUM\\ORGANS\\ADMINISTRATUM\\UTILITY\\run_administratum_context_bundle_workflow.ps1 -Target $targetMode -BuildBundle" }
    "RUN_CHAT_COMPILATION_WITH_OWNER_APPROVED_PRIVATE_CONTEXT" { $ownerCommand = "powershell -ExecutionPolicy Bypass -File E:\\IMPERIUM\\ORGANS\\ADMINISTRATUM\\UTILITY\\run_administratum_context_bundle_workflow.ps1 -Target $targetMode -BuildBundle -IncludePrivateApproved" }
    "COMMIT_PUBLIC_CHANGES" { $ownerCommand = "git add <safe_public_paths> ; git commit -m 'commit public safe changes' ; git push origin master" }
    "UPDATE_IGNORE_OR_KEEP_LOCAL_ONLY" { $ownerCommand = "Review .gitignore local-only roots and keep local-only files out of tracking" }
    "COMMIT_ANALYZER_ARTIFACTS_OR_IGNORE_GENERATED" { $ownerCommand = "Commit analyzer artifacts or ignore purely local generated outputs" }
    "FIX_GIT_SYNC_FIRST" { $ownerCommand = "git fetch origin ; git rev-parse HEAD ; git rev-parse origin/master ; git ls-remote origin refs/heads/master" }
}

$expectedZipLocation = if ($targetMode -eq "VM2_WORK") { "E:\\IMPERIUM\\.imperium_runtime\\bundles\\VM2_CONTEXT_<timestamp>.zip" } else { "E:\\IMPERIUM\\.imperium_runtime\\bundles\\FULL_IMPERIUM_CONTEXT_<timestamp>.zip" }

$recommendedCompilation = [ordered]@{
    needed = $needsBundle
    bundle_type = if ($targetMode -eq "VM2_WORK") { "CHAT_COMPILATION_VM2_SAFE_V0_2" } else { "CHAT_COMPILATION_SAFE_V0_2" }
    output_root = ".imperium_runtime/bundles"
    include_public_paths = @($requiredPublicPaths | Where-Object { Test-ExistsRel -RelPath $_ })
    include_artifact_paths = @(
        "ARTIFACTS/TASK-20260510-GIT-SANITIZE-PRIVATE-SOURCES-AND-CLEAN-HISTORY-V0_1/04_RECEIPTS/FINAL_RECEIPT.json",
        "ARTIFACTS/TASK-20260510-ADMINISTRATUM-REPO-LOCAL-ENGINEERING-CLEAN-POINT-V0_1/06_RECEIPTS/FINAL_RECEIPT.json",
        "ARTIFACTS/TASK-20260510-REPO-FORMATTING-AND-IGNORE-RULES-REPAIR-V0_1/06_RECEIPTS/FINAL_RECEIPT.json",
        "ARTIFACTS/TASK-20260510-ADMINISTRATUM-GIT-LOCAL-ANALYZER-AND-CONTEXT-BUNDLE-BUTTON-V0_1/06_RECEIPTS/FINAL_RECEIPT.json"
    )
    include_local_safe_indexes = @(
        "CURRENT_STATE/LOCAL_ONLY_SOURCES_INDEX.md",
        "CURRENT_STATE/LOCAL_ONLY_SOURCES_INDEX.json",
        "CURRENT_STATE/EXCLUDED_LOCAL_SOURCES.md",
        ".imperium_runtime/administratum_analyzer/latest/GIT_LOCAL_ANALYSIS.json",
        ".imperium_runtime/administratum_analyzer/latest/WORKTREE_CLASSIFICATION_REPORT.md",
        ".imperium_runtime/administratum_analyzer/latest/OWNER_NEXT_ACTION.md"
    )
    include_private_candidates = @(
        "SSH_COMMAND_LIBRARY inventory (filenames/sizes only)",
        "BUNDLES_LOCAL inventory (filenames/sizes only)",
        "PRIVATE_CONTEXT_LOCAL inventory (filenames/sizes only)",
        "ARCHIVE top-level inventory only"
    )
    owner_approval_required_for = @(
        "Any raw private file content",
        "VM2 connection/address details",
        "Any potential secret-bearing file classes"
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
        "Analyzer-driven bundle selection",
        "Safe default excludes raw secrets",
        "Supports Owner-uploaded chat continuity"
    )
}

$analysis = [ordered]@{
    schema_version = "IMPERIUM_ADMINISTRATUM_GIT_LOCAL_ANALYSIS_V0_2"
    task_id = "TASK-20260510-ADMINISTRATUM-ANALYZER-WORKTREE-CLASSIFIER-AND-FINAL-RECEIPT-SYNC-V0_1"
    generated_at = $analysisTime
    target = $targetMode
    runtime_output_dir = $outputDir
    legacy_tracked_output_dir = $legacyOutputDir
    git_reality = [ordered]@{
        root = $Root
        remote = $Remote
        branch = $branch
        local_head = $localHead
        origin_master_head = $originMasterHead
        upstream_head = $upstreamHead
        ls_remote_master_head = $lsRemoteMasterHead
        working_tree_clean = $workingTreeClean
        status_short_count = $statusShortCount
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
        tools_bundle_builder_exists = $toolsBundleBuilderExists
        workflow_launcher_exists = $workflowLauncherExists
        public_memory_ready_for_chat = $publicMemoryReadyForChat
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
        untracked_count = $untrackedCount
        untracked_paths_summary_file = $untrackedSummaryPath
        untracked_suspicious_count = $suspiciousManualReviewCandidates.Count
        untracked_heavy_count = @($privateRiskCandidates | Where-Object { $_ -match "\.zip$|\.tar\.gz$" }).Count
        untracked_recommendation = if ($recommendedWorktreeAction -eq "MANUAL_REVIEW_REQUIRED") { "MANUAL_REVIEW_REQUIRED" } elseif ($untrackedCount -gt 0) { "REVIEW_UNTRACKED" } else { "NONE" }
    }
    worktree_classifier = $worktreeClassifier
    context_gap = [ordered]@{
        target = $targetMode
        missing_public_context = $missingPublicContext
        missing_local_safe_context = $missingLocalSafeContext
        missing_private_owner_approved_context = $missingPrivateOwnerApprovedContext
        missing_for_vm2 = $missingForVm2
        missing_for_target = $missingForTarget
        enough_for_full_summary = ($missingPublicContext.Count -eq 0)
        enough_for_vm2 = ($missingForVm2.Count -eq 0)
        can_continue_from_git_only = $canContinueFromGitOnly
    }
    recommended_compilation = $recommendedCompilation
    owner_action = [ordered]@{
        recommended_owner_action = $recommendedOwnerAction
        reason = $ownerActionReason
        command_to_run_if_bundle_needed = $ownerCommand
        expected_zip_location = $expectedZipLocation
    }
    limitations = @(
        "Analyzer is metadata/path based and does not inspect secret file contents.",
        "Raw private data is excluded from default bundle behavior.",
        "VM2 workflow is advisory only and not executed in this task.",
        "Analyzer writes runtime outputs to .imperium_runtime and does not overwrite tracked CURRENT_STATE files.",
        "Analyzer remains PASS_WITH_LIMITATIONS."
    )
}

# Write outputs
$analysisPath = Join-Path $outputDir "GIT_LOCAL_ANALYSIS.json"
$recommendedPath = Join-Path $outputDir "RECOMMENDED_CHAT_COMPILATION.json"
$safeInventoryPath = Join-Path $outputDir "LOCAL_ONLY_SAFE_INVENTORY.json"
$worktreeJsonPath = Join-Path $outputDir "WORKTREE_CLASSIFICATION.json"
$worktreeReportPath = Join-Path $outputDir "WORKTREE_CLASSIFICATION_REPORT.md"
$gitSummaryPath = Join-Path $outputDir "GIT_PUBLIC_MEMORY_SUMMARY.md"
$gitRealityPath = Join-Path $outputDir "GIT_REALITY_REPORT.md"
$boundaryReportPath = Join-Path $outputDir "PUBLIC_PRIVATE_BOUNDARY_REPORT.md"
$contextGapPath = Join-Path $outputDir "CONTEXT_GAP_REPORT.md"
$ownerNextActionPath = Join-Path $outputDir "OWNER_NEXT_ACTION.md"
$lastVerifiedHeadPath = Join-Path $outputDir "LAST_VERIFIED_PUBLIC_HEAD.json"
$receiptPath = Join-Path $outputDir "ANALYZER_RECEIPT.json"

Write-JsonFile -Path $analysisPath -Data $analysis
Write-JsonFile -Path $recommendedPath -Data $recommendedCompilation
Write-JsonFile -Path $safeInventoryPath -Data ([ordered]@{
    schema_version = "LOCAL_ONLY_SAFE_INVENTORY_V0_2"
    generated_at = $analysisTime
    local_private_memory = $localPrivateMemory
    ignored_private_roots = $ignoredPrivateRoots
    not_ignored_private_roots = $notIgnoredPrivateRoots
})
Write-JsonFile -Path $worktreeJsonPath -Data $worktreeClassifier

if (-not $JsonOnly) {
    @(
        "# GIT PUBLIC MEMORY SUMMARY",
        "",
        "- generated_at: $analysisTime",
        "- branch: $branch",
        "- local_head: $localHead",
        "- origin_master_head: $originMasterHead",
        "- ls_remote_master_head: $lsRemoteMasterHead",
        "- public_memory_ready_for_chat: $publicMemoryReadyForChat"
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
        "- status_short_count: $statusShortCount",
        "- analyzer_report_commit: $localHead",
        "- git_reality_verdict: $gitRealityVerdict",
        "- post_push_reality_check_passed: $(if($PostPushRealityCheck){$postPushRealityPassed}else{'NOT_REQUESTED'})"
    ) | Set-Content -LiteralPath $gitRealityPath -Encoding UTF8

    @(
        "# PUBLIC PRIVATE BOUNDARY REPORT",
        "",
        "## Public in Git",
        "- Source, docs, status, tools, public artifacts, analyzer outputs.",
        "",
        "## Local-only",
        "- SSH_COMMAND_LIBRARY, ARCHIVE, BUNDLES_LOCAL, PRIVATE_CONTEXT_LOCAL, RUNTIME_LOCAL, CHAT_COMPILATIONS_LOCAL",
        "",
        "## Ignore summary",
        "- ignored_private_roots: $($ignoredPrivateRoots -join ', ')",
        "- not_ignored_private_roots: $($notIgnoredPrivateRoots -join ', ')",
        "",
        "## Suspicious scans",
        "- suspicious_tracked_paths_count: $($trackedSuspicious.Count)",
        "- suspicious_history_paths_count: $($historySuspicious.Count)",
        "- boundary_verdict: $boundaryVerdict",
        "",
        "## Must never commit",
        "- raw keys/tokens/passwords/.env/private command bodies",
        "- full ARCHIVE and full SSH_COMMAND_LIBRARY content"
    ) | Set-Content -LiteralPath $boundaryReportPath -Encoding UTF8

    $contextLines = @(
        "# CONTEXT GAP REPORT",
        "",
        "- target: $targetMode",
        "- enough_for_full_summary: $(($missingPublicContext.Count -eq 0))",
        "- enough_for_vm2: $(($missingForVm2.Count -eq 0))",
        "- can_continue_from_git_only: $canContinueFromGitOnly",
        "- needs_chat_compilation_bundle: $needsBundle",
        "",
        "## Missing Public Context"
    )
    if ($missingPublicContext.Count -eq 0) { $contextLines += "- none" } else { foreach ($m in $missingPublicContext) { $contextLines += "- $m" } }
    $contextLines += ""
    $contextLines += "## Missing Local Safe Context"
    if ($missingLocalSafeContext.Count -eq 0) { $contextLines += "- none" } else { foreach ($m in $missingLocalSafeContext) { $contextLines += "- $m" } }
    $contextLines += ""
    $contextLines += "## Missing Private Owner-Approved Context"
    if ($missingPrivateOwnerApprovedContext.Count -eq 0) { $contextLines += "- none" } else { foreach ($m in $missingPrivateOwnerApprovedContext) { $contextLines += "- $m" } }
    if ($targetMode -eq "VM2_WORK") {
        $contextLines += ""
        $contextLines += "## Missing for VM2"
        if ($missingForVm2.Count -eq 0) { $contextLines += "- none" } else { foreach ($m in $missingForVm2) { $contextLines += "- $m" } }
    }
    $contextLines += ""
    $contextLines += "## Recommendation"
    $contextLines += "- recommended_owner_action: $recommendedOwnerAction"
    $contextLines | Set-Content -LiteralPath $contextGapPath -Encoding UTF8

    $worktreeLines = @(
        "# WORKTREE CLASSIFICATION REPORT",
        "",
        "- total_changed_paths: $statusShortCount",
        "- modified_count: $modifiedCount",
        "- untracked_count: $untrackedCount",
        "- deleted_count: $deletedCount",
        "- renamed_count: $renamedCount",
        "- worktree_verdict: $worktreeVerdict",
        "- recommended_worktree_action: $recommendedWorktreeAction",
        ""
    )
    $groups = @(
        [ordered]@{ name = "PUBLIC_COMMIT_CANDIDATE"; items = $publicCommitCandidates; action = "COMMIT_PUBLIC_CHANGES" },
        [ordered]@{ name = "GENERATED_ARTIFACT_CANDIDATE"; items = $generatedArtifactCandidates; action = "COMMIT_ANALYZER_ARTIFACTS_OR_IGNORE_GENERATED" },
        [ordered]@{ name = "LOCAL_ONLY_IGNORE_CANDIDATE"; items = $localOnlyIgnoreCandidates; action = "KEEP_LOCAL_ONLY / UPDATE_IGNORE" },
        [ordered]@{ name = "SAFE_UNTRACKED_CANDIDATE"; items = $safeUntrackedCandidates; action = "COMMIT_PUBLIC_CHANGES" },
        [ordered]@{ name = "SUSPICIOUS_MANUAL_REVIEW"; items = $suspiciousManualReviewCandidates; action = "MANUAL_REVIEW_REQUIRED" },
        [ordered]@{ name = "PRIVATE_RISK_CANDIDATE"; items = $privateRiskCandidates; action = "MANUAL_REVIEW_REQUIRED" }
    )
    foreach ($g in $groups) {
        $worktreeLines += "## $($g.name)"
        $worktreeLines += "- recommended_action: $($g.action)"
        if ($g.items.Count -eq 0) { $worktreeLines += "- none" } else { foreach ($p in $g.items) { $worktreeLines += "- $p" } }
        $worktreeLines += ""
    }
    $worktreeLines += "Suspicious/private-risk present: $(if($suspiciousManualReviewCandidates.Count -gt 0 -or $privateRiskCandidates.Count -gt 0){'yes'}else{'no'})"
    $worktreeLines | Set-Content -LiteralPath $worktreeReportPath -Encoding UTF8

    @(
        "# OWNER NEXT ACTION",
        "",
        "- recommended_owner_action: $recommendedOwnerAction",
        "- reason: $ownerActionReason",
        "- command_to_run_if_bundle_needed: $ownerCommand",
        "- expected_zip_location: $expectedZipLocation",
        "",
        "Warning: if MANUAL_REVIEW_REQUIRED, review worktree classifier before any bundle build."
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
    can_use_github_as_public_memory = ($publicMemoryReadyForChat -and $postPushRealityPassed)
}
Write-JsonFile -Path $lastVerifiedHeadPath -Data $lastVerified

$receipt = [ordered]@{
    schema_version = "ADMINISTRATUM_ANALYZER_RECEIPT_V0_2"
    generated_at = $analysisTime
    target = $targetMode
    analyzer_report_commit = $localHead
    git_reality_verdict = $gitRealityVerdict
    working_tree_clean = $workingTreeClean
    status_short_count = $statusShortCount
    recommended_owner_action = $recommendedOwnerAction
    suspicious_tracked_paths_count = $trackedSuspicious.Count
    suspicious_history_paths_count = $historySuspicious.Count
    raw_secrets_copied = $false
    outputs = @(
        $analysisPath,
        $worktreeJsonPath,
        $worktreeReportPath,
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

Write-Output $analysisPath
