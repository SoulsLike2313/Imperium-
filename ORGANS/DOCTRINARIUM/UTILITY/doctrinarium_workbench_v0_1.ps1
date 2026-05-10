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

    [System.Windows.Forms.MessageBox]::Show("Refresh completed. Exit code: $($p.ExitCode)", "Doctrinarium")
    Load-All
}

function Format-StatusSummary {
    $statusPath = Join-Path $Status "DOCTRINARIUM_STATUS.json"
    $s = Read-JsonSafe $statusPath

    if ($null -eq $s) {
        return "Status JSON not found or invalid.`r`n$statusPath"
    }

    $lines = @()
    $lines += "DOCTRINARIUM STATUS"
    $lines += "===================="
    $lines += "Verdict: $($s.verdict)"
    $lines += "Passport: $($s.passport_status)"
    $lines += "Constitution: $($s.constitution_status)"
    $lines += "Codex: $($s.codex_status)"
    $lines += "Doctrine Index: $($s.doctrine_index_status)"
    $lines += ""
    $lines += "Real task execution allowed: $($s.real_task_execution_allowed)"
    $lines += "Bootstrap/review allowed: $($s.bootstrap_review_allowed)"
    $lines += ""
    $lines += "LAWS"
    $lines += "----"
    $lines += "Total laws: $($s.law_registry_status.total_laws)"
    $lines += "Not fully enforced: $($s.law_registry_status.not_fully_enforced_count)"
    $lines += "HARD_BLOCK not fully enforced: $($s.law_registry_status.hard_not_fully_enforced_count)"
    $lines += ""
    $lines += "ORGAN GAPS"
    $lines += "----------"
    $lines += "Organs checked: $($s.organ_gap_summary.total_organs_checked)"
    $lines += "Total blockers: $($s.organ_gap_summary.total_blockers_found)"
    $lines += ""
    $lines += "NEXT RECOMMENDED STEPS"
    $lines += "----------------------"
    if ($s.next_recommended_steps) {
        foreach ($n in $s.next_recommended_steps) {
            $lines += "- $n"
        }
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

    return ($lines -join "`r`n")
}

function Format-LawList {
    $lawIndexPath = Join-Path $Laws "LAW_INDEX.json"
    $mandatoryPath = Join-Path $Laws "MANDATORY_LAWS.json"
    $enforcementPath = Join-Path $Laws "LAW_ENFORCEMENT_MAP.json"

    $lawIndex = Read-JsonSafe $lawIndexPath
    $mandatory = Read-JsonSafe $mandatoryPath
    $enforcement = Read-JsonSafe $enforcementPath

    $lines = @()
    $lines += "CODEX / LAW REGISTRY"
    $lines += "===================="
    $lines += "LAW_INDEX:"
    $lines += $lawIndexPath
    $lines += ""
    $lines += "MANDATORY_LAWS:"
    $lines += $mandatoryPath
    $lines += ""
    $lines += "LAW_ENFORCEMENT_MAP:"
    $lines += $enforcementPath
    $lines += ""

    if ($null -eq $lawIndex) {
        $lines += "LAW_INDEX.json not found or invalid."
        return ($lines -join "`r`n")
    }

    $raw = Get-Content $lawIndexPath -Raw -Encoding UTF8

    $lines += "RAW LAW INDEX SUMMARY"
    $lines += "---------------------"

    # Flexible display: generated files may use different shapes.
    if ($lawIndex.laws) {
        foreach ($law in $lawIndex.laws) {
            $lines += ""
            $lines += "Law: $($law.law_id) $($law.title)"
            $lines += "Severity: $($law.severity)"
            $lines += "Status: $($law.status)"
            $lines += "Violation verdict: $($law.violation_verdict)"
            $lines += "Enforcement status: $($law.enforcement_status)"
            if ($law.source_document_path) { $lines += "Source: $($law.source_document_path)" }
        }
    } elseif ($lawIndex.mandatory_laws) {
        foreach ($law in $lawIndex.mandatory_laws) {
            $lines += ""
            $lines += "Law: $($law.law_id) $($law.title)"
            $lines += "Severity: $($law.severity)"
            $lines += "Status: $($law.status)"
            $lines += "Violation verdict: $($law.violation_verdict)"
            $lines += "Enforcement status: $($law.enforcement_status)"
        }
    } else {
        $lines += "Could not detect law array shape. Showing raw LAW_INDEX.json below:"
        $lines += ""
        $lines += $raw
    }

    $lines += ""
    $lines += ""
    $lines += "ENFORCEMENT MAP RAW"
    $lines += "-------------------"
    if (Test-Path $enforcementPath) {
        $lines += Read-TextSafe $enforcementPath
    } else {
        $lines += "NOT FOUND: $enforcementPath"
    }

    return ($lines -join "`r`n")
}

function Load-All {
    $txtStatus.Text = Format-StatusSummary
    $txtAllGaps.Text = Read-TextSafe (Join-Path $Reports "ALL_ORGANS_GAP_REPORT.md")
    $txtUtilityGaps.Text = Read-TextSafe (Join-Path $Reports "ORGAN_UTILITY_GAP_REPORT.md")
    $txtDoctrine.Text = Read-TextSafe (Join-Path $Doctrine "DOCTRINE_INDEX.json")
    $txtLaws.Text = Format-LawList
    $txtRaw.Text = "Paths:`r`n" +
        "Doctrinarium: $Doc`r`n" +
        "Doctrine: $Doctrine`r`n" +
        "Laws: $Laws`r`n" +
        "Standards: $Standards`r`n" +
        "Reports: $Reports`r`n" +
        "Status: $Status`r`n" +
        "Utility: $Utility`r`n"
}

$form = New-Object System.Windows.Forms.Form
$form.Text = "Doctrinarium Workbench v0_1"
$form.Size = New-Object System.Drawing.Size(1180, 780)
$form.StartPosition = "CenterScreen"

$topPanel = New-Object System.Windows.Forms.Panel
$topPanel.Dock = "Top"
$topPanel.Height = 48
$form.Controls.Add($topPanel)

$btnRefresh = New-Object System.Windows.Forms.Button
$btnRefresh.Text = "Run Doctrinarium Refresh"
$btnRefresh.Width = 190
$btnRefresh.Height = 30
$btnRefresh.Left = 10
$btnRefresh.Top = 9
$btnRefresh.Add_Click({ Run-Refresh })
$topPanel.Controls.Add($btnRefresh)

$btnReports = New-Object System.Windows.Forms.Button
$btnReports.Text = "Open Reports"
$btnReports.Width = 110
$btnReports.Height = 30
$btnReports.Left = 210
$btnReports.Top = 9
$btnReports.Add_Click({ Open-Folder $Reports })
$topPanel.Controls.Add($btnReports)

$btnDoctrine = New-Object System.Windows.Forms.Button
$btnDoctrine.Text = "Open Doctrine"
$btnDoctrine.Width = 115
$btnDoctrine.Height = 30
$btnDoctrine.Left = 330
$btnDoctrine.Top = 9
$btnDoctrine.Add_Click({ Open-Folder $Doctrine })
$topPanel.Controls.Add($btnDoctrine)

$btnLaws = New-Object System.Windows.Forms.Button
$btnLaws.Text = "Open Laws"
$btnLaws.Width = 100
$btnLaws.Height = 30
$btnLaws.Left = 455
$btnLaws.Top = 9
$btnLaws.Add_Click({ Open-Folder $Laws })
$topPanel.Controls.Add($btnLaws)

$btnStandards = New-Object System.Windows.Forms.Button
$btnStandards.Text = "Open Standards"
$btnStandards.Width = 125
$btnStandards.Height = 30
$btnStandards.Left = 565
$btnStandards.Top = 9
$btnStandards.Add_Click({ Open-Folder $Standards })
$topPanel.Controls.Add($btnStandards)

$btnUtility = New-Object System.Windows.Forms.Button
$btnUtility.Text = "Open Utility"
$btnUtility.Width = 105
$btnUtility.Height = 30
$btnUtility.Left = 700
$btnUtility.Top = 9
$btnUtility.Add_Click({ Open-Folder $Utility })
$topPanel.Controls.Add($btnUtility)

$btnReload = New-Object System.Windows.Forms.Button
$btnReload.Text = "Reload View"
$btnReload.Width = 105
$btnReload.Height = 30
$btnReload.Left = 815
$btnReload.Top = 9
$btnReload.Add_Click({ Load-All })
$topPanel.Controls.Add($btnReload)

$tabs = New-Object System.Windows.Forms.TabControl
$tabs.Dock = "Fill"
$form.Controls.Add($tabs)

function New-TabTextBox($Title) {
    $tab = New-Object System.Windows.Forms.TabPage
    $tab.Text = $Title

    $txt = New-Object System.Windows.Forms.TextBox
    $txt.Multiline = $true
    $txt.ScrollBars = "Both"
    $txt.WordWrap = $false
    $txt.ReadOnly = $true
    $txt.Dock = "Fill"
    $txt.Font = New-Object System.Drawing.Font("Consolas", 10)

    $tab.Controls.Add($txt)
    $tabs.TabPages.Add($tab)

    return $txt
}

$txtStatus = New-TabTextBox "Status"
$txtAllGaps = New-TabTextBox "Organ Gaps"
$txtUtilityGaps = New-TabTextBox "Utility Gaps"
$txtLaws = New-TabTextBox "Laws / Codex"
$txtDoctrine = New-TabTextBox "Doctrine Index"
$txtRaw = New-TabTextBox "Paths"

Load-All

[void]$form.ShowDialog()
