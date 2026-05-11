# TASK-20260511-SANCTUM-V0_28-TRANSFER-CONTROL-MANUAL-BUILD-V0_1

## Purpose

Manual implementation task for Sanctum v0.28 Transfer Control.

## Starting point

Sanctum v0.28 was created from the working Sanctum v0.26 dashboard base.

v0.26 is visually confirmed working as dashboard shell:
- Mission Control Core
- Unified Planet Map
- active task panel
- task list
- top action buttons

v0.28 now exists and launches as:

SANCTUM/sanctum_v0_28.py

Launcher:

SANCTUM/RUN_SANCTUM_V0_28.ps1

## Goal

Add a Sanctum Transfer Control window for VM2 workflow:

1. Send prompt to VM2.
2. Auto-open prompt text file on VM2.
3. Lock verified route after successful delivery.
4. List/fetch VM2 artifact bundles.
5. Save fetched bundles on PC.
6. Write transfer receipts.
7. Keep Sanctum as dashboard shell, not source of truth.

## Route model

PC prompt outbox:

E:\IMPERIUM\OUTBOX\VM2_PROMPTS

VM2 prompt drop:

/home/vboxuser2/IMPERIUM_PRIVATE/WORKDROP

VM2 bundle outbox:

/home/vboxuser2/IMPERIUM_PRIVATE/OUTBOX_BUNDLES

PC bundle inbox:

E:\IMPERIUM\INBOX\VM2_BUNDLES

Transfer receipts:

E:\IMPERIUM\.imperium_runtime\transfer\receipts

## Hard rules

- Do not break v0.26.
- Do not make Sanctum an organ.
- Do not make Sanctum source of truth.
- Do not store SSH private keys in Git.
- Do not commit runtime transfer receipts unless intentionally summarized.
- Do not write tracked state on ordinary launch.
- New implementation must be in v0.28.
