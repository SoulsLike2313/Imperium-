# BIG_SCRIPT_BOOTSTRAP_PROTOCOL_V1

Status: candidate tooling law.

## Problem

Large inline Windows shell/PowerShell command blocks may fail because of command-line length and quoting limits.

## Law

Large PC/Windows scripts MUST be file-backed and phase-based:

1. write `.ps1` or `.py` runner file in step workspace
2. store long parameters in JSON config/manifest
3. execute short command referencing script file
4. split run into resumable phases if needed
5. persist stdout/stderr/exit-code for each phase
6. write phase markers for resume

## Forbidden

- huge inline one-liner scripts
- hidden non-resumable long command blocks
- no-log execution for long scripts
