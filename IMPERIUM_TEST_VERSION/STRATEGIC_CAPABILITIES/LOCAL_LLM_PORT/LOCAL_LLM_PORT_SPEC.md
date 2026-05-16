# LOCAL LLM PORT SPECIFICATION

**Version:** 1.1.0  
**Status:** FOUNDATION  
**Created:** 2026-05-16

## Purpose
Define the minimal, honest contract for local LLM readiness checks in IMPERIUM test scope.

## Current Status
- Implemented level: `HEALTH_CHECK_ONLY`.
- Real inference execution: **NOT_IMPLEMENTED**.

## What Works Now
- Local model profile schema (`local_llm_profile.schema.json`).
- Request/response schemas (`local_llm_request.schema.json`, `local_llm_response.schema.json`).
- Config template for local execution contract.
- Health check script that reports `NOT_CONFIGURED`, `NOT_INSTALLED`, `PASS`, or `FAIL` without fake green.

## Foundation Only
- Prompt execution pipeline is not wired.
- No automatic model install.
- No production routing or security hardening.

## Pass-Fail Logic
- `PASS`: configured model command is resolvable and safe probe command returns exit code `0`.
- `NOT_CONFIGURED`: command is empty or template placeholder.
- `NOT_INSTALLED`: command configured but executable not found.
- `FAIL`: invalid JSON config, probe timeout, or non-zero probe exit.

## Manual Confirmation Required
- Confirm local model binary/runtime is installed.
- Confirm configured command is safe and expected.
- Confirm inference quality separately from health probe.

## Next Steps
1. Owner provides real config values.
2. Run health check and archive output receipt.
3. Add real local inference runner and integration tests.
