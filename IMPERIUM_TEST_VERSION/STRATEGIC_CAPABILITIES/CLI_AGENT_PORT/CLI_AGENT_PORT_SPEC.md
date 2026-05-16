# CLI AGENT PORT SPECIFICATION

**Version:** 1.1.0  
**Status:** MVP FOUNDATION BRIDGE  
**Created:** 2026-05-16

## Purpose
Define a CLI contract for health checks, capability inspection, and sample summarization within test scope.

## Current Status
- Script exists and returns JSON output for required modes.
- Real Codex/Servitor remote execution is **NOT_IMPLEMENTED**.

## What Works Now
- `--mode health` returns runtime and file readiness status.
- `--mode inspect-capabilities` reads capability map and reports status matrix.
- `--mode summarize --input <json>` validates request payload and returns structured summary.

## Foundation Only
- No real external agent dispatch.
- No production queue/transport/auth.

## Pass-Fail Logic
- `PASS`: command runs and JSON status indicates expected operation success.
- `NOT_IMPLEMENTED`: returned for external execution paths not wired by design.
- `FAIL` or `ERROR`: invalid arguments, invalid JSON, missing required input fields.
- Invalid input returns non-zero exit code.

## Manual Confirmation Required
- Confirm contract fields are sufficient for future real integration.
- Confirm expected behavior for owner-specific request types before production adoption.

## Next Steps
1. Bind to real execution adapter.
2. Add schema-level validation library.
3. Add end-to-end tests for request and response contracts.
