# V1 Repo Purity Contract

## Purity baseline
- Repository stores canonical tracked project artifacts.
- Local/private/runtime/generated payloads are excluded unless explicitly canonicalized.

## Bundle and continuity destinations
- Final bundle and continuity packs require controlled destination paths.
- Archive/index updates are mandatory when moving artifacts.

## Hardening execution constraints
- No broad cleanup during hardening execution.
- No mass deletion without explicit owner approval.
- No unrelated path edits outside stage scope.

## Future checker expectations
- Repo purity report must list allowed paths and violations.
- Diff scope validation is mandatory per local task and final bundle.
