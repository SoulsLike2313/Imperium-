# IMPERIUM TASK RULES

## Core Rules

1. **ONE TASK = ONE PROMPT** — каждая задача выполняется одним промптом
2. **NO COMMIT** — без прямой команды Owner
3. **NO PUSH** — без прямой команды Owner
4. **NO MERGE** — без прямой команды Owner
5. **OWNER REVIEW REQUIRED** — перед любым изменением master

## Evidence Rules

6. **NO PASS WITHOUT EVIDENCE** — PASS требует доказательства
7. **NO FAKE GREEN** — если нет evidence, статус = UNKNOWN, не PASS
8. **TESTING FIELD REQUIRED** — UI/script изменения требуют smoke test
9. **SCREENSHOT REQUIRED** — UI изменения требуют screenshot

## Scope Rules

10. **SCOPE CORRIDOR** — агент работает только в разрешённых зонах
11. **NO BLOAT** — минимальный output, без лишних файлов
12. **REGISTRY SYNC** — новые скрипты/файлы регистрируются

## Baseline Rules

13. **CURRENT = EVIDENCE-BASELINE** — текущее состояние ≠ product-v1
14. **SCAFFOLD ≠ OPERATIONAL** — scaffold органы не принимают задачи
15. **DEBT DOCUMENTED** — известный долг задокументирован

## Verification Rules

16. **PREFLIGHT REQUIRED** — перед работой: git status, verify_repo
17. **POSTFLIGHT REQUIRED** — после работы: git status, verify_repo
18. **RECEIPT REQUIRED** — каждое действие создаёт receipt
