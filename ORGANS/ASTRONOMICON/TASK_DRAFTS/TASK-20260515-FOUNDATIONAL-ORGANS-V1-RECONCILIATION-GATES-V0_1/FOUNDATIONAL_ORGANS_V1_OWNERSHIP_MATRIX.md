# Foundational Organs V1 Ownership Matrix

Canonical ownership boundaries and allowed read/write scopes.

| domain | source_of_truth_owner | may_read | may_write | must_not_decide | required_receipt | dashboard_display_allowed | sanctum_display_allowed | notes |
|---|---|---|---|---|---|---|---|---|
| task_future_memory | Astronomicon | Administratum, Officio Agentis, Doctrinarium, Sanctum | Astronomicon | Sanctum, Officio Agentis, Doctrinarium | astronomicon_memory_update_receipt | true | true | memory registry authority remains in Astronomicon |
| task_scope | Astronomicon | All foundational organs, Sanctum | Astronomicon | Administratum, Officio Agentis, Doctrinarium, Sanctum | task_scope_decision_receipt | true | true | scope changes require owner-approved task records |
| stage_topology | Astronomicon | Administratum, Officio Agentis, Doctrinarium, Sanctum | Astronomicon | Sanctum | stage_map_registration_receipt | true | true | topology is registration-level truth |
| execution_lifecycle | Administratum | Astronomicon, Officio Agentis, Doctrinarium, Sanctum | Administratum | Astronomicon, Sanctum | execution_lifecycle_update_receipt | true | true | execution state transitions owned by Administratum |
| work_packet | Administratum | Astronomicon, Officio Agentis, Doctrinarium | Administratum | Sanctum | work_packet_receipt | true | true | packet schema must be versioned |
| route_sheet | Administratum | Astronomicon, Officio Agentis, Doctrinarium | Administratum | Sanctum | route_sheet_receipt | true | true | route sheet drives stage corridor |
| stage_completion_truth | Administratum | Astronomicon, Officio Agentis, Doctrinarium, Sanctum | Administratum | Sanctum, Officio Agentis | admin_stage_completion_receipt | true | true | stage PASS/BLOCK truth comes from admin receipts |
| final_bundle | Administratum | Astronomicon, Doctrinarium, Officio Agentis, Sanctum | Administratum | Sanctum | final_bundle_manifest | true | true | bundle completeness audited by receipts |
| continuity_pack | Administratum | Astronomicon, Sanctum | Administratum | Sanctum | continuity_pack_receipt | true | true | continuity truth fed from canonical execution artifacts |
| role_contracts | Officio Agentis | Astronomicon, Administratum, Doctrinarium, Sanctum | Officio Agentis | Administratum, Sanctum | role_contract_update_receipt | true | true | contract version pinned and auditable |
| mode_contracts | Officio Agentis | Astronomicon, Administratum, Doctrinarium, Sanctum | Officio Agentis | Sanctum | mode_contract_update_receipt | true | true | mode behavior must match role contract |
| response_contracts | Officio Agentis | Astronomicon, Administratum, Doctrinarium, Sanctum | Officio Agentis | Sanctum | response_contract_receipt | true | true | response envelope must remain deterministic |
| law_registry | Doctrinarium | Astronomicon, Administratum, Officio Agentis, Sanctum | Doctrinarium | Sanctum, Administratum | law_registry_change_receipt | true | true | law entries cannot be edited by dashboard |
| doctrine_registry | Doctrinarium | Astronomicon, Administratum, Officio Agentis, Sanctum | Doctrinarium | Sanctum | doctrine_registry_change_receipt | true | true | canon change requires doctrinarium receipt |
| law_canon_acceptance | Doctrinarium | Astronomicon, Administratum, Officio Agentis | Doctrinarium | Sanctum, Administratum | law_change_receipt | true | true | owner decision still required for acceptance flows |
| organ_health_gate | Doctrinarium | Astronomicon, Administratum, Officio Agentis, Sanctum | Doctrinarium | Sanctum | organ_health_verdict_receipt | true | true | stale health cannot be green |
| task_start_gate | Doctrinarium | Astronomicon, Administratum, Officio Agentis, Sanctum | Doctrinarium | Sanctum | task_start_gate_verdict_receipt | true | true | corridor launch requires gate verdict artifact |
| violations | Doctrinarium | Astronomicon, Administratum, Officio Agentis, Sanctum | Doctrinarium | Sanctum | violation_record_receipt | true | true | inquisition hook remains disabled in V1 |
| dashboard_rendering | Sanctum | All foundational organs | Sanctum | Sanctum | dashboard_render_report | true | true | rendering is presentation-only |
| dashboard_data_adapters | Sanctum | All foundational organs | Sanctum | Sanctum | dashboard_adapter_receipt | true | true | adapters consume canonical reports only |
| dashboard_action_receipts | Administratum | Astronomicon, Officio Agentis, Doctrinarium, Sanctum | Administratum | Sanctum | dashboard_action_receipt | true | true | actions need confirm, timeout, failure receipt |
| sanctum_aggregation | Sanctum | All foundational organs | Sanctum | Sanctum | sanctum_aggregation_report | true | true | aggregation never overrides source truth |
| source_package_manifest | Astronomicon | Administratum, Officio Agentis, Doctrinarium, Sanctum | Astronomicon | Sanctum | source_package_manifest_receipt | true | true | hashes and provenance mandatory |
| evidence_schemas | Doctrinarium | Astronomicon, Administratum, Officio Agentis, Sanctum | Doctrinarium | Sanctum | evidence_schema_change_receipt | true | true | schema gate controls pass criteria |
| receipt_schemas | Doctrinarium | Astronomicon, Administratum, Officio Agentis, Sanctum | Doctrinarium | Sanctum | receipt_schema_change_receipt | true | true | receipt contracts cannot drift silently |
| repo_purity | Administratum | Astronomicon, Officio Agentis, Doctrinarium, Sanctum | Administratum | Sanctum | repo_purity_report | true | true | runtime/local payload separation required |
| git_truth | Astronomicon | All foundational organs, Sanctum | Astronomicon | Sanctum | git_truth_receipt | true | true | git head and branch truth must be explicit |
