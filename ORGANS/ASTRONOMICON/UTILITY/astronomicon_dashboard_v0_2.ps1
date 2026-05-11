Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName PresentationCore
Add-Type -AssemblyName WindowsBase

$ErrorActionPreference = "Stop"

$script:RepoRoot = "E:\IMPERIUM"
$script:GeneralTasksRoot = "E:\IMPERIUM\ASTRONOMICON\GENERAL_TASKS"
$script:DashboardStateRoot = "E:\IMPERIUM\CURRENT_STATE\ASTRONOMICON_DASHBOARD"
$script:ParserPath = "E:\IMPERIUM\TOOLS\astronomicon_parse_general_task_v0_1.ps1"
$script:CurrentTaskRoot = $null
$script:CurrentInputPath = $null
$script:CurrentOutputRoot = $null

New-Item -ItemType Directory -Force $script:GeneralTasksRoot, $script:DashboardStateRoot | Out-Null

function Write-Utf8Bom {
    param([string]$Path, [string]$Content)

    $Dir = Split-Path -Parent $Path
    if ($Dir -and !(Test-Path $Dir)) {
        New-Item -ItemType Directory -Force $Dir | Out-Null
    }

    $Utf8Bom = New-Object System.Text.UTF8Encoding($true)
    [System.IO.File]::WriteAllText($Path, $Content.Replace("`n","`r`n"), $Utf8Bom)
}

function Get-DefaultTaskId {
    $DateStamp = Get-Date -Format "yyyyMMdd"
    return "GTASK-$DateStamp-ASTRONOMICON-GENERAL-TASK-V0_2"
}

function Ensure-TaskLayout {
    param([string]$GeneralTaskId)

    $TaskRoot = Join-Path $script:GeneralTasksRoot $GeneralTaskId
    $InputRoot = Join-Path $TaskRoot "INPUT"
    $OutputRoot = Join-Path $TaskRoot "OUTPUT"
    $StateRoot = Join-Path $TaskRoot "STATE"

    New-Item -ItemType Directory -Force $TaskRoot, $InputRoot, $OutputRoot, $StateRoot | Out-Null

    $script:CurrentTaskRoot = $TaskRoot
    $script:CurrentInputPath = Join-Path $InputRoot "GENERAL_TASK_INPUT.txt"
    $script:CurrentOutputRoot = $OutputRoot

    return [ordered]@{
        task_root = $TaskRoot
        input_path = $script:CurrentInputPath
        output_root = $OutputRoot
        state_root = $StateRoot
    }
}

function Get-Template {
    param(
        [string]$GeneralTaskId,
        [string]$TaskTitle,
        [string]$TaskCode,
        [string]$ExecutionIntent,
        [string]$Priority
    )

@"
ASTRONOMICON_GENERAL_TASK_V0_1
ENCODING: UTF-8-BOM
LINE_ENDINGS: CRLF

GENERAL_TASK_ID:
$GeneralTaskId

GENERAL_TASK_TITLE:
$TaskTitle

GENERAL_TASK_CODE:
$TaskCode

AUTHOR:
Owner

EXECUTION_INTENT:
$ExecutionIntent

PRIORITY:
$Priority

BEGIN_GOAL
Опиши главную цель задачи.
END_GOAL

BEGIN_CONTEXT
Опиши текущий контекст, что уже сделано, почему эта задача нужна, на что она опирается.
END_CONTEXT

BEGIN_CURRENT_PROBLEM
Опиши, какая проблема сейчас мешает или что именно ещё не построено.
END_CURRENT_PROBLEM

BEGIN_EXPECTED_FINAL_STATE
- Опиши конечное ожидаемое состояние.
- Что должно существовать в системе после выполнения.
- Что должно быть проверяемо.
END_EXPECTED_FINAL_STATE

BEGIN_HARD_CONSTRAINTS
- Не публиковать секреты.
- Не делать fake green.
- Не пропускать обязательные проверки.
END_HARD_CONSTRAINTS

BEGIN_DO_NOT_DO
- Не делать лишнюю магию без артефактов.
- Не размывать scope задачи.
END_DO_NOT_DO

BEGIN_PLAN_ITEMS

ITEM_ID: PI-001
TITLE: First local task title
TEXT:
Опиши первый локальный таск.
EXPECTED_OUTPUT:
Опиши ожидаемый результат первого локального таска.
REQUIRED_ORGANS:
Astronomicon, Administratum
EXECUTION_MODE:
manual
DEPENDS_ON:
none
END_ITEM

ITEM_ID: PI-002
TITLE: Second local task title
TEXT:
Опиши второй локальный таск.
EXPECTED_OUTPUT:
Опиши ожидаемый результат второго локального таска.
REQUIRED_ORGANS:
Astronomicon, Mechanicus
EXECUTION_MODE:
scripted
DEPENDS_ON:
PI-001
END_ITEM

END_PLAN_ITEMS

BEGIN_KNOWN_RISKS
- Укажи известные риски.
END_KNOWN_RISKS

BEGIN_REQUIRED_ORGANS
- Astronomicon
- Administratum
END_REQUIRED_ORGANS

BEGIN_REQUIRED_INPUTS
- Укажи необходимые входы.
END_REQUIRED_INPUTS

BEGIN_EXPECTED_ARTIFACTS
- Укажи ожидаемые артефакты.
END_EXPECTED_ARTIFACTS

BEGIN_OWNER_NOTES
Свободные заметки Owner.
END_OWNER_NOTES
"@
}

[xml]$Xaml = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="IMPERIUM :: ASTRONOMICON DASHBOARD v0.2"
        Height="980"
        Width="1600"
        WindowStartupLocation="CenterScreen"
        Background="#070B15"
        Foreground="#EAF0FF"
        ResizeMode="CanResize">

    <Window.Resources>
        <Style TargetType="Button">
            <Setter Property="Height" Value="40"/>
            <Setter Property="Margin" Value="0,0,0,9"/>
            <Setter Property="Background" Value="#142545"/>
            <Setter Property="Foreground" Value="#F1F5FF"/>
            <Setter Property="BorderBrush" Value="#334C7A"/>
            <Setter Property="BorderThickness" Value="1"/>
            <Setter Property="FontSize" Value="13"/>
            <Setter Property="Cursor" Value="Hand"/>
        </Style>

        <Style TargetType="TextBox">
            <Setter Property="Background" Value="#091022"/>
            <Setter Property="Foreground" Value="#F4F7FF"/>
            <Setter Property="BorderBrush" Value="#2D426B"/>
            <Setter Property="BorderThickness" Value="1"/>
            <Setter Property="Padding" Value="7,4,7,4"/>
            <Setter Property="FontSize" Value="13"/>
        </Style>

        <Style TargetType="TextBlock">
            <Setter Property="Foreground" Value="#EAF0FF"/>
        </Style>
    </Window.Resources>

    <Grid Margin="12">
        <Grid.ColumnDefinitions>
            <ColumnDefinition Width="215"/>
            <ColumnDefinition Width="*"/>
            <ColumnDefinition Width="370"/>
        </Grid.ColumnDefinitions>

        <!-- LEFT -->
        <Border Grid.Column="0" CornerRadius="18" Background="#0D1426" BorderBrush="#273858" BorderThickness="1" Margin="0,0,10,0">
            <DockPanel Margin="16">
                <StackPanel DockPanel.Dock="Top">
                    <TextBlock Text="ASTRONOMICON" FontSize="23" FontWeight="Bold"/>
                    <TextBlock Text="Task forge v0.2" Foreground="#8DA7FF" Margin="0,4,0,16"/>

                    <Button Name="btnLoadTemplate" Content="Load Template"/>
                    <Button Name="btnSaveForm" Content="Save Form"/>
                    <Button Name="btnParse" Content="Parse → Local Tasks" Background="#13A9B8" BorderBrush="#13A9B8"/>
                    <Button Name="btnRefresh" Content="Refresh Local Tasks"/>
                    <Button Name="btnOpenTaskRoot" Content="Open Task Root"/>
                    <Button Name="btnOpenOutput" Content="Open Output"/>

                    <Separator Margin="0,12,0,14"/>

                    <TextBlock Text="Current target" Foreground="#8DA7FF" FontWeight="SemiBold"/>
                    <Border Background="#101A31" CornerRadius="10" Padding="10" Margin="0,8,0,0">
                        <TextBlock Name="txtCurrentTarget" Text="No task loaded" TextWrapping="Wrap"/>
                    </Border>
                </StackPanel>
            </DockPanel>
        </Border>

        <!-- CENTER -->
        <Border Grid.Column="1" CornerRadius="18" Background="#0A1020" BorderBrush="#273858" BorderThickness="1" Margin="0,0,10,0">
            <Grid Margin="16">
                <Grid.RowDefinitions>
                    <RowDefinition Height="Auto"/>
                    <RowDefinition Height="Auto"/>
                    <RowDefinition Height="*"/>
                </Grid.RowDefinitions>

                <Grid Grid.Row="0" Margin="0,0,0,12">
                    <Grid.ColumnDefinitions>
                        <ColumnDefinition Width="*"/>
                        <ColumnDefinition Width="260"/>
                    </Grid.ColumnDefinitions>

                    <StackPanel Grid.Column="0">
                        <TextBlock Text="Astronomicon General Task Forge" FontSize="28" FontWeight="Bold"/>
                        <TextBlock Text="Strict form → parser → Local Tasks → Servitor dispatch" Foreground="#8FA2CC" Margin="0,5,0,0"/>
                    </StackPanel>

                    <Border Grid.Column="1" Background="#101A31" BorderBrush="#2D426B" BorderThickness="1" CornerRadius="12" Padding="12">
                        <StackPanel>
                            <TextBlock Text="Status" Foreground="#8DA7FF" FontWeight="SemiBold"/>
                            <TextBlock Name="txtStatus" Text="Ready" Foreground="#7FE6FF" Margin="0,5,0,0"/>
                        </StackPanel>
                    </Border>
                </Grid>

                <Border Grid.Row="1" CornerRadius="14" Background="#0E172C" BorderBrush="#26395E" BorderThickness="1" Padding="12" Margin="0,0,0,12">
                    <Grid>
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

                        <StackPanel Grid.Row="0" Grid.Column="0" Margin="0,0,10,8">
                            <TextBlock Text="GENERAL_TASK_ID" Foreground="#8DA7FF"/>
                            <TextBox Name="txtTaskId"/>
                        </StackPanel>

                        <StackPanel Grid.Row="0" Grid.Column="1" Margin="10,0,10,8">
                            <TextBlock Text="TITLE" Foreground="#8DA7FF"/>
                            <TextBox Name="txtTitle"/>
                        </StackPanel>

                        <StackPanel Grid.Row="0" Grid.Column="2" Margin="10,0,10,8">
                            <TextBlock Text="MODE" Foreground="#8DA7FF"/>
                            <TextBox Name="txtExecutionIntent"/>
                        </StackPanel>

                        <StackPanel Grid.Row="0" Grid.Column="3" Margin="10,0,0,8">
                            <TextBlock Text="PRIORITY" Foreground="#8DA7FF"/>
                            <TextBox Name="txtPriority"/>
                        </StackPanel>

                        <StackPanel Grid.Row="1" Grid.Column="0" Margin="0,0,10,0">
                            <TextBlock Text="GENERAL_TASK_CODE" Foreground="#8DA7FF"/>
                            <TextBox Name="txtTaskCode"/>
                        </StackPanel>

                        <StackPanel Grid.Row="1" Grid.Column="1" Grid.ColumnSpan="3" Margin="10,0,0,0">
                            <TextBlock Text="TASK ROOT" Foreground="#8DA7FF"/>
                            <TextBox Name="txtTaskRoot" IsReadOnly="True"/>
                        </StackPanel>
                    </Grid>
                </Border>

                <Border Grid.Row="2" CornerRadius="14" Background="#0E172C" BorderBrush="#26395E" BorderThickness="1" Padding="12">
                    <DockPanel>
                        <TextBlock DockPanel.Dock="Top" Text="General Task Form" Foreground="#8DA7FF" FontWeight="SemiBold" Margin="0,0,0,8"/>
                        <TextBox Name="txtForm"
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
            </Grid>
        </Border>

        <!-- RIGHT -->
        <Border Grid.Column="2" CornerRadius="18" Background="#0D1426" BorderBrush="#273858" BorderThickness="1">
            <Grid Margin="16">
                <Grid.RowDefinitions>
                    <RowDefinition Height="230"/>
                    <RowDefinition Height="280"/>
                    <RowDefinition Height="*"/>
                </Grid.RowDefinitions>

                <Border Grid.Row="0" CornerRadius="14" Background="#101A31" BorderBrush="#2D426B" BorderThickness="1" Padding="10" Margin="0,0,0,12">
                    <DockPanel>
                        <TextBlock DockPanel.Dock="Top" Text="Local Tasks" Foreground="#8DA7FF" FontWeight="SemiBold" Margin="0,0,0,8"/>
                        <ListBox Name="lstTasks" Background="#070C18" Foreground="#F6F8FF" BorderThickness="0" FontFamily="Consolas"/>
                    </DockPanel>
                </Border>

                <Border Grid.Row="1" CornerRadius="14" Background="#101A31" BorderBrush="#2D426B" BorderThickness="1" Padding="10" Margin="0,0,0,12">
                    <DockPanel>
                        <TextBlock DockPanel.Dock="Top" Text="Preview" Foreground="#8DA7FF" FontWeight="SemiBold" Margin="0,0,0,8"/>
                        <TextBox Name="txtPreview"
                                 AcceptsReturn="True"
                                 TextWrapping="Wrap"
                                 VerticalScrollBarVisibility="Auto"
                                 Background="#070C18"
                                 Foreground="#F6F8FF"
                                 BorderThickness="0"
                                 FontFamily="Consolas"
                                 IsReadOnly="True"/>
                    </DockPanel>
                </Border>

                <Border Grid.Row="2" CornerRadius="14" Background="#101A31" BorderBrush="#2D426B" BorderThickness="1" Padding="10">
                    <DockPanel>
                        <TextBlock DockPanel.Dock="Top" Text="Log" Foreground="#8DA7FF" FontWeight="SemiBold" Margin="0,0,0,8"/>
                        <TextBox Name="txtLog"
                                 AcceptsReturn="True"
                                 TextWrapping="Wrap"
                                 VerticalScrollBarVisibility="Auto"
                                 Background="#070C18"
                                 Foreground="#DCE8FF"
                                 BorderThickness="0"
                                 FontFamily="Consolas"
                                 IsReadOnly="True"/>
                    </DockPanel>
                </Border>
            </Grid>
        </Border>
    </Grid>
</Window>
"@

$Reader = New-Object System.Xml.XmlNodeReader $Xaml
$Window = [Windows.Markup.XamlReader]::Load($Reader)

$txtTaskId = $Window.FindName("txtTaskId")
$txtTitle = $Window.FindName("txtTitle")
$txtExecutionIntent = $Window.FindName("txtExecutionIntent")
$txtPriority = $Window.FindName("txtPriority")
$txtTaskCode = $Window.FindName("txtTaskCode")
$txtTaskRoot = $Window.FindName("txtTaskRoot")
$txtForm = $Window.FindName("txtForm")
$txtCurrentTarget = $Window.FindName("txtCurrentTarget")
$txtStatus = $Window.FindName("txtStatus")
$lstTasks = $Window.FindName("lstTasks")
$txtPreview = $Window.FindName("txtPreview")
$txtLog = $Window.FindName("txtLog")

$btnLoadTemplate = $Window.FindName("btnLoadTemplate")
$btnSaveForm = $Window.FindName("btnSaveForm")
$btnParse = $Window.FindName("btnParse")
$btnRefresh = $Window.FindName("btnRefresh")
$btnOpenTaskRoot = $Window.FindName("btnOpenTaskRoot")
$btnOpenOutput = $Window.FindName("btnOpenOutput")

function Log {
    param([string]$Message)
    $Stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $txtLog.AppendText("[$Stamp] $Message`r`n")
    $txtLog.ScrollToEnd()
}

function Status {
    param([string]$Message)
    $txtStatus.Text = $Message
    Log $Message
}

function RefreshTasks {
    $lstTasks.Items.Clear()

    if (!$script:CurrentOutputRoot -or !(Test-Path (Join-Path $script:CurrentOutputRoot "LOCAL_TASKS"))) {
        return
    }

    Get-ChildItem (Join-Path $script:CurrentOutputRoot "LOCAL_TASKS") -Directory | Sort-Object Name | ForEach-Object {
        [void]$lstTasks.Items.Add($_.Name)
    }

    Status "Local Tasks refreshed."
}

function SaveForm {
    $TaskId = $txtTaskId.Text.Trim()
    if ([string]::IsNullOrWhiteSpace($TaskId)) {
        throw "GENERAL_TASK_ID is empty."
    }

    $Layout = Ensure-TaskLayout $TaskId

    Write-Utf8Bom -Path $Layout.input_path -Content $txtForm.Text

    $txtTaskRoot.Text = $Layout.task_root
    $txtCurrentTarget.Text = $TaskId

    Status "Saved form: $($Layout.input_path)"
    return $Layout
}

$btnLoadTemplate.Add_Click({
    try {
        $txtForm.Text = Get-Template `
            -GeneralTaskId $txtTaskId.Text.Trim() `
            -TaskTitle $txtTitle.Text.Trim() `
            -TaskCode $txtTaskCode.Text.Trim() `
            -ExecutionIntent $txtExecutionIntent.Text.Trim() `
            -Priority $txtPriority.Text.Trim()

        Status "Template loaded."
    }
    catch {
        Status "ERROR Load Template: $($_.Exception.Message)"
    }
})

$btnSaveForm.Add_Click({
    try {
        $Layout = SaveForm
        $txtPreview.Text = Get-Content -Encoding UTF8 $Layout.input_path -Raw
    }
    catch {
        Status "ERROR Save Form: $($_.Exception.Message)"
    }
})

$btnParse.Add_Click({
    try {
        $Layout = SaveForm

        if (!(Test-Path $script:ParserPath)) {
            throw "Parser not found: $script:ParserPath"
        }

        Status "Parser started."

        $Result = & powershell.exe -ExecutionPolicy Bypass -File $script:ParserPath `
            -InputPath $Layout.input_path `
            -OutputRoot $Layout.output_root 2>&1 | Out-String

        if ($Result.Trim()) {
            Log $Result.Trim()
        }

        $script:CurrentOutputRoot = $Layout.output_root

        $Route = Join-Path $Layout.output_root "SERVITOR_ROUTE_TEST.md"
        if (Test-Path $Route) {
            $txtPreview.Text = Get-Content -Encoding UTF8 $Route -Raw
        }

        RefreshTasks
        Status "Parse complete."
    }
    catch {
        Status "ERROR Parse: $($_.Exception.Message)"
    }
})

$btnRefresh.Add_Click({
    try {
        RefreshTasks
    }
    catch {
        Status "ERROR Refresh: $($_.Exception.Message)"
    }
})

$btnOpenTaskRoot.Add_Click({
    try {
        if (!$script:CurrentTaskRoot -or !(Test-Path $script:CurrentTaskRoot)) {
            $null = SaveForm
        }
        Start-Process explorer.exe $script:CurrentTaskRoot
        Status "Opened task root."
    }
    catch {
        Status "ERROR Open Task Root: $($_.Exception.Message)"
    }
})

$btnOpenOutput.Add_Click({
    try {
        if (!$script:CurrentOutputRoot -or !(Test-Path $script:CurrentOutputRoot)) {
            throw "Output root does not exist yet. Run Parse first."
        }
        Start-Process explorer.exe $script:CurrentOutputRoot
        Status "Opened output root."
    }
    catch {
        Status "ERROR Open Output: $($_.Exception.Message)"
    }
})

$lstTasks.Add_SelectionChanged({
    try {
        if ($null -eq $lstTasks.SelectedItem) { return }
        if (!$script:CurrentOutputRoot) { return }

        $Id = [string]$lstTasks.SelectedItem
        $Md = Join-Path $script:CurrentOutputRoot "LOCAL_TASKS\$Id\LOCAL_TASK.md"
        $Json = Join-Path $script:CurrentOutputRoot "LOCAL_TASKS\$Id\LOCAL_TASK.json"

        if (Test-Path $Md) {
            $txtPreview.Text = Get-Content -Encoding UTF8 $Md -Raw
        }
        elseif (Test-Path $Json) {
            $txtPreview.Text = Get-Content -Encoding UTF8 $Json -Raw
        }

        Status "Selected $Id."
    }
    catch {
        Status "ERROR Preview: $($_.Exception.Message)"
    }
})

$Window.Add_ContentRendered({
    try {
        $txtTaskId.Text = Get-DefaultTaskId
        $txtTitle.Text = "Astronomicon New General Task"
        $txtTaskCode.Text = "ASTRONOMICON_GENERAL_TASK"
        $txtExecutionIntent.Text = "manual"
        $txtPriority.Text = "high"
        $txtCurrentTarget.Text = $txtTaskId.Text
        $txtTaskRoot.Text = ""

        $txtForm.Text = Get-Template `
            -GeneralTaskId $txtTaskId.Text.Trim() `
            -TaskTitle $txtTitle.Text.Trim() `
            -TaskCode $txtTaskCode.Text.Trim() `
            -ExecutionIntent $txtExecutionIntent.Text.Trim() `
            -Priority $txtPriority.Text.Trim()

        Status "Dashboard v0.2 ready. Buttons are wired."
    }
    catch {
        Status "ERROR Init: $($_.Exception.Message)"
    }
})

[void]$Window.ShowDialog()