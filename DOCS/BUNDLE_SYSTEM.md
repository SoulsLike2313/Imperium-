# BUNDLE_SYSTEM

## Model
- Git = public engineering memory.
- Local PC = private operational memory.
- Bundle = frozen context/evidence capsule.

## Analyzer-Driven Policy
Do not guess bundle content manually.
- Run analyzer v0.2.
- Use `recommended_compilation` + `owner_action` + worktree classifier.
- Include analyzer reports inside bundle.

## Decision Split
- Git-only when analyzer says `READ_GIT_ONLY`.
- Build safe bundle when analyzer says `RUN_CHAT_COMPILATION_SAFE`.
- Require explicit human review when analyzer says `MANUAL_REVIEW_REQUIRED`.

## Local-Only Rule
`CHAT_COMPILATIONS_LOCAL` bundles remain local and are ignored by Git.

## Secret Safety
Default builder mode excludes raw secret-bearing content.
Private raw context requires explicit Owner approval and allowlist handling.
