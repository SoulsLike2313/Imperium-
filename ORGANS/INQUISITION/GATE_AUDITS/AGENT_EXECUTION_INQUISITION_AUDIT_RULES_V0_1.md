# Agent Execution Inquisition Audit Rules V0.1

## Purpose

This file gives Inquisition rules for auditing agent execution quality.

It combines first-pass audit coverage for:
- script artifact loss;
- KPD waste;
- command avalanche;
- fake completion.

## 1. Script Artifact Loss Audit

Blockers:
- generated helper script deleted without record;
- useful parser/checker/generator left only in terminal history;
- temporary tool not saved to buffer or manifest;
- tool used for task but absent from receipt;
- agent claims cleanup but loses useful artifact.

Required evidence:
- preservation manifest;
- explicit discard reason;
- tool path or buffer path;
- KPD note if created by big model.

## 2. Agent KPD Waste Audit

Warnings:
- agent repeated discovery of known paths;
- agent ignored existing Scriptorium tools;
- agent produced long prose but few durable artifacts;
- agent generated a tool but failed to classify it;
- task scope was too broad but agent did not recommend narrower profiles;
- no future prompt/profile improvements recorded.

Blockers:
- major big-model run has no KPD self-review;
- self-review claims high efficiency while tools/results are missing;
- agent hid uncertainty or fake completion.

## 3. Command Avalanche Audit

Warnings:
- single huge command attempted;
- command-length failure occurred;
- phase validation missing;
- generator mixed core docs, gates, reports, and commit in one block.

Blockers:
- failed giant command created partial dirty files and agent continued;
- partial artifacts not quarantined or cleaned safely;
- final commit includes accidental partial output.

## 4. Fake Completion Audit

Blockers:
- PASS claim without receipt;
- implemented claim when only contract exists;
- ready claim while readiness matrix says BLOCKED/UNKNOWN;
- performance claim while required CSS/JS/API failed;
- agent factory ready claim while only concept exists;
- control center ready claim while only requirements exist.

## Required Audit Verdicts

Use:
- PASS
- WARN
- BLOCKED
- REVIEW_REQUIRED

Do not produce fake PASS if evidence is missing.

## Minimum Audit Checklist

For each agent task, ask:
1. Did it start clean?
2. Did it use compact command phases?
3. Did it preserve generated tools?
4. Did it produce receipts?
5. Did it self-assess pass criteria?
6. Did big model provide KPD review if required?
7. Did it avoid forbidden paths?
8. Did it avoid fake completion claims?

## Relation to Gates

This audit supports:
- `GATE-U09-NO-FAKE-GREEN`
- `GATE-U12-REPORT-OUTPUT-BUDGET`
- `GATE-U19-SCRIPT-ARTIFACT-PRESERVATION`
- `GATE-U20-AGENT-KPD-SELF-REVIEW`
- `GATE-U21-COMMAND-CHUNKING`
