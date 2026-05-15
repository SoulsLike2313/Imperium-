# Schema Baseline Index

This index freezes the minimum schema baseline for V1 hardening execution.

| Schema ID | Owner | Must Exist Before Execution | Stub Allowed |
|---|---|---|---|
| organ_self_report | Doctrinarium | true | false |
| evidence_common | Doctrinarium | true | true |
| receipt_common | Doctrinarium | true | true |
| gate_report | Doctrinarium | true | false |
| work_packet | Administratum | true | false |
| route_sheet | Administratum | true | false |
| stage_map | Astronomicon | true | false |
| stage_record | Administratum | true | false |
| admin_stage_completion_receipt | Administratum | true | false |
| role_contract | Officio Agentis | true | false |
| role_read_receipt | Officio Agentis | false | true |
| law_registry_entry | Doctrinarium | true | false |
| law_change_receipt | Doctrinarium | false | true |
| task_start_gate_verdict | Doctrinarium | true | false |
| dashboard_state | Sanctum | false | true |
| dashboard_actions | Sanctum+Administratum | false | true |
| dashboard_metrics | Sanctum | false | true |
| dashboard_evidence_index | Sanctum | false | true |
| dashboard_render_report | Sanctum | false | true |
| source_package_manifest | Astronomicon | true | false |
| final_bundle_manifest | Administratum | false | true |
| stale_status_report | Doctrinarium+Sanctum | false | true |
| repo_purity_report | Administratum | true | false |
