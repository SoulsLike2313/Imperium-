# ASTRONOMICON MVP OWNER DECISIONS V0.1 (DRAFT)

| decision | recommended default | current owner decision | why it matters | blocker if unanswered |
|---|---|---|---|---|
| General Task format | YAML frontmatter + Markdown body | ACCEPT_RECOMMENDED_YAML_FRONTMATTER_MARKDOWN | stable intake format for owner intent and machine parsing later | MEDIUM |
| First decomposition | TASK candidates only, not registered TASKs | TASK_CANDIDATES_ONLY | avoids premature activation while corridor is being built | MEDIUM |
| Speculum review before stage split | optional/deferred for MVP, mandatory-capable later | OWNER_CONFIRMATION_RECOMMENDED | balances speed with review quality controls | LOW |
| Dashboard approach | backend JSON first + minimal read-only viewer before Sanctum integration | OWNER_CONFIRMATION_RECOMMENDED | prevents fake UI progress without backend truth | HIGH |
| Final task bundle location | ORGANS/ADMINISTRATUM/TASK_ARTIFACTS/{TASK_ID}/FINAL_BUNDLE/ | OWNER_CONFIRMATION_RECOMMENDED | defines clear artifact handoff endpoint | MEDIUM |
| Administratum stage permission strictness | basic strict in MVP, full strict later | OWNER_CONFIRMATION_RECOMMENDED | controls safety vs speed during first implementation arc | MEDIUM |
| First E2E scope | one General Task to one TASK candidate to one STAGE to one acceptance cycle | OWNER_CONFIRMATION_RECOMMENDED | creates smallest trustworthy corridor | HIGH |
| Kiro responses | store as RAW_ADVISORY, never active canon directly | ACCEPT_RAW_ADVISORY_ONLY | prevents advisory/canon conflation | HIGH |
| Metric BLOCKER policy | hard stop unless Owner override | OWNER_CONFIRMATION_RECOMMENDED | keeps blocker semantics trustworthy | HIGH |
| VM2 | deferred until PC corridor proven | DEFERRED_OFFLINE | avoids cross-contour noise before baseline is stable | HIGH |
| commit/push automation | reject for now | REJECTED_FOR_NOW | no write automation before fail-closed controls | HIGH |

## Route note

- Owner confirmation recommended: local operational bundles use E:\\IMPERIUM_CONTEXT\\LOCAL\\OUTBOX\\PC_SERVITOR_BUNDLES; repo keeps tracked canonical artifacts only.

