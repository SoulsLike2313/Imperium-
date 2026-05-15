# Officio Agentis Architecture v0.1

## Scope

Officio Agentis provides role contracts and role validation artifacts. It does not execute Astronomicon or Administratum ownership domains.

## Core Components

- `ROLE_CONTRACTS/`: JSON and Markdown contracts per role.
- `MODES/`: role mode definitions and transition rules.
- `PROMPTS/`: system prompt artifacts for role behavior constraints.
- `TESTS/`: role behavior test case catalogs and dry-run runner.
- `SCHEMAS/`: JSON schemas for role contracts, mode contracts, settings, tests, and response contracts.
- `POLICIES/`: role-level policies for questions, evidence, language, stop behavior, prompt writing, and execution boundaries.
- `RESPONSE_CONTRACTS/`: machine-readable response shapes for Owner and artifact exchanges.
- `REGISTRY/`: role/schema/mode/policy registries and task stage evidence.
- `REPORTS/`: checker outputs and stage-level proof reports.

## Boundaries

- Astronomicon remains owner of stage maps and task lifecycle orchestration.
- Administratum remains owner of address book, chronicle, and task lifecycle backend.
- Doctrinarium remains owner of legal doctrine.
- Mechanicus remains owner of automation machinery.
- Inquisition remains owner of audit verdict authority.
- Sanctum remains owner of UI and dashboards.
- Scriptorium remains owner of documentation generation.
- Arsenal remains owner of reusable assets.

## Validation Flow

1. Foundation validator checks skeleton, registries, schemas, and README boundaries.
2. Role contract validator checks role JSON, modes, prompt constraints, and tests.
3. Dry-run role test runner checks deterministic contract/test completeness.
4. `officio_agentis_check_all_v0_1.py` aggregates all checks into a single report.
