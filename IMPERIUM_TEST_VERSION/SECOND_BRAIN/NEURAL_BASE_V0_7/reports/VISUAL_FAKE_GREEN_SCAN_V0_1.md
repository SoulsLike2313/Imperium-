# VISUAL FAKE GREEN SCAN V0.1

- task_id: `TASK-SECOND-BRAIN-V07-VISUAL-FAKE-GREEN-SCANNER`
- generated_at: `2026-05-17T02:14:39+00:00`
- current_head: `6cd43c85fb08f4f8cc556c5992148986a3840685`
- scanner_version: `visual_fake_green_scanner_v0_1`
- verdict: `WARN`
- next_recommended_action: `TASK-SECOND-BRAIN-V07-BROWSER-PERFORMANCE-AUDIT-RUNNER`
- raw_dump_status: `OMITTED_BY_REPORT_BUDGET`

## Scan Stats
- scanned_files: `34`
- inspected_lines: `7719`
- missing_expected_paths: `0`
- skipped_paths_by_budget_count: `0`
- skipped_generated_reports_count: `8`
- baseline_blocked_reference: `True`
- fps_missing_reference: `True`

## Finding Counts
- HARD_BLOCKER: `0`
- WARNING: `45`
- REVIEW_REQUIRED: `26`
- ALLOWED_CONTEXT: `60`
- NOT_APPLICABLE: `0`
- omitted_findings_count: `101`
- allowed_context_count: `60`

## Top Findings
- [WARNING] FG-RULE-001 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css:54 :: --green-glow:    rgba(41, 194, 114, 0.5);
- [WARNING] FG-RULE-001 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css:308 :: .badge-working   { color: var(--green-bright); background: rgba(41,194,114,0.08); border-color: rgba(41,194,114,0.3); }
- [WARNING] FG-RULE-001 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css:315 :: color: var(--green-bright); background: rgba(41,194,114,0.1); border-color: rgba(41,194,114,0.5);
- [WARNING] FG-RULE-001 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css:321 :: 50%       { box-shadow: 0 0 12px var(--green-glow); }
- [WARNING] FG-RULE-001 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css:326 :: background: var(--green-bright);
- [WARNING] FG-RULE-001 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css:327 :: box-shadow: 0 0 10px var(--green-glow), 0 0 20px rgba(41,194,114,0.3);
- [WARNING] FG-RULE-001 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css:335 :: 0%, 100% { opacity: 1; box-shadow: 0 0 10px var(--green-glow); }
- [WARNING] FG-RULE-001 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css:374 :: .stat-num.accent-green   { color: var(--green-bright);   text-shadow: 0 0 12px var(--green-glow); }
- [WARNING] FG-RULE-001 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css:388 :: text-shadow: 0 0 12px var(--green-glow), 0 0 24px rgba(41,194,114,0.2);
- [WARNING] FG-RULE-001 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css:458 :: .freshness-val[data-state="FRESH"]   { color: var(--green-bright); text-shadow: 0 0 8px var(--green-glow); }
- [WARNING] FG-RULE-001 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css:878 :: .tel-chip.good  { color: var(--green-bright);   background: rgba(41,194,114,0.08);  border-color: rgba(41,194,114,0.25); }
- [WARNING] FG-RULE-001 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css:1283 :: background: var(--green-bright); border-color: var(--green);
- [WARNING] FG-RULE-001 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css:1284 :: box-shadow: 0 0 8px var(--green-glow);
- [WARNING] FG-RULE-001 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css:1320 :: background: rgba(41,194,114,0.08); border-color: rgba(41,194,114,0.38); color: var(--green-bright);
- [WARNING] FG-RULE-001 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css:1515 :: background: rgba(41,194,114,0.12); border-color: rgba(41,194,114,0.5); color: var(--green-bright);
- [WARNING] FG-RULE-001 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.html:159 :: <filter id="glow-green"   x="-80%" y="-80%" width="260%" height="260%">
- [WARNING] FG-RULE-001 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.js:84 :: "#29c272": "url(#glow-green)",
- [WARNING] FG-RULE-001 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.js:563 :: filter: isWorking ? "url(#glow-green)" : ""
- [WARNING] FG-RULE-001 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.js:1230 :: <div class="card-row"><span>Sources present</span><span class="val" style="color:var(--green)">${zone.source_present_count}</span></div>
- [WARNING] FG-RULE-001 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.js:1231 :: <div class="card-row"><span>Sources missing</span><span class="val" style="color:${zone.source_missing_count > 0 ? 'var(--amber)' : 'var(--green)'}">${zone.source_missing_count}</span></div>

## Top Rules By Count
- FG-RULE-001: `64`
- FG-RULE-002: `23`
- FG-RULE-008: `18`
- FG-RULE-003: `12`
- FG-RULE-007: `10`
- FG-RULE-004: `3`
- FG-RULE-006: `1`

## Top Paths By Count
- IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.js: `22`
- IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css: `19`
- IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/server_v0_6.py: `17`
- IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/VISUAL_SYSTEM/FAKE_GREEN_VISUAL_RULES_V0_1.md: `14`
- IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/PERFORMANCE_BASELINE_INTERPRETATION_V0_1.md: `8`
- IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/PERFORMANCE_BASELINE_INTERPRETATION_V0_1.json: `6`
- IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/PERFORMANCE_BLOCKER_MAP_V0_1.md: `5`
- IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/VISUAL_PERFORMANCE_RECEIPT_V0_1.json: `5`
- IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/PERFORMANCE_BLOCKER_MAP_V0_1.json: `4`
- IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.html: `3`
- omitted_paths_count: `0`

## Limitations
- Static text/source scan only; does not execute runtime or backend.
- Context classification is heuristic and may require manual review.
- Scanner does not replace truth parity audit or browser performance audit.
- Generated reports are compacted by budget; raw unlimited dump is omitted by default.
- Some large report files are intentionally skipped to prevent recursive output avalanche.
