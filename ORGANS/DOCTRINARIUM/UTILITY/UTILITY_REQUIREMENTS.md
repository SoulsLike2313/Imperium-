# Doctrinarium Utility Requirements v0_1

Status: UTILITY_SCAFFOLD
Owner-facing name: Doctrinarium Workbench v0_1

Purpose:
The Doctrinarium utility must let the Owner observe and trigger Doctrinarium checks without treating the UI as source of truth.

This utility is not a GUI yet.
This is the first utility declaration and script-backed workbench surface.

It must expose:
- doctrine triad status;
- law registry status;
- laws not fully enforced;
- organ gap report;
- organ utility gap report;
- Doctrinarium status report;
- blockers;
- warnings;
- latest receipts;
- raw JSON paths;
- allowed modes: bootstrap/review vs real task execution.

Source of truth:
- doctrine documents;
- law registry JSON files;
- standards JSON files;
- validator scripts;
- reports;
- receipts;
- hashes.

The utility must not:
- replace Owner;
- claim canon;
- approve documents;
- repair other organs directly;
- execute task stages;
- hide blockers;
- show green without evidence.

Promotion rule:
Doctrinarium cannot become CANON_CANDIDATE or CANON_V0_1 without this utility being script-backed and visible.
