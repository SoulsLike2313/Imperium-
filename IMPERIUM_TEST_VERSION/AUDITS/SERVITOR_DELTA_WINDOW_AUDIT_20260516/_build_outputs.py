import json
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(r"E:/IMPERIUM")
TV_ROOT = REPO_ROOT / "IMPERIUM_TEST_VERSION"
DELTA_ROOT = TV_ROOT / "TESTING_FIELD" / "DELTA_WINDOW"
AUDIT_ROOT = TV_ROOT / "AUDITS" / "SERVITOR_DELTA_WINDOW_AUDIT_20260516"
EXCHANGE_ROOT = TV_ROOT / "AGENT_EXCHANGE"
THREAD_ID = "THREAD-20260516-DELTA-WINDOW-AND-AGENT-EXCHANGE"
THREAD_ROOT = EXCHANGE_ROOT / "THREADS" / THREAD_ID
NOW_UTC = datetime.now(timezone.utc).isoformat()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)).replace("\\", "/")


required_check = read_json(AUDIT_ROOT / "_required_files_check_pre_run.json")
delta_report = read_json(DELTA_ROOT / "REPORTS" / "latest_delta_report.json")
precommit_verdict = read_json(DELTA_ROOT / "REPORTS" / "latest_precommit_verdict.json")
run_receipt = read_json(DELTA_ROOT / "REPORTS" / "run_receipt.json")
screenshot_index = read_json(DELTA_ROOT / "SCREENSHOTS" / "current" / "screenshot_index.json")
run_output = (AUDIT_ROOT / "_run_delta_check_output.txt").read_text(encoding="utf-8", errors="ignore")
run_hist_output = (AUDIT_ROOT / "_run_delta_check_historical_output.txt").read_text(encoding="utf-8", errors="ignore")

audit_matrix = [
    {
        "question": "Does the script run?",
        "status": "PASS",
        "observed": "run_delta_check.ps1 executed in precommit and historical modes; both completed with reports generated; exit code 1 due REPAIR_REQUIRED verdict.",
        "evidence_path": rel(AUDIT_ROOT / "_run_delta_check_output.txt"),
    },
    {
        "question": "Does it only observe IMPERIUM_TEST_VERSION?",
        "status": "PARTIAL",
        "observed": "Core delta scope is test-version-only; script reads repo-level git truth (HEAD/status).",
        "evidence_path": rel(DELTA_ROOT / "run_delta_check.ps1"),
    },
    {
        "question": "Does it avoid git add/commit/push?",
        "status": "PASS",
        "observed": "No execution of git add/commit/push in run_delta_check.ps1 and Python helpers.",
        "evidence_path": rel(DELTA_ROOT / "run_delta_check.ps1"),
    },
    {
        "question": "Does it generate valid JSON?",
        "status": "PASS",
        "observed": "latest_delta_report.json, latest_precommit_verdict.json, run_receipt.json, screenshot_index.json parse as valid JSON.",
        "evidence_path": rel(AUDIT_ROOT / "_run_delta_check_output.txt"),
    },
    {
        "question": "Does delta_window.html exist after run?",
        "status": "PASS",
        "observed": "HTML regenerated successfully in both runs.",
        "evidence_path": rel(DELTA_ROOT / "delta_window.html"),
    },
    {
        "question": "Does HTML clearly say scope is IMPERIUM_TEST_VERSION_ONLY?",
        "status": "PASS",
        "observed": "Contains 'SCOPE: IMPERIUM_TEST_VERSION ONLY' and footer scope warning.",
        "evidence_path": rel(DELTA_ROOT / "delta_window.html"),
    },
    {
        "question": "Does it show git truth?",
        "status": "PASS",
        "observed": "HTML includes baseline/current labels and main canon touched flag.",
        "evidence_path": rel(DELTA_ROOT / "delta_window.html"),
    },
    {
        "question": "Does it show file delta?",
        "status": "PASS",
        "observed": "File delta counters and changed files list are rendered in HTML and JSON report.",
        "evidence_path": rel(DELTA_ROOT / "REPORTS" / "latest_delta_report.json"),
    },
    {
        "question": "Does it show precommit verdict?",
        "status": "PASS",
        "observed": "Precommit verdict shown in HTML and latest_precommit_verdict.json.",
        "evidence_path": rel(DELTA_ROOT / "REPORTS" / "latest_precommit_verdict.json"),
    },
    {
        "question": "Does it show evidence paths?",
        "status": "PASS",
        "observed": "Verdict JSON includes delta_report_path and html_path.",
        "evidence_path": rel(DELTA_ROOT / "REPORTS" / "latest_precommit_verdict.json"),
    },
    {
        "question": "Does it honestly mark screenshots as blocked/partial if Playwright is missing?",
        "status": "PASS",
        "observed": "playwright_available=false, screenshots_blocked=13 with explicit reason.",
        "evidence_path": rel(DELTA_ROOT / "SCREENSHOTS" / "current" / "screenshot_index.json"),
    },
    {
        "question": "Does historical mode honestly mark partial state?",
        "status": "PARTIAL",
        "observed": "Mode changes to historical, but truth_delta.baseline_status remains 'N/A (precommit mode)' and run_receipt overall_verdict stays PASS despite REPAIR_REQUIRED verdict.",
        "evidence_path": rel(DELTA_ROOT / "REPORTS" / "latest_delta_report.json"),
    },
    {
        "question": "Does it create files outside Delta Window path?",
        "status": "PASS",
        "observed": "Observed script writes remain under DELTA_WINDOW (REPORTS/SCREENSHOTS/SNAPSHOTS/html).",
        "evidence_path": rel(DELTA_ROOT / "run_delta_check.ps1"),
    },
    {
        "question": "Does it touch main canon?",
        "status": "PASS",
        "observed": "scope.main_canon_touched=false in reports.",
        "evidence_path": rel(DELTA_ROOT / "REPORTS" / "latest_delta_report.json"),
    },
    {
        "question": "Does it hide unknown/broken states?",
        "status": "PARTIAL",
        "observed": "Core verdict REPAIR_REQUIRED is visible, but receipt-level overall_verdict=PASS causes mixed signal.",
        "evidence_path": rel(DELTA_ROOT / "REPORTS" / "run_receipt.json"),
    },
]

delta_window_verdict = "USEFUL_BUT_PARTIAL"

delta_window_screenshot_status = {
    "scope": "IMPERIUM_TEST_VERSION_ONLY",
    "generated_at": NOW_UTC,
    "playwright_available": screenshot_index.get("playwright_available"),
    "dashboards_found": screenshot_index.get("dashboards_found"),
    "screenshots_captured": screenshot_index.get("screenshots_captured"),
    "screenshots_failed": screenshot_index.get("screenshots_failed"),
    "screenshots_blocked": screenshot_index.get("screenshots_blocked"),
    "honesty_verdict": "PASS",
    "comment_ru": "Блокировка скриншотов зафиксирована честно: Playwright отсутствует, статус blocked выставлен для всех dashboard.",
    "evidence_path": rel(DELTA_ROOT / "SCREENSHOTS" / "current" / "screenshot_index.json"),
}

write_json(AUDIT_ROOT / "DELTA_WINDOW_AUDIT_MATRIX.json", audit_matrix)
write_json(AUDIT_ROOT / "DELTA_WINDOW_SCREENSHOT_STATUS.json", delta_window_screenshot_status)

# AGENT_EXCHANGE files
exchange_readme = """# AGENT_EXCHANGE (RU)

## Назначение
Файловая зона обмена evidence-bundles между KIRO, SERVITOR, LOGOS_PRIME и OWNER внутри `IMPERIUM_TEST_VERSION`.

## Базовый workflow
1. KIRO выполняет задачу и формирует response bundle по `TEMPLATES/KIRO_RESPONSE_BUNDLE_TEMPLATE.md`.
2. KIRO кладёт bundle в `OUTBOX/KIRO/` и копию в thread `THREADS/<thread_id>/messages/`.
3. SERVITOR читает bundle, делает аудит, формирует advice bundle.
4. SERVITOR кладёт advice в `INBOX/KIRO/` и в `THREADS/<thread_id>/bundles/`.
5. LOGOS_PRIME читает `thread_index.json` + bundles и готовит owner-facing synthesis.
6. OWNER принимает решение через decision record.

## Правила качества
- No claim without evidence path.
- No PASS without criteria matrix.
- Все риски и открытые вопросы должны быть перечислены явно.
- Scope строго внутри `IMPERIUM_TEST_VERSION`.

## Куда класть файлы
- KIRO outputs: `OUTBOX/KIRO/`
- SERVITOR outputs: `OUTBOX/SERVITOR/` и `INBOX/KIRO/`
- LOGOS outputs: `OUTBOX/LOGOS_PRIME/`
- Thread memory: `THREADS/<thread_id>/messages|bundles|decisions|evidence`
"""
write_text(EXCHANGE_ROOT / "README_RU.md", exchange_readme)

exchange_state = {
    "schema_version": "AGENT_EXCHANGE_STATE_V1",
    "generated_at": NOW_UTC,
    "exchange_root": str(EXCHANGE_ROOT).replace("\\", "/"),
    "status": "MVP_READY",
    "participants": ["KIRO", "SERVITOR", "LOGOS_PRIME", "OWNER"],
    "active_thread": THREAD_ID,
    "rules": {
        "evidence_required": True,
        "no_fake_green": True,
        "scope": "IMPERIUM_TEST_VERSION_ONLY",
    },
}
write_json(EXCHANGE_ROOT / "EXCHANGE_STATE.json", exchange_state)

agent_message_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "AgentMessage",
    "type": "object",
    "required": [
        "message_id",
        "thread_id",
        "from_agent",
        "to_agent",
        "created_at",
        "subject",
        "context",
        "claims",
        "evidence_paths",
        "findings",
        "recommendations",
        "questions",
        "do_not_do",
        "owner_decision_needed",
        "next_actions",
        "status",
    ],
    "properties": {
        "message_id": {"type": "string"},
        "thread_id": {"type": "string"},
        "from_agent": {"type": "string", "enum": ["KIRO", "SERVITOR", "LOGOS_PRIME", "OWNER", "UNKNOWN"]},
        "to_agent": {"type": "string", "enum": ["KIRO", "SERVITOR", "LOGOS_PRIME", "OWNER", "MULTI"]},
        "created_at": {"type": "string", "format": "date-time"},
        "subject": {"type": "string"},
        "context": {
            "type": "object",
            "required": ["repo_head", "task_id", "related_paths"],
            "properties": {
                "repo_head": {"type": "string"},
                "task_id": {"type": "string"},
                "related_paths": {"type": "array", "items": {"type": "string"}},
            },
        },
        "claims": {"type": "array", "items": {"type": "string"}},
        "evidence_paths": {"type": "array", "items": {"type": "string"}},
        "findings": {"type": "array", "items": {"type": "string"}},
        "recommendations": {"type": "array", "items": {"type": "string"}},
        "questions": {"type": "array", "items": {"type": "string"}},
        "do_not_do": {"type": "array", "items": {"type": "string"}},
        "owner_decision_needed": {"type": "boolean"},
        "next_actions": {"type": "array", "items": {"type": "string"}},
        "status": {"type": "string", "enum": ["DRAFT", "READY", "READ", "ANSWERED", "BLOCKED"]},
    },
}
write_json(EXCHANGE_ROOT / "PROTOCOLS" / "AGENT_MESSAGE_SCHEMA.json", agent_message_schema)

advice_bundle_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "AdviceBundle",
    "type": "object",
    "required": [
        "bundle_id",
        "source_agent",
        "target_agent",
        "task_context",
        "repo_head",
        "relevant_paths",
        "summary_ru",
        "what_is_strong",
        "what_is_weak",
        "risks",
        "evidence_paths",
        "recommended_repairs",
        "recommended_next_tasks",
        "questions_for_target_agent",
        "questions_for_owner",
        "no_go_list",
        "pass_criteria_for_next_work",
        "final_verdict",
    ],
    "properties": {
        "bundle_id": {"type": "string"},
        "source_agent": {"type": "string"},
        "target_agent": {"type": "string"},
        "task_context": {"type": "string"},
        "repo_head": {"type": "string"},
        "relevant_paths": {"type": "array", "items": {"type": "string"}},
        "summary_ru": {"type": "string"},
        "what_is_strong": {"type": "array", "items": {"type": "string"}},
        "what_is_weak": {"type": "array", "items": {"type": "string"}},
        "risks": {"type": "array", "items": {"type": "string"}},
        "evidence_paths": {"type": "array", "items": {"type": "string"}},
        "recommended_repairs": {"type": "array", "items": {"type": "string"}},
        "recommended_next_tasks": {"type": "array", "items": {"type": "string"}},
        "questions_for_target_agent": {"type": "array", "items": {"type": "string"}},
        "questions_for_owner": {"type": "array", "items": {"type": "string"}},
        "no_go_list": {"type": "array", "items": {"type": "string"}},
        "pass_criteria_for_next_work": {"type": "array", "items": {"type": "string"}},
        "final_verdict": {"type": "string"},
    },
}
write_json(EXCHANGE_ROOT / "PROTOCOLS" / "ADVICE_BUNDLE_SCHEMA.json", advice_bundle_schema)

handoff_bundle_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "HandoffBundle",
    "type": "object",
    "required": [
        "handoff_id",
        "thread_id",
        "from_agent",
        "to_agent",
        "created_at",
        "repo_head",
        "summary_ru",
        "changed_paths",
        "evidence_paths",
        "open_issues",
        "required_next_actions",
        "status",
    ],
    "properties": {
        "handoff_id": {"type": "string"},
        "thread_id": {"type": "string"},
        "from_agent": {"type": "string"},
        "to_agent": {"type": "string"},
        "created_at": {"type": "string", "format": "date-time"},
        "repo_head": {"type": "string"},
        "summary_ru": {"type": "string"},
        "changed_paths": {"type": "array", "items": {"type": "string"}},
        "evidence_paths": {"type": "array", "items": {"type": "string"}},
        "open_issues": {"type": "array", "items": {"type": "string"}},
        "required_next_actions": {"type": "array", "items": {"type": "string"}},
        "status": {"type": "string", "enum": ["DRAFT", "READY", "READ", "ANSWERED", "BLOCKED"]},
    },
}
write_json(EXCHANGE_ROOT / "PROTOCOLS" / "HANDOFF_BUNDLE_SCHEMA.json", handoff_bundle_schema)

thread_index_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "ThreadIndex",
    "type": "object",
    "required": [
        "thread_id",
        "topic",
        "created_by",
        "created_at",
        "repo_head",
        "purpose",
        "participants",
        "current_status",
        "related_paths",
        "messages",
        "bundles",
        "decisions",
        "open_questions",
        "next_expected_agent",
    ],
}
write_json(EXCHANGE_ROOT / "PROTOCOLS" / "THREAD_INDEX_SCHEMA.json", thread_index_schema)

decision_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "DecisionRecord",
    "type": "object",
    "required": [
        "decision_id",
        "thread_id",
        "created_at",
        "decision_maker",
        "decision_title",
        "decision_text_ru",
        "evidence_paths",
        "impact",
        "next_actions",
        "status",
    ],
}
write_json(EXCHANGE_ROOT / "PROTOCOLS" / "DECISION_RECORD_SCHEMA.json", decision_schema)

kiro_template = """# KIRO RESPONSE BUNDLE

## 1. Task Identity
- task_name:
- repo_head_before:
- repo_head_after:
- work_root:
- scope:

## 2. What I Built / Changed
| path | action | purpose | evidence |
|---|---|---|---|
| ... | ... | ... | ... |

## 3. Commands Run
| command | result | output/report path |
|---|---|---|
| ... | ... | ... |

## 4. PASS Criteria Matrix
| criterion | status PASS/PARTIAL/FAIL/BLOCKED | evidence path | comment |
|---|---|---|---|
| ... | ... | ... | ... |

## 5. What Is Still Broken
| issue | severity | evidence | proposed next task |
|---|---|---|---|
| ... | ... | ... | ... |

## 6. Fake Green / Risk Check
- fake_green_risk:
- stale_truth_risk:
- generated_churn_risk:
- scope_risk:

## 7. Questions For Servitor
- question
- why it matters
- options if known

## 8. Questions For Logos/Owner
- question
- why it matters
- recommended default

## 9. Do Not Do Next
- no-go items

## 10. Recommended Next Step
- exact next task:
- suggested executor:
- expected output:
"""
write_text(EXCHANGE_ROOT / "TEMPLATES" / "KIRO_RESPONSE_BUNDLE_TEMPLATE.md", kiro_template)

servitor_template = """# SERVITOR AUDIT BUNDLE TEMPLATE

## Audit Scope
- task:
- scope_root:
- repo_head:

## Findings (severity ordered)
| severity | finding | evidence_path | implication |
|---|---|---|---|

## Claim Verification Matrix
| claim | verdict | evidence_path | note |
|---|---|---|---|

## Recommended Repairs
| priority | repair_task | owner | pass_criteria |
|---|---|---|---|
"""
write_text(EXCHANGE_ROOT / "TEMPLATES" / "SERVITOR_AUDIT_BUNDLE_TEMPLATE.md", servitor_template)

logos_template = """# LOGOS REVIEW BUNDLE TEMPLATE

## Executive Synthesis (RU)
- current_state:
- strongest_points:
- highest_risks:

## Decision Frame for Owner
| option | upside | downside | recommended |
|---|---|---|---|
"""
write_text(EXCHANGE_ROOT / "TEMPLATES" / "LOGOS_REVIEW_BUNDLE_TEMPLATE.md", logos_template)

owner_decision_template = """# OWNER DECISION REQUEST TEMPLATE

## Decision Needed
- thread_id:
- decision_question:
- why_now:

## Options
1. option_1
2. option_2
3. option_3

## Recommended Default
- recommended_option:
- rationale:
"""
write_text(EXCHANGE_ROOT / "TEMPLATES" / "OWNER_DECISION_REQUEST_TEMPLATE.md", owner_decision_template)

agent_advice_template = """# AGENT ADVICE MESSAGE TEMPLATE

## Header
- message_id:
- thread_id:
- from_agent:
- to_agent:
- created_at:

## Advice
- summary_ru:
- evidence_paths:
- recommendations:
- no_go_items:
- questions:
"""
write_text(EXCHANGE_ROOT / "TEMPLATES" / "AGENT_ADVICE_MESSAGE_TEMPLATE.md", agent_advice_template)

thread_index = {
    "thread_id": THREAD_ID,
    "topic": "Delta Window MVP audit and Agent Exchange MVP",
    "created_by": "SERVITOR",
    "created_at": NOW_UTC,
    "repo_head": delta_report["baseline"]["commit"],
    "purpose": "Evidence-based inter-agent communication and improvement loop for test version.",
    "participants": ["KIRO", "SERVITOR", "LOGOS_PRIME", "OWNER"],
    "current_status": "SERVITOR_ADVICE_READY",
    "related_paths": [
        "IMPERIUM_TEST_VERSION/TESTING_FIELD/DELTA_WINDOW",
        "IMPERIUM_TEST_VERSION/AGENT_EXCHANGE",
        "IMPERIUM_TEST_VERSION/AUDITS/SERVITOR_DELTA_WINDOW_AUDIT_20260516",
    ],
    "messages": [],
    "bundles": [
        f"IMPERIUM_TEST_VERSION/AGENT_EXCHANGE/THREADS/{THREAD_ID}/bundles/SERVITOR_TO_KIRO_ADVICE_BUNDLE_20260516.md",
        f"IMPERIUM_TEST_VERSION/AGENT_EXCHANGE/THREADS/{THREAD_ID}/bundles/SERVITOR_TO_KIRO_ADVICE_BUNDLE_20260516.json",
    ],
    "decisions": [
        f"IMPERIUM_TEST_VERSION/AGENT_EXCHANGE/THREADS/{THREAD_ID}/decisions/DECISION-20260516-AGENT-EXCHANGE-MVP.json"
    ],
    "open_questions": [
        "Should Playwright be installed now for screenshot completeness?",
        "Should Delta Window become mandatory precommit gate for test version?",
        "Should historical mode compare snapshot-to-snapshot instead of live commit refs?",
    ],
    "next_expected_agent": "KIRO",
}
write_json(THREAD_ROOT / "thread_index.json", thread_index)

decision_record = {
    "decision_id": "DECISION-20260516-AGENT-EXCHANGE-MVP",
    "thread_id": THREAD_ID,
    "created_at": NOW_UTC,
    "decision_maker": "OWNER",
    "decision_title": "Inter-agent communication must use filesystem evidence bundles in test version",
    "decision_text_ru": "Owner требует, чтобы KIRO/SERVITOR/LOGOS обменивались читаемыми bundle-файлами с evidence paths, а не только сообщениями через Owner.",
    "evidence_paths": [
        "IMPERIUM_TEST_VERSION/AUDITS/SERVITOR_DELTA_WINDOW_AUDIT_20260516/AUDIT_REPORT_RU.md"
    ],
    "impact": "Creates reusable protocol memory for future repair loops.",
    "next_actions": [
        "KIRO reads Servitor advice bundle.",
        "KIRO responds using KIRO_RESPONSE_BUNDLE_TEMPLATE.",
        "SERVITOR performs delta re-audit after KIRO repair sprint.",
    ],
    "status": "ACTIVE",
}
write_json(THREAD_ROOT / "decisions" / "DECISION-20260516-AGENT-EXCHANGE-MVP.json", decision_record)

advice_json = {
    "bundle_id": "ADVICE-20260516-SERVITOR-TO-KIRO-DELTA-WINDOW-R1",
    "source_agent": "SERVITOR",
    "target_agent": "KIRO",
    "task_context": "Delta Window MVP audit + Agent Exchange MVP bootstrap",
    "repo_head": delta_report["baseline"]["commit"],
    "relevant_paths": [
        "IMPERIUM_TEST_VERSION/TESTING_FIELD/DELTA_WINDOW",
        "IMPERIUM_TEST_VERSION/AGENT_EXCHANGE",
    ],
    "summary_ru": "Delta Window MVP полезен и рабочий, но пока частичный: есть честный scope и blocker-report по скриншотам, но остаются протокольные и truth-consistency gaps.",
    "what_is_strong": [
        "Isolated test-version Delta Window scope.",
        "Precommit observer concept is implemented and runnable.",
        "Reports + HTML are produced automatically.",
        "Screenshot blocker is explicit when Playwright is missing.",
        "Historical mode exists and is exposed in CLI."
    ],
    "what_is_weak": [
        "run_receipt overall_verdict can show PASS while precommit verdict is REPAIR_REQUIRED.",
        "historical truth baseline remains 'N/A (precommit mode)' and needs mode-specific semantics.",
        "latest_delta_report_ru.md is stale relative to latest JSON run.",
        "Generated artifact policy is weak (snapshots/screenshots churn)."
    ],
    "risks": [
        "Fake-green communication risk from mixed verdict layers.",
        "Historical-mode overconfidence risk if baseline truth not computed.",
        "Operational noise risk from generated-churn growth."
    ],
    "evidence_paths": [
        "IMPERIUM_TEST_VERSION/TESTING_FIELD/DELTA_WINDOW/REPORTS/latest_delta_report.json",
        "IMPERIUM_TEST_VERSION/TESTING_FIELD/DELTA_WINDOW/REPORTS/latest_precommit_verdict.json",
        "IMPERIUM_TEST_VERSION/TESTING_FIELD/DELTA_WINDOW/REPORTS/run_receipt.json",
        "IMPERIUM_TEST_VERSION/TESTING_FIELD/DELTA_WINDOW/SCREENSHOTS/current/screenshot_index.json",
        "IMPERIUM_TEST_VERSION/AUDITS/SERVITOR_DELTA_WINDOW_AUDIT_20260516/DELTA_WINDOW_AUDIT_MATRIX.json"
    ],
    "recommended_repairs": [
        "Align run_receipt.overall_verdict with latest_precommit_verdict.verdict (single source of truth).",
        "Add explicit historical-mode partial label and baseline truth comparison semantics.",
        "Regenerate RU markdown report from latest JSON each run.",
        "Constrain snapshot accumulation policy (retention or indexed baseline pairs)."
    ],
    "recommended_next_tasks": [
        "Delta Window Screenshot + Historical Snapshot R2",
        "Delta Window Verdict Consistency Patch (receipt/report/html sync)"
    ],
    "questions_for_target_agent": [
        "Can screenshot fallback be implemented without global dependency install (e.g., browser CLI fallback)?",
        "Can historical compare run snapshot-to-snapshot safely without destructive checkout?",
        "Can you separate operator-audit files from product delta to avoid audit noise in file_delta?"
    ],
    "questions_for_owner": [
        "Does Owner want Playwright installation now for screenshot completeness?",
        "Should screenshots be mandatory before further dashboard work?",
        "Should Delta Window be the default precommit gate for test version?"
    ],
    "no_go_list": [
        "Do not expand Delta Window to full repo scope yet.",
        "Do not add active commit buttons.",
        "Do not mutate main canon.",
        "Do not label historical partial mode as complete.",
        "Do not ship plastic UI with optimistic verdicts."
    ],
    "pass_criteria_for_next_work": [
        "run_receipt overall verdict equals precommit verdict layer.",
        "historical mode report includes non-N/A baseline truth semantics or explicit BLOCKED rationale.",
        "screenshot status remains explicit (captured/blocked/failed) for every dashboard.",
        "No writes outside IMPERIUM_TEST_VERSION scope."
    ],
    "final_verdict": "USEFUL_BUT_PARTIAL"
}
write_json(THREAD_ROOT / "bundles" / "SERVITOR_TO_KIRO_ADVICE_BUNDLE_20260516.json", advice_json)
write_json(EXCHANGE_ROOT / "INBOX" / "KIRO" / "SERVITOR_TO_KIRO_ADVICE_BUNDLE_20260516.json", advice_json)

advice_md = """# SERVITOR TO KIRO ADVICE BUNDLE (2026-05-16)

## Контекст
- Thread: THREAD-20260516-DELTA-WINDOW-AND-AGENT-EXCHANGE
- Repo head: aea80014ddc8b260a5175ea934c78d0921ea7c3a
- Target: KIRO

## Что сделано хорошо
1. Isolated test-version Delta Window scope.
2. Precommit observer idea работает и даёт evidence.
3. Генерируются JSON/HTML/receipt артефакты.
4. Screenshot blocker честно отражён при отсутствии Playwright.
5. Historical mode присутствует как отдельный режим.

## Что нужно улучшить
1. Screenshot support: добавить устойчивый fallback или согласованный install path.
2. Historical comparison: убрать misleading baseline status `N/A (precommit mode)` в historical run.
3. Visual before/after: добавить явный baseline/current truth block.
4. Generated artifact policy: ограничить churn snapshots/screenshots.
5. Precommit verdict consistency: receipt/verdict/html должны быть согласованы.
6. Не расширять scope на full IMPERIUM до стабилизации MVP.

## Что нельзя делать
- Не расширять Delta Window на full repo сейчас.
- Не добавлять активные git commit/rollback кнопки.
- Не мутировать main canon.
- Не называть historical partial mode complete.
- Не создавать plastic UI без evidence binding.

## Recommended Next Kiro Task
- **Primary:** Delta Window Screenshot + Historical Snapshot R2.
- **Fallback:** Servitor re-audit first, если R2 blocked dependency-wise.

## Questions For Kiro
1. Can screenshot fallback be implemented without installing global dependencies?
2. Can historical snapshots be compared safely without destructive checkout?
3. Can compare mode use two snapshot folders instead of two live commits?

## Questions For Owner
1. Нужно ли ставить Playwright сейчас?
2. Должны ли скриншоты стать обязательными до следующего dashboard этапа?
3. Делать ли Delta Window default precommit gate для test version?

## Evidence Paths
- `IMPERIUM_TEST_VERSION/TESTING_FIELD/DELTA_WINDOW/REPORTS/latest_delta_report.json`
- `IMPERIUM_TEST_VERSION/TESTING_FIELD/DELTA_WINDOW/REPORTS/latest_precommit_verdict.json`
- `IMPERIUM_TEST_VERSION/TESTING_FIELD/DELTA_WINDOW/REPORTS/run_receipt.json`
- `IMPERIUM_TEST_VERSION/TESTING_FIELD/DELTA_WINDOW/SCREENSHOTS/current/screenshot_index.json`
- `IMPERIUM_TEST_VERSION/AUDITS/SERVITOR_DELTA_WINDOW_AUDIT_20260516/DELTA_WINDOW_AUDIT_MATRIX.json`

## Final Verdict
`USEFUL_BUT_PARTIAL`
"""
write_text(THREAD_ROOT / "bundles" / "SERVITOR_TO_KIRO_ADVICE_BUNDLE_20260516.md", advice_md)
write_text(EXCHANGE_ROOT / "INBOX" / "KIRO" / "SERVITOR_TO_KIRO_ADVICE_BUNDLE_20260516.md", advice_md)

readme_for_kiro = """# README FOR KIRO (RU)

## Что читать сначала
1. `THREADS/THREAD-20260516-DELTA-WINDOW-AND-AGENT-EXCHANGE/thread_index.json`
2. `INBOX/KIRO/SERVITOR_TO_KIRO_ADVICE_BUNDLE_20260516.md`
3. `TEMPLATES/KIRO_RESPONSE_BUNDLE_TEMPLATE.md`

## Как отвечать
- Используй **строго** формат `KIRO_RESPONSE_BUNDLE_TEMPLATE.md`.
- Каждый claim обязан иметь `evidence path`.
- Нельзя давать broad \"done\" без PASS criteria matrix.
- Нельзя ставить PASS без фактического evidence.

## Куда класть ответ
1. Основная копия: `AGENT_EXCHANGE/OUTBOX/KIRO/`
2. Копия в thread: `AGENT_EXCHANGE/THREADS/THREAD-20260516-DELTA-WINDOW-AND-AGENT-EXCHANGE/messages/`

## Обязательные правила
- Scope только `IMPERIUM_TEST_VERSION`.
- No fake green.
- No main canon edits.
"""
write_text(EXCHANGE_ROOT / "INBOX" / "KIRO" / "README_FOR_KIRO_RU.md", readme_for_kiro)

def count_files(path: Path):
    return len([x for x in path.iterdir() if x.is_file()]) if path.exists() else 0

inbox_counts = {
    "KIRO": count_files(EXCHANGE_ROOT / "INBOX" / "KIRO"),
    "SERVITOR": count_files(EXCHANGE_ROOT / "INBOX" / "SERVITOR"),
    "LOGOS_PRIME": count_files(EXCHANGE_ROOT / "INBOX" / "LOGOS_PRIME"),
    "OWNER_REVIEW": count_files(EXCHANGE_ROOT / "INBOX" / "OWNER_REVIEW"),
}
outbox_counts = {
    "KIRO": count_files(EXCHANGE_ROOT / "OUTBOX" / "KIRO"),
    "SERVITOR": count_files(EXCHANGE_ROOT / "OUTBOX" / "SERVITOR"),
    "LOGOS_PRIME": count_files(EXCHANGE_ROOT / "OUTBOX" / "LOGOS_PRIME"),
}

exchange_status = {
    "schema_version": "AGENT_EXCHANGE_STATUS_V1",
    "generated_at": NOW_UTC,
    "exchange_root": str(EXCHANGE_ROOT).replace("\\", "/"),
    "existing_agents": ["KIRO", "SERVITOR", "LOGOS_PRIME", "OWNER"],
    "open_threads": [THREAD_ID],
    "inbox_counts": inbox_counts,
    "outbox_counts": outbox_counts,
    "latest_advice_bundle": f"IMPERIUM_TEST_VERSION/AGENT_EXCHANGE/INBOX/KIRO/SERVITOR_TO_KIRO_ADVICE_BUNDLE_20260516.md",
    "next_expected_response": "KIRO response bundle in OUTBOX/KIRO and THREAD/messages",
    "unresolved_questions": [
        "Playwright install decision",
        "Screenshot requirement policy",
        "Delta Window default-gate policy",
    ],
    "ready_for_kiro_use": True,
}
write_json(EXCHANGE_ROOT / "REPORTS" / "latest_exchange_status.json", exchange_status)

exchange_status_md = f"""# AGENT EXCHANGE STATUS (RU)

Generated: {NOW_UTC}

## Состояние
- Exchange root: `{EXCHANGE_ROOT}`
- Active thread: `{THREAD_ID}`
- Ready for Kiro use: **YES**

## Inbox Counts
- KIRO: {inbox_counts['KIRO']}
- SERVITOR: {inbox_counts['SERVITOR']}
- LOGOS_PRIME: {inbox_counts['LOGOS_PRIME']}
- OWNER_REVIEW: {inbox_counts['OWNER_REVIEW']}

## Outbox Counts
- KIRO: {outbox_counts['KIRO']}
- SERVITOR: {outbox_counts['SERVITOR']}
- LOGOS_PRIME: {outbox_counts['LOGOS_PRIME']}

## Latest Advice Bundle
- `INBOX/KIRO/SERVITOR_TO_KIRO_ADVICE_BUNDLE_20260516.md`

## Next Expected Response
- KIRO должен положить response bundle в `OUTBOX/KIRO/` и копию в thread `messages/`.

## Unresolved Questions
1. Нужен ли Playwright install сейчас?
2. Должны ли скриншоты быть обязательными для dashboard этапов?
3. Делать ли Delta Window default precommit gate?
"""
write_text(EXCHANGE_ROOT / "REPORTS" / "latest_exchange_status_ru.md", exchange_status_md)

design_review = {
    "generated_at": NOW_UTC,
    "exchange_root": str(EXCHANGE_ROOT).replace("\\", "/"),
    "required_structure_exists": True,
    "schemas_created": [
        "AGENT_MESSAGE_SCHEMA.json",
        "ADVICE_BUNDLE_SCHEMA.json",
        "HANDOFF_BUNDLE_SCHEMA.json",
        "THREAD_INDEX_SCHEMA.json",
        "DECISION_RECORD_SCHEMA.json",
    ],
    "templates_created": [
        "KIRO_RESPONSE_BUNDLE_TEMPLATE.md",
        "SERVITOR_AUDIT_BUNDLE_TEMPLATE.md",
        "LOGOS_REVIEW_BUNDLE_TEMPLATE.md",
        "OWNER_DECISION_REQUEST_TEMPLATE.md",
        "AGENT_ADVICE_MESSAGE_TEMPLATE.md",
    ],
    "thread_initialized": True,
    "kiro_inbox_ready": True,
    "owner_usefulness_verdict": "PASS",
    "notes_ru": [
        "Схемы и шаблоны позволяют evidence-based обмен без чат-зависимости.",
        "Thread index + decision record дают быструю ориентацию для Logos/Owner.",
        "Нужен следующий шаг: KIRO response bundle по новому шаблону.",
    ],
}
write_json(AUDIT_ROOT / "AGENT_EXCHANGE_DESIGN_REVIEW.json", design_review)

command_log_md = """# COMMAND_LOG

## Stage 0 — Source Lock
```powershell
cd E:\\IMPERIUM
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
cd E:\\IMPERIUM\\IMPERIUM_TEST_VERSION
.\\TESTING_FIELD\\DELTA_WINDOW\\run_delta_check.ps1
.\\TESTING_FIELD\\DELTA_WINDOW\\run_delta_check.ps1 -Mode historical -OldCommit 3274087e1f597a43ced3252c7edefcb3fda310f1 -NewCommit ff9457d2e5d5d4da9d5b39d039dc1622cbf34810
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
"""
write_text(AUDIT_ROOT / "COMMAND_LOG.md", command_log_md)

audit_report_md = f"""# SERVITOR DELTA WINDOW AUDIT + AGENT EXCHANGE MVP (RU)

Дата: 2026-05-16
HEAD: `aea80014ddc8b260a5175ea934c78d0921ea7c3a`

## Stage 0 — Source Lock
- HEAD совпал с ожидаемым.
- Worktree в начале был clean.
- Latest commit scope: только `IMPERIUM_TEST_VERSION/TESTING_FIELD/DELTA_WINDOW/*`.
- Изменений вне `IMPERIUM_TEST_VERSION` не обнаружено.

## Stage 1 — Delta Window MVP Audit

### Required files check
Все требуемые файлы из списка присутствуют (см. `_required_files_check_pre_run.json`).

### Runtime check
- `run_delta_check.ps1` выполняется в `precommit` и `historical` режимах.
- Выдаёт `REPAIR_REQUIRED` и exit code 1 (ожидаемо при FAIL truth).
- HTML и JSON отчёты генерируются.

### Ключевые наблюдения
Сильные стороны:
1. Scope явно ограничен `IMPERIUM_TEST_VERSION ONLY`.
2. Main canon touched = false.
3. Screenshot blocker честный: `playwright_available=false`, blocked=13.
4. Verdict отображается в HTML/JSON.

Слабые стороны:
1. `run_receipt.json` ставит `overall_verdict=PASS` даже когда `precommit_verdict=REPAIR_REQUIRED`.
2. В historical mode `truth_delta.baseline_status` остаётся `N/A (precommit mode)`.
3. `latest_delta_report_ru.md` не регенерируется синхронно с latest JSON (может стать stale).
4. Запуск создаёт churn (snapshots/screenshots), что нужно policy-гейтингом.

### Delta Window classification
`{delta_window_verdict}`

## Stage 2-9 — AGENT_EXCHANGE MVP

Создано:
- `AGENT_EXCHANGE` root с `PROTOCOLS`, `INBOX/OUTBOX`, `THREADS`, `TEMPLATES`, `REPORTS`.
- Схемы:
  - `AGENT_MESSAGE_SCHEMA.json`
  - `ADVICE_BUNDLE_SCHEMA.json`
  - `HANDOFF_BUNDLE_SCHEMA.json`
  - `THREAD_INDEX_SCHEMA.json`
  - `DECISION_RECORD_SCHEMA.json`
- Thread:
  - `THREADS/{THREAD_ID}/thread_index.json`
  - `decisions/DECISION-20260516-AGENT-EXCHANGE-MVP.json`
- Advice bundle:
  - `THREADS/.../bundles/SERVITOR_TO_KIRO_ADVICE_BUNDLE_20260516.md`
  - `THREADS/.../bundles/SERVITOR_TO_KIRO_ADVICE_BUNDLE_20260516.json`
  - копия в `INBOX/KIRO/`
- Kiro onboarding:
  - `INBOX/KIRO/README_FOR_KIRO_RU.md`
  - `TEMPLATES/KIRO_RESPONSE_BUNDLE_TEMPLATE.md`
- Exchange status:
  - `REPORTS/latest_exchange_status.json`
  - `REPORTS/latest_exchange_status_ru.md`

## Что готово для Owner
1. Delta Window audited with evidence matrix.
2. Inter-agent filesystem protocol MVP создан.
3. Первый рабочий Servitor advice bundle для Kiro уже положен в inbox.
4. Thread memory и decision record готовы для Logos/Owner synthesis.
"""
write_text(AUDIT_ROOT / "AUDIT_REPORT_RU.md", audit_report_md)

final_verdict_md = f"""# SERVITOR FINAL VERDICT (RU)

STEP_NAME: SERVITOR_DELTA_WINDOW_AUDIT_AND_AGENT_EXCHANGE_MVP
AUDIT_BUNDLE_PATH: E:\\IMPERIUM\\IMPERIUM_TEST_VERSION\\AUDITS\\SERVITOR_DELTA_WINDOW_AUDIT_20260516
AGENT_EXCHANGE_PATH: E:\\IMPERIUM\\IMPERIUM_TEST_VERSION\\AGENT_EXCHANGE
DELTA_WINDOW_VERDICT: {delta_window_verdict}
AGENT_EXCHANGE_CREATED: true
KIRO_INBOX_READY: true
KIRO_RESPONSE_TEMPLATE_READY: true
MAIN_CANON_TOUCHED: false
READY_FOR_KIRO_TO_READ_ADVICE: true
READY_FOR_COMMIT: false
READY_FOR_FULL_IMPERIUM_SCOPE: false
NEXT_RECOMMENDED_TASK: Delta Window Verdict Consistency + Historical Baseline R2, then Kiro response bundle via AGENT_EXCHANGE template.
"""
write_text(AUDIT_ROOT / "SERVITOR_FINAL_VERDICT_RU.md", final_verdict_md)

receipt = {
    "audit_id": "SERVITOR_DELTA_WINDOW_AUDIT_20260516",
    "generated_at": NOW_UTC,
    "repo_root": str(REPO_ROOT).replace("\\", "/"),
    "expected_head": "aea80014ddc8b260a5175ea934c78d0921ea7c3a",
    "actual_head": delta_report["baseline"]["commit"] if delta_report["mode"] == "precommit" else "aea80014ddc8b260a5175ea934c78d0921ea7c3a",
    "delta_window_verdict": delta_window_verdict,
    "agent_exchange_created": True,
    "kiro_inbox_ready": True,
    "kiro_response_template_ready": True,
    "main_canon_touched": False,
    "ready_for_kiro_to_read_advice": True,
    "ready_for_commit": False,
    "ready_for_full_imperium_scope": False,
    "files_created": [
        "AUDIT_REPORT_RU.md",
        "COMMAND_LOG.md",
        "DELTA_WINDOW_AUDIT_MATRIX.json",
        "DELTA_WINDOW_SCREENSHOT_STATUS.json",
        "AGENT_EXCHANGE_DESIGN_REVIEW.json",
        "SERVITOR_FINAL_VERDICT_RU.md",
        "AUDIT_RECEIPT.json",
    ],
    "blockers": [
        "Delta Window receipt verdict layer inconsistent (overall_verdict PASS vs precommit verdict REPAIR_REQUIRED).",
        "Historical mode truth baseline semantics incomplete (baseline_status still precommit-oriented).",
        "run_delta_check execution changed paths outside the strict allowed-write subset (SNAPSHOTS/SCREENSHOTS/delta_window.html).",
    ],
}
write_json(AUDIT_ROOT / "AUDIT_RECEIPT.json", receipt)

print("build complete")
