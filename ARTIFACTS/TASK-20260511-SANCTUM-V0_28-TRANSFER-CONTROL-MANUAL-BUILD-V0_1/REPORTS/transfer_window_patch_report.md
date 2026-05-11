# Transfer Window Patch Report

Patched at: 2026-05-11T19:37:24+03:00

## Changes

- Added Transfer Control button to Sanctum v0.28 top bar.
- Added TransferWindow popup.
- Added PC to VM2 prompt send flow.
- Added VM2 remote prompt auto-open via xdg-open.
- Added remote VM2 bundle listing.
- Added selected/latest VM2 bundle fetch.
- Added local runtime transfer receipts.
- Disabled tracked SANCTUM_STATUS/README write on ordinary v0.28 launch.

## Runtime receipt path

E:\IMPERIUM\.imperium_runtime\transfer\receipts

## Route

PC prompt outbox:

E:\IMPERIUM\OUTBOX\VM2_PROMPTS

VM2 workdrop:

/home/vboxuser2/IMPERIUM_PRIVATE/WORKDROP

VM2 bundle outbox:

/home/vboxuser2/IMPERIUM_PRIVATE/OUTBOX_BUNDLES

PC bundle inbox:

E:\IMPERIUM\INBOX\VM2_BUNDLES
