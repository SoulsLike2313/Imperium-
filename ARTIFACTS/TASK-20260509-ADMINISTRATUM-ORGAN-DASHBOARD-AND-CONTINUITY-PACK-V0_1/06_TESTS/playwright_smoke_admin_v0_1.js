const { chromium } = require('playwright');

(async () => {
  const out = {
    started_at: new Date().toISOString(),
    checks: [],
    page_errors: [],
    console_errors: [],
    screenshots: []
  };
  const add = (name, ok, detail='') => out.checks.push({ name, ok, detail });

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

  page.on('pageerror', e => out.page_errors.push(String(e)));
  page.on('console', m => {
    if (m.type() === 'error') out.console_errors.push(m.text());
  });

  await page.goto('http://127.0.0.1:8792', { waitUntil: 'networkidle', timeout: 60000 });
  add('dashboard opens', true);

  const buildBtn = page.locator('#btnBuild');
  add('Build Continuity Pack button exists', await buildBtn.count() === 1, `count=${await buildBtn.count()}`);

  await page.screenshot({ path: 'E:/IMPERIUM/ARTIFACTS/TASK-20260509-ADMINISTRATUM-ORGAN-DASHBOARD-AND-CONTINUITY-PACK-V0_1/06_TESTS/playwright_01_initial.png', fullPage: true });
  out.screenshots.push('E:/IMPERIUM/ARTIFACTS/TASK-20260509-ADMINISTRATUM-ORGAN-DASHBOARD-AND-CONTINUITY-PACK-V0_1/06_TESTS/playwright_01_initial.png');

  const beforeText = await page.locator('#latestPack').innerText();

  await buildBtn.click();
  await page.waitForTimeout(2500);

  // wait for action log to mention build_result or compare_result
  await page.waitForFunction(() => {
    const el = document.querySelector('#actionLog');
    if (!el) return false;
    const t = el.textContent || '';
    return t.includes('build_result') || t.includes('build_ok=true');
  }, {}, { timeout: 120000 });

  const afterText = await page.locator('#latestPack').innerText();
  add('new pack path appears', afterText && afterText.includes('CONTINUITY_PACK_'), `before=${beforeText} | after=${afterText}`);

  const compareText = await page.locator('#latestComparison').innerText();
  add('comparison path appears', compareText && compareText.includes('CONTINUITY_COMPARISON_'), compareText);

  await page.screenshot({ path: 'E:/IMPERIUM/ARTIFACTS/TASK-20260509-ADMINISTRATUM-ORGAN-DASHBOARD-AND-CONTINUITY-PACK-V0_1/06_TESTS/playwright_02_after_build.png', fullPage: true });
  out.screenshots.push('E:/IMPERIUM/ARTIFACTS/TASK-20260509-ADMINISTRATUM-ORGAN-DASHBOARD-AND-CONTINUITY-PACK-V0_1/06_TESTS/playwright_02_after_build.png');

  add('no page errors', out.page_errors.length === 0, String(out.page_errors.length));
  add('no console errors', out.console_errors.length === 0, String(out.console_errors.length));

  out.finished_at = new Date().toISOString();
  out.pass = out.checks.every(c => c.ok) && out.page_errors.length === 0 && out.console_errors.length === 0;
  out.verdict = out.pass
    ? 'PASS_PLAYWRIGHT_ADMINISTRATUM_DASHBOARD_V0_1_SMOKE'
    : 'REPAIR_REQUIRED_PLAYWRIGHT_ADMINISTRATUM_DASHBOARD_V0_1';

  const fs = require('fs');
  fs.writeFileSync('E:/IMPERIUM/ARTIFACTS/TASK-20260509-ADMINISTRATUM-ORGAN-DASHBOARD-AND-CONTINUITY-PACK-V0_1/06_TESTS/PLAYWRIGHT_SMOKE_REPORT.json', JSON.stringify(out, null, 2), 'utf8');

  const md = [];
  md.push('# PLAYWRIGHT SMOKE REPORT');
  md.push('');
  md.push(`- Verdict: ${out.verdict}`);
  md.push(`- Pass: ${out.pass}`);
  md.push('');
  md.push('## Checks');
  for (const c of out.checks) md.push(`- ${c.name}: ${c.ok} (${c.detail})`);
  md.push('');
  md.push(`- page_errors: ${out.page_errors.length}`);
  md.push(`- console_errors: ${out.console_errors.length}`);
  md.push('');
  md.push('## Screenshots');
  for (const s of out.screenshots) md.push(`- ${s}`);
  fs.writeFileSync('E:/IMPERIUM/ARTIFACTS/TASK-20260509-ADMINISTRATUM-ORGAN-DASHBOARD-AND-CONTINUITY-PACK-V0_1/06_TESTS/PLAYWRIGHT_SMOKE_REPORT.md', md.join('\n') + '\n', 'utf8');

  await browser.close();
  console.log(JSON.stringify({ verdict: out.verdict, pass: out.pass }, null, 2));
})();
