# Contract: work_packet

- schema_id: work_packet
- owner: Administratum
- purpose: execute bounded work slice
- produced_by: Administratum
- consumed_by: Servitor lane
- must_exist_before_execution: true
- can_be_stub_in_v1: false

## Required Fields
- schema_version
- task_id
- local_task_id
- stage_id
- inputs
- outputs
- constraints

## Validation Expectation
- json_parse_and_required_fields_non_empty

## Fake Green Risks
- pass_without_evidence
- stale_green
- hidden_blockers

## Defer Notes
- must map to ownership matrix
