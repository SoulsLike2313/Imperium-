# STAGE-5 Task Start Gate Prompt

## role
PC Servitor for IMPERIUM

## mode
Cold executor. No fake green. No broad cleanup.

## task id
TASK-20260515-DOCTRINARIUM-MVP-V0_1

## stage id
STAGE-5

## exact scope
Implement task start gate and violation records.

## files allowed
- Stage-5 gate files and reports
- Stage evidence outputs for this stage.

## files forbidden
- Unrelated stage files outside task gate scope
- Any unrelated organ ownership modifications.

## pass criteria
- Gate verdict deterministic and violation records generated when blocked
- Evidence paths are non-empty and parseable.

## stop criteria
- Missing verdict file, inconsistent allow_execution, or missing violation artifact
- Any ownership boundary violation.

## evidence output
- Primary report: `ORGANS/DOCTRINARIUM/REPORTS/task_start_gate_verdict_report.json`
- Stage marker with checker commands and results.

## validation commands
- `git status --short`
- `python scripts/doctrinarium_task_start_gate_v0_1.py && python scripts/doctrinarium_record_violation_v0_1.py`

## final response requirement
Final response to Owner must be in Russian and exactly this 4-part form:
1) Step name
2) Full path
3) Verdict
4) 3-4 short Russian lines for Owner
