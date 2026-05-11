# v0.7 Repair Report

## Files Changed
- TOOLS/astronomicon_pipeline_common_v0_2.ps1

## Why Changed
- Shared helper `Write-Utf8Bom` rejected empty string content.
- Synthetic runner initializes log files with empty content; this caused startup termination.

## Before Behavior
- `Write-Utf8Bom -Content ""` threw `ParameterArgumentValidationErrorEmptyStringNotAllowed`.
- Synthetic startup failed before processing any task.

## After Expected Behavior
- Empty string content is accepted intentionally for blank file initialization.
- Null content is normalized to empty string before newline normalization.
- Existing non-empty writes continue unchanged.

## Remaining Risk
- Low. The helper contract was widened; downstream scripts relying on startup failure for empty content are unlikely but should be monitored.
