# Mode Transitions v0.1

## SERVITOR

- `CHECK_ONLY -> EXECUTE` when execution is required.
- `EXECUTE -> REPAIR_WITHIN_SCOPE` when checker fails inside stage scope.
- `EXECUTE/REPAIR_WITHIN_SCOPE -> STOPPED_PENDING_OWNER` when stop criteria trigger.

## LOGOS_PRIME

- `CHAT_ASSIST -> PLANNING` on planning request.
- `PLANNING -> COMMAND_BUILDER` on command request.
- `COMMAND_BUILDER -> REVIEW -> HANDOFF` as workflow progresses.

## LOGOS_SPECULUM

- `RED_TEAM -> SPEC_REVIEW -> GATE_AUDIT -> CONTRADICTION_HUNT` based on audit depth.

## ADVISOR_SERVITOR

- `RESEARCH -> OPTIONS_REVIEW -> PLAN_BUILDER` when recommendation is selected.
- `PLAN_BUILDER -> TASK_CLARIFIER` when ambiguity blocks safe recommendation.
