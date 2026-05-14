# ASTRONOMICON WORKBENCH OWNER FLOW V0.1

Owner opens Astronomicon Workbench
→ inserts General Task into window
→ clicks Validate
→ clicks Decompose
→ sees Local Task candidates
→ selects 1 Local Task
→ clicks Export to Speculum
→ sends Speculum review pack
→ imports structured Speculum response
→ clicks Modernize Task
→ clicks Decompose to Stages
→ sees stage map
→ exports stage map to Speculum
→ imports stage review
→ clicks Register
→ gets registered Local Task + STAGEs
→ gives Servitor Local Task name + short recipe

| step | Owner action | backend script | input | output | status in MVP |
|---|---|---|---|---|---|
| 1 | Open Workbench | `scripts/astronomicon_workbench_server.py` | none | UI loaded | PASS |
| 2 | Fill General Task form | future form->file writer | form fields | GT markdown/json | PLACEHOLDER |
| 3 | Validate | `scripts/astronomicon_validate_general_task.py` | GT markdown path | pass/fail | PASS |
| 4 | Decompose | `scripts/astronomicon_decompose_general_task_to_candidates.py` | GT markdown path | candidate JSON files | PASS |
| 5 | Inspect candidates | dashboard JSON | candidate files | candidates panel | PASS |
| 6 | Select one task | future selector action | candidate id | selected task state | PLACEHOLDER |
| 7 | Export task review request | future export task script | selected task | speculum request pack | PLACEHOLDER |
| 8 | Import task review response | future import/validate script | response payload | validated review state | PLACEHOLDER |
| 9 | Modernize selected task | future modernization script | selected task + review | updated task draft | PLACEHOLDER |
| 10 | Decompose to stages | future stage decomposition script | selected task | stage map draft | PLACEHOLDER |
| 11 | Export stage review request | future export stage script | stage map | speculum stage pack | PLACEHOLDER |
| 12 | Import stage review response | future import/validate script | stage response payload | validated stage review state | PLACEHOLDER |
| 13 | Register task+stages | future register script | reviewed task + stages | registered artifacts | PLACEHOLDER |
| 14 | Servitor handoff | future task lookup path | local task id + recipe | self-loaded task context | PLACEHOLDER |
