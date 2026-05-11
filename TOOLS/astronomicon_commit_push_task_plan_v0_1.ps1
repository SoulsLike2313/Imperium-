param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("COMMIT", "PUSH")]
    [string]$Mode,

    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,

    [string[]]$IncludePaths = @(),

    [string]$CommitMessage = "",

    [string]$ReceiptPath = ""
)

$ErrorActionPreference = "Stop"
. "E:\IMPERIUM\TOOLS\astronomicon_pipeline_common_v0_2.ps1"

if (-not (Test-Path -LiteralPath $RepoRoot)) {
    throw "RepoRoot not found: $RepoRoot"
}

$repoRootAbs = (Resolve-Path -LiteralPath $RepoRoot).Path

function Invoke-Git {
    param(
        [Parameter(Mandatory = $true)][string[]]$Args
    )

    $output = & git -C $repoRootAbs @Args 2>&1
    $exitCode = $LASTEXITCODE
    return [ordered]@{
        exit_code = $exitCode
        output = ($output | Out-String).Trim()
    }
}

function Get-RepoRelativePath {
    param([Parameter(Mandatory = $true)][string]$Path)

    $abs = [System.IO.Path]::GetFullPath($Path)
    if ($abs.StartsWith($repoRootAbs, [System.StringComparison]::OrdinalIgnoreCase)) {
        $rel = $abs.Substring($repoRootAbs.Length).TrimStart('\')
        return $rel.Replace('\', '/')
    }
    throw "Path is outside repo root and cannot be staged safely: $Path"
}

function Collect-IncludeFiles {
    param([string[]]$Paths)

    $collected = New-Object System.Collections.Generic.List[string]
    foreach ($path in $Paths) {
        if ([string]::IsNullOrWhiteSpace($path)) { continue }

        $full = [System.IO.Path]::GetFullPath($path)
        if (-not (Test-Path -LiteralPath $full)) {
            throw "Include path not found: $path"
        }

        if ((Get-Item -LiteralPath $full).PSIsContainer) {
            Get-ChildItem -LiteralPath $full -Recurse -File | ForEach-Object {
                $collected.Add((Get-RepoRelativePath -Path $_.FullName))
            }
        }
        else {
            $collected.Add((Get-RepoRelativePath -Path $full))
        }
    }

    return @($collected | Sort-Object -Unique)
}

$receipt = [ordered]@{
    schema_version = "ASTRONOMICON_SAFE_COMMIT_PUSH_RECEIPT_V0_1"
    mode = $Mode
    repo_root = $repoRootAbs
    include_paths = $IncludePaths
    status = "UNKNOWN"
    generated_at = (Get-Date).ToString("o")
}

try {
    if ($Mode -eq "COMMIT") {
        if ([string]::IsNullOrWhiteSpace($CommitMessage)) {
            throw "CommitMessage is required in COMMIT mode."
        }
        if ($IncludePaths.Count -eq 0) {
            throw "IncludePaths cannot be empty in COMMIT mode."
        }

        $filesToStage = Collect-IncludeFiles -Paths $IncludePaths
        if ($filesToStage.Count -eq 0) {
            throw "No files resolved from IncludePaths."
        }

        $suspiciousCurrent = Get-SuspiciousPathMatches -Paths $filesToStage
        if ($suspiciousCurrent.Count -gt 0) {
            $receipt.status = "BLOCKED_SUSPICIOUS_CURRENT_PATHS"
            $receipt.suspicious_current_paths = $suspiciousCurrent
            throw "Suspicious current paths detected in include set. Commit blocked."
        }

        $diffCachedNameOnly = Invoke-Git -Args @("diff", "--cached", "--name-only")
        if ($diffCachedNameOnly.exit_code -ne 0) {
            throw "git diff --cached failed: $($diffCachedNameOnly.output)"
        }
        $alreadyStaged = @($diffCachedNameOnly.output -split "`r?`n" | Where-Object { $_.Trim() -ne "" })
        $suspiciousStagedBefore = Get-SuspiciousPathMatches -Paths $alreadyStaged
        if ($suspiciousStagedBefore.Count -gt 0) {
            $receipt.status = "BLOCKED_SUSPICIOUS_STAGED_PATHS_BEFORE"
            $receipt.suspicious_staged_paths_before = $suspiciousStagedBefore
            throw "Suspicious paths already staged before commit. Commit blocked."
        }

        $addArgs = @("add", "--")
        $addArgs += $filesToStage
        $addResult = Invoke-Git -Args $addArgs
        if ($addResult.exit_code -ne 0) {
            throw "git add failed: $($addResult.output)"
        }

        $diffCachedAfter = Invoke-Git -Args @("diff", "--cached", "--name-only")
        if ($diffCachedAfter.exit_code -ne 0) {
            throw "git diff --cached failed: $($diffCachedAfter.output)"
        }
        $stagedAfter = @($diffCachedAfter.output -split "`r?`n" | Where-Object { $_.Trim() -ne "" })
        if ($stagedAfter.Count -eq 0) {
            throw "No staged files after scoped git add."
        }

        $suspiciousStagedAfter = Get-SuspiciousPathMatches -Paths $stagedAfter
        if ($suspiciousStagedAfter.Count -gt 0) {
            $receipt.status = "BLOCKED_SUSPICIOUS_STAGED_PATHS_AFTER"
            $receipt.suspicious_staged_paths_after = $suspiciousStagedAfter
            throw "Suspicious staged paths detected after staging. Commit blocked."
        }

        $commitResult = Invoke-Git -Args @("commit", "-m", $CommitMessage)
        if ($commitResult.exit_code -ne 0) {
            throw "git commit failed: $($commitResult.output)"
        }

        $headResult = Invoke-Git -Args @("rev-parse", "HEAD")
        if ($headResult.exit_code -ne 0) {
            throw "git rev-parse HEAD failed: $($headResult.output)"
        }

        $receipt.status = "COMMIT_CREATED"
        $receipt.staged_file_count = $stagedAfter.Count
        $receipt.staged_files = $stagedAfter
        $receipt.commit_output = $commitResult.output
        $receipt.commit_hash = $headResult.output
    }
    else {
        $pushResult = Invoke-Git -Args @("push", "origin", "master")
        if ($pushResult.exit_code -ne 0) {
            throw "git push failed: $($pushResult.output)"
        }

        $localHead = Invoke-Git -Args @("rev-parse", "HEAD")
        $originHead = Invoke-Git -Args @("rev-parse", "origin/master")
        $remoteHead = Invoke-Git -Args @("ls-remote", "origin", "refs/heads/master")

        if ($localHead.exit_code -ne 0 -or $originHead.exit_code -ne 0 -or $remoteHead.exit_code -ne 0) {
            throw "HEAD verification commands failed."
        }

        $remoteHash = ($remoteHead.output -split "\s+")[0].Trim()
        $localHash = $localHead.output.Trim()
        $originHash = $originHead.output.Trim()
        $allMatch = ($localHash -eq $originHash -and $originHash -eq $remoteHash)

        $receipt.status = $(if ($allMatch) { "PUSH_VERIFIED" } else { "PUSH_MISMATCH" })
        $receipt.push_output = $pushResult.output
        $receipt.local_head = $localHash
        $receipt.origin_master_head = $originHash
        $receipt.remote_master_head = $remoteHash

        if (-not $allMatch) {
            throw "HEAD mismatch after push. local=$localHash origin=$originHash remote=$remoteHash"
        }
    }
}
catch {
    if ($receipt.status -eq "UNKNOWN") {
        $receipt.status = "FAIL"
    }
    $receipt.error = $_.Exception.Message
    if (-not [string]::IsNullOrWhiteSpace($ReceiptPath)) {
        Write-JsonFile -Path $ReceiptPath -Object $receipt -Depth 40
    }
    throw
}

if (-not [string]::IsNullOrWhiteSpace($ReceiptPath)) {
    Write-JsonFile -Path $ReceiptPath -Object $receipt -Depth 40
}

Write-Host ($receipt | ConvertTo-Json -Depth 40)
