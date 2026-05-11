# v0.7 Root Cause Report

Root cause category: bad parameter contract.

## Root Cause
- `Write-Utf8Bom` in `TOOLS/astronomicon_pipeline_common_v0_2.ps1` rejects empty strings for `Content`.
- `TOOLS/astronomicon_synthetic_full_run_v0_1.ps1` initializes log files with `Write-Utf8Bom -Content ""`.
- Startup fails immediately with `ParameterArgumentValidationErrorEmptyStringNotAllowed,Write-Utf8Bom` before any task executes.

## Minimal Safe Fix
- Widen helper contract to allow empty string (`[AllowEmptyString()]`) and normalize `$null` to empty string.
- Keep all existing file path and run flow behavior unchanged.

## Risk Assessment
- Risk: low, localized to helper input validation behavior.
- No broad migration or folder moves required.
- Owner approval: not required (safe localized bugfix).
