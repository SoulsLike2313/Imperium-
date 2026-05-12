# Sanctum Adaptive Operator Layer v0.1

Статус: support hardening vertical slice (не финальный Sanctum).
Task: `TASK-20260513-SANCTUM-ADAPTIVE-OPERATOR-LAYER-V0_1`

## Что добавлено

1. Backend state collector:
- `TOOLS/build_sanctum_state_v0_1.py`
- генерирует:
  - `.imperium_runtime/sanctum/state/SANCTUM_STATE_V0_1.json`
  - `.imperium_runtime/sanctum/state/SANCTUM_STATE_VERDICT.md`
  - `.imperium_runtime/sanctum/state/SANCTUM_STATE_RECEIPT.json`

2. Sanctum adaptive checker:
- `TOOLS/check_sanctum_adaptive_operator_layer_v0_1.py`
- пишет отчёты в:
  - `.imperium_runtime/sanctum/checks/`

3. Frontend vertical slice в `SANCTUM/sanctum_v0_29_qt.py`:
- добавлен `AdaptiveOperatorPanel` (вкладка `Operator Layer`);
- отображает реальные секции:
  - Git Truth;
  - Bundle Index;
  - Latest Receipts;
  - SCRIPTORIUM;
  - ARSENAL;
  - Act3 Spine;
  - Warning/Stale;
  - Operator Actions.

4. Обновлён Script Registry:
- добавлены записи для:
  - `TOOLS/build_sanctum_state_v0_1.py`
  - `TOOLS/check_sanctum_adaptive_operator_layer_v0_1.py`

## Источники истины, которые читает слой

- Git CLI (`git rev-parse`, `git ls-remote`, `git status`);
- `.imperium_runtime/administratum/git_cli_check/GIT_CLI_CHECK_RESULT.json`;
- `.imperium_runtime/administratum/act3_address_truth_capability_spine_check/...`;
- `REGISTRY/SCRIPT_REGISTRY.json`;
- `REGISTRY/ARSENAL_TOOL_INDEX.json`;
- `REGISTRY/ARSENAL_INSTALL_STATUS.json`;
- `ORGANS/ADMINISTRATUM/REGISTRY/ZONE_REGISTRY_V0_1.json`;
- `ORGANS/ADMINISTRATUM/REGISTRY/TRUTH_SOURCE_REGISTRY_V0_1.json`;
- `ORGANS/ADMINISTRATUM/REGISTRY/CAPABILITY_SPINE_V0_1.json`;
- `ORGANS/ADMINISTRATUM/REGISTRY/WARNING_STALE_BASELINE_V0_1.json`;
- VM2 handoff output: `/home/vboxuser2/IMPERIUM_WORK/_handoff_out/`.

## Принципы безопасности

- Sanctum не является source of truth;
- PASS/WARNING/BLOCKED/UNKNOWN/STALE строятся из файлов, receipts, registries;
- owner-gated или destructive действия не автоматизированы;
- commit/push/sync не выполняются из этого слоя;
- для PC intake есть command-prep блок, а не auto-commit.

## Что намеренно не реализовано в v0.1

- Полный MetaOS orchestration;
- автоматический commit/push/sync;
- unsafe destructive actions;
- Act 4 коридор;
- построение Inquisition.

## v0.30 Repair Slice (2026-05-13)

Цель этого ремонта: сделать Sanctum практичным операторским кокпитом без fake green.

Что исправлено:
- UI identity обновлён до `IMPERIUM Sanctum v0.30 Adaptive Operator Dashboard`.
- Добавлен явный слой-лейбл: `Sanctum v0.30 UI shell + Adaptive Operator Layer v0.1`.
- Убрано hardcoded stale task truth из mission core; верхняя truth-полоса и карта теперь читают live state.
- `Refresh State` вызывает реальный `TOOLS/build_sanctum_state_v0_1.py`, затем сразу перерисовывает панели.
- Bundle list/fetch переведены на VM2 outbox ` /home/vboxuser2/IMPERIUM_WORK/_handoff_out ` (с fallback на legacy outbox).
- Bundle rows показывают evidence-based статусы (`REMOTE_ONLY`, `SHA_MISSING`, `SHA_PASS`, `SHA_FAIL`, `STALE`, ...).
- `Fetch Selected/Fetch Latest` копируют `.zip` и `.sha256` (если есть) и делают локальную SHA-проверку.
- На non-Windows контуре fetch не притворяется рабочим: отображается `COMMAND_PREP_ONLY` с командой для PC.
- Улучшены визуал и layout: более читаемый truth bar, расширенный operator tab, улучшенный planet/orbits/synapse рендер.

Ограничения:
- Визуальный QA (фактический look/feel в Windows Qt) требует ручной проверки на PC contour.
- Sanctum не выполняет commit/push/sync и не объявляет PASS без file/receipt evidence.
