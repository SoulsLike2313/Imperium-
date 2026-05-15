# Dashboard Truth and Beauty Doctrine V0.1

Status: draft derived from Owner answers.

## Core doctrine

Dashboard V1 equals 100 percent truth surface plus beauty.

If there is no evidence, the dashboard may not claim truth.
If a script is shown, it must work or be explicitly disabled.
If a button is shown, it must work or be explicitly disabled.
If a status is green, it must link to real backend reports and evidence.

## Required dashboard truth fields

Every serious status should provide:

- status value;
- source report path;
- source script path if applicable;
- evidence paths;
- last updated timestamp;
- freshness status;
- warnings;
- blockers.

## Button contract

Every action button that performs meaningful work must define:

- button_id;
- labels for English and Russian UI;
- target action or script;
- allowed role;
- required confirmation;
- expected report path;
- expected receipt path;
- success condition;
- failure condition;
- timeout;
- disabled reason if not available.

## Script display contract

Every script displayed in a dashboard must show:

- script path;
- purpose;
- last run timestamp;
- last verdict;
- last report path;
- last evidence paths;
- whether it can be run from the dashboard.

## Animation doctrine

Animation must communicate state, not hide state.

Required stage visuals:

- completed: changed color and dim glow;
- active: active pulse and animation;
- future: white-platinum slow stellar glow;
- blocked: severe warning marker with clear blocker reason;
- waiting for evidence: subdued cold glow with missing-evidence marker.

## Aesthetic doctrine

The desired visual language:

- Warhammer / Imperial spirit;
- sci-fi;
- Jarvis-like command interface;
- cosmic motion;
- smooth architecture;
- readable dense information;
- 60 FPS target where feasible;
- organ-specific dashboard identity;
- unified Sanctum flow.

## No fake green doctrine

Forbidden:

- dashboard green without evidence;
- mock data in production truth panels;
- button that does not execute its declared action;
- hidden script failure behind pretty UI;
- active claim for disabled features;
- PASS_WITH_WARNINGS with empty warnings;
- PASS with empty evidence paths.
