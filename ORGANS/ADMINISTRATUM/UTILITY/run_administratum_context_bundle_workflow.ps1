param(
    [string]$Root = "E:\IMPERIUM",
    [string]$Target = "FULL_IMPERIUM_SUMMARY",
    [switch]$ForVM2,
    [switch]$IncludePrivateApproved
)

$ErrorActionPreference = "Stop"

$analyzer = Join-Path $Root "TOOLS\administratum_analyze_git_local_context.ps1"
$builder = Join-Path $Root "TOOLS\build_chat_compilation_from_analysis.ps1"
$analysisPath = Join-Path $Root "CURRENT_STATE\ADMINISTRATUM_ANALYZER\RECOMMENDED_CHAT_COMPILATION.json"

$analyzerArgs = @("-Root", $Root, "-Target", $Target)
if ($ForVM2) { $analyzerArgs += "-ForVM2" }

& powershell -ExecutionPolicy Bypass -File $analyzer @analyzerArgs | Out-Null

$taskId = if ($ForVM2 -or $Target -eq "VM2_WORK") { "VM2_CONTEXT" } else { "FULL_IMPERIUM_CONTEXT" }
$builderArgs = @("-Root", $Root, "-AnalysisPath", $analysisPath, "-TaskId", $taskId)
if ($ForVM2) { $builderArgs += "-ForVM2" }
if ($IncludePrivateApproved) { $builderArgs += "-IncludePrivateApproved" }

$zipPath = & powershell -ExecutionPolicy Bypass -File $builder @builderArgs
Write-Output ($zipPath | Select-Object -Last 1)
