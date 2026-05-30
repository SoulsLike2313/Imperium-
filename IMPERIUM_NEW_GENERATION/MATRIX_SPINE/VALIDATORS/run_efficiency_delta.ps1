$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..\..\..")).Path
$outputDir = Join-Path $repoRoot "IMPERIUM_NEW_GENERATION/ORGANS/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-MATRIX-SPINE-STATUS-NORMALIZATION-AND-RUNTIME-CORRIDOR-PROOF-VM3-V0_1"

python3 (Join-Path $scriptDir "score_efficiency_delta.py") `
  --repo-root $repoRoot `
  --output-dir $outputDir `
  @args
