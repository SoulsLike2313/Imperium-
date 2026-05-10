# examples

Manual visible run:

```powershell
cd E:\IMPERIUM\SSH_COMMAND_LIBRARY\06_TOOLS\20_CONTINUITY
.\launch_continuity_executor.ps1
```

Direct python run:

```powershell
python run_continuity_pack_executor.py --imperium-root E:\IMPERIUM --mode manual-visible
```

Expected visible flow:
- `[001/010] Address hardening check ...`
- `[002/010] Artifact inventory ...`
- ...
- `FINAL VERDICT: ...`
