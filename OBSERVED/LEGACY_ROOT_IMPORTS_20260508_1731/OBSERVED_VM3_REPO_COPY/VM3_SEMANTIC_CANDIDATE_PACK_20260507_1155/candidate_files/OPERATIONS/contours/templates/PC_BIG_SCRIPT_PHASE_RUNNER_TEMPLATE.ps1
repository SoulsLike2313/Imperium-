param(
    [Parameter(Mandatory=$true)][string]$ConfigPath,
    [Parameter(Mandatory=$true)][string]$LogDir,
    [Parameter(Mandatory=$true)][string]$Phase
)

$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$config = Get-Content -Raw -Path $ConfigPath | ConvertFrom-Json
$stdoutPath = Join-Path $LogDir ("{0}_stdout.log" -f $Phase)
$stderrPath = Join-Path $LogDir ("{0}_stderr.log" -f $Phase)
$exitPath = Join-Path $LogDir ("{0}_exit_code.txt" -f $Phase)
$markerPath = Join-Path $LogDir ("{0}.done" -f $Phase)

try {
    "START_PHASE $Phase" | Out-File -FilePath $stdoutPath -Encoding utf8
    # TODO: call bounded phase action from $config
    "CONFIG_LOADED" | Out-File -FilePath $stdoutPath -Append -Encoding utf8
    "0" | Out-File -FilePath $exitPath -Encoding ascii
    "DONE" | Out-File -FilePath $markerPath -Encoding ascii
    exit 0
}
catch {
    $_ | Out-File -FilePath $stderrPath -Encoding utf8
    "1" | Out-File -FilePath $exitPath -Encoding ascii
    exit 1
}
