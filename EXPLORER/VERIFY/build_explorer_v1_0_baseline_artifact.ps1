$ErrorActionPreference = "Stop"

$TaskId = "TASK-20260509-EXPLORER-V1_0-READONLY-BASELINE-FREEZE-PROOF-V1"

$ImperiumRoot = "E:\IMPERIUM"
$ExplorerRoot = "E:\IMPERIUM\EXPLORER"
$VerifyRoot = "E:\IMPERIUM\EXPLORER\VERIFY"
$ScreensRoot = "E:\IMPERIUM\EXPLORER\SCREENSHOTS"
$PolicyRoot = "E:\IMPERIUM\EXPLORER\POLICIES"

$ArtifactRoot = "E:\IMPERIUM\ARTIFACTS\$TaskId"

$ExplorerV10 = "$ExplorerRoot\imperium_explorer_v1_0.py"
$Readme = "$ExplorerRoot\README.md"
$Changelog = "$ExplorerRoot\CHANGELOG.md"

$StaticReportJson = "$VerifyRoot\EXPLORER_V1_0_STATIC_READ_ONLY_SCAN_REPORT.json"
$StaticReportMd = "$VerifyRoot\EXPLORER_V1_0_STATIC_READ_ONLY_SCAN_REPORT.md"

$TruthRun = Get-ChildItem "$VerifyRoot\RUN-V1_0-*" -Directory |
    Where-Object { Test-Path "$($_.FullName)\EXPLORER_TRUTH_AUDIT_REPORT.json" } |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

$AutoRun = Get-ChildItem "$ScreensRoot\AUTO-RUN-*" -Directory |
    Where-Object { Test-Path "$($_.FullName)\AUTO_SCREENSHOT_TRUTH_CHECK_REPORT.json" } |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if (!(Test-Path $ExplorerV10)) { throw "Missing Explorer v1.0: $ExplorerV10" }
if (!(Test-Path $StaticReportJson)) { throw "Missing static report: $StaticReportJson" }
if ($null -eq $TruthRun) { throw "Missing latest v1.0 truth audit run" }
if ($null -eq $AutoRun) { throw "Missing latest v1.0 autoscreenshot run" }

$Static = Get-Content $StaticReportJson -Raw | ConvertFrom-Json
$Truth = Get-Content "$($TruthRun.FullName)\EXPLORER_TRUTH_AUDIT_REPORT.json" -Raw | ConvertFrom-Json
$Auto = Get-Content "$($AutoRun.FullName)\AUTO_SCREENSHOT_TRUTH_CHECK_REPORT.json" -Raw | ConvertFrom-Json

$StaticPass = $Static.verdict -eq "PASS_STATIC_READ_ONLY_SCAN"
$TruthPass = $Truth.verdict -eq "PASS_TRUTH_SNAPSHOT_READY_FOR_SCREENSHOT_COMPARE"
$AutoPass = ($Auto.verdict -eq "PASS_AUTOSCREENSHOT_TRUTH_COMPARE") -and ([int]$Auto.checks_failed -eq 0)

if (!($StaticPass -and $TruthPass -and $AutoPass)) {
    throw "BLOCKED: proof chain is not fully PASS"
}

New-Item -ItemType Directory -Force -Path $ArtifactRoot | Out-Null
New-Item -ItemType Directory -Force -Path "$ArtifactRoot\00_SOURCE" | Out-Null
New-Item -ItemType Directory -Force -Path "$ArtifactRoot\01_POLICIES" | Out-Null
New-Item -ItemType Directory -Force -Path "$ArtifactRoot\02_PROOF_TOOLS" | Out-Null
New-Item -ItemType Directory -Force -Path "$ArtifactRoot\03_STATIC_READONLY_SCAN" | Out-Null
New-Item -ItemType Directory -Force -Path "$ArtifactRoot\04_TRUTH_AUDIT" | Out-Null
New-Item -ItemType Directory -Force -Path "$ArtifactRoot\05_SCREENSHOT_TRUTH_CHECK" | Out-Null
New-Item -ItemType Directory -Force -Path "$ArtifactRoot\06_SCREENSHOTS" | Out-Null
New-Item -ItemType Directory -Force -Path "$ArtifactRoot\07_RECEIPTS" | Out-Null
New-Item -ItemType Directory -Force -Path "$ArtifactRoot\08_BUNDLE" | Out-Null

Copy-Item $ExplorerV10 "$ArtifactRoot\00_SOURCE\" -Force
if (Test-Path $Readme) { Copy-Item $Readme "$ArtifactRoot\00_SOURCE\" -Force }
if (Test-Path $Changelog) { Copy-Item $Changelog "$ArtifactRoot\00_SOURCE\" -Force }

Copy-Item "$PolicyRoot\EXPLORER_BASELINE_POLICY.json" "$ArtifactRoot\01_POLICIES\" -Force
Copy-Item "$PolicyRoot\EXPLORER_BASELINE_POLICY.md" "$ArtifactRoot\01_POLICIES\" -Force
Copy-Item "$PolicyRoot\EXPLORER_ARCHIVE_POLICY.json" "$ArtifactRoot\01_POLICIES\" -Force
Copy-Item "$PolicyRoot\EXPLORER_ARCHIVE_POLICY.md" "$ArtifactRoot\01_POLICIES\" -Force

Copy-Item "$VerifyRoot\static_readonly_source_scan_v1_0.py" "$ArtifactRoot\02_PROOF_TOOLS\" -Force
Copy-Item "$VerifyRoot\explorer_truth_audit_v1_0.py" "$ArtifactRoot\02_PROOF_TOOLS\" -Force
Copy-Item "$VerifyRoot\auto_explorer_screenshot_truth_check_v1_0.py" "$ArtifactRoot\02_PROOF_TOOLS\" -Force
if (Test-Path "$VerifyRoot\run_explorer_v1_0_full_proof_check.ps1") {
    Copy-Item "$VerifyRoot\run_explorer_v1_0_full_proof_check.ps1" "$ArtifactRoot\02_PROOF_TOOLS\" -Force
}

Copy-Item $StaticReportJson "$ArtifactRoot\03_STATIC_READONLY_SCAN\" -Force
Copy-Item $StaticReportMd "$ArtifactRoot\03_STATIC_READONLY_SCAN\" -Force

Copy-Item "$($TruthRun.FullName)\EXPLORER_TRUTH_AUDIT_REPORT.json" "$ArtifactRoot\04_TRUTH_AUDIT\" -Force
Copy-Item "$($TruthRun.FullName)\EXPLORER_TRUTH_AUDIT_REPORT.md" "$ArtifactRoot\04_TRUTH_AUDIT\" -Force

Copy-Item "$($AutoRun.FullName)\AUTO_SCREENSHOT_TRUTH_CHECK_REPORT.json" "$ArtifactRoot\05_SCREENSHOT_TRUTH_CHECK\" -Force
Copy-Item "$($AutoRun.FullName)\AUTO_SCREENSHOT_TRUTH_CHECK_REPORT.md" "$ArtifactRoot\05_SCREENSHOT_TRUTH_CHECK\" -Force
if (Test-Path "$($AutoRun.FullName)\SCREENSHOT_GALLERY.md") {
    Copy-Item "$($AutoRun.FullName)\SCREENSHOT_GALLERY.md" "$ArtifactRoot\05_SCREENSHOT_TRUTH_CHECK\" -Force
}

Copy-Item "$($AutoRun.FullName)\*.png" "$ArtifactRoot\06_SCREENSHOTS\" -Force

$Receipt = [PSCustomObject]@{
    task_id = $TaskId
    artifact_type = "EXPLORER_V1_0_READONLY_BASELINE_FREEZE_PROOF"
    status = "PASS_EXPLORER_V1_0_READONLY_VISUAL_MIRROR_BASELINE"
    created_at_local = (Get-Date).ToString("s")

    explorer_version = "1.0"
    explorer_source = "E:\IMPERIUM\EXPLORER\imperium_explorer_v1_0.py"

    static_readonly_scan = [PSCustomObject]@{
        verdict = $Static.verdict
        pass = $StaticPass
    }

    truth_audit = [PSCustomObject]@{
        verdict = $Truth.verdict
        pass = $TruthPass
        run_id = $Truth.run_id
        total_nodes_scanned_excluding_archive_contents = $Truth.tree_scan.total_nodes_scanned_excluding_archive_contents
        archive_roots_skipped_recursive_count = $Truth.tree_scan.archive_roots_skipped_recursive_count
        task_folders_count = $Truth.tree_scan.task_folders_count
        receipts_count = $Truth.tree_scan.receipts_count
        manifests_count = $Truth.tree_scan.manifests_count
        bundles_count = $Truth.tree_scan.bundles_count
    }

    autoscreenshot_truth_check = [PSCustomObject]@{
        verdict = $Auto.verdict
        pass = $AutoPass
        run_id = $Auto.run_id
        targets_total = $Auto.targets_total
        screenshots_created = $Auto.screenshots_created
        checks_total = $Auto.checks_total
        checks_passed = $Auto.checks_passed
        checks_failed = $Auto.checks_failed
    }

    baseline_definition = "Explorer 1.0 is a local read-only visual mirror of E:\IMPERIUM. It is not the source of truth."
    source_of_truth = @("filesystem", "manifests", "SHA256SUMS", "receipts", "truth audits", "screenshot truth checks", "Speculum reviews", "Owner decisions")

    allowed_ui_side_effects = @("clipboard_copy_path", "open_path_in_windows_explorer")

    forbidden_claims = @(
        "Sanctum ready",
        "Aquarium ready",
        "organs implemented",
        "PC-VM2 E2E ready",
        "THRONE connected",
        "CONTINUITY_GREEN",
        "Explorer proves all historical semantics"
    )

    forbidden_actions = @(
        "write_files",
        "edit_files",
        "delete_files",
        "move_files",
        "vm2_contact",
        "throne_contact",
        "e2e_run",
        "watchers",
        "background_automation",
        "continuity_pack_execution"
    )

    recommended_next = "SPECULUM_REVIEW_EXPLORER_V1_0_BASELINE_FREEZE_PROOF"
}

$Receipt | ConvertTo-Json -Depth 12 | Set-Content "$ArtifactRoot\07_RECEIPTS\EXPLORER_V1_0_BASELINE_RECEIPT.json" -Encoding UTF8

$OwnerSummary = @"
# Explorer V1.0 Read-Only Baseline Freeze Proof

TASK_ID: $TaskId

STATUS:
PASS_EXPLORER_V1_0_READONLY_VISUAL_MIRROR_BASELINE

## What this proves

Explorer v1.0 passed the full local proof chain:

- static read-only source scan: $($Static.verdict)
- truth audit: $($Truth.verdict)
- auto screenshot truth check: $($Auto.verdict)

Auto screenshot truth check:
- targets_total: $($Auto.targets_total)
- screenshots_created: $($Auto.screenshots_created)
- checks_total: $($Auto.checks_total)
- checks_passed: $($Auto.checks_passed)
- checks_failed: $($Auto.checks_failed)

## What Explorer 1.0 is

Explorer 1.0 is a local Python/Tkinter read-only visual mirror of E:\IMPERIUM.

It can show:
- filesystem tree;
- node type;
- path;
- direct folder/file counts;
- direct markers;
- small previews;
- visual helix panel;
- Copy Path;
- Open in Explorer.

## What Explorer 1.0 is not

Explorer 1.0 is not:
- Sanctum;
- Aquarium;
- organ implementation;
- PC↔VM2 E2E proof;
- THRONE connection;
- continuity GREEN;
- source of truth;
- full semantic proof of all IMPERIUM history.

## Archive policy

ARCHIVE is cold storage.
ARCHIVE recursive scan is disabled.
ARCHIVE is not active task history.

## Next proposed step

Give this artifact to Logos-Speculum for hard review.

Question:
Can this be accepted as Explorer 1.0 READ_ONLY_VISUAL_MIRROR_BASELINE?

"@

$OwnerSummary | Set-Content "$ArtifactRoot\OWNER_SUMMARY.md" -Encoding UTF8

$Files = Get-ChildItem $ArtifactRoot -Recurse -File |
    Where-Object {
        $_.FullName -notlike "*\08_BUNDLE\*" -and
        $_.Name -ne "MANIFEST.json" -and
        $_.Name -ne "SHA256SUMS.txt"
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

$Manifest | ConvertTo-Json -Depth 12 | Set-Content "$ArtifactRoot\MANIFEST.json" -Encoding UTF8

$ManifestRows | ForEach-Object {
    "$($_.sha256)  $($_.path)"
} | Set-Content "$ArtifactRoot\SHA256SUMS.txt" -Encoding UTF8

$ZipPath = "$ArtifactRoot\08_BUNDLE\$TaskId.zip"

if (Test-Path $ZipPath) {
    Remove-Item $ZipPath -Force
}

$CompressPaths = @(
    "$ArtifactRoot\00_SOURCE",
    "$ArtifactRoot\01_POLICIES",
    "$ArtifactRoot\02_PROOF_TOOLS",
    "$ArtifactRoot\03_STATIC_READONLY_SCAN",
    "$ArtifactRoot\04_TRUTH_AUDIT",
    "$ArtifactRoot\05_SCREENSHOT_TRUTH_CHECK",
    "$ArtifactRoot\06_SCREENSHOTS",
    "$ArtifactRoot\07_RECEIPTS",
    "$ArtifactRoot\OWNER_SUMMARY.md",
    "$ArtifactRoot\MANIFEST.json",
    "$ArtifactRoot\SHA256SUMS.txt"
)

Compress-Archive -Path $CompressPaths -DestinationPath $ZipPath -Force

$ZipHash = (Get-FileHash -Algorithm SHA256 $ZipPath).Hash.ToLower()
"$ZipHash  $TaskId.zip" | Set-Content "$ZipPath.sha256" -Encoding UTF8

Write-Host ""
Write-Host "PASS: Explorer v1.0 baseline artifact created"
Write-Host ""
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
