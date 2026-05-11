Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName PresentationCore
Add-Type -AssemblyName WindowsBase

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$script:RepoRoot = "E:\IMPERIUM"
$script:GeneralTasksRoot = "E:\IMPERIUM\ASTRONOMICON\GENERAL_TASKS"
$script:ParserPath = "E:\IMPERIUM\TOOLS\astronomicon_parse_general_task_v0_2.ps1"
$script:ExportLocalTasksPath = "E:\IMPERIUM\TOOLS\astronomicon_export_local_tasks_for_speculum_v0_2.ps1"
$script:ImportLocalTaskRefinementsPath = "E:\IMPERIUM\TOOLS\astronomicon_import_local_task_refinements_v0_2.ps1"
$script:DecomposeLocalTaskPath = "E:\IMPERIUM\TOOLS\astronomicon_decompose_local_task_to_stages_v0_2.ps1"
$script:ExportStageMapPath = "E:\IMPERIUM\TOOLS\astronomicon_export_stage_map_for_speculum_v0_1.ps1"
$script:ImportStageRefinementsPath = "E:\IMPERIUM\TOOLS\astronomicon_import_stage_refinements_v0_1.ps1"
$script:VerifyTaskIdSyncPath = "E:\IMPERIUM\TOOLS\astronomicon_verify_task_id_sync_v0_1.ps1"
$script:CommitPushPath = "E:\IMPERIUM\TOOLS\astronomicon_commit_push_task_plan_v0_1.ps1"

$script:CurrentTaskId = $null
$script:CurrentTaskRoot = $null
$script:CurrentInputPath = $null
$script:CurrentOutputRoot = $null

$script:PipelineState = [ordered]@{
    general_task_created = "READY"
    local_tasks_created = "READY"
    speculum_local_exported = "READY"
    local_refinements_imported = "READY"
    stages_created = "READY"
    speculum_stage_exported = "READY"
    stage_refinements_imported = "READY"
    commit_ready = "READY"
    push_verified = "READY"
}

New-Item -ItemType Directory -Force -Path $script:GeneralTasksRoot | Out-Null

function Write-Utf8Bom {
    param([string]$Path, [string]$Content)
    $directory = Split-Path -Parent $Path
    if ($directory -and -not (Test-Path -LiteralPath $directory)) {
        New-Item -ItemType Directory -Force -Path $directory | Out-Null
    }
    $utf8Bom = New-Object System.Text.UTF8Encoding($true)
    [System.IO.File]::WriteAllText($Path, ($Content -replace "`r`n","`n" -replace "`r","`n").Replace("`n","`r`n"), $utf8Bom)
}

function Log {
    param([string]$Message)
    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $script:txtLog.AppendText("[$stamp] $Message`r`n")
    $script:txtLog.ScrollToEnd()
}

function Status {
    param(
        [string]$State,
        [string]$Message
    )
    $script:txtStatus.Text = "$State :: $Message"
    Log "$State :: $Message"
}

function Set-PipelineState {
    param(
        [string]$Key,
        [string]$Value
    )
    $script:PipelineState[$Key] = $Value
    Refresh-PipelinePanel
}

function Refresh-PipelinePanel {
    $script:txtPipelineState.Text = @(
        "General Task created: $($script:PipelineState.general_task_created)"
        "Local Tasks created: $($script:PipelineState.local_tasks_created)"
        "Speculum Local Review exported: $($script:PipelineState.speculum_local_exported)"
        "Local Refinements imported: $($script:PipelineState.local_refinements_imported)"
        "Stages created: $($script:PipelineState.stages_created)"
        "Speculum Stage Review exported: $($script:PipelineState.speculum_stage_exported)"
        "Stage Refinements imported: $($script:PipelineState.stage_refinements_imported)"
        "Commit ready: $($script:PipelineState.commit_ready)"
        "Push verified: $($script:PipelineState.push_verified)"
    ) -join "`r`n"
}

function Get-ScalarFieldFromText {
    param([string]$Text, [string]$FieldName)
    $normalized = (($Text -replace "`r`n","`n") -replace "`r","`n")
    $escaped = [regex]::Escape($FieldName)
    $pattern = "(?ms)^$escaped\s*:\s*\n(?<v>.*?)(?=\n\n[A-Z0-9_]+:|\n\nBEGIN_|\n---|$)"
    $match = [regex]::Match($normalized, $pattern)
    if ($match.Success) { return $match.Groups["v"].Value.Trim() }
    return ""
}

function Ensure-TaskLayout {
    param([string]$TaskId)
    $taskRoot = Join-Path $script:GeneralTasksRoot $TaskId
    $inputRoot = Join-Path $taskRoot "INPUT"
    $outputRoot = Join-Path $taskRoot "OUTPUT"
    $stateRoot = Join-Path $taskRoot "STATE"
    New-Item -ItemType Directory -Force -Path $taskRoot, $inputRoot, $outputRoot, $stateRoot | Out-Null

    $script:CurrentTaskId = $TaskId
    $script:CurrentTaskRoot = $taskRoot
    $script:CurrentInputPath = Join-Path $inputRoot "GENERAL_TASK_INPUT.txt"
    $script:CurrentOutputRoot = $outputRoot
}

function New-DefaultTaskId {
    $stamp = Get-Date -Format "yyyyMMdd"
    return "GTASK-$stamp-ASTRONOMICON-DASHBOARD-V0_6"
}

function Get-TaskTemplate {
    param(
        [string]$TaskId,
        [string]$Title,
        [string]$Code,
        [string]$Mode,
        [string]$Priority
    )
    return @"
ASTRONOMICON_GENERAL_TASK_V0_1
ENCODING: UTF-8-BOM
LINE_ENDINGS: CRLF

GENERAL_TASK_ID:
$TaskId

GENERAL_TASK_TITLE:
$Title

GENERAL_TASK_CODE:
$Code

AUTHOR:
Owner

EXECUTION_INTENT:
$Mode

PRIORITY:
$Priority

BEGIN_GOAL
Describe the main goal of this General Task.
END_GOAL

BEGIN_CONTEXT
Describe what already exists, why this task is needed, and dependencies.
END_CONTEXT

BEGIN_CURRENT_PROBLEM
Describe the current missing capability or technical blocker.
END_CURRENT_PROBLEM

BEGIN_EXPECTED_FINAL_STATE
- Describe expected final state.
- Describe required scripts/files/artifacts.
- Describe required verification.
END_EXPECTED_FINAL_STATE

BEGIN_HARD_CONSTRAINTS
- No secret leakage.
- No fake green states.
- Evidence and receipts required.
END_HARD_CONSTRAINTS

BEGIN_DO_NOT_DO
- Do not broaden scope without Owner approval.
- Do not skip ID and schema checks.
END_DO_NOT_DO

BEGIN_PLAN_ITEMS

ITEM_ID: PI-001
TITLE: Build first local task
TEXT:
Describe the first local task.
EXPECTED_OUTPUT:
Describe expected output.
REQUIRED_ORGANS:
Astronomicon, Administratum
EXECUTION_MODE:
manual
DEPENDS_ON:
none
END_ITEM

ITEM_ID: PI-002
TITLE: Build second local task
TEXT:
Describe the second local task.
EXPECTED_OUTPUT:
Describe expected output.
REQUIRED_ORGANS:
Astronomicon, Mechanicus
EXECUTION_MODE:
scripted
DEPENDS_ON:
PI-001
END_ITEM

END_PLAN_ITEMS

BEGIN_KNOWN_RISKS
- Add known technical risks.
END_KNOWN_RISKS

BEGIN_REQUIRED_ORGANS
- Astronomicon
- Administratum
END_REQUIRED_ORGANS

BEGIN_REQUIRED_INPUTS
- Add required inputs.
END_REQUIRED_INPUTS

BEGIN_EXPECTED_ARTIFACTS
- Add expected artifacts.
END_EXPECTED_ARTIFACTS

BEGIN_OWNER_NOTES
Owner notes.
END_OWNER_NOTES
"@
}

function Show-PreviewFile {
    param([string]$Path)
    if (Test-Path -LiteralPath $Path) {
        $script:txtPreview.Text = Get-Content -LiteralPath $Path -Encoding UTF8 -Raw
        $script:txtPreviewFile.Text = $Path
    }
    else {
        throw "Preview file not found: $Path"
    }
}

function Invoke-BackendScript {
    param(
        [string]$ScriptPath,
        [string[]]$Parameters
    )
    if (-not (Test-Path -LiteralPath $ScriptPath)) {
        throw "Backend script not found: $ScriptPath"
    }
    $args = @("-ExecutionPolicy", "Bypass", "-File", $ScriptPath) + $Parameters
    $result = & powershell.exe @args 2>&1 | Out-String
    if ($result.Trim()) { Log ($result.Trim()) }
    if ($LASTEXITCODE -ne 0) {
        throw "Backend script failed: $ScriptPath"
    }
}

function New-IdSyncReceiptPath {
    param([string]$ActionName)
    $receiptRoot = Join-Path $script:CurrentOutputRoot "RECEIPTS\ID_SYNC"
    New-Item -ItemType Directory -Force -Path $receiptRoot | Out-Null
    $stamp = Get-Date -Format "yyyyMMdd-HHmmss-fff"
    return Join-Path $receiptRoot "$ActionName-$stamp.json"
}

function Invoke-TaskIdSyncCheck {
    param(
        [string]$ActionName,
        [bool]$RequireRegistry
    )
    if (-not $script:CurrentInputPath -or -not (Test-Path -LiteralPath $script:CurrentInputPath)) {
        throw "No General Task input file found."
    }
    if (-not $script:CurrentTaskRoot -or -not (Test-Path -LiteralPath $script:CurrentTaskRoot)) {
        throw "No task root found."
    }
    if ([string]::IsNullOrWhiteSpace($script:CurrentTaskId)) {
        throw "Dashboard task ID is empty."
    }

    $receiptPath = New-IdSyncReceiptPath -ActionName $ActionName
    Invoke-BackendScript -ScriptPath $script:VerifyTaskIdSyncPath -Parameters @(
        "-InputPath", $script:CurrentInputPath,
        "-TaskRoot", $script:CurrentTaskRoot,
        "-DashboardTaskId", $script:CurrentTaskId,
        "-ReceiptPath", $receiptPath,
        "-RequireRegistry", $(if ($RequireRegistry) { '1' } else { '0' })
    )
    return $receiptPath
}

function Refresh-LocalTasks {
    $script:lstLocalTasks.Items.Clear()
    if (-not $script:CurrentOutputRoot) { return }
    $localRoot = Join-Path $script:CurrentOutputRoot "LOCAL_TASKS"
    if (-not (Test-Path -LiteralPath $localRoot)) { return }
    Get-ChildItem -LiteralPath $localRoot -Directory | Sort-Object Name | ForEach-Object {
        [void]$script:lstLocalTasks.Items.Add($_.Name)
    }
}

function Refresh-StagesForSelectedLocalTask {
    $script:lstStages.Items.Clear()
    if (-not $script:CurrentOutputRoot) { return }
    if (-not $script:lstLocalTasks.SelectedItem) { return }
    $localTaskId = [string]$script:lstLocalTasks.SelectedItem
    $stagesRoot = Join-Path $script:CurrentOutputRoot "STAGE_MAPS\$localTaskId\STAGES"
    if (-not (Test-Path -LiteralPath $stagesRoot)) { return }
    Get-ChildItem -LiteralPath $stagesRoot -Directory | Sort-Object Name | ForEach-Object {
        [void]$script:lstStages.Items.Add($_.Name)
    }
}

function Refresh-View {
    Refresh-LocalTasks
    Refresh-StagesForSelectedLocalTask
}

function Show-GeneralTaskEditor {
    $dialogXaml = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="Create General Task"
        Width="1100"
        Height="840"
        WindowStartupLocation="CenterScreen"
        Background="#070B15"
        Foreground="#EAF0FF">
    <Window.Resources>
        <Style TargetType="TextBox">
            <Setter Property="Background" Value="#091022"/>
            <Setter Property="Foreground" Value="#F4F7FF"/>
            <Setter Property="BorderBrush" Value="#2D426B"/>
            <Setter Property="Padding" Value="7,4,7,4"/>
            <Setter Property="FontSize" Value="13"/>
        </Style>
        <Style TargetType="Button">
            <Setter Property="Height" Value="38"/>
            <Setter Property="Margin" Value="0,0,8,0"/>
            <Setter Property="Background" Value="#142545"/>
            <Setter Property="Foreground" Value="#F1F5FF"/>
            <Setter Property="BorderBrush" Value="#334C7A"/>
        </Style>
    </Window.Resources>
    <Grid Margin="16">
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="*"/>
            <RowDefinition Height="Auto"/>
        </Grid.RowDefinitions>
        <StackPanel Grid.Row="0" Margin="0,0,0,12">
            <TextBlock Text="Create General Task" FontSize="28" FontWeight="Bold"/>
            <TextBlock Text="Fill strict English form. Saved form controls the dashboard task ID." Foreground="#8FA2CC" Margin="0,5,0,0"/>
        </StackPanel>
        <Grid Grid.Row="1" Margin="0,0,0,12">
            <Grid.ColumnDefinitions>
                <ColumnDefinition Width="2*"/>
                <ColumnDefinition Width="2*"/>
                <ColumnDefinition Width="1*"/>
                <ColumnDefinition Width="1*"/>
            </Grid.ColumnDefinitions>
            <Grid.RowDefinitions>
                <RowDefinition Height="Auto"/>
                <RowDefinition Height="Auto"/>
            </Grid.RowDefinitions>
            <StackPanel Grid.Row="0" Grid.Column="0" Margin="0,0,8,8">
                <TextBlock Text="GENERAL_TASK_ID" Foreground="#8DA7FF"/>
                <TextBox Name="dlgTaskId"/>
            </StackPanel>
            <StackPanel Grid.Row="0" Grid.Column="1" Margin="8,0,8,8">
                <TextBlock Text="TITLE" Foreground="#8DA7FF"/>
                <TextBox Name="dlgTitle"/>
            </StackPanel>
            <StackPanel Grid.Row="0" Grid.Column="2" Margin="8,0,8,8">
                <TextBlock Text="MODE" Foreground="#8DA7FF"/>
                <TextBox Name="dlgMode"/>
            </StackPanel>
            <StackPanel Grid.Row="0" Grid.Column="3" Margin="8,0,0,8">
                <TextBlock Text="PRIORITY" Foreground="#8DA7FF"/>
                <TextBox Name="dlgPriority"/>
            </StackPanel>
            <StackPanel Grid.Row="1" Grid.Column="0" Grid.ColumnSpan="4">
                <TextBlock Text="GENERAL_TASK_CODE" Foreground="#8DA7FF"/>
                <TextBox Name="dlgCode"/>
            </StackPanel>
        </Grid>
        <Border Grid.Row="2" CornerRadius="14" Background="#0E172C" BorderBrush="#26395E" BorderThickness="1" Padding="12">
            <DockPanel>
                <TextBlock DockPanel.Dock="Top" Text="General Task Form" Foreground="#8DA7FF" FontWeight="SemiBold" Margin="0,0,0,8"/>
                <TextBox Name="dlgForm"
                         AcceptsReturn="True"
                         AcceptsTab="True"
                         TextWrapping="Wrap"
                         VerticalScrollBarVisibility="Auto"
                         HorizontalScrollBarVisibility="Auto"
                         FontFamily="Consolas"
                         FontSize="14"
                         Background="#070C18"
                         Foreground="#F6F8FF"
                         BorderThickness="0"/>
            </DockPanel>
        </Border>
        <StackPanel Grid.Row="3" Orientation="Horizontal" HorizontalAlignment="Right" Margin="0,14,0,0">
            <Button Name="dlgLoadTemplate" Content="Load Template" Width="130"/>
            <Button Name="dlgPasteClipboard" Content="Paste Clipboard" Width="140"/>
            <Button Name="dlgSave" Content="Save General Task" Width="160" Background="#13A9B8" BorderBrush="#13A9B8"/>
            <Button Name="dlgCancel" Content="Cancel" Width="100"/>
        </StackPanel>
    </Grid>
</Window>
"@

    [xml]$xml = $dialogXaml
    $reader = New-Object System.Xml.XmlNodeReader $xml
    $dialog = [Windows.Markup.XamlReader]::Load($reader)

    $dlgTaskId = $dialog.FindName("dlgTaskId")
    $dlgTitle = $dialog.FindName("dlgTitle")
    $dlgMode = $dialog.FindName("dlgMode")
    $dlgPriority = $dialog.FindName("dlgPriority")
    $dlgCode = $dialog.FindName("dlgCode")
    $dlgForm = $dialog.FindName("dlgForm")
    $dlgLoadTemplate = $dialog.FindName("dlgLoadTemplate")
    $dlgPasteClipboard = $dialog.FindName("dlgPasteClipboard")
    $dlgSave = $dialog.FindName("dlgSave")
    $dlgCancel = $dialog.FindName("dlgCancel")

    $dlgTaskId.Text = New-DefaultTaskId
    $dlgTitle.Text = "Astronomicon General Task v0.6"
    $dlgCode.Text = "ASTRONOMICON-DASHBOARD"
    $dlgMode.Text = "manual"
    $dlgPriority.Text = "high"

    $loadTemplate = {
        $dlgForm.Text = Get-TaskTemplate -TaskId ($dlgTaskId.Text.Trim()) -Title ($dlgTitle.Text.Trim()) -Code ($dlgCode.Text.Trim()) -Mode ($dlgMode.Text.Trim()) -Priority ($dlgPriority.Text.Trim())
    }
    $dlgLoadTemplate.Add_Click($loadTemplate)

    $dlgPasteClipboard.Add_Click({
        if ([System.Windows.Clipboard]::ContainsText()) {
            $dlgForm.Text = [System.Windows.Clipboard]::GetText()
            $foundId = Get-ScalarFieldFromText -Text $dlgForm.Text -FieldName "GENERAL_TASK_ID"
            $foundTitle = Get-ScalarFieldFromText -Text $dlgForm.Text -FieldName "GENERAL_TASK_TITLE"
            $foundCode = Get-ScalarFieldFromText -Text $dlgForm.Text -FieldName "GENERAL_TASK_CODE"
            $foundMode = Get-ScalarFieldFromText -Text $dlgForm.Text -FieldName "EXECUTION_INTENT"
            $foundPriority = Get-ScalarFieldFromText -Text $dlgForm.Text -FieldName "PRIORITY"
            if ($foundId) { $dlgTaskId.Text = $foundId }
            if ($foundTitle) { $dlgTitle.Text = $foundTitle }
            if ($foundCode) { $dlgCode.Text = $foundCode }
            if ($foundMode) { $dlgMode.Text = $foundMode }
            if ($foundPriority) { $dlgPriority.Text = $foundPriority }
        }
    })

    $dlgSave.Add_Click({
        try {
            if ([string]::IsNullOrWhiteSpace($dlgForm.Text)) { throw "Form is empty." }
            $formTaskId = Get-ScalarFieldFromText -Text $dlgForm.Text -FieldName "GENERAL_TASK_ID"
            if ([string]::IsNullOrWhiteSpace($formTaskId)) { throw "GENERAL_TASK_ID missing in form." }
            Ensure-TaskLayout -TaskId $formTaskId
            Write-Utf8Bom -Path $script:CurrentInputPath -Content $dlgForm.Text

            $script:txtMainTaskId.Text = $formTaskId
            $script:txtMainTaskTitle.Text = (Get-ScalarFieldFromText -Text $dlgForm.Text -FieldName "GENERAL_TASK_TITLE")
            $script:txtMainTaskRoot.Text = $script:CurrentTaskRoot
            $script:txtGeneralCardTitle.Text = $script:txtMainTaskTitle.Text
            $script:txtGeneralCardSubtitle.Text = $formTaskId
            $script:txtGeneralCardMeta.Text = "mode: $($dlgMode.Text.Trim()) | priority: $($dlgPriority.Text.Trim())"

            Set-PipelineState -Key "general_task_created" -Value "PASS"
            Set-PipelineState -Key "local_tasks_created" -Value "READY"
            Set-PipelineState -Key "speculum_local_exported" -Value "READY"
            Set-PipelineState -Key "local_refinements_imported" -Value "READY"
            Set-PipelineState -Key "stages_created" -Value "READY"
            Set-PipelineState -Key "speculum_stage_exported" -Value "READY"
            Set-PipelineState -Key "stage_refinements_imported" -Value "READY"
            Set-PipelineState -Key "commit_ready" -Value "READY"
            Set-PipelineState -Key "push_verified" -Value "READY"

            Show-PreviewFile -Path $script:CurrentInputPath
            Status -State "PASS" -Message "General Task saved and ID synchronized."
            $dialog.DialogResult = $true
            $dialog.Close()
        }
        catch {
            [System.Windows.MessageBox]::Show($_.Exception.Message, "Save failed", "OK", "Error") | Out-Null
        }
    })

    $dlgCancel.Add_Click({
        $dialog.DialogResult = $false
        $dialog.Close()
    })

    & $loadTemplate
    [void]$dialog.ShowDialog()
}

[xml]$xaml = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="IMPERIUM :: ASTRONOMICON DASHBOARD v0.6"
        Height="1000"
        Width="1700"
        WindowStartupLocation="CenterScreen"
        Background="#070B15"
        Foreground="#EAF0FF"
        ResizeMode="CanResize">
    <Window.Resources>
        <Style TargetType="Button">
            <Setter Property="Height" Value="38"/>
            <Setter Property="Margin" Value="0,0,0,8"/>
            <Setter Property="Background" Value="#142545"/>
            <Setter Property="Foreground" Value="#F1F5FF"/>
            <Setter Property="BorderBrush" Value="#334C7A"/>
            <Setter Property="Cursor" Value="Hand"/>
        </Style>
        <Style TargetType="TextBox">
            <Setter Property="Background" Value="#091022"/>
            <Setter Property="Foreground" Value="#F4F7FF"/>
            <Setter Property="BorderBrush" Value="#2D426B"/>
            <Setter Property="Padding" Value="7,4,7,4"/>
        </Style>
    </Window.Resources>
    <Grid Margin="12">
        <Grid.ColumnDefinitions>
            <ColumnDefinition Width="300"/>
            <ColumnDefinition Width="*"/>
            <ColumnDefinition Width="430"/>
        </Grid.ColumnDefinitions>

        <Border Grid.Column="0" CornerRadius="18" Background="#0D1426" BorderBrush="#273858" BorderThickness="1" Margin="0,0,10,0">
            <DockPanel Margin="16">
                <StackPanel DockPanel.Dock="Top">
                    <TextBlock Text="ASTRONOMICON" FontSize="23" FontWeight="Bold"/>
                    <TextBlock Text="Pipeline forge v0.6" Foreground="#8DA7FF" Margin="0,4,0,16"/>
                    <Button Name="btnCreateGeneral" Content="1) Create General Task" Background="#5A3DF0" BorderBrush="#5A3DF0"/>
                    <Button Name="btnParse" Content="2) Parse to Local Tasks" Background="#13A9B8" BorderBrush="#13A9B8"/>
                    <Button Name="btnExportLocalSpeculum" Content="3) Export Local Tasks"/>
                    <Button Name="btnImportLocalSpeculum" Content="4) Import Local Refinements"/>
                    <Button Name="btnDecomposeSelected" Content="5) Decompose Selected LTASK" Background="#5A3DF0" BorderBrush="#5A3DF0"/>
                    <Button Name="btnExportStageSpeculum" Content="6) Export Stages for Speculum"/>
                    <Button Name="btnImportStageSpeculum" Content="7) Import Stage Refinements"/>
                    <Button Name="btnCommitTaskPlan" Content="8) Commit Task Plan" Background="#1F7A4D" BorderBrush="#1F7A4D"/>
                    <Button Name="btnPushTaskPlan" Content="9) Push Task Plan" Background="#29639A" BorderBrush="#29639A"/>
                    <Button Name="btnRefresh" Content="Refresh Pyramid"/>
                    <Button Name="btnOpenSpeculum" Content="Open Speculum Folder"/>
                    <Button Name="btnOpenTaskRoot" Content="Open Task Root"/>
                    <Button Name="btnOpenOutput" Content="Open Output"/>
                </StackPanel>
            </DockPanel>
        </Border>

        <Border Grid.Column="1" CornerRadius="18" Background="#0A1020" BorderBrush="#273858" BorderThickness="1" Margin="0,0,10,0">
            <Grid Margin="18">
                <Grid.RowDefinitions>
                    <RowDefinition Height="Auto"/>
                    <RowDefinition Height="180"/>
                    <RowDefinition Height="205"/>
                    <RowDefinition Height="205"/>
                    <RowDefinition Height="*"/>
                </Grid.RowDefinitions>

                <StackPanel Grid.Row="0" Margin="0,0,0,14">
                    <TextBlock Text="Astronomicon Task Pyramid" FontSize="30" FontWeight="Bold"/>
                    <TextBlock Text="General Task to Local Tasks to Stage Maps to safe Commit and Push." Foreground="#8FA2CC" Margin="0,4,0,0"/>
                </StackPanel>

                <Border Grid.Row="1" CornerRadius="24" Background="#101A31" BorderBrush="#576DFF" BorderThickness="2" Padding="16" Margin="80,0,80,12">
                    <StackPanel>
                        <TextBlock Text="GENERAL TASK" Foreground="#8DA7FF" FontWeight="Bold" HorizontalAlignment="Center"/>
                        <TextBlock Name="txtGeneralCardTitle" Text="No General Task created" FontSize="22" FontWeight="Bold" TextAlignment="Center" Margin="0,8,0,4"/>
                        <TextBlock Name="txtGeneralCardSubtitle" Text="Create General Task first" Foreground="#C8D5FF" TextAlignment="Center"/>
                        <TextBlock Name="txtGeneralCardMeta" Text="" Foreground="#7FE6FF" TextAlignment="Center" Margin="0,6,0,0"/>
                    </StackPanel>
                </Border>

                <Grid Grid.Row="2" Margin="0,0,0,12">
                    <Grid.ColumnDefinitions>
                        <ColumnDefinition Width="*"/>
                        <ColumnDefinition Width="*"/>
                    </Grid.ColumnDefinitions>
                    <Border Grid.Column="0" CornerRadius="16" Background="#0E172C" BorderBrush="#3A4F87" BorderThickness="1" Padding="10" Margin="0,0,6,0">
                        <DockPanel>
                            <TextBlock DockPanel.Dock="Top" Text="LOCAL TASKS" Foreground="#8DA7FF" FontWeight="Bold" Margin="0,0,0,8"/>
                            <ListBox Name="lstLocalTasks" Background="#070C18" Foreground="#F6F8FF" BorderThickness="0" FontFamily="Consolas"/>
                        </DockPanel>
                    </Border>
                    <Border Grid.Column="1" CornerRadius="16" Background="#0E172C" BorderBrush="#33405E" BorderThickness="1" Padding="10" Margin="6,0,0,0">
                        <DockPanel>
                            <TextBlock DockPanel.Dock="Top" Text="STAGES ({LTASK-ID})" Foreground="#8DA7FF" FontWeight="Bold" Margin="0,0,0,8"/>
                            <ListBox Name="lstStages" Background="#070C18" Foreground="#F6F8FF" BorderThickness="0" FontFamily="Consolas"/>
                        </DockPanel>
                    </Border>
                </Grid>

                <Border Grid.Row="3" CornerRadius="16" Background="#111827" BorderBrush="#5A3DF0" BorderThickness="1" Padding="10" Margin="0,0,0,12">
                    <DockPanel>
                        <TextBlock DockPanel.Dock="Top" Text="PIPELINE STATE" Foreground="#D8D0FF" FontWeight="Bold" Margin="0,0,0,8"/>
                        <TextBox Name="txtPipelineState" AcceptsReturn="True" IsReadOnly="True" VerticalScrollBarVisibility="Auto" Background="#0B111E" Foreground="#DCE8FF" BorderThickness="0" FontFamily="Consolas"/>
                    </DockPanel>
                </Border>

                <Border Grid.Row="4" CornerRadius="14" Background="#0E172C" BorderBrush="#26395E" BorderThickness="1" Padding="12">
                    <Grid>
                        <Grid.ColumnDefinitions>
                            <ColumnDefinition Width="*"/>
                            <ColumnDefinition Width="*"/>
                        </Grid.ColumnDefinitions>
                        <StackPanel Grid.Column="0" Margin="0,0,8,0">
                            <TextBlock Text="GENERAL_TASK_ID" Foreground="#8DA7FF"/>
                            <TextBox Name="txtMainTaskId" IsReadOnly="True"/>
                            <TextBlock Text="TITLE" Foreground="#8DA7FF" Margin="0,8,0,0"/>
                            <TextBox Name="txtMainTaskTitle" IsReadOnly="True"/>
                        </StackPanel>
                        <StackPanel Grid.Column="1" Margin="8,0,0,0">
                            <TextBlock Text="TASK ROOT" Foreground="#8DA7FF"/>
                            <TextBox Name="txtMainTaskRoot" IsReadOnly="True"/>
                        </StackPanel>
                    </Grid>
                </Border>
            </Grid>
        </Border>

        <Border Grid.Column="2" CornerRadius="18" Background="#0D1426" BorderBrush="#273858" BorderThickness="1">
            <Grid Margin="16">
                <Grid.RowDefinitions>
                    <RowDefinition Height="52"/>
                    <RowDefinition Height="42"/>
                    <RowDefinition Height="360"/>
                    <RowDefinition Height="*"/>
                </Grid.RowDefinitions>
                <Border Grid.Row="0" Background="#101A31" BorderBrush="#2D426B" BorderThickness="1" CornerRadius="12" Padding="10" Margin="0,0,0,10">
                    <TextBlock Name="txtStatus" Text="READY :: dashboard initialized" Foreground="#7FE6FF" FontWeight="SemiBold"/>
                </Border>
                <Border Grid.Row="1" Background="#101A31" BorderBrush="#2D426B" BorderThickness="1" CornerRadius="10" Padding="8" Margin="0,0,0,10">
                    <TextBlock Name="txtPreviewFile" Text="Preview file path will appear here" Foreground="#8DA7FF" FontFamily="Consolas" FontSize="11"/>
                </Border>
                <Border Grid.Row="2" CornerRadius="14" Background="#101A31" BorderBrush="#2D426B" BorderThickness="1" Padding="10" Margin="0,0,0,12">
                    <DockPanel>
                        <TextBlock DockPanel.Dock="Top" Text="Preview" Foreground="#8DA7FF" FontWeight="SemiBold" Margin="0,0,0,8"/>
                        <TextBox Name="txtPreview" AcceptsReturn="True" TextWrapping="Wrap" VerticalScrollBarVisibility="Auto" Background="#070C18" Foreground="#F6F8FF" BorderThickness="0" FontFamily="Consolas" IsReadOnly="True"/>
                    </DockPanel>
                </Border>
                <Border Grid.Row="3" CornerRadius="14" Background="#101A31" BorderBrush="#2D426B" BorderThickness="1" Padding="10">
                    <DockPanel>
                        <TextBlock DockPanel.Dock="Top" Text="Log" Foreground="#8DA7FF" FontWeight="SemiBold" Margin="0,0,0,8"/>
                        <TextBox Name="txtLog" AcceptsReturn="True" TextWrapping="Wrap" VerticalScrollBarVisibility="Auto" Background="#070C18" Foreground="#DCE8FF" BorderThickness="0" FontFamily="Consolas" IsReadOnly="True"/>
                    </DockPanel>
                </Border>
            </Grid>
        </Border>
    </Grid>
</Window>
"@

$reader = New-Object System.Xml.XmlNodeReader $xaml
$window = [Windows.Markup.XamlReader]::Load($reader)

$script:txtMainTaskId = $window.FindName("txtMainTaskId")
$script:txtMainTaskTitle = $window.FindName("txtMainTaskTitle")
$script:txtMainTaskRoot = $window.FindName("txtMainTaskRoot")
$script:txtGeneralCardTitle = $window.FindName("txtGeneralCardTitle")
$script:txtGeneralCardSubtitle = $window.FindName("txtGeneralCardSubtitle")
$script:txtGeneralCardMeta = $window.FindName("txtGeneralCardMeta")
$script:txtPipelineState = $window.FindName("txtPipelineState")
$script:txtStatus = $window.FindName("txtStatus")
$script:txtPreviewFile = $window.FindName("txtPreviewFile")
$script:txtPreview = $window.FindName("txtPreview")
$script:txtLog = $window.FindName("txtLog")
$script:lstLocalTasks = $window.FindName("lstLocalTasks")
$script:lstStages = $window.FindName("lstStages")

$btnCreateGeneral = $window.FindName("btnCreateGeneral")
$btnParse = $window.FindName("btnParse")
$btnExportLocalSpeculum = $window.FindName("btnExportLocalSpeculum")
$btnImportLocalSpeculum = $window.FindName("btnImportLocalSpeculum")
$btnDecomposeSelected = $window.FindName("btnDecomposeSelected")
$btnExportStageSpeculum = $window.FindName("btnExportStageSpeculum")
$btnImportStageSpeculum = $window.FindName("btnImportStageSpeculum")
$btnCommitTaskPlan = $window.FindName("btnCommitTaskPlan")
$btnPushTaskPlan = $window.FindName("btnPushTaskPlan")
$btnRefresh = $window.FindName("btnRefresh")
$btnOpenSpeculum = $window.FindName("btnOpenSpeculum")
$btnOpenTaskRoot = $window.FindName("btnOpenTaskRoot")
$btnOpenOutput = $window.FindName("btnOpenOutput")

Refresh-PipelinePanel

$btnCreateGeneral.Add_Click({
    try {
        Show-GeneralTaskEditor
    }
    catch {
        Status -State "FAIL" -Message "Create General Task failed: $($_.Exception.Message)"
    }
})

$btnParse.Add_Click({
    try {
        if (-not $script:CurrentInputPath -or -not (Test-Path -LiteralPath $script:CurrentInputPath)) {
            throw "No General Task input found. Create General Task first."
        }
        Status -State "WORKING" -Message "Running ID sync check before parse."
        $syncBefore = Invoke-TaskIdSyncCheck -ActionName "PRE_PARSE" -RequireRegistry $false
        Log "ID sync pre-parse receipt: $syncBefore"

        Status -State "WORKING" -Message "Parsing General Task to Local Tasks."
        Invoke-BackendScript -ScriptPath $script:ParserPath -Parameters @(
            "-InputPath", $script:CurrentInputPath,
            "-OutputRoot", $script:CurrentOutputRoot
        )

        Status -State "WORKING" -Message "Running ID sync check after parse."
        $syncAfter = Invoke-TaskIdSyncCheck -ActionName "POST_PARSE" -RequireRegistry $true
        Log "ID sync post-parse receipt: $syncAfter"

        Refresh-View
        $routePath = Join-Path $script:CurrentOutputRoot "SERVITOR_ROUTE_TEST.md"
        if (Test-Path -LiteralPath $routePath) {
            Show-PreviewFile -Path $routePath
        }
        Set-PipelineState -Key "local_tasks_created" -Value "PASS"
        Status -State "PASS" -Message "Local Tasks created."
    }
    catch {
        Set-PipelineState -Key "local_tasks_created" -Value "BLOCKED"
        Status -State "BLOCKED" -Message "Parse blocked: $($_.Exception.Message)"
    }
})

$btnExportLocalSpeculum.Add_Click({
    try {
        if (-not $script:CurrentOutputRoot -or -not (Test-Path -LiteralPath $script:CurrentOutputRoot)) {
            throw "No output root found."
        }
        Status -State "WORKING" -Message "Exporting Local Tasks for Speculum."
        Invoke-BackendScript -ScriptPath $script:ExportLocalTasksPath -Parameters @("-OutputRoot", $script:CurrentOutputRoot)
        $exportPath = Join-Path $script:CurrentOutputRoot "SPECULUM\SPECULUM_LOCAL_TASK_REVIEW_REQUEST.json"
        Show-PreviewFile -Path $exportPath
        Set-PipelineState -Key "speculum_local_exported" -Value "EXPORTED"
        Status -State "EXPORTED" -Message "Local Task review payload exported."
    }
    catch {
        Set-PipelineState -Key "speculum_local_exported" -Value "FAIL"
        Status -State "FAIL" -Message "Export Local Tasks failed: $($_.Exception.Message)"
    }
})

$btnImportLocalSpeculum.Add_Click({
    try {
        if (-not $script:CurrentOutputRoot) { throw "No output root found." }
        Status -State "WORKING" -Message "Running ID sync check before Local import."
        $syncPath = Invoke-TaskIdSyncCheck -ActionName "PRE_IMPORT_LOCAL" -RequireRegistry $true
        Log "ID sync import-local receipt: $syncPath"

        $refPath = Join-Path $script:CurrentOutputRoot "SPECULUM\SPECULUM_LOCAL_TASK_REFINEMENTS.json"
        if (-not (Test-Path -LiteralPath $refPath)) {
            $dialog = New-Object Microsoft.Win32.OpenFileDialog
            $dialog.Title = "Select SPECULUM_LOCAL_TASK_REFINEMENTS.json"
            $dialog.Filter = "JSON files (*.json)|*.json|All files (*.*)|*.*"
            $dialog.InitialDirectory = Join-Path $script:CurrentOutputRoot "SPECULUM"
            if ($dialog.ShowDialog() -ne $true) {
                Status -State "READY" -Message "Import canceled."
                return
            }
            $refPath = $dialog.FileName
        }

        Status -State "WORKING" -Message "Importing Local Task refinements."
        Invoke-BackendScript -ScriptPath $script:ImportLocalTaskRefinementsPath -Parameters @(
            "-OutputRoot", $script:CurrentOutputRoot,
            "-RefinementsPath", $refPath
        )
        $receiptPath = Join-Path $script:CurrentOutputRoot "SPECULUM\IMPORTS\LOCAL_TASK_REFINEMENTS\IMPORT_LOCAL_TASK_REFINEMENTS_RECEIPT.json"
        Show-PreviewFile -Path $receiptPath
        Refresh-View
        Set-PipelineState -Key "local_refinements_imported" -Value "IMPORTED"
        Status -State "IMPORTED" -Message "Local refinements imported."
    }
    catch {
        Set-PipelineState -Key "local_refinements_imported" -Value "BLOCKED"
        Status -State "BLOCKED" -Message "Import Local refinements blocked: $($_.Exception.Message)"
    }
})

$btnDecomposeSelected.Add_Click({
    try {
        if (-not $script:CurrentOutputRoot) { throw "No output root found." }
        if ($null -eq $script:lstLocalTasks.SelectedItem) { throw "Select one Local Task first." }
        Status -State "WORKING" -Message "Running ID sync check before decomposition."
        $syncPath = Invoke-TaskIdSyncCheck -ActionName "PRE_DECOMPOSE" -RequireRegistry $true
        Log "ID sync decompose receipt: $syncPath"

        $localTaskId = [string]$script:lstLocalTasks.SelectedItem
        Status -State "WORKING" -Message "Decomposing $localTaskId to stages."
        Invoke-BackendScript -ScriptPath $script:DecomposeLocalTaskPath -Parameters @(
            "-OutputRoot", $script:CurrentOutputRoot,
            "-LocalTaskId", $localTaskId
        )
        Refresh-StagesForSelectedLocalTask
        $stageMapPath = Join-Path $script:CurrentOutputRoot "STAGE_MAPS\$localTaskId\STAGE_MAP.md"
        Show-PreviewFile -Path $stageMapPath
        Set-PipelineState -Key "stages_created" -Value "DECOMPOSED"
        Set-PipelineState -Key "commit_ready" -Value "READY"
        Status -State "DECOMPOSED" -Message "$localTaskId decomposed to stages."
    }
    catch {
        Set-PipelineState -Key "stages_created" -Value "BLOCKED"
        Status -State "BLOCKED" -Message "Decompose failed: $($_.Exception.Message)"
    }
})

$btnExportStageSpeculum.Add_Click({
    try {
        if (-not $script:CurrentOutputRoot) { throw "No output root found." }
        if ($null -eq $script:lstLocalTasks.SelectedItem) { throw "Select one Local Task first." }
        Status -State "WORKING" -Message "Running ID sync check before stage export."
        $syncPath = Invoke-TaskIdSyncCheck -ActionName "PRE_EXPORT_STAGE" -RequireRegistry $true
        Log "ID sync export-stage receipt: $syncPath"

        $localTaskId = [string]$script:lstLocalTasks.SelectedItem
        Status -State "WORKING" -Message "Exporting stage map for Speculum: $localTaskId"
        Invoke-BackendScript -ScriptPath $script:ExportStageMapPath -Parameters @(
            "-OutputRoot", $script:CurrentOutputRoot,
            "-LocalTaskId", $localTaskId
        )
        $exportPath = Join-Path $script:CurrentOutputRoot "SPECULUM\STAGE_REVIEW\SPECULUM_STAGE_REVIEW_REQUEST_$localTaskId.json"
        Show-PreviewFile -Path $exportPath
        Set-PipelineState -Key "speculum_stage_exported" -Value "EXPORTED"
        Status -State "EXPORTED" -Message "Stage review payload exported for $localTaskId."
    }
    catch {
        Set-PipelineState -Key "speculum_stage_exported" -Value "FAIL"
        Status -State "FAIL" -Message "Export stage review failed: $($_.Exception.Message)"
    }
})

$btnImportStageSpeculum.Add_Click({
    try {
        if (-not $script:CurrentOutputRoot) { throw "No output root found." }
        if ($null -eq $script:lstLocalTasks.SelectedItem) { throw "Select one Local Task first." }
        Status -State "WORKING" -Message "Running ID sync check before stage import."
        $syncPath = Invoke-TaskIdSyncCheck -ActionName "PRE_IMPORT_STAGE" -RequireRegistry $true
        Log "ID sync import-stage receipt: $syncPath"

        $localTaskId = [string]$script:lstLocalTasks.SelectedItem
        $refPath = Join-Path $script:CurrentOutputRoot "SPECULUM\STAGE_REVIEW\SPECULUM_STAGE_REFINEMENTS_$localTaskId.json"
        if (-not (Test-Path -LiteralPath $refPath)) {
            $dialog = New-Object Microsoft.Win32.OpenFileDialog
            $dialog.Title = "Select SPECULUM_STAGE_REFINEMENTS_{LTASK-ID}.json"
            $dialog.Filter = "JSON files (*.json)|*.json|All files (*.*)|*.*"
            $dialog.InitialDirectory = Join-Path $script:CurrentOutputRoot "SPECULUM\STAGE_REVIEW"
            if ($dialog.ShowDialog() -ne $true) {
                Status -State "READY" -Message "Stage import canceled."
                return
            }
            $refPath = $dialog.FileName
        }

        Status -State "WORKING" -Message "Importing stage refinements for $localTaskId."
        Invoke-BackendScript -ScriptPath $script:ImportStageRefinementsPath -Parameters @(
            "-OutputRoot", $script:CurrentOutputRoot,
            "-LocalTaskId", $localTaskId,
            "-RefinementsPath", $refPath
        )
        $receiptPath = Join-Path $script:CurrentOutputRoot "SPECULUM\IMPORTS\STAGE_REFINEMENTS\$localTaskId\IMPORT_STAGE_REFINEMENTS_RECEIPT.json"
        Show-PreviewFile -Path $receiptPath
        Refresh-StagesForSelectedLocalTask
        Set-PipelineState -Key "stage_refinements_imported" -Value "IMPORTED"
        Set-PipelineState -Key "commit_ready" -Value "READY"
        Status -State "IMPORTED" -Message "Stage refinements imported for $localTaskId."
    }
    catch {
        Set-PipelineState -Key "stage_refinements_imported" -Value "BLOCKED"
        Status -State "BLOCKED" -Message "Import stage refinements blocked: $($_.Exception.Message)"
    }
})

$btnCommitTaskPlan.Add_Click({
    try {
        if (-not $script:CurrentTaskRoot -or -not (Test-Path -LiteralPath $script:CurrentTaskRoot)) {
            throw "No current task root found."
        }
        $receiptPath = Join-Path $script:CurrentOutputRoot "RECEIPTS\GIT\COMMIT_RECEIPT.json"
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $receiptPath) | Out-Null
        Status -State "WORKING" -Message "Creating safe scoped commit for task plan."
        Invoke-BackendScript -ScriptPath $script:CommitPushPath -Parameters @(
            "-Mode", "COMMIT",
            "-RepoRoot", $script:RepoRoot,
            "-IncludePaths", $script:CurrentTaskRoot,
            "-CommitMessage", "task plan update $script:CurrentTaskId",
            "-ReceiptPath", $receiptPath
        )
        Show-PreviewFile -Path $receiptPath
        Set-PipelineState -Key "commit_ready" -Value "PASS"
        Status -State "PASS" -Message "Task plan commit created safely."
    }
    catch {
        Set-PipelineState -Key "commit_ready" -Value "BLOCKED"
        Status -State "BLOCKED" -Message "Commit blocked: $($_.Exception.Message)"
    }
})

$btnPushTaskPlan.Add_Click({
    try {
        $receiptPath = Join-Path $script:CurrentOutputRoot "RECEIPTS\GIT\PUSH_RECEIPT.json"
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $receiptPath) | Out-Null
        Status -State "WORKING" -Message "Pushing and verifying HEAD parity."
        Invoke-BackendScript -ScriptPath $script:CommitPushPath -Parameters @(
            "-Mode", "PUSH",
            "-RepoRoot", $script:RepoRoot,
            "-ReceiptPath", $receiptPath
        )
        Show-PreviewFile -Path $receiptPath
        Set-PipelineState -Key "push_verified" -Value "PASS"
        Status -State "PASS" -Message "Push verified: local/origin/remote HEAD match."
    }
    catch {
        Set-PipelineState -Key "push_verified" -Value "FAIL"
        Status -State "FAIL" -Message "Push verification failed: $($_.Exception.Message)"
    }
})

$btnRefresh.Add_Click({
    try {
        Refresh-View
        Status -State "READY" -Message "View refreshed."
    }
    catch {
        Status -State "FAIL" -Message "Refresh failed: $($_.Exception.Message)"
    }
})

$btnOpenSpeculum.Add_Click({
    try {
        if (-not $script:CurrentOutputRoot) { throw "No output root." }
        $speculumRoot = Join-Path $script:CurrentOutputRoot "SPECULUM"
        New-Item -ItemType Directory -Force -Path $speculumRoot | Out-Null
        Start-Process explorer.exe $speculumRoot
        Status -State "READY" -Message "Speculum folder opened."
    }
    catch {
        Status -State "FAIL" -Message "Open Speculum failed: $($_.Exception.Message)"
    }
})

$btnOpenTaskRoot.Add_Click({
    try {
        if (-not $script:CurrentTaskRoot -or -not (Test-Path -LiteralPath $script:CurrentTaskRoot)) { throw "No task root." }
        Start-Process explorer.exe $script:CurrentTaskRoot
        Status -State "READY" -Message "Task root opened."
    }
    catch {
        Status -State "FAIL" -Message "Open task root failed: $($_.Exception.Message)"
    }
})

$btnOpenOutput.Add_Click({
    try {
        if (-not $script:CurrentOutputRoot -or -not (Test-Path -LiteralPath $script:CurrentOutputRoot)) { throw "No output root." }
        Start-Process explorer.exe $script:CurrentOutputRoot
        Status -State "READY" -Message "Output root opened."
    }
    catch {
        Status -State "FAIL" -Message "Open output failed: $($_.Exception.Message)"
    }
})

$script:lstLocalTasks.Add_SelectionChanged({
    try {
        if ($null -eq $script:lstLocalTasks.SelectedItem) { return }
        $localTaskId = [string]$script:lstLocalTasks.SelectedItem
        Refresh-StagesForSelectedLocalTask

        $localMdPath = Join-Path $script:CurrentOutputRoot "LOCAL_TASKS\$localTaskId\LOCAL_TASK.md"
        $refMdPath = Join-Path $script:CurrentOutputRoot "LOCAL_TASKS\$localTaskId\SPECULUM_REFINEMENTS.md"
        if (Test-Path -LiteralPath $refMdPath) {
            $combinedPath = Join-Path $script:CurrentOutputRoot "RECEIPTS\PREVIEW\LOCAL_TASK_${localTaskId}_WITH_REFINEMENTS.md"
            New-Item -ItemType Directory -Force -Path (Split-Path -Parent $combinedPath) | Out-Null
            $combined = (Get-Content -LiteralPath $localMdPath -Encoding UTF8 -Raw) + "`r`n`r`n--- SPECULUM REFINEMENTS ---`r`n`r`n" + (Get-Content -LiteralPath $refMdPath -Encoding UTF8 -Raw)
            Write-Utf8Bom -Path $combinedPath -Content $combined
            Show-PreviewFile -Path $combinedPath
        }
        else {
            Show-PreviewFile -Path $localMdPath
        }
        Status -State "READY" -Message "Selected $localTaskId."
    }
    catch {
        Status -State "FAIL" -Message "Local task selection failed: $($_.Exception.Message)"
    }
})

$script:lstStages.Add_SelectionChanged({
    try {
        if ($null -eq $script:lstStages.SelectedItem) { return }
        if ($null -eq $script:lstLocalTasks.SelectedItem) { return }
        $localTaskId = [string]$script:lstLocalTasks.SelectedItem
        $stageId = [string]$script:lstStages.SelectedItem
        $stageMdPath = Join-Path $script:CurrentOutputRoot "STAGE_MAPS\$localTaskId\STAGES\$stageId\STAGE.md"
        $stageRefPath = Join-Path $script:CurrentOutputRoot "STAGE_MAPS\$localTaskId\STAGES\$stageId\SPECULUM_STAGE_REFINEMENTS.md"
        if (Test-Path -LiteralPath $stageRefPath) {
            $combinedPath = Join-Path $script:CurrentOutputRoot "RECEIPTS\PREVIEW\STAGE_${stageId}_WITH_REFINEMENTS.md"
            New-Item -ItemType Directory -Force -Path (Split-Path -Parent $combinedPath) | Out-Null
            $combined = (Get-Content -LiteralPath $stageMdPath -Encoding UTF8 -Raw) + "`r`n`r`n--- SPECULUM STAGE REFINEMENTS ---`r`n`r`n" + (Get-Content -LiteralPath $stageRefPath -Encoding UTF8 -Raw)
            Write-Utf8Bom -Path $combinedPath -Content $combined
            Show-PreviewFile -Path $combinedPath
        }
        else {
            Show-PreviewFile -Path $stageMdPath
        }
        Status -State "READY" -Message "Selected $stageId."
    }
    catch {
        Status -State "FAIL" -Message "Stage selection failed: $($_.Exception.Message)"
    }
})

$window.Add_ContentRendered({
    Status -State "READY" -Message "Dashboard v0.6 ready."
})

[void]$window.ShowDialog()

