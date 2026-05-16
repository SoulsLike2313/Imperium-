# COMMAND_LOG

## Stage 0 — Source Lock
```powershell
cd E:\IMPERIUM
git status --short
git log -1 --oneline
git rev-parse HEAD
git rev-list --count HEAD
git show --stat --oneline --name-status HEAD
```
Key output:
- HEAD: `aea80014ddc8b260a5175ea934c78d0921ea7c3a`
- Latest commit: `aea8001 EXPERIMENT: add test version delta window MVP`
- Worktree at start: clean

## Stage 1 — Delta Window Audit
```powershell
cd E:\IMPERIUM\IMPERIUM_TEST_VERSION
.\TESTING_FIELD\DELTA_WINDOW\run_delta_check.ps1
.\TESTING_FIELD\DELTA_WINDOW\run_delta_check.ps1 -Mode historical -OldCommit 3274087e1f597a43ced3252c7edefcb3fda310f1 -NewCommit ff9457d2e5d5d4da9d5b39d039dc1622cbf34810
```
Key output:
- precommit exit: 1, verdict: REPAIR_REQUIRED
- historical exit: 1, verdict: REPAIR_REQUIRED
- screenshots: blocked=13, reason=Playwright not installed

## Stage 2-9 — Agent Exchange MVP
Created structure under:
- `IMPERIUM_TEST_VERSION/AGENT_EXCHANGE/`
- `PROTOCOLS/*` schemas
- `TEMPLATES/*` templates
- thread index + decision record
- Servitor advice bundle in thread bundles and `INBOX/KIRO`

## Stage 10 — Final Scope Check
```powershell
cd E:\IMPERIUM
git status --short
```
Key output:
- allowed paths updated: `AGENT_EXCHANGE/*`, `AUDITS/SERVITOR_DELTA_WINDOW_AUDIT_20260516/*`, `DELTA_WINDOW/REPORTS/*`
- outside strict allowed list also changed by Delta run side-effects:
  - `DELTA_WINDOW/SCREENSHOTS/current/screenshot_index.json`
  - `DELTA_WINDOW/delta_window.html`
  - `DELTA_WINDOW/SNAPSHOTS/SNAP-*`
