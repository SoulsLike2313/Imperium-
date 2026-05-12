# Capability References For TASK/STAGE/RUN v0.1

Статус: active support guidance.

## Зачем

TASK/STAGE/RUN должны ссылаться на capabilities явно, чтобы:
- не запускать случайные инструменты,
- не нарушать owner gate,
- улучшать повторяемость исполнения.

## Рекомендуемые поля в будущих контрактах

- `required_capabilities`
- `allowed_scripts`
- `allowed_tools`
- `required_owner_approval_tools`
- `forbidden_tools`
- `tooling_refs`

## Пример

```json
{
  "required_capabilities": ["python", "powershell", "git", "ssh", "sha256"],
  "allowed_scripts": ["administratum_git_cli_check_v0_1", "verify_worker_bundle"],
  "allowed_tools": ["git", "python", "powershell"],
  "tooling_refs": [
    "REGISTRY/SCRIPT_REGISTRY.json",
    "REGISTRY/ARSENAL_TOOL_INDEX.json",
    "REGISTRY/ARSENAL_INSTALL_STATUS.json"
  ]
}
```

## Практика применения

- Перед run сверять availability нужных tools по `ARSENAL_INSTALL_STATUS`.
- Перед запуском scripts сверять side_effects/safety/status по `SCRIPT_REGISTRY`.
- Для owner-gated tools фиксировать decision packet/evidence в run receipt.

## No Fake Green

Если capability не подтверждена в contour, это отражается как risk/warning/blocker, а не скрывается.
