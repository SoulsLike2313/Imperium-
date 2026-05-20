# SHELL CONTRACT :: MECHANICUS_AGENT

Reference operator shell for Mechanicus must expose real operator context, not help-only smoke output.

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
- BOTTOM EVENT BAR
- renderer mode visibility
- tool registry summary visibility
