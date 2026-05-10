# SINGLE_ACTIVE_WORKER_COPY_HYGIENE_LAW_V1

Status: candidate law.

## Core rule

VM3 must maintain one active worker copy for execution.

## Current active copy

- `/home/vboxuser3/Desktop/IMPERIUM`

## Lifecycle classes

- active_worker_copy
- stale_local_copy_retired
- preserved_evidence_archive
- runtime_signal_surface
- historical_snapshot_reference

## Hygiene requirements

1. Before major fix-wave, active copy must align to THRONE HEAD.
2. Non-active copies must be classified as retired or preserved evidence.
3. New execution steps must declare active copy path explicitly.
4. Signals must include repo_path of active copy.

## Forbidden

- multiple confusing active copies
- silent switch of active copy without report
- continuing major fixes from stale unaligned copy
