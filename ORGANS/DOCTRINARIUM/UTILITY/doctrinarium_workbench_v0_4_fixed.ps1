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

$BG = [System.Drawing.Color]::FromArgb(10, 15, 28)
$PANEL = [System.Drawing.Color]::FromArgb(22, 32, 52)
$PANEL2 = [System.Drawing.Color]::FromArgb(30, 44, 70)
$TEXT = [System.Drawing.Color]::FromArgb(232, 238, 248)
$MUTED = [System.Drawing.Color]::FromArgb(150, 165, 190)
$BLUE = [System.Drawing.Color]::FromArgb(80, 160, 255)
$RED = [System.Drawing.Color]::FromArgb(255, 90, 115)
$GREEN = [System.Drawing.Color]::FromArgb(70, 210, 130)
$YELLOW = [System.Drawing.Color]::FromArgb(250, 205, 80)
$ORANGE = [System.Drawing.Color]::FromArgb(255, 160, 75)

function Read-JsonSafe($Path) {
    if (!(Test-Path $Path)) { return $null }
    try { return Get-Content $Path -Raw -Encoding UTF8 | ConvertFrom-Json }
    catch { return $null }
}

function Open-Folder($Path) {
    if (Test-Path $Path) { Start-Process explorer.exe $Path }
}

function New-Card($parent, $title, $x, $y, $w, $h) {
    $p = New-Object System.Windows.Forms.Panel
    $p.Left = $x
    $p.Top = $y
    $p.Width = $w
    $p.Height = $h
    $p.BackColor = $PANEL
    $p.BorderStyle = "FixedSingle"

    $bar = New-Object System.Windows.Forms.Panel
    $bar.Left = 0
    $bar.Top = 0
    $bar.Width = 6
    $bar.Height = $h
    $bar.BackColor = $BLUE
    $p.Controls.Add($bar)

    $t = New-Object System.Windows.Forms.Label
    $t.Left = 14
    $t.Top = 8
    $t.Width = $w - 22
    $t.Height = 20
    $t.Text = $title
    $t.ForeColor = $MUTED
    $t.Font = New-Object System.Drawing.Font("Segoe UI", 8)
    $p.Controls.Add($t)

    $v = New-Object System.Windows.Forms.Label
    $v.Left = 14
    $v.Top = 33
    $v.Width = $w - 22
    $v.Height = 28
    $v.Text = "..."
    $v.ForeColor = $TEXT
    $v.Font = New-Object System.Drawing.Font("Segoe UI", 13, [System.Drawing.FontStyle]::Bold)
    $p.Controls.Add($v)

    $parent.Controls.Add($p)

    return [pscustomobject]@{ Panel=$p; Bar=$bar; Value=$v }
}

function Set-Card($card, $text, $color) {
    $card.Value.Text = [string]$text
    $card.Value.ForeColor = $color
    $card.Bar.BackColor = $color
}

function New-Button($ButtonLabel, $x, $handler) {
    $b = New-Object System.Windows.Forms.Button
    $b.Left = $x
    $b.Top = 10
    $b.Width = 132
    $b.Height = 34
    $b.Text = $ButtonLabel
    $b.FlatStyle = "Flat"
    $b.BackColor = $PANEL2
    $b.ForeColor = $TEXT
    $b.Font = New-Object System.Drawing.Font("Segoe UI", 9, [System.Drawing.FontStyle]::Bold)
    $b.FlatAppearance.BorderColor = $BLUE
    $b.Add_Click($handler)
    return $b
}

function New-Grid() {
    $g = New-Object System.Windows.Forms.DataGridView
    $g.Dock = "Fill"
    $g.BackgroundColor = [System.Drawing.Color]::FromArgb(6, 10, 20)
    $g.GridColor = [System.Drawing.Color]::FromArgb(55, 70, 95)
    $g.ForeColor = $TEXT
    $g.DefaultCellStyle.BackColor = [System.Drawing.Color]::FromArgb(8, 13, 25)
    $g.DefaultCellStyle.ForeColor = $TEXT
    $g.DefaultCellStyle.SelectionBackColor = [System.Drawing.Color]::FromArgb(45, 90, 150)
    $g.DefaultCellStyle.SelectionForeColor = [System.Drawing.Color]::White
    $g.ColumnHeadersDefaultCellStyle.BackColor = $PANEL2
    $g.ColumnHeadersDefaultCellStyle.ForeColor = [System.Drawing.Color]::White
    $g.ColumnHeadersDefaultCellStyle.Font = New-Object System.Drawing.Font("Segoe UI", 9, [System.Drawing.FontStyle]::Bold)
    $g.EnableHeadersVisualStyles = $false
    $g.RowHeadersVisible = $false
    $g.AllowUserToAddRows = $false
    $g.AllowUserToDeleteRows = $false
    $g.ReadOnly = $true
    $g.AutoSizeColumnsMode = "Fill"
    return $g
}

function Add-Cols($grid, $cols) {
    $grid.Columns.Clear()
    foreach ($c in $cols) {
        [void]$grid.Columns.Add($c, $c)
    }
}

function Add-Row($grid, $values) {
    [void]$grid.Rows.Add($values)
}

function New-PanelTitle($parent, $TitleText, $x, $y, $w) {
    $l = New-Object System.Windows.Forms.Label
    $l.Left = $x
    $l.Top = $y
    $l.Width = $w
    $l.Height = 28
    $l.Text = $TitleText
    $l.ForeColor = $TEXT
    $l.Font = New-Object System.Drawing.Font("Segoe UI", 12, [System.Drawing.FontStyle]::Bold)
    $parent.Controls.Add($l)
    return $l
}

function Run-Refresh {
    if (!(Test-Path $RefreshScript)) {
        [System.Windows.Forms.MessageBox]::Show("Refresh launcher not found:`n$RefreshScript", "Doctrinarium")
        return
    }

    $progress.Visible = $true
    $lblRefresh.Text = "Refreshing..."
    $form.Refresh()

    $p = Start-Process pwsh -ArgumentList @(
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File", "`"$RefreshScript`""
    ) -Wait -PassThru

    Load-All

    $progress.Visible = $false
    $lblRefresh.Text = "Ready"
    [System.Windows.Forms.MessageBox]::Show("Refresh completed. Exit code: $($p.ExitCode)", "Doctrinarium")
}

function Load-All {
    $statusJson = Join-Path $Status "DOCTRINARIUM_STATUS.json"
    $gapJson = Join-Path $Reports "ALL_ORGANS_GAP_REPORT.json"
    $utilityJson = Join-Path $Reports "ORGAN_UTILITY_GAP_REPORT.json"
    $lawJson = Join-Path $Laws "LAW_INDEX.json"

    $s = Read-JsonSafe $statusJson
    $g = Read-JsonSafe $gapJson
    $u = Read-JsonSafe $utilityJson
    $laws = Read-JsonSafe $lawJson

    if ($s) {
        if ($s.real_task_execution_allowed -eq $true) {
            Set-Card $cardReal "ALLOWED" $GREEN
        } else {
            Set-Card $cardReal "BLOCKED" $RED
        }

        if ($s.bootstrap_review_allowed -eq $true) {
            Set-Card $cardBoot "TRUE" $GREEN
        } else {
            Set-Card $cardBoot "FALSE" $RED
        }

        Set-Card $cardDoctrine "OWNER REVIEW" $YELLOW
        Set-Card $cardLaws ("{0}/{1}" -f $s.law_registry_status.not_fully_enforced_count, $s.law_registry_status.total_laws) $ORANGE
    }

    if ($g) {
        Set-Card $cardOrgans ("{0}" -f $g.total_organs_checked) $BLUE
        Set-Card $cardBlockers ("{0}" -f $g.total_blockers_found) $RED
    }

    if ($u) {
        Set-Card $cardUtility ("{0} backed" -f $u.summary.script_backed_count) $BLUE
    }

    # Dashboard summary text
    $txtDashboard.Clear()
    $txtDashboard.SelectionColor = $TEXT
    $txtDashboard.AppendText("CURRENT DOCTRINARIUM STATE`r`n")
    $txtDashboard.AppendText("============================`r`n`r`n")
    if ($s) {
        $txtDashboard.AppendText("Verdict: $($s.verdict)`r`n")
        $txtDashboard.AppendText("Real task execution: $($s.real_task_execution_allowed)`r`n")
        $txtDashboard.AppendText("Bootstrap/review: $($s.bootstrap_review_allowed)`r`n`r`n")
        $txtDashboard.AppendText("Doctrine:`r`n")
        $txtDashboard.AppendText("  Passport:     $($s.passport_status)`r`n")
        $txtDashboard.AppendText("  Constitution: $($s.constitution_status)`r`n")
        $txtDashboard.AppendText("  Codex:        $($s.codex_status)`r`n`r`n")
        $txtDashboard.AppendText("Current blockers:`r`n")
        foreach ($b in $s.doctrinarium_organ_status.current_blockers) {
            $txtDashboard.AppendText("  - $b`r`n")
        }
    }

    # Organ overview grid
    $gridOrg.Rows.Clear()
    if ($g -and $g.organs) {
        foreach ($o in $g.organs) {
            Add-Row $gridOrg @(
                $o.organ_id,
                $o.classification,
                $o.blockers.Count,
                $o.organ_contract_exists,
                $o.self_report_exists,
                $o.receipts_exists,
                ($o.why_not_canon -join "; ")
            )
        }
    }

    # Major gaps grid
    $gridGaps.Rows.Clear()
    if ($g -and $g.major_gaps) {
        foreach ($gap in $g.major_gaps) {
            Add-Row $gridGaps @($gap.organ, $gap.gap)
        }
    }

    # Utility grid
    $gridUtility.Rows.Clear()
    if ($u -and $u.organs) {
        foreach ($o in $u.organs) {
            Add-Row $gridUtility @(
                $o.organ_id,
                $o.organ_status,
                $o.utility_declared,
                $o.script_backed,
                (($o.warnings + $o.blockers) -join "; ")
            )
        }
    }

    # Laws grid
    $gridLaws.Rows.Clear()
    if ($laws) {
        $arr = $null
        if ($laws.laws) { $arr = $laws.laws }
        elseif ($laws.mandatory_laws) { $arr = $laws.mandatory_laws }
        elseif ($laws.entries) { $arr = $laws.entries }

        if ($arr) {
            foreach ($law in $arr) {
                Add-Row $gridLaws @(
                    $law.law_id,
                    $law.title,
                    $law.severity,
                    $law.enforcement_status,
                    $law.violation_verdict
                )
            }
        }
    }

    # Paths
    $txtPaths.Clear()
    $txtPaths.AppendText("MAIN PATHS`r`n")
    $txtPaths.AppendText("==========`r`n`r`n")
    $txtPaths.AppendText("Doctrinarium:`r`n  $Doc`r`n`r`n")
    $txtPaths.AppendText("Reports:`r`n  $Reports`r`n`r`n")
    $txtPaths.AppendText("Status:`r`n  $Status`r`n`r`n")
    $txtPaths.AppendText("Doctrine:`r`n  $Doctrine`r`n`r`n")
    $txtPaths.AppendText("Laws:`r`n  $Laws`r`n`r`n")
    $txtPaths.AppendText("Standards:`r`n  $Standards`r`n`r`n")
    $txtPaths.AppendText("Utility:`r`n  $Utility`r`n`r`n")
    $txtPaths.AppendText("Refresh launcher:`r`n  $RefreshScript`r`n")
}

# Form
$form = New-Object System.Windows.Forms.Form
$form.Text = "Doctrinarium Workbench v0_4"
$form.Width = 1380
$form.Height = 860
$form.StartPosition = "CenterScreen"
$form.BackColor = $BG

# Top cards
$cards = New-Object System.Windows.Forms.Panel
$cards.Dock = "Top"
$cards.Height = 96
$cards.BackColor = $BG
$form.Controls.Add($cards)

$cardReal = New-Card $cards "REAL TASK" 16 10 170 74
$cardBoot = New-Card $cards "BOOTSTRAP" 198 10 170 74
$cardDoctrine = New-Card $cards "DOCTRINE" 380 10 170 74
$cardLaws = New-Card $cards "LAWS OPEN" 562 10 170 74
$cardOrgans = New-Card $cards "ORGANS" 744 10 170 74
$cardBlockers = New-Card $cards "BLOCKERS" 926 10 170 74
$cardUtility = New-Card $cards "UTILITY" 1108 10 170 74

# Toolbar
$tools = New-Object System.Windows.Forms.Panel
$tools.Dock = "Top"
$tools.Height = 56
$tools.BackColor = $BG
$form.Controls.Add($tools)

$tools.Controls.Add((New-Button "Run Refresh" 16 { Run-Refresh }))
$tools.Controls.Add((New-Button "Open Reports" 160 { Open-Folder $Reports }))
$tools.Controls.Add((New-Button "Open Doctrine" 304 { Open-Folder $Doctrine }))
$tools.Controls.Add((New-Button "Open Laws" 448 { Open-Folder $Laws }))
$tools.Controls.Add((New-Button "Open Utility" 592 { Open-Folder $Utility }))
$tools.Controls.Add((New-Button "Reload View" 736 { Load-All }))

$lblRefresh = New-Object System.Windows.Forms.Label
$lblRefresh.Left = 900
$lblRefresh.Top = 18
$lblRefresh.Width = 100
$lblRefresh.Height = 20
$lblRefresh.Text = "Ready"
$lblRefresh.ForeColor = $MUTED
$lblRefresh.Font = New-Object System.Drawing.Font("Segoe UI", 9, [System.Drawing.FontStyle]::Bold)
$tools.Controls.Add($lblRefresh)

$progress = New-Object System.Windows.Forms.ProgressBar
$progress.Left = 1000
$progress.Top = 15
$progress.Width = 260
$progress.Height = 22
$progress.Style = "Marquee"
$progress.Visible = $false
$tools.Controls.Add($progress)

# Header
$header = New-Object System.Windows.Forms.Panel
$header.Dock = "Top"
$header.Height = 70
$header.BackColor = [System.Drawing.Color]::FromArgb(17, 25, 42)
$form.Controls.Add($header)

$title = New-Object System.Windows.Forms.Label
$title.Text = "Doctrinarium Control Panel"
$title.Left = 22
$title.Top = 10
$title.Width = 520
$title.Height = 30
$title.ForeColor = $TEXT
$title.Font = New-Object System.Drawing.Font("Segoe UI", 18, [System.Drawing.FontStyle]::Bold)
$header.Controls.Add($title)

$sub = New-Object System.Windows.Forms.Label
$sub.Text = "Readable panels for doctrine, laws, organ gaps and utility state"
$sub.Left = 24
$sub.Top = 42
$sub.Width = 700
$sub.Height = 20
$sub.ForeColor = $MUTED
$sub.Font = New-Object System.Drawing.Font("Segoe UI", 9)
$header.Controls.Add($sub)

# Tabs
$tabs = New-Object System.Windows.Forms.TabControl
$tabs.Dock = "Fill"
$tabs.Font = New-Object System.Drawing.Font("Segoe UI", 9)
$form.Controls.Add($tabs)

function New-Tab($name) {
    $t = New-Object System.Windows.Forms.TabPage
    $t.Text = $name
    $t.BackColor = $BG
    $tabs.TabPages.Add($t)
    return $t
}

$tabDash = New-Tab "Dashboard"
$tabOrg = New-Tab "Organ Overview"
$tabGaps = New-Tab "Major Gaps"
$tabUtility = New-Tab "Utility"
$tabLaws = New-Tab "Laws"
$tabPaths = New-Tab "Paths"

# Dashboard
New-PanelTitle $tabDash "Summary" 16 14 300 | Out-Null
$txtDashboard = New-Object System.Windows.Forms.RichTextBox
$txtDashboard.Left = 16
$txtDashboard.Top = 48
$txtDashboard.Width = 620
$txtDashboard.Height = 580
$txtDashboard.BackColor = [System.Drawing.Color]::FromArgb(6, 10, 20)
$txtDashboard.ForeColor = $TEXT
$txtDashboard.Font = New-Object System.Drawing.Font("Consolas", 10)
$txtDashboard.BorderStyle = "FixedSingle"
$txtDashboard.ReadOnly = $true
$tabDash.Controls.Add($txtDashboard)

New-PanelTitle $tabDash "Organ Snapshot" 660 14 300 | Out-Null
$gridOrg = New-Grid
$gridOrg.Left = 660
$gridOrg.Top = 48
$gridOrg.Width = 650
$gridOrg.Height = 580
$gridOrg.Dock = "None"
Add-Cols $gridOrg @("Organ", "Class", "Blockers", "Contract", "SelfReport", "Receipts", "WhyNotCanon")
$tabDash.Controls.Add($gridOrg)

# Organ overview full
$gridOrgFull = New-Grid
Add-Cols $gridOrgFull @("Organ", "Class", "Blockers", "Contract", "SelfReport", "Receipts", "WhyNotCanon")
$tabOrg.Controls.Add($gridOrgFull)

# Major gaps
$gridGaps = New-Grid
Add-Cols $gridGaps @("Organ", "Gap")
$tabGaps.Controls.Add($gridGaps)

# Utility
$gridUtility = New-Grid
Add-Cols $gridUtility @("Organ", "Status", "UtilityDeclared", "ScriptBacked", "WarningsOrBlockers")
$tabUtility.Controls.Add($gridUtility)

# Laws
$gridLaws = New-Grid
Add-Cols $gridLaws @("LawId", "Title", "Severity", "Enforcement", "Verdict")
$tabLaws.Controls.Add($gridLaws)

# Paths
$txtPaths = New-Object System.Windows.Forms.RichTextBox
$txtPaths.Dock = "Fill"
$txtPaths.BackColor = [System.Drawing.Color]::FromArgb(6, 10, 20)
$txtPaths.ForeColor = $TEXT
$txtPaths.Font = New-Object System.Drawing.Font("Consolas", 10)
$txtPaths.ReadOnly = $true
$tabPaths.Controls.Add($txtPaths)

# Keep full org grid in sync by pointing to same source on reload
function Copy-GridRows($src, $dst) {
    $dst.Rows.Clear()
    foreach ($row in $src.Rows) {
        if (!$row.IsNewRow) {
            $vals = @()
            foreach ($cell in $row.Cells) { $vals += $cell.Value }
            Add-Row $dst $vals
        }
    }
}

$oldLoad = ${function:Load-All}
function Load-All-And-Copy {
    Load-All
    Copy-GridRows $gridOrg $gridOrgFull
}

Load-All-And-Copy

# override refresh reload calls
$btnReload = $null

[void]$form.ShowDialog()
