import { chromium } from "playwright";
import fs from "fs";
import path from "path";

const URL = "http://127.0.0.1:8791";
const outDir = process.cwd();
const screenshotsDir = path.join(outDir, "screenshots");
fs.mkdirSync(screenshotsDir, { recursive: true });

const report = {
  audit_id: "DOCTRINARIUM_DASHBOARD_V0_8_PLAYWRIGHT_AUDIT",
  started_at: new Date().toISOString(),
  url: URL,
  checks: [],
  screenshots: [],
  console_warnings: [],
  page_errors: [],
  metrics: {}
};

function check(name, ok, detail = "") {
  report.checks.push({ name, ok, detail });
  console.log(`${ok ? "PASS" : "FAIL"} - ${name}${detail ? " :: " + detail : ""}`);
}

async function shot(page, name) {
  const file = path.join(screenshotsDir, `${name}.png`);
  await page.screenshot({ path: file, fullPage: true });
  report.screenshots.push(file);
  console.log(`SCREENSHOT - ${file}`);
}

async function nav(page, view, label, shotName) {
  await page.locator(`.nav-item[data-view="${view}"]`).click();
  await page.waitForTimeout(600);
  await shot(page, shotName);
  const active = await page.locator(`#view-${view}.active`).count();
  check(`Navigation opens ${label}`, active === 1, `active=${active}`);
}

async function visibleText(page, text, name) {
  const count = await page.locator(`text=${text}`).count();
  check(name, count > 0, `text="${text}" count=${count}`);
}

const browser = await chromium.launch({
  headless: false,
  args: ["--start-maximized"]
});

const context = await browser.newContext({
  viewport: { width: 1800, height: 1050 },
  deviceScaleFactor: 1
});

const page = await context.newPage();

page.on("console", msg => {
  if (["warning", "error"].includes(msg.type())) {
    report.console_warnings.push({ type: msg.type(), text: msg.text() });
  }
});

page.on("pageerror", err => {
  report.page_errors.push(err.message);
});

try {
  await page.goto(URL, { waitUntil: "networkidle", timeout: 20000 });

  await visibleText(page, "Doctrinarium Control Panel", "Header visible");
  await visibleText(page, "REAL TASK EXECUTION", "Real task card visible");
  await visibleText(page, "LAWS NOT ENFORCED", "Laws metric visible");
  await visibleText(page, "ORGAN BLOCKERS", "Blockers metric visible");

  check("Background canvas exists", await page.locator("canvas#bgCanvas").count() === 1);
  check("Spark canvas exists", await page.locator("canvas#sparkCanvas").count() === 1);
  check("Dashboard nav exists", await page.locator('.nav-item[data-view="dashboard"]').count() === 1);
  check("Priority nav exists", await page.locator('.nav-item[data-view="priority"]').count() === 1);
  check("Risk nav exists", await page.locator('.nav-item[data-view="risk"]').count() === 1);

  await shot(page, "01_dashboard_initial");

  const api = await page.request.get(`${URL}/api/data?audit=${Date.now()}`);
  check("API /api/data returns OK", api.ok(), `status=${api.status()}`);

  if (api.ok()) {
    const data = await api.json();

    report.metrics.organs_checked = data?.gaps?.total_organs_checked;
    report.metrics.total_blockers = data?.gaps?.total_blockers_found;
    report.metrics.utility_declared = data?.utility?.summary?.utility_declared_count;
    report.metrics.utility_backed = data?.utility?.summary?.script_backed_count;
    report.metrics.laws_total = data?.status?.law_registry_status?.total_laws;
    report.metrics.laws_not_enforced = data?.status?.law_registry_status?.not_fully_enforced_count;
    report.metrics.priority_fixes = data?.useful?.priority_fixes?.length || 0;
    report.metrics.risk_items = data?.useful?.organ_risk?.length || 0;

    check("API has status", !!data.status);
    check("API has gaps", !!data.gaps);
    check("API has utility", !!data.utility);
    check("API has laws", !!data.laws || !!data.mandatory_laws);
    check("API has useful metrics", !!data.useful);
    check("Organs checked >= 1", Number(data?.gaps?.total_organs_checked || 0) >= 1, `value=${data?.gaps?.total_organs_checked}`);
    check("Blockers visible >= 1", Number(data?.gaps?.total_blockers_found || 0) >= 1, `value=${data?.gaps?.total_blockers_found}`);
    check("Priority fixes generated", Number(data?.useful?.priority_fixes?.length || 0) >= 1, `value=${data?.useful?.priority_fixes?.length || 0}`);
    check("Risk matrix generated", Number(data?.useful?.organ_risk?.length || 0) >= 1, `value=${data?.useful?.organ_risk?.length || 0}`);
  }

  await nav(page, "laws", "Laws & Codex", "02_laws_codex");

  const lawCards = await page.locator("#lawList .law-card").count();
  const lawText = await page.locator("#view-laws").innerText();
  check("Laws page not empty", lawCards > 1 || lawText.includes("LAW-001"), `lawCards=${lawCards}`);
  check("Laws page contains Codex registry", lawText.includes("CODEX") || lawText.includes("LAW_INDEX"), "Codex source visible");
  check("Laws page contains law identifiers", /LAW-\d+/.test(lawText), "LAW-* visible");

  await nav(page, "organs", "Organ Health", "03_organ_health");

  const organCards = await page.locator("#organCards .organ-card").count();
  check("Organ cards rendered", organCards >= 1, `count=${organCards}`);

  if (organCards >= 1) {
    await page.locator("#organCards .organ-card").first().click();
    await page.waitForTimeout(500);

    const drawerVisible = await page.locator("#organDrawer:not(.hidden)").count();
    check("Organ detail drawer opens", drawerVisible === 1, `visible=${drawerVisible}`);
    await shot(page, "04_organ_detail_drawer");

    const drawerText = await page.locator("#organDrawer").innerText();
    check("Drawer shows risk", drawerText.toLowerCase().includes("risk"));
    check("Drawer shows evidence", drawerText.toLowerCase().includes("evidence"));
    check("Drawer shows priority actions", drawerText.toLowerCase().includes("priority actions"));

    await page.locator("#drawerClose").click();
    await page.waitForTimeout(300);
  }

  await nav(page, "gaps", "Major Gaps", "05_major_gaps");
  const gapCards = await page.locator("#gapList .gap-card").count();
  check("Major gaps rendered", gapCards >= 1, `count=${gapCards}`);

  await nav(page, "utility", "Utility Matrix", "06_utility_matrix");
  const utilityCards = await page.locator("#utilityCards .organ-card").count();
  check("Utility cards rendered", utilityCards >= 1, `count=${utilityCards}`);

  await nav(page, "priority", "Priority Fixes", "07_priority_fixes");
  const priorityCards = await page.locator("#priorityList .gap-card").count();
  check("Priority fix cards rendered", priorityCards >= 1, `count=${priorityCards}`);

  await nav(page, "risk", "Risk Matrix", "08_risk_matrix");
  const riskCards = await page.locator("#riskMatrix .organ-card").count();
  check("Risk matrix cards rendered", riskCards >= 1, `count=${riskCards}`);

  await nav(page, "paths", "Paths", "09_paths");
  await visibleText(page, "Reports", "Paths page has report paths");

  await page.locator("#btnReload").click();
  await page.waitForTimeout(800);
  await shot(page, "10_after_reload_data");
  check("Reload Data clicked", true);

  await nav(page, "dashboard", "Dashboard", "11_dashboard_return");

} catch (err) {
  report.page_errors.push(err.stack || String(err));
  check("Fatal audit exception", false, err.message || String(err));
}

report.finished_at = new Date().toISOString();

const hardFails = report.checks.filter(c => !c.ok);
report.verdict = hardFails.length === 0 && report.page_errors.length === 0
  ? "PASS_PLAYWRIGHT_V0_8_VISUAL_FUNCTIONAL_AUDIT"
  : "REVIEW_REQUIRED_PLAYWRIGHT_V0_8";

report.pass = report.verdict.startsWith("PASS");

fs.writeFileSync(
  path.join(outDir, "PLAYWRIGHT_AUDIT_V0_8_REPORT.json"),
  JSON.stringify(report, null, 2),
  "utf8"
);

const md = [
  "# Doctrinarium Dashboard v0.8 Playwright Audit",
  "",
  `- URL: ${report.url}`,
  `- Started: ${report.started_at}`,
  `- Finished: ${report.finished_at}`,
  `- Verdict: ${report.verdict}`,
  "",
  "## Metrics",
  ...Object.entries(report.metrics).map(([k, v]) => `- ${k}: ${v}`),
  "",
  "## Checks",
  ...report.checks.map(c => `- ${c.ok ? "PASS" : "FAIL"} — ${c.name}${c.detail ? " — " + c.detail : ""}`),
  "",
  "## Screenshots",
  ...report.screenshots.map(s => `- ${s}`),
  "",
  "## Console Warnings / Errors",
  ...(report.console_warnings.length ? report.console_warnings.map(e => `- ${e.type}: ${e.text}`) : ["- none"]),
  "",
  "## Page Errors",
  ...(report.page_errors.length ? report.page_errors.map(e => `- ${e}`) : ["- none"])
].join("\n");

fs.writeFileSync(path.join(outDir, "PLAYWRIGHT_AUDIT_V0_8_REPORT.md"), md, "utf8");

console.log("");
console.log(`FINAL VERDICT: ${report.verdict}`);
console.log(`REPORT JSON: ${path.join(outDir, "PLAYWRIGHT_AUDIT_V0_8_REPORT.json")}`);
console.log(`REPORT MD: ${path.join(outDir, "PLAYWRIGHT_AUDIT_V0_8_REPORT.md")}`);

await page.waitForTimeout(1500);
await browser.close();
