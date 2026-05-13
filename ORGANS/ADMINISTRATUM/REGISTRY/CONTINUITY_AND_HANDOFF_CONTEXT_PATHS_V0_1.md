# Continuity and Handoff Context Paths v0.1

## Context Collection Roots
- Git context source: `E:\IMPERIUM`
- Local operational context source: `E:\IMPERIUM_CONTEXT\LOCAL`
- Private Owner-controlled context source: `E:\IMPERIUM_CONTEXT\PRIVATE`

## Inclusion Policy
- Private context is included only by Owner decision.
- Full handoff may reference local/private manifests without embedding private payload content.
- Do not commit continuity outputs unless explicitly intended and reviewed.
- Private/local payloads must never be committed.

## Operational Notes
- Legacy roots (`E:\IMPERIUM_LOCAL`, `E:\IMPERIUM_PRIVATE`) are not primary collection roots after unification.
- Future continuity collectors should read from unified `E:\IMPERIUM_CONTEXT` roots first.
