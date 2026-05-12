# IMPERIUM — FIRST 12 STEPS OWNER DECISIONS 2026-05-12

## Статус

Тип: Owner / Logos-Prime decision note.

Основание: Kiro review of `IMPERIUM_FIRST_12_STEPS_PLAN_FOR_KIRO_REVIEW_V0_1.md`.

Текущая цель: подготовить первый VM2 construction step к реальному строительству первых 4 органов прозрения.

## Принятый verdict по Kiro review

Kiro review принят как advisory input.

Основной verdict:

GOOD / NEEDS MINOR SPLITS

План считается достаточно зрелым, чтобы начинать VM2 construction, но только малыми шагами.

## Принятая corrected sequence

Step 0: Baseline — DONE  
Step 1: Organ folder standard document  
Step 2: Missing 4 organ scaffolds + ORGAN_REGISTRY sync to 10  
Step 3: Sanctum HUD data service v0.1  
Step 4: Warning flood cleanup plan  
Step 5: Warning flood fix execution — PC-only  
Step 6: Doctrinarium real preflight v0.1  
Step 7: Administratum task registration + address packet v0.1  
Step 8: Officio Agentis corridor packet v0.1  
Step 9a: Astronomicon General Task registration v0.1  
Step 9b: Astronomicon Stage Map generation v0.1  
Step 10: First-four-organs work packet generator  
Step 11: Sanctum HUD minimal integration  
Step 12: First-four-organs dry-run  

## Owner decisions по вопросам Kiro

### 1. Warning flood fix

`git rm --cached` для continuity packs допустим только после отдельного плана и Owner approval.

Физически файлы не удалять.

Перед execution желательно иметь backup / rollback note.

Execution этого шага — PC-only, не VM2.

### 2. Sanctum HUD v0.1

Для v0.1 достаточно лёгкого HUD:

Health: DEGRADED | Task: ... | Stage: ...

Не надо сразу делать 10 тяжёлых панелей.

Цель — реальная data service + минимальная интеграция без потери FPS.

### 3. Agent profiles

Нужен отдельный профиль:

VM2_SERVITOR.json

Потому что VM2 имеет отдельные правила:

- no push
- no commit
- bundle-only output
- short final verdict
- strict scope

### 4. General Task format

v0.1 формат:

Markdown для Owner-readable задачи + machine-readable JSON record рядом.

Не только JSON, потому что Owner должен читать и править руками.

### 5. Dry-run task

Первый dry-run должен быть фейковый/test task.

Цель dry-run — проверить цепочку органов, а не решить полезную задачу.

### 6. Clarification loop

Kiro / Speculum clarification обязателен для крупных General Tasks.

Малые operational tasks могут пропускать clarification loop, если Owner явно разрешает.

### 7. DEGRADED vs BLOCKED

Принято:

BLOCKED — если сломан один из первых 4 органов прозрения.

DEGRADED — если неполные/scaffold-only органы 5–10.

Preflight не должен возвращать CLEAR, пока система содержит scaffold-only органы или missing mechanisms.

## Принятый первый VM2 construction target

TASK-20260512-ORGAN-STANDARD-AND-SCAFFOLDS-V0_1

Scope:

1. Создать `DOCS/OWNER_DOCTRINE/ORGAN_FOLDER_STANDARD_V0_1.md`
2. Создать scaffold для:
   - `ORGANS/CUSTODES/`
   - `ORGANS/STRATEGIUM/`
   - `ORGANS/SCHOLA_IMPERIALIS/`
   - `ORGANS/THRONE/`
3. В каждом органе:
   - `README.md`
   - `ORGAN_STATUS.json`
   - `ORGAN_CONTRACT.json`
   - `PORTS/`
   - `SCHEMAS/`
   - `SCRIPTS/`
   - `UTILITY/`
4. Обновить `REGISTRY/ORGAN_REGISTRY.json` до 10 органов.

Not included:

- no Sanctum changes
- no script logic
- no warning flood fix
- no workflow automation
- no Freelance Console

## Статус после этого decision note

После commit этого файла можно давать VM2 первый construction prompt.