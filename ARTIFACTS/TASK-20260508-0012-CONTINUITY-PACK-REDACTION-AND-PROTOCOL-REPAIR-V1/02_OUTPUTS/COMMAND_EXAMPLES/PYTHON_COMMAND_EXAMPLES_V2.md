# PYTHON COMMAND EXAMPLES V2

All examples below are redacted and use placeholders.
Do not substitute shareable files with local secrets.

## Send prompt example

```powershell
python "E:\IMPERIUM\SSH_COMMAND_LIBRARY\06_TOOLS\send_prompt_to_vm2.py" `
  --task-id <TASK_ID> `
  --stage-id <STAGE_ID> `
  --run-id <RUN_ID> `
  --contour-id VM2 `
  --config <CONFIG_LOCAL_ONLY> `
  --local-prompt "E:\IMPERIUM\ARTIFACTS\<TASK_ID>\01_INPUTS\PROMPT.md" `
  --write-receipt `
  --no-delete `
  --no-throne `
  --no-autosync
```

## Fetch bundle example

```powershell
python "E:\IMPERIUM\SSH_COMMAND_LIBRARY\06_TOOLS\fetch_vm2_stage_bundle.py" `
  --task-id <TASK_ID> `
  --stage-id <STAGE_ID> `
  --run-id <RUN_ID> `
  --contour-id VM2 `
  --config <CONFIG_LOCAL_ONLY> `
  --write-receipt `
  --no-delete `
  --no-throne `
  --no-autosync
```

## Notes
- Open prompt on VM2 should be a separate manual convenience tool later.
- Open folder should be a separate UI helper later.
- Core transport scripts should not mix GUI operations with transfer and verification in canonical use.
