# Internet Research Notes

TASK_ID: TASK-20260511-IMPERIUM-STRUCTURE-PORTS-REGISTRY-AND-SERVITOR-WORKFLOW-HARDENING-V0_1

## 1) Diátaxis documentation system
- source/framework: Diátaxis
- URL: https://diataxis.fr/index.html
- core idea: Documentation should be organized by four user needs: tutorials, how-to guides, reference, explanation.
- adapt for IMPERIUM: Split docs by intent (operator runbooks vs architecture reference vs rationale).
- do not copy blindly: Do not force every existing file into strict quadrants in one migration.
- proposed local adaptation: Keep legacy docs, add a gradual Diátaxis map and tagging in registries.

## 2) ADR / MADR architecture decision records
- source/framework: MADR (Markdown Architectural Decision Records)
- URL: https://adr.github.io/madr/
- core idea: Record one decision per file with context, options, consequences, and status.
- adapt for IMPERIUM: Add architecture decisions for zone model, registry spine, and port contract governance.
- do not copy blindly: Do not require full historical backfill of old decisions before shipping improvements.
- proposed local adaptation: Start ADRs from this task forward, reference prior artifacts as historical evidence.

## 3) C4 model architecture visualization
- source/framework: C4 model
- URL: https://c4model.com/abstractions
- core idea: Use consistent abstraction levels (system, container, component, code) and diagram zoom levels.
- adapt for IMPERIUM: Use C4-style levels for ORGANS (system context), organ scripts/schemas (component), and execution paths.
- do not copy blindly: Do not create code-level diagrams for every script; keep value-focused views.
- proposed local adaptation: Document static model + execution flow diagrams in text-first markdown artifacts.

## 4) AsyncAPI-style communication contracts
- source/framework: AsyncAPI Specification 3.1.0
- URL: https://www.asyncapi.com/docs/reference/specification/latest
- core idea: Machine-readable contract for event/message-driven interfaces, protocol-agnostic structure, reusable components.
- adapt for IMPERIUM: Model organ-to-organ port messages as schema-first JSON with explicit payload and operation fields.
- do not copy blindly: Do not adopt full broker/protocol complexity where local script dispatch is synchronous.
- proposed local adaptation: Use lightweight AsyncAPI-inspired fields for registered internal ports and receipts.

## 5) OpenAPI-style request/response contracts
- source/framework: OpenAPI Specification
- URL: https://spec.openapis.org/oas/latest
- core idea: Standard interface contracts with operation-level definitions and explicit request/response structure.
- adapt for IMPERIUM: Define strict port message/response schemas and operation-specific schemas per organ.
- do not copy blindly: Do not model Imperium scripts as HTTP services unless they are actually exposed as services.
- proposed local adaptation: Use OpenAPI discipline (explicit fields, statuses, references) for internal JSON contracts.

## 6) Schema-first JSON contract discipline
- source/framework: JSON Schema specification
- URL: https://json-schema.org/specification
- core idea: Separate schema core/validation model and use schemas as executable data contracts.
- adapt for IMPERIUM: Every major registry and port payload should have schema and parse validation.
- do not copy blindly: Do not over-constrain exploratory legacy artifacts that cannot yet be normalized safely.
- proposed local adaptation: Validate new contracts strictly; mark legacy fields as unknown/optional with migration notes.

## 7) Monorepo hygiene and tradeoffs
- source/framework: Google research publication + Monorepo tools definition
- URLs:
  - https://research.google/pubs/why-google-stores-billions-of-lines-of-code-in-a-single-repository/
  - https://monorepo.tools/
- core idea: Monorepo scales with strong tooling/conventions; repository boundaries are an architecture decision, not dogma.
- adapt for IMPERIUM: Keep single repo with explicit zones, ownership registries, and script/port contracts.
- do not copy blindly: Do not imitate hyperscale operational assumptions or require enterprise-grade infra before basics.
- proposed local adaptation: Prioritize enforceable repository rules and traceability over large-scale optimization.

## 8) Artifact/evidence/provenance patterns
- source/framework: SLSA provenance
- URL: https://slsa.dev/spec/v1.0-rc2/provenance
- core idea: Provenance is an attestation linking artifacts to build definition and platform context.
- adapt for IMPERIUM: Treat task receipts as lightweight provenance with source script, inputs, outputs, hash metadata.
- do not copy blindly: Do not claim cryptographic supply-chain guarantees without signing and trusted verification roots.
- proposed local adaptation: Keep practical provenance fields in receipts and registry references now; add stronger attestation later.

## 9) Task/run/stage traceability patterns
- source/framework: OpenTelemetry traces/spans
- URL: https://opentelemetry.io/docs/concepts/signals/traces/
- core idea: Root trace + spans create a structured execution graph with timestamps and context propagation.
- adapt for IMPERIUM: Model TASK_ID as root, STAGE_ID as execution units, RECEIPT_ID as span evidence.
- do not copy blindly: Do not introduce full telemetry stack before basic schema and registry correctness are stable.
- proposed local adaptation: Traceability IDs in registries/artifacts first; optional telemetry integration later.
