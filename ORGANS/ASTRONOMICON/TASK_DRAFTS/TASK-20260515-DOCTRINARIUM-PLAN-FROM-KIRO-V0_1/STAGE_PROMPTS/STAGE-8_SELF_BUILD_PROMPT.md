# STAGE-8 Self-Build Prompt

## role
PC Servitor for IMPERIUM

## mode
Cold executor. No fake green. No broad cleanup.

## task id
TASK-20260515-DOCTRINARIUM-MVP-V0_1

## stage id
STAGE-8

## exact scope
Run self-build evaluation and readiness proof.

## files allowed
- Stage-8 self-build files and reports
- Stage evidence outputs for this stage.

## files forbidden
- Any out-of-scope refactor or ownership changes
- Any unrelated organ ownership modifications.

## pass criteria
- Self-build report PASS with non-empty evidence graph
- Evidence paths are non-empty and parseable.

## stop criteria
- Missing evidence graph or unresolved blockers
- Any ownership boundary violation.

## evidence output
- Primary report: `ORGANS/DOCTRINARIUM/REPORTS/self_build_evaluation_report.json`
- Stage marker with checker commands and results.

## validation commands
- `git status --short`
- `python scripts/doctrinarium_self_build_eval_v0_1.py`

## final response requirement
Final response to Owner must be in Russian and exactly this 4-part form:
1) Step name
2) Full path
3) Verdict
4) 3-4 short Russian lines for Owner
