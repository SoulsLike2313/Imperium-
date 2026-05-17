# RUNTIME AUDIT STATIC ASSET ROUTE FIX DIAGNOSIS V0.1

- task_id: `TASK-SECOND-BRAIN-V07-RUNTIME-AUDIT-STATIC-ASSET-ROUTE-FIX`
- generated_at: `2026-05-17T14:23:35Z`
- current_head: `a6520bfea976b6b54497219518f6068fc83e27f5`
- primary_cause_category: `D` (runner target path does not match server static mount)
- secondary_categories: `A, B`
- verdict: `DIAGNOSIS_CONFIRMED_ROUTE_STATIC_MISMATCH`

## Evidence
- previous_target: `http://127.0.0.1:8767/neural_map_v0_6.html`
- previous_http_status: `404`
- css_loaded_previous: `False`
- js_loaded_previous: `False`
- api_checks_previous: `API_CHECKS_PASS`

## Diagnosis
- Runner used /neural_map_v0_6.html while V0.6 server serves the UI entry from /. This produced 404, prevented required CSS/JS requests, and invalidated FPS for full UI acceptance.

## Planned Repair
- Native route discovery first.
- If native route not usable, start 127.0.0.1 audit static proxy with /api/* pass-through to runtime backend.
- Accept FPS only when HTML/CSS/JS/API are all valid.
