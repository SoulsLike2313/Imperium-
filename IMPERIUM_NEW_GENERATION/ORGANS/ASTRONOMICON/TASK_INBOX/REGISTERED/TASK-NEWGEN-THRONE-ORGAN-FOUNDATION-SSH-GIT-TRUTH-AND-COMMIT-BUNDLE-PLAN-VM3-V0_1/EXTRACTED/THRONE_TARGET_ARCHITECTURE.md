# Throne Target Architecture

## Identity

Throne is a local TUI/script-first IMPERIUM organ-agent. It is not a public server and not a GitHub replacement service. It is the local seal of git and admission truth.

## Deployment model

- Runs on Owner laptop.
- Used over SSH only on local network.
- No public exposure by default.
- Cloudflare/read-only viewer is a later optional candidate, not part of V0.1.

## Core commands in future

```text
throne status
throne sync
throne commits list --limit 50
throne commits find --task-id <TASK_ID>
throne bundle latest --for LOGOS_PRIME
throne bundle commit <SHA> --for INQUISITOR
throne bundle task <TASK_ID> --for SPECULUM
throne export tree <SHA>
throne receipts find <SHA>
```

## Commit table of contents

Throne must be able to show a fast commit TOC:

| order | short_sha | date | task_id | role | summary | bundle_available |
|---|---|---|---|---|---|---|

## Deep commit evidence

For a specific commit, Throne must export:
- metadata
- parent relation
- diff
- changed file list
- changed file snapshot
- tree archive
- receipts found in repo
- task report paths
- review context
- hashes

## Review recipients

The same commit truth can be packaged for:
- LOGOS_PRIME
- INQUISITOR
- SPECULUM

The project truth must remain the same. Role-specific additions must be separate role packs, not altered truth.
