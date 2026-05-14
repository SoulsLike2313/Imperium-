# Local/Private Context Paths v0.2

Administratum path policy for repo purity and continuity routing.

## Context Roots
- Git context root (PC): `E:\IMPERIUM`
- Local operational context root (PC): `E:\IMPERIUM_CONTEXT\LOCAL`
- Private Owner context root (PC): `E:\IMPERIUM_CONTEXT\PRIVATE`
- Git context root (VM2): `/home/vboxuser2/IMPERIUM_WORK/Imperium-`

## Legacy compatibility notes
- Legacy labels (`E:\IMPERIUM_LOCAL`, `E:\IMPERIUM_PRIVATE`) are compatibility references only.
- New operational writes must target `E:\IMPERIUM_CONTEXT\LOCAL` and `E:\IMPERIUM_CONTEXT\PRIVATE`.

## Continuity and Handoff Rule
- Continuity Pack and handoff collectors must read from registered roots.
- Private context is included only by Owner decision.
- Private/local payloads must never be committed.

## Structural Rule
- `SCRIPTORIUM` and `ARSENAL` live under `ORGANS/MECHANICUS/` and remain Mechanicus-owned support layers.
