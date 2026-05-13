# Local/Private Context Paths v0.2

Administratum path policy for repo parity and continuity routing.

## Context Roots
- Git context root (PC): `E:\IMPERIUM`
- Local operational context root (PC): `E:\IMPERIUM_LOCAL`
- Private Owner context root (PC): `E:\IMPERIUM_PRIVATE`
- Git context root (VM2): `/home/vboxuser2/IMPERIUM_WORK/Imperium-`
- VM2 external roots reserved for future:
  - `~/IMPERIUM_LOCAL`
  - `~/IMPERIUM_PRIVATE`

## Continuity and Handoff Rule
- Continuity Pack and full handoff collectors must explicitly read from these roots.
- Private context is included only by Owner decision.
- Private/local payloads must never be committed.

## Structural Rule
- `SCRIPTORIUM` and `ARSENAL` live under `ORGANS/MECHANICUS/` and remain Mechanicus-owned support layers.
