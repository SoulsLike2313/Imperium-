# Button Wiring Report — Sanctum Qt v0.29

Patched at: 2026-05-11T20:05:36+03:00

## Problem

The Qt shell had working Transfer Control, but top command buttons were placeholders.

## Fixed buttons

- Open Astra Utility
- Open Explorer
- Open Task Folder
- Open Notes
- Refresh Tasks

## Current behavior

Open Astra Utility:
opens ASTRONOMICON folder.

Open Explorer:
opens EXPLORER folder.

Open Task Folder:
opens ARTIFACTS/<selected task> if present, otherwise ARTIFACTS root.

Open Notes:
opens CHAT_COMPILATIONS_LOCAL if present, otherwise DOCS.

Refresh Tasks:
reloads task list from ARTIFACTS/TASK-* directories.

## Notes

This is pragmatic wiring for the current Qt shell.
Later these buttons can launch dedicated dashboard utilities instead of opening folders.
