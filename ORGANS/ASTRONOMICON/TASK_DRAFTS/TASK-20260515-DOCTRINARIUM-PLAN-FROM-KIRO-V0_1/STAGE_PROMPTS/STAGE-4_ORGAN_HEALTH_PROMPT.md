# STAGE-4 Organ Health Prompt

## role
PC Servitor for IMPERIUM

## mode
Cold executor. No fake green. No broad cleanup.

## task id
TASK-20260515-DOCTRINARIUM-MVP-V0_1

## stage id
STAGE-4

## exact scope
Implement self-report collection and health verdict logic.

## files allowed
- Stage-4 health files and reports
- Stage evidence outputs for this stage.

## files forbidden
- Task gate or inquisition hook files
- Any unrelated organ ownership modifications.

## pass criteria
- Health verdict PASS with checker_last_run_utc
- Evidence paths are non-empty and parseable.

## stop criteria
- Missing/stale self-report or invalid verdict schema
- Any ownership boundary violation.

## evidence output
- Primary report: `ORGANS/DOCTRINARIUM/REPORTS/organ_health_verdict_report.json`
- Stage marker with checker commands and results.

## validation commands
- `git status --short`
- `python scripts/doctrinarium_collect_organ_self_reports_v0_1.py && python scripts/doctrinarium_evaluate_organ_health_v0_1.py`

## final response requirement
Final response to Owner must be in Russian and exactly this 4-part form:
1) Step name
2) Full path
3) Verdict
4) 3-4 short Russian lines for Owner
