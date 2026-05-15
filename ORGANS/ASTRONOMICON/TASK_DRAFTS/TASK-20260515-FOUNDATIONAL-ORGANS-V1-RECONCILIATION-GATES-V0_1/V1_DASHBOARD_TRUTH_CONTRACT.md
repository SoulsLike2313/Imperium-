# V1 Dashboard Truth Contract

## Truth-first rules
- Dashboards read backend reports via data adapters.
- No green state is allowed without evidence from backend reports.
- No mock truth panel is allowed in V1 hardening execution.

## Script and status display
- Every shown script must exist.
- Each script card must show last run report or explicit disabled reason.
- Disabled state must include reason, owner, and re-enable condition.

## Action button contract
- Each action button needs action contract, confirmation flow, timeout, and failure behavior.
- Each action invocation must generate a dashboard action receipt.
- Missing receipt forces non-green state for that action surface.

## i18n separation
- Canonical machine contracts stay English UTF-8.
- RU/EN presentation layers are localized display assets, not canonical truth owners.

## Sanctum aggregation
- Sanctum is read-only aggregation.
- Sanctum must never become canonical source of truth.
