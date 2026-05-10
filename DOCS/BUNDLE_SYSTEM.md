# BUNDLE SYSTEM

- Git = public engineering memory/code.
- Local PC = private operational memory.
- Bundle = task-specific handoff/evidence capsule.

## When a Bundle Is Needed
- VM2/isolated worker needs private context unavailable in Git.
- Owner requests controlled transfer of local-only references.
- A task requires reproducible private evidence capsule.

## What a Bundle May Contain
- Safe task inputs/outputs/receipts/manifests/hashes.
- Explicit indexes to local-only sources.
- Approved local context files without secrets unless Owner explicitly permits.

## What Must Not Be Published to Git
- SSH commands, credentials, keys, tokens, passwords, cookies/sessions.
- Raw private/local command libraries.
- Unapproved secret-bearing runtime/config files.
