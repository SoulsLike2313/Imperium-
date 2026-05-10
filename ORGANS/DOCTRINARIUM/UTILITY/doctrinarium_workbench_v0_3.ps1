$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

[System.Windows.Forms.Application]::EnableVisualStyles()

$Root = "E:\IMPERIUM"
$Doc = Join-Path $Root "ORGANS\DOCTRINARIUM"
$Reports = Join-Path $Doc "REPORTS"
$Status = Join-Path $Doc "STATUS"
$Doctrine = Join-Path $Doc "DOCTRINE"
$Laws = Join-Path $Doc "LAWS"
$Standards = Join-Path $Doc "STANDARDS"
$Utility = Join-Path $Doc "UTILITY"
$RefreshScript = Join-Path $Utility "run_doctrinarium_workbench_refresh.ps1"

# ---------- Theme ----------
$C_BG = [System.Drawing.Color]::FromArgb(11,16,28)
$C_BG2 = [System.Drawing.Color]::FromArgb(18,26,43)
$C_PANEL = [System.Drawing.Color]::FromArgb(22,33,53)
$C_PANEL2 = [System.Drawing.Color]::FromArgb(30,43,69)
$C_TEXT = [System.Drawing.Color]::FromArgb(230,235,245)
$C_MUTED = [System.Drawing.Color]::FromArgb(155,165,185)
$C_ACCENT = [System.Drawing.Color]::FromArgb(90,170,255)
$C_GREEN = [System.Drawing.Color]::FromArgb(70,200,120)
$C_RED = [System.Drawing.Color]::FromArgb(235,90,110)
$C_YELLOW = [System.Drawing.Color]::FromArgb(245,200,80)
$C_ORANGE = [System.Drawing.Color]::FromArgb(255,155,70)

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

function Set-RichTextTheme($Box) {
    $Box.ReadOnly = $true
    $Box.Multiline = $true
    $Box.ScrollBars = "Both"
    $Box.WordWrap = $false
    $Box.BorderStyle = "None"
    $Box.Font = New-Object System.Drawing.Font("Consolas", 10)
    $Box.BackColor = [System.Drawing.Color]::FromArgb(7,11,21)
    $Box.ForeColor = $C_TEXT
    $Box.Dock = "Fill"
}

function New-NavButton($Text, $Top, $Handler) {
    $btn = New-Object System.Windows.Forms.Button
    $btn.Text = $Text
    $btn.Left = 12
    $btn.Top = $Top
    $btn.Width = 180
    $btn.Height = 38
    $btn.FlatStyle = "Flat"
    $btn.BackColor = $C_PANEL2
    $btn.ForeColor = $C_TEXT
    $btn.Font = New-Object System.Drawing.Font("Segoe UI", 9, [System.Drawing.FontStyle]::Bold)
    $btn.FlatAppearance.BorderColor = $C_ACCENT
    $btn.Add_Click($Handler)
    return $btn
}

function New-Card($Parent, $Title, $Left, $Top, $Width) {
    $panel = New-Object System.Windows.Forms.Panel
    $panel.Left = $Left
    $panel.Top = $Top
    $panel.Width = $Width
    $panel.Height = 82
    $panel.BackColor = $C_PANEL
    $panel.BorderStyle = "FixedSingle"

    $line = New-Object System.Windows.Forms.Panel
    $line.Left = 0
    $line.Top = 0
    $line.Width = 6
    $line.Height = 82
    $line.BackColor = $C_ACCENT
    $panel.Controls.Add($line)

    $lblTitle = New-Object System.Windows.Forms.Label
    $lblTitle.Text = $Title
    $lblTitle.Left = 14
    $lblTitle.Top = 10
    $lblTitle.Width = $Width - 24
    $lblTitle.Height = 18
    $lblTitle.ForeColor = $C_MUTED
    $lblTitle.Font = New-Object System.Drawing.Font("Segoe UI", 8)

    $lblValue = New-Object System.Windows.Forms.Label
    $lblValue.Text = "..."
    $lblValue.Left = 14
    $lblValue.Top = 34
    $lblValue.Width = $Width - 24
    $lblValue.Height = 30
    $lblValue.ForeColor = $C_TEXT
    $lblValue.Font = New-Object System.Drawing.Font("Segoe UI", 13, [System.Drawing.FontStyle]::Bold)

    $panel.Controls.Add($lblTitle)
    $panel.Controls.Add($lblValue)
    $Parent.Controls.Add($panel)

    return [pscustomobject]@{
        Panel = $panel
        Accent = $line
        Value = $lblValue
    }
}

function Set-Card($Card, $Text, $Color) {
    $Card.Value.Text = [string]$Text
    $Card.Value.ForeColor = $Color
    $Card.Accent.BackColor = $Color
}

function Show-View($name) {
    $views = @($viewStatus,$viewOrgGaps,$viewUtilityGaps,$viewLaws,$viewDoctrine,$viewPaths)
    foreach ($v in $views) { $v.Visible = $false }
    switch ($name) {
        "status" { $viewStatus.Visible = $true }
        "orggaps" { $viewOrgGaps.Visible = $true }
        "utility" { $viewUtilityGaps.Visible = $true }
        "laws" { $viewLaws.Visible = $true }
        "doctrine" { $viewDoctrine.Visible = $true }
        "paths" { $viewPaths.Visible = $true }
    }
}

function Format-StatusSummary {
    $statusPath = Join-Path $Status "DOCTRINARIUM_STATUS.json"
    $gapPath = Join-Path $Reports "ALL_ORGANS_GAP_REPORT.json"
    $utilityPath = Join-Path $Reports "ORGAN_UTILITY_GAP_REPORT.json"

    $s = Read-JsonSafe $statusPath
    $g = Read-JsonSafe $gapPath
    $u = Read-JsonSafe $utilityPath

    if ($null -eq $s) {
        return "STATUS JSON not found or invalid.`r`n$statusPath"
    }

    $lines = @()
    $lines += "DOCTRINARIUM STATUS"
    $lines += "==================="
    $lines += ""
    $lines += "Primary verdict: $($s.verdict)"
    $lines += "Real task execution allowed: $($s.real_task_execution_allowed)"
    $lines += "Bootstrap/review allowed: $($s.bootstrap_review_allowed)"
    $lines += ""
    $lines += "DOCTRINE TRIAD"
    $lines += "--------------"
    $lines += "Passport:     $($s.passport_status)"
    $lines += "Constitution: $($s.constitution_status)"
    $lines += "Codex:        $($s.codex_status)"
    $lines += "Doctrine Index: $($s.doctrine_index_status)"
    $lines += ""
    $lines += "LAW REGISTRY"
    $lines += "------------"
    $lines += "Total laws: $($s.law_registry_status.total_laws)"
    $lines += "Not fully enforced: $($s.law_registry_status.not_fully_enforced_count)"
    $lines += "Hard block not fully enforced: $($s.law_registry_status.hard_not_fully_enforced_count)"
    $lines += ""

    if ($null -ne $g) {
        $lines += "ORGAN GAPS"
        $lines += "----------"
        $lines += "Gap verdict: $($g.verdict)"
        $lines += "Organs checked: $($g.total_organs_checked)"
        $lines += "Total blockers: $($g.total_blockers_found)"
        $lines += ""
    }

    if ($null -ne $u) {
        $lines += "UTILITY GAPS"
        $lines += "------------"
        $lines += "Utility verdict: $($u.verdict)"
        $lines += "Utility declared: $($u.summary.utility_declared_count)"
        $lines += "Script-backed utilities: $($u.summary.script_backed_count)"
        $lines += "Warnings: $($u.summary.warnings_count)"
        $lines += ""
    }

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

function Format-LawsPretty {
    $lawIndexPath = Join-Path $Laws "LAW_INDEX.json"
    $mandatoryPath = Join-Path $Laws "MANDATORY_LAWS.json"
    $addressPath = Join-Path $Laws "LAW_ADDRESS_REGISTRY.json"
    $enforcementPath = Join-Path $Laws "LAW_ENFORCEMENT_MAP.json"

    $lawIndex = Read-JsonSafe $lawIndexPath

    $lines = @()
    $lines += "CODEX / LAW REGISTRY"
    $lines += "===================="
    $lines += ""
    $lines += "FILES"
    $lines += "-----"
    $lines += "LAW_INDEX.json:"
    $lines += "  $lawIndexPath"
    $lines += "MANDATORY_LAWS.json:"
    $lines += "  $mandatoryPath"
    $lines += "LAW_ADDRESS_REGISTRY.json:"
    $lines += "  $addressPath"
    $lines += "LAW_ENFORCEMENT_MAP.json:"
    $lines += "  $enforcementPath"
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
        $lines += "Could not detect laws array shape."
        $lines += ""
        $lines += Read-TextSafe $lawIndexPath
        return ($lines -join "`r`n")
    }

    $lines += "REGISTERED LAWS"
    $lines += "---------------"

    foreach ($law in $laws) {
        $lines += ""
        $lines += ("{0} - {1}" -f $law.law_id, $law.title)
        $lines += ("  Severity:           {0}" -f $law.severity)
        $lines += ("  Status:             {0}" -f $law.status)
        $lines += ("  Enforcement status: {0}" -f $law.enforcement_status)
        $lines += ("  Violation verdict:  {0}" -f $law.violation_verdict)
        if ($law.source_document_path) {
            $lines += ("  Source path:        {0}" -f $law.source_document_path)
        }
        if ($law.enforcement_points) {
            $lines += "  Enforcement points:"
            foreach ($p in $law.enforcement_points) {
                $lines += ("    - {0}" -f $p)
            }
        }
    }

    $lines += ""
    $lines += "RAW ENFORCEMENT MAP"
    $lines += "-------------------"
    $lines += Read-TextSafe $enforcementPath

    return ($lines -join "`r`n")
}

function Run-Refresh {
    if (!(Test-Path $RefreshScript)) {
        [System.Windows.Forms.MessageBox]::Show("Refresh launcher not found:`n$RefreshScript", "Doctrinarium")
        return
    }

    $progress.Visible = $true
    $lblLoader.Visible = $true
    $lblLoader.Text = "Refreshing Doctrinarium..."
    $form.Refresh()

    $p = Start-Process pwsh -ArgumentList @(
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File", "`"$RefreshScript`""
    ) -Wait -PassThru

    Load-All

    $progress.Visible = $false
    $lblLoader.Visible = $false

    [System.Windows.Forms.MessageBox]::Show("Refresh completed. Exit code: $($p.ExitCode)", "Doctrinarium")
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
            Set-Card $cardReal "ALLOWED" $C_GREEN
        } else {
            Set-Card $cardReal "BLOCKED" $C_RED
        }

        if ($s.bootstrap_review_allowed -eq $true) {
            Set-Card $cardBootstrap "TRUE" $C_GREEN
        } else {
            Set-Card $cardBootstrap "FALSE" $C_RED
        }

        Set-Card $cardDoctrine "OWNER REVIEW" $C_YELLOW
        Set-Card $cardLaws ("{0}/{1}" -f $s.law_registry_status.not_fully_enforced_count, $s.law_registry_status.total_laws) $C_ORANGE
    }

    if ($null -ne $g) {
        Set-Card $cardOrgans ("{0} checked" -f $g.total_organs_checked) $C_ACCENT
        Set-Card $cardBlockers $g.total_blockers_found $C_RED
    }

    if ($null -ne $u) {
        Set-Card $cardUtility ("{0} backed" -f $u.summary.script_backed_count) $C_ACCENT
    }

    $txtStatus.Text = Format-StatusSummary
    $txtOrgGaps.Text = Read-TextSafe (Join-Path $Reports "ALL_ORGANS_GAP_REPORT.md")
    $txtUtilityGaps.Text = Read-TextSafe (Join-Path $Reports "ORGAN_UTILITY_GAP_REPORT.md")
    $txtLaws.Text = Format-LawsPretty
    $txtDoctrine.Text = Read-TextSafe (Join-Path $Doctrine "DOCTRINE_INDEX.json")
    $txtPaths.Text = @"
PATHS
=====

Doctrinarium:
  $Doc

Doctrine:
  $Doctrine

Laws:
  $Laws

Standards:
  $Standards

Reports:
  $Reports

Status:
  $Status

Utility:
  $Utility

Refresh launcher:
  $RefreshScript
"@
}

# ---------- Form ----------
$form = New-Object System.Windows.Forms.Form
$form.Text = "Doctrinarium Workbench v0_3"
$form.Width = 1360
$form.Height = 860
$form.StartPosition = "CenterScreen"
$form.BackColor = $C_BG

# Header
$header = New-Object System.Windows.Forms.Panel
$header.Dock = "Top"
$header.Height = 72
$header.BackColor = $C_BG2
$form.Controls.Add($header)

$lblTitle = New-Object System.Windows.Forms.Label
$lblTitle.Text = "Doctrinarium Workbench"
$lblTitle.Left = 18
$lblTitle.Top = 10
$lblTitle.Width = 500
$lblTitle.Height = 28
$lblTitle.ForeColor = $C_TEXT
$lblTitle.Font = New-Object System.Drawing.Font("Segoe UI", 18, [System.Drawing.FontStyle]::Bold)
$header.Controls.Add($lblTitle)

$lblSub = New-Object System.Windows.Forms.Label
$lblSub.Text = "Doctrine | Codex | Organ Gaps | Utility Rules"
$lblSub.Left = 20
$lblSub.Top = 42
$lblSub.Width = 560
$lblSub.Height = 18
$lblSub.ForeColor = $C_MUTED
$lblSub.Font = New-Object System.Drawing.Font("Segoe UI", 9)
$header.Controls.Add($lblSub)

# Toolbar
$toolbar = New-Object System.Windows.Forms.Panel
$toolbar.Dock = "Top"
$toolbar.Height = 58
$toolbar.BackColor = $C_BG
$form.Controls.Add($toolbar)

$btnRefresh = New-NavButton "Run Refresh" 10 { Run-Refresh }
$btnRefresh.Left = 14
$btnRefresh.Width = 130
$toolbar.Controls.Add($btnRefresh)

$btnReports = New-NavButton "Open Reports" 10 { Open-Folder $Reports }
$btnReports.Left = 156
$btnReports.Width = 120
$toolbar.Controls.Add($btnReports)

$btnDoctrineOpen = New-NavButton "Open Doctrine" 10 { Open-Folder $Doctrine }
$btnDoctrineOpen.Left = 288
$btnDoctrineOpen.Width = 120
$toolbar.Controls.Add($btnDoctrineOpen)

$btnLawsOpen = New-NavButton "Open Laws" 10 { Open-Folder $Laws }
$btnLawsOpen.Left = 420
$btnLawsOpen.Width = 110
$toolbar.Controls.Add($btnLawsOpen)

$btnStandardsOpen = New-NavButton "Open Standards" 10 { Open-Folder $Standards }
$btnStandardsOpen.Left = 542
$btnStandardsOpen.Width = 130
$toolbar.Controls.Add($btnStandardsOpen)

$btnUtilityOpen = New-NavButton "Open Utility" 10 { Open-Folder $Utility }
$btnUtilityOpen.Left = 684
$btnUtilityOpen.Width = 120
$toolbar.Controls.Add($btnUtilityOpen)

$btnReload = New-NavButton "Reload View" 10 { Load-All }
$btnReload.Left = 816
$btnReload.Width = 110
$toolbar.Controls.Add($btnReload)

$lblLoader = New-Object System.Windows.Forms.Label
$lblLoader.Text = "Refreshing..."
$lblLoader.Left = 950
$lblLoader.Top = 18
$lblLoader.Width = 180
$lblLoader.Height = 18
$lblLoader.ForeColor = $C_YELLOW
$lblLoader.Font = New-Object System.Drawing.Font("Segoe UI", 9, [System.Drawing.FontStyle]::Bold)
$lblLoader.Visible = $false
$toolbar.Controls.Add($lblLoader)

$progress = New-Object System.Windows.Forms.ProgressBar
$progress.Style = "Marquee"
$progress.MarqueeAnimationSpeed = 28
$progress.Left = 1080
$progress.Top = 14
$progress.Width = 230
$progress.Height = 24
$progress.Visible = $false
$toolbar.Controls.Add($progress)

# Cards
$cards = New-Object System.Windows.Forms.Panel
$cards.Dock = "Top"
$cards.Height = 96
$cards.BackColor = $C_BG
$form.Controls.Add($cards)

$cardReal = New-Card $cards "REAL TASK EXECUTION" 14 8 170
$cardBootstrap = New-Card $cards "BOOTSTRAP / REVIEW" 196 8 170
$cardDoctrine = New-Card $cards "DOCTRINE STATUS" 378 8 170
$cardLaws = New-Card $cards "LAWS NOT ENFORCED" 560 8 170
$cardOrgans = New-Card $cards "ORGANS CHECKED" 742 8 170
$cardBlockers = New-Card $cards "ORGAN BLOCKERS" 924 8 170
$cardUtility = New-Card $cards "UTILITIES" 1106 8 170

# Main split
$split = New-Object System.Windows.Forms.SplitContainer
$split.Dock = "Fill"
$split.SplitterDistance = 210
$split.BackColor = $C_BG
$form.Controls.Add($split)

# Left nav
$left = $split.Panel1
$left.BackColor = $C_BG2

$lblNav = New-Object System.Windows.Forms.Label
$lblNav.Text = "Navigation"
$lblNav.Left = 16
$lblNav.Top = 16
$lblNav.Width = 160
$lblNav.Height = 24
$lblNav.ForeColor = $C_TEXT
$lblNav.Font = New-Object System.Drawing.Font("Segoe UI", 12, [System.Drawing.FontStyle]::Bold)
$left.Controls.Add($lblNav)

$left.Controls.Add((New-NavButton "Status Overview" 54 { Show-View "status" }))
$left.Controls.Add((New-NavButton "Organ Gaps" 98 { Show-View "orggaps" }))
$left.Controls.Add((New-NavButton "Utility Gaps" 142 { Show-View "utility" }))
$left.Controls.Add((New-NavButton "Laws / Codex" 186 { Show-View "laws" }))
$left.Controls.Add((New-NavButton "Doctrine Index" 230 { Show-View "doctrine" }))
$left.Controls.Add((New-NavButton "Paths" 274 { Show-View "paths" }))

$lblHint = New-Object System.Windows.Forms.Label
$lblHint.Text = "Future direction:`r`n- richer panels`r`n- charts`r`n- organ cards`r`n- Sanctum integration"
$lblHint.Left = 16
$lblHint.Top = 340
$lblHint.Width = 170
$lblHint.Height = 100
$lblHint.ForeColor = $C_MUTED
$lblHint.Font = New-Object System.Drawing.Font("Segoe UI", 9)
$left.Controls.Add($lblHint)

# Right content area
$right = $split.Panel2
$right.BackColor = $C_BG

function New-ViewPanel {
    $p = New-Object System.Windows.Forms.Panel
    $p.Dock = "Fill"
    $p.BackColor = $C_BG
    $p.Visible = $false
    $right.Controls.Add($p)
    return $p
}

$viewStatus = New-ViewPanel
$viewOrgGaps = New-ViewPanel
$viewUtilityGaps = New-ViewPanel
$viewLaws = New-ViewPanel
$viewDoctrine = New-ViewPanel
$viewPaths = New-ViewPanel

$txtStatus = New-Object System.Windows.Forms.RichTextBox
Set-RichTextTheme $txtStatus
$viewStatus.Controls.Add($txtStatus)

$txtOrgGaps = New-Object System.Windows.Forms.RichTextBox
Set-RichTextTheme $txtOrgGaps
$viewOrgGaps.Controls.Add($txtOrgGaps)

$txtUtilityGaps = New-Object System.Windows.Forms.RichTextBox
Set-RichTextTheme $txtUtilityGaps
$viewUtilityGaps.Controls.Add($txtUtilityGaps)

$txtLaws = New-Object System.Windows.Forms.RichTextBox
Set-RichTextTheme $txtLaws
$viewLaws.Controls.Add($txtLaws)

$txtDoctrine = New-Object System.Windows.Forms.RichTextBox
Set-RichTextTheme $txtDoctrine
$viewDoctrine.Controls.Add($txtDoctrine)

$txtPaths = New-Object System.Windows.Forms.RichTextBox
Set-RichTextTheme $txtPaths
$viewPaths.Controls.Add($txtPaths)

# Small pulse animation on header accent feel
$PulseState = $false
$timer = New-Object System.Windows.Forms.Timer
$timer.Interval = 700
$timer.Add_Tick({
    if ($PulseState) {
        $header.BackColor = $C_BG2
        $PulseState = $false
    } else {
        $header.BackColor = [System.Drawing.Color]::FromArgb(22,32,52)
        $PulseState = $true
    }
})
$timer.Start()

Load-All
Show-View "status"

[void]$form.ShowDialog()
