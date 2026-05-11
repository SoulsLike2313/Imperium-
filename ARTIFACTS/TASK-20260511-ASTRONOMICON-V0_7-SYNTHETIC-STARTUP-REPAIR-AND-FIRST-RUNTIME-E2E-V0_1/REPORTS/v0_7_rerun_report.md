# v0.7 Rerun Report

Command: powershell.exe -ExecutionPolicy Bypass -File TOOLS/astronomicon_synthetic_full_run_v0_1.ps1 -GeneralTasksRoot "ARTIFACTS/TASK-20260511-ASTRONOMICON-V0_7-SYNTHETIC-STARTUP-REPAIR-AND-FIRST-RUNTIME-E2E-V0_1/RUNTIME/rerun_after_fix/GENERAL_TASKS" -OutputRoot "ARTIFACTS/TASK-20260511-ASTRONOMICON-V0_7-SYNTHETIC-STARTUP-REPAIR-AND-FIRST-RUNTIME-E2E-V0_1/RUNTIME/rerun_after_fix/SYNTH_OUTPUT" -TaskCount 3
Exit code: 0
Summary exists: True
Verdict: PASS

## Summary Metrics
- total synthetic General Tasks: 3
- total Local Tasks: 9
- total Stage Maps: 3
- total Stages: 9
- imports passed: 6
- orphans: 2
- blocked states: 2
- errors: 0

## Git Status Before
```text
 M TOOLS/astronomicon_pipeline_common_v0_2.ps1
?? ARTIFACTS/TASK-20260511-ASTRONOMICON-V0_7-SYNTHETIC-STARTUP-REPAIR-AND-FIRST-RUNTIME-E2E-V0_1/

```

## Git Status After
```text
 M TOOLS/astronomicon_pipeline_common_v0_2.ps1
?? ARTIFACTS/TASK-20260511-ASTRONOMICON-V0_7-SYNTHETIC-STARTUP-REPAIR-AND-FIRST-RUNTIME-E2E-V0_1/

```

## stderr
```text

```

## stdout
```text
[2026-05-11 17:21:35] [GTASK-SYNTH-20260511-001] General Task form created.
[2026-05-11 17:21:38] [GTASK-SYNTH-20260511-001] Synthetic full run completed.
[2026-05-11 17:21:38] [GTASK-SYNTH-20260511-002] General Task form created.
[2026-05-11 17:21:41] [GTASK-SYNTH-20260511-002] Synthetic full run completed.
[2026-05-11 17:21:41] [GTASK-SYNTH-20260511-003] General Task form created.
[2026-05-11 17:21:44] [GTASK-SYNTH-20260511-003] Synthetic full run completed.
Synthetic full run complete.
Summary: ARTIFACTS\TASK-20260511-ASTRONOMICON-V0_7-SYNTHETIC-STARTUP-REPAIR-AND-FIRST-RUNTIME-E2E-V0_1\RUNTIME\rerun_after_fix\SYNTH_OUTPUT\SYNTHETIC_SUMMARY.json

```

Generated runtime files: 177
Synthetic summary path: ARTIFACTS/TASK-20260511-ASTRONOMICON-V0_7-SYNTHETIC-STARTUP-REPAIR-AND-FIRST-RUNTIME-E2E-V0_1/RUNTIME/rerun_after_fix/SYNTH_OUTPUT/SYNTHETIC_SUMMARY.json
