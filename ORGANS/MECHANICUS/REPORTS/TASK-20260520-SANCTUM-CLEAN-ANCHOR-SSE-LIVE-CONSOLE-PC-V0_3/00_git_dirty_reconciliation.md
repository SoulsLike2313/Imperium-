# 00 Git Dirty Reconciliation

- task_id: TASK-20260520-SANCTUM-CLEAN-ANCHOR-SSE-LIVE-CONSOLE-PC-V0_3
- starting_head: 670f1a1dc53d5c2f34805a09736676e3c03e83f3
- policy: hidden dirty state forbidden; reconcile before implementation

## Dirty Status Before
```text
 M IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/MECHANICUS_AGENT/REPORTS/base_half_check_report.json
 M IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/MECHANICUS_AGENT/REPORTS/base_half_check_report.md
 M IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/MECHANICUS_AGENT/state/current_status.json
?? ORGANS/MECHANICUS/REPORTS/
```

## File Classification
- path: IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/MECHANICUS_AGENT/REPORTS/base_half_check_report.json
  class: runtime_side_effect
  reason: timestamp/content refresh from Mechanicus checks; not in this task scope
  action: restore_to_head
- path: IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/MECHANICUS_AGENT/REPORTS/base_half_check_report.md
  class: runtime_side_effect
  reason: timestamp/content refresh from Mechanicus checks; not in this task scope
  action: restore_to_head
- path: IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/MECHANICUS_AGENT/state/current_status.json
  class: runtime_side_effect
  reason: auto-regenerated state snapshot caused by Mechanicus runner commands
  action: restore_to_head

## Reconciliation Decision
- All pre-existing dirty files were runtime side effects outside V0_3 source scope.
- They were restored to HEAD before core edits.
- During SSE proof execution, `state/current_status.json` mutated again (runner side effect) and was restored to HEAD a second time.

## Dirty Status After Reconciliation
```text
 M IMPERIUM_NEW_GENERATION/SANCTUM_MINI/api/actions.py
 M IMPERIUM_NEW_GENERATION/SANCTUM_MINI/api/state_builder.py
 M IMPERIUM_NEW_GENERATION/SANCTUM_MINI/server.py
 M IMPERIUM_NEW_GENERATION/SANCTUM_MINI/static/app.js
 M IMPERIUM_NEW_GENERATION/SANCTUM_MINI/static/index.html
 M IMPERIUM_NEW_GENERATION/SANCTUM_MINI/static/styles.css
?? IMPERIUM_NEW_GENERATION/SANCTUM_MINI/api/event_stream.py
?? ORGANS/MECHANICUS/REPORTS/TASK-20260520-SANCTUM-CLEAN-ANCHOR-SSE-LIVE-CONSOLE-PC-V0_3/
```
