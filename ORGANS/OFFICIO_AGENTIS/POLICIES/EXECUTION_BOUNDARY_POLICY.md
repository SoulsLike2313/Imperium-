# EXECUTION_BOUNDARY_POLICY v0.1

Execution boundaries by role:

- `SERVITOR`: may execute in `EXECUTE` mode within declared stage scope.
- `LOGOS_PRIME`: does not execute repo changes without explicit Owner approval/mode.
- `LOGOS_SPECULUM`: never executes fixes.
- `ADVISOR_SERVITOR`: does not execute repo changes unless explicitly promoted.

Boundary violations must trigger stop behavior and be reported in machine-readable evidence.
