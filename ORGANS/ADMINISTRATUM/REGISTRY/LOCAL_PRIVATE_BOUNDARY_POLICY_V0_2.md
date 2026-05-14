# LOCAL PRIVATE BOUNDARY POLICY V0.2

## Placement policy
- Repo (`E:\IMPERIUM`): tracked canonical source, schemas, tests, policies, redacted indexes.
- LOCAL (`E:\IMPERIUM_CONTEXT\LOCAL`): runtime output, bundles, transport artifacts, temporary/log data.
- PRIVATE (`E:\IMPERIUM_CONTEXT\PRIVATE`): sensitive/private context, secret notes, private route details.

## Never commit
- Secret payloads, keys, private handoff payload, runtime/local transport bundles.

## Redaction and references
- Repo may reference private/local paths as redacted pointers only.
- Never copy private payload content into tracked files.

## Access model
- Repo: readable by all task agents in scoped tasks.
- LOCAL: readable when operational evidence is required.
- PRIVATE: readable only under explicit Owner task-level permission.
