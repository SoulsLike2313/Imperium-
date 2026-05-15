# Doctrinarium Stage Matrix (Draft)

## STAGE-0 Planning / Registration Package
- purpose: finalize planning package and registration-ready draft artifacts without executing registration.
- source references: Kiro advisory buffer and large-plan method outputs.
- files to create: planning docs, stage map, evidence requirements, stage prompts.
- scripts to create: optional planning helpers only.
- schemas to create/validate: planning JSON artifacts.
- tests: JSON parse checks and checklist pass.
- pass criteria: all planning artifacts exist and parse; no implementation or registration actions.
- stop criteria: missing files, invalid JSON, unresolved owner decisions.
- evidence paths: TASK_DRAFTS/.../REPORTS/doctrinarium_planning_package_report.json
- fake green checks: no PASS without evidence paths.
- owner approval needs: yes, before registration.
- expected receipts: planning package report and git evidence.

## STAGE-1 Foundation
- purpose: establish Doctrinarium scope, ownership boundaries, and baseline structure.
- source references: approved planning package.
- files to create: boundary docs, base readme, foundational contracts.
- scripts to create: foundation validator.
- schemas to create/validate: foundation schema references.
- tests: foundation dry-run validation.
- pass criteria: boundary and foundation reports PASS.
- stop criteria: ownership collision or failed checker.
- evidence paths: ORGANS/DOCTRINARIUM/REPORTS/foundation_validation_report.json
- fake green checks: no PASS_WITH_WARNINGS with empty warnings.
- owner approval needs: no.
- expected receipts: foundation receipt.

## STAGE-2 Law Registry
- purpose: define law format and registry contracts.
- source references: stage-1 outputs and approved decisions.
- files to create: law and registry schema artifacts.
- scripts to create: law registry validator.
- schemas to create/validate: law.schema, doctrine.schema, law_registry.schema.
- tests: schema parsing and registry checks.
- pass criteria: registry validation PASS with provenance.
- stop criteria: schema invalid or provenance missing.
- evidence paths: ORGANS/DOCTRINARIUM/REPORTS/law_registry_validation_report.json
- fake green checks: no law compliance claim without report.
- owner approval needs: no.
- expected receipts: law registry receipt.

## STAGE-3 Law Integrity
- purpose: detect contradictions and integrity drift.
- source references: stage-2 law registry outputs.
- files to create: integrity checker contracts and reports.
- scripts to create: law integrity checker.
- schemas to create/validate: law_compliance_report.schema.json.
- tests: contradiction scenario dry-run tests.
- pass criteria: integrity report PASS and contradiction handling evidence.
- stop criteria: unresolved contradiction or checker failure.
- evidence paths: ORGANS/DOCTRINARIUM/REPORTS/law_integrity_report.json
- fake green checks: no PASS if contradiction_count unresolved.
- owner approval needs: no.
- expected receipts: integrity receipt.

## STAGE-4 Organ Health
- purpose: collect self-reports and produce health verdict.
- source references: stage-1 boundaries and stage-2 schemas.
- files to create: self-report and health verdict artifacts.
- scripts to create: self-report collector and health evaluator.
- schemas to create/validate: organ_self_report.schema.json, organ_health_verdict.schema.json.
- tests: freshness and missing-report scenarios.
- pass criteria: health verdict PASS with checker_last_run_utc.
- stop criteria: stale or missing self-report, invalid verdict schema.
- evidence paths: ORGANS/DOCTRINARIUM/REPORTS/organ_health_verdict_report.json
- fake green checks: no HEALTHY without freshness timestamp.
- owner approval needs: no.
- expected receipts: organ health receipt.

## STAGE-5 Task Start Gate
- purpose: enforce admission gate and emit violation records.
- source references: stage-2 and stage-4 outputs.
- files to create: gate request/verdict and violation artifacts.
- scripts to create: task start gate checker and violation recorder.
- schemas to create/validate: task_start_gate_request.schema.json, task_start_gate_verdict.schema.json, violation_record.schema.json.
- tests: allow/block scenario dry-runs.
- pass criteria: deterministic gate verdict and violation evidence when blocked.
- stop criteria: missing verdict file or inconsistent allow status.
- evidence paths: ORGANS/DOCTRINARIUM/REPORTS/task_start_gate_verdict_report.json
- fake green checks: no task start allowed without verdict artifact.
- owner approval needs: no.
- expected receipts: task gate receipt.

## STAGE-6 Inquisition Hook Disabled
- purpose: define disabled hook contract with explicit non-active status.
- source references: planning decisions and boundary constraints.
- files to create: disabled hook packet schema and verification report.
- scripts to create: disabled-hook verifier.
- schemas to create/validate: inquisition_hook_packet.schema.json.
- tests: disabled-state assertions.
- pass criteria: report confirms disabled state with no active behavior.
- stop criteria: any artifact implies active hook.
- evidence paths: ORGANS/DOCTRINARIUM/REPORTS/inquisition_hook_disabled_report.json
- fake green checks: no active hook claim while unimplemented.
- owner approval needs: no.
- expected receipts: inquisition disabled receipt.

## STAGE-7 Integration / Tests
- purpose: run integrated checks and anti-fake-green scenarios.
- source references: stage-1 through stage-6 outputs.
- files to create: integration reports and test evidence.
- scripts to create: check_all and test runners.
- schemas to create/validate: all Doctrinarium MVP schemas.
- tests: full dry-run and critical-only dry-run.
- pass criteria: check_all PASS with warning disclosure and linked reports.
- stop criteria: required reports missing or fake-green pattern detected.
- evidence paths: ORGANS/DOCTRINARIUM/REPORTS/check_all_report.json
- fake green checks: no PASS_WITH_WARNINGS with empty warnings.
- owner approval needs: no.
- expected receipts: integration receipt.

## STAGE-8 Self-Build
- purpose: prove deterministic self-build and final readiness graph.
- source references: stage-7 integrated outputs.
- files to create: self-build evaluation report and receipt.
- scripts to create: self-build evaluator.
- schemas to create/validate: self-build report contract.
- tests: self-build repeatability checks.
- pass criteria: self-build PASS with complete evidence graph.
- stop criteria: blockers unresolved or evidence graph missing.
- evidence paths: ORGANS/DOCTRINARIUM/REPORTS/self_build_evaluation_report.json
- fake green checks: no PASS with empty evidence graph.
- owner approval needs: yes, final acceptance.
- expected receipts: self-build receipt.
