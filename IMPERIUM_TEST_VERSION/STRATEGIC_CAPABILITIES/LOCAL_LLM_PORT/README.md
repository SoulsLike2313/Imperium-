# Local LLM Port Capability

## Purpose
Provide a safe foundation for checking whether a local LLM runtime is configured and executable.

## Current Status
FOUNDATION / HEALTH_CHECK_ONLY.

## What Works Now
- Model profile schema exists.
- Request/response schemas exist.
- Config template exists.
- `local_llm_health_check.py` returns honest JSON status.

## Foundation Only / Not Implemented
- No real prompt inference routing.
- No guaranteed model installation.
- No integration with CLI agent execution path.

## Pass-Fail Logic
- `PASS`: configured command exists and safe probe command exits `0`.
- `NOT_CONFIGURED`: model command is empty/template.
- `NOT_INSTALLED`: configured command is not found.
- `FAIL`: config invalid or probe fails.

## Manual Confirmation Required
- Owner configures a real local model command.
- Owner confirms safe probe output for the intended model runtime.

## Key Files
- `LOCAL_LLM_PORT_SPEC.md`
- `local_llm_profile.schema.json`
- `local_llm_request.schema.json`
- `local_llm_response.schema.json`
- `local_llm_config.template.json`
- `local_llm_health_check.py`

## Next Steps
1. Configure a concrete local model command.
2. Run health check and archive JSON evidence.
3. Implement real request/response execution port.
