# Contract: route_sheet

- schema_id: route_sheet
- owner: Administratum
- purpose: describe stage routing and transitions
- produced_by: Administratum
- consumed_by: Administratum,Sanctum
- must_exist_before_execution: true
- can_be_stub_in_v1: false

## Required Fields
- schema_version
- task_id
- route_steps
- current_step
- next_step

## Validation Expectation
- json_parse_and_required_fields_non_empty

## Fake Green Risks
- pass_without_evidence
- stale_green
- hidden_blockers

## Defer Notes
- corridor truth contract
