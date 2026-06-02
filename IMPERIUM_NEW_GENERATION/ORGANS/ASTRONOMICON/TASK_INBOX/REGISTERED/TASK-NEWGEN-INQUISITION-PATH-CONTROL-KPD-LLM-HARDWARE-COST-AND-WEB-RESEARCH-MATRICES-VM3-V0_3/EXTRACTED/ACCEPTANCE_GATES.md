# Acceptance Gates

## BLOCK gates

The task must BLOCK if:

- Astronomicon resolver cannot resolve this TASK_ID.
- Officio role read is skipped.
- The task claims cost reduction while deleting or weakening required evidence.
- Deep web research is skipped without a documented connectivity/tooling blocker.
- Required outputs are missing.
- Non-BLOCK result is not committed and pushed unless an explicit unsafe gate blocks closure.
- PC transfer is required but not attempted.
- PC transfer is claimed PASS without a transfer receipt.

## PASS_WITH_WARNINGS gates

The task may return PASS_WITH_WARNINGS if:

- some hardware metrics are not instrumented yet but are explicitly marked UNKNOWN_NOT_INSTRUMENTED;
- PC SSH transfer fails but a local output bundle exists and exact recovery/scp command is provided;
- web research source coverage is partial but the limitation is documented;
- validator remains seed-level but schemas/examples are present.

## Local PASS rules

A local step may be locally PASS when:

- all step-specific required outputs exist;
- matrix schemas/examples are present;
- fake-economy checks are present;
- cost/hardware/local-agent metrics are specified;
- web research dossier exists;
- PC transfer receipt exists or a precise transfer-block receipt exists;
- commit/push closure is complete.

Global caps such as IDE/WARP/Custodes may be carried separately and must not automatically block local step pass if they are outside this task scope.
