# Administratum MVP Stage Prompts v0.1

task_id: TASK-20260514-BUILD-ADMINISTRATUM-MVP-V0_1
created_utc: 2026-05-14T21:15:35Z
canonical_language: English
owner_chat_language: Russian

## Put These Files Here

Recommended repo path:

```text
E:\IMPERIUM\ORGANS\ADMINISTRATUM\REGISTRY\TASKS\TASK-20260514-BUILD-ADMINISTRATUM-MVP-V0_1\PROMPTS
```

Relative repo path:

```text
ORGANS/ADMINISTRATUM/REGISTRY/TASKS/TASK-20260514-BUILD-ADMINISTRATUM-MVP-V0_1/PROMPTS
```

## Files

1. `01_STAGE-01_REGISTER_ADMINISTRATUM_MVP_FRAME.md`
2. `02_STAGE-02_BUILD_ADDRESS_BOOK_V0_1.md`
3. `03_STAGE-03_BUILD_CHRONICLE_MEMORY_V0_1.md`
4. `04_STAGE-04_BUILD_TASK_LIFECYCLE_BACKEND_V0_1.md`
5. `05_STAGE-05_SYNTHETIC_SUCCESS_PROOF.md`
6. `06_STAGE-06_SYNTHETIC_FAIL_STOP_PROOF.md`

## Execution Logic

Servitor should execute prompts in order.

- Continue to next stage only after local green/self-check.
- Stop on a true blocker.
- Do not touch Astronomicon.
- Do not set READY_FOR_AGENT true.
- Do not sync VM2 without Owner command.
- Ideal expected autonomous stop point is:
  `STAGE-06-02-DELIBERATE-STAGE-2-FAILURE-AND-STOP`.

## Notes

These files are canonical repo prompt artifacts and are intentionally English-only.
Russian belongs in live chat and controlled UI/i18n resources.
