# BUNDLE_SYSTEM

## Model
- Git = public engineering memory and safe source.
- Local PC = private operational memory.
- Bundle = frozen context/evidence capsule.

## Bundle Types
- `ARTIFACTS/*`: engineering evidence artifacts.
- `CHAT_COMPILATIONS_LOCAL/*`: local chat/task context bundles for Owner upload.

## Analyzer-Driven Rule
- Bundle content should be generated from analyzer output.
- Do not manually guess bundle contents.
- Analyzer reports must be included in the bundle.

## Safety
- `CHAT_COMPILATIONS_LOCAL` is local-only and ignored by Git.
- Default bundle excludes raw secret-bearing data.
- Private raw context requires explicit Owner approval and allowlist handling.
