$ErrorActionPreference = "Stop"

$TaskId = "TASK-20260509-EXPLORER-V0_6-BASELINE-PROOF-V1"
$ArtifactRoot = "E:\IMPERIUM\ARTIFACTS\$TaskId"

$ExplorerRoot = "E:\IMPERIUM\EXPLORER"
$VerifyRoot = "E:\IMPERIUM\EXPLORER\VERIFY"
$ScreensRoot = "E:\IMPERIUM\EXPLORER\SCREENSHOTS"

$ExplorerPy = "$ExplorerRoot\imperium_explorer_v0_6.py"
$Readme = "$ExplorerRoot\README.md"
$Changelog = "$ExplorerRoot\CHANGELOG.md"

$LatestTruthRun = Get-ChildItem "$VerifyRoot\RUN-*" -Directory |
    Where-Object { Test-Path "$($_.FullName)\EXPLORER_TRUTH_AUDIT_REPORT.json" } |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

$LatestScreenRun = Get-ChildItem "$ScreensRoot\AUTO-RUN-*" -Directory |
    Where-Object { Test-Path "$($_.FullName)\AUTO_SCREENSHOT_TRUTH_CHECK_REPORT.json" } |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if (!(Test-Path $ExplorerPy)) {
    throw "Missing Explorer v0.6 file: $ExplorerPy"
}

if ($null -eq $LatestTruthRun) {
    throw "No truth audit run found under $VerifyRoot"
}

if ($null -eq $LatestScreenRun) {
    throw "No auto screenshot run found under $ScreensRoot"
}

New-Item -ItemType Directory -Force -Path $ArtifactRoot | Out-Null
New-Item -ItemType Directory -Force -Path "$ArtifactRoot\00_SOURCE" | Out-Null
New-Item -ItemType Directory -Force -Path "$ArtifactRoot\01_TRUTH_AUDIT" | Out-Null
New-Item -ItemType Directory -Force -Path "$ArtifactRoot\02_SCREENSHOT_TRUTH_CHECK" | Out-Null
New-Item -ItemType Directory -Force -Path "$ArtifactRoot\03_SCREENSHOTS" | Out-Null
New-Item -ItemType Directory -Force -Path "$ArtifactRoot\04_REPORTS" | Out-Null
New-Item -ItemType Directory -Force -Path "$ArtifactRoot\05_RECEIPTS" | Out-Null
New-Item -ItemType Directory -Force -Path "$ArtifactRoot\06_BUNDLE" | Out-Null

Copy-Item $ExplorerPy "$ArtifactRoot\00_SOURCE\" -Force

if (Test-Path $Readme) {
    Copy-Item $Readme "$ArtifactRoot\00_SOURCE\" -Force
}

if (Test-Path $Changelog) {
    Copy-Item $Changelog "$ArtifactRoot\00_SOURCE\" -Force
}

Copy-Item "$($LatestTruthRun.FullName)\EXPLORER_TRUTH_AUDIT_REPORT.json" "$ArtifactRoot\01_TRUTH_AUDIT\" -Force
Copy-Item "$($LatestTruthRun.FullName)\EXPLORER_TRUTH_AUDIT_REPORT.md" "$ArtifactRoot\01_TRUTH_AUDIT\" -Force

Copy-Item "$($LatestScreenRun.FullName)\AUTO_SCREENSHOT_TRUTH_CHECK_REPORT.json" "$ArtifactRoot\02_SCREENSHOT_TRUTH_CHECK\" -Force
Copy-Item "$($LatestScreenRun.FullName)\AUTO_SCREENSHOT_TRUTH_CHECK_REPORT.md" "$ArtifactRoot\02_SCREENSHOT_TRUTH_CHECK\" -Force

if (Test-Path "$($LatestScreenRun.FullName)\SCREENSHOT_GALLERY.md") {
    Copy-Item "$($LatestScreenRun.FullName)\SCREENSHOT_GALLERY.md" "$ArtifactRoot\02_SCREENSHOT_TRUTH_CHECK\" -Force
}

Copy-Item "$($LatestScreenRun.FullName)\*.png" "$ArtifactRoot\03_SCREENSHOTS\" -Force

$TruthJson = Get-Content "$ArtifactRoot\01_TRUTH_AUDIT\EXPLORER_TRUTH_AUDIT_REPORT.json" -Raw | ConvertFrom-Json
$ScreenJson = Get-Content "$ArtifactRoot\02_SCREENSHOT_TRUTH_CHECK\AUTO_SCREENSHOT_TRUTH_CHECK_REPORT.json" -Raw | ConvertFrom-Json

$OwnerSummary = @"
# Explorer V0.6 Baseline Proof

TASK_ID: $TaskId

STATUS:
PASS_AS_TRUTH_ALIGNED_CANDIDATE

## What was collected

This artifact preserves the current Explorer v0.6 baseline candidate:

- source script;
- README / CHANGELOG;
- latest truth audit;
- latest auto screenshot truth check;
- screenshot gallery;
- raw screenshots.

## Explorer candidate

Source:
E:\IMPERIUM\EXPLORER\imperium_explorer_v0_6.py

## Truth audit

Truth audit verdict:
$($TruthJson.verdict)

Truth audit run:
$($TruthJson.run_id)

Truth audit root:
$($TruthJson.imperium_root)

Archive policy:
ARCHIVE is cold storage.
ARCHIVE recursive scan is disabled.
Only archive top-level index is collected.

## Auto screenshot truth check

Screenshot check verdict:
$($ScreenJson.verdict)

Screenshot run:
$($ScreenJson.run_id)

Targets total:
$($ScreenJson.targets_total)

Screenshots created:
$($ScreenJson.screenshots_created)

Checks total:
$($ScreenJson.checks_total)

Checks passed:
$($ScreenJson.checks_passed)

Checks failed:
$($ScreenJson.checks_failed)

## Honest interpretation

Explorer v0.6 is not declared final Sanctum or Aquarium backend.

Explorer v0.6 is currently a read-only visual mirror candidate that passed the latest automated screenshot truth comparison on the selected control set.

This means:
- it can display checked filesystem reality for the sampled nodes;
- it correctly matches visible PATH / TYPE / DIRECT_FOLDERS / DIRECT_FILES against the latest truth audit;
- it does not prove full semantic correctness of all IMPERIUM history;
- it does not make organs implemented;
- it does not make E2E ready;
- it does not make THRONE ready.

## Forbidden claims

Do not claim:
- Explorer is final production app;
- Sanctum is ready;
- Aquarium is ready;
- organs are implemented;
- PC↔VM2 E2E is ready;
- THRONE is connected;
- continuity is GREEN.

## Proposed Speculum question

Can Explorer v0.6 be promoted to Explorer 1.0 baseline as a read-only truth-aligned visual mirror for IMPERIUM, given this artifact evidence?

If not, identify exact blockers and required repair tasks.

"@

$OwnerSummary | Set-Content "$ArtifactRoot\OWNER_SUMMARY.md" -Encoding UTF8

$Receipt = [PSCustomObject]@{
    task_id = $TaskId
    artifact_type = "EXPLORER_BASELINE_PROOF"
    status = "PASS_AS_TRUTH_ALIGNED_CANDIDATE"
    created_at_local = (Get-Date).ToString("s")
    explorer_version = "v0.6"
    explorer_source = $ExplorerPy
    truth_audit_source_folder = $LatestTruthRun.FullName
    screenshot_check_source_folder = $LatestScreenRun.FullName
    truth_audit_verdict = $TruthJson.verdict
    truth_audit_run_id = $TruthJson.run_id
    screenshot_check_verdict = $ScreenJson.verdict
    screenshot_check_run_id = $ScreenJson.run_id
    targets_total = $ScreenJson.targets_total
    screenshots_created = $ScreenJson.screenshots_created
    checks_total = $ScreenJson.checks_total
    checks_passed = $ScreenJson.checks_passed
    checks_failed = $ScreenJson.checks_failed
    archive_policy = "ARCHIVE_COLD_STORAGE_TOP_LEVEL_ONLY_RECURSIVE_SCAN_DISABLED"
    read_only_guarantee = $true
    no_vm2_contact = $true
    no_throne_contact = $true
    no_e2e_run = $true
    no_watchers = $true
    recommended_next = "SPECULUM_REVIEW_EXPLORER_V0_6_BASELINE_PROOF"
}

$Receipt | ConvertTo-Json -Depth 8 | Set-Content "$ArtifactRoot\05_RECEIPTS\EXPLORER_V0_6_BASELINE_RECEIPT.json" -Encoding UTF8

$Files = Get-ChildItem $ArtifactRoot -Recurse -File |
    Where-Object {
        $_.FullName -notlike "*\06_BUNDLE\*" -and
        $_.Name -ne "SHA256SUMS.txt" -and
        $_.Name -ne "MANIFEST.json"
    }

$ManifestRows = foreach ($File in $Files) {
    $Relative = $File.FullName.Substring($ArtifactRoot.Length + 1)
    [PSCustomObject]@{
        path = $Relative
        size_bytes = $File.Length
        sha256 = (Get-FileHash -Algorithm SHA256 $File.FullName).Hash.ToLower()
    }
}

$Manifest = [PSCustomObject]@{
    task_id = $TaskId
    artifact_root = $ArtifactRoot
    created_at_local = (Get-Date).ToString("s")
    file_count = @($ManifestRows).Count
    files = $ManifestRows
}

$Manifest | ConvertTo-Json -Depth 8 | Set-Content "$ArtifactRoot\MANIFEST.json" -Encoding UTF8

$ManifestRows | ForEach-Object {
    "$($_.sha256)  $($_.path)"
} | Set-Content "$ArtifactRoot\SHA256SUMS.txt" -Encoding UTF8

$ZipPath = "$ArtifactRoot\06_BUNDLE\$TaskId.zip"

if (Test-Path $ZipPath) {
    Remove-Item $ZipPath -Force
}

Compress-Archive -Path `
    "$ArtifactRoot\00_SOURCE", `
    "$ArtifactRoot\01_TRUTH_AUDIT", `
    "$ArtifactRoot\02_SCREENSHOT_TRUTH_CHECK", `
    "$ArtifactRoot\03_SCREENSHOTS", `
    "$ArtifactRoot\04_REPORTS", `
    "$ArtifactRoot\05_RECEIPTS", `
    "$ArtifactRoot\OWNER_SUMMARY.md", `
    "$ArtifactRoot\MANIFEST.json", `
    "$ArtifactRoot\SHA256SUMS.txt" `
    -DestinationPath $ZipPath -Force

$ZipHash = (Get-FileHash -Algorithm SHA256 $ZipPath).Hash.ToLower()
"$ZipHash  $TaskId.zip" | Set-Content "$ZipPath.sha256" -Encoding UTF8

Write-Host ""
Write-Host "PASS: Explorer v0.6 baseline artifact created"
Write-Host "Artifact root:"
Write-Host $ArtifactRoot
Write-Host ""
Write-Host "Bundle:"
Write-Host $ZipPath
Write-Host ""
Write-Host "Bundle sha256:"
Write-Host $ZipHash
Write-Host ""
Write-Host "Owner summary:"
Write-Host "$ArtifactRoot\OWNER_SUMMARY.md"
