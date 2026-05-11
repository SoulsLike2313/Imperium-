Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName PresentationCore
Add-Type -AssemblyName WindowsBase

$ErrorActionPreference = "Stop"

$script:RepoRoot = "E:\IMPERIUM"
$script:GeneralTasksRoot = "E:\IMPERIUM\ASTRONOMICON\GENERAL_TASKS"
$script:ParserPath = "E:\IMPERIUM\TOOLS\astronomicon_parse_general_task_v0_1.ps1"
$script:CurrentTaskId = $null
$script:CurrentTaskRoot = $null
$script:CurrentInputPath = $null
$script:CurrentOutputRoot = $null

New-Item -ItemType Directory -Force $script:GeneralTasksRoot | Out-Null

function Write-Utf8Bom {
    param([string]$Path, [string]$Content)
    $Dir = Split-Path -Parent $Path
    if ($Dir -and !(Test-Path $Dir)) { New-Item -ItemType Directory -Force $Dir | Out-Null }
    $Utf8Bom = New-Object System.Text.UTF8Encoding($true)
    [System.IO.File]::WriteAllText($Path, $Content.Replace("`n","`r`n"), $Utf8Bom)
}

function New-DefaultTaskId {
    $DateStamp = Get-Date -Format "yyyyMMdd"
    return "GTASK-$DateStamp-ASTRONOMICON-GENERAL-TASK-V0_3"
}

function Ensure-TaskLayout {
    param([string]$TaskId)
    $TaskRoot = Join-Path $script:GeneralTasksRoot $TaskId
    $InputRoot = Join-Path $TaskRoot "INPUT"
    $OutputRoot = Join-Path $TaskRoot "OUTPUT"
    $StateRoot = Join-Path $TaskRoot "STATE"
    New-Item -ItemType Directory -Force $TaskRoot, $InputRoot, $OutputRoot, $StateRoot | Out-Null

    $script:CurrentTaskId = $TaskId
    $script:CurrentTaskRoot = $TaskRoot
    $script:CurrentInputPath = Join-Path $InputRoot "GENERAL_TASK_INPUT.txt"
    $script:CurrentOutputRoot = $OutputRoot
}

function Get-Template {
    param(
        [string]$TaskId,
        [string]$Title,
        [string]$Code,
        [string]$Mode,
        [string]$Priority
    )

@"
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

function Show-GeneralTaskEditor {
    $DialogXaml = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="Create General Task"
        Width="1050"
        Height="820"
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
            <TextBlock Text="Fill strict form or paste from clipboard. Save creates the top pyramid card." Foreground="#8FA2CC" Margin="0,5,0,0"/>
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
            <Button Name="dlgPasteClipboard" Content="Paste from Clipboard" Width="170"/>
            <Button Name="dlgSave" Content="Save General Task" Width="160" Background="#13A9B8" BorderBrush="#13A9B8"/>
            <Button Name="dlgCancel" Content="Cancel" Width="100"/>
        </StackPanel>
    </Grid>
</Window>
"@

    [xml]$Xml = $DialogXaml
    $Reader = New-Object System.Xml.XmlNodeReader $Xml
    $Dialog = [Windows.Markup.XamlReader]::Load($Reader)

    $dlgTaskId = $Dialog.FindName("dlgTaskId")
    $dlgTitle = $Dialog.FindName("dlgTitle")
    $dlgMode = $Dialog.FindName("dlgMode")
    $dlgPriority = $Dialog.FindName("dlgPriority")
    $dlgCode = $Dialog.FindName("dlgCode")
    $dlgForm = $Dialog.FindName("dlgForm")
    $dlgLoadTemplate = $Dialog.FindName("dlgLoadTemplate")
    $dlgPasteClipboard = $Dialog.FindName("dlgPasteClipboard")
    $dlgSave = $Dialog.FindName("dlgSave")
    $dlgCancel = $Dialog.FindName("dlgCancel")

    $dlgTaskId.Text = New-DefaultTaskId
    $dlgTitle.Text = "Astronomicon New General Task"
    $dlgCode.Text = "ASTRONOMICON_GENERAL_TASK"
    $dlgMode.Text = "manual"
    $dlgPriority.Text = "high"

    $LoadTemplateAction = {
        $dlgForm.Text = Get-Template `
            -TaskId $dlgTaskId.Text.Trim() `
            -Title $dlgTitle.Text.Trim() `
            -Code $dlgCode.Text.Trim() `
            -Mode $dlgMode.Text.Trim() `
            -Priority $dlgPriority.Text.Trim()
    }

    $dlgLoadTemplate.Add_Click($LoadTemplateAction)

    $dlgPasteClipboard.Add_Click({
        if ([System.Windows.Clipboard]::ContainsText()) {
            $dlgForm.Text = [System.Windows.Clipboard]::GetText()
        }
    })

    $dlgSave.Add_Click({
        try {
            $TaskId = $dlgTaskId.Text.Trim()
            if ([string]::IsNullOrWhiteSpace($TaskId)) { throw "GENERAL_TASK_ID is empty." }
            if ([string]::IsNullOrWhiteSpace($dlgForm.Text)) { throw "Form is empty." }

            Ensure-TaskLayout $TaskId
            Write-Utf8Bom -Path $script:CurrentInputPath -Content $dlgForm.Text

            $script:MainTaskIdText.Text = $TaskId
            $script:MainTaskTitleText.Text = $dlgTitle.Text.Trim()
            $script:MainTaskRootText.Text = $script:CurrentTaskRoot
            $script:GeneralCardTitle.Text = $dlgTitle.Text.Trim()
            $script:GeneralCardSubtitle.Text = $TaskId
            $script:GeneralCardMeta.Text = "mode: $($dlgMode.Text.Trim()) | priority: $($dlgPriority.Text.Trim())"
            $script:CurrentTargetText.Text = $TaskId
            $script:PreviewText.Text = $dlgForm.Text

            Log "Saved General Task: $TaskId"
            Status "General Task saved as top pyramid card."
            $Dialog.DialogResult = $true
            $Dialog.Close()
        }
        catch {
            [System.Windows.MessageBox]::Show($_.Exception.Message, "Save failed", "OK", "Error") | Out-Null
        }
    })

    $dlgCancel.Add_Click({
        $Dialog.DialogResult = $false
        $Dialog.Close()
    })

    & $LoadTemplateAction
    [void]$Dialog.ShowDialog()
}

[xml]$Xaml = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="IMPERIUM :: ASTRONOMICON DASHBOARD v0.3"
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
            <ColumnDefinition Width="215"/>
            <ColumnDefinition Width="*"/>
            <ColumnDefinition Width="380"/>
        </Grid.ColumnDefinitions>

        <Border Grid.Column="0" CornerRadius="18" Background="#0D1426" BorderBrush="#273858" BorderThickness="1" Margin="0,0,10,0">
            <DockPanel Margin="16">
                <StackPanel DockPanel.Dock="Top">
                    <TextBlock Text="ASTRONOMICON" FontSize="23" FontWeight="Bold"/>
                    <TextBlock Text="Task pyramid v0.3" Foreground="#8DA7FF" Margin="0,4,0,16"/>

                    <Button Name="btnCreateGeneral" Content="Create General Task" Background="#5A3DF0" BorderBrush="#5A3DF0"/>
                    <Button Name="btnParse" Content="Parse → Local Tasks" Background="#13A9B8" BorderBrush="#13A9B8"/>
                    <Button Name="btnRefresh" Content="Refresh Pyramid"/>
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

        <Border Grid.Column="1" CornerRadius="18" Background="#0A1020" BorderBrush="#273858" BorderThickness="1" Margin="0,0,10,0">
            <Grid Margin="18">
                <Grid.RowDefinitions>
                    <RowDefinition Height="Auto"/>
                    <RowDefinition Height="*"/>
                </Grid.RowDefinitions>

                <StackPanel Grid.Row="0" Margin="0,0,0,16">
                    <TextBlock Text="Astronomicon Task Pyramid" FontSize="30" FontWeight="Bold"/>
                    <TextBlock Text="Create General Task as top card. Parse it into Local Tasks. Stages layer is next." Foreground="#8FA2CC" Margin="0,5,0,0"/>
                </StackPanel>

                <Grid Grid.Row="1">
                    <Grid.RowDefinitions>
                        <RowDefinition Height="150"/>
                        <RowDefinition Height="185"/>
                        <RowDefinition Height="185"/>
                        <RowDefinition Height="120"/>
                        <RowDefinition Height="*"/>
                    </Grid.RowDefinitions>

                    <!-- General Task top -->
                    <Border Grid.Row="0" Width="540" HorizontalAlignment="Center" CornerRadius="24" Background="#101A31" BorderBrush="#576DFF" BorderThickness="2" Padding="18" Margin="0,0,0,12">
                        <StackPanel>
                            <TextBlock Text="GENERAL TASK" Foreground="#8DA7FF" FontWeight="Bold" HorizontalAlignment="Center"/>
                            <TextBlock Name="txtGeneralCardTitle" Text="No General Task created" FontSize="22" FontWeight="Bold" TextAlignment="Center" TextWrapping="Wrap" Margin="0,8,0,4"/>
                            <TextBlock Name="txtGeneralCardSubtitle" Text="Create General Task first" Foreground="#C8D5FF" TextAlignment="Center" TextWrapping="Wrap"/>
                            <TextBlock Name="txtGeneralCardMeta" Text="" Foreground="#7FE6FF" TextAlignment="Center" Margin="0,6,0,0"/>
                        </StackPanel>
                    </Border>

                    <!-- Local Tasks layer -->
                    <Border Grid.Row="1" CornerRadius="22" Background="#0E172C" BorderBrush="#3A4F87" BorderThickness="1" Padding="14" Margin="50,0,50,12">
                        <DockPanel>
                            <TextBlock DockPanel.Dock="Top" Text="LOCAL TASKS" Foreground="#8DA7FF" FontWeight="Bold" HorizontalAlignment="Center" Margin="0,0,0,8"/>
                            <ListBox Name="lstLocalTasks" Background="#070C18" Foreground="#F6F8FF" BorderThickness="0" FontFamily="Consolas"/>
                        </DockPanel>
                    </Border>

                    <!-- Stages placeholder -->
                    <Border Grid.Row="2" CornerRadius="22" Background="#0E172C" BorderBrush="#33405E" BorderThickness="1" Padding="14" Margin="85,0,85,12" Opacity="0.8">
                        <StackPanel HorizontalAlignment="Center" VerticalAlignment="Center">
                            <TextBlock Text="STAGES" Foreground="#8DA7FF" FontWeight="Bold" HorizontalAlignment="Center"/>
                            <TextBlock Text="Empty in v0.3. Next: Decompose selected LTASK to stages." Foreground="#A8B8DD" TextAlignment="Center" TextWrapping="Wrap" Margin="0,8,0,0"/>
                        </StackPanel>
                    </Border>

                    <!-- Sanctum placeholder -->
                    <Border Grid.Row="3" CornerRadius="22" Background="#111827" BorderBrush="#5A3DF0" BorderThickness="1" Padding="14" Margin="120,0,120,12" Opacity="0.85">
                        <StackPanel HorizontalAlignment="Center" VerticalAlignment="Center">
                            <TextBlock Text="SANCTUM NAVIGATION LAYER" Foreground="#D8D0FF" FontWeight="Bold" HorizontalAlignment="Center"/>
                            <TextBlock Text="Reserved: task navigation, execution buttons, artifact/commit/push." Foreground="#A8B8DD" TextAlignment="Center" TextWrapping="Wrap" Margin="0,8,0,0"/>
                        </StackPanel>
                    </Border>

                    <!-- Metadata -->
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
            </Grid>
        </Border>

        <Border Grid.Column="2" CornerRadius="18" Background="#0D1426" BorderBrush="#273858" BorderThickness="1">
            <Grid Margin="16">
                <Grid.RowDefinitions>
                    <RowDefinition Height="52"/>
                    <RowDefinition Height="360"/>
                    <RowDefinition Height="*"/>
                </Grid.RowDefinitions>

                <Border Grid.Row="0" Background="#101A31" BorderBrush="#2D426B" BorderThickness="1" CornerRadius="12" Padding="10" Margin="0,0,0,12">
                    <TextBlock Name="txtStatus" Text="Ready" Foreground="#7FE6FF" FontWeight="SemiBold"/>
                </Border>

                <Border Grid.Row="1" CornerRadius="14" Background="#101A31" BorderBrush="#2D426B" BorderThickness="1" Padding="10" Margin="0,0,0,12">
                    <DockPanel>
                        <TextBlock DockPanel.Dock="Top" Text="Preview" Foreground="#8DA7FF" FontWeight="SemiBold" Margin="0,0,0,8"/>
                        <TextBox Name="txtPreview" AcceptsReturn="True" TextWrapping="Wrap" VerticalScrollBarVisibility="Auto" Background="#070C18" Foreground="#F6F8FF" BorderThickness="0" FontFamily="Consolas" IsReadOnly="True"/>
                    </DockPanel>
                </Border>

                <Border Grid.Row="2" CornerRadius="14" Background="#101A31" BorderBrush="#2D426B" BorderThickness="1" Padding="10">
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

$Reader = New-Object System.Xml.XmlNodeReader $Xaml
$Window = [Windows.Markup.XamlReader]::Load($Reader)

$script:MainTaskIdText = $Window.FindName("txtMainTaskId")
$script:MainTaskTitleText = $Window.FindName("txtMainTaskTitle")
$script:MainTaskRootText = $Window.FindName("txtMainTaskRoot")
$script:CurrentTargetText = $Window.FindName("txtCurrentTarget")
$script:GeneralCardTitle = $Window.FindName("txtGeneralCardTitle")
$script:GeneralCardSubtitle = $Window.FindName("txtGeneralCardSubtitle")
$script:GeneralCardMeta = $Window.FindName("txtGeneralCardMeta")
$script:PreviewText = $Window.FindName("txtPreview")

$txtStatus = $Window.FindName("txtStatus")
$txtLog = $Window.FindName("txtLog")
$lstLocalTasks = $Window.FindName("lstLocalTasks")

$btnCreateGeneral = $Window.FindName("btnCreateGeneral")
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

function Refresh-Pyramid {
    $lstLocalTasks.Items.Clear()

    if (!$script:CurrentOutputRoot -or !(Test-Path (Join-Path $script:CurrentOutputRoot "LOCAL_TASKS"))) {
        Status "No Local Tasks yet."
        return
    }

    Get-ChildItem (Join-Path $script:CurrentOutputRoot "LOCAL_TASKS") -Directory | Sort-Object Name | ForEach-Object {
        [void]$lstLocalTasks.Items.Add($_.Name)
    }

    Status "Pyramid refreshed."
}

$btnCreateGeneral.Add_Click({
    try { Show-GeneralTaskEditor }
    catch { Status "ERROR Create General Task: $($_.Exception.Message)" }
})

$btnParse.Add_Click({
    try {
        if (!$script:CurrentInputPath -or !(Test-Path $script:CurrentInputPath)) {
            throw "No General Task saved. Click Create General Task first."
        }

        if (!(Test-Path $script:ParserPath)) {
            throw "Parser not found: $script:ParserPath"
        }

        Status "Parser started."

        $Result = & powershell.exe -ExecutionPolicy Bypass -File $script:ParserPath `
            -InputPath $script:CurrentInputPath `
            -OutputRoot $script:CurrentOutputRoot 2>&1 | Out-String

        if ($Result.Trim()) { Log $Result.Trim() }

        $Route = Join-Path $script:CurrentOutputRoot "SERVITOR_ROUTE_TEST.md"
        if (Test-Path $Route) {
            $script:PreviewText.Text = Get-Content -Encoding UTF8 $Route -Raw
        }

        Refresh-Pyramid
        Status "Parse complete."
    }
    catch {
        Status "ERROR Parse: $($_.Exception.Message)"
    }
})

$btnRefresh.Add_Click({
    try { Refresh-Pyramid }
    catch { Status "ERROR Refresh: $($_.Exception.Message)" }
})

$btnOpenTaskRoot.Add_Click({
    try {
        if (!$script:CurrentTaskRoot -or !(Test-Path $script:CurrentTaskRoot)) {
            throw "No task root yet."
        }
        Start-Process explorer.exe $script:CurrentTaskRoot
        Status "Opened task root."
    }
    catch { Status "ERROR Open Task Root: $($_.Exception.Message)" }
})

$btnOpenOutput.Add_Click({
    try {
        if (!$script:CurrentOutputRoot -or !(Test-Path $script:CurrentOutputRoot)) {
            throw "No output root yet."
        }
        Start-Process explorer.exe $script:CurrentOutputRoot
        Status "Opened output root."
    }
    catch { Status "ERROR Open Output: $($_.Exception.Message)" }
})

$lstLocalTasks.Add_SelectionChanged({
    try {
        if ($null -eq $lstLocalTasks.SelectedItem) { return }
        $Id = [string]$lstLocalTasks.SelectedItem
        $Md = Join-Path $script:CurrentOutputRoot "LOCAL_TASKS\$Id\LOCAL_TASK.md"
        $Json = Join-Path $script:CurrentOutputRoot "LOCAL_TASKS\$Id\LOCAL_TASK.json"

        if (Test-Path $Md) {
            $script:PreviewText.Text = Get-Content -Encoding UTF8 $Md -Raw
        }
        elseif (Test-Path $Json) {
            $script:PreviewText.Text = Get-Content -Encoding UTF8 $Json -Raw
        }

        Status "Selected $Id."
    }
    catch { Status "ERROR Select Local Task: $($_.Exception.Message)" }
})

$Window.Add_ContentRendered({
    Status "Dashboard v0.3 ready. Use Create General Task."
})

[void]$Window.ShowDialog()