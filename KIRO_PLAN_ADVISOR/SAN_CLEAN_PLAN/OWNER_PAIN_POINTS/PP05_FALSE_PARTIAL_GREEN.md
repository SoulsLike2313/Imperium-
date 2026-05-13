# PP05: False or Partial Green is Dangerous

## Проблема
Команды иногда выглядят успешными, хотя файлы на самом деле не были применены или закоммичены.
"PASS" без доказательств — опасная ложь.

## Требование Owner
Каждый PASS должен быть подкреплён:
- Evidence (доказательства)
- Receipts (квитанции)
- Exact path checks (проверка путей)
- Staged-file checks (проверка staged файлов)
- Post-state verification (верификация после)

## Решение

### Архитектурный паттерн: Evidence-Based Verification
Источник: [Automating Evidence Collection in Git](https://hoop.dev/blog/automating-evidence-collection-in-git-for-continuous-compliance-and-security/)

> "Every commit, every merge, every release—documentation, logs, code diffs, test results, and approvals—captured instantly and stored in a secure, tamper-proof system."

### Receipt + Validator Pattern
Источник: [A Minimal Receipt + Validator Pattern](https://forum.langchain.com/t/a-minimal-receipt-validator-pattern-for-tool-calling-agents/3546)

> "A portable record of what request was made, which policy snapshot applied, which tool was used, what input and output were recorded, and whether an independent verifier can detect later changes."

### Структура Evidence-Based PASS

```
PASS = Evidence + Receipt + Post-Check
```

#### 1. Evidence (Доказательства)

```json
{
  "evidence_type": "file_creation",
  "timestamp_utc": "2026-05-14T12:00:00Z",
  "claims": [
    {
      "claim": "File TOOLS/launcher_fetch_bundle_v0_1.py was created",
      "proof": {
        "file_exists": true,
        "file_path": "TOOLS/launcher_fetch_bundle_v0_1.py",
        "file_size_bytes": 4523,
        "sha256": "abc123...",
        "mtime_utc": "2026-05-14T12:00:00Z"
      }
    }
  ]
}
```

#### 2. Receipt (Квитанция)

```json
{
  "schema_version": "launcher_receipt_v0_1",
  "launcher_id": "APPLY_BUNDLE",
  "task_id": "TASK-20260514-001",
  "verdict": "PASS",
  "evidence_refs": [
    ".imperium_runtime/evidence/APPLY_BUNDLE_EVIDENCE_20260514_120000.json"
  ],
  "steps": [
    {"step": "FILE_COPY", "status": "PASS", "files_copied": 5},
    {"step": "POST_CHECK", "status": "PASS", "all_files_exist": true}
  ]
}
```

#### 3. Post-Check (Пост-проверка)

```python
def post_check_file_creation(expected_files: List[Path]) -> Dict:
    """Проверить что файлы реально созданы."""
    results = []
    all_pass = True
    
    for file_path in expected_files:
        exists = file_path.exists()
        result = {
            "file": str(file_path),
            "exists": exists,
        }
        
        if exists:
            result["size"] = file_path.stat().st_size
            result["sha256"] = compute_sha256(file_path)
        else:
            all_pass = False
        
        results.append(result)
    
    return {
        "verdict": "PASS" if all_pass else "FAIL",
        "files_checked": len(expected_files),
        "files_found": len([r for r in results if r["exists"]]),
        "details": results
    }
```

### Anti-Fake-Green Gates

#### Gate 1: Pre-State Capture
```python
def capture_pre_state(repo_root: Path) -> Dict:
    """Захватить состояние ДО операции."""
    return {
        "git_head": get_git_head(repo_root),
        "git_status": get_git_status(repo_root),
        "file_hashes": compute_file_hashes(repo_root),
        "timestamp_utc": datetime.now(timezone.utc).isoformat()
    }
```

#### Gate 2: Operation Execution
```python
def execute_with_evidence(operation: Callable, pre_state: Dict) -> Dict:
    """Выполнить операцию с записью evidence."""
    try:
        result = operation()
        return {
            "success": True,
            "result": result,
            "pre_state": pre_state
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "pre_state": pre_state
        }
```

#### Gate 3: Post-State Verification
```python
def verify_post_state(pre_state: Dict, expected_changes: List[Dict]) -> Dict:
    """Верифицировать состояние ПОСЛЕ операции."""
    post_state = capture_current_state()
    
    verifications = []
    for expected in expected_changes:
        if expected["type"] == "file_created":
            verified = Path(expected["path"]).exists()
        elif expected["type"] == "file_modified":
            old_hash = pre_state["file_hashes"].get(expected["path"])
            new_hash = compute_sha256(Path(expected["path"]))
            verified = old_hash != new_hash
        elif expected["type"] == "git_commit":
            verified = post_state["git_head"] != pre_state["git_head"]
        
        verifications.append({
            "expected": expected,
            "verified": verified
        })
    
    all_verified = all(v["verified"] for v in verifications)
    
    return {
        "verdict": "PASS" if all_verified else "FAIL",
        "verifications": verifications,
        "pre_state_head": pre_state["git_head"],
        "post_state_head": post_state["git_head"]
    }
```

### Запрещённые паттерны (Fake Green)

```python
# ❌ FAKE GREEN: Возврат PASS без проверки
def bad_apply_bundle():
    shutil.copy(src, dst)
    return {"verdict": "PASS"}  # НЕТ ПРОВЕРКИ!

# ✅ REAL GREEN: Возврат PASS с проверкой
def good_apply_bundle():
    shutil.copy(src, dst)
    
    # Проверить что файл реально скопирован
    if not dst.exists():
        return {"verdict": "FAIL", "error": "File not created"}
    
    if compute_sha256(src) != compute_sha256(dst):
        return {"verdict": "FAIL", "error": "Hash mismatch"}
    
    return {
        "verdict": "PASS",
        "evidence": {
            "file_exists": True,
            "hash_match": True,
            "dst_sha256": compute_sha256(dst)
        }
    }
```

## Файлы для создания

| Файл | Назначение | TASK |
|------|------------|------|
| `src/imperium/evidence.py` | Evidence collection module | TASK_01 |
| `schemas/evidence_v0_1.schema.json` | Evidence schema | TASK_01 |
| `TOOLS/verify_evidence_v0_1.py` | Evidence validator | TASK_08 |

## Проверка

```bash
# 1. Запустить операцию
python3 TOOLS/launcher_apply_bundle_v0_1.py --task TASK-001 --verbose

# 2. Проверить receipt
cat .imperium_runtime/launcher/apply_bundle/APPLY_BUNDLE_RECEIPT.json

# 3. Проверить evidence
cat .imperium_runtime/evidence/APPLY_BUNDLE_EVIDENCE_*.json

# 4. Независимая верификация
python3 TOOLS/verify_evidence_v0_1.py --receipt .imperium_runtime/launcher/apply_bundle/APPLY_BUNDLE_RECEIPT.json
```

## Связь с задачами
- **TASK_01** (Launcher Spine) — receipts в каждом лаунчере
- **TASK_08** (Dashboard Data) — evidence в dashboard

## Критерии успеха
- [ ] Каждый PASS имеет receipt
- [ ] Каждый receipt имеет evidence
- [ ] Evidence можно независимо верифицировать
- [ ] Нет PASS без post-check
- [ ] Dashboard показывает только verified PASS
