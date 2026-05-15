# Contract: dashboard_actions

- schema_id: dashboard_actions
- owner: Sanctum+Administratum
- purpose: action button contract
- produced_by: Sanctum+Administratum
- consumed_by: Owner display,Administratum
- must_exist_before_execution: false
- can_be_stub_in_v1: true

## Required Fields
- action_id
- allowed_roles
- confirmation_required
- disabled_reason
- enabled
- expected_receipt_path
- expected_report_path
- failure_condition
- label_key
- receipt_schema
- requires_confirmation
- schema_version
- success_condition
- target_script_or_action
- timeout_seconds

## Validation Expectation
- json_parse_and_required_fields_non_empty

## Fake Green Risks
- pass_without_evidence
- stale_green
- hidden_blockers

## Defer Notes
- no action without receipt
