# Contract: stage_map

- schema_id: stage_map
- owner: Astronomicon
- purpose: canonical stage dependency map
- produced_by: Astronomicon
- consumed_by: Administratum,Doctrinarium,Officio
- must_exist_before_execution: true
- can_be_stub_in_v1: false

## Required Fields
- schema_version
- task_id
- stages
- depends_on
- pass_criteria
- stop_criteria

## Validation Expectation
- json_parse_and_required_fields_non_empty

## Fake Green Risks
- pass_without_evidence
- stale_green
- hidden_blockers

## Defer Notes
- pre-launch mandatory
