# Script Artifact Preservation Policy V0.1

## Purpose

This policy prevents useful generated tools from disappearing after a task.

During complex work, agents often create temporary scripts, parsers, checkers, generators, and data transforms. These may become valuable future tools. IMPERIUM must not lose them silently.

## Core Law

No useful tool disappears.
No temporary script is silently deleted.

## Applies To

This applies to:
- Python scripts;
- PowerShell scripts;
- JavaScript helpers;
- report generators;
- JSON validators;
- parsers;
- migration helpers;
- screenshot tools;
- presentation builders;
- package builders;
- one-off commands saved as files.

## Required Classification

Each generated script/tool must be classified:

- `ABSORB_NOW`
- `BUFFER_FOR_SCRIPTORIUM_REVIEW`
- `REWRITE_REQUIRED`
- `KEEP_LOCAL_ONLY`
- `NEGATIVE_SAMPLE`
- `DISCARD_AFTER_REVIEW`

## Required Metadata

For each generated tool, record:
- task_id;
- artifact_id;
- original path;
- buffer path if applicable;
- purpose;
- inputs;
- outputs;
- dependencies;
- result;
- risk;
- recommendation.

## Buffer Rule

If a tool is not committed as an approved Scriptorium tool, it should go to a controlled buffer or be registered as intentionally discarded.

Recommended external local buffer:
`E:\IMPERIUM_CONTEXT\LOCAL\SCRIPT_BUFFER\`

Repo should store only a manifest/summary when the payload is local/private/temporary.

## Forbidden Behavior

Agents must not:
- delete a useful helper after using it without recording it;
- leave tool only in terminal history;
- bury generated code in a huge report;
- commit raw scratch tools as core tools without review;
- present a tool as reusable without type/safety review.

## Relation to Scriptorium

Scriptorium decides whether a buffered tool becomes:
- reusable tool;
- gate runner;
- receipt checker;
- agent factory helper;
- negative sample;
- archive-only reference.

## Pass Conditions

PASS if every generated tool is preserved, buffered, or intentionally classified.

## Fail Conditions

FAIL if any useful generated tool disappears silently.
