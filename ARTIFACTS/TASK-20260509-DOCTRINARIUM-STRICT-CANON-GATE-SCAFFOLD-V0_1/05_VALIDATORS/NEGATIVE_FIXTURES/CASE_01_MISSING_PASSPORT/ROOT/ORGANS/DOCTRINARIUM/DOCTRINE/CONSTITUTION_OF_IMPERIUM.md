---
document_id: CONSTITUTION_OF_IMPERIUM
schema_version: DOCTRINE_DOCUMENT_V0_1A
document_role: SYSTEM_CONSTITUTION_AND_OPERATIONAL_LAW
status: CANON_CANDIDATE_OWNER_REVIEW_REQUIRED
canon_for_real_task_execution: false
owner_approval_required: true
doctrinarium_priority: 2
language: en
created_for_task_context: IMPERIUM_DOCTRINARIUM_PRIMARY_DOCTRINE_TRIAD_V0_1A
---

# Constitution of Imperium

## 1. Purpose

The Constitution of Imperium defines the operational structure of IMPERIUM.

It defines:
- what IMPERIUM is;
- what entities exist inside it;
- how tasks are created, routed, executed, audited, and handed off;
- what organs are and what they are not;
- what contours are;
- how evidence, receipts, manifests, hashes, and current state work;
- how bootstrap, canon candidate, canon, interim, and final states differ;
- how continuity is preserved across chats, agents, and execution contours;
- how user interfaces such as Sanctum must behave;
- how Doctrinarium, Passport of Emperor, and Codex Imperium relate to the task pipeline.

This document is a primary Doctrinarium input document.

Until Owner approval, this document remains a canon candidate only.

---

## 2. Sovereignty and Authority

The Owner, also called the Emperor in IMPERIUM doctrine, is the supreme authority of IMPERIUM.

No agent, organ, script, tool, chat, worker contour, UI, automation, or future subsystem may replace the Owner.

The Constitution defines system structure.  
It does not replace the Owner.

Doctrinarium validates doctrine and law.  
It does not replace the Owner.

Inquisition audits evidence and detects violations.  
It does not replace the Owner.

Sanctum displays and controls system surfaces.  
It does not replace the Owner.

THRONE may later become a canon admission or ultimate canon truth center, but it does not replace the Owner.

---

## 3. Doctrine Triad

The first three primary meaning-scope documents of IMPERIUM are:

1. `PASSPORT_OF_EMPEROR.md`
2. `CONSTITUTION_OF_IMPERIUM.md`
3. `CODEX_IMPERIUM.md`

Their roles are distinct.

### 3.1 Passport of Emperor

The Passport defines Owner authority:
- who decides;
- what cannot be delegated;
- what requires explicit Owner approval;
- how Owner acceptance is recognized;
- what actions must stop without Owner approval.

### 3.2 Constitution of Imperium

The Constitution defines system structure:
- entities;
- organs;
- contours;
- task execution model;
- evidence model;
- source-of-truth layers;
- continuity model;
- UI boundaries.

### 3.3 Codex Imperium

The Codex defines mandatory laws:
- prohibitions;
- required evidence;
- blocking rules;
- violation verdicts;
- law enforcement requirements.

Doctrinarium must read all three before allowing real task execution.

---

## 4. Truth Layers

IMPERIUM must not rely on a single weak truth surface.

Truth is layered.

### 4.1 Owner Authority Layer

The Owner is the highest decision authority.

Owner decisions are required for:
- acceptance;
- canon approval;
- baseline acceptance;
- final acceptance;
- destructive actions;
- major overrides.

### 4.2 Doctrine Layer

The doctrine layer contains:
- Passport of Emperor;
- Constitution of Imperium;
- Codex Imperium;
- doctrine indices;
- law registries;
- approval artifacts.

Doctrine defines what the system is allowed to consider legitimate.

### 4.3 Operational Evidence Chain

The operational evidence chain contains:
- receipts;
- manifests;
- hashes;
- current state files;
- owner decision artifacts;
- audit reports;
- finalization receipts;
- continuity candidates or packs.

Operational work must rely on this evidence chain, not on chat memory.

### 4.4 Organ Report Layer

Organs may provide:
- self-reports;
- health checks;
- validation reports;
- audit reports;
- status files.

Organ reports are evidence inputs, not final truth by themselves.

### 4.5 UI Display Layer

Sanctum, Explorer, and future panels may display status and trigger checks.

UI display is not truth.

A green UI state is invalid unless backed by:
- Doctrinarium validation;
- Inquisition audit when relevant;
- Administratum current state;
- receipts, hashes, and manifests;
- Owner decision when required.

### 4.6 THRONE Future Canon Layer

THRONE may later become a canon admission or ultimate canon truth center.

Until THRONE is explicitly introduced by Owner-approved task, local operational work relies on:
- PC operational evidence chain;
- Doctrinarium gates;
- Inquisition audits;
- Administratum memory and current state.

THRONE absence must not be used to fake canon.  
THRONE absence must not stop all bootstrap and candidate development unless the specific task requires THRONE.

---

## 5. Core Entities

### 5.1 TASK

A TASK is a named unit of work with a unique `TASK_ID`.

A task must have:
- task name;
- task recipe or launch card;
- scope;
- allowed actions;
- forbidden actions;
- expected artifacts;
- receipts;
- current state.

No serious work may proceed without a clear `TASK_ID`.

### 5.2 RUN

A RUN is a specific execution instance of a task or stage.

A run must have a `RUN_ID` when evidence needs to distinguish multiple executions.

### 5.3 STAGE

A STAGE is an atomic step inside a task.

A stage must have:
- `STAGE_ID`;
- purpose;
- inputs;
- outputs;
- pass criteria;
- executor;
- required organs;
- forbidden paths;
- receipt requirements.

### 5.4 ORGAN

An ORGAN is a functional control or execution domain inside IMPERIUM.

An organ is not real merely because a folder exists.

A real organ must have, at minimum:
- `README.md`;
- `ORGAN_STATUS.json`;
- `ORGAN_CONTRACT.json`;
- scripts or explicit non-script role;
- receipts;
- allowed write roots;
- forbidden roots;
- entrypoints;
- self-report or equivalent status report;
- validation receipt;
- known limitations.

### 5.5 CONTOUR

A CONTOUR is an execution or control environment.

Current and future contours may include:
- PC;
- VM2;
- THRONE;
- other worker or review environments.

A contour must never become source of truth by itself.

### 5.6 RECEIPT

A RECEIPT is a machine-readable proof of an action, check, stage, audit, or decision.

A receipt must include:
- schema version;
- task id;
- run id when required;
- actor;
- organ or phase;
- inputs;
- outputs;
- hashes where applicable;
- verdict;
- blockers;
- next action;
- timestamp.

No receipt means no proof.

### 5.7 ARTIFACT

An ARTIFACT is an output of work.

An artifact must have:
- path;
- purpose;
- relation to task/stage;
- hash when meaningful;
- manifest entry when packaged.

### 5.8 MANIFEST

A MANIFEST lists files, roles, paths, and package structure.

A manifest must not include self-referential final zip entries unless the packaging policy explicitly supports it.

### 5.9 HASH

A HASH proves file identity at a point in time.

A hash alone is not full truth.  
It must be tied to path, manifest, receipt, or task context.

### 5.10 CURRENT_STATE

`CURRENT_STATE` is the current evidence-based state of a task, organ, or system surface.

It must include:
- status;
- current stage;
- blocker;
- next action;
- do-not-do list;
- latest receipts;
- latest artifacts;
- source-of-truth references;
- last verified time.

### 5.11 CONTINUITY PACK

A CONTINUITY PACK is a handoff package for a new chat, agent, or contour.

It must include enough evidence to continue without relying on chat memory.

### 5.12 OWNER_DECISION

An OWNER_DECISION is an artifact that records a system-relevant decision by the Owner.

Owner decision artifacts are required for:
- acceptance;
- canon approval;
- baseline acceptance;
- final acceptance;
- destructive permission;
- major overrides.

---

## 6. Task Execution Model

A real task must follow the organ-gated pipeline.

The default pipeline is:

```text
Owner goal
→ TASK_ID
→ TASK_RECIPE
→ Doctrinarium preflight
→ Officio Agentis scope
→ Administratum memory/current state
→ Astronomicon route/stage map
→ Mechanicus script/tool resolution
→ Servitor execution
→ Inquisition audit
→ Administratum current state update
→ continuity candidate or pack
→ Owner / Logos-Prime / Logos-Speculum review
```

A task that bypasses this pipeline must be explicitly labeled:
- bootstrap;
- experimental;
- manual;
- emergency;
- or owner-authorized exception.

No task may claim full real execution readiness by bypassing the gate sequence.

---

## 7. Organ Model

### 7.1 Organ Recognition

An organ may be recognized conceptually before it is operational.

Recognition does not equal readiness.

Folder presence does not equal organ existence.

A task may mention an organ, but Doctrinarium decides whether that organ meets the required standard for the requested mode.

### 7.2 Organ Status Levels

Organs may have the following statuses:

```text
NOT_FOUND
FOLDER_ONLY
PLACEHOLDER
SCAFFOLD
BOOTSTRAP
CANON_CANDIDATE
CANON_V0_1
DEGRADED
BLOCKED
DEPRECATED
UNKNOWN
```

### 7.3 Status Meanings

- `NOT_FOUND`: required organ was not found.
- `FOLDER_ONLY`: folder exists, but required files are missing.
- `PLACEHOLDER`: conceptual or draft material exists, not operational.
- `SCAFFOLD`: basic structure exists, not proven by execution.
- `BOOTSTRAP`: limited execution proof exists, not canon.
- `CANON_CANDIDATE`: structured and reviewable, pending Owner approval.
- `CANON_V0_1`: Owner accepted within defined scope.
- `DEGRADED`: previously valid or useful, but currently blocked or limited.
- `BLOCKED`: cannot be used until repaired or approved.
- `DEPRECATED`: old surface, not active.
- `UNKNOWN`: unclassified and not trusted.

### 7.4 No Organ by Folder Name

A folder named after an organ does not make that organ real.

Doctrinarium must validate:
- contract;
- status;
- scripts;
- receipts;
- self-report;
- allowed writes;
- forbidden roots;
- current blockers.

### 7.5 Organ Contract

Each operational organ must have an `ORGAN_CONTRACT.json`.

It must define:
- responsibilities;
- explicitly excluded responsibilities;
- reads;
- writes;
- allowed write roots;
- forbidden roots;
- entrypoints;
- required scripts;
- required receipts;
- self-report;
- health check;
- dependencies;
- callers allowed;
- outputs;
- stop conditions;
- fake-green risks;
- owner-approval-required actions;
- current blockers.

---

## 8. Active Organ Cycle

The current local active task pipeline uses the following organs.

### 8.1 Doctrinarium

Doctrinarium is the doctrine, law, task permission, and organ-standard gate.

It reads:
- Passport;
- Constitution;
- Codex;
- law registry;
- task recipe;
- organ contracts;
- organ statuses.

It writes:
- validation receipts;
- blocker reports;
- doctrine status reports;
- caller responses.

It does not execute task stages.

### 8.2 Officio Agentis

Officio Agentis defines agent behavior and task-specific scopes.

It answers:
- who is the acting agent;
- what actions are allowed;
- what actions are forbidden;
- what evidence is required;
- when the agent must stop;
- how the agent reports to the Owner.

It does not decide task truth.

### 8.3 Administratum

Administratum owns operational memory.

It maintains:
- event chronology;
- task timelines;
- current state;
- active task registry;
- receipt indexes;
- continuity candidates and packs.

It is memory and registry, not final authority.

### 8.4 Astronomicon

Astronomicon defines routes, stage maps, pass criteria, dependencies, and future route.

It answers:
- what stages exist;
- what stage is current;
- what pass criteria apply;
- what is next;
- what is blocked.

It does not execute scripts.

### 8.5 Mechanicus

Mechanicus owns tools, scripts, validators, script registries, and execution machinery.

It answers:
- which script is allowed;
- where the script is;
- what hash it has;
- what inputs it accepts;
- what outputs it may write;
- what safety level applies.

It does not decide task meaning.

### 8.6 Inquisition

Inquisition audits evidence, scope, duplicates, forbidden paths, fake green, and protocol violations.

It answers:
- did the task create forbidden dirt;
- are receipts missing;
- are hashes inconsistent;
- is baseline/final/canon claimed without evidence;
- did execution exceed scope.

It does not repair by itself.

---

## 9. Future and Inactive Organs

The following organs may be part of the wider constitutional frame but are not required in the current local execution cycle unless explicitly invoked by a task.

### 9.1 THRONE

THRONE is future canon admission or ultimate truth center.

It is not active by default in the current local pipeline.

No task may contact THRONE without explicit Owner approval.

### 9.2 Custodes

Custodes is a future protection, security, and guard layer.

It is not required for current bootstrap/candidate local tasks unless the task explicitly requires security enforcement.

### 9.3 Schola Imperialis

Schola Imperialis is a future training, learning, and doctrine education layer.

It is not required for current local execution.

### 9.4 Strategium

Strategium is a strategic planning and priority layer.

It is not part of the immediate organ-gated execution cycle unless explicitly included later.

---

## 10. Contour Model

### 10.1 PC Contour

PC is the local orchestration, registry, memory, verification, and final bundle contour.

PC may:
- coordinate tasks;
- hold active operational evidence;
- run local scripts;
- verify returned worker results;
- build continuity candidates;
- host Doctrinarium, Administratum, and other organ files.

PC must not fake canon or finality.

### 10.2 VM2 Contour

VM2 is a future worker contour.

Desired future mode:

```text
VM2 receives TASK_ID
→ reads task card / Explorer / Administratum from PC through defined access
→ executes only assigned stage
→ returns artifacts, receipts, hashes, and logs to PC
→ PC verifies before admission into task evidence
```

VM2 is not source of truth.

VM2 cannot execute real tasks without:
- Owner approval;
- Officio Agentis VM2 scope;
- Doctrinarium gate;
- Astronomicon stage assignment;
- Mechanicus tool contract;
- PC-side Inquisition verification.

### 10.3 Chat Contour

Chat is a communication surface.

Chat is not source of truth.

A new chat must continue by reading:
- current state;
- continuity pack;
- receipts;
- doctrine;
- task recipe;
- next action;
- do-not-do list.

### 10.4 THRONE Contour

THRONE is future canon/admission contour.

Until introduced by Owner-approved task, THRONE must not be contacted or treated as active operational dependency.

---

## 11. Source of Truth Model

No single chat message, UI panel, folder, script result, or receipt is enough by itself to become truth.

Operational truth requires evidence chain.

A strong evidence chain may include:
- doctrine documents;
- task recipe;
- agent scope;
- stage map;
- current state;
- receipts;
- manifest;
- hashes;
- audit reports;
- owner decisions.

If the evidence chain is incomplete, the status must be:
- candidate;
- partial;
- blocked;
- degraded;
- owner decision required;
- or unknown.

No fake certainty is allowed.

---

## 12. Receipt and Evidence Law

Evidence must be machine-readable where possible.

A valid receipt should include:
- schema version;
- task id;
- run id when required;
- stage id when applicable;
- actor;
- organ or phase;
- input paths;
- output paths;
- hashes;
- verdict;
- blockers;
- next action;
- timestamp.

Evidence rules:
- no receipt means no proof;
- receipt without hash context is weak proof;
- hash without path context is incomplete proof;
- manifest with self-reference is suspect or invalid;
- final package without external finalization receipt is not clean final;
- Owner acceptance cannot be inferred from technical pass.

---

## 13. Bootstrap, Canon Candidate, Canon, Interim, and Final

### 13.1 Bootstrap

Bootstrap is limited proof mode.

Bootstrap may prove:
- a script can run;
- a receipt can be created;
- a pipeline rail exists;
- a smoke test passes.

Bootstrap does not prove:
- canon;
- real execution readiness;
- full organ maturity;
- continuity green;
- final acceptance.

### 13.2 Canon Candidate

Canon candidate means structured, reviewable, and prepared for Owner decision.

Canon candidate is not final canon.

### 13.3 Canon V0.1

Canon V0.1 means Owner accepted the doctrine, organ, or structure within a defined scope.

Canon V0.1 is scoped and versioned.  
It is not eternal unconditional truth.

### 13.4 Interim

Interim means temporary handoff or incomplete state.

Interim must not be treated as final.

### 13.5 Final

Final requires:
- finalization receipt;
- manifest;
- hashes;
- audits as required;
- Owner acceptance when required;
- no unresolved hard blockers.

---

## 14. Continuity Law

IMPERIUM must preserve continuity without relying on chat memory.

Every active task must maintain:
- `CURRENT_STATE`;
- next action;
- do-not-do list;
- blocker list;
- receipt chain;
- latest artifacts;
- latest hashes;
- continuity candidate or continuity pack.

A continuity pack must clearly state:
- what is proven;
- what is not proven;
- what is current;
- what is blocked;
- what must not be done;
- what the next agent should read first.

If continuity is ambiguous, the correct status is:
`BLOCKED_AMBIGUOUS_CONTINUITY`.

---

## 15. UI Law

Sanctum, Explorer, and future organ panels are interfaces.

They may:
- display state;
- help navigation;
- trigger approved checks;
- show receipts, blockers, and organ status;
- help the Owner understand the system.

They may not:
- create truth;
- bypass Doctrinarium;
- bypass Inquisition;
- accept baselines;
- hide blockers;
- show green without evidence.

A UI button must not be stronger than the gate behind it.

---

## 16. OBSERVED Law

`OBSERVED` is source material, map material, or evidence surface.

`OBSERVED` is not active canon by itself.

Anything extracted from `OBSERVED` must be:
- snapshotted;
- hashed;
- reviewed;
- normalized;
- placed into active doctrine or artifact paths;
- registered;
- receipted.

No file from `OBSERVED` becomes active truth merely because it exists.

---

## 17. Amendment Procedure

Changing the Constitution requires:

1. A task id.
2. A reason.
3. A source or issue description.
4. A proposed diff.
5. Owner review.
6. Owner decision artifact when accepted.
7. Updated doctrine index.
8. Updated hash.
9. Validation receipt.

No agent may silently amend the Constitution.

Emergency amendments must be:
- explicit;
- scoped;
- recorded;
- reviewed later.

---

## 18. Relation to Codex Imperium

The Constitution defines system structure.

The Codex defines mandatory laws and prohibitions.

Doctrinarium validates both.

If the Constitution and Codex conflict, the task must stop with:
`BLOCKED_SEMANTIC_CONFLICT`.

The Owner must decide how to resolve the conflict.

---

## 19. Doctrine Status and Use

This Constitution is a primary doctrine input for Doctrinarium.

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
- its hash must be recorded in `DOCTRINE_INDEX.json`;
- Doctrinarium must block real tasks if it is missing, altered, unregistered, or contradicted.
