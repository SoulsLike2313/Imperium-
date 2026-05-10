# LEGACY SCAN REPORT

Duplicate or legacy candidates observed:
- send_prompt_to_vm2.py: exists both at root legacy path and normalized active pipeline path.
- fetch_vm2_stage_bundle.py: exists both at root legacy path and normalized active pipeline path.
- VM3 legacy send/fetch scripts remain for historical reference and are blocked for new protocol.

Actions in this task:
- No delete performed.
- Active tools copied/normalized into class folders.
- Legacy paths registered as LEGACY_CANDIDATE in TOOLS_MASTER_INDEX.

Recommended future cleanup:
- Owner-approved move-only quarantine of legacy top-level scripts into 90_LEGACY_QUARANTINE.
