# REPO PURITY POLICY V0.1

## Principle
- `E:\IMPERIUM` should remain equivalent to canonical tracked tree (GitHub + future VM2 tracked worktree parity).
- Ignored/grey IDE/runtime/transport folders must not be used inside repo as normal working zones.

## Operational output placement
- Runtime/outbox/temp/logs/transport outputs must target `E:\IMPERIUM_CONTEXT\LOCAL`.
- Private sensitive payload must target `E:\IMPERIUM_CONTEXT\PRIVATE` with owner-controlled access.

## Future script rule
- Scripts producing local operational data must write to LOCAL roots.
- Scripts requiring private data must request Owner permission and use private registry references.
