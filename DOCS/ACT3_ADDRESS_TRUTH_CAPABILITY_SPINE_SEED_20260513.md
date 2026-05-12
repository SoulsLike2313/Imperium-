# Act 3 Address / Truth / Capability Spine Seed (2026-05-13)

Статус: seed stage, machine-checkable foundation.
Task: `TASK-20260513-ACT3-ADDRESS-TRUTH-CAPABILITY-SPINE-SEED-V0_1`
Stage: `STAGE-001-ACT3-SEED-REGISTRIES-CHECKER-AND-BASELINES-V0_1`
Baseline head: `36ffba1883d895d3f0a880de6b72cd5046be2c24`
Exact tree URL: `https://github.com/SoulsLike2313/Imperium-/tree/36ffba1883d895d3f0a880de6b72cd5046be2c24`

## Зачем Act 3 шире, чем список адресов

Act 3 фиксирует не только пути, но и проверяемые правила доверия:
- где лежат зоны и кто их владелец;
- где источник истины Git, а где только локальная/временная среда;
- какие capabilities реально доступны, owner-gated или неизвестны;
- какие предупреждения считаются нормой seed-этапа и что блокирует работу.

## Address Spine

Address Spine задаёт машиночитаемую карту зон:
- tracked repo-зоны;
- runtime/local-only зоны;
- PC/VM2 handoff-точки;
- advisory/input-зоны;
- SCRIPTORIUM/ARSENAL регистры.

Реализация: `ORGANS/ADMINISTRATUM/REGISTRY/ZONE_REGISTRY_V0_1.json`.

## Truth Spine

Truth Spine задаёт приоритеты истины:
- exact SHA tree URL выше floating ссылок;
- равенство `HEAD == origin/master == remote/master` как базовая синхронизация;
- commit/push только на PC;
- VM2 только bundle contour;
- receipts выше chat-утверждений без evidence;
- runtime evidence ограничен контуром/временем;
- старый baseline `090c75...` для этой стадии помечен stale.

Реализация: `ORGANS/ADMINISTRATUM/REGISTRY/TRUTH_SOURCE_REGISTRY_V0_1.json`.

## Capability Spine

Capability Spine связывает выполнение с support layers:
- `REGISTRY/SCRIPT_REGISTRY.json` (SCRIPTORIUM);
- `REGISTRY/ARSENAL_TOOL_INDEX.json` и `REGISTRY/ARSENAL_INSTALL_STATUS.json` (ARSENAL);
- явные списки allowed/owner-gated/unknown;
- обязательные поля для будущих TASK/STAGE/RUN.

Реализация: `ORGANS/ADMINISTRATUM/REGISTRY/CAPABILITY_SPINE_V0_1.json`.

## Warning/Stale Baseline

Отдельный baseline фиксирует типовые риски seed-уровня:
- encoding/mojibake;
- stale/floating references;
- path mismatch;
- warning flood;
- fake green;
- raw advisory mistaken for doctrine;
- stale HEAD risk;
- dirty VM2 worktree risk.

Реализация: `ORGANS/ADMINISTRATUM/REGISTRY/WARNING_STALE_BASELINE_V0_1.json`.

## Как используется Kiro advisory

Kiro advisory (`KIRO_INQUISITION_SELF_BUILD_ADVISORY_20260513`) используется только как
`RAW_ADVISORY_INPUT_NOT_YET_RECONCILED` / `REGISTERED_RAW_ADVISORY_NOT_RECONCILED`.
Он не является doctrine и не является execution authority.

Advisory даёт требования к будущему self-build циклу органа:
- organ = contract + schemas + checks + receipts + self-report;
- Inquisition v0.1 строится позже через зарегистрированный коридор.

## Подготовка Act 4 и Act 5

Act 3 подготавливает Act 4:
- регистрационные spine-реестры;
- первый checker согласованности адрес/истина/capability;
- минимальные organ self-description schemas.

Act 3 подготавливает Act 5:
- вводит минимальные `organ_contract` и `organ_self_report` schemas;
- создаёт базу для первого self-descriptive organ build: Inquisition v0.1 через полный цикл IMPERIUM.

## Что намеренно не делается сейчас

- Не запускается Act 4 full corridor implementation.
- Не строится Inquisition v0.1 в этом пакете.
- Не переводится raw advisory в canon doctrine.
- Не выполняется broad cleanup warning debt.
