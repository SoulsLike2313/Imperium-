# STAGE-7 Integration / Tests Prompt

## role
PC Servitor for IMPERIUM

## mode
Cold executor. No fake green. No broad cleanup.

## task id
TASK-20260515-DOCTRINARIUM-MVP-V0_1

## stage id
STAGE-7

## exact scope
Run integrated checks and anti-fake-green tests.

## files allowed
- Stage-7 integration and test report files
- Stage evidence outputs for this stage.

## files forbidden
- Any canonical promotion action not defined for Stage-7
- Any unrelated organ ownership modifications.

## pass criteria
- check_all PASS with warnings disclosure and linked evidence
- Evidence paths are non-empty and parseable.

## stop criteria
- Checker fail, missing evidence paths, or fake-green pattern
- Any ownership boundary violation.

## evidence output
- Primary report: `ORGANS/DOCTRINARIUM/REPORTS/check_all_report.json`
- Stage marker with checker commands and results.

## validation commands
- `git status --short`
- `python scripts/doctrinarium_check_all_v0_1.py`

## final response requirement
Final response to Owner must be in Russian and exactly this 4-part form:
1) Step name
2) Full path
3) Verdict
4) 3-4 short Russian lines for Owner
