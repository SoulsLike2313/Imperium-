# WARNING_FLOOD_FIX_PLAN_V0_1

## 0. Executive verdict
- Основной источник warning flood: **tracked legacy evidence/snapshot массивы**, прежде всего `ARTIFACTS/` и `ORGANS/ADMINISTRATUM/CONTINUITY/PACKS/`, содержащие массовые абсолютные пути (`E:\\IMPERIUM`, частично `/home/vboxuser2`).
- Исполнение cleanup **технически безопасно**, если делать только `git rm --cached` (без физического удаления файлов) и только после точного review списка.
- Требуется **явное одобрение Owner** перед execution, потому что затрагивается публичная история tracking и объёмный legacy-контур.
- Что нельзя делать: физическое удаление, массовые move, silent cleanup без review, изменение active source под видом warning fix.

## 1. Current evidence
- Дата анализа (UTC): `2026-05-12`.
- HEAD: `06df498d7e9b09e22bb25a5d5f1820e0267868d6`.
- Commit count: `39`.
- Latest commit: `06df498 TASK-20260512: add Sanctum organ HUD data service`.
- Worktree до planning: `clean`.
- `run_administratum_git_cli_check`: `PASS` (до внесения plan-файла).
- `verify_repo` verdict: `PASS_WITH_WARNINGS`.
- `verify_repo` blockers: `0`.
- `verify_repo` warnings: `121458`.
- Gate verdicts:
  - `no_pycache_tracked`: `PASS`
  - `no_raw_subprocess`: `PASS_WITH_WARNINGS` (warnings=`1`)
  - `public_private_boundary_scan`: `PASS_WITH_WARNINGS` (warnings=`103813`)
  - `receipt_portability_check`: `PASS_WITH_WARNINGS` (warnings=`17644`)
  - `python_py_compile`: `PASS`
- Ключевые observed counts:
  - tracked files total: `6985`
  - `ARTIFACTS/`: `5177`
  - `ORGANS/ADMINISTRATUM/CONTINUITY/PACKS/`: `429`
  - `OBSERVED/`: `42`
  - `CURRENT_STATE/`: `123`
  - `PC_ENGINEERING_ROOM/`: `21`
  - tracked `*.zip`: `85`
  - tracked `*.png`: `563`
  - tracked occurrences `E:\\IMPERIUM`: `29658` строк
  - tracked occurrences `/home/vboxuser2`: `91` строк

## 2. Warning source map
| Source / pattern | Tracked count | Approx warning contribution | Category | Recommended action | Risk |
|---|---:|---:|---|---|---|
| `ARTIFACTS/` | 5177 files | very high (`~103k` + часть `~17k`) | legacy evidence/snapshots | Кандидат на staged untracking по фазам (PC-only) | High (массовый объём, нужен review) |
| `ORGANS/ADMINISTRATUM/CONTINUITY/PACKS/` | 429 files | medium-high (`1270` попаданий `E:\\IMPERIUM`) | continuity snapshots | Вынести из tracking через `git rm --cached`, оставить физически | Medium |
| `EXPLORER/SCREENSHOTS` и подобные media evidence | сотни файлов (внутри `EXPLORER`=391) | заметный вклад (по `E:\\IMPERIUM` hit map) | runtime/local evidence | Untrack по явному списку и закрыть `.gitignore` | Medium |
| `CURRENT_STATE/`, `OBSERVED/`, часть `PC_ENGINEERING_ROOM/` | 123 / 42 / 21 | low-medium | legacy/local state | Owner decision list, не auto-cleanup | Medium |
| Активные source-файлы (`SANCTUM/*.py`, `TOOLS/*`, `scripts/*`) | низкий объём | низкий в total flood, но важный техдолг | active source | Оставить tracked, фиксить точечно отдельными задачами | High (если скрыть baseline-ом) |
| `no_raw_subprocess` warnings | n/a | `1` | active tech debt | Не маскировать cleanup-ом | Low |

## 3. Continuity packs analysis
- `ORGANS/ADMINISTRATUM/CONTINUITY/PACKS/` содержит `429` tracked файлов (`227 .md`, `187 .json`, `14 .txt`, `1 .zip`).
- Это не active product source, а continuity/evidence с сильной исторической привязкой к локальным путям.
- Внутри этого сегмента обнаружено `1270` строк с `E:\\IMPERIUM`.
- Поэтому безопасный путь: **`git rm --cached`** (снять из tracking) при сохранении файлов на диске.
- Прямое удаление физически не требуется и запрещено данным планом.

## 4. Proposed safe execution plan (PC-ONLY, DO NOT EXECUTE IN THIS STEP)
1. Подтвердить backup и точку отката на PC.
2. Получить snapshot tracked counts до cleanup.
3. Сформировать review-list candidate paths (сначала continuity packs, затем staged legacy evidence buckets).
4. Выполнить `git rm --cached` только по одобренным путям.
5. Добавить/уточнить `.gitignore` правила для предотвращения повторного re-track.
6. Ввести warning baseline (`WARNING_BASELINE.json`) и policy сравнения.
7. Прогнать валидации (`verify_repo`, `git cli check`, targeted scans).
8. Сделать отдельный review commit (PC-only).

### Proposed `.gitignore` additions (text proposal, not executed here)
```gitignore
# WARNING_FLOOD_FIX (proposal only)
/ORGANS/ADMINISTRATUM/CONTINUITY/PACKS/
/ARTIFACTS/
/EXPLORER/SCREENSHOTS/
/CURRENT_STATE/
/OBSERVED/
# Optional by Owner decision:
#/PC_ENGINEERING_ROOM/
```

### Proposed WARNING baseline shape (text proposal)
```json
{
  "schema_version": "imperium.warning_baseline.v0_1",
  "created_at_utc": "2026-05-12T00:00:00Z",
  "repo_ref": "<pc_commit_hash>",
  "gates": {
    "public_private_boundary_scan": {
      "warnings_total": 0,
      "allowed_patterns": []
    },
    "receipt_portability_check": {
      "warnings_total": 0,
      "allowed_patterns": []
    },
    "no_raw_subprocess": {
      "warnings_total": 1,
      "allowed_files": ["SANCTUM/sanctum_v0_29_qt.py"]
    }
  },
  "policy": {
    "fail_on_new_blockers": true,
    "fail_on_warning_regression": true,
    "allow_warning_reduction": true
  }
}
```

### Commit message suggestion (PC-only)
`TASK-20260512: warning flood cleanup phase1 (untrack legacy snapshots, keep files locally)`

## 5. PC-only execution commands
> Принципы: запускать только на PC (`E:\IMPERIUM`), только после Owner approval, без физического удаления.

```powershell
# 0) Open repo root
Set-Location E:\IMPERIUM

# 1) Safety snapshot
git status --short
git rev-parse HEAD
git rev-list --count HEAD

# 2) Count before cleanup
git ls-files | Measure-Object | Select-Object -ExpandProperty Count
git ls-files ORGANS/ADMINISTRATUM/CONTINUITY/PACKS | Measure-Object | Select-Object -ExpandProperty Count

# 3) Candidate review list (save to file)
git ls-files ORGANS/ADMINISTRATUM/CONTINUITY/PACKS > .\CURRENT_STATE\warning_cleanup_candidates_phase1.txt

# 4) Untrack only (keeps physical files)
git rm -r --cached -- ORGANS/ADMINISTRATUM/CONTINUITY/PACKS

# 5) Optional next phase by explicit Owner decision
# git rm -r --cached -- ARTIFACTS
# git rm -r --cached -- EXPLORER/SCREENSHOTS
# git rm -r --cached -- CURRENT_STATE
# git rm -r --cached -- OBSERVED

# 6) Re-check
git status --short
py -3 .\scripts\verify_repo.py
powershell -ExecutionPolicy Bypass -NoProfile -File .\TOOLS\RUN_ADMINISTRATUM_GIT_CLI_CHECK.ps1
```

## 6. Rollback plan
- До коммита:
  - Если staged не тот набор: `git restore --staged -- <path>`.
  - Для массового отката staged-untrack до коммита: `git reset`.
- После коммита:
  - Откат коммита стандартным `git revert <commit>` (без переписывания истории).
- Локальные файлы:
  - `git rm --cached` физические файлы не удаляет; дополнительно сверить наличия через `Test-Path`/`Get-ChildItem`.

## 7. Acceptance criteria
- Физические файлы не удалены.
- Tracked count для целевых continuity snapshot зон падает до ожидаемого значения.
- `verify_repo` blockers остаётся `0`.
- Warnings снижаются существенно (или переводятся под baseline policy без маскировки новых регрессий).
- Git CLI check после PC-коммита: `PASS`.
- VM2 sync возвращается к clean после подтягивания.
- Active source не выведен из tracking ошибочно.

## 8. New baseline / regression policy
- Нельзя просто игнорировать warnings: это скрывает новые утечки и деградации portability.
- Нужен `WARNING_BASELINE.json` с gate-wise лимитами/allowlist и ссылкой на commit.
- Будущая проверка `verify_repo` должна сравнивать текущие warnings с baseline:
  - новые warnings => регрессия;
  - уменьшение warnings => улучшение;
  - blockers всегда fail независимо от baseline.

## 9. What remains technical debt after cleanup
- Raw subprocess debt в активном Sanctum/legacy местах (не закрывается untrack cleanup).
- Hardcoded absolute paths в active source, если остались (точечные задачи).
- Command gateway coverage не завершён.
- Legacy/version sprawl остаётся и требует отдельного архивационного плана.
- Registry drift / канонизация реестров требует отдельного контроля.

## 10. Recommendation
- Рекомендация: **исполнять cleanup на PC, но по фазам и только после Owner approval**.
- Первой фазой выполнять только continuity packs (`ORGANS/ADMINISTRATUM/CONTINUITY/PACKS`) как low-risk/high-gain.
- `ARTIFACTS` и остальные legacy buckets выполнять отдельными подфазами с явным review-list.
- Следующая задача для исполнения: **`TASK-20260512-WARNING-FLOOD-FIX-EXECUTE-PC-V0_1`**.
