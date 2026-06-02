# Throne TUI V0.1 Spec

Status: `CANDIDATE_SPEC`

## Purpose

The Throne TUI is a local SSH operator surface for commit truth, commit lookup, and evidence bundle export.

## Core Views

### Status

Fields:

- repo path;
- branch;
- local HEAD;
- origin HEAD after fetch;
- worktree cleanliness;
- last bundle export time;
- active caps.

### Commit Table Of Contents

Columns:

| order | short_sha | date | task_id | role | summary | bundle_available |
|---|---|---|---|---|---|---|

### Commit Detail

Sections:

- metadata;
- parents;
- changed files;
- diff preview path;
- receipts found;
- bundle manifest path;
- local object verification status;
- GitHub URL status when checked.

### Bundle Export

Controls:

- selected commit or task group;
- recipient selector: `LOGOS_PRIME`, `INQUISITION`, `SPECULUM`, `OWNER`;
- output directory;
- export command preview;
- receipt path.

## Forbidden UI Claims

- Do not label a commit as Custodes-admitted before Custodes exists.
- Do not use GitHub URL availability as the primary truth state.
- Do not show a clean PASS unless local object verification and bundle manifest checks pass.
