# IMPERIUM Explorer Changelog

## v0_4 - Helix Depth Visual Upgrade

Source baseline:
- `imperium_explorer_v0_3.py` (liked baseline, preserved).

What changed from v0_3 to v0_4:
- Added new file `imperium_explorer_v0_4.py` based on v0_3 structure.
- Central helix panel now reflects selected node depth relative to `E:\IMPERIUM`.
- Added depth-driven active helix segment highlight with pulse/glow.
- Added stronger inward/deeper visual effect for deeper nodes.
- Central panel now shows selected node type and selected depth.
- Right details panel now starts with a compact block:
  - `NODE DEPTH`
  - `NODE TYPE`
  - `PARENT`
  - `DIRECT FOLDERS`
  - `DIRECT FILES`
  - markers:
    - manifest
    - sha256
    - owner summary
    - known blockers
    - direct receipts
- Animation tuned to lightweight non-blocking Tkinter Canvas redraw loop.

What was not changed:
- v0_3 file was not modified.
- No backend/services were added.
- No write operations to IMPERIUM data were added.
- No VM2/E2E/THRONE/watcher/automation logic was added.
- Left tree, right details, Copy Path, Open in Explorer behavior retained.

Known limitations:
- Marker scan is direct-children only (no deep recursive scan by design).
- Very large folders may still be visually dense in tree navigation.
- Helix depth mapping is a visual approximation, not a semantic workflow stage model.

Read-only guarantee:
- Explorer remains read-only:
  - no file edits/deletes/moves,
  - no VM2 contact,
  - no THRONE contact,
  - no background watchers/automation.

## V0.5

STATUS: ARCHIVE_CLASSIFICATION_TRUTH_PATCH

Changed:
- created imperium_explorer_v0_5.py from v0_4;
- added ARCHIVE_COLD_STORAGE node type;
- added archive cold-storage note in details panel;
- v0_4 preserved as previous visual candidate.

Launch:
python E:\IMPERIUM\EXPLORER\imperium_explorer_v0_5.py



## V0.6

STATUS: ARCHIVE_TRUTH_ALIGNMENT_REPAIR

Changed:
- created imperium_explorer_v0_6.py;
- forces ARCHIVE / _ARCHIVE / IMPERIUM_ARCHIVE to display as ARCHIVE_COLD_STORAGE;
- adds archive policy lines to details panel;
- keeps Explorer read-only.

Launch:
python E:\IMPERIUM\EXPLORER\imperium_explorer_v0_6.py

