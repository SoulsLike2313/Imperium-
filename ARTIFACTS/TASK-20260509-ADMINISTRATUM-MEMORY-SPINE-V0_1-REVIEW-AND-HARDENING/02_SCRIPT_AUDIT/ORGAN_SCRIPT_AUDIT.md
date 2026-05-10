# ORGAN SCRIPT AUDIT

## E:\IMPERIUM\ORGANS\DOCTRINARIUM\SCRIPTS\doctrinarium_preflight.py
- exists: True
- sha256: 9647f751ba45834ec00ceb18146311f51e5b5c98a10ead6c869f7d4fc7f91f4c
- size_bytes: 5726
- modified_utc: 2026-05-09T15:11:39.085824+00:00
- purpose: Doctrinarium preflight: validate laws/doctrine presence and emit receipt 00.
- inputs_inferred: --recipe-path, --root, --run-id, --task-id
- outputs_inferred: E:\IMPERIUM
- forbidden_actions_found: not found
- writes_outside_allowed_roots: False
- scans_archive: False
- touches_sanctum: False
- contacts_network: False
- starts_background_jobs: False
- has_schema_version_literal: True
- writes_receipts: True
- exits_non_zero_on_hard_failure_evidence: True
- risk_level: OK
- risks:
  - none

## E:\IMPERIUM\ORGANS\OFFICIO_AGENTIS\SCRIPTS\officio_agentis_scope.py
- exists: True
- sha256: f94ca72fee266884fdf9b48bb5370626881e9afe7f0b264184073f751c694aed
- size_bytes: 4125
- modified_utc: 2026-05-09T14:52:28.417923+00:00
- purpose: Build task-specific agent scope and emit receipt 01.
- inputs_inferred: --recipe-path, --root, --run-id, --task-id
- outputs_inferred: E:\IMPERIUM
- forbidden_actions_found: sanctum_touch:token_detected
- writes_outside_allowed_roots: False
- scans_archive: False
- touches_sanctum: True
- contacts_network: False
- starts_background_jobs: False
- has_schema_version_literal: True
- writes_receipts: True
- exits_non_zero_on_hard_failure_evidence: False
- risk_level: OK
- risks:
  - none

## E:\IMPERIUM\ORGANS\ADMINISTRATUM\SCRIPTS\administratum_record_event.py
- exists: True
- sha256: 40fb571886d48d8940ebe2ccc9d61532108fb5febb299be2faa8b528d5eda7eb
- size_bytes: 4318
- modified_utc: 2026-05-09T14:54:20.817094+00:00
- purpose: Append context event to memory JSONL and emit receipt 02.
- inputs_inferred: --actor, --event-type, --organ, --output-paths, --receipt-paths, --root, --run-id, --summary-ru, --task-id, --verdict
- outputs_inferred: E:\IMPERIUM
- forbidden_actions_found: not found
- writes_outside_allowed_roots: False
- scans_archive: False
- touches_sanctum: False
- contacts_network: False
- starts_background_jobs: False
- has_schema_version_literal: True
- writes_receipts: True
- exits_non_zero_on_hard_failure_evidence: False
- risk_level: OK
- risks:
  - none

## E:\IMPERIUM\ORGANS\ADMINISTRATUM\SCRIPTS\administratum_build_current_state.py
- exists: True
- sha256: 0425aa83d60df7b478ff22ccdb187a895977b35150cb2a165e2de7f339359bd6
- size_bytes: 6114
- modified_utc: 2026-05-09T14:54:20.818070+00:00
- purpose: Build TASK CURRENT_STATE and emit receipt 07.
- inputs_inferred: --root, --run-id, --task-id
- outputs_inferred: E:\IMPERIUM
- forbidden_actions_found: sanctum_touch:token_detected
- writes_outside_allowed_roots: False
- scans_archive: False
- touches_sanctum: True
- contacts_network: False
- starts_background_jobs: False
- has_schema_version_literal: True
- writes_receipts: True
- exits_non_zero_on_hard_failure_evidence: False
- risk_level: OK
- risks:
  - none

## E:\IMPERIUM\ORGANS\ADMINISTRATUM\SCRIPTS\administratum_view_task_timeline.py
- exists: True
- sha256: 165a391952a8bffb7795694b59470238b658f34bfbd8fcac5c4e79a0153ce131
- size_bytes: 845
- modified_utc: 2026-05-09T14:54:20.820023+00:00
- purpose: Read-only timeline viewer utility.
- inputs_inferred: --root, --task-id
- outputs_inferred: E:\IMPERIUM
- forbidden_actions_found: not found
- writes_outside_allowed_roots: False
- scans_archive: False
- touches_sanctum: False
- contacts_network: False
- starts_background_jobs: False
- has_schema_version_literal: False
- writes_receipts: False
- exits_non_zero_on_hard_failure_evidence: False
- risk_level: OK
- risks:
  - Utility script does not emit receipt by design.

## E:\IMPERIUM\ORGANS\ADMINISTRATUM\SCRIPTS\administratum_build_continuity_candidate.py
- exists: True
- sha256: 158a928300a2ae6da5199c2dfa5029b721ee88dd1a2555b329611583715c9c1d
- size_bytes: 5106
- modified_utc: 2026-05-09T15:11:19.462430+00:00
- purpose: Build continuity candidate MD/JSON and emit receipt 08.
- inputs_inferred: --root, --run-id, --task-id
- outputs_inferred: E:\IMPERIUM
- forbidden_actions_found: sanctum_touch:token_detected
- writes_outside_allowed_roots: False
- scans_archive: False
- touches_sanctum: True
- contacts_network: False
- starts_background_jobs: False
- has_schema_version_literal: True
- writes_receipts: True
- exits_non_zero_on_hard_failure_evidence: True
- risk_level: OK
- risks:
  - none

## E:\IMPERIUM\ORGANS\ADMINISTRATUM\SCRIPTS\imperium_task_start.ps1
- exists: True
- sha256: e1933d5b2b7cbeda1f34835ed7e81044825b13165e62682502c175280ff30aae
- size_bytes: 5335
- modified_utc: 2026-05-09T14:57:20.799878+00:00
- purpose: Entrypoint orchestrating ordered organ-gated execution chain.
- inputs_inferred: --actor, --event-type, --organ, --receipt-paths, --recipe-path, --root, --run-id, --stage-id, --summary-ru, --task-id, --verdict
- outputs_inferred: E:\IMPERIUM, E:\IMPERIUM\ORGANS\ADMINISTRATUM\SCRIPTS\administratum_build_continuity_candidate.py, E:\IMPERIUM\ORGANS\ADMINISTRATUM\SCRIPTS\administratum_build_current_state.py, E:\IMPERIUM\ORGANS\ADMINISTRATUM\SCRIPTS\administratum_record_event.py, E:\IMPERIUM\ORGANS\ASTRONOMICON\SCRIPTS\astronomicon_load_route.py, E:\IMPERIUM\ORGANS\DOCTRINARIUM\SCRIPTS\doctrinarium_preflight.py, E:\IMPERIUM\ORGANS\INQUISITION\SCRIPTS\inquisition_post_stage_audit.py, E:\IMPERIUM\ORGANS\MECHANICUS\SCRIPTS\mechanicus_dummy_stage.py, E:\IMPERIUM\ORGANS\MECHANICUS\SCRIPTS\mechanicus_resolve_scripts.py, E:\IMPERIUM\ORGANS\OFFICIO_AGENTIS\SCRIPTS\officio_agentis_scope.py
- forbidden_actions_found: not found
- writes_outside_allowed_roots: False
- scans_archive: False
- touches_sanctum: False
- contacts_network: False
- starts_background_jobs: False
- has_schema_version_literal: False
- writes_receipts: True
- exits_non_zero_on_hard_failure_evidence: True
- risk_level: OK
- risks:
  - none

## E:\IMPERIUM\ORGANS\ASTRONOMICON\SCRIPTS\astronomicon_load_route.py
- exists: True
- sha256: 35127a3871fb742965d5b9027a38c66a1c40d86a63249abaab307737f3e5b640
- size_bytes: 4102
- modified_utc: 2026-05-09T14:55:01.589322+00:00
- purpose: Validate and load stage map/criteria; emit receipt 03.
- inputs_inferred: --root, --run-id, --task-id
- outputs_inferred: E:\IMPERIUM, E:\IMPERIUM\ARCHIVE, E:\IMPERIUM\SANCTUM, E:\IMPERIUM\THRONE
- forbidden_actions_found: sanctum_touch:token_detected
- writes_outside_allowed_roots: False
- scans_archive: False
- touches_sanctum: True
- contacts_network: False
- starts_background_jobs: False
- has_schema_version_literal: True
- writes_receipts: True
- exits_non_zero_on_hard_failure_evidence: False
- risk_level: OK
- risks:
  - none

## E:\IMPERIUM\ORGANS\MECHANICUS\SCRIPTS\mechanicus_resolve_scripts.py
- exists: True
- sha256: 7d27fbcd67f33895d0cafde0fcbfb9a8ed1e038eca728e97a50a71c71747155e
- size_bytes: 4063
- modified_utc: 2026-05-09T14:55:48.568225+00:00
- purpose: Resolve stage script by registry and emit receipt 04.
- inputs_inferred: --root, --run-id, --task-id
- outputs_inferred: E:\IMPERIUM
- forbidden_actions_found: not found
- writes_outside_allowed_roots: False
- scans_archive: False
- touches_sanctum: False
- contacts_network: False
- starts_background_jobs: False
- has_schema_version_literal: True
- writes_receipts: True
- exits_non_zero_on_hard_failure_evidence: False
- risk_level: OK
- risks:
  - none

## E:\IMPERIUM\ORGANS\MECHANICUS\SCRIPTS\mechanicus_dummy_stage.py
- exists: True
- sha256: 5f97685593408117d304e94dd353d85184dc2e8514f4ed4ea4dd6178de8a59c4
- size_bytes: 2553
- modified_utc: 2026-05-09T14:55:48.569202+00:00
- purpose: Execute safe dummy stage output and emit receipt 05.
- inputs_inferred: --root, --run-id, --stage-id, --task-id
- outputs_inferred: E:\IMPERIUM
- forbidden_actions_found: not found
- writes_outside_allowed_roots: False
- scans_archive: False
- touches_sanctum: False
- contacts_network: False
- starts_background_jobs: False
- has_schema_version_literal: True
- writes_receipts: True
- exits_non_zero_on_hard_failure_evidence: False
- risk_level: OK
- risks:
  - none

## E:\IMPERIUM\ORGANS\INQUISITION\SCRIPTS\inquisition_post_stage_audit.py
- exists: True
- sha256: 5fc6b4d43b267e939135d3a92155aeeca68e5c02d820e98ad02b6d5df1e9a4e8
- size_bytes: 10271
- modified_utc: 2026-05-09T15:15:00.892062+00:00
- purpose: Post-stage audit checks and emit receipt 06.
- inputs_inferred: --enforce-extended-checks, --review-package-root, --root, --run-id, --task-id
- outputs_inferred: E:\IMPERIUM
- forbidden_actions_found: archive_scan:pattern_detected
- writes_outside_allowed_roots: False
- scans_archive: True
- touches_sanctum: False
- contacts_network: False
- starts_background_jobs: False
- has_schema_version_literal: True
- writes_receipts: True
- exits_non_zero_on_hard_failure_evidence: False
- risk_level: OK
- risks:
  - none

## E:\IMPERIUM\PC_ENGINEERING_ROOM\SCRIPTS\imperium_task_start.ps1
- exists: True
- sha256: e1933d5b2b7cbeda1f34835ed7e81044825b13165e62682502c175280ff30aae
- size_bytes: 5335
- modified_utc: 2026-05-09T14:57:20.799878+00:00
- purpose: Entrypoint orchestrating ordered organ-gated execution chain.
- inputs_inferred: --actor, --event-type, --organ, --receipt-paths, --recipe-path, --root, --run-id, --stage-id, --summary-ru, --task-id, --verdict
- outputs_inferred: E:\IMPERIUM, E:\IMPERIUM\ORGANS\ADMINISTRATUM\SCRIPTS\administratum_build_continuity_candidate.py, E:\IMPERIUM\ORGANS\ADMINISTRATUM\SCRIPTS\administratum_build_current_state.py, E:\IMPERIUM\ORGANS\ADMINISTRATUM\SCRIPTS\administratum_record_event.py, E:\IMPERIUM\ORGANS\ASTRONOMICON\SCRIPTS\astronomicon_load_route.py, E:\IMPERIUM\ORGANS\DOCTRINARIUM\SCRIPTS\doctrinarium_preflight.py, E:\IMPERIUM\ORGANS\INQUISITION\SCRIPTS\inquisition_post_stage_audit.py, E:\IMPERIUM\ORGANS\MECHANICUS\SCRIPTS\mechanicus_dummy_stage.py, E:\IMPERIUM\ORGANS\MECHANICUS\SCRIPTS\mechanicus_resolve_scripts.py, E:\IMPERIUM\ORGANS\OFFICIO_AGENTIS\SCRIPTS\officio_agentis_scope.py
- forbidden_actions_found: not found
- writes_outside_allowed_roots: False
- scans_archive: False
- touches_sanctum: False
- contacts_network: False
- starts_background_jobs: False
- has_schema_version_literal: False
- writes_receipts: True
- exits_non_zero_on_hard_failure_evidence: True
- risk_level: OK
- risks:
  - none

