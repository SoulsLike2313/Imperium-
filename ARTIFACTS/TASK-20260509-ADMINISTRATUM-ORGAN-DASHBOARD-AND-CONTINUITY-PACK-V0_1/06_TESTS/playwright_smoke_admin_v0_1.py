import json
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_JSON = Path(r"E:\IMPERIUM\ARTIFACTS\TASK-20260509-ADMINISTRATUM-ORGAN-DASHBOARD-AND-CONTINUITY-PACK-V0_1\06_TESTS\PLAYWRIGHT_SMOKE_REPORT.json")
OUT_MD = Path(r"E:\IMPERIUM\ARTIFACTS\TASK-20260509-ADMINISTRATUM-ORGAN-DASHBOARD-AND-CONTINUITY-PACK-V0_1\06_TESTS\PLAYWRIGHT_SMOKE_REPORT.md")
SHOT1 = r"E:\IMPERIUM\ARTIFACTS\TASK-20260509-ADMINISTRATUM-ORGAN-DASHBOARD-AND-CONTINUITY-PACK-V0_1\06_TESTS\playwright_01_initial.png"
SHOT2 = r"E:\IMPERIUM\ARTIFACTS\TASK-20260509-ADMINISTRATUM-ORGAN-DASHBOARD-AND-CONTINUITY-PACK-V0_1\06_TESTS\playwright_02_after_build.png"

out = {
  'started_at': None,
  'checks': [],
  'page_errors': [],
  'console_errors': [],
  'screenshots': [],
}

def add(name, ok, detail=''):
  out['checks'].append({'name': name, 'ok': bool(ok), 'detail': detail})

with sync_playwright() as p:
  out['started_at'] = __import__('datetime').datetime.utcnow().isoformat() + 'Z'
  browser = p.chromium.launch(headless=True)
  page = browser.new_page(viewport={'width': 1440, 'height': 900})

  page.on('pageerror', lambda e: out['page_errors'].append(str(e)))
  def on_console(msg):
    if msg.type == 'error':
      out['console_errors'].append(msg.text)
  page.on('console', on_console)

  page.goto('http://127.0.0.1:8792', wait_until='networkidle', timeout=60000)
  add('dashboard opens', True)

  build_btn = page.locator('#btnBuild')
  count = build_btn.count()
  add('Build Continuity Pack button exists', count == 1, f'count={count}')

  page.screenshot(path=SHOT1, full_page=True)
  out['screenshots'].append(SHOT1)

  before_text = page.locator('#latestPack').inner_text()
  build_btn.click()

  page.wait_for_timeout(2500)
  page.wait_for_function(
    """
    () => {
      const el = document.querySelector('#actionLog');
      if (!el) return false;
      const t = el.textContent || '';
      return t.includes('build_result') || t.includes('build_ok=true');
    }
    """,
    timeout=120000,
  )

  after_text = page.locator('#latestPack').inner_text()
  add('new pack path appears', bool(after_text and 'CONTINUITY_PACK_' in after_text), f'before={before_text} | after={after_text}')

  compare_text = page.locator('#latestComparison').inner_text()
  add('comparison path appears', bool(compare_text and 'CONTINUITY_COMPARISON_' in compare_text), compare_text)

  page.screenshot(path=SHOT2, full_page=True)
  out['screenshots'].append(SHOT2)

  add('no page errors', len(out['page_errors']) == 0, str(len(out['page_errors'])))
  add('no console errors', len(out['console_errors']) == 0, str(len(out['console_errors'])))

  browser.close()

out['finished_at'] = __import__('datetime').datetime.utcnow().isoformat() + 'Z'
out['pass'] = all(c['ok'] for c in out['checks']) and len(out['page_errors']) == 0 and len(out['console_errors']) == 0
out['verdict'] = 'PASS_PLAYWRIGHT_ADMINISTRATUM_DASHBOARD_V0_1_SMOKE' if out['pass'] else 'REPAIR_REQUIRED_PLAYWRIGHT_ADMINISTRATUM_DASHBOARD_V0_1'

OUT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')

md = []
md.append('# PLAYWRIGHT SMOKE REPORT')
md.append('')
md.append(f"- Verdict: {out['verdict']}")
md.append(f"- Pass: {out['pass']}")
md.append('')
md.append('## Checks')
for c in out['checks']:
  md.append(f"- {c['name']}: {c['ok']} ({c['detail']})")
md.append('')
md.append(f"- page_errors: {len(out['page_errors'])}")
md.append(f"- console_errors: {len(out['console_errors'])}")
md.append('')
md.append('## Screenshots')
for s in out['screenshots']:
  md.append(f"- {s}")
OUT_MD.write_text('\n'.join(md) + '\n', encoding='utf-8')

print(json.dumps({'verdict': out['verdict'], 'pass': out['pass']}, ensure_ascii=False, indent=2))
