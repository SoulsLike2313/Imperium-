$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..\..\..")).Path
$outputDir = Join-Path $repoRoot "IMPERIUM_NEW_GENERATION/ORGANS/MECHANICUS/REPORTS/TASK-NEWGEN-MATRIX-SPINE-CLOSURE-PROVENANCE-CORRIDOR-NAMING-AND-REVIEW-PIPELINE-HARDENING-VM3-V0_1"

python3 (Join-Path $scriptDir "run_synthetic_runtime_corridor.py") `
  --repo-root $repoRoot `
  --output-dir $outputDir `
  @args
