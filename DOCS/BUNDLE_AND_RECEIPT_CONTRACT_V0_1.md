# Bundle And Receipt Contract v0.1

Статус: active (v0.1 foundation)

## Назначение

Этот контракт задает минимальный доверенный формат VM2 worker bundle для проверки на PC до любых действий с коммитом.
VM2 bundle по умолчанию считается недоверенным, пока не пройдет проверку структуры, целостности, provenance и scope.

## Обязательные элементы bundle

- `MANIFEST.json`
- `RECEIPT.json`
- `VERDICT.md`
- каталог `repo/` (только измененные repo-файлы в рамках задачи)
- каталог `evidence/` (проверки, отчеты, мотивировка вердикта)

Рядом с zip желательно иметь `*.sha256` для проверки целостности архива на PC.

## Обязательные поля provenance/spine

`MANIFEST.json` должен содержать:
- `bundle_id`, `task_id`, `stage_id`, `run_id`
- `builder` (кто собрал пакет)
- `source_git_truth` (head, commit_count, tree_url)
- `route_truth_ref`
- списки `repo_files`, `evidence_files`, `receipt_files`
- `sha256` (карта контрольных сумм)
- `scope.allowed_paths` и `scope.forbidden_paths_touched`
- `declared_verdict`
- `no_fake_green_statement`

## Trust and Intake Rules

- PC обязан проверить `bundle.zip` и `bundle.zip.sha256` (если `.sha256` приложен).
- Отсутствие/повреждение manifest или sha mismatch = rejection/quarantine.
- Любые forbidden touch (`THRONE/`, `.git/`, `.ssh/`, private keys, secrets) = blocker.
- advisory claims без evidence не дают зеленый статус.

## Вердикты Intake (PC)

Финальные intake-статусы:
- `CAN_COMMIT`
- `CANNOT_COMMIT`
- `NEEDS_OWNER_DECISION`
- `BLOCKED`

Важно: `CAN_COMMIT` не означает, что коммит уже выполнен. Это только разрешение Owner принять решение о commit.

## No Fake Green

- Нельзя заявлять `PASS`, если есть blocker.
- Нельзя объявлять `CLEAR`/`SYSTEM_READY` без явного подтверждающего evidence.
- Все warnings и ограничения должны быть явно отражены в receipts и review report.

## Receipts and Logs

- Receipts и отчеты сохраняются в plain JSON/Markdown.
- Цветной вывод CLI допустим только как UI-слой терминала; файлы логов остаются читаемыми без цвета.
