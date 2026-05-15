# Contract: role_contract

- schema_id: role_contract
- owner: Officio Agentis
- purpose: agent role/mode contract control
- produced_by: Officio Agentis
- consumed_by: Administratum,Sanctum
- must_exist_before_execution: true
- can_be_stub_in_v1: false

## Required Fields
- schema_version
- role_id
- modes
- constraints
- owner
- version

## Validation Expectation
- json_parse_and_required_fields_non_empty

## Fake Green Risks
- pass_without_evidence
- stale_green
- hidden_blockers

## Defer Notes
- contract compliance must be testable
