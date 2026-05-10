# READONLY EXPLORER

Script:
imperium_readonly_explorer.py

Purpose:
Read-only address and status explorer for tools registry entries.

Modes:
- summary
- details
- tool
- class
- map

Safety:
- no write/move/delete by default
- no network or VM2 contact
- optional --json-output writes only when explicitly requested

Usage:
- `python imperium_readonly_explorer.py --tools-index <TOOLS_MASTER_INDEX.json> --mode summary --readonly-assert`
- `python imperium_readonly_explorer.py --tools-index <TOOLS_MASTER_INDEX.json> --mode map --readonly-assert`
- `python imperium_readonly_explorer.py --tools-index <TOOLS_MASTER_INDEX.json> --mode summary --readonly-assert --verify-registry-hashes`
