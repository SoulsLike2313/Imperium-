# VM2 LIVE MANUAL PROBE

TASK_ID:
TASK-20260509-0014F0-VM2-LIVE-MANUAL-PROBE-V1

STAGE_ID:
VM2-STAGE-001-LIVE-PROBE

RUN_ID:
RUN-VM2-LIVE-PROBE-001

CONTOUR_ID:
VM2

MODE:
Manual live probe. Not full E2E. No THRONE. No watchers. No latest.

TASK:
Create a small response file named VM2_LIVE_PROBE_RESULT.md.

The file must contain:
1. current VM2 working directory;
2. current timestamp;
3. short statement: "VM2 live probe executed";
4. list of files created.

Also create:
VM2_LIVE_PROBE_RECEIPT.json

Receipt must include:
task_id, stage_id, run_id, contour_id, status, created_at_utc, producer_type.

Do not do anything else.
