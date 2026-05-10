# PUBLIC PRIVATE BOUNDARY REPORT

## Public in Git
- Source, docs, receipts, safe indexes, analyzer outputs.

## Local-only roots
- SSH_COMMAND_LIBRARY
- ARCHIVE
- BUNDLES_LOCAL
- PRIVATE_CONTEXT_LOCAL
- RUNTIME_LOCAL
- CHAT_COMPILATIONS_LOCAL

## Ignore state
- ignored_private_roots: SSH_COMMAND_LIBRARY, ARCHIVE, BUNDLES_LOCAL, PRIVATE_CONTEXT_LOCAL, RUNTIME_LOCAL, CHAT_COMPILATIONS_LOCAL
- not_ignored_private_roots: OBSERVED/THRONE_REPO_COPY, OBSERVED/VM3_REPO_COPY

## Suspicious scans
- suspicious_tracked_paths_count: 0
- suspicious_history_paths_count: 0
- boundary_verdict: NEEDS_IGNORE_REPAIR

## Never commit
- raw keys/tokens/passwords/.env values/private command bodies
- full ARCHIVE and full SSH_COMMAND_LIBRARY content
