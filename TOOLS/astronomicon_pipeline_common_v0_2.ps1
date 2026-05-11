Set-StrictMode -Version Latest

function Write-Utf8Bom {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Content
    )

    $directory = Split-Path -Parent $Path
    if ($directory -and -not (Test-Path -LiteralPath $directory)) {
        New-Item -ItemType Directory -Force -Path $directory | Out-Null
    }

    $utf8Bom = New-Object System.Text.UTF8Encoding($true)
    [System.IO.File]::WriteAllText($Path, ($Content -replace "`r`n", "`n" -replace "`r", "`n").Replace("`n", "`r`n"), $utf8Bom)
}

function Read-JsonFile {
    param(
        [Parameter(Mandatory = $true)][string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "JSON file not found: $Path"
    }
    return Get-Content -LiteralPath $Path -Encoding UTF8 -Raw | ConvertFrom-Json
}

function Write-JsonFile {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)]$Object,
        [int]$Depth = 30
    )

    Write-Utf8Bom -Path $Path -Content ($Object | ConvertTo-Json -Depth $Depth)
}

function Get-NormalizedText {
    param(
        [Parameter(Mandatory = $true)][string]$Text
    )
    return (($Text -replace "`r`n", "`n") -replace "`r", "`n")
}

function Get-ScalarFieldFromStrictText {
    param(
        [Parameter(Mandatory = $true)][string]$Text,
        [Parameter(Mandatory = $true)][string]$FieldName
    )

    $normalized = Get-NormalizedText -Text $Text
    $escaped = [regex]::Escape($FieldName)
    $pattern = "(?ms)^$escaped\s*:\s*\n(?<v>.*?)(?=\n\n[A-Z0-9_]+:|\n\nBEGIN_|\n---|$)"
    $match = [regex]::Match($normalized, $pattern)
    if ($match.Success) {
        return $match.Groups["v"].Value.Trim()
    }
    return ""
}

function Get-StrictBlock {
    param(
        [Parameter(Mandatory = $true)][string]$Text,
        [Parameter(Mandatory = $true)][string]$BlockName
    )

    $normalized = Get-NormalizedText -Text $Text
    $begin = [regex]::Escape("BEGIN_$BlockName")
    $end = [regex]::Escape("END_$BlockName")
    $pattern = "(?ms)^$begin\s*\n(?<v>.*?)\n$end\s*"
    $match = [regex]::Match($normalized, $pattern)
    if ($match.Success) {
        return $match.Groups["v"].Value.Trim()
    }
    return ""
}

function Get-Sha256String {
    param(
        [Parameter(Mandatory = $true)][string]$Text
    )

    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
        $hashBytes = $sha.ComputeHash($bytes)
        return ([System.BitConverter]::ToString($hashBytes)).Replace("-", "").ToLowerInvariant()
    }
    finally {
        $sha.Dispose()
    }
}

function New-ReceiptRecord {
    param(
        [Parameter(Mandatory = $true)][string]$SchemaVersion,
        [Parameter(Mandatory = $true)][string]$Status,
        [string]$GeneralTaskId = "",
        [hashtable]$Fields = @{}
    )

    $record = [ordered]@{
        schema_version = $SchemaVersion
        status = $Status
        general_task_id = $GeneralTaskId
        generated_at = (Get-Date).ToString("o")
    }

    foreach ($key in $Fields.Keys) {
        $record[$key] = $Fields[$key]
    }

    return $record
}

function Get-OrphanRefinementRecord {
    param(
        [Parameter(Mandatory = $true)]$RefinementItem,
        [Parameter(Mandatory = $true)][string]$Reason
    )

    return [ordered]@{
        reason = $Reason
        refinement = $RefinementItem
    }
}

function Update-StatusFile {
    param(
        [Parameter(Mandatory = $true)][string]$StatusPath,
        [Parameter(Mandatory = $true)][hashtable]$Patch
    )

    $status = @{}
    if (Test-Path -LiteralPath $StatusPath) {
        $existing = Read-JsonFile -Path $StatusPath
        $existing.PSObject.Properties | ForEach-Object {
            $status[$_.Name] = $_.Value
        }
    }

    foreach ($key in $Patch.Keys) {
        $status[$key] = $Patch[$key]
    }
    $status["updated_at"] = (Get-Date).ToString("o")

    Write-JsonFile -Path $StatusPath -Object $status -Depth 20
}

function Get-SuspiciousPathMatches {
    param(
        [Parameter(Mandatory = $true)][string[]]$Paths
    )

    $pattern = '(SSH_COMMAND_LIBRARY|id_rsa|id_ed25519|\.pem$|\.ppk$|\.key$|\.env$|token|secret|password|credential|cookie|session|known_hosts|authorized_keys)'
    $hits = @()
    foreach ($path in $Paths) {
        if ($path -match $pattern) {
            $hits += $path
        }
    }
    return $hits
}

function Ensure-Directory {
    param(
        [Parameter(Mandatory = $true)][string]$Path
    )
    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Force -Path $Path | Out-Null
    }
}

function Get-AbsolutePath {
    param(
        [Parameter(Mandatory = $true)][string]$Path
    )
    $resolved = Resolve-Path -LiteralPath $Path -ErrorAction Stop
    return $resolved.Path
}
