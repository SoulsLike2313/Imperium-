Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName PresentationCore
Add-Type -AssemblyName WindowsBase

$ErrorActionPreference = "Stop"

$script:RepoRoot = "E:\IMPERIUM"
$script:AstronomiconDataRoot = "E:\IMPERIUM\ASTRONOMICON"
$script:GeneralTasksRoot = "E:\IMPERIUM\ASTRONOMICON\GENERAL_TASKS"
$script:DashboardStateRoot = "E:\IMPERIUM\CURRENT_STATE\ASTRONOMICON_DASHBOARD"
$script:DefaultParserPath = "E:\IMPERIUM\TOOLS\astronomicon_parse_general_task_v0_1.ps1"
$script:CurrentOutputRoot = $null

New-Item -ItemType Directory -Force $script:GeneralTasksRoot, $script:DashboardStateRoot | Out-Null

function Write-Utf8Bom {
    param(
        [Parameter(Mandatory=$true)][string]$Path,
        [Parameter(Mandatory=$true)][string]$Content
    )

    $Dir = Split-Path -Parent $Path
    if ($Dir -and !(Test-Path $Dir)) {
        New-Item -ItemType Directory -Force $Dir | Out-Null
    }

    $Utf8Bom = New-Object System.Text.UTF8Encoding($true)
    [System.IO.File]::WriteAllText($Path, $Content.Replace("`n","`r`n"), $Utf8Bom)
}

function Get-DefaultTaskId {
    $DateStamp = Get-Date -Format "yyyyMMdd"
    return "GTASK-$DateStamp-ASTRONOMICON-GENERAL-TASK-V0_1"
}

function Ensure-TaskLayout {
    param([Parameter(Mandatory=$true)][string]$GeneralTaskId)

    $TaskRoot = Join-Path $script:GeneralTasksRoot $GeneralTaskId
    $InputRoot = Join-Path $TaskRoot "INPUT"
    $OutputRoot = Join-Path $TaskRoot "OUTPUT"
    $StateRoot = Join-Path $TaskRoot "STATE"

    New-Item -ItemType Directory -Force $TaskRoot, $InputRoot, $OutputRoot, $StateRoot | Out-Null

    return [ordered]@{
        task_root    = $TaskRoot
        input_root   = $InputRoot
        output_root  = $OutputRoot
        state_root   = $StateRoot
        input_path   = (Join-Path $InputRoot "GENERAL_TASK_INPUT.txt")
        state_path   = (Join-Path $StateRoot "DASHBOARD_STATE.json")
    }
}

function Get-GeneralTaskTemplate {
    param(
        [string]$GeneralTaskId,
        [string]$TaskTitle,
        [string]$TaskCode,
        [string]$Author,
        [string]$ExecutionIntent,
        [string]$Priority
    )

    return @"
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
$Author

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
        Title="IMPERIUM :: ASTRONOMICON DASHBOARD v0.1"
        Height="980"
        Width="1600"
        WindowStartupLocation="CenterScreen"
        Background="#090D18"
        Foreground="#E8ECFF"
        ResizeMode="CanResize">
    <Grid Margin="12">
        <Grid.ColumnDefinitions>
            <ColumnDefinition Width="220"/>
            <ColumnDefinition Width="*"/>
            <ColumnDefinition Width="380"/>
        </Grid.ColumnDefinitions>

        <!-- Left rail -->
        <Border Grid.Column="0" CornerRadius="18" Background="#0E1324" BorderBrush="#24304F" BorderThickness="1" Margin="0,0,10,0">
            <DockPanel Margin="16">
                <StackPanel DockPanel.Dock="Top">
                    <TextBlock Text="ASTRONOMICON" FontSize="24" FontWeight="Bold" Foreground="#F3F6FF"/>
                    <TextBlock Text="Dashboard v0.1" FontSize="13" Margin="0,4,0,18" Foreground="#8EA6FF"/>

                    <Button Name="btnNavGeneralTask" Content="General Task" Margin="0,0,0,8" Height="42" Background="#5A3DF0" Foreground="White" BorderThickness="0"/>
                    <Button Name="btnNavLocalTasks" Content="Local Tasks" Margin="0,0,0,8" Height="38" Background="#18203A" Foreground="#DDE6FF" BorderBrush="#283557"/>
                    <Button Name="btnNavOutput" Content="Output / Results" Margin="0,0,0,8" Height="38" Background="#18203A" Foreground="#DDE6FF" BorderBrush="#283557"/>
                    <Button Name="btnNavLogs" Content="Logs" Margin="0,0,0,8" Height="38" Background="#18203A" Foreground="#DDE6FF" BorderBrush="#283557"/>

                    <Separator Margin="0,16,0,16"/>

                    <TextBlock Text="Actions" FontSize="14" FontWeight="SemiBold" Foreground="#9CB2FF" Margin="0,0,0,10"/>

                    <Button Name="btnLoadTemplate" Content="Load Template" Margin="0,0,0,8" Height="38" Background="#152847" Foreground="#DDE6FF" BorderBrush="#34507D"/>
                    <Button Name="btnSaveForm" Content="Save Form" Margin="0,0,0,8" Height="38" Background="#152847" Foreground="#DDE6FF" BorderBrush="#34507D"/>
                    <Button Name="btnParse" Content="Parse to Local Tasks" Margin="0,0,0,8" Height="42" Background="#11A7B8" Foreground="White" BorderThickness="0"/>
                    <Button Name="btnRefreshLocalTasks" Content="Refresh Local Tasks" Margin="0,0,0,8" Height="38" Background="#152847" Foreground="#DDE6FF" BorderBrush="#34507D"/>
                    <Button Name="btnOpenTaskRoot" Content="Open Task Root" Margin="0,0,0,8" Height="38" Background="#152847" Foreground="#DDE6FF" BorderBrush="#34507D"/>
                    <Button Name="btnOpenOutput" Content="Open Output" Margin="0,0,0,8" Height="38" Background="#152847" Foreground="#DDE6FF" BorderBrush="#34507D"/>
                </StackPanel>

                <Border DockPanel.Dock="Bottom" CornerRadius="12" Background="#12182C" Padding="12" Margin="0,18,0,0">
                    <StackPanel>
                        <TextBlock Text="Current target" FontWeight="SemiBold" Foreground="#9CB2FF"/>
                        <TextBlock Name="txtLeftCurrentTaskId" Text="No task loaded" Margin="0,8,0,0" TextWrapping="Wrap"/>
                    </StackPanel>
                </Border>
            </DockPanel>
        </Border>

        <!-- Center content -->
        <Border Grid.Column="1" CornerRadius="18" Background="#0B1020" BorderBrush="#24304F" BorderThickness="1" Margin="0,0,10,0">
            <Grid Margin="16">
                <Grid.RowDefinitions>
                    <RowDefinition Height="Auto"/>
                    <RowDefinition Height="Auto"/>
                    <RowDefinition Height="*"/>
                </Grid.RowDefinitions>

                <StackPanel Grid.Row="0" Margin="0,0,0,12">
                    <TextBlock Text="Astronomicon General Task Workbench" FontSize="28" FontWeight="Bold" Foreground="#F4F7FF"/>
                    <TextBlock Text="Strict General Task form -> parser -> Local Tasks. Dark neon shell now, deeper organ integration next." Margin="0,6,0,0" FontSize="13" Foreground="#95A8D8"/>
                </StackPanel>

                <Grid Grid.Row="1" Margin="0,0,0,12">
                    <Grid.ColumnDefinitions>
                        <ColumnDefinition Width="*"/>
                        <ColumnDefinition Width="*"/>
                    </Grid.ColumnDefinitions>
                    <Grid.RowDefinitions>
                        <RowDefinition Height="Auto"/>
                        <RowDefinition Height="Auto"/>
                        <RowDefinition Height="Auto"/>
                        <RowDefinition Height="Auto"/>
                    </Grid.RowDefinitions>

                    <StackPanel Grid.Row="0" Grid.Column="0" Margin="0,0,10,8">
                        <TextBlock Text="Repository Root" Margin="0,0,0,4" Foreground="#9CB2FF"/>
                        <TextBox Name="txtRepoRoot" Height="30" Background="#10182D" Foreground="#F2F6FF" BorderBrush="#314368"/>
                    </StackPanel>

                    <StackPanel Grid.Row="0" Grid.Column="1" Margin="10,0,0,8">
                        <TextBlock Text="Parser Path" Margin="0,0,0,4" Foreground="#9CB2FF"/>
                        <TextBox Name="txtParserPath" Height="30" Background="#10182D" Foreground="#F2F6FF" BorderBrush="#314368"/>
                    </StackPanel>

                    <StackPanel Grid.Row="1" Grid.Column="0" Margin="0,0,10,8">
                        <TextBlock Text="GENERAL_TASK_ID" Margin="0,0,0,4" Foreground="#9CB2FF"/>
                        <TextBox Name="txtTaskId" Height="30" Background="#10182D" Foreground="#F2F6FF" BorderBrush="#314368"/>
                    </StackPanel>

                    <StackPanel Grid.Row="1" Grid.Column="1" Margin="10,0,0,8">
                        <TextBlock Text="GENERAL_TASK_CODE" Margin="0,0,0,4" Foreground="#9CB2FF"/>
                        <TextBox Name="txtTaskCode" Height="30" Background="#10182D" Foreground="#F2F6FF" BorderBrush="#314368"/>
                    </StackPanel>

                    <StackPanel Grid.Row="2" Grid.Column="0" Margin="0,0,10,8">
                        <TextBlock Text="Title" Margin="0,0,0,4" Foreground="#9CB2FF"/>
                        <TextBox Name="txtTitle" Height="30" Background="#10182D" Foreground="#F2F6FF" BorderBrush="#314368"/>
                    </StackPanel>

                    <StackPanel Grid.Row="2" Grid.Column="1" Margin="10,0,0,8">
                        <TextBlock Text="Author" Margin="0,0,0,4" Foreground="#9CB2FF"/>
                        <TextBox Name="txtAuthor" Height="30" Background="#10182D" Foreground="#F2F6FF" BorderBrush="#314368"/>
                    </StackPanel>

                    <Grid Grid.Row="3" Grid.ColumnSpan="2">
                        <Grid.ColumnDefinitions>
                            <ColumnDefinition Width="*"/>
                            <ColumnDefinition Width="*"/>
                            <ColumnDefinition Width="2*"/>
                        </Grid.ColumnDefinitions>

                        <StackPanel Grid.Column="0" Margin="0,0,10,0">
                            <TextBlock Text="Execution Intent" Margin="0,0,0,4" Foreground="#9CB2FF"/>
                            <ComboBox Name="cmbExecutionIntent" Height="30" Background="#10182D" Foreground="#F2F6FF" BorderBrush="#314368">
                                <ComboBoxItem Content="manual"/>
                                <ComboBoxItem Content="scripted"/>
                            </ComboBox>
                        </StackPanel>

                        <StackPanel Grid.Column="1" Margin="10,0,10,0">
                            <TextBlock Text="Priority" Margin="0,0,0,4" Foreground="#9CB2FF"/>
                            <ComboBox Name="cmbPriority" Height="30" Background="#10182D" Foreground="#F2F6FF" BorderBrush="#314368">
                                <ComboBoxItem Content="high"/>
                                <ComboBoxItem Content="medium"/>
                                <ComboBoxItem Content="low"/>
                            </ComboBox>
                        </StackPanel>

                        <StackPanel Grid.Column="2" Margin="10,0,0,0">
                            <TextBlock Text="Task Root" Margin="0,0,0,4" Foreground="#9CB2FF"/>
                            <TextBox Name="txtTaskRoot" Height="30" Background="#10182D" Foreground="#F2F6FF" BorderBrush="#314368"/>
                        </StackPanel>
                    </Grid>
                </Grid>

                <Border Grid.Row="2" Background="#0E1428" BorderBrush="#2C3E66" BorderThickness="1" CornerRadius="16" Padding="12">
                    <DockPanel LastChildFill="True">
                        <TextBlock DockPanel.Dock="Top" Text="General Task Form" FontSize="16" FontWeight="SemiBold" Foreground="#9CB2FF" Margin="0,0,0,10"/>
                        <TextBox Name="txtGeneralTaskForm"
                                 AcceptsReturn="True"
                                 AcceptsTab="True"
                                 TextWrapping="Wrap"
                                 VerticalScrollBarVisibility="Auto"
                                 HorizontalScrollBarVisibility="Auto"
                                 Background="#0A0F1F"
                                 Foreground="#F5F8FF"
                                 BorderThickness="0"
                                 FontFamily="Consolas"
                                 FontSize="14"/>
                    </DockPanel>
                </Border>
            </Grid>
        </Border>

        <!-- Right side -->
        <Border Grid.Column="2" CornerRadius="18" Background="#0E1324" BorderBrush="#24304F" BorderThickness="1">
            <Grid Margin="16">
                <Grid.RowDefinitions>
                    <RowDefinition Height="Auto"/>
                    <RowDefinition Height="220"/>
                    <RowDefinition Height="230"/>
                    <RowDefinition Height="*"/>
                </Grid.RowDefinitions>

                <StackPanel Grid.Row="0" Margin="0,0,0,12">
                    <TextBlock Text="Live Status" FontSize="20" FontWeight="Bold" Foreground="#F4F7FF"/>
                    <TextBlock Name="txtStatusLine" Text="Idle" Margin="0,6,0,0" Foreground="#7FE6FF"/>
                </StackPanel>

                <Border Grid.Row="1" Background="#10182D" BorderBrush="#2A3A5D" BorderThickness="1" CornerRadius="14" Padding="10" Margin="0,0,0,12">
                    <DockPanel>
                        <TextBlock DockPanel.Dock="Top" Text="Local Tasks" FontWeight="SemiBold" Foreground="#9CB2FF" Margin="0,0,0,8"/>
                        <ListBox Name="lstLocalTasks"
                                 Background="#0A0F1F"
                                 Foreground="#F2F6FF"
                                 BorderThickness="0"/>
                    </DockPanel>
                </Border>

                <Border Grid.Row="2" Background="#10182D" BorderBrush="#2A3A5D" BorderThickness="1" CornerRadius="14" Padding="10" Margin="0,0,0,12">
                    <DockPanel>
                        <TextBlock DockPanel.Dock="Top" Text="Preview" FontWeight="SemiBold" Foreground="#9CB2FF" Margin="0,0,0,8"/>
                        <TextBox Name="txtPreview"
                                 AcceptsReturn="True"
                                 TextWrapping="Wrap"
                                 VerticalScrollBarVisibility="Auto"
                                 Background="#0A0F1F"
                                 Foreground="#F2F6FF"
                                 BorderThickness="0"
                                 FontFamily="Consolas"
                                 IsReadOnly="True"/>
                    </DockPanel>
                </Border>

                <Border Grid.Row="3" Background="#10182D" BorderBrush="#2A3A5D" BorderThickness="1" CornerRadius="14" Padding="10">
                    <DockPanel>
                        <TextBlock DockPanel.Dock="Top" Text="Log" FontWeight="SemiBold" Foreground="#9CB2FF" Margin="0,0,0,8"/>
                        <TextBox Name="txtLog"
                                 AcceptsReturn="True"
                                 TextWrapping="Wrap"
                                 VerticalScrollBarVisibility="Auto"
                                 Background="#0A0F1F"
                                 Foreground="#D9E8FF"
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

$txtRepoRoot = $Window.FindName("txtRepoRoot")
$txtParserPath = $Window.FindName("txtParserPath")
$txtTaskId = $Window.FindName("txtTaskId")
$txtTaskCode = $Window.FindName("txtTaskCode")
$txtTitle = $Window.FindName("txtTitle")
$txtAuthor = $Window.FindName("txtAuthor")
$cmbExecutionIntent = $Window.FindName("cmbExecutionIntent")
$cmbPriority = $Window.FindName("cmbPriority")
$txtTaskRoot = $Window.FindName("txtTaskRoot")
$txtGeneralTaskForm = $Window.FindName("txtGeneralTaskForm")
$txtStatusLine = $Window.FindName("txtStatusLine")
$lstLocalTasks = $Window.FindName("lstLocalTasks")
$txtPreview = $Window.FindName("txtPreview")
$txtLog = $Window.FindName("txtLog")
$txtLeftCurrentTaskId = $Window.FindName("txtLeftCurrentTaskId")

$btnLoadTemplate = $Window.FindName("btnLoadTemplate")
$btnSaveForm = $Window.FindName("btnSaveForm")
$btnParse = $Window.FindName("btnParse")
$btnRefreshLocalTasks = $Window.FindName("btnRefreshLocalTasks")
$btnOpenTaskRoot = $Window.FindName("btnOpenTaskRoot")
$btnOpenOutput = $Window.FindName("btnOpenOutput")

$txtRepoRoot.Text = $script:RepoRoot
$txtParserPath.Text = $script:DefaultParserPath
$txtTaskId.Text = Get-DefaultTaskId
$txtTaskCode.Text = "ASTRONOMICON_GENERAL_TASK"
$txtTitle.Text = "Astronomicon New General Task"
$txtAuthor.Text = "Owner"
$cmbExecutionIntent.SelectedIndex = 0
$cmbPriority.SelectedIndex = 0
$txtTaskRoot.Text = ""
$txtLeftCurrentTaskId.Text = $txtTaskId.Text

function Write-Log {
    param([string]$Message)
    $Stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $txtLog.AppendText("[$Stamp] $Message`r`n")
    $txtLog.ScrollToEnd()
}

function Set-Status {
    param([string]$Text)
    $txtStatusLine.Text = $Text
}

function Save-CurrentForm {
    $GeneralTaskId = $txtTaskId.Text.Trim()
    if ([string]::IsNullOrWhiteSpace($GeneralTaskId)) {
        throw "GENERAL_TASK_ID is empty."
    }

    $Layout = Ensure-TaskLayout $GeneralTaskId

    if ([string]::IsNullOrWhiteSpace($txtGeneralTaskForm.Text)) {
        throw "General Task form is empty."
    }

    Write-Utf8Bom -Path $Layout.input_path -Content $txtGeneralTaskForm.Text

    $State = [ordered]@{
        general_task_id = $GeneralTaskId
        general_task_code = $txtTaskCode.Text.Trim()
        title = $txtTitle.Text.Trim()
        author = $txtAuthor.Text.Trim()
        parser_path = $txtParserPath.Text.Trim()
        saved_at = (Get-Date).ToString("o")
    }
    ($State | ConvertTo-Json -Depth 6) | Set-Content -Encoding UTF8 $Layout.state_path

    $txtTaskRoot.Text = $Layout.task_root
    $txtLeftCurrentTaskId.Text = $GeneralTaskId
    $script:CurrentOutputRoot = $Layout.output_root

    Write-Log "Saved General Task form -> $($Layout.input_path)"
    return $Layout
}

function Refresh-LocalTasks {
    $lstLocalTasks.Items.Clear()

    if ([string]::IsNullOrWhiteSpace($script:CurrentOutputRoot)) {
        return
    }

    $LocalTasksRoot = Join-Path $script:CurrentOutputRoot "LOCAL_TASKS"
    if (!(Test-Path $LocalTasksRoot)) {
        return
    }

    Get-ChildItem $LocalTasksRoot -Directory | Sort-Object Name | ForEach-Object {
        [void]$lstLocalTasks.Items.Add($_.Name)
    }

    Write-Log "Refreshed Local Tasks list."
}

$lstLocalTasks.Add_SelectionChanged({
    if ($null -eq $lstLocalTasks.SelectedItem) {
        return
    }

    $Selected = [string]$lstLocalTasks.SelectedItem
    if ([string]::IsNullOrWhiteSpace($script:CurrentOutputRoot)) {
        return
    }

    $MdPath = Join-Path $script:CurrentOutputRoot "LOCAL_TASKS\$Selected\LOCAL_TASK.md"
    $JsonPath = Join-Path $script:CurrentOutputRoot "LOCAL_TASKS\$Selected\LOCAL_TASK.json"

    if (Test-Path $MdPath) {
        $txtPreview.Text = Get-Content -Encoding UTF8 $MdPath -Raw
        Set-Status "Previewing $Selected"
    }
    elseif (Test-Path $JsonPath) {
        $txtPreview.Text = Get-Content -Encoding UTF8 $JsonPath -Raw
        Set-Status "Previewing $Selected"
    }
})

$btnLoadTemplate.Add_Click({
    try {
        $Intent = $cmbExecutionIntent.Text
        $Priority = $cmbPriority.Text
        $txtGeneralTaskForm.Text = Get-GeneralTaskTemplate `
            -GeneralTaskId $txtTaskId.Text.Trim() `
            -TaskTitle $txtTitle.Text.Trim() `
            -TaskCode $txtTaskCode.Text.Trim() `
            -Author $txtAuthor.Text.Trim() `
            -ExecutionIntent $Intent `
            -Priority $Priority

        Set-Status "Template loaded"
        Write-Log "Loaded strict General Task template."
    }
    catch {
        Set-Status "Template load failed"
        Write-Log "ERROR: $($_.Exception.Message)"
    }
})

$btnSaveForm.Add_Click({
    try {
        $Layout = Save-CurrentForm
        Set-Status "Form saved"
        $txtPreview.Text = Get-Content -Encoding UTF8 $Layout.input_path -Raw
    }
    catch {
        Set-Status "Save failed"
        Write-Log "ERROR: $($_.Exception.Message)"
    }
})

$btnParse.Add_Click({
    try {
        $Layout = Save-CurrentForm

        $ParserPath = $txtParserPath.Text.Trim()
        if (!(Test-Path $ParserPath)) {
            throw "Parser not found: $ParserPath"
        }

        Set-Status "Parsing..."
        Write-Log "Running parser..."
        Write-Log "Parser path: $ParserPath"

        $Result = & powershell.exe -ExecutionPolicy Bypass -File $ParserPath `
            -InputPath $Layout.input_path `
            -OutputRoot $Layout.output_root 2>&1 | Out-String

        if ($Result) {
            Write-Log ($Result.Trim())
        }

        $script:CurrentOutputRoot = $Layout.output_root
        Refresh-LocalTasks

        $RouteTestPath = Join-Path $Layout.output_root "SERVITOR_ROUTE_TEST.md"
        if (Test-Path $RouteTestPath) {
            $txtPreview.Text = Get-Content -Encoding UTF8 $RouteTestPath -Raw
        }

        Set-Status "Parse complete"
    }
    catch {
        Set-Status "Parse failed"
        Write-Log "ERROR: $($_.Exception.Message)"
    }
})

$btnRefreshLocalTasks.Add_Click({
    try {
        Refresh-LocalTasks
        Set-Status "Local Tasks refreshed"
    }
    catch {
        Set-Status "Refresh failed"
        Write-Log "ERROR: $($_.Exception.Message)"
    }
})

$btnOpenTaskRoot.Add_Click({
    try {
        if ([string]::IsNullOrWhiteSpace($txtTaskRoot.Text)) {
            throw "Task root is empty."
        }
        Start-Process explorer.exe $txtTaskRoot.Text
        Set-Status "Opened task root"
    }
    catch {
        Set-Status "Open task root failed"
        Write-Log "ERROR: $($_.Exception.Message)"
    }
})

$btnOpenOutput.Add_Click({
    try {
        if ([string]::IsNullOrWhiteSpace($script:CurrentOutputRoot)) {
            throw "Output root is empty."
        }
        Start-Process explorer.exe $script:CurrentOutputRoot
        Set-Status "Opened output"
    }
    catch {
        Set-Status "Open output failed"
        Write-Log "ERROR: $($_.Exception.Message)"
    }
})

$Window.Add_ContentRendered({
    try {
        $txtGeneralTaskForm.Text = Get-GeneralTaskTemplate `
            -GeneralTaskId $txtTaskId.Text.Trim() `
            -TaskTitle $txtTitle.Text.Trim() `
            -TaskCode $txtTaskCode.Text.Trim() `
            -Author $txtAuthor.Text.Trim() `
            -ExecutionIntent $cmbExecutionIntent.Text `
            -Priority $cmbPriority.Text

        Set-Status "Ready"
        Write-Log "Astronomicon Dashboard v0.1 started."
        Write-Log "Visual shell is active. Real parser is wired."
    }
    catch {
        Set-Status "Init failed"
        Write-Log "ERROR: $($_.Exception.Message)"
    }
})

[void]$Window.ShowDialog()