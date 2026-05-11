# TASK-20260511-SANCTUM-QT-60FPS-SHELL-AND-TRANSFER-CONTROL-V0_1

## Purpose

Build a new Sanctum Qt dashboard shell because Tkinter v0.26/v0.28 cannot reliably provide the required stable 60 FPS planet/orbit view.

## Starting point

- Sanctum v0.26 is the working visual reference.
- Sanctum v0.28 proved Transfer Control logic in Tkinter.
- v0.28 flicker was reduced only by disabling/slowing animation, which is not acceptable.
- New direction: PySide6 / Qt dashboard.

## Target

Create:

SANCTUM/sanctum_v0_29_qt.py

Launcher:

SANCTUM/RUN_SANCTUM_V0_29_QT.ps1

## Required features for v0.29 Qt first shell

1. Direct dashboard launch, not through VS Code.
2. 60 FPS central planet/orbit render.
3. Left task panel.
4. Top command bar.
5. Transfer Control dock/panel.
6. Send prompt to VM2.
7. Auto-open prompt on VM2 through xdg-open.
8. List/fetch VM2 bundles.
9. Runtime transfer receipts.
10. No tracked state writes on ordinary launch.

## Route model

PC prompt outbox:

E:\IMPERIUM\OUTBOX\VM2_PROMPTS

VM2 prompt drop:

/home/vboxuser2/IMPERIUM_PRIVATE/WORKDROP

VM2 bundle outbox:

/home/vboxuser2/IMPERIUM_PRIVATE/OUTBOX_BUNDLES

PC bundle inbox:

E:\IMPERIUM\INBOX\VM2_BUNDLES

Runtime transfer receipts:

E:\IMPERIUM\.imperium_runtime\transfer\receipts
