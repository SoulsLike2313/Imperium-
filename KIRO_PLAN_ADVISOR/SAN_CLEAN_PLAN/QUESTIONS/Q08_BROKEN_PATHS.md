# Q08: Broken Paths After External Context Migration

## ВОПРОС
Какие скрипты/документы должны быть обновлены первыми для:
- prompt dispatch
- bundle fetch
- bundle review
- continuity pack
- handoff pack
- route verification
- Sanctum action registry
- dashboard data builders

## РЕШЕНИЕ

### Категории файлов для обновления

#### 1. Prompt Dispatch
| Файл | Текущий путь | Новый путь |
|------|--------------|------------|
| `ORGANS/ADMINISTRATUM/REGISTRY/PROMPT_AND_BUNDLE_ROUTE_MAP_V0_1.md` | ✅ Уже обновлён | — |

#### 2. Bundle Fetch
| Файл | Проблема | Решение |
|------|----------|---------|
| `TOOLS/review_worker_bundle_intake.ps1` | Использует `E:\IMPERIUM\INBOX` | Заменить на `E:\IMPERIUM_CONTEXT\LOCAL\VM2_BUNDLES` |

#### 3. Bundle Review
| Файл | Проблема | Решение |
|------|----------|---------|
| `TOOLS/verify_worker_bundle.py` | Может использовать старые пути | Проверить и обновить |

#### 4. Continuity Pack
| Файл | Проблема | Решение |
|------|----------|---------|
| `ORGANS/ADMINISTRATUM/SCRIPTS/administratum_build_continuity_pack.py` | `E:\IMPERIUM_LOCAL` | `E:\IMPERIUM_CONTEXT\LOCAL` |
| `ORGANS/ADMINISTRATUM/SCRIPTS/administratum_build_resume_continuity_pack_v0_2.py` | `E:\IMPERIUM_LOCAL` | `E:\IMPERIUM_CONTEXT\LOCAL` |
| `ORGANS/ADMINISTRATUM/SCRIPTS/administratum_build_developer_grade_continuity_pack.py` | `E:\IMPERIUM_LOCAL` | `E:\IMPERIUM_CONTEXT\LOCAL` |

#### 5. Handoff Pack
| Файл | Проблема | Решение |
|------|----------|---------|
| `ORGANS/ADMINISTRATUM/SCRIPTS/administratum_qa_developer_handoff_pack.py` | `E:\IMPERIUM_LOCAL`, `E:\IMPERIUM_PRIVATE` | Обновить на новые корни |

#### 6. Route Verification
| Файл | Проблема | Решение |
|------|----------|---------|
| `TOOLS/check_repo_parity_external_context_v0_2.py` | ✅ Уже обновлён | — |
| `TOOLS/check_external_context_registry_v0_1.py` | ✅ Уже обновлён | — |

#### 7. Sanctum Action Registry
| Файл | Проблема | Решение |
|------|----------|---------|
| `SANCTUM/sanctum_v0_29_qt.py` | **НЕ ТРОГАТЬ RUNTIME** | Только документация |

#### 8. Dashboard Data Builders
| Файл | Проблема | Решение |
|------|----------|---------|
| `TOOLS/build_sanctum_state_v0_1.py` | Может использовать старые пути | Проверить |
| `TOOLS/build_sanctum_dashboard_v0_5_data.py` | Может использовать старые пути | Проверить |
| `ORGANS/ADMINISTRATUM/UTILITY/WEB_DASHBOARD_V0_3/dashboard_server.py` | `can_update_later` | Обновить позже |

### Полный список must_update_soon (20 файлов)

```
1.  ORGANS/ADMINISTRATUM/SCRIPTS/administratum_build_resume_continuity_pack_v0_2.py
2.  ORGANS/ADMINISTRATUM/SCRIPTS/administratum_qa_developer_handoff_pack.py
3.  ORGANS/ADMINISTRATUM/SCRIPTS/administratum_build_continuity_pack.py
4.  ORGANS/ADMINISTRATUM/SCRIPTS/administratum_build_developer_grade_continuity_pack.py
5.  ORGANS/ADMINISTRATUM/SCRIPTS/administratum_scan_real_imperium_state.py
6.  ORGANS/ADMINISTRATUM/SCRIPTS/administratum_compare_continuity_pack.py
7.  ORGANS/ADMINISTRATUM/SCRIPTS/administratum_qa_continuity_pack_against_reality.py
8.  ORGANS/ADMINISTRATUM/SCRIPTS/administratum_build_continuity_candidate.py
9.  ORGANS/ADMINISTRATUM/SCRIPTS/administratum_build_current_state.py
10. ORGANS/ADMINISTRATUM/UTILITY/run_administratum_context_bundle_workflow.ps1
11. TOOLS/review_worker_bundle_intake.ps1
12. TOOLS/build_chat_compilation_from_analysis.ps1
13. TOOLS/administratum_analyze_git_local_context.ps1
14. TOOLS/administratum_record_analyzer_checkpoint.ps1
15. ORGANS/ADMINISTRATUM/CONTINUITY/COMPARISONS/FINAL_HANDOFF_SUFFICIENCY_DECISION.md
16. ORGANS/ADMINISTRATUM/REPORTS/ADMINISTRATUM_CONTINUITY_STATUS.md
17. ORGANS/ADMINISTRATUM/REPORTS/ADMINISTRATUM_CONTINUITY_STATUS.json
18. ORGANS/ADMINISTRATUM/CONFIG/ADMINISTRATUM_ROUTE_TRUTH_V0_1.json
19. ORGANS/ADMINISTRATUM/ADDRESSES/ADDRESS_REGISTRY.json
20. ORGANS/ADMINISTRATUM/ADDRESSES/READ_ROUTE_REGISTRY.json
```

### Путь решения — Шаги

#### Шаг 1: Создать backup
```bash
# На VM2
mkdir -p /tmp/address_rewrite_backup_20260514
for f in <list>; do
    cp "$f" "/tmp/address_rewrite_backup_20260514/"
done
```

#### Шаг 2: Для каждого файла
1. Прочитать содержимое
2. Найти все legacy patterns
3. Заменить на новые пути
4. Сохранить
5. Проверить компиляцию (для .py)
6. Записать в отчёт

#### Шаг 3: Запустить чекер
```bash
python3 TOOLS/check_address_rewrite_v0_1.py --repo-root . --human
```

#### Шаг 4: Создать отчёт
Файл: `CURRENT_STATE/ADDRESS_REWRITE_IMPLEMENTATION_REPORT_20260514.md`

### Критерии успеха
- [ ] Все 20 файлов обновлены
- [ ] Все .py файлы компилируются
- [ ] Чекер проходит с 0 violations
- [ ] Отчёт создан

### Критерии блокировки
- Любой файл не компилируется после замены
- Legacy path найден в must_update_soon файлах

## ПРИМЕР СТРУКТУРЫ

См. `TASKS/TASK_02_ADDRESS_REWRITE/`
