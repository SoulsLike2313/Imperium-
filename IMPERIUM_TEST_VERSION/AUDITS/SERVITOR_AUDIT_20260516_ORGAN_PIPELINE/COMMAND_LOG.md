# COMMAND_LOG

## Stage 0 — Safety / Source Lock

```powershell
git status --short
git fetch origin
git log -1 --oneline
git rev-parse HEAD
git rev-parse origin/master
git ls-remote origin refs/heads/master
git rev-list --count HEAD
git show --stat --oneline --name-status HEAD
```

Key output:
- `HEAD`: `3274087e1f597a43ced3252c7edefcb3fda310f1`
- `origin/master`: `3274087e1f597a43ced3252c7edefcb3fda310f1`
- Latest commit: `3274087 EXPERIMENT: advance Imperium test version lab to organ pipeline`
- Worktree before audit: dirty (`M`/`??` already present under `IMPERIUM_TEST_VERSION`)

## Stage 1 — Commit Scope Audit

```powershell
git show --shortstat --oneline HEAD
git show --name-status --pretty=format: HEAD
```

Key output:
- `181 files changed, 19093 insertions(+), 299 deletions(-)`
- Name-status counts: `A=159 M=20 D=2`
- Scope check: only `.gitignore` + `IMPERIUM_TEST_VERSION/*`
- `IMPERIUM_TEST_VERSION/Kiro_task.zip` deleted in commit

## Stage 2 — Claim Discovery

```powershell
rg -n "824|99.9|11 dashboards|10 organs|7 evolution|Truth Spine|Dashboard Generator|Learning Loop|Promotion Pipeline|Auto-Sync|RUN_ALL" IMPERIUM_TEST_VERSION DOCS ORGANS
Get-ChildItem -Recurse -File -Filter *.pdf
```

Key output:
- Claims found in `README_RU.md`, `OWNER_CHRONOLOGY_RU.md`, `K10_KIRO_LAB_ROADMAP.json`, `SYSTEM_STATE_V2_4/V2_5.md`
- PDF plan `IMPERIUM_KIRO_PIPELINE_PLAN_20260516.pdf` not found in repo.

## Stage 3 — Pipeline Run

```powershell
cd E:\IMPERIUM\IMPERIUM_TEST_VERSION
powershell -ExecutionPolicy Bypass -File .\RUN_ALL.ps1
```

Key output:
- `RUN_ALL_EXIT_CODE=1`
- Smoke: `PARTIAL` (4/5)
- Mechanicus: `PARTIAL` (823/824)
- Inquisition: `FAIL` (100 issues, fake_green=2, stale_truth=98)
- Multiple `UnicodeEncodeError` in steps 5,6,7b,9,10,12
- Overall `FAIL`

Changed-by-run check:

```powershell
git status --short  # before and after RUN_ALL
```

Key output:
- before entries: `39`
- after entries: `48`
- new entries after run: `9` (new receipts/reports)

## Stage 4 — Dashboard Inventory & HTTP Check

```powershell
Get-ChildItem IMPERIUM_TEST_VERSION -Recurse -File -Include "*.html" | Select-Object FullName
```

Key output:
- Dashboard HTML files found: `14`
- Organ dashboards: `10`
- Broken internal links detected for 8 organ dashboards

## Stage 5 — Screenshot Pass

Server:

```powershell
cd E:\IMPERIUM\IMPERIUM_TEST_VERSION
py -3 -m http.server 8765
```

Screenshots fallback (Playwright unavailable):

```powershell
"C:\Program Files\Google\Chrome\Application\chrome.exe" --headless=new --screenshot=... http://localhost:8765/...
```

Key output:
- screenshots created: `14`
- files stored under `IMPERIUM_TEST_VERSION/AUDITS/SERVITOR_AUDIT_20260516_ORGAN_PIPELINE/SCREENSHOTS/`

## Additional Truth Checks (AGENTS.md)

```powershell
powershell -ExecutionPolicy Bypass -NoProfile -File .\TOOLS\RUN_ADMINISTRATUM_GIT_CLI_CHECK.ps1
py -3 .\scripts\verify_repo.py
```

Key output:
- `RUN_ADMINISTRATUM_GIT_CLI_CHECK.ps1`: artifacts in `.imperium_runtime/administratum/git_cli_check/`
- `verify_repo.py`: overall `FAIL`, blockers=`20`, warnings=`118412`
