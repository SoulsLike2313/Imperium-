# Administratum Git Sync Console v0.1

## Что это
`Administratum Git Sync Console v0.1` — standalone GUI-утилита на PySide6 для безопасного принятия изменений после VM2-bundle или локальной работы на PC.

## Где живёт
- `ORGANS/ADMINISTRATUM/UTILITY/GIT_SYNC_CONSOLE/git_sync_console_v0_1.py`

## Почему именно Administratum
Administratum отвечает за Git-truth, фиксацию изменений, контроль commit/push и операционные receipts. Эта утилита относится к зоне ответственности Administratum и не требует интеграции в Sanctum на этапе v0.1.

## Как запускать
Linux / VM2:
```bash
cd /home/vboxuser2/IMPERIUM_WORK/Imperium-
python3 ORGANS/ADMINISTRATUM/UTILITY/GIT_SYNC_CONSOLE/git_sync_console_v0_1.py
```

Windows / PC:
```powershell
cd <REPO_ROOT>
py -3 .\ORGANS\ADMINISTRATUM\UTILITY\GIT_SYNC_CONSOLE\git_sync_console_v0_1.py
```

## Что умеет v0.1
- показывает `repo root`, `branch`, `local HEAD`, `upstream HEAD`, clean/dirty состояние;
- показывает changed files с фильтрами: `all`, `staged`, `unstaged`, `untracked`, `likely runtime/noise`;
- показывает diff и preview untracked text file;
- stage/unstage selected;
- stage all visible (с подтверждением);
- discard selected (с подтверждением), но discard untracked **заблокирован**;
- запускает проверки: Git CLI check, `verify_repo.py`, `check_agent_entrypoint.py`, optional pytest quick;
- commit staged changes и отдельная кнопка push;
- push требует отдельное подтверждение, а при не-запущенных/не-PASS checks требует явный Owner override;
- пишет structured receipts в runtime.

## Какие команды использует
Через `GitCommandRunner` (единый subprocess adapter):
- `git status --porcelain=v1`
- `git branch --show-current`
- `git rev-parse --short HEAD`
- `git rev-parse --short @{u}`
- `git diff [--staged] -- <path>`
- `git add -- <paths...>`
- `git restore --staged -- <paths...>`
- `git restore -- <paths...>`
- `git commit -m <message>`
- `git push`
- `python scripts/verify_repo.py`
- `python scripts/check_agent_entrypoint.py`
- `bash TOOLS/run_administratum_git_cli_check.sh` (Linux) / PowerShell-обёртка (Windows)

## Где receipts
- `.imperium_runtime/administratum/git_sync_console/`
  - `SESSION_STATE.json`
  - `LAST_ACTION_RECEIPT.json`
  - `ACTION_RECEIPT_<timestamp>_<action>.json`
  - `CHECKS_SUMMARY.md`

## Временная архитектура subprocess
В v0.1 subprocess оставлен только в `GitCommandRunner` как временный адаптер. В будущем вызовы должны быть мигрированы в `command_gateway.run_allowed()` после расширения allowlist.

## Что v0.1 не делает
- не интегрируется в Sanctum;
- не делает fetch/pull/rebase;
- не делает partial-hunk staging;
- не реализует open file/folder actions;
- не выполняет auto-cleanup runtime/noise;
- не обходит owner-подтверждения для рискованных действий.
