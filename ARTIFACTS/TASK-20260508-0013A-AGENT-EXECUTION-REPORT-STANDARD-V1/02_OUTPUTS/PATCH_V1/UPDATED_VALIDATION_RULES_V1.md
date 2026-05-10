# UPDATED_VALIDATION_RULES_V1

## Identity and provenance
- TASK_ID, STAGE_ID, RUN_ID, CONTOUR_ID are mandatory where applicable.
- producer_type and producer_id are mandatory for accepted artifacts.
- UNKNOWN origin is forbidden for accepted artifacts.

## Integrity
- Manifest is mandatory.
- SHA256 records are mandatory.
- Receipt is mandatory.
- Hash mismatch is immediate FAIL.

## Owner-facing response validation
- Every accepted final agent response must follow `AGENT_EXECUTION_REPORT_STANDARD_V1.md`.
- Missing any required section (`ШАГ`, `БАНДЛ`, `ВЕРДИКТ`, `КОММЕНТАРИЙ ДЛЯ OWNER`) is a validation failure.
- Agent reports must be concise and Owner-readable by default.

## SHA256SUMS machine-check rule
- `SHA256SUMS.txt` must be machine-checkable without warnings.
- Do not include a self-hash line that breaks verification workflows.
- If bundle-level self-hash is needed, place it in `BUNDLE_SHA256.txt` or `MANIFEST.json`, not in `SHA256SUMS.txt` in a warning-producing form.

## Policy
- No latest-bundle logic.
- No THRONE transfer.
- No auto-sync.
- No fake PASS based on file existence only.
