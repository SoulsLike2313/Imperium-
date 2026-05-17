# VISUAL FAKE GREEN SCAN V0.1

- task_id: `TASK-SECOND-BRAIN-V07-VISUAL-FAKE-GREEN-SCANNER`
- generated_at: `2026-05-17T01:52:06+00:00`
- current_head: `c448ad30d680eebf1b2857996970b7aa007a52cb`
- scanner_version: `visual_fake_green_scanner_v0_1`
- verdict: `WARN`
- next_recommended_action: `TASK-SECOND-BRAIN-V07-BROWSER-PERFORMANCE-AUDIT-RUNNER`

## Scan Stats
- scanned_files: `36`
- inspected_lines: `48532`
- missing_expected_paths: `0`
- baseline_blocked_reference: `True`
- fps_missing_reference: `True`

## Finding Counts
- HARD_BLOCKER: `0`
- WARNING: `2627`
- REVIEW_REQUIRED: `432`
- ALLOWED_CONTEXT: `4415`
- NOT_APPLICABLE: `0`

## Key Findings
- [WARNING] FG-RULE-001 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css:54 :: --green-glow:    rgba(41, 194, 114, 0.5);
- [WARNING] FG-RULE-001 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css:308 :: .badge-working   { color: var(--green-bright); background: rgba(41,194,114,0.08); border-color: rgba(41,194,114,0.3); }
- [WARNING] FG-RULE-001 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css:315 :: color: var(--green-bright); background: rgba(41,194,114,0.1); border-color: rgba(41,194,114,0.5);
- [WARNING] FG-RULE-001 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css:321 :: 50%       { box-shadow: 0 0 12px var(--green-glow); }
- [WARNING] FG-RULE-001 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css:326 :: background: var(--green-bright);
- [WARNING] FG-RULE-001 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css:327 :: box-shadow: 0 0 10px var(--green-glow), 0 0 20px rgba(41,194,114,0.3);
- [WARNING] FG-RULE-001 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css:335 :: 0%, 100% { opacity: 1; box-shadow: 0 0 10px var(--green-glow); }
- [WARNING] FG-RULE-001 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css:374 :: .stat-num.accent-green   { color: var(--green-bright);   text-shadow: 0 0 12px var(--green-glow); }
- [REVIEW_REQUIRED] FG-RULE-002 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css:2 :: Second Brain Neural Map V0.6 — AAA Visual Pass V0.1
- [REVIEW_REQUIRED] FG-RULE-002 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css:1342 :: animation: launch-btn-ready 3s ease-in-out infinite;
- [REVIEW_REQUIRED] FG-RULE-002 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css:1346 :: @keyframes launch-btn-ready {
- [REVIEW_REQUIRED] FG-RULE-002 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css:1403 :: .verdict-block.ready {
- [REVIEW_REQUIRED] FG-RULE-007 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.js:1231 :: <div class="card-row"><span>Sources missing</span><span class="val" style="color:${zone.source_missing_count > 0 ? 'var(--amber)' : 'var(--green)'}">${zone.source_missing_count}</span></div>
- [REVIEW_REQUIRED] FG-RULE-002 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.js:1692 :: <label>Pass Criteria <span class="req-mark">*</span>
- [REVIEW_REQUIRED] FG-RULE-002 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.js:1693 :: <span class="field-indicator ${d.pass_criteria ? 'filled' : ''}" id="ind-pass"></span>
- [REVIEW_REQUIRED] FG-RULE-002 IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.js:1695 :: <textarea id="c-pass" placeholder="One criterion per line. What counts as success?" rows="3">${esc(d.pass_criteria || '')}</textarea>

## Limitations
- Static text/source scan only; does not execute runtime or backend.
- Context classification is heuristic and may require manual review for borderline phrasing.
- Scanner does not replace truth parity audit or browser performance audit.
- If expected paths are missing, PASS is disallowed.

## Rule Reminder
- This scanner does not replace browser performance audit or truth parity audit.
