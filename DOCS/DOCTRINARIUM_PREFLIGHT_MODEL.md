# Doctrinarium Preflight Model

Request operation:
preflight_task_execution

Response must include:
- status (ALLOW / ALLOW_WITH_LIMITATIONS / BLOCK)
- required_organs
- organ_health
- blocked
- limitations
- forbidden_actions
- required_receipts
- blockers
- receipt_path
