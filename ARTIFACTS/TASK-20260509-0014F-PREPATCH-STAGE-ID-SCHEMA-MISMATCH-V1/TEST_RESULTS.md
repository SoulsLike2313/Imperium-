# TEST RESULTS

task_id: TASK-20260509-0014F-PREPATCH-STAGE-ID-SCHEMA-MISMATCH-V1
run_id: RUN-20260509-0014
tests_run_count: 12
tests_passed_count: 12
tests_failed_count: 0

## Required Matrix
- PC-STAGE-001 must pass: PASS
- VM2-STAGE-001 must pass: PASS
- PC-STAGE-999 must pass if number format is valid: PASS
- STAGE-PC-001 must fail for new artifact creation: PASS
- STAGE-VM2-001 must fail for new artifact creation: PASS
- PC_STAGE_001 must fail: PASS
- PC-STAGE-1 must fail: PASS
- empty stage_id must fail: PASS
- unknown contour DOG-STAGE-001 must fail: PASS

## Executed Commands
- python -m unittest SSH_COMMAND_LIBRARY/06_TOOLS/tests/test_stage_id_schema.py -v
- python SSH_COMMAND_LIBRARY/06_TOOLS/10_PC_VM2_PIPELINE/send_prompt_to_vm2.py ... --stage-id VM2-STAGE-001 --dry-run
- python SSH_COMMAND_LIBRARY/06_TOOLS/10_PC_VM2_PIPELINE/send_prompt_to_vm2.py ... --stage-id STAGE-VM2-001 --dry-run
