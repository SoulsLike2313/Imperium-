# TASK AGENT MAP

Task ID:
TASK-20260508-0012-CONTINUITY-PACK-REDACTION-AND-PROTOCOL-REPAIR-V1

Purpose:
Create a clean, redacted, and accurate continuity handoff pack V2 without exposing local route values.
Repair continuity protocol documentation after Speculum review feedback.

Mode:
- PC Servitor only.
- Read-only continuity repair and redacted handoff generation.
- No SSH.
- No VM2/VM3 operations.
- No THRONE operations.
- No file move/delete.

Redaction policy:
- Do not copy local-only route configs.
- Do not copy raw host/user/port/private-key path values.
- Replace sensitive route examples with placeholders.
- Mark legacy VM3 latest-bundle materials as historical and blocked for new protocol.

Expected outputs:
- NEW_CHAT_HANDOFF_REDACTED_V2
- CONTINUITY_SUMMARY_V2 (md/json)
- SECURITY_REDACTION_REPORT and REDACTION_FINDINGS
- EXECUTOR_INDEX_V1 (csv/json)
- ARTIFACT_TASK_INDEX_V2 (csv/json)
- RECEIPT_SCHEMA_V1 (md/json)
- OPEN_BLOCKERS_V2
- PYTHON_COMMAND_EXAMPLES_V2
- LEGACY_VM3_ROUTE_POLICY
- SANITIZED_EVIDENCE summaries
- receipt, manifest, hashes, final bundle

PASS criteria:
- All required V2 redacted documents are created.
- No SSH used.
- VM2/VM3/THRONE untouched.
- No local-only configs copied.
- No raw route values included in handoff outputs.
- Final bundle created inside FINAL_STEP_BUNDLE.

BLOCKED/PARTIAL criteria:
- Missing required V2 files.
- Sensitive route values leaked.
- Any forbidden environment touched.

Scope note:
This task does not prove new execution.
This task only repairs continuity handoff quality and protocol documentation.
