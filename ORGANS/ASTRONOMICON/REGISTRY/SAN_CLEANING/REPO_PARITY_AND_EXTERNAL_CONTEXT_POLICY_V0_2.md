# Repo Parity and External Context Policy v0.2

## Scope
This policy defines the canonical Git worktree boundary and external local/private context model for IMPERIUM.

## Required Canonical Worktrees
- PC canonical Git worktree: `E:\IMPERIUM`
- VM2 canonical Git worktree: `/home/vboxuser2/IMPERIUM_WORK/Imperium-`
- GitHub canonical tree reference for this cycle: `216b07504e0cb8406a1b464abfd17763ffbafc2a`

Tracked project files must remain equivalent across:
1. GitHub exact tree.
2. PC worktree tracked file set.
3. VM2 worktree tracked file set.

## External Context Roots (PC)
- Local operational context root: `E:\IMPERIUM_LOCAL`
- Private Owner context root: `E:\IMPERIUM_PRIVATE`

## Reserved External Roots (Future VM)
- `~/IMPERIUM_LOCAL`
- `~/IMPERIUM_PRIVATE`

## Canonical Boundary Rule
- `E:\IMPERIUM` and `/home/vboxuser2/IMPERIUM_WORK/Imperium-` are canonical tracked worktree roots only.
- Ignored/local/private/generated payloads must not physically live inside canonical repo roots.
- Ignored/local/private/generated payloads must live outside repo roots in approved external local/private paths.
- PC repo must not act as a warehouse for ignored junk.

## Owner Control Rule
- Private context inclusion in continuity/full handoff is Owner-controlled.
- Continuity/full handoff may include local/private data only by explicit Owner decision.
- Private/local payloads must never be committed.

## Mechanicus Structural Rule
- `SCRIPTORIUM` and `ARSENAL` live under `ORGANS/MECHANICUS/`.
- They are support sub-systems, not independent organs.

## Advisory Input
Required advisory reference input:
`ORGANS/ASTRONOMICON/REGISTRY/ADVISORY_RESPONSES/ADVISORY-RESPONSE-20260513-KIRO-SAN-CLEANING-BACKEND-TRUTH-V0_1.md`

Relevant sections for this policy slice: 2, 3, 8, 10, 11, 12, 15, 16.
Advisory is required input, not automatic canon.
