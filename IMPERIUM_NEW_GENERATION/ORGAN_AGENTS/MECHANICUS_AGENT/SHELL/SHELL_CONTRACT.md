# SHELL CONTRACT :: MECHANICUS_AGENT

Reference operator shell for Mechanicus must expose real operator context, not help-only smoke output.

Visual Shell V0.2 is summary-first:
- compact operator cards by default;
- raw JSON only on explicit detail requests;
- Mechanicus identity accents and operator palette.

## Supported Shell Commands
- help
- status
- check
- where
- identity
- tools
- pack
- shell --once help
- shell --once status
- shell --once tools
- shell --once identity
- shell --once check
- shell --once raw-status
- shell --once raw-tools
- shell --once raw-identity
- shell --once raw-check
- exit

## Visual Status
- PASS_RICH_OPERATOR_SHELL
- PASS_PLAIN_OPERATOR_SHELL
- WARN_PLAIN_FALLBACK
- BLOCKED_SHELL_NOT_IMPLEMENTED
- FAIL_FAKE_SHELL

## Required Operator Surfaces
- TOP STATUS BAR
- LEFT WORK ZONE
- RIGHT COMMAND ZONE
- TOOL REGISTRY
- BOTTOM EVENT BAR
- renderer mode visibility
- tool registry summary visibility
- command palette visibility
