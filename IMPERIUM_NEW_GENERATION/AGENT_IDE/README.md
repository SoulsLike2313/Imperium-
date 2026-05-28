# IMPERIUM Agent IDE

## V0.2 (Dual Surface, Read-only)

Task: `TASK-NEWGEN-AGENT-IDE-DUAL-SURFACE-SELF-VALIDATOR-BLOCK-FOUNDATION-PC-V0_1`

### What is included

- Desktop IDE (`tkinter`) remains read-only and launchable.
- Shared view model builder:
  - `VIEW_MODEL/ide_view_model_v0_2.json`
  - `VIEW_MODEL/dashboard_view_model_v0_1.json`
  - `VIEW_MODEL/block_view_model_v0_1.json`
- Web Projection dashboard on `127.0.0.1` reading the same shared model.
- Self-validator that writes source/view-model/desktop/web/parity receipts.
- Playwright capture runner (runs if available, otherwise returns warning).
- Block Foundation seed (`BLOCK_FOUNDATION/*`).
- Mechanicus tool registration entries for reusable tooling.

### Launch V0.2 desktop

```powershell
cd E:\IMPERIUM
.\IMPERIUM_NEW_GENERATION\AGENT_IDE\TUI_OR_LAUNCHERS\LAUNCH_AGENT_IDE_V0_2.ps1
```

### Launch web projection

```powershell
cd E:\IMPERIUM
.\IMPERIUM_NEW_GENERATION\AGENT_IDE\TUI_OR_LAUNCHERS\LAUNCH_AGENT_IDE_WEB_PROJECTION_V0_1.ps1
```

Then open: `http://127.0.0.1:4173/`

### Run self-validator

```powershell
cd E:\IMPERIUM
.\IMPERIUM_NEW_GENERATION\AGENT_IDE\TUI_OR_LAUNCHERS\RUN_AGENT_IDE_SELF_VALIDATOR_V0_1.ps1
```

## V0.1 (Legacy baseline kept usable)

Task: `TASK-NEWGEN-READONLY-AGENT-IDE-V0_1-PC`

- `APP/agent_ide_app_v0_1.py`
- `TUI_OR_LAUNCHERS/LAUNCH_AGENT_IDE_V0_1.ps1`
- `TUI_OR_LAUNCHERS/LAUNCH_AGENT_IDE_V0_1.cmd`

V0.1 remains available for compatibility, but V0.2 is the primary dual-surface foundation.
