# Commit Evidence Bundle Contract

Status: `CANDIDATE_V0_1`

Owner organ: `THRONE`

## Purpose

A commit evidence bundle is the portable review unit for a selected commit or task group. It lets Logos-Prime, Inquisition, or Speculum review local git truth even when GitHub web pages are unavailable.

## Required Bundle Sections

- commit metadata;
- parent relation;
- changed file list;
- diff patch;
- selected changed file snapshots;
- task report and receipt manifest;
- tree archive or explicit cap when omitted;
- SHA-256 sums;
- role-specific review note pack when requested.

## Recipient Boundary

The project truth must not change per recipient. `LOGOS_PRIME`, `INQUISITION`, and `SPECULUM` packs may add role-specific notes, but they must all reference the same commit SHA and base bundle manifest.

## PASS Conditions

- Commit object verification passes locally.
- Bundle manifest matches the target commit SHA.
- Bundle hash is recorded.
- Missing sections are explicit caps, not hidden gaps.

## WARN Conditions

- Tree archive is omitted in a prototype run.
- SSH probe was not used because the task did not provide safe target access.
- GitHub URL status is unavailable but local git truth passes.

## BLOCK Conditions

- Bundle manifest is missing.
- Bundle target SHA does not match the verified local commit.
- Runtime evidence is claimed without replay command or receipt.
