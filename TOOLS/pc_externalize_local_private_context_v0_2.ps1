param(
    [string]$RepoRoot = 'E:\IMPERIUM',
    [string]$LocalRoot = 'E:\IMPERIUM_LOCAL',
    [string]$PrivateRoot = 'E:\IMPERIUM_PRIVATE',
    [string]$ReportTag = 'SAN_CLEANING_REPO_PARITY_20260513',
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-WarnLine {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Ok {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Ensure-Dir {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function Git-Out {
    param([string[]]$GitArgs)
    & git -C $RepoRoot @GitArgs
}

function Normalize-Rel {
    param([string]$Rel)
    return ($Rel -replace '\\', '/').Trim()
}

function Get-GitStatusKind {
    param(
        [string]$Rel,
        [System.Collections.Generic.HashSet[string]]$IgnoredSet,
        [System.Collections.Generic.HashSet[string]]$UntrackedSet,
        [System.Collections.Generic.HashSet[string]]$TrackedSet
    )
    if ($TrackedSet.Contains($Rel)) { return 'tracked' }
    if ($IgnoredSet.Contains($Rel)) { return 'ignored' }
    if ($UntrackedSet.Contains($Rel)) { return 'untracked' }
    return 'unknown'
}

function Get-Classification {
    param([string]$RelNorm)

    if ($RelNorm -match '(^|/)\.imperium_runtime(/|$)') {
        return @{ classification = 'move_to_local_runtime'; target = 'RUNTIME' }
    }

    if ($RelNorm -match '(^|/)(INBOX|_INBOX)(/|$)') {
        return @{ classification = 'move_to_local_inbox'; target = 'INBOX' }
    }

    if ($RelNorm -match '(^|/)(VM2_BUNDLES|BUNDLES_LOCAL)(/|$)' -or $RelNorm -match '(^|/)INBOX/VM2_BUNDLES(/|$)') {
        return @{ classification = 'move_to_local_inbox'; target = 'VM2_BUNDLES' }
    }

    if ($RelNorm -match 'bundle_review|bundle-review|bundle_intake|bundle-intake|bundle_extract|bundle-extract|review_bundle') {
        return @{ classification = 'move_to_local_bundle_reviews'; target = 'BUNDLE_REVIEWS' }
    }

    if ($RelNorm -match '(^|/)(CHAT_COMPILATIONS_LOCAL|OWNER_SUPPLEMENTS|PRIVATE_CONTEXT_LOCAL|PRIVATE_CONTEXT_PACKS|FULL_HANDOFF_INPUTS|LOCAL_ONLY_ARCHIVE_IF_NEEDED|SECRETS_NEVER_COMMIT)(/|$)') {
        return @{ classification = 'move_to_private_owner_context'; target = 'PRIVATE' }
    }

    if ($RelNorm -match '(^|/)LOCAL_CLEANUP_RECEIPTS(/|$)') {
        return @{ classification = 'move_to_local_reports'; target = 'LOCAL_CLEANUP_RECEIPTS' }
    }

    if ($RelNorm -match '(^|/)(GENERATED_LOCAL_REPORTS|LOCAL_REPORTS|RUNTIME_REPORTS|LOCAL_DIAGNOSTICS)(/|$)') {
        return @{ classification = 'move_to_local_reports'; target = 'GENERATED_LOCAL_REPORTS' }
    }

    if ($RelNorm -match '(^|/)(__pycache__|\.pytest_cache)(/|$)' -or $RelNorm -match '\.pyc$') {
        return @{ classification = 'delete_disposable_cache'; target = 'DELETE' }
    }

    if ($RelNorm -match '\.zip$' -and ($RelNorm -match 'bundle|handoff|transfer|inbox|outbox|vm2')) {
        return @{ classification = 'move_to_local_inbox'; target = 'VM2_BUNDLES' }
    }

    return @{ classification = 'leave_in_place_ambiguous'; target = 'AMBIGUOUS' }
}

if (-not (Test-Path -LiteralPath (Join-Path $RepoRoot '.git'))) {
    throw "Repo root is not a git worktree: $RepoRoot"
}

Write-Info "RepoRoot=$RepoRoot"
Write-Info "LocalRoot=$LocalRoot"
Write-Info "PrivateRoot=$PrivateRoot"
Write-Info "DryRun=$($DryRun.IsPresent)"

$localSkeleton = @(
    $LocalRoot,
    (Join-Path $LocalRoot 'INBOX'),
    (Join-Path $LocalRoot 'VM2_BUNDLES'),
    (Join-Path $LocalRoot 'BUNDLE_REVIEWS'),
    (Join-Path $LocalRoot 'LOCAL_CLEANUP_RECEIPTS'),
    (Join-Path $LocalRoot 'CONTINUITY_PACK_OUTPUT'),
    (Join-Path $LocalRoot 'TEMP_WORK'),
    (Join-Path $LocalRoot 'GENERATED_LOCAL_REPORTS'),
    (Join-Path $LocalRoot 'RUNTIME'),
    (Join-Path $LocalRoot 'CACHE_DISPOSABLE'),
    (Join-Path $LocalRoot 'ARTIFACTS_LOCAL')
)

$privateSkeleton = @(
    $PrivateRoot,
    (Join-Path $PrivateRoot 'OWNER_SUPPLEMENTS'),
    (Join-Path $PrivateRoot 'PRIVATE_CONTEXT_PACKS'),
    (Join-Path $PrivateRoot 'FULL_HANDOFF_INPUTS'),
    (Join-Path $PrivateRoot 'LOCAL_ONLY_ARCHIVE_IF_NEEDED'),
    (Join-Path $PrivateRoot 'SECRETS_NEVER_COMMIT')
)

foreach ($path in ($localSkeleton + $privateSkeleton)) {
    Ensure-Dir -Path $path
}

$reportDir = Join-Path (Join-Path $LocalRoot 'GENERATED_LOCAL_REPORTS') $ReportTag
Ensure-Dir -Path $reportDir

$beforeHead = (Git-Out -GitArgs @('rev-parse', 'HEAD') | Select-Object -First 1).Trim()
$beforeCount = (Git-Out -GitArgs @('rev-list', '--count', 'HEAD') | Select-Object -First 1).Trim()
$beforeSubject = (Git-Out -GitArgs @('log', '-1', '--pretty=%s') | Select-Object -First 1).Trim()
$statusShortBefore = @(Git-Out -GitArgs @('status', '--short'))
$statusShortIgnoredBefore = @(Git-Out -GitArgs @('status', '--short', '--ignored'))
$trackedBefore = @(Git-Out -GitArgs @('ls-files'))
$ignoredBefore = @(Git-Out -GitArgs @('ls-files', '--others', '--ignored', '--exclude-standard'))
$untrackedBefore = @(Git-Out -GitArgs @('ls-files', '--others', '--exclude-standard'))

Set-Content -Encoding UTF8 (Join-Path $reportDir 'PC_GIT_TRUTH_BEFORE.txt') -Value @(
    "head=$beforeHead",
    "commit_count=$beforeCount",
    "latest_subject=$beforeSubject"
)
Set-Content -Encoding UTF8 (Join-Path $reportDir 'PC_STATUS_SHORT_BEFORE.txt') -Value $statusShortBefore
Set-Content -Encoding UTF8 (Join-Path $reportDir 'PC_STATUS_SHORT_IGNORED_BEFORE.txt') -Value $statusShortIgnoredBefore
Set-Content -Encoding UTF8 (Join-Path $reportDir 'PC_IGNORED_FILES_BEFORE.txt') -Value $ignoredBefore
Set-Content -Encoding UTF8 (Join-Path $reportDir 'PC_UNTRACKED_FILES_BEFORE.txt') -Value $untrackedBefore
Set-Content -Encoding UTF8 (Join-Path $reportDir 'PC_TRACKED_FILES_BEFORE.txt') -Value $trackedBefore

$ignoredSet = New-Object 'System.Collections.Generic.HashSet[string]' ([System.StringComparer]::OrdinalIgnoreCase)
$untrackedSet = New-Object 'System.Collections.Generic.HashSet[string]' ([System.StringComparer]::OrdinalIgnoreCase)
$trackedSet = New-Object 'System.Collections.Generic.HashSet[string]' ([System.StringComparer]::OrdinalIgnoreCase)
foreach ($p in $ignoredBefore) { if ($p) { [void]$ignoredSet.Add((Normalize-Rel $p)) } }
foreach ($p in $untrackedBefore) { if ($p) { [void]$untrackedSet.Add((Normalize-Rel $p)) } }
foreach ($p in $trackedBefore) { if ($p) { [void]$trackedSet.Add((Normalize-Rel $p)) } }

$allCandidates = @()
foreach ($p in $ignoredSet) { $allCandidates += $p }
foreach ($p in $untrackedSet) { if (-not $ignoredSet.Contains($p)) { $allCandidates += $p } }
$allCandidates = $allCandidates | Sort-Object -Unique

$manifest = @()

foreach ($rel in $allCandidates) {
    $relNorm = Normalize-Rel $rel
    $statusKind = Get-GitStatusKind -Rel $relNorm -IgnoredSet $ignoredSet -UntrackedSet $untrackedSet -TrackedSet $trackedSet
    $classInfo = Get-Classification -RelNorm $relNorm
    $classification = $classInfo.classification
    $target = $classInfo.target

    $sourcePath = Join-Path $RepoRoot ($relNorm -replace '/', '\\')
    $entry = [ordered]@{
        source_path = $sourcePath
        repo_relative_path = $relNorm
        git_status_kind = $statusKind
        classification = $classification
        action = ''
        destination_path = $null
        reason = ''
        timestamp = (Get-Date).ToString('s')
        success = $false
        error = $null
    }

    if ($statusKind -eq 'tracked') {
        $entry.action = 'left_in_place_tracked'
        $entry.reason = 'Tracked files must never be moved or deleted by this launcher.'
        $entry.success = $true
        $manifest += [pscustomobject]$entry
        continue
    }

    if (-not (Test-Path -LiteralPath $sourcePath)) {
        $entry.action = 'left_in_place_ambiguous'
        $entry.reason = 'Source path not found at execution time; no action performed.'
        $entry.success = $false
        $entry.error = 'source_missing'
        $manifest += [pscustomobject]$entry
        continue
    }

    if ($classification -eq 'delete_disposable_cache') {
        $entry.action = 'deleted_cache'
        $entry.reason = 'Ignored/untracked disposable Python cache path.'
        try {
            if (-not $DryRun) {
                Remove-Item -LiteralPath $sourcePath -Recurse -Force -ErrorAction Stop
            }
            $entry.success = $true
        } catch {
            $entry.success = $false
            $entry.error = $_.Exception.Message
        }
        $manifest += [pscustomobject]$entry
        continue
    }

    if ($classification -eq 'move_to_private_owner_context') {
        $destRoot = Join-Path $PrivateRoot 'FULL_HANDOFF_INPUTS'
        $entry.action = 'moved_to_private'
        $entry.reason = 'Owner/private context path must live outside canonical git worktree.'
    } elseif ($classification -eq 'move_to_local_runtime') {
        $destRoot = Join-Path $LocalRoot 'RUNTIME'
        $entry.action = 'moved_to_local'
        $entry.reason = 'Runtime/generated artifacts are local-only and should not remain in repo.'
    } elseif ($classification -eq 'move_to_local_inbox') {
        if ($target -eq 'VM2_BUNDLES') {
            $destRoot = Join-Path $LocalRoot 'VM2_BUNDLES'
        } else {
            $destRoot = Join-Path $LocalRoot 'INBOX'
        }
        $entry.action = 'moved_to_local'
        $entry.reason = 'Local intake/bundle materials belong in external local root.'
    } elseif ($classification -eq 'move_to_local_bundle_reviews') {
        $destRoot = Join-Path $LocalRoot 'BUNDLE_REVIEWS'
        $entry.action = 'moved_to_local'
        $entry.reason = 'Bundle review/extract materials belong in external local review root.'
    } elseif ($classification -eq 'move_to_local_reports') {
        if ($target -eq 'LOCAL_CLEANUP_RECEIPTS') {
            $destRoot = Join-Path $LocalRoot 'LOCAL_CLEANUP_RECEIPTS'
        } else {
            $destRoot = Join-Path $LocalRoot 'GENERATED_LOCAL_REPORTS'
        }
        $entry.action = 'moved_to_local'
        $entry.reason = 'Generated local reports/receipts should be externalized.'
    } else {
        $entry.action = 'left_in_place_ambiguous'
        $entry.reason = 'Ambiguous path classification requires Owner decision.'
        $entry.success = $true
        $manifest += [pscustomobject]$entry
        continue
    }

    $destPath = Join-Path $destRoot ($relNorm -replace '/', '\\')
    $entry.destination_path = $destPath

    try {
        Ensure-Dir -Path (Split-Path -Parent $destPath)
        if (-not $DryRun) {
            Move-Item -LiteralPath $sourcePath -Destination $destPath -Force -ErrorAction Stop
        }
        $entry.success = $true
    } catch {
        $entry.success = $false
        $entry.error = $_.Exception.Message
    }

    $manifest += [pscustomobject]$entry
}

$manifestPath = Join-Path $reportDir 'PC_EXTERNALIZATION_MANIFEST_20260513.json'
$manifest | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 $manifestPath

$afterHead = (Git-Out -GitArgs @('rev-parse', 'HEAD') | Select-Object -First 1).Trim()
$afterCount = (Git-Out -GitArgs @('rev-list', '--count', 'HEAD') | Select-Object -First 1).Trim()
$afterSubject = (Git-Out -GitArgs @('log', '-1', '--pretty=%s') | Select-Object -First 1).Trim()
$statusShortAfter = @(Git-Out -GitArgs @('status', '--short'))
$statusShortIgnoredAfter = @(Git-Out -GitArgs @('status', '--short', '--ignored'))
$ignoredAfter = @(Git-Out -GitArgs @('ls-files', '--others', '--ignored', '--exclude-standard'))
$untrackedAfter = @(Git-Out -GitArgs @('ls-files', '--others', '--exclude-standard'))
$trackedAfter = @(Git-Out -GitArgs @('ls-files'))

Set-Content -Encoding UTF8 (Join-Path $reportDir 'PC_GIT_TRUTH_AFTER.txt') -Value @(
    "head=$afterHead",
    "commit_count=$afterCount",
    "latest_subject=$afterSubject"
)
Set-Content -Encoding UTF8 (Join-Path $reportDir 'PC_STATUS_SHORT_AFTER.txt') -Value $statusShortAfter
Set-Content -Encoding UTF8 (Join-Path $reportDir 'PC_STATUS_SHORT_IGNORED_AFTER.txt') -Value $statusShortIgnoredAfter
Set-Content -Encoding UTF8 (Join-Path $reportDir 'PC_IGNORED_FILES_AFTER.txt') -Value $ignoredAfter
Set-Content -Encoding UTF8 (Join-Path $reportDir 'PC_UNTRACKED_FILES_AFTER.txt') -Value $untrackedAfter
Set-Content -Encoding UTF8 (Join-Path $reportDir 'PC_TRACKED_FILES_AFTER.txt') -Value $trackedAfter

$counts = @{
    moved_to_local = ($manifest | Where-Object { $_.action -eq 'moved_to_local' -and $_.success }).Count
    moved_to_private = ($manifest | Where-Object { $_.action -eq 'moved_to_private' -and $_.success }).Count
    deleted_cache = ($manifest | Where-Object { $_.action -eq 'deleted_cache' -and $_.success }).Count
    left_in_place_ambiguous = ($manifest | Where-Object { $_.action -eq 'left_in_place_ambiguous' }).Count
    left_in_place_tracked = ($manifest | Where-Object { $_.action -eq 'left_in_place_tracked' }).Count
    errors = ($manifest | Where-Object { -not $_.success }).Count
}

$archiveAbsent = -not (Test-Path -LiteralPath (Join-Path $RepoRoot 'ARCHIVE'))
$observedAbsent = -not (Test-Path -LiteralPath (Join-Path $RepoRoot 'OBSERVED'))

$summaryPath = Join-Path $reportDir 'PC_EXTERNALIZATION_SUMMARY_20260513.md'
@(
    '# PC Externalization Summary (2026-05-13)',
    '',
    "- repo_root: $RepoRoot",
    "- local_root: $LocalRoot",
    "- private_root: $PrivateRoot",
    "- dry_run: $($DryRun.IsPresent)",
    "- before_head: $beforeHead",
    "- after_head: $afterHead",
    "- moved_to_local: $($counts.moved_to_local)",
    "- moved_to_private: $($counts.moved_to_private)",
    "- deleted_cache: $($counts.deleted_cache)",
    "- left_in_place_ambiguous: $($counts.left_in_place_ambiguous)",
    "- errors: $($counts.errors)",
    "- archive_absent: $archiveAbsent",
    "- observed_absent: $observedAbsent",
    "- ignored_before_count: $($ignoredBefore.Count)",
    "- ignored_after_count: $($ignoredAfter.Count)",
    "- untracked_before_count: $($untrackedBefore.Count)",
    "- untracked_after_count: $($untrackedAfter.Count)",
    "- manifest: $manifestPath"
) | Set-Content -Encoding UTF8 $summaryPath

Write-Ok "Externalization run finished."
Write-Host "report_dir=$reportDir"
Write-Host "manifest=$manifestPath"
Write-Host "archive_absent=$archiveAbsent observed_absent=$observedAbsent"
Write-Host "counts=$(($counts | ConvertTo-Json -Compress))"
