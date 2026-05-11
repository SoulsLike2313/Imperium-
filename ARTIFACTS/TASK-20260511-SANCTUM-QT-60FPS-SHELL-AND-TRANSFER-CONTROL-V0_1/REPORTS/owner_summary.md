# Owner Summary — Sanctum Qt v0.29

## What was done

Created a new PySide6 / Qt Sanctum dashboard:

SANCTUM/sanctum_v0_29_qt.py

Created launcher:

SANCTUM/RUN_SANCTUM_V0_29_QT.ps1

## Why

Tkinter v0.26/v0.28 could not provide stable animated dashboard behavior at the desired quality level. Flicker disappeared only when animation was slowed or disabled, which was not acceptable.

## Current result

Sanctum v0.29 Qt now provides:

- direct dashboard launch;
- central animated planet/orbit view;
- FPS counter;
- left task panel;
- top command bar;
- Transfer Control panel;
- VM2 prompt send;
- VM2 bundle list/fetch;
- runtime transfer receipts;
- pragmatic folder-opening buttons.

## Important routes

PC prompt outbox:

E:\IMPERIUM\OUTBOX\VM2_PROMPTS

VM2 prompt drop:

/home/vboxuser2/IMPERIUM_PRIVATE/WORKDROP

VM2 bundle outbox:

/home/vboxuser2/IMPERIUM_PRIVATE/OUTBOX_BUNDLES

PC bundle inbox:

E:\IMPERIUM\INBOX\VM2_BUNDLES

## Current verdict

PASS_WITH_LIMITATIONS

Good enough to fix state and move to new chat.
