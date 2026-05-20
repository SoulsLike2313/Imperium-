# Validation Report

- generated_at_utc: 2026-05-20T15:25:06.7452521Z
- base_url: http://127.0.0.1:18765
- pass_count: 13
- fail_count: 0
- overall: PASS

## Checks
- [PASS] py_compile_server | exit=0 | command=`python -m py_compile IMPERIUM_NEW_GENERATION/SANCTUM_MINI/server.py` | evidence=IMPERIUM_NEW_GENERATION/SANCTUM_MINI/server.py | limitation=Syntax/import-time check only
- [PASS] py_compile_actions | exit=0 | command=`python -m py_compile IMPERIUM_NEW_GENERATION/SANCTUM_MINI/api/actions.py` | evidence=IMPERIUM_NEW_GENERATION/SANCTUM_MINI/api/actions.py | limitation=Syntax/import-time check only
- [PASS] py_compile_state_builder | exit=0 | command=`python -m py_compile IMPERIUM_NEW_GENERATION/SANCTUM_MINI/api/state_builder.py` | evidence=IMPERIUM_NEW_GENERATION/SANCTUM_MINI/api/state_builder.py | limitation=Syntax/import-time check only
- [PASS] py_compile_event_stream | exit=0 | command=`python -m py_compile IMPERIUM_NEW_GENERATION/SANCTUM_MINI/api/event_stream.py` | evidence=IMPERIUM_NEW_GENERATION/SANCTUM_MINI/api/event_stream.py | limitation=Syntax/import-time check only
- [PASS] node_check_app_js | exit=0 | command=`node --check IMPERIUM_NEW_GENERATION/SANCTUM_MINI/static/app.js` | evidence=IMPERIUM_NEW_GENERATION/SANCTUM_MINI/static/app.js | limitation=No runtime DOM assertions
- [PASS] api_health | exit=0 | command=`GET /api/health` | evidence=POST_api_health.json | limitation=Runtime checked on local port 18765
- [PASS] api_state | exit=0 | command=`GET /api/state` | evidence=POST_api_state.json | limitation=Runtime checked on local port 18765
- [PASS] api_actions | exit=0 | command=`GET /api/actions` | evidence=POST_api_actions.json | limitation=Runtime checked on local port 18765
- [PASS] json_verdict | exit=0 | command=`python -m json.tool CURRENT_SANCTUM_TRUTH_VERDICT.json` | evidence=CURRENT_SANCTUM_TRUTH_VERDICT.json | limitation=Format/parse check only
- [PASS] json_sse_report | exit=0 | command=`python -m json.tool sse_proof_report.json` | evidence=sse_proof_report.json | limitation=Format/parse check only
- [PASS] json_performance_report | exit=0 | command=`python -m json.tool performance_probe_report.json` | evidence=performance_probe_report.json | limitation=Format/parse check only
- [PASS] json_playwright_report | exit=0 | command=`python -m json.tool playwright_capture_report.json` | evidence=playwright_capture_report.json | limitation=Format/parse check only
- [PASS] json_post_api_state | exit=0 | command=`python -m json.tool POST_api_state.json` | evidence=POST_api_state.json | limitation=Format/parse check only

