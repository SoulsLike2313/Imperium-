# SCRIPT ARTIFACT PRESERVATION REPORT

- task_id: TASK-20260520-SANCTUM-CLEAN-ANCHOR-SSE-LIVE-CONSOLE-PC-V0_3
- generated_at_utc: 2026-05-20T15:22:08.9821606Z

## Artifacts
- artifact_id: sse_proof_check_py
  - path: ORGANS/MECHANICUS/REPORTS/TASK-20260520-SANCTUM-CLEAN-ANCHOR-SSE-LIVE-CONSOLE-PC-V0_3/sse_proof_check.py
  - purpose: Verify SSE stream receives heartbeat + state_snapshot + command event.
  - classification: KEEP_LOCAL_ONLY
  - recommendation: Reuse as task-local checker template for future Sanctum SSE gates.

- artifact_id: playwright_capture_and_probe_mjs
  - path: ORGANS/MECHANICUS/REPORTS/TASK-20260520-SANCTUM-CLEAN-ANCHOR-SSE-LIVE-CONSOLE-PC-V0_3/playwright_capture_and_probe.mjs
  - purpose: Capture required screenshots and collect compact UI performance probe.
  - classification: BUFFER_FOR_SCRIPTORIUM_REVIEW
  - recommendation: Candidate for absorption as reusable Sanctum visual-audit script.

## Notes
- Raw runtime payloads (
ode_modules, raw SSE dump) were intentionally excluded from final bundle to obey report output budget.
- Reproducibility dependencies are documented via package.json + package-lock.json in this task bundle.
