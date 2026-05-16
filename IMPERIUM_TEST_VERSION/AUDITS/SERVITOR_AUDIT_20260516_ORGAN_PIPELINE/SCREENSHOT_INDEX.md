# SCREENSHOT_INDEX

- Screenshot: `IMPERIUM_TEST_VERSION/AUDITS/SERVITOR_AUDIT_20260516_ORGAN_PIPELINE/SCREENSHOTS/live_workbench.png`
  Dashboard: `http://localhost:8765/LIVE_WORKBENCH/DASHBOARD/index.html`
  Verdict: `USEFUL`
  Comment: Статический, но честно показывает sandbox test snapshot и не маскирует FAIL статусы других систем.
- Screenshot: `IMPERIUM_TEST_VERSION/AUDITS/SERVITOR_AUDIT_20260516_ORGAN_PIPELINE/SCREENSHOTS/organ_administratum.png`
  Dashboard: `http://localhost:8765/ORGANS/ADMINISTRATUM/DASHBOARD/index.html`
  Verdict: `BROKEN`
  Comment: Открывается, но все ключевые ссылки битые (неверные относительные пути).
- Screenshot: `IMPERIUM_TEST_VERSION/AUDITS/SERVITOR_AUDIT_20260516_ORGAN_PIPELINE/SCREENSHOTS/organ_astronomicon.png`
  Dashboard: `http://localhost:8765/ORGANS/ASTRONOMICON/DASHBOARD/index.html`
  Verdict: `BROKEN`
  Comment: Открывается, но evidence/navigation ссылки ведут в несуществующие пути.
- Screenshot: `IMPERIUM_TEST_VERSION/AUDITS/SERVITOR_AUDIT_20260516_ORGAN_PIPELINE/SCREENSHOTS/organ_custodes.png`
  Dashboard: `http://localhost:8765/ORGANS/CUSTODES/DASHBOARD/index.html`
  Verdict: `BROKEN`
  Comment: Открывается, но ссылки на контракт/скрипты/возврат в master битые.
- Screenshot: `IMPERIUM_TEST_VERSION/AUDITS/SERVITOR_AUDIT_20260516_ORGAN_PIPELINE/SCREENSHOTS/organ_doctrinarium.png`
  Dashboard: `http://localhost:8765/ORGANS/DOCTRINARIUM/DASHBOARD/index.html`
  Verdict: `BROKEN`
  Comment: Открывается, но ссылки на контракт/smoke/master невалидны.
- Screenshot: `IMPERIUM_TEST_VERSION/AUDITS/SERVITOR_AUDIT_20260516_ORGAN_PIPELINE/SCREENSHOTS/organ_inquisition.png`
  Dashboard: `http://localhost:8765/ORGANS/INQUISITION/DASHBOARD/index.html`
  Verdict: `USEFUL`
  Comment: Показывает FAIL/100 issues; статично, но owner-полезно для triage.
- Screenshot: `IMPERIUM_TEST_VERSION/AUDITS/SERVITOR_AUDIT_20260516_ORGAN_PIPELINE/SCREENSHOTS/organ_mechanicus.png`
  Dashboard: `http://localhost:8765/ORGANS/MECHANICUS/DASHBOARD/index.html`
  Verdict: `USEFUL`
  Comment: Показывает PARTIAL и broken script count; статично, но информативно.
- Screenshot: `IMPERIUM_TEST_VERSION/AUDITS/SERVITOR_AUDIT_20260516_ORGAN_PIPELINE/SCREENSHOTS/organ_officio_agentis.png`
  Dashboard: `http://localhost:8765/ORGANS/OFFICIO_AGENTIS/DASHBOARD/index.html`
  Verdict: `BROKEN`
  Comment: Открывается, но ссылки на контракт/скрипты/master битые.
- Screenshot: `IMPERIUM_TEST_VERSION/AUDITS/SERVITOR_AUDIT_20260516_ORGAN_PIPELINE/SCREENSHOTS/organ_schola_imperialis.png`
  Dashboard: `http://localhost:8765/ORGANS/SCHOLA_IMPERIALIS/DASHBOARD/index.html`
  Verdict: `BROKEN`
  Comment: Открывается, но множество broken evidence links (10).
- Screenshot: `IMPERIUM_TEST_VERSION/AUDITS/SERVITOR_AUDIT_20260516_ORGAN_PIPELINE/SCREENSHOTS/organ_strategium.png`
  Dashboard: `http://localhost:8765/ORGANS/STRATEGIUM/DASHBOARD/index.html`
  Verdict: `BROKEN`
  Comment: Открывается, но контракт/скрипты/master links битые.
- Screenshot: `IMPERIUM_TEST_VERSION/AUDITS/SERVITOR_AUDIT_20260516_ORGAN_PIPELINE/SCREENSHOTS/organ_throne.png`
  Dashboard: `http://localhost:8765/ORGANS/THRONE/DASHBOARD/index.html`
  Verdict: `BROKEN`
  Comment: Открывается, но все основные ссылки битые, включая report link.
- Screenshot: `IMPERIUM_TEST_VERSION/AUDITS/SERVITOR_AUDIT_20260516_ORGAN_PIPELINE/SCREENSHOTS/02_sanctum_mirror_legacy_dashboard.png`
  Dashboard: `http://localhost:8765/SANCTUM_MIRROR/dashboard.html`
  Verdict: `STATIC`
  Comment: Legacy статическая витрина, полезна как исторический контекст, не как truth-surface.
- Screenshot: `IMPERIUM_TEST_VERSION/AUDITS/SERVITOR_AUDIT_20260516_ORGAN_PIPELINE/SCREENSHOTS/00_sanctum_mirror_index.png`
  Dashboard: `http://localhost:8765/SANCTUM_MIRROR/index.html`
  Verdict: `PLASTIC`
  Comment: Статический status-board без live-source; есть пустые поля и encoding artefacts.
- Screenshot: `IMPERIUM_TEST_VERSION/AUDITS/SERVITOR_AUDIT_20260516_ORGAN_PIPELINE/SCREENSHOTS/01_master_dashboard.png`
  Dashboard: `http://localhost:8765/SANCTUM_MIRROR/master_dashboard.html`
  Verdict: `PLASTIC`
  Comment: Есть evidence links, но статический snapshot с overclaim 7/7 COMPLETE и устаревающими значениями.
