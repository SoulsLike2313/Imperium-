# CHAT_COMPILATION_PROTOCOL

## Principle
1. Read Git public memory first.
2. Run Administratum analyzer to identify context gaps.
3. Build a recommended chat compilation bundle from safe local context.
4. Owner uploads the produced zip to chat manually.

## Workflow
- Analyzer script: `TOOLS/administratum_analyze_git_local_context.ps1`
- Bundle builder: `TOOLS/build_chat_compilation_from_analysis.ps1`
- Optional one-command workflow: `ORGANS/ADMINISTRATUM/UTILITY/run_administratum_context_bundle_workflow.ps1`

## Output Location
- Local compilation root: `CHAT_COMPILATIONS_LOCAL/`
- These bundles are local handoff capsules and are not Git artifacts.

## Safety Defaults
- Default mode excludes raw private keys, tokens, passwords, `.env` values, cookies/sessions, and private command bodies.
- Default mode does not copy full `ARCHIVE` or full `SSH_COMMAND_LIBRARY` contents.
- Private inclusion requires explicit Owner approval and should remain allowlist-driven.
