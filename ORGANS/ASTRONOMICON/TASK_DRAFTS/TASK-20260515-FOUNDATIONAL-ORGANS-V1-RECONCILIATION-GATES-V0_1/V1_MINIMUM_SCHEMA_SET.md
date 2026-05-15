# V1 Minimum Schema Set

Minimum schema/contracts baseline needed for foundational organs V1 hardening.

| schema_id | owner | why_needed | v1_minimum_fields | produced_by | consumed_by | must_exist_before_execution | can_be_stub_in_v1 | defer_notes |
|---|---|---|---|---|---|---|---|---|
| organ_self_report | Doctrinarium | freshness and organ health evaluation input | schema_version,organ_id,generated_at_utc,checker_last_run_utc,status,evidence_paths | Doctrinarium | Doctrinarium,Administratum,Sanctum | true | false | already available in MVP base |
| evidence_common | Doctrinarium | normalize evidence metadata | schema_version,evidence_id,generated_at_utc,git_head,source_hash,evidence_paths | Doctrinarium | All organs | true | true | can start as thin wrapper |
| receipt_common | Doctrinarium | normalize receipt envelope | schema_version,receipt_id,task_id,stage_id,verdict,timestamp_utc,evidence_paths | Doctrinarium | All organs | true | true | must be frozen before stage receipts |
| gate_report | Doctrinarium | standard gate PASS/STOP output | schema_version,gate_id,verdict,blockers,warnings,evidence_paths,checked_at_utc | Doctrinarium | Astronomicon,Administratum,Sanctum | true | false | required for gate index execution |
| work_packet | Administratum | execute bounded work slice | schema_version,task_id,local_task_id,stage_id,inputs,outputs,constraints | Administratum | Servitor lane | true | false | must map to ownership matrix |
| route_sheet | Administratum | describe stage routing and transitions | schema_version,task_id,route_steps,current_step,next_step | Administratum | Administratum,Sanctum | true | false | corridor truth contract |
| stage_map | Astronomicon | canonical stage dependency map | schema_version,task_id,stages,depends_on,pass_criteria,stop_criteria | Astronomicon | Administratum,Doctrinarium,Officio | true | false | pre-launch mandatory |
| stage_record | Administratum | record stage execution outcome | schema_version,stage_id,status,started_utc,completed_utc,checker_results,evidence_paths | Administratum | Astronomicon,Sanctum | true | false | replaces chat-memory truth |
| admin_stage_completion_receipt | Administratum | formal stage completion proof | schema_version,receipt_id,stage_id,status,evidence_paths,timestamp_utc | Administratum | Astronomicon,Sanctum | true | false | must exist for every stage |
| role_contract | Officio Agentis | agent role/mode contract control | schema_version,role_id,modes,constraints,owner,version | Officio Agentis | Administratum,Sanctum | true | false | contract compliance must be testable |
| role_read_receipt | Officio Agentis | proof role contract was read | schema_version,receipt_id,role_id,reader,read_utc,git_head | Officio Agentis | Administratum,Doctrinarium | false | true | can be stubbed first then enforced |
| law_registry_entry | Doctrinarium | canonical law entry representation | schema_version,law_id,status,title,provenance,timestamp_utc | Doctrinarium | Administratum,Sanctum | true | false | no advisory auto-promotion |
| law_change_receipt | Doctrinarium | track law registry mutation | schema_version,receipt_id,law_id,change_type,reason,timestamp_utc | Doctrinarium | Astronomicon,Sanctum | false | true | needed before canon elevation |
| task_start_gate_verdict | Doctrinarium | allow/block execution admission | schema_version,task_id,verdict,allow_execution,reasons,evidence_paths | Doctrinarium | Administratum,Sanctum | true | false | mandatory corridor gate |
| dashboard_state | Sanctum | renderable dashboard truth state | schema_version,panel_id,status,source_report,stale_status,generated_at_utc | Sanctum | Owner display | false | true | must map to backend reports |
| dashboard_actions | Sanctum+Administratum | action button contract | schema_version,action_id,allowed_roles,confirmation_required,timeout_seconds,receipt_schema | Sanctum+Administratum | Owner display,Administratum | false | true | no action without receipt |
| dashboard_metrics | Sanctum | display metrics surface | schema_version,metric_id,value,source_report,checked_at_utc | Sanctum | Owner display | false | true | truth over animation |
| dashboard_evidence_index | Sanctum | index report links behind UI | schema_version,index_id,evidence_items,generated_at_utc | Sanctum | Owner display | false | true | supports no-fake-green audits |
| dashboard_render_report | Sanctum | prove render sources and staleness | schema_version,render_id,panels_rendered,source_reports,stale_panels | Sanctum | Administratum,Owner | false | true | must include disabled reasons where relevant |
| source_package_manifest | Astronomicon | frozen planning source inventory | schema_version,task_id,sources,sha256,read_utc,git_head_used | Astronomicon | All organs | true | false | launch precondition |
| final_bundle_manifest | Administratum | final evidence bundle completeness | schema_version,bundle_id,artifacts,hashes,created_utc | Administratum | Astronomicon,Owner | false | true | required for certification stage |
| stale_status_report | Doctrinarium+Sanctum | freshness evaluation output | schema_version,artifact_id,generated_at_utc,expires_after_seconds,stale_status | Doctrinarium+Sanctum | Dashboards and gates | false | true | stale cannot be green |
| repo_purity_report | Administratum | scope and pollution check | schema_version,git_head,allowed_paths,violations,verdict,timestamp_utc | Administratum | Owner and gates | true | false | prevents runtime payload leakage |
