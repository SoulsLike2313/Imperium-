# Contract: task_start_gate_verdict

- schema_id: task_start_gate_verdict
- owner: Doctrinarium
- purpose: allow/block execution admission
- produced_by: Doctrinarium
- consumed_by: Administratum,Sanctum
- must_exist_before_execution: true
- can_be_stub_in_v1: false

## Required Fields
- schema_version
- task_id
- verdict
- allow_execution
- reasons
- evidence_paths

## Validation Expectation
- json_parse_and_required_fields_non_empty

## Fake Green Risks
- pass_without_evidence
- stale_green
- hidden_blockers

## Defer Notes
- mandatory corridor gate
