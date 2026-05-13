# BUNDLE_ROUTE_POLICY_V0_1

## Purpose
This policy locks a canonical VM2 bundle route so Sanctum and operators stop drifting between multiple ambiguous outbox folders.

## Canonical Route Truth
- VM2 canonical outbox: `/home/vboxuser2/IMPERIUM_WORK/VM2_BUNDLES/`
- PC canonical inbox: `E:\IMPERIUM\INBOX\VM2_BUNDLES\`

## Legacy Scan-Only Sources
- `/home/vboxuser2/IMPERIUM_WORK/_handoff_out/`
- `/home/vboxuser2/IMPERIUM_PRIVATE/OUTBOX/`

Legacy sources remain discovery fallback only and must never override canonical source priority.

## Source Priority
1. canonical VM2 outbox
2. legacy `_handoff_out`
3. legacy private `OUTBOX`

## Fetch Latest / Dedupe Rules
- `Fetch Latest` uses canonical-first selection.
- If the same bundle name exists in multiple source dirs:
  1. canonical source wins,
  2. then newest mtime if same priority,
  3. unresolved ambiguity is reported explicitly.

## Owner Rule
Canonical `VM2_BUNDLES` is mandatory primary source for new VM2 bundle emission.

## Safety Notes
- Policy change does not set `READY_FOR_AGENT` to true.
- Policy change does not make Act 5 execution ready.
- VM2 remains no-commit/no-push contour.
