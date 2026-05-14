# ADDRESS REGISTRY V0.2

| address_id | path | owner organ | context type | purpose | payload allowed? | commit allowed? | agent access | notes |
|---|---|---|---|---|---|---|---|---|
| PC_REPO_ROOT | `E:\IMPERIUM` | ADMINISTRATUM | REPO_CANONICAL | tracked canonical project source | canonical only | YES | default | do not store local/private payload here |
| LOCAL_CONTEXT_ROOT | `E:\IMPERIUM_CONTEXT\LOCAL` | ADMINISTRATUM | LOCAL_OPERATIONAL | operational non-secret context root | local operational payload | NO | task-scoped | canonical evidence stays in repo files; operational evidence in local bundle |
| PRIVATE_CONTEXT_ROOT | `E:\IMPERIUM_CONTEXT\PRIVATE` | ADMINISTRATUM | PRIVATE_SENSITIVE | sensitive/private context root | private payload only | NO | owner-approved only | never commit private payload |
| LOCAL_INBOX | `E:\IMPERIUM_CONTEXT\LOCAL\INBOX` | ADMINISTRATUM | LOCAL_OPERATIONAL | inbound operational transfers | yes | NO | task-scoped | transport zone |
| LOCAL_OUTBOX | `E:\IMPERIUM_CONTEXT\LOCAL\OUTBOX` | ADMINISTRATUM | LOCAL_OPERATIONAL | outbound operational transfers | yes | NO | task-scoped | contains PC servitor bundles |
| LOCAL_RUNTIME | `E:\IMPERIUM_CONTEXT\LOCAL\RUNTIME` | ADMINISTRATUM | LOCAL_OPERATIONAL | runtime receipts/logs/evidence | yes | NO | task-scoped | replaces repo `.imperium_runtime` working zone |
| LOCAL_LOGS | `E:\IMPERIUM_CONTEXT\LOCAL\LOGS` | ADMINISTRATUM | LOCAL_OPERATIONAL | local logs | yes | NO | task-scoped | non-canonical logs |
| LOCAL_TEMP | `E:\IMPERIUM_CONTEXT\LOCAL\TEMP` | ADMINISTRATUM | LOCAL_OPERATIONAL | temporary files | yes | NO | task-scoped | purge policy by owner decision |
| LOCAL_ARTIFACTS | `E:\IMPERIUM_CONTEXT\LOCAL\ARTIFACTS` | ADMINISTRATUM | LOCAL_OPERATIONAL | generated artifacts not for Git | yes | NO | task-scoped | avoid pushing into repo |
| LOCAL_HANDOFF | `E:\IMPERIUM_CONTEXT\LOCAL\HANDOFF` | ADMINISTRATUM | LOCAL_OPERATIONAL | handoff payload | yes | NO | task-scoped | transport only |
| LOCAL_ADVISORY_INBOX | `E:\IMPERIUM_CONTEXT\LOCAL\ADVISORY_INBOX` | ASTRONOMICON | LOCAL_OPERATIONAL | advisory source intake | yes | NO | task-scoped | advisory remains not canon until gated |
| LOCAL_PC_SERVITOR_BUNDLES | `E:\IMPERIUM_CONTEXT\LOCAL\OUTBOX\PC_SERVITOR_BUNDLES` | ADMINISTRATUM | LOCAL_OPERATIONAL | PC servitor bundle output root | yes | NO | task-scoped | canonical local evidence folder |
| LOCAL_TRANSPORT_ZIPS | `E:\IMPERIUM_CONTEXT\LOCAL\TRANSPORT_ZIPS` | ADMINISTRATUM | LOCAL_OPERATIONAL | transport zip storage | yes | NO | task-scoped | zip is transport only |
| PRIVATE_AGENT_COMMUNICATION_ROUTES | `E:\IMPERIUM_CONTEXT\PRIVATE\AGENT_COMMUNICATION_ROUTES` | ADMINISTRATUM | PRIVATE_SENSITIVE | private route notes | private notes | NO | owner-approved only | no secret dumps in repo |
| PRIVATE_SSH_KEYS_INDEX | `E:\IMPERIUM_CONTEXT\PRIVATE\SSH_KEYS_INDEX` | ADMINISTRATUM | PRIVATE_SENSITIVE | private key index metadata | index metadata | NO | owner-approved only | no key material in repo |
| PRIVATE_CONTEXT_INDEX | `E:\IMPERIUM_CONTEXT\PRIVATE\PRIVATE_CONTEXT_INDEX` | ADMINISTRATUM | PRIVATE_SENSITIVE | private context index | index metadata | NO | owner-approved only | redact when referenced in repo |
| PRIVATE_HANDOFF | `E:\IMPERIUM_CONTEXT\PRIVATE\PRIVATE_HANDOFF` | ADMINISTRATUM | PRIVATE_SENSITIVE | private handoff payload | yes | NO | owner-approved only | never commit |
| PRIVATE_SECRET_NOTES | `E:\IMPERIUM_CONTEXT\PRIVATE\SECRET_NOTES` | ADMINISTRATUM | PRIVATE_SENSITIVE | private secret notes | yes | NO | owner-approved only | never commit |
