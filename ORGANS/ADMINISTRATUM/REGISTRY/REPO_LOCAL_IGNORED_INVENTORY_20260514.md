# Repo Local Ignored Inventory (2026-05-14)

| path | exists? | git status class | ignored rule | category | recommended action | moved? | notes |
|---|---|---|---|---|---|---|---|
| `E:\IMPERIUM\OUTBOX` | NO | ignored (historical in this stage) | `.gitignore: /OUTBOX/` | LOCAL_TRANSPORT_BUNDLE | use `E:\IMPERIUM_CONTEXT\LOCAL\OUTBOX` only | YES | source folder is absent in repo; operational bundles now external-local |
| `E:\IMPERIUM\.imperium_runtime` | NO | ignored (historical in this stage) | `.gitignore: /.imperium_runtime/` | LOCAL_RUNTIME | use `E:\IMPERIUM_CONTEXT\LOCAL\RUNTIME` only | YES | source folder is absent in repo; runtime payload is external-local |
| `E:\IMPERIUM\scripts\__pycache__` | YES | ignored | Python cache ignore | LOCAL_TEMP_ARTIFACT | keep ignored, do not treat as canonical source | NO | non-canonical cache output |
| `E:\IMPERIUM\src\imperium\__pycache__` | YES | ignored | Python cache ignore | LOCAL_TEMP_ARTIFACT | keep ignored, do not treat as canonical source | NO | non-canonical cache output |
| `E:\IMPERIUM\src\imperium\receipts\__pycache__` | YES | ignored | Python cache ignore | LOCAL_TEMP_ARTIFACT | keep ignored, do not treat as canonical source | NO | non-canonical cache output |
| `E:\IMPERIUM\src\imperium\security\__pycache__` | YES | ignored | Python cache ignore | LOCAL_TEMP_ARTIFACT | keep ignored, do not treat as canonical source | NO | non-canonical cache output |
| `E:\IMPERIUM\ARTIFACTS` | YES | tracked | n/a | TRACKED_CANONICAL | keep in repo until owner-approved historical policy changes | n/a | legacy tracked area; not moved in this stage |

## Classification notes

- No tracked dirty files were present at startup.
- Local operational payload should be written under `E:\IMPERIUM_CONTEXT\LOCAL`.
- Sensitive payload should be written under `E:\IMPERIUM_CONTEXT\PRIVATE`.
