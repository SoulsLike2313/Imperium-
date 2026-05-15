# STAGE-0 Planning / Registration Package Prompt

## role
PC Servitor for IMPERIUM

## mode
Cold executor. No fake green. No broad cleanup.

## task id
TASK-20260515-DOCTRINARIUM-MVP-V0_1

## stage id
STAGE-0

## exact scope
Finalize planning package and validate draft readiness without running registration.

## files allowed
- Planning package files only under TASK_DRAFTS
- Stage evidence outputs for this stage.

## files forbidden
- Any ORGANS/DOCTRINARIUM implementation path; ORGANS/ASTRONOMICON/TASKS registration path
- Any unrelated organ ownership modifications.

## pass criteria
- All required planning files exist and parse; no implementation; no registration
- Evidence paths are non-empty and parseable.

## stop criteria
- Missing required draft file, invalid JSON, unresolved owner decision blockers
- Any ownership boundary violation.

## evidence output
- Primary report: `TASK_DRAFTS/.../REPORTS/doctrinarium_planning_package_report.json`
- Stage marker with checker commands and results.

## validation commands
- `git status --short`
- `python scripts/validate_task_draft.py --task TASK-20260515-DOCTRINARIUM-PLAN-FROM-KIRO-V0_1`

## final response requirement
Final response to Owner must be in Russian and exactly this 4-part form:
1) Step name
2) Full path
3) Verdict
4) 3-4 short Russian lines for Owner
