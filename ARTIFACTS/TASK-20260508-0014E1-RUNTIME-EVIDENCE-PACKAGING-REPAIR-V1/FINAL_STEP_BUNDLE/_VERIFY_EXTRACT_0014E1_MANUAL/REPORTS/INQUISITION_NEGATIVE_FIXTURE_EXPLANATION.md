# INQUISITION_NEGATIVE_FIXTURE_EXPLANATION

Purpose:
This note separates expected negative-fixture detections from real runtime path failures.

Key point:
`REPAIR_REQUIRED` in local Inquisition evidence was triggered by intentionally injected negative fixtures.
These fixtures were designed to prove detection of protocol violations, conflicts, and missing evidence.

What this means:
- `REPAIR_REQUIRED` in this context is expected negative-test output.
- It is not a claim that the positive runtime path is broken.
- Positive-path and negative-path evidence must be interpreted separately.

Negative-fixture categories used:
- ack without signal;
- completion signal missing receipt/provenance;
- broken ledger chain;
- conflict identity/hash setups;
- timeout wait path;
- latest-pattern rejection checks.

Operator guidance for 0014F:
- Keep positive and negative sections separate in reports.
- Treat negative detections as pass criteria for detection behavior.
- Escalate only if positive-path evidence fails or if negative fixtures are missing expected detections.
