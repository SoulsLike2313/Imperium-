# FULL RUNTIME AUDIT SOURCE SURVEY V0.1

## Files Inspected (Read-Only)
- `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/BROWSER_PERFORMANCE_AUDIT_RECEIPT_V0_1.json`
- `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/BROWSER_AUDIT_TARGET_PATH_FIX_REPORT_V0_1.json`
- `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/BROWSER_PERFORMANCE_TARGET_PATH_FIX_RUNNER_REPORT_V0_1.json`
- `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/tools/browser_performance_audit_runner_v0_1.py`
- `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/server_v0_6.py`
- `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.html`
- `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.js`
- `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css`

## Server Path Assumptions
`server_v0_6.py` defines fixed path constants relative to repository layout and writes into `MEMORY_ZONES` and `RUNTIME` trees.

## Possible Runtime Write Paths Discovered
- `IMPERIUM_TEST_VERSION/SECOND_BRAIN/MEMORY_ZONES/TASK_INTAKE/accepted_tasks.json`
- `IMPERIUM_TEST_VERSION/SECOND_BRAIN/MEMORY_ZONES/OWNER_COMMENTS/owner_comments_runtime.json`
- `IMPERIUM_TEST_VERSION/SECOND_BRAIN/MEMORY_ZONES/MEMORY_LINKS/task_comment_links.json`
- `IMPERIUM_TEST_VERSION/SECOND_BRAIN/RUNTIME/receipts/*.json`
- `IMPERIUM_TEST_VERSION/SECOND_BRAIN/RUNTIME/task_packages/<task_id>/**`
- `IMPERIUM_TEST_VERSION/SECOND_BRAIN/RUNTIME/exports/export_<stamp>/**`
- `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/reports/neural_snapshot_live.json`

## Possible API Endpoints Discovered
- `GET /api/snapshot`
- `GET /api/status`
- `GET /api/tasks`
- `GET /api/task_packages`
- `GET /api/tasks/<id>`
- `GET /api/tasks/<id>/validation`
- `GET /api/comments`
- `GET /api/links`
- `GET /api/receipts`
- `GET /api/export/status`
- `GET /api/thread/<task_id>`
- `POST /api/tasks/register`
- `POST /api/tasks/launch`
- `POST /api/tasks`
- `POST /api/comments`
- `POST /api/links`
- `POST /api/export`
- `POST /api/rebuild_snapshot`

## Possible Mutating Endpoints
- `POST /api/tasks/register`
- `POST /api/tasks/launch`
- `POST /api/tasks`
- `POST /api/comments`
- `POST /api/links`
- `POST /api/export`
- `POST /api/rebuild_snapshot`

## Static Frontend Limitations
- Static frontend audit does not validate live API/backend path truth.
- Static frontend FPS is not full runtime performance evidence.
- Static mode does not prove runtime write isolation or cleanup discipline.
- Console/network behavior in static mode differs from live runtime server mode.

## Full Runtime Audit Risks
- Runtime audit can write into MEMORY_ZONES and RUNTIME paths by design.
- Without quarantine, runtime writes can pollute repository truth and future gates.
- Mutating endpoints can alter task/comment/link state and create receipts/exports.
- Snapshot rebuild can invoke subprocess and generate new runtime/report artifacts.
- Leaving server running can create uncontrolled side effects after audit window.

## Recommended Safe Launch Approach (Future Task)
- Use disposable runtime workspace / copy of V0.6 runtime root.
- Start server inside isolated workspace only.
- Route all runtime writes into quarantine root and receipt every write.
- Enforce server stop and post-run path diff checks before any verdict.
