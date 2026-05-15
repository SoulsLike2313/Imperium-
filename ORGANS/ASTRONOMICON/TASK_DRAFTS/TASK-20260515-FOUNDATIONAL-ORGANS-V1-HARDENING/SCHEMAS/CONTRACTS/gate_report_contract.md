# Contract: gate_report

- schema_id: gate_report
- owner: Doctrinarium
- purpose: standard gate PASS/STOP output
- produced_by: Doctrinarium
- consumed_by: Astronomicon,Administratum,Sanctum
- must_exist_before_execution: true
- can_be_stub_in_v1: false

## Required Fields
- schema_version
- gate_id
- verdict
- blockers
- warnings
- evidence_paths
- checked_at_utc

## Validation Expectation
- json_parse_and_required_fields_non_empty

## Fake Green Risks
- pass_without_evidence
- stale_green
- hidden_blockers

## Defer Notes
- required for gate index execution
