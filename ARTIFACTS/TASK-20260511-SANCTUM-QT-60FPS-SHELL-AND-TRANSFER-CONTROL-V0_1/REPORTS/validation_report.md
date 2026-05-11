# Validation Report — Sanctum Qt v0.29

Validated at: 2026-05-11T20:07:58+03:00

## Git start state

Branch: master
Commit count: 25
Short HEAD: d12c6ed
Full HEAD: d12c6ed3c71151350dc26786b7db75a0d3bf47c3

## Validation

- PySide6 Qt Sanctum file compiles: PASS
- Tkinter v0.28 file compiles: PASS
- Runtime transfer receipts stay under .imperium_runtime: PASS
- INBOX/OUTBOX are local transfer folders and ignored: PASS
- v0.29 launches as direct dashboard shell: manually confirmed
- Transfer panel works: manually confirmed
- VM2 bundle listing/fetch route works: manually confirmed
- Top buttons are wired pragmatically: PASS

## Current state

Sanctum v0.29 Qt is now the active candidate dashboard shell.

Sanctum v0.28 remains as a Tkinter transfer-control experiment and fallback reference.

Sanctum v0.26 remains the old working visual reference.

## Known limitations

- v0.29 visual style is acceptable prototype quality, not final AAA.
- Some top buttons currently open folders rather than dedicated utilities.
- Full registry integration for route locks is not complete yet.
- Transfer receipts are runtime-local and not committed.
- Qt FPS can vary depending on panel width and scene complexity.

## File hashes

sanctum_v0_29_qt.py:
23342F9BE9C07BF620DF38C517C22B1731564B23D6A4C1FCF87C18BA94DC3097

RUN_SANCTUM_V0_29_QT.ps1:
BE76DDE09B7D2F3852EE380015A3606817765C61E3D303AF3F98098B097C057F
