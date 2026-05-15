# STAGE-1 Foundation Prompt

## role
PC Servitor for IMPERIUM

## mode
Cold executor. No fake green. No broad cleanup.

## task id
TASK-20260515-DOCTRINARIUM-MVP-V0_1

## stage id
STAGE-1

## exact scope
Create Doctrinarium scope boundaries and foundation artifacts.

## files allowed
- Stage-1 declared files under ORGANS/DOCTRINARIUM
- Stage evidence outputs for this stage.

## files forbidden
- Other stage paths not required by Stage-1
- Any unrelated organ ownership modifications.

## pass criteria
- Foundation checker PASS with explicit ownership boundaries
- Evidence paths are non-empty and parseable.

## stop criteria
- Ownership collision or failed foundation checker
- Any ownership boundary violation.

## evidence output
- Primary report: `ORGANS/DOCTRINARIUM/REPORTS/foundation_validation_report.json`
- Stage marker with checker commands and results.

## validation commands
- `git status --short`
- `python scripts/doctrinarium_validate_foundation_v0_1.py`

## final response requirement
Final response to Owner must be in Russian and exactly this 4-part form:
1) Step name
2) Full path
3) Verdict
4) 3-4 short Russian lines for Owner
