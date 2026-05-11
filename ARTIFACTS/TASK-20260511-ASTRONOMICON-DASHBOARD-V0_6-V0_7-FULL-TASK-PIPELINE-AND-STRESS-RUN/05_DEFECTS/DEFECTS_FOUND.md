# DEFECTS_FOUND

## DEF-001 synthetic stress runner aborts before task generation
- severity: high
- discovered_at: 2026-05-11T12:20:xx+03:00
- component: `TOOLS/astronomicon_synthetic_full_run_v0_1.ps1`
- trigger: run synthetic full-run command with `-TaskCount 3`
- observed_result: execution stops at startup with parameter binding error.
- error_excerpt:
  - `Write-Utf8Bom : Cannot bind argument to parameter 'Content' because it is an empty string.`
  - location: line calling `Write-Utf8Bom -Path $logPath -Content ""`
- expected_result: script creates log file, generates 3 synthetic General Tasks, and outputs summary counters.
- status_after_discovery: NOT_FIXED (per stress-test rule)
- evidence:
  - `04_V0_7_SYNTHETIC_STRESS_RUN/SYNTHETIC_RUN_FAILURE_LOG.txt`