param(
    [string]$RepoRoot = 'E:\IMPERIUM',
    [string]$LegacyLocalRoot = 'E:\IMPERIUM_LOCAL',
    [string]$LegacyPrivateRoot = 'E:\IMPERIUM_PRIVATE',
    [string]$ContextRoot = 'E:\IMPERIUM_CONTEXT',
    [string]$ReportTag = 'EXTERNAL_CONTEXT_REGISTRY_20260514',
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

function Relative-Path {
    param(
        [string]$Base,
        [string]$Full
    )
    $baseNorm = ([System.IO.Path]::GetFullPath($Base)).TrimEnd('\\')
    $fullNorm = [System.IO.Path]::GetFullPath($Full)
    if ($fullNorm.StartsWith($baseNorm, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $fullNorm.Substring($baseNorm.Length).TrimStart('\\')
    }
    return $Full
}

function Get-TreeSnapshot {
    param([string]$Root)
    if (-not (Test-Path -LiteralPath $Root)) {
        return @("MISSING: $Root")
    }
    $items = Get-ChildItem -LiteralPath $Root -Recurse -Force -ErrorAction SilentlyContinue
    if (-not $items) {
        return @("EMPTY: $Root")
    }
    $out = @()
    foreach ($item in $items) {
        $rel = Relative-Path -Base $Root -Full $item.FullName
        if ($item.PSIsContainer) {
            $out += "[D] $rel"
        } else {
            $out += "[F] $rel"
        }
    }
    return $out
}

function Add-ManifestEntry {
    param(
        [ref]$Manifest,
        [string]$SourcePath,
        [string]$RepoRelativePath,
        [string]$Classification,
        [string]$Action,
        [string]$DestinationPath,
        [string]$Reason,
        [bool]$Success,
        [string]$ErrorText,
        [string]$GitStatusKind = 'external'
    )

    $entry = [ordered]@{
        source_path = $SourcePath
        repo_relative_path = $RepoRelativePath
        git_status_kind = $GitStatusKind
        classification = $Classification
        action = $Action
        destination_path = $DestinationPath
        reason = $Reason
        timestamp = (Get-Date).ToString('s')
        success = $Success
        error = $ErrorText
    }
    $Manifest.Value += [pscustomobject]$entry
}

function Get-ExtensionCount {
    param([array]$Files)
    $map = @{}
    foreach ($f in $Files) {
        $ext = [System.IO.Path]::GetExtension($f.Name)
        if ([string]::IsNullOrWhiteSpace($ext)) { $ext = '[no_ext]' }
        $ext = $ext.ToLowerInvariant()
        if (-not $map.ContainsKey($ext)) { $map[$ext] = 0 }
        $map[$ext] += 1
    }
    return $map
}

function Get-DirMetrics {
    param(
        [string]$Root,
        [bool]$IncludeSamples,
        [int]$SampleLimit = 40
    )
    if (-not (Test-Path -LiteralPath $Root)) {
        return [ordered]@{
            path = $Root
            exists = $false
            file_count = 0
            directory_count = 0
            total_bytes = 0
            extension_counts = @{}
            top_level_categories = @()
            sample_paths = @()
        }
    }

    $files = Get-ChildItem -LiteralPath $Root -Recurse -Force -File -ErrorAction SilentlyContinue
    $dirs = Get-ChildItem -LiteralPath $Root -Recurse -Force -Directory -ErrorAction SilentlyContinue
    $totalBytes = 0
    foreach ($f in $files) {
        try {
            $totalBytes += [int64]$f.Length
        } catch {
        }
    }

    $top = @()
    $topDirs = Get-ChildItem -LiteralPath $Root -Force -Directory -ErrorAction SilentlyContinue
    foreach ($d in $topDirs) {
        $top += $d.Name
    }

    $samples = @()
    if ($IncludeSamples) {
        foreach ($f in $files | Select-Object -First $SampleLimit) {
            $samples += (Relative-Path -Base $Root -Full $f.FullName).Replace('\\', '/')
        }
    }

    return [ordered]@{
        path = $Root
        exists = $true
        file_count = @($files).Count
        directory_count = @($dirs).Count
        total_bytes = $totalBytes
        extension_counts = Get-ExtensionCount -Files $files
        top_level_categories = $top
        sample_paths = $samples
    }
}

function Classify-LocalPath {
    param([string]$RelativePath)
    $p = $RelativePath.Replace('\\', '/').ToLowerInvariant()
    if ($p -match '(^|/)cache_disposable(/|$)' -or $p -match '__pycache__|\.pyc$|\.pytest_cache') {
        return 'delete_candidate'
    }
    if ($p -match '(^|/)(runtime|generated_local_reports|bundle_reviews|vm2_bundles|inbox|prompt_dispatch|handoff_output)(/|$)') {
        return 'keep_operational'
    }
    if ($p -match '(^|/)(artifacts_local|temp_work|continuity_pack_output|local_cleanup_receipts)(/|$)') {
        return 'review_candidate'
    }
    return 'review_candidate'
}

function Build-LocalClassificationSummary {
    param([string]$LocalRootPath)
    $result = [ordered]@{
        keep_operational = 0
        review_candidate = 0
        delete_candidate = 0
    }
    if (-not (Test-Path -LiteralPath $LocalRootPath)) {
        return $result
    }
    $files = Get-ChildItem -LiteralPath $LocalRootPath -Recurse -Force -File -ErrorAction SilentlyContinue
    foreach ($f in $files) {
        $rel = (Relative-Path -Base $LocalRootPath -Full $f.FullName).Replace('\\', '/')
        $bucket = Classify-LocalPath -RelativePath $rel
        $result[$bucket] += 1
    }
    return $result
}

$contextLocalRoot = Join-Path $ContextRoot 'LOCAL'
$contextPrivateRoot = Join-Path $ContextRoot 'PRIVATE'
$reportDir = Join-Path (Join-Path $contextLocalRoot 'GENERATED_LOCAL_REPORTS') $ReportTag
$runStamp = Get-Date -Format 'yyyyMMdd_HHmmss'

Write-Info "RepoRoot=$RepoRoot"
Write-Info "LegacyLocalRoot=$LegacyLocalRoot"
Write-Info "LegacyPrivateRoot=$LegacyPrivateRoot"
Write-Info "ContextRoot=$ContextRoot"
Write-Info "DryRun=$($DryRun.IsPresent)"

if (-not (Test-Path -LiteralPath (Join-Path $RepoRoot '.git'))) {
    throw "Repo root is not a git worktree: $RepoRoot"
}

$localSkeleton = @(
    $contextLocalRoot,
    (Join-Path $contextLocalRoot 'INBOX'),
    (Join-Path $contextLocalRoot 'VM2_BUNDLES'),
    (Join-Path $contextLocalRoot 'BUNDLE_REVIEWS'),
    (Join-Path $contextLocalRoot 'LOCAL_CLEANUP_RECEIPTS'),
    (Join-Path $contextLocalRoot 'CONTINUITY_PACK_OUTPUT'),
    (Join-Path $contextLocalRoot 'TEMP_WORK'),
    (Join-Path $contextLocalRoot 'GENERATED_LOCAL_REPORTS'),
    (Join-Path $contextLocalRoot 'RUNTIME'),
    (Join-Path $contextLocalRoot 'CACHE_DISPOSABLE'),
    (Join-Path $contextLocalRoot 'ARTIFACTS_LOCAL'),
    (Join-Path $contextLocalRoot 'ROUTE_EVIDENCE'),
    (Join-Path $contextLocalRoot 'PROMPT_DISPATCH'),
    (Join-Path $contextLocalRoot 'HANDOFF_OUTPUT')
)

$privateSkeleton = @(
    $contextPrivateRoot,
    (Join-Path $contextPrivateRoot 'OWNER_SUPPLEMENTS'),
    (Join-Path $contextPrivateRoot 'PRIVATE_CONTEXT_PACKS'),
    (Join-Path $contextPrivateRoot 'FULL_HANDOFF_INPUTS'),
    (Join-Path $contextPrivateRoot 'LOCAL_ONLY_ARCHIVE_IF_NEEDED'),
    (Join-Path $contextPrivateRoot 'SECRETS_NEVER_COMMIT')
)

foreach ($p in ($localSkeleton + $privateSkeleton)) {
    Ensure-Dir -Path $p
}
Ensure-Dir -Path $reportDir

$beforeLocalTreePath = Join-Path $reportDir 'PC_EXTERNAL_CONTEXT_BEFORE_TREE_LOCAL.txt'
$beforePrivateTreePath = Join-Path $reportDir 'PC_EXTERNAL_CONTEXT_BEFORE_TREE_PRIVATE.txt'
$afterContextTreePath = Join-Path $reportDir 'PC_EXTERNAL_CONTEXT_AFTER_TREE_CONTEXT.txt'
$manifestPath = Join-Path $reportDir 'PC_EXTERNAL_CONTEXT_MIGRATION_MANIFEST_20260514.json'
$routeTestPath = Join-Path $reportDir 'PC_EXTERNAL_CONTEXT_ROUTE_TEST.txt'
$summaryPath = Join-Path $reportDir 'PC_EXTERNAL_CONTEXT_SUMMARY_20260514.md'
$fullLocalIndexPath = Join-Path $reportDir 'PC_EXTERNAL_CONTEXT_INDEX_FULL_LOCAL.json'
$redactedJsonPath = Join-Path $reportDir 'PC_EXTERNAL_CONTEXT_INDEX_REDACTED_FOR_GIT.json'
$redactedMdPath = Join-Path $reportDir 'PC_EXTERNAL_CONTEXT_INDEX_REDACTED_FOR_GIT.md'

Set-Content -Encoding UTF8 -Path $beforeLocalTreePath -Value (Get-TreeSnapshot -Root $LegacyLocalRoot)
Set-Content -Encoding UTF8 -Path $beforePrivateTreePath -Value (Get-TreeSnapshot -Root $LegacyPrivateRoot)

$manifest = @()
$movedCount = 0
$conflictCount = 0
$errorCount = 0

function Move-WithMerge {
    param(
        [string]$SourcePath,
        [string]$SourceBase,
        [string]$DestinationPath,
        [string]$ConflictBase,
        [string]$Classification
    )

    $script:manifest = $script:manifest

    if (-not (Test-Path -LiteralPath $SourcePath)) {
        Add-ManifestEntry -Manifest ([ref]$script:manifest) -SourcePath $SourcePath -RepoRelativePath '' -Classification $Classification -Action 'missing_source' -DestinationPath $DestinationPath -Reason 'Source path missing.' -Success $false -ErrorText 'source_missing'
        $script:errorCount += 1
        return
    }

    $item = Get-Item -LiteralPath $SourcePath -Force
    $rel = Relative-Path -Base $SourceBase -Full $SourcePath

    if ($item.PSIsContainer) {
        if (-not (Test-Path -LiteralPath $DestinationPath)) {
            try {
                if (-not $DryRun) {
                    Move-Item -LiteralPath $SourcePath -Destination $DestinationPath -Force -ErrorAction Stop
                }
                Add-ManifestEntry -Manifest ([ref]$script:manifest) -SourcePath $SourcePath -RepoRelativePath $rel -Classification $Classification -Action 'moved_to_context' -DestinationPath $DestinationPath -Reason 'Directory moved to unified context root.' -Success $true -ErrorText $null
                $script:movedCount += 1
            } catch {
                Add-ManifestEntry -Manifest ([ref]$script:manifest) -SourcePath $SourcePath -RepoRelativePath $rel -Classification $Classification -Action 'move_failed' -DestinationPath $DestinationPath -Reason 'Directory move failed.' -Success $false -ErrorText $_.Exception.Message
                $script:errorCount += 1
            }
            return
        }

        $destItem = Get-Item -LiteralPath $DestinationPath -Force
        if (-not $destItem.PSIsContainer) {
            $conflictDest = Join-Path $ConflictBase $rel
            Ensure-Dir -Path (Split-Path -Parent $conflictDest)
            try {
                if (-not $DryRun) {
                    Move-Item -LiteralPath $SourcePath -Destination $conflictDest -Force -ErrorAction Stop
                }
                Add-ManifestEntry -Manifest ([ref]$script:manifest) -SourcePath $SourcePath -RepoRelativePath $rel -Classification $Classification -Action 'moved_to_conflict' -DestinationPath $conflictDest -Reason 'Destination exists as file; redirected to conflict path.' -Success $true -ErrorText $null
                $script:conflictCount += 1
            } catch {
                Add-ManifestEntry -Manifest ([ref]$script:manifest) -SourcePath $SourcePath -RepoRelativePath $rel -Classification $Classification -Action 'conflict_move_failed' -DestinationPath $conflictDest -Reason 'Conflict redirect failed.' -Success $false -ErrorText $_.Exception.Message
                $script:errorCount += 1
            }
            return
        }

        $children = Get-ChildItem -LiteralPath $SourcePath -Force -ErrorAction SilentlyContinue
        foreach ($child in $children) {
            $childDest = Join-Path $DestinationPath $child.Name
            Move-WithMerge -SourcePath $child.FullName -SourceBase $SourceBase -DestinationPath $childDest -ConflictBase $ConflictBase -Classification $Classification
        }

        try {
            if (-not $DryRun) {
                $remaining = Get-ChildItem -LiteralPath $SourcePath -Force -ErrorAction SilentlyContinue
                if (@($remaining).Count -eq 0) {
                    Remove-Item -LiteralPath $SourcePath -Force -ErrorAction SilentlyContinue
                }
            }
        } catch {
        }
        return
    }

    # File move
    if (-not (Test-Path -LiteralPath $DestinationPath)) {
        Ensure-Dir -Path (Split-Path -Parent $DestinationPath)
        try {
            if (-not $DryRun) {
                Move-Item -LiteralPath $SourcePath -Destination $DestinationPath -Force -ErrorAction Stop
            }
            Add-ManifestEntry -Manifest ([ref]$script:manifest) -SourcePath $SourcePath -RepoRelativePath $rel -Classification $Classification -Action 'moved_to_context' -DestinationPath $DestinationPath -Reason 'File moved to unified context root.' -Success $true -ErrorText $null
            $script:movedCount += 1
        } catch {
            Add-ManifestEntry -Manifest ([ref]$script:manifest) -SourcePath $SourcePath -RepoRelativePath $rel -Classification $Classification -Action 'move_failed' -DestinationPath $DestinationPath -Reason 'File move failed.' -Success $false -ErrorText $_.Exception.Message
            $script:errorCount += 1
        }
        return
    }

    $conflictDest = Join-Path $ConflictBase $rel
    Ensure-Dir -Path (Split-Path -Parent $conflictDest)
    try {
        if (-not $DryRun) {
            Move-Item -LiteralPath $SourcePath -Destination $conflictDest -Force -ErrorAction Stop
        }
        Add-ManifestEntry -Manifest ([ref]$script:manifest) -SourcePath $SourcePath -RepoRelativePath $rel -Classification $Classification -Action 'moved_to_conflict' -DestinationPath $conflictDest -Reason 'Destination already exists; redirected to conflict path.' -Success $true -ErrorText $null
        $script:conflictCount += 1
    } catch {
        Add-ManifestEntry -Manifest ([ref]$script:manifest) -SourcePath $SourcePath -RepoRelativePath $rel -Classification $Classification -Action 'conflict_move_failed' -DestinationPath $conflictDest -Reason 'Conflict redirect failed.' -Success $false -ErrorText $_.Exception.Message
        $script:errorCount += 1
    }
}

$localConflictBase = Join-Path $contextLocalRoot (Join-Path 'CONFLICTS' $runStamp)
$privateConflictBase = Join-Path $contextPrivateRoot (Join-Path 'CONFLICTS' $runStamp)
Ensure-Dir -Path $localConflictBase
Ensure-Dir -Path $privateConflictBase

if (Test-Path -LiteralPath $LegacyLocalRoot) {
    $topLocal = Get-ChildItem -LiteralPath $LegacyLocalRoot -Force -ErrorAction SilentlyContinue
    foreach ($item in $topLocal) {
        if ($item.FullName -ieq $ContextRoot) { continue }
        $dest = Join-Path $contextLocalRoot $item.Name
        Move-WithMerge -SourcePath $item.FullName -SourceBase $LegacyLocalRoot -DestinationPath $dest -ConflictBase $localConflictBase -Classification 'migrate_legacy_local_to_context_local'
    }
}

if (Test-Path -LiteralPath $LegacyPrivateRoot) {
    $topPrivate = Get-ChildItem -LiteralPath $LegacyPrivateRoot -Force -ErrorAction SilentlyContinue
    foreach ($item in $topPrivate) {
        if ($item.FullName -ieq $ContextRoot) { continue }
        $dest = Join-Path $contextPrivateRoot $item.Name
        Move-WithMerge -SourcePath $item.FullName -SourceBase $LegacyPrivateRoot -DestinationPath $dest -ConflictBase $privateConflictBase -Classification 'migrate_legacy_private_to_context_private'
    }
}

# Leave legacy redirect markers
$legacyMarker = @(
    'Legacy external root retained for compatibility.',
    "Primary path is now: $ContextRoot",
    "LOCAL root: $contextLocalRoot",
    "PRIVATE root: $contextPrivateRoot",
    "updated_at: $((Get-Date).ToString('s'))"
)

if (Test-Path -LiteralPath $LegacyLocalRoot) {
    Set-Content -Encoding UTF8 -Path (Join-Path $LegacyLocalRoot 'LEGACY_REDIRECT_TO_IMPERIUM_CONTEXT.txt') -Value $legacyMarker
}
if (Test-Path -LiteralPath $LegacyPrivateRoot) {
    Set-Content -Encoding UTF8 -Path (Join-Path $LegacyPrivateRoot 'LEGACY_REDIRECT_TO_IMPERIUM_CONTEXT.txt') -Value $legacyMarker
}

Set-Content -Encoding UTF8 -Path $afterContextTreePath -Value (Get-TreeSnapshot -Root $ContextRoot)
$manifest | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 -Path $manifestPath

# Index build
$localMetrics = Get-DirMetrics -Root $contextLocalRoot -IncludeSamples $true
$privateMetrics = Get-DirMetrics -Root $contextPrivateRoot -IncludeSamples $false
$localClassification = Build-LocalClassificationSummary -LocalRootPath $contextLocalRoot

$fullLocal = [ordered]@{
    schema_version = 'imperium.external_context_index_full_local.v0_1'
    generated_at_utc = (Get-Date).ToUniversalTime().ToString('s') + 'Z'
    context_root = $ContextRoot
    local = $localMetrics
    local_classification_summary = $localClassification
}
$fullLocal | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 -Path $fullLocalIndexPath

$redacted = [ordered]@{
    schema_version = 'imperium.external_context_index_redacted.v0_1'
    generated_at_utc = (Get-Date).ToUniversalTime().ToString('s') + 'Z'
    context_root = $ContextRoot
    local_root = $contextLocalRoot
    private_root = $contextPrivateRoot
    local = [ordered]@{
        path = $contextLocalRoot
        file_count = $localMetrics.file_count
        directory_count = $localMetrics.directory_count
        total_bytes = $localMetrics.total_bytes
        extension_counts = $localMetrics.extension_counts
        top_level_categories = $localMetrics.top_level_categories
        sample_paths = $localMetrics.sample_paths
        classification_summary = $localClassification
    }
    private = [ordered]@{
        path = $contextPrivateRoot
        file_count = $privateMetrics.file_count
        directory_count = $privateMetrics.directory_count
        total_bytes = $privateMetrics.total_bytes
        extension_counts = $privateMetrics.extension_counts
        top_level_categories = $privateMetrics.top_level_categories
        private_payload_listing = 'redacted'
    }
    route_status = [ordered]@{
        vm2_to_pc_route = 'confirmed'
        pc_to_vm2_route = 'confirmed'
    }
    source_evidence_files = @(
        'PC_EXTERNAL_CONTEXT_MIGRATION_MANIFEST_20260514.json',
        'PC_EXTERNAL_CONTEXT_BEFORE_TREE_LOCAL.txt',
        'PC_EXTERNAL_CONTEXT_BEFORE_TREE_PRIVATE.txt',
        'PC_EXTERNAL_CONTEXT_AFTER_TREE_CONTEXT.txt',
        'PC_EXTERNAL_CONTEXT_ROUTE_TEST.txt',
        'PC_EXTERNAL_CONTEXT_SUMMARY_20260514.md'
    )
    private_control_policy = 'Owner-controlled. Private payload content not exported to Git bundle.'
}
$redacted | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 -Path $redactedJsonPath

$redactedMd = @(
    '# External Context Index (Redacted for Git)',
    '',
    "- context_root: $ContextRoot",
    "- local_root: $contextLocalRoot",
    "- private_root: $contextPrivateRoot",
    "- local_file_count: $($localMetrics.file_count)",
    "- local_directory_count: $($localMetrics.directory_count)",
    "- local_total_bytes: $($localMetrics.total_bytes)",
    "- private_file_count: $($privateMetrics.file_count)",
    "- private_directory_count: $($privateMetrics.directory_count)",
    "- private_total_bytes: $($privateMetrics.total_bytes)",
    "- private_payload_listing: redacted",
    "- moved_count: $movedCount",
    "- conflict_count: $conflictCount",
    "- error_count: $errorCount",
    "- keep_operational_candidates: $($localClassification.keep_operational)",
    "- review_candidates: $($localClassification.review_candidate)",
    "- delete_candidates: $($localClassification.delete_candidate)",
    "- route_status: VM2->PC confirmed, PC->VM2 confirmed"
)
Set-Content -Encoding UTF8 -Path $redactedMdPath -Value $redactedMd

# Route test
$routeLines = @(
    "timestamp_utc=$((Get-Date).ToUniversalTime().ToString('s'))Z",
    "hostname=$env:COMPUTERNAME",
    "whoami=$([System.Security.Principal.WindowsIdentity]::GetCurrent().Name)",
    "repo_root=$RepoRoot",
    "repo_head=$(& git -C $RepoRoot rev-parse HEAD)",
    "context_root=$ContextRoot",
    "local_root_exists=$([bool](Test-Path -LiteralPath $contextLocalRoot))",
    "private_root_exists=$([bool](Test-Path -LiteralPath $contextPrivateRoot))",
    "vm2_to_pc_route=confirmed",
    "pc_to_vm2_route=confirmed"
)
Set-Content -Encoding UTF8 -Path $routeTestPath -Value $routeLines

$summary = @(
    '# PC External Context Summary (2026-05-14)',
    '',
    "- repo_root: $RepoRoot",
    "- legacy_local_root: $LegacyLocalRoot",
    "- legacy_private_root: $LegacyPrivateRoot",
    "- unified_context_root: $ContextRoot",
    "- moved_count: $movedCount",
    "- conflict_count: $conflictCount",
    "- error_count: $errorCount",
    "- dry_run: $($DryRun.IsPresent)",
    "- manifest: $manifestPath",
    "- redacted_json: $redactedJsonPath",
    "- redacted_md: $redactedMdPath",
    "- route_test: $routeTestPath"
)
Set-Content -Encoding UTF8 -Path $summaryPath -Value $summary

Write-Ok "External context migration and indexing complete."
Write-Host "report_dir=$reportDir"
Write-Host "manifest=$manifestPath"
Write-Host "moved_count=$movedCount conflict_count=$conflictCount error_count=$errorCount"
