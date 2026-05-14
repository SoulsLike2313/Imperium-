# IMPERIUM Canonical Language and UI Localization Policy v0.1

## Status

Draft policy for Officio Agentis registration.
Candidate for later Doctrinarium canon registration.

## Purpose

Prevent mojibake, encoding loss, broken handoffs, corrupted receipts, and ambiguous machine state while preserving Owner-facing communication and bilingual dashboards/applications.

## Core Law

Canonical system artifacts MUST be English-only by default.

Non-English Owner-facing text is allowed only in:

1. live Owner-facing chat responses;
2. Servitor/Logos human-facing chat explanations;
3. dedicated UI localization resources;
4. dashboard/application presentation strings loaded through i18n.

Non-English text MUST NOT be stored as canonical truth inside machine-readable system artifacts unless explicitly approved by Owner for a dedicated localization file.

## Layer Separation

### Canonical / Machine Layer

Language: English only.

Applies to:

- schemas;
- JSON state files;
- receipts;
- manifests;
- task IDs;
- stage IDs;
- status enums;
- logs;
- script output;
- checker output;
- handoff manifests;
- result bundle machine files;
- canonical Markdown documentation;
- registry files;
- dashboard data files.

### Presentation / UI Layer

Language: English and Russian supported.

Russian may appear in:

- `i18n/ru.json`;
- UI translation packs;
- dashboard labels;
- button labels;
- tooltips;
- help panels;
- Owner-facing application text.

Canonical state must store stable English keys and statuses.
UI must translate those keys into Russian or English.

## Required Pattern

Canonical state:

```json
{
  "status": "REGISTERED_LOCAL_WORKBENCH_ACTIVE_STATE_ONLY",
  "ready_for_agent": false
}
```

UI presentation:

```text
EN: Registered locally - Workbench active state only
RU: Russian text belongs in a dedicated i18n resource, not in canonical state.
```

## Forbidden Pattern

Do not store display text as canonical state truth:

```json
{
  "status": "<localized display text>"
}
```

## Bundle Rule

Servitor result bundles must keep machine files English-only.

Allowed:

- `SERVITOR_STAGE_EXECUTION_REPORT.json` in English;
- receipts in English;
- check outputs in English;
- manifests in English.

Not allowed:

- localized human-facing text inside canonical bundle files.

Human summaries should be delivered in live chat, not stored as canonical artifacts, unless placed in a dedicated presentation/localization file.

## Dashboard and Application Rule

Every dashboard or application should support two presentation languages where practical:

- English;
- Russian.

Implementation should use dedicated localization resources, for example:

```text
SANCTUM/I18N/en.json
SANCTUM/I18N/ru.json
ORGANS/<ORGAN>/I18N/en.json
ORGANS/<ORGAN>/I18N/ru.json
```

Dashboard data remains English-only.
UI renders localized strings.

## Guard Requirements

Future guards should check:

1. canonical JSON files contain no Cyrillic text outside approved i18n/presentation paths;
2. receipts, manifests, logs, and check outputs are English-only;
3. Russian appears only in approved i18n/presentation paths;
4. all text files decode as UTF-8;
5. known mojibake patterns are absent;
6. UI localization files parse correctly.

## Owner Communication

Owner-facing live responses remain Russian by preference.

Servitor/Logos chat reports should keep the established Owner format:

1. step name;
2. full path;
3. verdict;
4. 3-4 Russian comments.

This chat format does not authorize Russian inside canonical machine artifacts.

## No Fake Green

A file passing UTF-8 decode is not enough.

A file fails language policy if it stores localized text in canonical truth fields where only English should exist.
