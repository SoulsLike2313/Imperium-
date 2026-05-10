# SANCTUM ACTION MAP CONTRACT V1

Sanctum actions must call tool_id from TOOLS_MASTER_INDEX.json.
Hardcoded script file paths are forbidden in button logic.

Each Sanctum action must emit:
- receipt
- ledger event
- Owner report
- provenance record when artifact is produced

Sanctum action routing must respect no-latest logic and no THRONE transfer constraints.
