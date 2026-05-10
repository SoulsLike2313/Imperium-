param(
    [string]$Root = "E:\IMPERIUM",
    [string]$Target = "FULL_IMPERIUM_SUMMARY",
    [switch]$ForVM2,
    [switch]$IncludePrivateApproved,
    [switch]$AnalyzeOnly,
    [switch]$BuildBundle
)

$ErrorActionPreference = "Stop"

$analyzer = Join-Path $Root "TOOLS\administratum_analyze_git_local_context.ps1"
$builder = Join-Path $Root "TOOLS\build_chat_compilation_from_analysis.ps1"
$recommendedPath = Join-Path $Root "CURRENT_STATE\ADMINISTRATUM_ANALYZER\RECOMMENDED_CHAT_COMPILATION.json"
$analysisJsonPath = Join-Path $Root "CURRENT_STATE\ADMINISTRATUM_ANALYZER\GIT_LOCAL_ANALYSIS.json"
$ownerNextActionPath = Join-Path $Root "CURRENT_STATE\ADMINISTRATUM_ANALYZER\OWNER_NEXT_ACTION.md"

$analyzerArgs = @("-Root", $Root, "-Target", $Target, "-PostPushRealityCheck")
if ($ForVM2) { $analyzerArgs += "-ForVM2" }

& powershell -ExecutionPolicy Bypass -File $analyzer @analyzerArgs | Out-Null

if (Test-Path -LiteralPath $ownerNextActionPath) {
    Write-Output "OWNER_NEXT_ACTION:"
    Get-Content -LiteralPath $ownerNextActionPath | Write-Output
}

if ($AnalyzeOnly -and -not $BuildBundle) {
    Write-Output "AnalyzeOnly completed. Bundle build skipped."
    return
}

$shouldBuild = $BuildBundle
if (-not $AnalyzeOnly -and -not $BuildBundle) {
    $shouldBuild = $true
}

if ($shouldBuild) {
    $taskId = if ($ForVM2 -or $Target -eq "VM2_WORK") { "VM2_CONTEXT" } else { "FULL_IMPERIUM_CONTEXT" }
    $builderArgs = @("-Root", $Root, "-AnalysisPath", $recommendedPath, "-TaskId", $taskId)
    if ($ForVM2) { $builderArgs += "-ForVM2" }
    if ($IncludePrivateApproved) { $builderArgs += "-IncludePrivateApproved" }

    $zip = & powershell -ExecutionPolicy Bypass -File $builder @builderArgs
    Write-Output ($zip | Select-Object -Last 1)
}
