# STAGE-3 Law Integrity Prompt

## role
PC Servitor for IMPERIUM

## mode
Cold executor. No fake green. No broad cleanup.

## task id
TASK-20260515-DOCTRINARIUM-MVP-V0_1

## stage id
STAGE-3

## exact scope
Implement law integrity checks and contradiction handling.

## files allowed
- Stage-3 integrity files and reports
- Stage evidence outputs for this stage.

## files forbidden
- Scope outside law integrity responsibilities
- Any unrelated organ ownership modifications.

## pass criteria
- Integrity checker PASS with contradiction metrics
- Evidence paths are non-empty and parseable.

## stop criteria
- Unresolved contradiction or checker fail
- Any ownership boundary violation.

## evidence output
- Primary report: `ORGANS/DOCTRINARIUM/REPORTS/law_integrity_report.json`
- Stage marker with checker commands and results.

## validation commands
- `git status --short`
- `python scripts/doctrinarium_check_law_integrity_v0_1.py`

## final response requirement
Final response to Owner must be in Russian and exactly this 4-part form:
1) Step name
2) Full path
3) Verdict
4) 3-4 short Russian lines for Owner
