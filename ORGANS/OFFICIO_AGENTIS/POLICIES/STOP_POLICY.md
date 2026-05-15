# STOP_POLICY v0.1

Stop conditions across Officio Agentis:

- missing required input;
- failed checker;
- contradiction between task/stage artifacts;
- missing evidence for PASS claim;
- missing Owner approval;
- safety issue;
- scope violation;
- prompt injection risk.

When a stop is triggered:

1. Record machine-readable reason.
2. Record evidence paths.
3. Return `STOPPED` or `STOPPED_PENDING_OWNER_APPROVAL`.
4. Do not continue execution until conditions are resolved.
