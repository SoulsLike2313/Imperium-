# Visual Evidence Index

- generated_at_utc: 2026-05-20T15:19:59.4489593Z
- source_report: playwright_capture_report.json
- sse_status_visible: SSE CONNECTED
## 01_sanctum_overview_brain_shell.png
- proves: Overview brain shell layout exists with explicit organ cards.
- does_not_prove: Does not prove SSE delivery by itself.
- known_gaps: No human visual review on real owner display yet.

## 02_live_operator_console_redesign.png
- proves: LIVE view is operator-console styled, not tiny raw terminal box.
- does_not_prove: Does not prove command pipeline without execution event.
- known_gaps: Aesthetic quality can still be improved.

## 03_live_operator_console_after_status.png
- proves: Operator console updates after allowlisted status command.
- does_not_prove: Does not prove every command path.
- known_gaps: Only one command path sampled.

## 04_sse_connection_visible_state.png
- proves: Visible SSE status indicator exists and shows current mode.
- does_not_prove: Does not prove all SSE event types.
- known_gaps: Indicator screenshot is pill-focused, not full panel context.

## 05_raw_terminal_technical_view.png
- proves: RAW technical mode is preserved in LIVE panel.
- does_not_prove: Does not prove long history persistence.
- known_gaps: Captured with finite sample output.

## 06_evidence_tab.png
- proves: EVIDENCE tab is reachable and rendered.
- does_not_prove: Does not prove screenshot file freshness semantics.
- known_gaps: Depends on existing mechanicus screenshot inventory.

## 07_reports_tab.png
- proves: REPORTS tab is reachable and shows backend-bound report paths.
- does_not_prove: Does not prove all listed paths exist on disk at owner check time.
- known_gaps: Path existence can change after cleanup.

## 08_raw_json_tab.png
- proves: RAW JSON tab is reachable and displays machine payload.
- does_not_prove: Does not prove schema completeness outside displayed slice.
- known_gaps: Payload is truncated for UI safety.

## 09_action_history_tab.png
- proves: ACTION HISTORY tab is reachable and displays executed/blocked entries.
- does_not_prove: Does not prove historical completeness before current runtime start.
- known_gaps: History window is bounded.

