$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$Root = "E:\IMPERIUM"
$Doc = Join-Path $Root "ORGANS\DOCTRINARIUM"
$Reports = Join-Path $Doc "REPORTS"
$Status = Join-Path $Doc "STATUS"
$Doctrine = Join-Path $Doc "DOCTRINE"
$Laws = Join-Path $Doc "LAWS"
$Standards = Join-Path $Doc "STANDARDS"
$Utility = Join-Path $Doc "UTILITY"
$RefreshScript = Join-Path $Utility "run_doctrinarium_workbench_refresh.ps1"

$ColorBg = [System.Drawing.Color]::FromArgb(17, 24, 39)
$ColorPanel = [System.Drawing.Color]::FromArgb(31, 41, 55)
$ColorPanel2 = [System.Drawing.Color]::FromArgb(15, 23, 42)
$ColorText = [System.Drawing.Color]::FromArgb(229, 231, 235)
$ColorMuted = [System.Drawing.Color]::FromArgb(156, 163, 175)
$ColorAccent = [System.Drawing.Color]::FromArgb(96, 165, 250)
$ColorGreen = [System.Drawing.Color]::FromArgb(34, 197, 94)
$ColorRed = [System.Drawing.Color]::FromArgb(248, 113, 113)
$ColorYellow = [System.Drawing.Color]::FromArgb(250, 204, 21)

function Read-TextSafe($Path) {
    if (Test-Path $Path) {
        return Get-Content $Path -Raw -Encoding UTF8
    }
    return "NOT FOUND:`r`n$Path"
}

function Read-JsonSafe($Path) {
    if (Test-Path $Path) {
        try {
            return Get-Content $Path -Raw -Encoding UTF8 | ConvertFrom-Json
        } catch {
            return $null
        }
    }
    return $null
}

function Open-Folder($Path) {
    if (Test-Path $Path) {
        Start-Process explorer.exe $Path
    } else {
        [System.Windows.Forms.MessageBox]::Show("Folder not found:`n$Path", "Doctrinarium")
    }
}

function New-Button($Text, $Left, $Width, $Handler) {
    $btn = New-Object System.Windows.Forms.Button
    $btn.Text = $Text
    $btn.Width = $Width
    $btn.Height = 32
    $btn.Left = $Left
    $btn.Top = 12
    $btn.FlatStyle = "Flat"
    $btn.BackColor = [System.Drawing.Color]::FromArgb(30, 64, 175)
    $btn.ForeColor = [System.Drawing.Color]::White
    $btn.Font = New-Object System.Drawing.Font("Segoe UI", 9, [System.Drawing.FontStyle]::Bold)
    $btn.FlatAppearance.BorderColor = $ColorAccent
    $btn.Add_Click($Handler)
    return $btn
}

function New-Card($Parent, $Title, $Left, $Top, $Width) {
    $panel = New-Object System.Windows.Forms.Panel
    $panel.Left = $Left
    $panel.Top = $Top
    $panel.Width = $Width
    $panel.Height = 74
    $panel.BackColor = $ColorPanel

    $lblTitle = New-Object System.Windows.Forms.Label
    $lblTitle.Text = $Title
    $lblTitle.Left = 12
    $lblTitle.Top = 8
    $lblTitle.Width = $Width - 24
    $lblTitle.Height = 18
    $lblTitle.ForeColor = $ColorMuted
    $lblTitle.Font = New-Object System.Drawing.Font("Segoe UI", 8)

    $lblValue = New-Object System.Windows.Forms.Label
    $lblValue.Text = "..."
    $lblValue.Left = 12
    $lblValue.Top = 30
    $lblValue.Width = $Width - 24
    $lblValue.Height = 32
    $lblValue.ForeColor = $ColorText
    $lblValue.Font = New-Object System.Drawing.Font("Segoe UI", 13, [System.Drawing.FontStyle]::Bold)

    $panel.Controls.Add($lblTitle)
    $panel.Controls.Add($lblValue)
    $Parent.Controls.Add($panel)

    return $lblValue
}

function New-TabTextBox($Title) {
    $tab = New-Object System.Windows.Forms.TabPage
    $tab.Text = $Title
    $tab.BackColor = $ColorBg

    $txt = New-Object System.Windows.Forms.RichTextBox
    $txt.Multiline = $true
    $txt.ScrollBars = "Both"
    $txt.WordWrap = $false
    $txt.ReadOnly = $true
    $txt.Dock = "Fill"
    $txt.Font = New-Object System.Drawing.Font("Consolas", 10)
    $txt.BackColor = [System.Drawing.Color]::FromArgb(3, 7, 18)
    $txt.ForeColor = $ColorText
    $txt.BorderStyle = "None"

    $tab.Controls.Add($txt)
    $tabs.TabPages.Add($tab)

    return $txt
}

function Format-StatusSummary {
    $statusPath = Join-Path $Status "DOCTRINARIUM_STATUS.json"
    $gapPath = Join-Path $Reports "ALL_ORGANS_GAP_REPORT.json"
    $utilityPath = Join-Path $Reports "ORGAN_UTILITY_GAP_REPORT.json"

    $s = Read-JsonSafe $statusPath
    $g = Read-JsonSafe $gapPath
    $u = Read-JsonSafe $utilityPath

    $lines = @()
    $lines += "DOCTRINARIUM WORKBENCH v0_2"
    $lines += "================================"
    $lines += ""

    if ($null -eq $s) {
        $lines += "STATUS JSON NOT FOUND OR INVALID:"
        $lines += $statusPath
        return ($lines -join "`r`n")
    }

    $lines += "PRIMARY VERDICT"
    $lines += "---------------"
    $lines += "Status verdict: $($s.verdict)"
    $lines += "Real task execution allowed: $($s.real_task_execution_allowed)"
    $lines += "Bootstrap/review allowed: $($s.bootstrap_review_allowed)"
    $lines += ""

    $lines += "DOCTRINE TRIAD"
    $lines += "--------------"
    $lines += "Passport:     $($s.passport_status)"
    $lines += "Constitution: $($s.constitution_status)"
    $lines += "Codex:        $($s.codex_status)"
    $lines += "Index:        $($s.doctrine_index_status)"
    $lines += ""

    $lines += "LAW REGISTRY"
    $lines += "------------"
    $lines += "Total laws: $($s.law_registry_status.total_laws)"
    $lines += "Not fully enforced: $($s.law_registry_status.not_fully_enforced_count)"
    $lines += "HARD_BLOCK not fully enforced: $($s.law_registry_status.hard_not_fully_enforced_count)"
    $lines += ""

    $lines += "ORGAN GAPS"
    $lines += "----------"
    if ($null -ne $g) {
        $lines += "Gap verdict: $($g.verdict)"
        $lines += "Organs checked: $($g.total_organs_checked)"
        $lines += "Total blockers: $($g.total_blockers_found)"
        if ($g.classification_summary) {
            $lines += "Classification:"
            $g.classification_summary.PSObject.Properties | ForEach-Object {
                $lines += "  - $($_.Name): $($_.Value)"
            }
        }
    } else {
        $lines += "ALL_ORGANS_GAP_REPORT.json not found or invalid."
    }
    $lines += ""

    $lines += "UTILITY GAPS"
    $lines += "------------"
    if ($null -ne $u) {
        $lines += "Utility verdict: $($u.verdict)"
        $lines += "Organs checked: $($u.summary.total_organs_checked)"
        $lines += "Utility declared: $($u.summary.utility_declared_count)"
        $lines += "Script-backed utilities: $($u.summary.script_backed_count)"
        $lines += "Warnings: $($u.summary.warnings_count)"
    } else {
        $lines += "ORGAN_UTILITY_GAP_REPORT.json not found or invalid."
    }
    $lines += ""

    $lines += "CURRENT BLOCKERS"
    $lines += "----------------"
    if ($s.doctrinarium_organ_status.current_blockers) {
        foreach ($b in $s.doctrinarium_organ_status.current_blockers) {
            $lines += "- $b"
        }
    } else {
        $lines += "- none"
    }

    $lines += ""
    $lines += "NEXT RECOMMENDED STEPS"
    $lines += "----------------------"
    if ($s.next_recommended_steps) {
        foreach ($n in $s.next_recommended_steps) {
            $lines += "- $n"
        }
    }

    return ($lines -join "`r`n")
}

function Format-LawList {
    $lawIndexPath = Join-Path $Laws "LAW_INDEX.json"
    $mandatoryPath = Join-Path $Laws "MANDATORY_LAWS.json"
    $addressPath = Join-Path $Laws "LAW_ADDRESS_REGISTRY.json"
    $enforcementPath = Join-Path $Laws "LAW_ENFORCEMENT_MAP.json"

    $lawIndex = Read-JsonSafe $lawIndexPath

    $lines = @()
    $lines += "CODEX / LAW REGISTRY"
    $lines += "===================="
    $lines += ""
    $lines += "LAW FILES"
    $lines += "---------"
    $lines += "LAW_INDEX:            $lawIndexPath"
    $lines += "MANDATORY_LAWS:       $mandatoryPath"
    $lines += "LAW_ADDRESS_REGISTRY: $addressPath"
    $lines += "LAW_ENFORCEMENT_MAP:  $enforcementPath"
    $lines += ""

    if ($null -eq $lawIndex) {
        $lines += "LAW_INDEX.json not found or invalid."
        return ($lines -join "`r`n")
    }

    $laws = $null
    if ($lawIndex.laws) { $laws = $lawIndex.laws }
    elseif ($lawIndex.mandatory_laws) { $laws = $lawIndex.mandatory_laws }
    elseif ($lawIndex.entries) { $laws = $lawIndex.entries }

    if ($null -eq $laws) {
        $lines += "Could not detect law array shape. Raw LAW_INDEX.json:"
        $lines += ""
        $lines += Read-TextSafe $lawIndexPath
        return ($lines -join "`r`n")
    }

    $lines += "LAWS"
    $lines += "----"

    foreach ($law in $laws) {
        $lines += ""
        $lines += ("{0} - {1}" -f $law.law_id, $law.title)
        $lines += "  Severity:           $($law.severity)"
        $lines += "  Status:             $($law.status)"
        $lines += "  Enforcement status: $($law.enforcement_status)"
        $lines += "  Violation verdict:  $($law.violation_verdict)"
        if ($law.source_document_path) {
            $lines += "  Source:             $($law.source_document_path)"
        }
        if ($law.enforcement_points) {
            $lines += "  Enforcement points:"
            foreach ($p in $law.enforcement_points) {
                $lines += "    - $p"
            }
        }
    }

    $lines += ""
    $lines += "ENFORCEMENT MAP RAW"
    $lines += "-------------------"
    $lines += Read-TextSafe $enforcementPath

    return ($lines -join "`r`n")
}

function Run-Refresh {
    if (!(Test-Path $RefreshScript)) {
        [System.Windows.Forms.MessageBox]::Show("Refresh launcher not found:`n$RefreshScript", "Doctrinarium")
        return
    }

    $p = Start-Process powershell.exe -ArgumentList @(
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File", "`"$RefreshScript`""
    ) -Wait -PassThru

    Load-All
    [System.Windows.Forms.MessageBox]::Show("Refresh completed. Exit code: $($p.ExitCode)", "Doctrinarium")
}

function Set-Card($Label, $Value, $Color) {
    $Label.Text = [string]$Value
    $Label.ForeColor = $Color
}

function Load-All {
    $statusPath = Join-Path $Status "DOCTRINARIUM_STATUS.json"
    $gapPath = Join-Path $Reports "ALL_ORGANS_GAP_REPORT.json"
    $utilityPath = Join-Path $Reports "ORGAN_UTILITY_GAP_REPORT.json"

    $s = Read-JsonSafe $statusPath
    $g = Read-JsonSafe $gapPath
    $u = Read-JsonSafe $utilityPath

    if ($null -ne $s) {
        if ($s.real_task_execution_allowed -eq $true) {
            Set-Card $cardRealTask "ALLOWED" $ColorGreen
        } else {
            Set-Card $cardRealTask "BLOCKED" $ColorRed
        }

        if ($s.bootstrap_review_allowed -eq $true) {
            Set-Card $cardBootstrap "TRUE" $ColorGreen
        } else {
            Set-Card $cardBootstrap "FALSE" $ColorRed
        }

        Set-Card $cardLaws "$($s.law_registry_status.not_fully_enforced_count) / $($s.law_registry_status.total_laws)" $ColorYellow
        Set-Card $cardDoctrine "OWNER REVIEW" $ColorYellow
    }

    if ($null -ne $g) {
        Set-Card $cardOrgans "$($g.total_organs_checked) organs" $ColorAccent
        Set-Card $cardBlockers "$($g.total_blockers_found)" $ColorRed
    }

    if ($null -ne $u) {
        Set-Card $cardUtility "$($u.summary.script_backed_count) backed" $ColorAccent
    }

    $txtStatus.Text = Format-StatusSummary
    $txtAllGaps.Text = Read-TextSafe (Join-Path $Reports "ALL_ORGANS_GAP_REPORT.md")
    $txtUtilityGaps.Text = Read-TextSafe (Join-Path $Reports "ORGAN_UTILITY_GAP_REPORT.md")
    $txtDoctrine.Text = Read-TextSafe (Join-Path $Doctrine "DOCTRINE_INDEX.json")
    $txtLaws.Text = Format-LawList
    $txtRaw.Text = "PATHS`r`n=====`r`n" +
        "Doctrinarium: $Doc`r`n" +
        "Doctrine:     $Doctrine`r`n" +
        "Laws:         $Laws`r`n" +
        "Standards:    $Standards`r`n" +
        "Reports:      $Reports`r`n" +
        "Status:       $Status`r`n" +
        "Utility:      $Utility`r`n" +
        "Refresh:      $RefreshScript`r`n"
}

$form = New-Object System.Windows.Forms.Form
$form.Text = "Doctrinarium Workbench v0_2"
$form.Size = New-Object System.Drawing.Size(1240, 820)
$form.StartPosition = "CenterScreen"
$form.BackColor = $ColorBg

$header = New-Object System.Windows.Forms.Panel
$header.Dock = "Top"
$header.Height = 70
$header.BackColor = $ColorPanel2
$form.Controls.Add($header)

$title = New-Object System.Windows.Forms.Label
$title.Text = "Doctrinarium Workbench"
$title.Left = 18
$title.Top = 10
$title.Width = 440
$title.Height = 28
$title.ForeColor = [System.Drawing.Color]::White
$title.Font = New-Object System.Drawing.Font("Segoe UI", 17, [System.Drawing.FontStyle]::Bold)
$header.Controls.Add($title)

$subtitle = New-Object System.Windows.Forms.Label
$subtitle.Text = "Doctrine - Laws - Organ Gaps - Utility Validation"
$subtitle.Left = 20
$subtitle.Top = 42
$subtitle.Width = 520
$subtitle.Height = 18
$subtitle.ForeColor = $ColorMuted
$subtitle.Font = New-Object System.Drawing.Font("Segoe UI", 9)
$header.Controls.Add($subtitle)

$btnPanel = New-Object System.Windows.Forms.Panel
$btnPanel.Dock = "Top"
$btnPanel.Height = 58
$btnPanel.BackColor = $ColorBg
$form.Controls.Add($btnPanel)

$btnPanel.Controls.Add((New-Button "Run Refresh" 12 130 { Run-Refresh }))
$btnPanel.Controls.Add((New-Button "Open Reports" 154 120 { Open-Folder $Reports }))
$btnPanel.Controls.Add((New-Button "Open Doctrine" 286 130 { Open-Folder $Doctrine }))
$btnPanel.Controls.Add((New-Button "Open Laws" 428 110 { Open-Folder $Laws }))
$btnPanel.Controls.Add((New-Button "Open Standards" 550 135 { Open-Folder $Standards }))
$btnPanel.Controls.Add((New-Button "Open Utility" 697 120 { Open-Folder $Utility }))
$btnPanel.Controls.Add((New-Button "Reload View" 829 115 { Load-All }))

$cardPanel = New-Object System.Windows.Forms.Panel
$cardPanel.Dock = "Top"
$cardPanel.Height = 94
$cardPanel.BackColor = $ColorBg
$form.Controls.Add($cardPanel)

$cardRealTask = New-Card $cardPanel "REAL TASK EXECUTION" 12 10 160
$cardBootstrap = New-Card $cardPanel "BOOTSTRAP / REVIEW" 184 10 160
$cardDoctrine = New-Card $cardPanel "DOCTRINE STATUS" 356 10 170
$cardLaws = New-Card $cardPanel "LAWS NOT ENFORCED" 538 10 170
$cardOrgans = New-Card $cardPanel "ORGANS CHECKED" 720 10 150
$cardBlockers = New-Card $cardPanel "ORGAN BLOCKERS" 882 10 150
$cardUtility = New-Card $cardPanel "UTILITIES" 1044 10 150

$tabs = New-Object System.Windows.Forms.TabControl
$tabs.Dock = "Fill"
$tabs.Font = New-Object System.Drawing.Font("Segoe UI", 9)
$form.Controls.Add($tabs)

$txtStatus = New-TabTextBox "Status"
$txtAllGaps = New-TabTextBox "Organ Gaps"
$txtUtilityGaps = New-TabTextBox "Utility Gaps"
$txtLaws = New-TabTextBox "Laws / Codex"
$txtDoctrine = New-TabTextBox "Doctrine Index"
$txtRaw = New-TabTextBox "Paths"

Load-All

[void]$form.ShowDialog()
