# SPECULUM TASK REVIEW RESPONSE TEMPLATE V0.1

- schema_required: `speculum_task_review_response.schema.json`
- response_status: DRAFT

## Mandatory Structured Fields

- review_verdict:
- stage_split_ready:
- hidden_failure_modes:
- missing_constraints:
- scope_corrections:
- forbidden_files_zones:
- required_checkers:
- required_receipts:
- owner_decision_points:
- metric_updates:
- reject_or_delay_reasons:
- minimal_viable_boundary:
- final_recommendation:

## Optional Limited Free-Form

- advisory_notes:

## Rules

- Speculum may be any agent/channel (including Telegram bot), but output must match schema.
- Structured fields are mandatory.
- Free-form text cannot replace required structured fields.
- Response must be imported and validated before task modernization.
