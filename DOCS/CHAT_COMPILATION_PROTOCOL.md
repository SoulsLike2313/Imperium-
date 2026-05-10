# CHAT_COMPILATION_PROTOCOL

## Core Principle
1. Read Git public memory first.
2. Run Administratum Analyzer v0.2 with post-push reality check.
3. Trust analyzer decision on whether Git-only continuation is enough.
4. If needed, build chat compilation bundle from analyzer recommendation.
5. Owner uploads zip to chat manually.

## Decision Model
- Analyzer v0.2 evaluates:
  - local HEAD vs origin/master vs ls-remote master
  - public memory completeness
  - boundary hygiene
  - context gaps for target (`FULL_IMPERIUM_SUMMARY` or `VM2_WORK`)
- Bundle builder follows analyzer output instead of manual guessing.

## Safety Defaults
- Default bundle is safe mode.
- No raw private keys, tokens, passwords, `.env` values, cookies/sessions, or private command bodies.
- Full `ARCHIVE` and full `SSH_COMMAND_LIBRARY` content are excluded by default.

## Post-Push Trust Rule
Post-push reality check must pass before treating Git as current trusted public memory.
