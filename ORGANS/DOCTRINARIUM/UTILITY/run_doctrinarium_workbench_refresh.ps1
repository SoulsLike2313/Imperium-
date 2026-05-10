$ErrorActionPreference = "Stop"

$Root = "E:\IMPERIUM"
$Doc = Join-Path $Root "ORGANS\DOCTRINARIUM"
$Reports = Join-Path $Doc "REPORTS"
$Status = Join-Path $Doc "STATUS"
$ManualRun = Join-Path $Root "ARTIFACTS\MANUAL-DOCTRINARIUM-WORKBENCH-REFRESH"

New-Item -ItemType Directory -Force -Path $Reports, $Status, $ManualRun | Out-Null

Write-Host "=== Doctrinarium Workbench Refresh ==="

Write-Host "`n[1/3] Validate all organs..."
python (Join-Path $Doc "SCRIPTS\doctrinarium_validate_all_organs.py") `
  --root $Root `
  --output-json (Join-Path $ManualRun "ALL_ORGANS_GAP_REPORT.json") `
  --output-md (Join-Path $ManualRun "ALL_ORGANS_GAP_REPORT.md") `
  --copy-json (Join-Path $Reports "ALL_ORGANS_GAP_REPORT.json") `
  --copy-md (Join-Path $Reports "ALL_ORGANS_GAP_REPORT.md")

Write-Host "`n[2/3] Validate organ utilities..."
python (Join-Path $Doc "SCRIPTS\doctrinarium_validate_organ_utilities.py") `
  --root $Root `
  --output-json (Join-Path $ManualRun "ORGAN_UTILITY_GAP_REPORT.json") `
  --output-md (Join-Path $ManualRun "ORGAN_UTILITY_GAP_REPORT.md") `
  --copy-json (Join-Path $Reports "ORGAN_UTILITY_GAP_REPORT.json") `
  --copy-md (Join-Path $Reports "ORGAN_UTILITY_GAP_REPORT.md")

Write-Host "`n[3/3] Generate Doctrinarium status report..."
python (Join-Path $Doc "SCRIPTS\doctrinarium_generate_status_report.py") `
  --root $Root `
  --task-artifact-root $ManualRun `
  --output-json (Join-Path $ManualRun "DOCTRINARIUM_STATUS_REPORT.json") `
  --output-md (Join-Path $ManualRun "DOCTRINARIUM_STATUS_REPORT.md") `
  --copy-json (Join-Path $Status "DOCTRINARIUM_STATUS.json") `
  --copy-md (Join-Path $Reports "DOCTRINARIUM_STATUS_REPORT.md")

Write-Host "`n=== DONE ==="
Write-Host "Workbench artifacts:"
Write-Host $ManualRun

Write-Host "`nMain reports:"
Write-Host (Join-Path $Reports "ALL_ORGANS_GAP_REPORT.md")
Write-Host (Join-Path $Reports "ORGAN_UTILITY_GAP_REPORT.md")
Write-Host (Join-Path $Reports "DOCTRINARIUM_STATUS_REPORT.md")
Write-Host (Join-Path $Status "DOCTRINARIUM_STATUS.json")
