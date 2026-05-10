# 0014E_NEGATIVE_TEST_REPORT

Negative tests and expected behavior:
- missing_run_id: rc=1 expected=nonzero => PASS
- ack_without_signal: rc=2 expected=nonzero => PASS
- completion_signal_without_receipt: rc=1 expected=nonzero => PASS
- manifest_write_v2: rc=0 expected=zero (setup step) => PASS
- manifest_conflict_compare: rc=2 expected=nonzero => PASS
- ledger_replay_broken: rc=1 expected=nonzero => PASS
- wait_timeout: rc=1 expected=nonzero => PASS
- latest_pattern: rc=1 expected=nonzero => PASS
- stage_started_without_gate: rc=0 expected=zero (setup step) => PASS
- accepted_artifact_without_provenance: rc=0 expected=zero (setup step) => PASS
- fatal_repair_request: rc=2 expected=nonzero => PASS
- inquisition_audit: rc=1 expected=nonzero => PASS

Summary: 12/12 negative-path checks matched expected outcomes.

Interpretation rule:
`REPAIR_REQUIRED` and related findings from the negative fixture set are expected detection outputs.
They validate audit sensitivity and must not be reported as positive-path runtime regression.
