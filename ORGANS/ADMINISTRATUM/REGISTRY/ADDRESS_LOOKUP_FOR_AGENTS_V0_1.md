# ADDRESS LOOKUP FOR AGENTS V0.1

## Quick answers
- Repo root: `E:\IMPERIUM`
- Local inbox/outbox/runtime: `E:\IMPERIUM_CONTEXT\LOCAL\INBOX`, `E:\IMPERIUM_CONTEXT\LOCAL\OUTBOX`, `E:\IMPERIUM_CONTEXT\LOCAL\RUNTIME`
- Advisory inbox: `E:\IMPERIUM_CONTEXT\LOCAL\ADVISORY_INBOX`
- Bundle output path: `E:\IMPERIUM_CONTEXT\LOCAL\OUTBOX\PC_SERVITOR_BUNDLES\{TASK_ID}\`
- Private route/key indexes: `E:\IMPERIUM_CONTEXT\PRIVATE\AGENT_COMMUNICATION_ROUTES`, `E:\IMPERIUM_CONTEXT\PRIVATE\SSH_KEYS_INDEX`

## Never commit
- LOCAL or PRIVATE payload content, runtime dumps, secret notes, transport bundles.

## If address is missing
1. Do not guess by scanning disk.
2. Record `BLOCKED_ADDRESS_UNRESOLVED` or warning in bundle.
3. Ask Owner/Administratum to register the missing address.

## How to report uncertainty
- Add explicit uncertainty line in `04_BLOCKERS_WARNINGS.md` with expected address id and requested owner decision.
