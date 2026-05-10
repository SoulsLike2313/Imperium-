# OWNER_SUMMARY

Это целевой cleanhash/packaging repair для TASK-0014C с выпуском объединенного исправленного bundle 0014C1.
Исправлено главное: пересобраны MANIFEST.json и SHA256SUMS.txt в стабильном порядке, теперь top-level checksum-проверка проходит без mismatch по MANIFEST.json.
Подтверждено: SHA256SUMS machine-checkable, пути только archive-relative POSIX, без абсолютных путей, без backslash и без traversal.
UX read-only explorer исправлен: поддерживается флаг `--readonly-assert` без значения; примеры и README обновлены.
Изначальные 0014C-доказательства сохранены: runtime smoke, dry-run final assembly, dependency closure, address map, registry и Sanctum prep notes.
Ограничения соблюдены: VM2 не трогали, реальный E2E не запускали, THRONE не трогали, watchers/automation не включали.
Пакет готов к Speculum hard-review по cleanhash/packaging блоку; TASK-0014D и TASK-0015 остаются по отдельному go/no-go после review.
