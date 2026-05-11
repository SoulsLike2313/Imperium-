param(

    [string]$InputPath = "E:\IMPERIUM\ASTRONOMICON\SMOKE_TESTS\GTASK-20260510-ASTRONOMICON-FORM-SMOKE-V0_1\GENERAL_TASK_INPUT.txt",

    [string]$OutputRoot = ""

)



$ErrorActionPreference = "Stop"



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

    [System.IO.File]::WriteAllText($Path, $Content.Replace("`n", "`r`n"), $Utf8Bom)

}



function Get-Sha256String {

    param([Parameter(Mandatory=$true)][string]$Text)



    $Sha = [System.Security.Cryptography.SHA256]::Create()

    $Bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)

    $HashBytes = $Sha.ComputeHash($Bytes)

    return ([System.BitConverter]::ToString($HashBytes)).Replace("-", "").ToLowerInvariant()

}



function Normalize-Text {

    param([string]$Text)

    return (($Text -replace "`r`n", "`n") -replace "`r", "`n")

}



function Get-ScalarField {

    param(

        [Parameter(Mandatory=$true)][string]$Text,

        [Parameter(Mandatory=$true)][string]$Name

    )



    $Escaped = [regex]::Escape($Name)

    $Pattern = "(?ms)^$Escaped\s*:\s*\n(?<v>.*?)(?=\n\n[A-Z0-9_]+:|\n\nBEGIN_|\n---|$)"

    $Match = [regex]::Match($Text, $Pattern)



    if ($Match.Success) {

        return $Match.Groups["v"].Value.Trim()

    }



    return ""

}



function Get-Block {

    param(

        [Parameter(Mandatory=$true)][string]$Text,

        [Parameter(Mandatory=$true)][string]$Name

    )



    $Begin = "BEGIN_$Name"

    $End = "END_$Name"

    $Pattern = "(?ms)^$Begin\s*\n(?<v>.*?)\n$End\s*"

    $Match = [regex]::Match($Text, $Pattern)



    if ($Match.Success) {

        return $Match.Groups["v"].Value.Trim()

    }



    return ""

}



if (!(Test-Path $InputPath)) {

    throw "Input file not found: $InputPath"

}



if ([string]::IsNullOrWhiteSpace($OutputRoot)) {

    $OutputRoot = Join-Path (Split-Path -Parent $InputPath) "OUTPUT"

}



$RawText = [System.IO.File]::ReadAllText($InputPath, [System.Text.Encoding]::UTF8)

$Text = Normalize-Text $RawText

$SourceHash = Get-Sha256String $Text



if (!($Text.StartsWith("ASTRONOMICON_GENERAL_TASK_V0_1"))) {

    throw "Invalid format: missing ASTRONOMICON_GENERAL_TASK_V0_1 header."

}



$ExplicitGeneralTaskId = Get-ScalarField $Text "GENERAL_TASK_ID"
$Title = Get-ScalarField $Text "GENERAL_TASK_TITLE"

$Code = Get-ScalarField $Text "GENERAL_TASK_CODE"

$Author = Get-ScalarField $Text "AUTHOR"

$ExecutionIntent = Get-ScalarField $Text "EXECUTION_INTENT"

$Priority = Get-ScalarField $Text "PRIORITY"



$Goal = Get-Block $Text "GOAL"

$Context = Get-Block $Text "CONTEXT"

$CurrentProblem = Get-Block $Text "CURRENT_PROBLEM"

$ExpectedFinalState = Get-Block $Text "EXPECTED_FINAL_STATE"

$HardConstraints = Get-Block $Text "HARD_CONSTRAINTS"

$DoNotDo = Get-Block $Text "DO_NOT_DO"

$KnownRisks = Get-Block $Text "KNOWN_RISKS"

$RequiredOrgans = Get-Block $Text "REQUIRED_ORGANS"

$RequiredInputs = Get-Block $Text "REQUIRED_INPUTS"

$ExpectedArtifacts = Get-Block $Text "EXPECTED_ARTIFACTS"

$OwnerNotes = Get-Block $Text "OWNER_NOTES"

$PlanBlock = Get-Block $Text "PLAN_ITEMS"



$Missing = @()

foreach ($Pair in @(

    @{Name="GENERAL_TASK_TITLE"; Value=$Title},

    @{Name="GENERAL_TASK_CODE"; Value=$Code},

    @{Name="GOAL"; Value=$Goal},

    @{Name="EXPECTED_FINAL_STATE"; Value=$ExpectedFinalState},

    @{Name="PLAN_ITEMS"; Value=$PlanBlock}

)) {

    if ([string]::IsNullOrWhiteSpace($Pair.Value)) {

        $Missing += $Pair.Name

    }

}



$ItemPattern = "(?ms)ITEM_ID:\s*(?<item_id>PI-\d+)\s*\nTITLE:\s*(?<title>.*?)\nTEXT:\s*\n(?<text>.*?)\nEXPECTED_OUTPUT:\s*\n(?<expected_output>.*?)\nREQUIRED_ORGANS:\s*\n(?<required_organs>.*?)\nEXECUTION_MODE:\s*\n(?<execution_mode>.*?)\nDEPENDS_ON:\s*\n(?<depends_on>.*?)\nEND_ITEM"

$ItemMatches = [regex]::Matches($PlanBlock, $ItemPattern)



if ($ItemMatches.Count -eq 0) {

    $Missing += "PLAN_ITEMS.ITEM"

}



New-Item -ItemType Directory -Force $OutputRoot | Out-Null



$Validation = [ordered]@{

    schema_version = "ASTRONOMICON_GENERAL_TASK_VALIDATION_V0_1"

    input_path = $InputPath

    output_root = $OutputRoot

    source_sha256 = $SourceHash

    valid = ($Missing.Count -eq 0)

    missing_fields = $Missing

    plan_items_detected = $ItemMatches.Count

    generated_at = (Get-Date).ToString("o")

}



Write-Utf8Bom "$OutputRoot\VALIDATION_REPORT.json" ($Validation | ConvertTo-Json -Depth 8)



if ($Missing.Count -gt 0) {

    throw "Validation failed. Missing: $($Missing -join ', '). See $OutputRoot\VALIDATION_REPORT.json"

}



$DateStamp = Get-Date -Format "yyyyMMdd"

$CodeSlug = (($Code -replace "[^A-Za-z0-9]+", "-").Trim("-")).ToUpperInvariant()

$GeneralTaskId = "GTASK-$DateStamp-$CodeSlug-V0_1"



$GeneralRoot = Join-Path $OutputRoot "GENERAL_TASK"

$LocalRoot = Join-Path $OutputRoot "LOCAL_TASKS"

New-Item -ItemType Directory -Force $GeneralRoot, $LocalRoot | Out-Null



Copy-Item $InputPath "$GeneralRoot\SOURCE_TEXT.txt" -Force



$GeneralTask = [ordered]@{

    schema_version = "ASTRONOMICON_GENERAL_TASK_RECORD_V0_1"

    general_task_id = $GeneralTaskId

    title = $Title

    code = $Code

    author = $Author

    execution_intent = $ExecutionIntent

    priority = $Priority

    source_path = $InputPath

    source_sha256 = $SourceHash

    status = "REGISTERED"

    goal = $Goal

    context = $Context

    current_problem = $CurrentProblem

    expected_final_state = $ExpectedFinalState

    hard_constraints = $HardConstraints

    do_not_do = $DoNotDo

    known_risks = $KnownRisks

    required_organs = $RequiredOrgans

    required_inputs = $RequiredInputs

    expected_artifacts = $ExpectedArtifacts

    owner_notes = $OwnerNotes

    created_at = (Get-Date).ToString("o")

}



$GeneralJson = $GeneralTask | ConvertTo-Json -Depth 12

Write-Utf8Bom "$GeneralRoot\GENERAL_TASK.json" $GeneralJson



$GeneralMd = @(

    "# General Task",

    "",

    "GENERAL_TASK_ID: $GeneralTaskId",

    "",

    "TITLE:",

    $Title,

    "",

    "STATUS:",

    "REGISTERED",

    "",

    "SOURCE_SHA256:",

    $SourceHash,

    "",

    "GOAL:",

    $Goal,

    "",

    "EXPECTED FINAL STATE:",

    $ExpectedFinalState

) -join "`n"



Write-Utf8Bom "$GeneralRoot\GENERAL_TASK.md" $GeneralMd



$GeneralHashRecord = [ordered]@{

    general_task_id = $GeneralTaskId

    source_sha256 = $SourceHash

    record_sha256 = Get-Sha256String $GeneralJson

    hash_policy = "sha256 over UTF-8 normalized source and JSON record"

}

Write-Utf8Bom "$GeneralRoot\HASH.json" ($GeneralHashRecord | ConvertTo-Json -Depth 8)



$RegistryItems = @()

$Index = 1



foreach ($Match in $ItemMatches) {

    $LocalNumber = "{0:D3}" -f $Index

    $LocalTaskId = "LTASK-$LocalNumber"

    $LocalTaskRoot = Join-Path $LocalRoot $LocalTaskId

    New-Item -ItemType Directory -Force $LocalTaskRoot | Out-Null



    $ItemId = $Match.Groups["item_id"].Value.Trim()

    $ItemTitle = $Match.Groups["title"].Value.Trim()

    $ItemText = $Match.Groups["text"].Value.Trim()

    $ExpectedOutput = $Match.Groups["expected_output"].Value.Trim()

    $RequiredOrgansText = $Match.Groups["required_organs"].Value.Trim()

    $ExecutionMode = $Match.Groups["execution_mode"].Value.Trim()

    $DependsOnText = $Match.Groups["depends_on"].Value.Trim()



    $RequiredOrgansList = @(

        $RequiredOrgansText -split "," |

            ForEach-Object { $_.Trim() } |

            Where-Object { $_ -ne "" }

    )



    $DependsOnList = @()

    if ($DependsOnText -and $DependsOnText.ToLowerInvariant() -ne "none") {

        $DependsOnList = @(

            $DependsOnText -split "," |

                ForEach-Object { $_.Trim() } |

                Where-Object { $_ -ne "" }

        )

    }



    $LocalTask = [ordered]@{

        schema_version = "ASTRONOMICON_LOCAL_TASK_RECORD_V0_1"

        local_task_id = $LocalTaskId

        source_plan_item_id = $ItemId

        parent_general_task_id = $GeneralTaskId

        title = $ItemTitle

        scope_text = $ItemText

        expected_output = $ExpectedOutput

        required_organs = $RequiredOrgansList

        execution_mode = $ExecutionMode

        depends_on_plan_items = $DependsOnList

        status = "CREATED_FROM_GENERAL_TASK"

        speculum_review_status = "NOT_REQUESTED"

        stage_decomposition_status = "NOT_STARTED"

        created_at = (Get-Date).ToString("o")

    }



    $LocalJson = $LocalTask | ConvertTo-Json -Depth 12

    $LocalHash = Get-Sha256String $LocalJson



    Write-Utf8Bom "$LocalTaskRoot\LOCAL_TASK.json" $LocalJson



    $LocalMd = @(

        "# Local Task",

        "",

        "LOCAL_TASK_ID: $LocalTaskId",

        "PARENT_GENERAL_TASK_ID: $GeneralTaskId",

        "SOURCE_PLAN_ITEM_ID: $ItemId",

        "",

        "TITLE:",

        $ItemTitle,

        "",

        "SCOPE:",

        $ItemText,

        "",

        "EXPECTED_OUTPUT:",

        $ExpectedOutput,

        "",

        "REQUIRED_ORGANS:",

        ($RequiredOrgansList -join ", "),

        "",

        "EXECUTION_MODE:",

        $ExecutionMode,

        "",

        "STATUS:",

        "CREATED_FROM_GENERAL_TASK",

        "",

        "HASH:",

        $LocalHash

    ) -join "`n"



    Write-Utf8Bom "$LocalTaskRoot\LOCAL_TASK.md" $LocalMd



    $HashRecord = [ordered]@{

        local_task_id = $LocalTaskId

        parent_general_task_id = $GeneralTaskId

        record_sha256 = $LocalHash

        hash_policy = "sha256 over UTF-8 JSON record"

    }

    Write-Utf8Bom "$LocalTaskRoot\HASH.json" ($HashRecord | ConvertTo-Json -Depth 8)



    $StatusRecord = [ordered]@{

        local_task_id = $LocalTaskId

        status = "CREATED_FROM_GENERAL_TASK"

        speculum_review_status = "NOT_REQUESTED"

        stage_decomposition_status = "NOT_STARTED"

        ready_for_servitor_routing = $true

    }

    Write-Utf8Bom "$LocalTaskRoot\STATUS.json" ($StatusRecord | ConvertTo-Json -Depth 8)



    $RegistryItems += [ordered]@{

        local_task_id = $LocalTaskId

        source_plan_item_id = $ItemId

        title = $ItemTitle

        execution_mode = $ExecutionMode

        required_organs = $RequiredOrgansList

        expected_output = $ExpectedOutput

        hash = $LocalHash

        path = "LOCAL_TASKS/$LocalTaskId"

    }



    $Index++

}



$Registry = [ordered]@{

    schema_version = "ASTRONOMICON_LOCAL_TASK_REGISTRY_V0_1"

    general_task_id = $GeneralTaskId

    source_sha256 = $SourceHash

    local_task_count = $RegistryItems.Count

    local_tasks = $RegistryItems

    generated_at = (Get-Date).ToString("o")

}



Write-Utf8Bom "$OutputRoot\LOCAL_TASK_REGISTRY.json" ($Registry | ConvertTo-Json -Depth 12)



$RouteTest = @(

    "# Servitor Route Test",

    "",

    "Purpose:",

    "Проверить, что Servitor можно направить в работу по Local Task ID.",

    "",

    "General Task:",

    $GeneralTaskId,

    "",

    "Example route:",

    "",

    "1. Servitor receives LOCAL_TASK_ID: LTASK-001",

    "2. Servitor opens: LOCAL_TASKS/LTASK-001/LOCAL_TASK.json",

    "3. Servitor reads parent_general_task_id, scope_text, expected_output, required_organs, execution_mode.",

    "4. Servitor goes to Administratum for context/readiness.",

    "5. Servitor follows required organs route.",

    "",

    "Available Local Tasks:",

    ""

)



foreach ($Item in $RegistryItems) {

    $RouteTest += "- $($Item.local_task_id): $($Item.title)"

}



Write-Utf8Bom "$OutputRoot\SERVITOR_ROUTE_TEST.md" ($RouteTest -join "`n")



$Receipt = [ordered]@{

    schema_version = "ASTRONOMICON_GENERAL_TO_LOCAL_PARSE_RECEIPT_V0_1"

    general_task_id = $GeneralTaskId

    input_path = $InputPath

    output_root = $OutputRoot

    source_sha256 = $SourceHash

    local_task_count = $RegistryItems.Count

    validation_passed = $true

    status = "PASS_WITH_LIMITATIONS"

    limitations = @(

        "Smoke parser only.",

        "No Speculum refinement import yet.",

        "No stage decomposition yet.",

        "No dashboard integration yet."

    )

    generated_at = (Get-Date).ToString("o")

}



Write-Utf8Bom "$OutputRoot\PARSE_RECEIPT.json" ($Receipt | ConvertTo-Json -Depth 10)



Write-Host "Astronomicon parse complete."

Write-Host "GENERAL_TASK_ID: $GeneralTaskId"

Write-Host "LOCAL_TASKS: $($RegistryItems.Count)"

Write-Host "OUTPUT_ROOT: $OutputRoot"
