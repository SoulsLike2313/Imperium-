# AGENT_EXECUTION_REPORT_STANDARD_V1

## Status
Mandatory for all IMPERIUM agents and executors.

## Applies to
- task execution reports
- stage execution reports
- fetch/verify reports
- review reports
- manual operation reports

## Mandatory final response format
Every agent must answer Owner using exactly these four sections:

1. ШАГ:
- task_id and/or stage_id
- human-readable step name if available

2. БАНДЛ:
- full path to created/fetched/reviewed bundle
- or N/A if no bundle was produced

3. ВЕРДИКТ:
Allowed values only:
- PASS
- PASS_FOR_PROTOCOL_BASE
- NEEDS_SPECULUM_REVIEW
- PARTIAL
- WAITING
- BLOCKED
- FAIL
- CONFLICT

4. КОММЕНТАРИЙ ДЛЯ OWNER:
- 3-4 short lines in Russian
- must state what was done
- must state what was proven or not proven
- must state what remains blocked/deferred
- must state the next step

## Hard requirements
- Missing any of the four sections is invalid.
- Section names must be exactly: `ШАГ`, `БАНДЛ`, `ВЕРДИКТ`, `КОММЕНТАРИЙ ДЛЯ OWNER`.
- By default the response must be concise and Owner-readable.
- Long arbitrary reports are allowed only when explicitly requested.
- Do not include raw secrets or local-only route values.
