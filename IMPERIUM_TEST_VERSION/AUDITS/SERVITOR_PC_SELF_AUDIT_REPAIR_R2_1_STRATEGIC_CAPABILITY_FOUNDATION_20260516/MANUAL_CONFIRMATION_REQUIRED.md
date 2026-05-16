# MANUAL CONFIRMATION REQUIRED

1. Local LLM runtime
- Configure a real model command in `STRATEGIC_CAPABILITIES/LOCAL_LLM_PORT/local_llm_config.template.json` (or external config).
- Re-run `python .\\STRATEGIC_CAPABILITIES\\LOCAL_LLM_PORT\\local_llm_health_check.py` until `PASS`.

2. Ubuntu laptop contour
- Run non-dry SSH probe with valid parameters:
  - `-HostName`
  - `-User`
  - `-KeyPath`
  - optional `-DryRun:$false`
- Confirm `PASS` in JSON receipt.

3. Delta infrastructure
- Investigate truth FAIL (Master Verification).
- Fix mojibake scan crash in `AGENT_EXCHANGE\\TOOLS\\mojibake_scan.py`.
