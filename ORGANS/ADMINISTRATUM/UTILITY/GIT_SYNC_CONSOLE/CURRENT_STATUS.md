# CURRENT_STATUS — Administratum Git Sync Console v0.1

## Статус реализации
- Статус: реализован standalone-прототип v0.1 в рамках шага `VM2-BUILD-ADMINISTRATUM-GIT-SYNC-CONSOLE-V0_1`.
- Формат: single-file PySide6 utility + сопроводительная документация.
- Интеграция в Sanctum: **не выполнялась** (осознанно вне scope).

## Что реализовано
- Классы: `RepoRootDetector`, `GitCommandRunner`, `GitStatusService`, `GitDiffService`, `GitStageService`, `VerificationService`, `ReceiptWriter`, `GitSyncConsoleWindow`.
- Dataclass-модели: `CommandResult`, `FileEntry`, `SessionState`, `VerificationState`.
- UI-блоки:
  - верхняя панель (repo root, branch, local/upstream head, clean/dirty, refresh);
  - список changed files с фильтрами: `all`, `staged`, `unstaged`, `untracked`, `likely runtime/noise`;
  - diff/preview панель с кнопкой Copy;
  - панель проверок (Git CLI check, verify_repo, agent entrypoint check, optional pytest quick);
  - commit/push панель с staged summary.
- Безопасность v0.1:
  - subprocess только в `GitCommandRunner`;
  - `shell=True` не используется;
  - git file-команды используют `--` перед путями;
  - path-валидация на принадлежность к repo root;
  - discard untracked заблокирован;
  - push требует отдельного подтверждения;
  - при не-запущенных checks или non-PASS checks push требует явный Owner override (`OWNER_OVERRIDE_PUSH`).
- Runtime outputs утилиты ограничены каталогом:
  - `.imperium_runtime/administratum/git_sync_console/`.

## Что не реализовано
- Open file/folder actions (осознанно не реализовано в v0.1).
- Интеграция с `command_gateway` (пока временный subprocess adapter).
- Интеграция в Sanctum (не входило в задачу).

## Известные ограничения
- На VM2 отсутствует пакет `PySide6`, поэтому GUI-launch не проверен на этой машине.
- `verify_repo.py` остаётся `PASS_WITH_WARNINGS` из-за существующего warning flood (legacy debt), blockers=0.
- `git cli check` после изменений даёт `PASS_WITH_WARNINGS`, так как рабочее дерево ожидаемо dirty новыми файлами.

## Как проверялось на VM2
- `python3 -m py_compile ORGANS/ADMINISTRATUM/UTILITY/GIT_SYNC_CONSOLE/git_sync_console_v0_1.py` -> PASS
- `python3 scripts/check_agent_entrypoint.py` -> PASS
- `python3 scripts/verify_repo.py` -> PASS_WITH_WARNINGS (blockers=0)
- `./TOOLS/run_administratum_git_cli_check.sh` -> PASS_WITH_WARNINGS (dirty worktree)
- `python3 -c "import PySide6"` -> FAIL (`ModuleNotFoundError`)

## Какие файлы изменены/созданы
- `ORGANS/ADMINISTRATUM/UTILITY/GIT_SYNC_CONSOLE/git_sync_console_v0_1.py`
- `ORGANS/ADMINISTRATUM/UTILITY/GIT_SYNC_CONSOLE/README.md`
- `ORGANS/ADMINISTRATUM/UTILITY/GIT_SYNC_CONSOLE/CURRENT_STATUS.md`

## Что должен проверить PC Owner
1. Установлен ли `PySide6` на PC и запускается ли GUI.
2. Логику commit/push guard-диалогов и Owner override.
3. Корректность filters и block untracked discard.
4. Создание receipts в `.imperium_runtime/administratum/git_sync_console/` при реальном UI-использовании.
5. Поведение на реальном merge/local-change сценарии перед production use.
