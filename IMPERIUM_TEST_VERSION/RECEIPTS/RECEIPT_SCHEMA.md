# RECEIPT SCHEMA

## Purpose
Receipts document every action taken in IMPERIUM for audit trail.

## Receipt Structure

```json
{
  "receipt_id": "RCP-YYYYMMDD-HHMMSS-XXXX",
  "schema_version": "IMPERIUM_RECEIPT_V0_1",
  "timestamp": "ISO 8601",
  "action": {
    "type": "command|script|button|manual",
    "name": "action name",
    "description": "what was done"
  },
  "actor": {
    "type": "agent|owner|system",
    "id": "KIRO|CODEX|OWNER|SYSTEM"
  },
  "inputs": {
    "files_read": ["list of files"],
    "parameters": {}
  },
  "outputs": {
    "files_created": ["list of files"],
    "files_modified": ["list of files"],
    "reports": ["list of reports"]
  },
  "context": {
    "git_head": "commit hash",
    "git_clean": true,
    "task_id": "optional task reference"
  },
  "result": {
    "status": "SUCCESS|FAILURE|PARTIAL",
    "exit_code": 0,
    "error": null,
    "duration_seconds": 1.5
  },
  "evidence": {
    "paths": ["list of evidence files"],
    "hashes": {}
  }
}
```

## Receipt Types

| Type | When Created | Actor |
|------|--------------|-------|
| COMMAND | Command executed via gateway | SYSTEM |
| SCRIPT | Script run | AGENT/OWNER |
| BUTTON | Dashboard button clicked | OWNER |
| AUDIT | Audit completed | INQUISITION |
| SMOKE | Smoke test run | TESTING_FIELD |
| PROMOTION | Candidate promoted | OWNER |

## Storage

Receipts stored in:
- `RECEIPTS/` — general receipts
- `ORGANS/*/RECEIPTS/` — organ-specific receipts
- `TESTING_FIELD/RECEIPTS/` — testing receipts

## Retention

- Keep all receipts for audit trail
- Archive old receipts monthly
- Never delete without Owner approval
