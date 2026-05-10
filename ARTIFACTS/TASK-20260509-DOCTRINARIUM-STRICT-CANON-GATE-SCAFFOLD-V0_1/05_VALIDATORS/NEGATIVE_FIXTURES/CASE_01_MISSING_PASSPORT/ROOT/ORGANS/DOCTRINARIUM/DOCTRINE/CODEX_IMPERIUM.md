---
document_id: CODEX_IMPERIUM
schema_version: DOCTRINE_DOCUMENT_V0_1A
document_role: MANDATORY_LAWBOOK
status: CANON_CANDIDATE_OWNER_REVIEW_REQUIRED
canon_for_real_task_execution: false
owner_approval_required: true
doctrinarium_priority: 3
language: en
created_for_task_context: IMPERIUM_DOCTRINARIUM_PRIMARY_DOCTRINE_TRIAD_V0_1A
---

# Codex Imperium

## 1. Purpose

The Codex Imperium is the mandatory lawbook of IMPERIUM.

The Passport of Emperor defines Owner authority.  
The Constitution of Imperium defines system structure.  
The Codex Imperium defines binding laws, prohibitions, required evidence, violation verdicts, and enforcement expectations.

The Codex exists so that Doctrinarium can check not only whether documents exist, but whether their laws are:
- addressed;
- registered;
- hashed;
- mapped to enforcement;
- checked by scripts or gates;
- able to block unsafe or fake-green execution.

Until Owner approval, this Codex remains a canon candidate only.

---

## 2. Law Model

Every law in the Codex must be machine-addressable.

Each law must have:
- `law_id`;
- title;
- meaning;
- applies-to scope;
- severity;
- required evidence;
- enforcement points;
- violation verdict;
- whether Owner override is allowed;
- whether the law blocks real task execution.

A law that is not mapped to enforcement is not fully operational.

---

## 3. Severity Levels

Codex laws use the following severity levels.

### 3.1 HARD_BLOCK

Violation blocks real task execution.

A HARD_BLOCK law may only be overridden by explicit Owner decision when the law permits override.

### 3.2 OWNER_DECISION_REQUIRED

The system cannot decide safely. The Owner must decide.

### 3.3 REPAIR_REQUIRED

The task may not proceed to finality until the issue is repaired.

### 3.4 WARNING

The issue must be visible to the Owner, but may not block narrow bootstrap or review work.

### 3.5 INFO

The issue is recorded for traceability.

---

## 4. Verdict Model

Common Codex violation verdicts include:

```text
BLOCKED_FAKE_GREEN_RISK
BLOCKED_OWNER_APPROVAL_REQUIRED
BLOCKED_MISSING_DOCTRINE
BLOCKED_MISSING_TASK_INPUTS
BLOCKED_ORGAN_NOT_CANON
BLOCKED_ORGAN_STANDARD_FAILED
BLOCKED_SEMANTIC_CONFLICT
BLOCKED_FORBIDDEN_ACTION
BLOCKED_ARCHIVE_SCAN_NOT_APPROVED
BLOCKED_DELETE_NOT_APPROVED
BLOCKED_THRONE_CONTACT_NOT_APPROVED
BLOCKED_VM2_SCOPE_OR_APPROVAL_MISSING
BLOCKED_SANCTUM_BASELINE_NOT_ACCEPTED
BLOCKED_UNREGISTERED_SCRIPT
BLOCKED_LATEST_BUNDLE_GUESSING
BLOCKED_BACKGROUND_WATCHER_NOT_APPROVED
BLOCKED_MANIFEST_SELF_REFERENCE
BLOCKED_AMBIGUOUS_CURRENT_STATE
BLOCKED_AMBIGUOUS_CONTINUITY
OWNER_DECISION_REQUIRED
REPAIR_REQUIRED
PASS_WITH_LIMITATIONS
PASS_BOOTSTRAP_ONLY
```

No law violation may be hidden under a generic `PASS`.

---

## 5. Enforcement Principle

Every mandatory law must be linked to at least one enforcement point.

Enforcement points may include:
- Doctrinarium preflight;
- Doctrinarium law validator;
- Doctrinarium semantic consistency validator;
- Officio Agentis scope builder;
- Administratum current state builder;
- Astronomicon route validator;
- Mechanicus script registry resolver;
- Inquisition audit;
- finalization checker;
- future Sanctum UI gate display.

A law is stronger when multiple organs check it independently.

A law that exists only as prose must be marked:
`LAW_NOT_FULLY_ENFORCED`.

---

## 6. Mandatory Laws

The following laws are mandatory for IMPERIUM v0.1A.

---

## LAW-001 — NO_FAKE_GREEN

### Meaning

No actor may claim that a task, stage, organ, artifact, baseline, doctrine document, continuity pack, UI state, or system surface is ready, accepted, final, canon, healthy, or green unless the claim is backed by evidence.

### Applies To

- tasks;
- stages;
- organs;
- doctrine;
- receipts;
- finalization;
- continuity;
- Sanctum/UI;
- VM2 results;
- baseline claims.

### Required Evidence

Depending on the claim:
- receipt;
- manifest;
- hash;
- audit report;
- current state;
- finalization receipt;
- Owner decision artifact;
- validation report.

### Violation Verdict

`BLOCKED_FAKE_GREEN_RISK`

### Enforcement

- Doctrinarium validation;
- Inquisition audit;
- Administratum current state;
- finalization review;
- future Sanctum panel status.

### Owner Override

Owner may accept risk explicitly, but the risk must remain recorded.

---

## LAW-002 — NO_OWNER_APPROVAL_BY_AGENT

### Meaning

No agent, role, organ, script, UI, or automation may infer Owner approval.

Only explicit Owner decision may approve:
- baseline;
- final result;
- canon document;
- organ canonization;
- destructive action;
- major override.

### Violation Verdict

`BLOCKED_OWNER_APPROVAL_REQUIRED`

### Enforcement

- Passport validation;
- Doctrinarium owner decision validator;
- Inquisition fake acceptance check;
- Administratum current state.

### Owner Override

Not applicable. The Owner cannot be replaced.

---

## LAW-003 — NO_TASK_WITHOUT_INPUTS

### Meaning

A task may not start as a real task without required inputs.

Minimum required inputs:
- `TASK_ID`;
- task recipe or launch card;
- Passport of Emperor;
- Constitution of Imperium;
- Codex Imperium;
- Doctrinarium preflight;
- Officio Agentis scope;
- stage map when stage execution is expected.

### Violation Verdict

`BLOCKED_MISSING_TASK_INPUTS`

### Enforcement

- Doctrinarium preflight;
- Administratum task context builder;
- Astronomicon route loader.

### Owner Override

Owner may authorize a bootstrap/manual exception, but it must be labeled and recorded.

---

## LAW-004 — NO_CHAT_MEMORY_AS_SOURCE_OF_TRUTH

### Meaning

Chat memory is not a source of truth.

A new chat, agent, or contour must continue from disk evidence:
- current state;
- receipts;
- doctrine;
- task recipe;
- continuity pack or candidate;
- next action;
- do-not-do list.

### Violation Verdict

`BLOCKED_AMBIGUOUS_CURRENT_STATE`

### Enforcement

- Administratum current state builder;
- continuity builder;
- Doctrinarium task input validation.

### Owner Override

Only for informal discussion, not for real task execution.

---

## LAW-005 — NO_DELETE_WITHOUT_OWNER_APPROVAL

### Meaning

No deletion, cleanup, migration, destructive edit, or irreversible modification may occur without explicit Owner approval.

### Applies To

- files;
- folders;
- artifacts;
- receipts;
- doctrine;
- organs;
- scripts;
- manifests;
- packs.

### Violation Verdict

`BLOCKED_DELETE_NOT_APPROVED`

### Enforcement

- Officio Agentis scope;
- Doctrinarium forbidden action validation;
- Inquisition forbidden action audit.

### Owner Override

Allowed only when explicit, scoped, recorded, and review-bound.

---

## LAW-006 — NO_ARCHIVE_SCAN_WITHOUT_OWNER_APPROVAL

### Meaning

Archive-like folders must not be recursively scanned, indexed, modified, or treated as active history without explicit Owner approval.

Archive-like names include:
- `ARCHIVE`;
- `Archive`;
- `archive`;
- `_archive`;
- `00_ARCHIVE`;
- `OLD`;
- `old`;
- `deprecated`;
- `DEPRECATED`.

### Violation Verdict

`BLOCKED_ARCHIVE_SCAN_NOT_APPROVED`

### Enforcement

- task recipe validation;
- path scanner;
- Inquisition forbidden path audit;
- Doctrinarium semantic check.

### Owner Override

Allowed only when explicit and scoped.

---

## LAW-007 — NO_THRONE_CONTACT_WITHOUT_OWNER_APPROVAL

### Meaning

No task, script, agent, or organ may contact, write to, or treat THRONE as active unless the Owner explicitly approves.

### Violation Verdict

`BLOCKED_THRONE_CONTACT_NOT_APPROVED`

### Enforcement

- Doctrinarium forbidden path validation;
- Officio Agentis scope;
- Inquisition audit;
- future THRONE admission protocol.

### Owner Override

Allowed only by explicit Owner decision.

---

## LAW-008 — NO_VM2_EXECUTION_WITHOUT_SCOPE

### Meaning

VM2 may not execute real work unless all of the following exist:
- Owner approval for VM2 real execution;
- Officio Agentis VM2 scope;
- Doctrinarium gate approval;
- Astronomicon stage assignment;
- Mechanicus allowed script/tool contract;
- PC-side return path;
- PC-side Inquisition verification plan.

### Violation Verdict

`BLOCKED_VM2_SCOPE_OR_APPROVAL_MISSING`

### Enforcement

- Doctrinarium task preflight;
- Officio Agentis VM2 scope;
- Astronomicon route;
- Mechanicus registry;
- Inquisition result audit.

### Owner Override

Owner may authorize VM2 smoke/bootstrap testing separately, but it must be labeled.

---

## LAW-009 — NO_SANCTUM_BASELINE_WITHOUT_OWNER_ACCEPTANCE

### Meaning

Sanctum baseline cannot be accepted by script, UI, receipt, or assistant summary.

Only explicit Owner acceptance may accept a Sanctum baseline.

### Violation Verdict

`BLOCKED_SANCTUM_BASELINE_NOT_ACCEPTED`

### Enforcement

- Doctrinarium baseline check;
- Inquisition fake baseline audit;
- Administratum current state;
- future Sanctum panel.

### Owner Override

Acceptance itself is Owner action.

---

## LAW-010 — NO_FINAL_WITHOUT_FINALIZATION_RECEIPT

### Meaning

No artifact or package may be called final without finalization evidence.

Minimum final evidence:
- final artifact path;
- manifest;
- hashes;
- finalization receipt;
- self-reference policy;
- sidecar when packaged;
- Owner acceptance when required.

### Violation Verdict

`BLOCKED_FINAL_WITHOUT_FINALIZATION_RECEIPT`

### Enforcement

- finalization checker;
- Inquisition audit;
- Administratum current state;
- Doctrinarium final claim validation.

### Owner Override

Owner may accept an unfinished artifact, but it must not be labeled final.

---

## LAW-011 — NO_BASELINE_WITHOUT_OWNER_ACCEPTANCE

### Meaning

No baseline may be marked accepted without explicit Owner acceptance.

A working version, screenshot, replay, or audit pass is not baseline acceptance.

### Violation Verdict

`BLOCKED_BASELINE_WITHOUT_OWNER_ACCEPTANCE`

### Enforcement

- Doctrinarium owner decision validation;
- Administratum current state;
- Inquisition fake baseline audit.

### Owner Override

Acceptance itself is Owner action.

---

## LAW-012 — NO_ORGAN_BY_FOLDER_NAME

### Meaning

An organ is not real merely because a folder exists.

To be considered operational, an organ must pass the required organ standard for the task mode.

### Required Evidence

- `ORGAN_STATUS.json`;
- `ORGAN_CONTRACT.json`;
- scripts or explicit non-script role;
- receipts;
- self-report or equivalent status report;
- allowed write roots;
- forbidden roots;
- validation receipt.

### Violation Verdict

`BLOCKED_ORGAN_STANDARD_FAILED`

### Enforcement

- Doctrinarium organ standard validator;
- Inquisition audit;
- future Sanctum organ panel.

### Owner Override

Owner may allow a bootstrap test, but the organ must remain labeled bootstrap or scaffold.

---

## LAW-013 — NO_ORGAN_SELF_REPORT_AS_PROOF_ALONE

### Meaning

An organ self-report is evidence input, not final proof.

Doctrinarium must cross-check self-reports against:
- contract;
- status;
- paths;
- hashes;
- receipts;
- script registry;
- current blockers.

### Violation Verdict

`BLOCKED_ORGAN_STANDARD_FAILED`

### Enforcement

- Doctrinarium self-report validator;
- Inquisition cross-check.

### Owner Override

Not for real task readiness.

---

## LAW-014 — NO_UNREGISTERED_SCRIPT_EXECUTION

### Meaning

Scripts used for task execution must be registered or explicitly authorized.

Mechanicus should provide:
- script id;
- path;
- hash;
- purpose;
- allowed stage types;
- required inputs;
- expected outputs;
- safety level.

### Violation Verdict

`BLOCKED_UNREGISTERED_SCRIPT`

### Enforcement

- Mechanicus script registry resolver;
- Doctrinarium task input validation;
- Inquisition audit.

### Owner Override

Allowed for manual/bootstrap testing if explicitly recorded.

---

## LAW-015 — NO_LATEST_BUNDLE_GUESSING

### Meaning

No task may rely on “latest bundle”, “newest file”, or ambiguous most-recent logic as source of truth.

Tasks must use exact:
- `TASK_ID`;
- `RUN_ID`;
- `STAGE_ID`;
- file path;
- hash;
- receipt;
- version.

### Violation Verdict

`BLOCKED_LATEST_BUNDLE_GUESSING`

### Enforcement

- Doctrinarium task input validator;
- Administratum current state builder;
- Inquisition audit.

### Owner Override

Allowed only for informal exploration, not evidence-chain execution.

---

## LAW-016 — NO_BACKGROUND_WATCHERS_WITHOUT_OWNER_APPROVAL

### Meaning

No watcher, daemon, background automation, scheduler, or auto-repair loop may be started without explicit Owner approval.

### Violation Verdict

`BLOCKED_BACKGROUND_WATCHER_NOT_APPROVED`

### Enforcement

- Officio Agentis scope;
- Doctrinarium forbidden action validation;
- Inquisition process/script review.

### Owner Override

Allowed only by explicit Owner decision and bounded scope.

---

## LAW-017 — NO_PROMPT_AS_CANON

### Meaning

A prompt is not canon.

A prompt may instruct an agent, but it does not replace:
- doctrine;
- task recipe;
- receipt;
- owner decision;
- current state;
- law registry.

### Violation Verdict

`BLOCKED_PROMPT_AS_CANON`

### Enforcement

- Doctrinarium task input validation;
- Administratum current state review;
- Inquisition fake canon audit.

### Owner Override

Not for canon status.

---

## LAW-018 — NO_RECEIPT_WITHOUT_HASH_CONTEXT

### Meaning

A receipt that references important outputs should include hash context or explain why hashing is not applicable.

Receipt without hash context is weak evidence.

### Violation Verdict

`REPAIR_REQUIRED` or `BLOCKED_FAKE_GREEN_RISK` depending on claim strength.

### Enforcement

- Inquisition receipt validation;
- finalization checker;
- Administratum evidence index.

### Owner Override

Allowed for discussion-only or early bootstrap, not for finality.

---

## LAW-019 — NO_SELF_REFERENTIAL_MANIFEST

### Meaning

A manifest or hash list must not include a final zip that is created after the manifest unless the packaging system has a clear external finalization policy.

Final zip and sidecar should normally be excluded from internal manifest/hash payload and referenced by an external finalization receipt.

### Violation Verdict

`BLOCKED_MANIFEST_SELF_REFERENCE`

### Enforcement

- finalization checker;
- Inquisition bundle audit.

### Owner Override

Not recommended for final packages.

---

## LAW-020 — NO_UI_GREEN_WITHOUT_EVIDENCE

### Meaning

A UI state, Sanctum panel, Explorer display, dashboard, color, icon, or button may not create truth.

Green UI is valid only if backed by evidence:
- Doctrinarium status;
- Inquisition audit;
- Administratum current state;
- receipts;
- hashes;
- Owner decision when required.

### Violation Verdict

`BLOCKED_FAKE_GREEN_RISK`

### Enforcement

- future Sanctum panel rules;
- Doctrinarium caller API;
- Inquisition status audit.

### Owner Override

Owner may accept a visual state, but acceptance must be recorded where system status changes.

---

## LAW-021 — NO_CONTINUITY_GREEN_WITHOUT_CURRENT_STATE

### Meaning

Continuity cannot be called green unless a current state exists and is consistent with receipts, artifacts, blockers, next action, and do-not-do list.

### Required Evidence

- `CURRENT_STATE`;
- continuity candidate or pack;
- latest receipt chain;
- blocker list;
- next action;
- do-not-do list.

### Violation Verdict

`BLOCKED_AMBIGUOUS_CONTINUITY`

### Enforcement

- Administratum continuity builder;
- Doctrinarium task preflight;
- Inquisition continuity audit.

### Owner Override

Owner may proceed manually, but continuity remains not green.

---

## LAW-022 — NO_SEMANTIC_CONFLICT_CONTINUATION

### Meaning

If two authoritative or evidence-bearing files conflict in meaning, execution must stop until the conflict is resolved or accepted by the Owner.

Examples:
- Constitution forbids Archive scan, but task recipe includes Archive path.
- Officio scope allows delete, but Codex forbids delete without Owner approval.
- Current state says active, finalization says final.
- Continuity next action differs from current state next action.
- Organ claims canon, but contract is missing.

### Violation Verdict

`BLOCKED_SEMANTIC_CONFLICT`

### Enforcement

- Doctrinarium semantic consistency validator;
- Inquisition audit;
- Administratum current state review.

### Owner Override

Allowed only by explicit Owner decision.

---

## LAW-023 — NO_REAL_TASK_WITH_BOOTSTRAP_DOCTRINE

### Meaning

A real task may not run under placeholder or bootstrap doctrine.

Bootstrap doctrine may only support:
- smoke tests;
- scaffold tests;
- review tasks;
- candidate generation.

### Violation Verdict

`BLOCKED_MISSING_DOCTRINE`

### Enforcement

- Doctrinarium preflight;
- doctrine index validation.

### Owner Override

Owner may authorize a limited exception, but the task must not claim real canon execution.

---

## LAW-024 — NO_CANON_WITHOUT_REGISTRATION

### Meaning

No document, organ, law, script, artifact, or system state may be called canon unless it is registered in the appropriate index and backed by evidence.

### Required Evidence

- canonical path;
- hash;
- owner approval when required;
- validation receipt;
- status entry.

### Violation Verdict

`BLOCKED_FAKE_GREEN_RISK`

### Enforcement

- Doctrinarium doctrine index;
- law registry;
- organ registry;
- Inquisition fake canon audit.

### Owner Override

Owner may approve canon, but registration must follow.

---

## LAW-025 — NO_LOCAL_CONFIG_IN_CANON_OR_HANDOFF

### Meaning

Secrets, machine-local credentials, private connection details, tokens, and unsafe local config must not be placed into canon documents or continuity handoffs.

### Violation Verdict

`BLOCKED_FORBIDDEN_ACTION` or `REPAIR_REQUIRED`

### Enforcement

- continuity builder;
- Inquisition package audit;
- future security checks.

### Owner Override

Not recommended. Sensitive material should be referenced safely, not embedded.

---

## 7. Law Enforcement Map Requirement

The Codex must be accompanied by a machine-readable law registry.

Recommended files:

```text
E:\IMPERIUM\ORGANS\DOCTRINARIUM\LAWS\MANDATORY_LAWS.json
E:\IMPERIUM\ORGANS\DOCTRINARIUM\LAWS\LAW_INDEX.json
E:\IMPERIUM\ORGANS\DOCTRINARIUM\LAWS\LAW_ADDRESS_REGISTRY.json
E:\IMPERIUM\ORGANS\DOCTRINARIUM\LAWS\LAW_ENFORCEMENT_MAP.json
```

Each mandatory law must be mapped to:
- enforcement script or gate;
- evidence required;
- blocking verdict;
- current enforcement status.

If a law is not yet enforced, it must be marked:
`LAW_NOT_FULLY_ENFORCED`.

---

## 8. Relation to Passport and Constitution

The Passport defines who may decide.

The Constitution defines how IMPERIUM is structured.

The Codex defines what must not be violated.

Doctrinarium validates all three.

If the Codex conflicts with the Passport or Constitution, the task must stop with:
`BLOCKED_SEMANTIC_CONFLICT`.

The Owner must resolve the conflict.

---

## 9. Doctrine Status and Use

This Codex is a primary doctrine input for Doctrinarium.

Current status:

```text
CANON_CANDIDATE_OWNER_REVIEW_REQUIRED
```

Until Owner approval:
- it may guide bootstrap and review tasks;
- it may be used to design validators;
- it may not be used to claim full real canon execution readiness.

After Owner approval and registration:
- it becomes a required input for real task preflight;
- its hash must be recorded in `DOCTRINE_INDEX.json` and law registries;
- Doctrinarium must block real tasks if it is missing, altered, unregistered, or contradicted.
