# PUBLIC PRIVATE BOUNDARY

## Safe for Git
- Source code, scripts, contracts, status files, safe docs.
- Receipts/manifests/hashes that do not disclose secrets.
- Safe indexes declaring local/private sources exist.

## Local-Only
- SSH_COMMAND_LIBRARY/
- ARCHIVE/
- BUNDLES_LOCAL/, PRIVATE_CONTEXT_LOCAL/, RUNTIME_LOCAL/
- legacy observed heavy copies and generated extract/check mirrors

## Private Bundle Required
Use approved private bundle flow when a worker needs local-only context.

## Never Publish
- credentials, keys, tokens, passwords, secret command bodies, session/cookie data.
