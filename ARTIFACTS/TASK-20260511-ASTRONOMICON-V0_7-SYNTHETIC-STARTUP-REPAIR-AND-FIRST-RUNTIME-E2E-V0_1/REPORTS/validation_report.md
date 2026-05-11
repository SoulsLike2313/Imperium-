# Validation Report

Verdict: PASS
Analyzer regression exit code: 0
Analyzer tracked-dirty regression: False
JSON parse failures: 0
Schema parse failures: 0
Registry path check failures: 0
Forbidden staged path hits: 0

## Git Status --short
```text
 M REGISTRY/ARTIFACT_REGISTRY.json
 M REGISTRY/DYNAMIC_STATE_REGISTRY.json
 M REGISTRY/KNOWN_DEFECTS.json
 M REGISTRY/PORT_REGISTRY.json
 M REGISTRY/SCRIPT_REGISTRY.json
 M TOOLS/astronomicon_pipeline_common_v0_2.ps1
?? ARTIFACTS/TASK-20260511-ASTRONOMICON-V0_7-SYNTHETIC-STARTUP-REPAIR-AND-FIRST-RUNTIME-E2E-V0_1/
?? ARTIFACTS/TASK-20260511-FIRST-RUNTIME-E2E-SMOKE-V0_1/
?? TOOLS/imperium_administratum_issue_work_packet_smoke.ps1
?? TOOLS/imperium_astronomicon_get_task_map_smoke.ps1
?? TOOLS/imperium_doctrinarium_preflight_smoke.ps1
?? TOOLS/imperium_register_stage_result_smoke.ps1
```

## Git Diff --stat
```text
 REGISTRY/ARTIFACT_REGISTRY.json             |  20 ++++-
 REGISTRY/DYNAMIC_STATE_REGISTRY.json        |  24 +++++-
 REGISTRY/KNOWN_DEFECTS.json                 |  33 ++++++--
 REGISTRY/PORT_REGISTRY.json                 |  26 +++++-
 REGISTRY/SCRIPT_REGISTRY.json               | 127 +++++++++++++++++++++++++++-
 TOOLS/astronomicon_pipeline_common_v0_2.ps1 |   5 +-
 6 files changed, 217 insertions(+), 18 deletions(-)

```

## Git Diff --name-status
```text
M	REGISTRY/ARTIFACT_REGISTRY.json
M	REGISTRY/DYNAMIC_STATE_REGISTRY.json
M	REGISTRY/KNOWN_DEFECTS.json
M	REGISTRY/PORT_REGISTRY.json
M	REGISTRY/SCRIPT_REGISTRY.json
M	TOOLS/astronomicon_pipeline_common_v0_2.ps1

```

## Analyzer Status Before
```text
 M REGISTRY/ARTIFACT_REGISTRY.json
 M REGISTRY/DYNAMIC_STATE_REGISTRY.json
 M REGISTRY/KNOWN_DEFECTS.json
 M REGISTRY/PORT_REGISTRY.json
 M REGISTRY/SCRIPT_REGISTRY.json
 M TOOLS/astronomicon_pipeline_common_v0_2.ps1
?? ARTIFACTS/TASK-20260511-ASTRONOMICON-V0_7-SYNTHETIC-STARTUP-REPAIR-AND-FIRST-RUNTIME-E2E-V0_1/
?? ARTIFACTS/TASK-20260511-FIRST-RUNTIME-E2E-SMOKE-V0_1/
?? TOOLS/imperium_administratum_issue_work_packet_smoke.ps1
?? TOOLS/imperium_astronomicon_get_task_map_smoke.ps1
?? TOOLS/imperium_doctrinarium_preflight_smoke.ps1
?? TOOLS/imperium_register_stage_result_smoke.ps1
```

## Analyzer Status After
```text
 M REGISTRY/ARTIFACT_REGISTRY.json
 M REGISTRY/DYNAMIC_STATE_REGISTRY.json
 M REGISTRY/KNOWN_DEFECTS.json
 M REGISTRY/PORT_REGISTRY.json
 M REGISTRY/SCRIPT_REGISTRY.json
 M TOOLS/astronomicon_pipeline_common_v0_2.ps1
?? ARTIFACTS/TASK-20260511-ASTRONOMICON-V0_7-SYNTHETIC-STARTUP-REPAIR-AND-FIRST-RUNTIME-E2E-V0_1/
?? ARTIFACTS/TASK-20260511-FIRST-RUNTIME-E2E-SMOKE-V0_1/
?? TOOLS/imperium_administratum_issue_work_packet_smoke.ps1
?? TOOLS/imperium_astronomicon_get_task_map_smoke.ps1
?? TOOLS/imperium_doctrinarium_preflight_smoke.ps1
?? TOOLS/imperium_register_stage_result_smoke.ps1
```

## JSON Parse Failures
```text
(none)
```

## Schema Parse Failures
```text
(none)
```

## Registry Path Checks
```text
SCRIPT-DOCTRINARIUM-PREFLIGHT-SMOKE-V0_1::TOOLS/imperium_doctrinarium_preflight_smoke.ps1::True
SCRIPT-ASTRONOMICON-GET-TASK-MAP-SMOKE-V0_1::TOOLS/imperium_astronomicon_get_task_map_smoke.ps1::True
SCRIPT-ADMINISTRATUM-ISSUE-WORK-PACKET-SMOKE-V0_1::TOOLS/imperium_administratum_issue_work_packet_smoke.ps1::True
SCRIPT-REGISTER-STAGE-RESULT-SMOKE-V0_1::TOOLS/imperium_register_stage_result_smoke.ps1::True
PORT-RUNNER-DOCTRINARIUM-PREFLIGHT-SMOKE::TOOLS/imperium_doctrinarium_preflight_smoke.ps1::True
PORT-RUNNER-ASTRONOMICON-TASK-STAGE-MAP-SMOKE::TOOLS/imperium_astronomicon_get_task_map_smoke.ps1::True
PORT-RUNNER-ADMINISTRATUM-ISSUE-WORK-PACKET-SMOKE::TOOLS/imperium_administratum_issue_work_packet_smoke.ps1::True
PORT-RUNNER-ADMINISTRATUM-REGISTER-STAGE-RESULT-SMOKE::TOOLS/imperium_register_stage_result_smoke.ps1::True
TASK-20260511-ASTRONOMICON-V0_7-SYNTHETIC-STARTUP-REPAIR-AND-FIRST-RUNTIME-E2E-V0_1::ARTIFACTS/TASK-20260511-ASTRONOMICON-V0_7-SYNTHETIC-STARTUP-REPAIR-AND-FIRST-RUNTIME-E2E-V0_1::True
TASK-20260511-FIRST-RUNTIME-E2E-SMOKE-V0_1::ARTIFACTS/TASK-20260511-FIRST-RUNTIME-E2E-SMOKE-V0_1::True
```

## Forbidden Staged Hits
```text
(none)
```
