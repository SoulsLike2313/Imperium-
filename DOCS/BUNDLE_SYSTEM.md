# BUNDLE_SYSTEM

## Model
- Git = public engineering memory and safe source.
- Local PC = private operational memory.
- Bundle = frozen evidence/task handoff capsule.

## Bundle Types
- `ARTIFACTS/*`: engineering evidence artifacts for tasks.
- `CHAT_COMPILATIONS_LOCAL/*`: local chat/task context capsules for Owner upload.

## Rules
- `CHAT_COMPILATIONS_LOCAL` bundles are not Git artifacts.
- Git remains public memory.
- Artifacts remain evidence.
- Chat compilation bundles are temporary context capsules.

## When Bundle Is Required
- Private/local context is needed for execution.
- A worker environment (future VM2) needs controlled transfer.
- Owner requests task-specific frozen evidence handoff.

## Never Publish
- Keys/tokens/passwords/credentials.
- Private command bodies.
- Raw local secret-bearing runtime data.
