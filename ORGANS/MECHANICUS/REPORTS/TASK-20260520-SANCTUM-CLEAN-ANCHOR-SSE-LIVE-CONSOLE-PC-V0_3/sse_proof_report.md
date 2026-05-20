# SSE Proof Report

- checked_at_utc: 05/20/2026 15:16:12
- sse_url: http://127.0.0.1:18765/api/events
- heartbeat_received: True
- state_snapshot_received: True
- command_event_received: True
- command_status: PASS
- command_action_id: mechanicus_visual_status
- command_exit_code: 0
- command_duration_ms: 690

## Event Sample
- state_snapshot | source=sanctum_state_builder | status=PASS | command=
- command_started | source=terminal_manual | status=PENDING | command=status
- terminal_entry_added | source=terminal_manual | status=PASS | command=status
- command_finished | source=terminal_manual | status=PASS | command=status
- heartbeat | source=sanctum_sse_gateway | status=PASS | command=

## Limitations
- SSE proof is local-PC runtime only (127.0.0.1:18765).
- Command proof uses allowlisted status command path.
- Full command stdout is truncated to obey report output budget.
