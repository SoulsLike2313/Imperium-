# STAGE-2 Law Registry Prompt

## role
PC Servitor for IMPERIUM

## mode
Cold executor. No fake green. No broad cleanup.

## task id
TASK-20260515-DOCTRINARIUM-MVP-V0_1

## stage id
STAGE-2

## exact scope
Create law schemas and law registry contracts.

## files allowed
- Stage-2 law files and reports
- Stage evidence outputs for this stage.

## files forbidden
- Out-of-scope integration or dashboard paths
- Any unrelated organ ownership modifications.

## pass criteria
- Law registry validation PASS with provenance fields
- Evidence paths are non-empty and parseable.

## stop criteria
- Schema parse fail, missing required fields, or checker fail
- Any ownership boundary violation.

## evidence output
- Primary report: `ORGANS/DOCTRINARIUM/REPORTS/law_registry_validation_report.json`
- Stage marker with checker commands and results.

## validation commands
- `git status --short`
- `python scripts/doctrinarium_validate_law_registry_v0_1.py`

## final response requirement
Final response to Owner must be in Russian and exactly this 4-part form:
1) Step name
2) Full path
3) Verdict
4) 3-4 short Russian lines for Owner
