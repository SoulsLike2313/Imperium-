$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..\..\..")).Path
$outputDir = Join-Path $repoRoot "IMPERIUM_NEW_GENERATION/MATRIX_SPINE/REPORTS/TASK-NEWGEN-MECHANICUS-MATRIX-SPINE-VALIDATOR-SUITE-VM3-V0_1"

python3 (Join-Path $scriptDir "validate_matrix_spine.py") `
  --repo-root $repoRoot `
  --output-dir $outputDir `
  @args
