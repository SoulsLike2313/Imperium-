# Truth Parity Matrix V0.1

Generated: 2026-05-16T17:55:25Z

| # | Claim | DOM | API | Backend | Status | Notes |
|---|---|---|---|---|---|---|
| 1 | total task count | #stat-tasks=4 | /api/status=4 | IMPERIUM_TEST_VERSION/SECOND_BRAIN/MEMORY_ZONES/TASK_INTAKE/accepted_tasks.json=4 | TRUE |  |
| 2 | total comment count | #stat-comments=4 | /api/status=4 | IMPERIUM_TEST_VERSION/SECOND_BRAIN/MEMORY_ZONES/OWNER_COMMENTS/owner_comments_runtime.json=4 | TRUE |  |
| 3 | total link count | #stat-links=4 | /api/status=4 | IMPERIUM_TEST_VERSION/SECOND_BRAIN/MEMORY_ZONES/MEMORY_LINKS/task_comment_links.json=4 | TRUE |  |
| 4 | total receipt count | #stat-receipts=12 | /api/status=12 | IMPERIUM_TEST_VERSION/SECOND_BRAIN/RUNTIME/receipts=12 | TRUE |  |
| 5 | health score | #health-score=9/12 | /api/status + /api/snapshot=9/12 | IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_5/reports/neural_snapshot_live.json=9/12 | TRUE |  |
| 6 | 12 zone labels | zone_labels_count=12 | /api/snapshot.zones[].display_name=12 | IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_5/reports/neural_snapshot_live.json=12 | TRUE | DOM labels are uppercase/transformed, compared by zone_id coverage. |
| 7 | 12 zone status states | zone_detail_panel Health row text | /api/snapshot.zones[].health=from zone detail panel | IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_5/reports/neural_snapshot_live.json=health values per zone | TRUE |  |
| 8 | 12 zone tooltip telemetry | zone tooltip summary/telemetry text | /api/snapshot.zones[].hover_summary_template + telemetry=tooltips=12 | IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_5/reports/neural_snapshot_live.json=telemetry + summary templates | PARTIAL | Placeholder tokens remain unresolved for at least one zone. |
| 9 | operator panel values for each zone | zone detail panel body text for 12 zones | /api/snapshot.zones[*]=12 | IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_5/reports/neural_snapshot_live.json=12 | TRUE |  |
| 10 | active links list | operator panel links tab text | /api/links=4 | IMPERIUM_TEST_VERSION/SECOND_BRAIN/MEMORY_ZONES/MEMORY_LINKS/task_comment_links.json=4 | TRUE |  |
| 11 | memory thread data | thread panel content | /api/thread/TI-20260516-174836-211=thread payload includes task/comments/receipts | IMPERIUM_TEST_VERSION/SECOND_BRAIN/MEMORY_ZONES/TASK_INTAKE/accepted_tasks.json=thread references created task/comment/link | TRUE |  |
| 12 | evidence panel data | evidence panel text block | /api/snapshot={'health_score': '9/12', 'warning_count': 3} | IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_5/reports/neural_snapshot_live.json={'health_score': '9/12', 'warning_count': 3} | TRUE |  |
| 13 | snapshot timestamp | Evidence panel Timestamp row | /api/snapshot.timestamp_utc=2026-05-16T17:48:39Z | IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_5/reports/neural_snapshot_live.json=2026-05-16T17:54:56Z | PARTIAL |  |
| 14 | partial zone count | Inferred from map health badges | /api/snapshot.partial_count=3 | IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_5/reports/neural_snapshot_live.json=3 | PARTIAL | No dedicated numeric DOM counter; inferred from zone statuses. |
| 15 | blocked/missing zone count | Inferred from map health badges | /api/snapshot.blocked_count + total_missing_sources={'blocked_count': 0, 'missing_sources': 0} | IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_5/reports/neural_snapshot_live.json={'blocked_count': 0, 'missing_sources': 0} | PARTIAL | No dedicated DOM counter; values only in snapshot/evidence panel. |
| 16 | warnings count | Core tooltip and evidence panel | /api/snapshot.warning_count=3 | IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_5/reports/neural_snapshot_live.json=3 | TRUE |  |
| 17 | export readiness | export_bundle_gate tooltip/detail | /api/snapshot.zones[export_bundle_gate].telemetry.gate_status=READY | IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_5/reports/neural_snapshot_live.json=READY | TRUE |  |
| 18 | NO_LOCAL_LLM | header/footer badge text | /api/status.no_local_llm=true | IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_5/reports/neural_snapshot_live.json=true | TRUE |  |
| 19 | NO_AGENT_API | header/footer badge text | /api/status.no_agent_api=true | IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_5/reports/neural_snapshot_live.json=true | TRUE |  |
| 20 | RULE_BASED_ONLY | header badge + runtime status | /api/status.rule_based=true | IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_5/reports/neural_snapshot_live.json=PROTOTYPE_INTERACTIVE | TRUE |  |
| 21 | PROTOTYPE_INTERACTIVE / NOT_PROD_READY | header/footer honesty labels | /api/status.mode + /api/status.not_production_ready={'mode': 'PROTOTYPE_INTERACTIVE', 'not_production_ready': True} | IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_5/reports/neural_snapshot_live.json={'runtime_mode': 'PROTOTYPE_INTERACTIVE', 'not_production_ready': True} | TRUE |  |

## Counts

- TRUE: 17
- PARTIAL: 4
- FALSE: 0
- STALE: 0
- UNPROVEN: 0
- STATIC_LABEL_ONLY: 0
- NOT_APPLICABLE: 0