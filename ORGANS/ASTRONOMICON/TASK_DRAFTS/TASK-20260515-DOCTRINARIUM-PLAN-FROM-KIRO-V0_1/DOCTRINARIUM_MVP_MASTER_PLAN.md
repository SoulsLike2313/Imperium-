# Doctrinarium MVP Master Plan (Draft)

## Purpose of Doctrinarium
Doctrinarium is planned as the governance backend for laws, law integrity, organ health gates, and task admission gates.

## What It Owns
- law and doctrine machine-readable contracts;
- law registry and law integrity verdict generation;
- organ self-report intake contract and health verdict logic;
- task start gate request and verdict contracts;
- violation record contracts and no-fake-green checks.

## What It Must Not Own
- Astronomicon orchestration ownership;
- Administratum task lifecycle backend ownership;
- Officio Agentis role ownership;
- active Inquisition powers while Inquisition is not implemented;
- dashboard authority to replace backend evidence.

## Authority Model
Advisory input remains reference-only. Owner decisions determine promotion to implementation candidates. Canonical status is possible only after registration, implementation, verification, and evidence-backed acceptance.

## Law Lifecycle
`reference_only -> candidate -> accepted_draft -> registered -> implemented -> verified -> canonical -> retired_or_superseded`

## Organ Health Model
Organs submit deterministic self-reports. Doctrinarium evaluates freshness and policy compliance, then emits machine-readable health verdicts.

## Task Start Gate Model
Task execution is allowed only with explicit gate verdict artifacts and evidence references.

## Inquisition Disabled Hook Model
V1 includes explicit disabled-hook artifacts and checks. Active hook behavior is forbidden in V1.

## Evidence Model
Each checker must output parseable reports with timestamps, provenance fields, and evidence paths.

## No-Fake-Green Model
- no PASS without evidence paths;
- no PASS_WITH_WARNINGS with empty warnings;
- no healthy claims without freshness timestamps;
- no dashboard-based PASS without backend report linkage.

## Dashboard Future Requirement
Sanctum can be added later as a read-only consumer of real reports. Mock status output is not evidence.

## Integration
- Astronomicon: registration and stage-execution framing.
- Administratum: consumer of gate and health verdicts.
- Officio Agentis: role behavior aligned with law and gate outcomes.
- Future Inquisition: may consume violation records once implemented.
- Sanctum: report visualization only, no authority transfer.

## Execution Start Rule
Implementation starts only after Owner review and formal registration of `TASK-20260515-DOCTRINARIUM-MVP-V0_1`.
