# Bundle Intake Review Flow v0.1

Статус: active (PC intake launcher contract)

## Цель

Обеспечить безопасный PC-side процесс приема VM2 bundle:
1. verify целостности и структуры,
2. controlled unpack,
3. pre-commit checks,
4. честный human-readable verdict без auto-commit.

## Поток

1. Owner запускает `TOOLS/review_worker_bundle_intake.ps1` на PC.
2. Скрипт проверяет:
- repo root,
- чистоту worktree до apply,
- наличие bundle и sibling `.sha256` (если есть),
- `TOOLS/verify_worker_bundle.py`.
3. Если verifier не прошел:
- bundle и отчеты уходят в quarantine/rejected,
- выставляется `CANNOT_COMMIT` или `BLOCKED`.
4. Если verifier прошел:
- bundle распаковывается в controlled incoming area,
- печатается список файлов из `repo/`.
5. В режиме `-Apply` скрипт накладывает `repo/` в worktree и запускает pre-commit checks:
- `git diff --check`
- `py_compile` для измененных `.py`
- `check_agent_entrypoint`
- `verify_repo`
- Administratum Git CLI check
- scope check по списку из manifest
6. Скрипт формирует итоговый intake verdict:
- `CAN_COMMIT`
- `CANNOT_COMMIT`
- `NEEDS_OWNER_DECISION`
- `BLOCKED`

## Режимы запуска

- По умолчанию: verify + intake preview без применения в worktree.
- `-Apply`: явное применение `repo/` в worktree и запуск pre-commit checks.
- Скрипт никогда не выполняет `git commit` и `git push`.

## Принципы безопасности

- No fake green.
- Dirty worktree до apply -> `BLOCKED`.
- Проверка пакета не зависит от цветов терминала; отчеты сохраняются в JSON/Markdown.
- Quarantine хранит отклоненные пакеты и причины отклонения.
