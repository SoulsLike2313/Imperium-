# v0.7 Defect Source Index Report

Task: TASK-20260511-ASTRONOMICON-V0_7-SYNTHETIC-STARTUP-REPAIR-AND-FIRST-RUNTIME-E2E-V0_1
Defect: DEFECT-20260511-ASTRONOMICON-V0_7-SYNTHETIC-STARTUP-FAIL

## Where Defect Is Recorded
- REGISTRY/KNOWN_DEFECTS.json: defect is registered as OPEN.
- ARTIFACTS/.../05_DEFECTS/DEFECTS_FOUND.json: explicit defect DEF-001 with startup error.
- ARTIFACTS/.../04_V0_7_SYNTHETIC_STRESS_RUN/SYNTHETIC_RUN_FAILURE_LOG.txt: raw error trace.
- ARTIFACTS/.../04_V0_7_SYNTHETIC_STRESS_RUN/SYNTHETIC_SUMMARY_FAIL.json: run failed at startup.

## Exact Failing Script/Command Context
- Primary failing script: TOOLS/astronomicon_synthetic_full_run_v0_1.ps1.
- Known failing line: startup call to Write-Utf8Bom with empty Content string.
- Prior failure signature: ParameterArgumentValidationErrorEmptyStringNotAllowed,Write-Utf8Bom.

## Expected vs Actual
- Expected: synthetic run completes 3 tasks and emits summary/report artifacts.
- Actual (historical evidence): run stops at startup before processing any task.

## Involved Files
- TOOLS/astronomicon_synthetic_full_run_v0_1.ps1
- TOOLS/astronomicon_pipeline_common_v0_2.ps1
- prior stress artifact files listed above

## Reproducibility From Current HEAD
- Status: pending explicit reproduction in Phase 2.
- Preliminary read indicates current HEAD still has the failing startup pattern.

## Blocking Assessment
- This defect blocks trustworthy runtime E2E because the synthetic startup path is a required confidence gate for Astronomicon v0.7 behavior.
