# Task Spec

## Task ID

`TASK-NEWGEN-INQUISITION-PATH-CONTROL-KPD-LLM-HARDWARE-COST-AND-WEB-RESEARCH-MATRICES-VM3-V0_3`

## Mission

Strengthen Inquisition matrices so IMPERIUM can measure the real cost and efficiency of each task, not only PASS/FAIL.

The task must produce a practical matrix pack that can answer:

- How expensive was this task for the LLM/context/output?
- How expensive was it for local hardware and local organ-agent execution?
- How much manual Owner work did it require?
- Did it save cost by being smarter, or did it fake savings by dropping evidence?
- Did the local step pass inside its own scope?
- Which global caps are merely carried and must not automatically poison the local step verdict?
- What should be improved next to reduce cost without reducing quality?

## Required work streams

### 1. Matrix hardening

Create or update matrices for:

- local step verdict;
- global carried caps;
- path control;
- KPD / efficiency;
- LLM cost / context / output;
- local hardware and runtime cost;
- local organ-agent cost;
- web research cost and source quality;
- artifact retention cost;
- Throne evidence bundle value;
- fake cost saving detection;
- matrix strength comparison against earlier matrix versions.

### 2. Local hardware and local organ-agent cost metrics

Add mandatory fields for:

- wall time;
- CPU time if measurable;
- peak memory if measurable;
- disk bytes written/read if measurable;
- bundle sizes;
- network transfer size;
- SSH call count;
- script count;
- validator count;
- local organ-agent/tool invocations;
- retries/failures;
- manual Owner interactions.

If a metric cannot be measured yet, record `UNKNOWN_NOT_INSTRUMENTED` and propose an instrumentation method. Do not invent numbers.

### 3. Deep web research

Perform deep web research on current best practices and tools for reducing LLM cost, context size, output bloat, agent runtime overhead, retrieval cost, prompt cost, validation cost, and local automation cost without quality loss.

The research must include official/primary sources when possible, and credible engineering sources when official docs are unavailable.

All research data must be exported into a ZIP dossier and transferred to the PC IMPERIUM context folder by SSH.

### 4. Practical recommendations

Produce a ranked action list:

- can start now;
- requires small Skill;
- requires validator;
- requires Throne support;
- requires future Custodes;
- should be rejected as fake economy.

### 5. VM2 next-step preparation

Create a VM2 handoff note for the next task, including what VM2 must read first, what context packs it should receive, and what must not be assumed.

## Scope boundaries

Allowed:

- repo artifacts under IMPERIUM_NEW_GENERATION;
- Inquisition matrix specs, examples, schemas, validator seed;
- reports and receipts;
- web research dossier;
- SSH transfer to PC context folder using existing route only;
- commit and push for non-BLOCK result.

Forbidden:

- no IDE/WARP runtime implementation;
- no Custodes implementation;
- no Codex CLI bridge implementation;
- no destructive cleanup of existing artifacts;
- no private key changes;
- no public server exposure;
- no fake measured costs.
