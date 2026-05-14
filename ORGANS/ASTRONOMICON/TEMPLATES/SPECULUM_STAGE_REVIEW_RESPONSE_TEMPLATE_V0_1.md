# SPECULUM STAGE REVIEW RESPONSE TEMPLATE V0.1

- schema_required: `speculum_stage_review_response.schema.json`
- response_status: DRAFT

## Mandatory Structured Fields

- stage_review_verdict:
- stage_atomicity:
- stage_sequence_risk:
- missing_preconditions:
- missing_checks:
- missing_receipts:
- forbidden_operations:
- owner_gates:
- fake_green_risk:
- continue_stop_rules:
- bundle_requirements:
- stage_metric_updates:
- final_recommendation:

## Optional Limited Free-Form

- advisory_notes:

## Rules

- Speculum may be any agent/channel (including Telegram bot), but output must match schema.
- Structured fields are mandatory.
- Free-form notes are supplementary only.
- Response must be imported and validated before state changes.
