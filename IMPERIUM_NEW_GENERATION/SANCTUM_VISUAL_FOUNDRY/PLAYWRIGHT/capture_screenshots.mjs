import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { chromium } from "playwright";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const labPath = path.resolve(__dirname, "../LAB/index.html");
const screenshotsDir = path.resolve(__dirname, "../SCREENSHOTS");
const out = (name) => path.join(screenshotsDir, name);

async function ensureDir() {
  await fs.mkdir(screenshotsDir, { recursive: true });
}

async function capture() {
  await ensureDir();
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const labUrl = pathToFileURL(labPath).href;

  await page.goto(labUrl);
  await page.waitForTimeout(700);

  await page.setViewportSize({ width: 1366, height: 768 });
  await page.waitForTimeout(350);
  await page.screenshot({ path: out("mechanicus_console_full_1366x768.png"), fullPage: true });

  await page.setViewportSize({ width: 1920, height: 1080 });
  await page.waitForTimeout(350);
  await page.screenshot({ path: out("mechanicus_console_full_1920x1080.png"), fullPage: true });

  await page.setViewportSize({ width: 1366, height: 768 });
  await page.waitForTimeout(250);

  await page.locator(".truth-strip").screenshot({ path: out("mechanicus_console_top_strip_detail.png") });
  await page.locator(".work-zone").screenshot({ path: out("mechanicus_console_work_zone_detail.png") });
  await page.locator(".command-rail").screenshot({ path: out("mechanicus_console_command_zone_detail.png") });

  await page.click("#rawToggle");
  await page.waitForTimeout(250);
  await page.locator(".command-rail").screenshot({ path: out("mechanicus_console_raw_secondary_mode.png") });

  const indexPath = path.join(screenshotsDir, "screenshot_index.json");
  const index = {
    generated_at_utc: new Date().toISOString(),
    viewport_targets: ["1366x768", "1920x1080"],
    files: [
      "mechanicus_console_full_1366x768.png",
      "mechanicus_console_full_1920x1080.png",
      "mechanicus_console_top_strip_detail.png",
      "mechanicus_console_work_zone_detail.png",
      "mechanicus_console_command_zone_detail.png",
      "mechanicus_console_raw_secondary_mode.png"
    ]
  };
  await fs.writeFile(indexPath, `${JSON.stringify(index, null, 2)}\n`, "utf8");

  await browser.close();
}

capture().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

