# Contract: organ_self_report

- schema_id: organ_self_report
- owner: Doctrinarium
- purpose: freshness and organ health evaluation input
- produced_by: Doctrinarium
- consumed_by: Doctrinarium,Administratum,Sanctum
- must_exist_before_execution: true
- can_be_stub_in_v1: false

## Required Fields
- schema_version
- organ_id
- generated_at_utc
- checker_last_run_utc
- status
- evidence_paths

## Validation Expectation
- json_parse_and_required_fields_non_empty

## Fake Green Risks
- pass_without_evidence
- stale_green
- hidden_blockers

## Defer Notes
- already available in MVP base
