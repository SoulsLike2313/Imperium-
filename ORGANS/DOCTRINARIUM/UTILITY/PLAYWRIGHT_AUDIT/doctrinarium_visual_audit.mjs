import { chromium } from "playwright";
import fs from "fs";
import path from "path";

const URL = "http://127.0.0.1:8787";
const outDir = process.cwd();
const screenshotsDir = path.join(outDir, "screenshots");
fs.mkdirSync(screenshotsDir, { recursive: true });

const report = {
  started_at: new Date().toISOString(),
  url: URL,
  checks: [],
  screenshots: [],
  errors: []
};

function addCheck(name, ok, detail = "") {
  report.checks.push({ name, ok, detail });
  console.log(`${ok ? "PASS" : "FAIL"} - ${name}${detail ? " :: " + detail : ""}`);
}

async function screenshot(page, name) {
  const file = path.join(screenshotsDir, `${name}.png`);
  await page.screenshot({ path: file, fullPage: true });
  report.screenshots.push(file);
  console.log(`SCREENSHOT - ${file}`);
}

async function exists(page, selector, name) {
  const count = await page.locator(selector).count();
  addCheck(name, count > 0, `${selector} count=${count}`);
  return count > 0;
}

async function clickNav(page, label, shotName) {
  const btn = page.locator(".nav-item", { hasText: label });
  await btn.click();
  await page.waitForTimeout(600);
  await screenshot(page, shotName);
  addCheck(`Navigation: ${label}`, true);
}

const browser = await chromium.launch({
  headless: false,
  args: ["--start-maximized"]
});

const context = await browser.newContext({
  viewport: { width: 1600, height: 1000 },
  deviceScaleFactor: 1
});

const page = await context.newPage();

page.on("console", msg => {
  const type = msg.type();
  if (["error", "warning"].includes(type)) {
    report.errors.push({ type, text: msg.text() });
  }
});

page.on("pageerror", err => {
  report.errors.push({ type: "pageerror", text: err.message });
});

try {
  await page.goto(URL, { waitUntil: "networkidle", timeout: 15000 });

  await exists(page, "text=Doctrinarium Control Panel", "Header visible");
  await exists(page, "text=Real task execution", "Real task metric visible");
  await exists(page, "text=Bootstrap / review", "Bootstrap metric visible");
  await exists(page, "text=Laws not enforced", "Laws metric visible");
  await exists(page, "text=Organ blockers", "Organ blockers metric visible");
  await exists(page, "canvas#bgCanvas", "Animated background canvas exists");
  await exists(page, "canvas#sparkCanvas", "Sparkline canvas exists");

  await screenshot(page, "01_dashboard_initial");

  const api = await page.request.get(`${URL}/api/data`);
  addCheck("API /api/data status", api.ok(), `status=${api.status()}`);

  if (api.ok()) {
    const data = await api.json();
    addCheck("API has status JSON", !!data.status);
    addCheck("API has organ gaps JSON", !!data.gaps);
    addCheck("API has utility JSON", !!data.utility);
    addCheck("API has laws JSON", !!data.laws);

    if (data.gaps) {
      addCheck("Organs checked >= 1", Number(data.gaps.total_organs_checked || 0) >= 1, `value=${data.gaps.total_organs_checked}`);
      addCheck("Blockers visible", Number(data.gaps.total_blockers_found || 0) >= 1, `value=${data.gaps.total_blockers_found}`);
    }
  }

  await clickNav(page, "Organ Health", "02_organ_health");
  await clickNav(page, "Major Gaps", "03_major_gaps");
  await clickNav(page, "Utility Matrix", "04_utility_matrix");
  await clickNav(page, "Laws & Codex", "05_laws_codex");
  await clickNav(page, "Paths", "06_paths");
  await clickNav(page, "Dashboard", "07_dashboard_return");

  const reload = page.locator("#btnReload");
  await reload.click();
  await page.waitForTimeout(800);
  await screenshot(page, "08_after_reload_data");
  addCheck("Reload Data clicked", true);

  // Visual sanity: ensure critical values are rendered somewhere.
  const bodyText = await page.locator("body").innerText();
  addCheck("BLOCKED rendered", bodyText.includes("BLOCKED"));
  addCheck("OWNER REVIEW rendered", bodyText.includes("OWNER REVIEW"));
  addCheck("62 or blockers text rendered", bodyText.includes("62") || bodyText.toLowerCase().includes("blocker"));

} catch (err) {
  report.errors.push({ type: "fatal", text: err.stack || String(err) });
  addCheck("Fatal error", false, err.message || String(err));
}

report.finished_at = new Date().toISOString();
report.pass = report.checks.every(c => c.ok) && report.errors.filter(e => e.type === "pageerror").length === 0;

fs.writeFileSync(
  path.join(outDir, "PLAYWRIGHT_VISUAL_AUDIT_REPORT.json"),
  JSON.stringify(report, null, 2),
  "utf8"
);

const md = [
  "# Doctrinarium Playwright Visual Audit",
  "",
  `- URL: ${report.url}`,
  `- Started: ${report.started_at}`,
  `- Finished: ${report.finished_at}`,
  `- Verdict: ${report.pass ? "PASS" : "REVIEW_REQUIRED"}`,
  "",
  "## Checks",
  ...report.checks.map(c => `- ${c.ok ? "PASS" : "FAIL"} — ${c.name}${c.detail ? " — " + c.detail : ""}`),
  "",
  "## Screenshots",
  ...report.screenshots.map(s => `- ${s}`),
  "",
  "## Browser Errors / Warnings",
  ...(report.errors.length ? report.errors.map(e => `- ${e.type}: ${e.text}`) : ["- none"])
].join("\n");

fs.writeFileSync(path.join(outDir, "PLAYWRIGHT_VISUAL_AUDIT_REPORT.md"), md, "utf8");

console.log("");
console.log(`FINAL VERDICT: ${report.pass ? "PASS" : "REVIEW_REQUIRED"}`);
console.log(`REPORT JSON: ${path.join(outDir, "PLAYWRIGHT_VISUAL_AUDIT_REPORT.json")}`);
console.log(`REPORT MD: ${path.join(outDir, "PLAYWRIGHT_VISUAL_AUDIT_REPORT.md")}`);

await page.waitForTimeout(1500);
await browser.close();
