<#
.SYNOPSIS
    IMPERIUM distributed contour SSH capability check.

.DESCRIPTION
    Default behavior is non-destructive dry-run.
    Reports MANUAL_CONFIRMATION_REQUIRED unless real SSH probe succeeds.

.PARAMETER HostName
    Target host or IP.

.PARAMETER Port
    SSH port. Default 22.

.PARAMETER User
    SSH user.

.PARAMETER KeyPath
    Optional path to private key.

.PARAMETER DryRun
    Run without network probe. Default true unless explicitly disabled.

.PARAMETER JsonOut
    Optional path for JSON receipt output.
#>

param(
    [string]$HostName = "",
    [int]$Port = 22,
    [string]$User = "",
    [string]$KeyPath = "",
    [switch]$DryRun,
    [string]$JsonOut = ""
)

$effectiveDryRun = $true
if ($PSBoundParameters.ContainsKey("DryRun")) {
    $effectiveDryRun = $DryRun.IsPresent
}

$timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$result = [ordered]@{
    check_id = "SSH_CAPABILITY_CHECK_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    timestamp = $timestamp
    status = "UNKNOWN"
    parameters = [ordered]@{
        host_name = $HostName
        port = $Port
        user = $User
        key_path = $KeyPath
        dry_run = $effectiveDryRun
    }
    checks = @()
    manual_confirmation_required = @()
    notes = @()
}

function Add-Check {
    param([string]$Name, [string]$Status, [string]$Message)
    $script:result.checks += [ordered]@{
        name = $Name
        status = $Status
        message = $Message
    }
}

$sshCmd = Get-Command ssh -ErrorAction SilentlyContinue
if ($null -eq $sshCmd) {
    Add-Check -Name "ssh_client" -Status "FAIL" -Message "ssh command not found"
    $result.status = "BLOCKED"
    $result.notes += "Install OpenSSH client to run real contour verification."
} else {
    Add-Check -Name "ssh_client" -Status "PASS" -Message "ssh command found: $($sshCmd.Source)"
}

if ([string]::IsNullOrWhiteSpace($HostName) -or [string]::IsNullOrWhiteSpace($User)) {
    Add-Check -Name "connection_profile" -Status "MANUAL_CONFIRMATION_REQUIRED" -Message "HostName and User are required for real probe"
    $result.manual_confirmation_required += "Provide -HostName and -User"
}

if (-not [string]::IsNullOrWhiteSpace($KeyPath)) {
    if (Test-Path -LiteralPath $KeyPath) {
        Add-Check -Name "key_path" -Status "PASS" -Message "key file exists"
    } else {
        Add-Check -Name "key_path" -Status "MANUAL_CONFIRMATION_REQUIRED" -Message "key path does not exist"
        $result.manual_confirmation_required += "Provide valid -KeyPath"
    }
} else {
    Add-Check -Name "key_path" -Status "MANUAL_CONFIRMATION_REQUIRED" -Message "KeyPath not provided"
    $result.manual_confirmation_required += "Provide -KeyPath for key-based auth"
}

if ($result.status -ne "BLOCKED") {
    if ($effectiveDryRun) {
        Add-Check -Name "ssh_probe" -Status "SKIP" -Message "DryRun active; no SSH call attempted"
        if ($result.manual_confirmation_required.Count -eq 0) {
            $result.manual_confirmation_required += "Run without dry-run and with valid credentials to verify Ubuntu contour"
        }
        $result.status = "MANUAL_CONFIRMATION_REQUIRED"
    } else {
        $canAttempt = ($HostName -and $User -and $sshCmd)
        if (-not $canAttempt) {
            Add-Check -Name "ssh_probe" -Status "MANUAL_CONFIRMATION_REQUIRED" -Message "insufficient connection parameters"
            $result.status = "MANUAL_CONFIRMATION_REQUIRED"
        } else {
            $args = @("-o", "BatchMode=yes", "-o", "ConnectTimeout=10", "-p", "$Port")
            if ($KeyPath) {
                $args += @("-i", $KeyPath)
            }
            $args += @("$User@$HostName", "echo IMPERIUM_SSH_OK")

            try {
                $probeOutput = & ssh @args 2>&1
                $probeText = ($probeOutput | Out-String).Trim()
                if ($LASTEXITCODE -eq 0 -and $probeText -match "IMPERIUM_SSH_OK") {
                    Add-Check -Name "ssh_probe" -Status "PASS" -Message "SSH probe succeeded"
                    $result.status = "PASS"
                } else {
                    Add-Check -Name "ssh_probe" -Status "FAIL" -Message "SSH probe failed: $probeText"
                    $result.status = "FAIL"
                }
            } catch {
                Add-Check -Name "ssh_probe" -Status "FAIL" -Message "SSH probe exception: $($_.Exception.Message)"
                $result.status = "FAIL"
            }
        }
    }
}

if ($result.status -eq "UNKNOWN") {
    $result.status = "MANUAL_CONFIRMATION_REQUIRED"
}

if ($JsonOut) {
    $jsonPath = [System.IO.Path]::GetFullPath($JsonOut)
    $dir = Split-Path -Parent $jsonPath
    if ($dir -and -not (Test-Path -LiteralPath $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    ($result | ConvertTo-Json -Depth 10) | Set-Content -LiteralPath $jsonPath -Encoding UTF8
    $result.notes += "json receipt written: $jsonPath"
}

Write-Output ($result | ConvertTo-Json -Depth 10)
if ($result.status -eq "PASS") {
    exit 0
}
if ($result.status -eq "MANUAL_CONFIRMATION_REQUIRED") {
    exit 0
}
if ($result.status -eq "BLOCKED") {
    exit 2
}
exit 1
