param(
    [Parameter(Mandatory = $true)]
    [string]$InputPath,

    [Parameter(Mandatory = $true)]
    [string]$OutputRoot
)

$ErrorActionPreference = "Stop"

. "E:\IMPERIUM\TOOLS\astronomicon_pipeline_common_v0_2.ps1"

if (-not (Test-Path -LiteralPath $InputPath)) {
    throw "Input file not found: $InputPath"
}

Ensure-Directory -Path $OutputRoot

$raw = [System.IO.File]::ReadAllText($InputPath, [System.Text.Encoding]::UTF8)
$text = Get-NormalizedText -Text $raw
$sourceSha256 = Get-Sha256String -Text $text

$header = ($text -split "`n")[0].Trim()
if ($header -ne "ASTRONOMICON_GENERAL_TASK_V0_1") {
    $validation = [ordered]@{
        schema_version = "ASTRONOMICON_GENERAL_TASK_VALIDATION_V0_2"
        valid = $false
        reason = "HEADER_MISMATCH"
        expected_header = "ASTRONOMICON_GENERAL_TASK_V0_1"
        found_header = $header
        input_path = $InputPath
        output_root = $OutputRoot
        source_sha256 = $sourceSha256
        generated_at = (Get-Date).ToString("o")
    }
    Write-JsonFile -Path (Join-Path $OutputRoot "VALIDATION_REPORT.json") -Object $validation -Depth 20
    throw "Invalid strict header in General Task form. Expected ASTRONOMICON_GENERAL_TASK_V0_1."
}

$generalTaskId = Get-ScalarFieldFromStrictText -Text $text -FieldName "GENERAL_TASK_ID"
$title = Get-ScalarFieldFromStrictText -Text $text -FieldName "GENERAL_TASK_TITLE"
$code = Get-ScalarFieldFromStrictText -Text $text -FieldName "GENERAL_TASK_CODE"
$author = Get-ScalarFieldFromStrictText -Text $text -FieldName "AUTHOR"
$executionIntent = Get-ScalarFieldFromStrictText -Text $text -FieldName "EXECUTION_INTENT"
$priority = Get-ScalarFieldFromStrictText -Text $text -FieldName "PRIORITY"

$goal = Get-StrictBlock -Text $text -BlockName "GOAL"
$context = Get-StrictBlock -Text $text -BlockName "CONTEXT"
$currentProblem = Get-StrictBlock -Text $text -BlockName "CURRENT_PROBLEM"
$expectedFinalState = Get-StrictBlock -Text $text -BlockName "EXPECTED_FINAL_STATE"
$hardConstraints = Get-StrictBlock -Text $text -BlockName "HARD_CONSTRAINTS"
$doNotDo = Get-StrictBlock -Text $text -BlockName "DO_NOT_DO"
$knownRisks = Get-StrictBlock -Text $text -BlockName "KNOWN_RISKS"
$requiredOrgans = Get-StrictBlock -Text $text -BlockName "REQUIRED_ORGANS"
$requiredInputs = Get-StrictBlock -Text $text -BlockName "REQUIRED_INPUTS"
$expectedArtifacts = Get-StrictBlock -Text $text -BlockName "EXPECTED_ARTIFACTS"
$ownerNotes = Get-StrictBlock -Text $text -BlockName "OWNER_NOTES"
$planBlock = Get-StrictBlock -Text $text -BlockName "PLAN_ITEMS"

$missing = @()
foreach ($required in @(
        @{ Name = "GENERAL_TASK_ID"; Value = $generalTaskId },
        @{ Name = "GENERAL_TASK_TITLE"; Value = $title },
        @{ Name = "GENERAL_TASK_CODE"; Value = $code },
        @{ Name = "GOAL"; Value = $goal },
        @{ Name = "EXPECTED_FINAL_STATE"; Value = $expectedFinalState },
        @{ Name = "PLAN_ITEMS"; Value = $planBlock }
    )) {
    if ([string]::IsNullOrWhiteSpace($required.Value)) {
        $missing += $required.Name
    }
}

$itemPattern = "(?ms)ITEM_ID:\s*(?<item_id>PI-\d+)\s*\nTITLE:\s*(?<title>.*?)\nTEXT:\s*\n(?<text>.*?)\nEXPECTED_OUTPUT:\s*\n(?<expected_output>.*?)\nREQUIRED_ORGANS:\s*\n(?<required_organs>.*?)\nEXECUTION_MODE:\s*\n(?<execution_mode>.*?)\nDEPENDS_ON:\s*\n(?<depends_on>.*?)\nEND_ITEM"
$matches = [regex]::Matches($planBlock, $itemPattern)
if ($matches.Count -eq 0) {
    $missing += "PLAN_ITEMS.ITEM"
}

$validation = [ordered]@{
    schema_version = "ASTRONOMICON_GENERAL_TASK_VALIDATION_V0_2"
    valid = ($missing.Count -eq 0)
    missing_fields = $missing
    input_path = $InputPath
    output_root = $OutputRoot
    source_sha256 = $sourceSha256
    plan_items_detected = $matches.Count
    generated_at = (Get-Date).ToString("o")
}
Write-JsonFile -Path (Join-Path $OutputRoot "VALIDATION_REPORT.json") -Object $validation -Depth 20

if ($missing.Count -gt 0) {
    throw "Validation failed. Missing: $($missing -join ', ')"
}

$generalRoot = Join-Path $OutputRoot "GENERAL_TASK"
$localRoot = Join-Path $OutputRoot "LOCAL_TASKS"
Ensure-Directory -Path $generalRoot
Ensure-Directory -Path $localRoot

Copy-Item -LiteralPath $InputPath -Destination (Join-Path $generalRoot "SOURCE_TEXT.txt") -Force

$generalTask = [ordered]@{
    schema_version = "ASTRONOMICON_GENERAL_TASK_RECORD_V0_2"
    general_task_id = $generalTaskId
    title = $title
    code = $code
    author = $author
    execution_intent = $executionIntent
    priority = $priority
    source_path = $InputPath
    source_sha256 = $sourceSha256
    parser_version = "astronomicon_parse_general_task_v0_2.ps1"
    parser_task_id_source = "GENERAL_TASK_ID_FIELD"
    status = "REGISTERED"
    goal = $goal
    context = $context
    current_problem = $currentProblem
    expected_final_state = $expectedFinalState
    hard_constraints = $hardConstraints
    do_not_do = $doNotDo
    known_risks = $knownRisks
    required_organs = $requiredOrgans
    required_inputs = $requiredInputs
    expected_artifacts = $expectedArtifacts
    owner_notes = $ownerNotes
    created_at = (Get-Date).ToString("o")
}

$generalJson = $generalTask | ConvertTo-Json -Depth 30
Write-Utf8Bom -Path (Join-Path $generalRoot "GENERAL_TASK.json") -Content $generalJson

$generalMd = @(
    "# General Task"
    ""
    "GENERAL_TASK_ID:"
    $generalTaskId
    ""
    "TITLE:"
    $title
    ""
    "STATUS:"
    "REGISTERED"
    ""
    "SOURCE_SHA256:"
    $sourceSha256
    ""
    "GOAL:"
    $goal
    ""
    "EXPECTED_FINAL_STATE:"
    $expectedFinalState
) -join "`n"
Write-Utf8Bom -Path (Join-Path $generalRoot "GENERAL_TASK.md") -Content $generalMd

$generalHashRecord = [ordered]@{
    general_task_id = $generalTaskId
    source_sha256 = $sourceSha256
    record_sha256 = Get-Sha256String -Text $generalJson
    hash_policy = "sha256 over UTF-8 JSON record"
}
Write-JsonFile -Path (Join-Path $generalRoot "HASH.json") -Object $generalHashRecord -Depth 10

$registryItems = @()
$index = 1

foreach ($match in $matches) {
    $localTaskId = "LTASK-{0:D3}" -f $index
    $localTaskRoot = Join-Path $localRoot $localTaskId
    Ensure-Directory -Path $localTaskRoot

    $itemId = $match.Groups["item_id"].Value.Trim()
    $itemTitle = $match.Groups["title"].Value.Trim()
    $itemText = $match.Groups["text"].Value.Trim()
    $expectedOutput = $match.Groups["expected_output"].Value.Trim()
    $requiredOrgansText = $match.Groups["required_organs"].Value.Trim()
    $executionMode = $match.Groups["execution_mode"].Value.Trim()
    $dependsOnText = $match.Groups["depends_on"].Value.Trim()

    $requiredOrgansList = @($requiredOrgansText -split "," | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" })
    $dependsOnList = @()
    if ($dependsOnText -and $dependsOnText.ToLowerInvariant() -ne "none") {
        $dependsOnList = @($dependsOnText -split "," | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" })
    }

    $localTask = [ordered]@{
        schema_version = "ASTRONOMICON_LOCAL_TASK_RECORD_V0_2"
        local_task_id = $localTaskId
        source_plan_item_id = $itemId
        parent_general_task_id = $generalTaskId
        title = $itemTitle
        scope_text = $itemText
        expected_output = $expectedOutput
        required_organs = $requiredOrgansList
        execution_mode = $executionMode
        depends_on_plan_items = $dependsOnList
        status = "CREATED_FROM_GENERAL_TASK"
        speculum_review_status = "NOT_REQUESTED"
        stage_decomposition_status = "NOT_STARTED"
        created_at = (Get-Date).ToString("o")
    }

    $localJson = $localTask | ConvertTo-Json -Depth 30
    $localHash = Get-Sha256String -Text $localJson
    Write-Utf8Bom -Path (Join-Path $localTaskRoot "LOCAL_TASK.json") -Content $localJson

    $localMd = @(
        "# Local Task"
        ""
        "LOCAL_TASK_ID: $localTaskId"
        "PARENT_GENERAL_TASK_ID: $generalTaskId"
        "SOURCE_PLAN_ITEM_ID: $itemId"
        ""
        "TITLE:"
        $itemTitle
        ""
        "SCOPE:"
        $itemText
        ""
        "EXPECTED_OUTPUT:"
        $expectedOutput
        ""
        "REQUIRED_ORGANS:"
        ($requiredOrgansList -join ", ")
        ""
        "EXECUTION_MODE:"
        $executionMode
        ""
        "STATUS:"
        "CREATED_FROM_GENERAL_TASK"
        ""
        "HASH:"
        $localHash
    ) -join "`n"
    Write-Utf8Bom -Path (Join-Path $localTaskRoot "LOCAL_TASK.md") -Content $localMd

    $hashRecord = [ordered]@{
        local_task_id = $localTaskId
        parent_general_task_id = $generalTaskId
        record_sha256 = $localHash
        hash_policy = "sha256 over UTF-8 JSON record"
    }
    Write-JsonFile -Path (Join-Path $localTaskRoot "HASH.json") -Object $hashRecord -Depth 10

    $statusRecord = [ordered]@{
        local_task_id = $localTaskId
        status = "CREATED_FROM_GENERAL_TASK"
        speculum_review_status = "NOT_REQUESTED"
        stage_decomposition_status = "NOT_STARTED"
        ready_for_servitor_routing = $true
        updated_at = (Get-Date).ToString("o")
    }
    Write-JsonFile -Path (Join-Path $localTaskRoot "STATUS.json") -Object $statusRecord -Depth 10

    $registryItems += [ordered]@{
        local_task_id = $localTaskId
        source_plan_item_id = $itemId
        title = $itemTitle
        execution_mode = $executionMode
        required_organs = $requiredOrgansList
        expected_output = $expectedOutput
        hash = $localHash
        path = "LOCAL_TASKS/$localTaskId"
    }

    $index++
}

$registry = [ordered]@{
    schema_version = "ASTRONOMICON_LOCAL_TASK_REGISTRY_V0_2"
    general_task_id = $generalTaskId
    source_sha256 = $sourceSha256
    local_task_count = $registryItems.Count
    local_tasks = $registryItems
    generated_at = (Get-Date).ToString("o")
}
Write-JsonFile -Path (Join-Path $OutputRoot "LOCAL_TASK_REGISTRY.json") -Object $registry -Depth 20

$routeLines = @(
    "# Servitor Route Test"
    ""
    "Purpose:"
    "Verify that a Servitor can route to a Local Task by ID."
    ""
    "General Task:"
    $generalTaskId
    ""
    "Example route:"
    "1. Servitor receives LOCAL_TASK_ID: LTASK-001"
    "2. Servitor opens LOCAL_TASKS/LTASK-001/LOCAL_TASK.json"
    "3. Servitor reads parent_general_task_id, scope_text, expected_output, required_organs, execution_mode."
    "4. Servitor moves to required organs with evidence-first discipline."
    ""
    "Available Local Tasks:"
)
foreach ($item in $registryItems) {
    $routeLines += "- $($item.local_task_id): $($item.title)"
}
Write-Utf8Bom -Path (Join-Path $OutputRoot "SERVITOR_ROUTE_TEST.md") -Content ($routeLines -join "`n")

$receipt = [ordered]@{
    schema_version = "ASTRONOMICON_GENERAL_TO_LOCAL_PARSE_RECEIPT_V0_2"
    general_task_id = $generalTaskId
    input_path = $InputPath
    output_root = $OutputRoot
    source_sha256 = $sourceSha256
    local_task_count = $registryItems.Count
    validation_passed = $true
    status = "PASS"
    generated_at = (Get-Date).ToString("o")
}
Write-JsonFile -Path (Join-Path $OutputRoot "PARSE_RECEIPT.json") -Object $receipt -Depth 20

Write-Host "Astronomicon parse complete."
Write-Host "GENERAL_TASK_ID: $generalTaskId"
Write-Host "LOCAL_TASKS: $($registryItems.Count)"
Write-Host "OUTPUT_ROOT: $OutputRoot"
