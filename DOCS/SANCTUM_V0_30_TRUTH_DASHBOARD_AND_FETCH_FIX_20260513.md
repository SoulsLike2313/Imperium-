# Sanctum v0.30 Truth Dashboard And Fetch Fix (2026-05-13)

Task: `TASK-20260513-SANCTUM-V0_30-TRUTH-DASHBOARD-LAYOUT-AND-BUNDLE-FETCH-FIX-V0_1`

## Scope

Вертикальный repair slice для:
- truth binding в UI;
- layout/hud readability;
- bundle refresh/fetch restore;
- честной маркировки WARNING/UNKNOWN/STALE/BLOCKED.

## Backend truth sources

- `.imperium_runtime/sanctum/state/SANCTUM_STATE_V0_1.json`
- `.imperium_runtime/administratum/git_cli_check/GIT_CLI_CHECK_RESULT.json`
- `.imperium_runtime/administratum/act3_address_truth_capability_spine_check/...`
- `.imperium_runtime/sanctum/checks/SANCTUM_ADAPTIVE_OPERATOR_LAYER_CHECK.json`
- `REGISTRY/SCRIPT_REGISTRY.json`
- `REGISTRY/ARSENAL_TOOL_INDEX.json`
- `REGISTRY/ARSENAL_INSTALL_STATUS.json`
- `ORGANS/ADMINISTRATUM/REGISTRY/*` (Act 3 spine)

## UI repairs

- Window title и version badge обновлены до v0.30.
- Верхняя truth bar показывает HEAD/count/tree/match/generated-at/verdict.
- Mission core больше не содержит hardcoded старый TASK как «текущую истину».
- Центр карты показывает runtime-driven chips и status-colored organ nodes.
- Добавлены synapse-like связи между узлами для читаемого state-flow.

## Bundle refresh/fetch repairs

- Remote list идёт из `/home/vboxuser2/IMPERIUM_WORK/_handoff_out` (fallback: legacy outbox).
- Bundles сортируются newest-first.
- Для строк отображаются `bundle_status` и `sha256_pair_status`.
- `Fetch Selected` и `Fetch Latest` копируют `.zip` + optional `.sha256`.
- После fetch выполняется local SHA verification:
  - `SHA_PASS` / `SHA_FAIL` / `SHA_MISSING` / `UNKNOWN`.
- На non-Windows контуре fetch переводится в `COMMAND_PREP_ONLY` с явной PC-командой.

## Safety guarantees

- Нет auto commit/push/sync.
- Нет destructive reset actions.
- Нет fake PASS: при отсутствии доказательств выводится WARNING/UNKNOWN/STALE/BLOCKED.
