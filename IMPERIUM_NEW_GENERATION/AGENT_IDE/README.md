# IMPERIUM Agent IDE V0.1 (Read-only)

Task: `TASK-NEWGEN-READONLY-AGENT-IDE-V0_1-PC`

This module provides a local desktop workbench for Owner visibility across IMPERIUM File Atlas data.

## V0.1 goals

- Local desktop app (`tkinter`, Python stdlib only).
- Read-only visibility of five organs and file passports.
- Role/rule/language gate surfaces.
- Tools/checkers/TUI/report/receipt surfaces.
- Route surfaces including `imperium-vm3` alias visibility when present.
- Owner pain map and gaps/successes.
- Unknown file kind warning/count.
- Plugin-ready provider descriptors (no untrusted dynamic code execution).

## Hard exclusions

- No WARP implementation.
- No CLI worker.
- No file editing.
- No command execution.
- No commit/push actions.
- No Officio hardening implementation.
- No Inquisition V0.2 hardening implementation.

## Launch

PowerShell:

```powershell
cd E:\IMPERIUM
.\IMPERIUM_NEW_GENERATION\AGENT_IDE\TUI_OR_LAUNCHERS\LAUNCH_AGENT_IDE_V0_1.ps1
```

CMD:

```cmd
cd /d E:\IMPERIUM
IMPERIUM_NEW_GENERATION\AGENT_IDE\TUI_OR_LAUNCHERS\LAUNCH_AGENT_IDE_V0_1.cmd
```

Direct Python:

```powershell
python IMPERIUM_NEW_GENERATION\AGENT_IDE\APP\agent_ide_app_v0_1.py
```

Smoke mode:

```powershell
python IMPERIUM_NEW_GENERATION\AGENT_IDE\APP\agent_ide_app_v0_1.py --smoke
```

## Input sources

The app reads Administratum File Atlas:

- `IMPERIUM_NEW_GENERATION/ADMINISTRATUM/FILE_ATLAS/file_passports_v0_1.jsonl`
- `file_atlas_index_v0_1.json`
- `organ_file_map_v0_1.json`
- `role_rule_surface_index_v0_1.json`
- `language_gate_surface_index_v0_1.json`
- `tui_surface_index_v0_1.json`
- `checker_tool_index_v0_1.json`
- `report_receipt_index_v0_1.json`
- `route_connection_surface_index_v0_1.json`
- `owner_pain_to_file_map_v0_1.json`
- `gap_success_index_v0_1.json`

Missing files are shown as warnings and do not crash the app.
