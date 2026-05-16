# CLI Agent Port Capability

## Purpose
Provide a machine-readable CLI bridge for health, capability inspection, and sample request summarization.

## Current Status
MVP in test scope.

## What Works Now
- JSON output for required modes.
- Input JSON validation for summarize mode.
- Honest `NOT_IMPLEMENTED` signaling for external execution.

## Foundation Only
- No real remote agent runtime integration.

## Pass-Fail Logic
- Return code `0` for successful command execution and expected `NOT_IMPLEMENTED` paths.
- Return non-zero for invalid input and structural failures.

## Manual Confirmation Required
- Confirm request contract before connecting to production agent adapter.

## Commands
```powershell
python .\STRATEGIC_CAPABILITIES\CLI_AGENT_PORT\imperium_cli_agent_port.py --mode health
python .\STRATEGIC_CAPABILITIES\CLI_AGENT_PORT\imperium_cli_agent_port.py --mode inspect-capabilities
python .\STRATEGIC_CAPABILITIES\CLI_AGENT_PORT\imperium_cli_agent_port.py --mode summarize --input .\STRATEGIC_CAPABILITIES\CLI_AGENT_PORT\sample_request.json
```
