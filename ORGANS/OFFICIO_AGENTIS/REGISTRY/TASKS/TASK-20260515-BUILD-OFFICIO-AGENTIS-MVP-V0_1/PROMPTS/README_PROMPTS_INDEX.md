# Officio Agentis MVP Stage Prompts v0.1

task_id: TASK-20260515-BUILD-OFFICIO-AGENTIS-MVP-V0_1
created_utc: 2026-05-15T00:51:43Z
canonical_language: English
owner_chat_language: Russian

## Put These Files Here

Recommended repo path:

```text
E:\IMPERIUM\ORGANS\OFFICIO_AGENTIS\REGISTRY\TASKS\TASK-20260515-BUILD-OFFICIO-AGENTIS-MVP-V0_1\PROMPTS
```

Relative repo path:

```text
ORGANS/OFFICIO_AGENTIS/REGISTRY/TASKS/TASK-20260515-BUILD-OFFICIO-AGENTIS-MVP-V0_1/PROMPTS
```

## Files

1. `01_STAGE-01_OFFICIO_FOUNDATION_V0_1.md`
2. `02_STAGE-02_SERVITOR_CONTRACT_V0_1.md`
3. `03_STAGE-03_LOGOS_PRIME_CONTRACT_V0_1.md`
4. `04_STAGE-04_LOGOS_SPECULUM_CONTRACT_V0_1.md`
5. `05_STAGE-05_ADVISOR_SERVITOR_CONTRACT_V0_1.md`
6. `06_STAGE-06_OFFICIO_TEST_SUITE_V0_1.md`
7. `07_STAGE-07_INTEGRATION_POLICIES_V0_1.md`

## Execution Logic

Servitor should execute prompts in order.

- Continue to the next stage only after PASS.
- Stop on a true blocker.
- Do not touch Astronomicon.
- Do not modify Administratum MVP backend.
- Do not set READY_FOR_AGENT true.
- Do not sync VM2 without Owner command.
- Owner-facing stage summaries and comments must be Russian.
- Canonical machine artifacts must be English-only.

## Expected Final State

Officio Agentis MVP proves:
- role contracts;
- modes;
- response contracts;
- question policy;
- evidence policy;
- stop policy;
- language policy;
- prompt-writing policy;
- execution-boundary policy;
- deterministic dry-run behavior tests.
