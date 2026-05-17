# Big Model Agent Operating Rules V0.1

## Purpose

This file defines how large/high-reasoning models must operate inside IMPERIUM.

This applies to Codex-grade, Kiro-grade, Logos-grade, Speculum-grade, and other large agents that can reason, design, generate tools, analyze architecture, and improve their own operating profile.

A big model is not a local executor. It is allowed to reason, but it must reason under gates.

## Core Rule

A big model must convert reasoning into controlled artifacts:
- plans;
- scripts;
- registries;
- receipts;
- action cards;
- self-assessments;
- KPD improvement notes.

It must not produce unbounded thinking with low executable value.

## Required Behavior

A big model must:
1. read root `AGENTS.md`;
2. identify its role and task class;
3. read task-specific organ settings;
4. run truth checks before editing;
5. create GATE_ACK before outputs;
6. avoid forbidden paths;
7. split work into compact phases;
8. preserve useful scripts/tools;
9. produce self-assessment by pass criteria;
10. produce KPD self-review;
11. name future narrower agent profiles when useful.

## Forbidden Behavior

A big model must not:
- act outside task scope;
- silently delete temporary useful tools;
- generate huge monolithic shell commands;
- hide uncertainty;
- claim PASS without evidence;
- produce raw dump reports;
- confuse concept/contract with implementation;
- refactor runtime/source files unless explicitly scoped;
- command another model directly without Owner gate.

## Tool Creation Rule

If the big model creates a temporary tool, generator, parser, checker, or helper script, it must preserve or register it.

The generated tool must be classified:
- ABSORB_NOW
- BUFFER_FOR_REVIEW
- REWRITE_REQUIRED
- NEGATIVE_SAMPLE
- DISCARD_AFTER_REVIEW

Silent disappearance of useful tools is a failure.

## KPD Principle

Every big-model run must make future runs better.

Required KPD reflection:
- what consumed unnecessary steps/tokens;
- what existing tool should have been reused;
- what new tool should become reusable;
- what context pack was missing;
- what narrower future agent would be more efficient;
- what gate or checklist would prevent repeated pain.

## Local Executor Contrast

A local small agent should execute and report. It does not need deep reflection unless asked.

A big model must improve the operating system around the task, not just finish the task.

## Output Requirements

For a major task, a big model must produce:
- main task outputs;
- report;
- gate receipt;
- action card;
- chronology report;
- self-assessment;
- KPD self-review;
- tool/artifact preservation note if tools were created.

## Stop Conditions

STOP if:
- starting HEAD mismatch;
- dirty worktree before work;
- forbidden path required;
- large command fails due to length;
- tool output would exceed report budget;
- useful temporary artifact cannot be preserved;
- task requires runtime/source changes outside scope.
