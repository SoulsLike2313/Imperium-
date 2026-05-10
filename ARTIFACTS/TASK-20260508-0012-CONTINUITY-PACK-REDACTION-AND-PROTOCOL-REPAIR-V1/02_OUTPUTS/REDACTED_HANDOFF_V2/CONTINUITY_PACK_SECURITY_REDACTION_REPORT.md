# CONTINUITY PACK SECURITY REDACTION REPORT

## Scope
This report documents redaction and exclusion actions applied while creating continuity handoff V2.

## What was redacted
- Raw route host values.
- Raw route user@host values.
- Raw route port values.
- Raw private-key file paths.
- Raw command examples containing local route values.

## What was not copied
- *.local.json files.
- *.local.md files.
- files matching *LOCAL_ACCESS*.
- raw local-only route configuration content.

## Why local route values are sensitive
Local route values can expose machine identity, account metadata, network details, and key-location hints.
Shareable handoff packs must not include these details.

## Additional policy notes
- No private key contents were intentionally included.
- Local-only config files were excluded.
- Raw user@host/port/private-key examples were replaced with REDACTED_LOCAL_ROUTE_VALUE.
- Legacy VM3 route and latest-bundle materials are marked historical only and blocked for new protocol use.
