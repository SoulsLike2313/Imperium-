# EXTERNAL CONTEXT PATHS V0.2

## Rule
- `E:\IMPERIUM` stores tracked canonical repo files.
- `E:\IMPERIUM_CONTEXT\LOCAL` stores operational non-secret payload (inbox/outbox/runtime/logs/temp/handoff/artifacts).
- `E:\IMPERIUM_CONTEXT\PRIVATE` stores sensitive/private payload and private indexes.
- Repo keeps policies, registries and redacted references only; no private/local payload dumps.

## Agent behavior
- Agents must consult Administratum address registry before touching non-repo paths.
- Agents must not scan full disk to discover context.
- Missing address resolution must be reported to Owner via bundle blocker/warning.

## Legacy roots
- Legacy path labels (`E:\IMPERIUM_LOCAL`, `E:\IMPERIUM_PRIVATE`) are compatibility references only and not primary targets for new operations.
