# ASTRONOMICON WORKBENCH README V0.1

## Purpose

Minimal dashboard/workbench-first owner flow for Astronomicon MVP dense base.
Backend server action handling uses direct Python function calls (no raw subprocess spawning).

## Start server

```powershell
python scripts/astronomicon_create_dashboard_data.py
python scripts/astronomicon_workbench_server.py --host 127.0.0.1 --port 8765
```

Open: `http://127.0.0.1:8765`

## Button to backend mapping

| Button | Script/action | MVP status |
|---|---|---|
| Save General Task | Planned: save form -> markdown/json writer (not fully implemented) | PLACEHOLDER |
| Validate | `python scripts/astronomicon_validate_general_task.py <path>` | AVAILABLE (manual file path in MVP) |
| Decompose General Task | `python scripts/astronomicon_decompose_general_task_to_candidates.py <path> --out <dir>` | AVAILABLE |
| Export Local Task to Speculum | Planned export pack script | PLACEHOLDER |
| Import Speculum Task Review | Planned import+validate script by schema | PLACEHOLDER |
| Modernize Local Task | Planned transformation script after valid review | PLACEHOLDER |
| Decompose to Stages | Planned stage decomposition script | PLACEHOLDER |
| Export Stage Map to Speculum | Planned export stage review request script | PLACEHOLDER |
| Import Speculum Stage Review | Planned import+validate script by schema | PLACEHOLDER |
| Register | Planned register selected task+stages script | PLACEHOLDER (disabled by dashboard data) |
| Refresh Dashboard Data | `python scripts/astronomicon_create_dashboard_data.py` (via `/api/action`) | AVAILABLE |

## Data source

Workbench reads backend JSON from:

- `ORGANS/ASTRONOMICON/DASHBOARD_DATA/active_state.json`
- `ORGANS/ASTRONOMICON/DASHBOARD_DATA/general_task_current.json`
- `ORGANS/ASTRONOMICON/DASHBOARD_DATA/task_candidates.json`
- `ORGANS/ASTRONOMICON/DASHBOARD_DATA/selected_task.json`
- `ORGANS/ASTRONOMICON/DASHBOARD_DATA/stage_map.json`
- `ORGANS/ASTRONOMICON/DASHBOARD_DATA/speculum_review_state.json`
- `ORGANS/ASTRONOMICON/DASHBOARD_DATA/blockers.json`
- `ORGANS/ASTRONOMICON/DASHBOARD_DATA/workbench_meta.json`

## Honest MVP limits

- UI exists and is backend-data driven.
- Several actions are placeholder routes, intentionally non-fake.
- No registration promotion without completed review/import gates.
