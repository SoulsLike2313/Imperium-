# STAGE-6 Inquisition Hook Disabled Prompt

## role
PC Servitor for IMPERIUM

## mode
Cold executor. No fake green. No broad cleanup.

## task id
TASK-20260515-DOCTRINARIUM-MVP-V0_1

## stage id
STAGE-6

## exact scope
Create disabled hook artifacts and verify non-active behavior.

## files allowed
- Stage-6 inquisition-disabled files and reports
- Stage evidence outputs for this stage.

## files forbidden
- Any active-hook implementation behavior
- Any unrelated organ ownership modifications.

## pass criteria
- Disabled hook report PASS and explicit disabled status
- Evidence paths are non-empty and parseable.

## stop criteria
- Any claim or behavior indicating active hook
- Any ownership boundary violation.

## evidence output
- Primary report: `ORGANS/DOCTRINARIUM/REPORTS/inquisition_hook_disabled_report.json`
- Stage marker with checker commands and results.

## validation commands
- `git status --short`
- `python scripts/doctrinarium_verify_inquisition_hook_disabled_v0_1.py`

## final response requirement
Final response to Owner must be in Russian and exactly this 4-part form:
1) Step name
2) Full path
3) Verdict
4) 3-4 short Russian lines for Owner
