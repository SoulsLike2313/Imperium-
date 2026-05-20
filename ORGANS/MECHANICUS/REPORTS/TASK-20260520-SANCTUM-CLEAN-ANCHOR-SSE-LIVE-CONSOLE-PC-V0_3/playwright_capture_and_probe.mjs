import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";

function parseArgs(argv) {
  const args = {
    baseUrl: "http://127.0.0.1:18765",
    outRoot: process.cwd(),
  };
  for (let i = 2; i < argv.length; i += 1) {
    const token = argv[i];
    if (token === "--base-url" && argv[i + 1]) {
      args.baseUrl = argv[i + 1];
      i += 1;
      continue;
    }
    if (token === "--out-root" && argv[i + 1]) {
      args.outRoot = path.resolve(argv[i + 1]);
      i += 1;
      continue;
    }
  }
  return args;
}

function nowIso() {
  return new Date().toISOString();
}

async function measureFps(page, durationMs = 2000) {
  return page.evaluate(
    (ms) =>
      new Promise((resolve) => {
        const deltas = [];
        let frames = 0;
        let prev = performance.now();
        const stopAt = prev + ms;

        function tick(now) {
          frames += 1;
          deltas.push(now - prev);
          prev = now;
          if (now >= stopAt) {
            const fpsValues = deltas
              .filter((d) => d > 0)
              .map((d) => 1000 / d)
              .sort((a, b) => a - b);
            const avg = fpsValues.length ? fpsValues.reduce((acc, x) => acc + x, 0) / fpsValues.length : 0;
            const idx = fpsValues.length ? Math.floor(fpsValues.length * 0.01) : 0;
            const onePctLow = fpsValues.length ? fpsValues[Math.min(idx, fpsValues.length - 1)] : 0;
            resolve({
              sample_duration_ms: ms,
              frame_count: frames,
              average_fps: Number(avg.toFixed(2)),
              fps_1pct_low: Number(onePctLow.toFixed(2)),
            });
            return;
          }
          requestAnimationFrame(tick);
        }

        requestAnimationFrame(tick);
      }),
    durationMs
  );
}

async function run() {
  const args = parseArgs(process.argv);
  const outRoot = path.resolve(args.outRoot);
  const screenshotsDir = path.join(outRoot, "SCREENSHOTS");
  fs.mkdirSync(screenshotsDir, { recursive: true });

  const errors = [];
  let failedRequests = 0;

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
  const page = await context.newPage();
  page.setDefaultTimeout(30000);

  page.on("console", (msg) => {
    if (msg.type() === "error") {
      errors.push(msg.text());
    }
  });
  page.on("requestfailed", () => {
    failedRequests += 1;
  });

  await page.goto(args.baseUrl, { waitUntil: "domcontentloaded" });
  await page.waitForSelector("#organGrid");
  await page.waitForTimeout(1800);

  const screenshots = [];
  async function capture(fileName, options = {}) {
    const fullPath = path.join(screenshotsDir, fileName);
    if (options.locator) {
      await page.locator(options.locator).first().screenshot({ path: fullPath, timeout: 15000 });
    } else {
      await page.screenshot({ path: fullPath, fullPage: true, timeout: 15000 });
    }
    screenshots.push({
      file_name: fileName,
      path: fullPath,
      note: options.note || "",
    });
  }

  await capture("01_sanctum_overview_brain_shell.png", { note: "overview tab default" });

  await page.click("#tabLive");
  await page.waitForTimeout(800);
  await capture("02_live_operator_console_redesign.png", { note: "live operator console baseline" });

  const statusButton = page.locator('.command-btn[data-command="status"]');
  if (await statusButton.count()) {
    await statusButton.first().click();
    await page.waitForTimeout(2200);
  }
  await capture("03_live_operator_console_after_status.png", { note: "after status command" });
  await capture("04_sse_connection_visible_state.png", { locator: "#sseStatusPill", note: "sse indicator pill" });
  await capture("05_raw_terminal_technical_view.png", { locator: ".raw-stream-wrap", note: "raw technical mode panel" });

  await page.click("#tabEvidence");
  await page.waitForTimeout(600);
  await capture("06_evidence_tab.png");

  await page.click("#tabReports");
  await page.waitForTimeout(600);
  await capture("07_reports_tab.png");

  await page.click("#tabRaw");
  await page.waitForTimeout(600);
  await capture("08_raw_json_tab.png");

  await page.click("#tabActionHistory");
  await page.waitForTimeout(600);
  await capture("09_action_history_tab.png");

  const fps = await measureFps(page, 2200);
  const pageMetrics = await page.evaluate(() => {
    const nav = performance.getEntriesByType("navigation")[0];
    const nodes = document.querySelectorAll("*").length;
    const svgElements = document.querySelectorAll("svg *").length;
    return {
      load_to_domcontentloaded_ms: nav ? Math.round(nav.domContentLoadedEventEnd - nav.startTime) : null,
      load_to_load_event_ms: nav ? Math.round(nav.loadEventEnd - nav.startTime) : null,
      dom_nodes: nodes,
      svg_elements: svgElements,
      renderer: "DOM_CSS",
    };
  });

  const sseStatusText = await page.locator("#sseStatusPill").innerText();

  await context.close();
  await browser.close();

  const result = {
    schema_version: "SANCTUM_SSE_LIVE_CONSOLE_PLAYWRIGHT_CAPTURE_V0_1",
    generated_at_utc: nowIso(),
    base_url: args.baseUrl,
    sse_status_text: sseStatusText.trim(),
    screenshots,
    performance_probe: {
      ...pageMetrics,
      ...fps,
      long_task_count: "UNPROVEN",
      console_errors: errors.length,
      failed_requests: failedRequests,
      console_error_samples: errors.slice(0, 8),
    },
  };

  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

run().catch((error) => {
  const payload = {
    schema_version: "SANCTUM_SSE_LIVE_CONSOLE_PLAYWRIGHT_CAPTURE_V0_1",
    generated_at_utc: nowIso(),
    status: "ERROR",
    error: String(error),
  };
  process.stdout.write(`${JSON.stringify(payload, null, 2)}\n`);
  process.exitCode = 1;
});
