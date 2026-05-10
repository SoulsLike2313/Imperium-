# ADMINISTRATUM SCRIPT ROUTING RULES V1

Rules:
- every stage must declare required tool_id list
- tool_id must exist in registry and be not UNKNOWN_UNACCEPTED
- stage start requires gate decision GATE_READY
- each stage transition requires receipt + ledger + provenance
- final acceptance requires barrier result
