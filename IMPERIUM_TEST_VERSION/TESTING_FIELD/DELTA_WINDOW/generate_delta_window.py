#!/usr/bin/env python3
"""Generate Delta Window HTML with strategic capability foundation context."""

from __future__ import annotations

import argparse
import json
import html
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            return json.load(handle)
    except Exception:
        return None


def render_list(items: list[str], empty_text: str = "None") -> str:
    if not items:
        return f"<li>{html.escape(empty_text)}</li>"
    return "".join(f"<li>{html.escape(item)}</li>" for item in items)


def css() -> str:
    return """
    :root {
      --bg: #0d1117;
      --panel: #161b22;
      --line: #30363d;
      --text: #e6edf3;
      --muted: #9fb0c1;
      --pass: #2ea043;
      --warn: #d29922;
      --fail: #f85149;
      --manual: #ff9e64;
      --note: #58a6ff;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Segoe UI", Tahoma, sans-serif;
      background:
        radial-gradient(circle at 5% 10%, rgba(88,166,255,.18), transparent 40%),
        radial-gradient(circle at 95% 90%, rgba(210,153,34,.15), transparent 42%),
        var(--bg);
      color: var(--text);
      padding: 18px;
    }
    .wrap { max-width: 1280px; margin: 0 auto; display: grid; gap: 14px; }
    .panel {
      border: 1px solid var(--line);
      background: linear-gradient(160deg, rgba(22,27,34,.96), rgba(13,17,23,.94));
      border-radius: 12px;
      padding: 16px;
    }
    h1, h2 { margin: 0 0 10px 0; }
    h1 { color: var(--note); }
    h2 { color: #c9d1d9; font-size: 1.05rem; }
    p { margin: 0 0 8px 0; color: var(--muted); }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 12px; }
    .badge { display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: .8rem; font-weight: 600; border: 1px solid var(--line); }
    .PASS { color: var(--pass); background: rgba(46,160,67,.15); }
    .COMMIT_OK { color: var(--pass); background: rgba(46,160,67,.15); }
    .PARTIAL, .REPAIR_REQUIRED { color: var(--warn); background: rgba(210,153,34,.14); }
    .NOT_IMPLEMENTED, .MANUAL_CONFIRMATION_REQUIRED { color: var(--manual); background: rgba(255,158,100,.14); }
    .FAIL, .BLOCKED, .BLOCKED_SCOPE_VIOLATION, .BLOCKED_TECHNICAL_FAILURE { color: var(--fail); background: rgba(248,81,73,.15); }
    .meta { font-family: Consolas, monospace; font-size: .86rem; color: var(--muted); }
    ul { margin: 8px 0 0 18px; }
    li { margin: 4px 0; }
    .truth {
      border-left: 4px solid var(--manual);
      padding-left: 10px;
      color: #ffcfb3;
      font-size: .92rem;
    }
    .kv { display: grid; grid-template-columns: 170px 1fr; gap: 6px; font-size: .9rem; margin: 6px 0; }
    .k { color: var(--muted); }
    .v { color: var(--text); }
    """


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Delta Window HTML")
    parser.add_argument("--report", help="Path to latest_delta_report.json")
    parser.add_argument("--output", help="Output HTML path")
    parser.add_argument("--test-version", default=".", help="IMPERIUM_TEST_VERSION root")
    args = parser.parse_args()

    tv_root = Path(args.test_version).resolve()
    report_path = Path(args.report).resolve() if args.report else tv_root / "TESTING_FIELD" / "DELTA_WINDOW" / "REPORTS" / "latest_delta_report.json"
    output_path = Path(args.output).resolve() if args.output else tv_root / "TESTING_FIELD" / "DELTA_WINDOW" / "delta_window.html"

    delta = read_json(report_path) or {}
    strategic_report_path = tv_root / "RUNS" / "KIRO_REPAIR_R2_1_STRATEGIC_CAPABILITY_FOUNDATION_20260516" / "STRATEGIC_CAPABILITY_CHECK_REPORT.json"
    strategic = read_json(strategic_report_path) or {}

    verdict = str(delta.get("precommit_verdict", {}).get("verdict", "UNKNOWN"))
    reasons = delta.get("precommit_verdict", {}).get("reasons", []) or ["No reasons available"]

    required_exchange = [
        "AGENT_EXCHANGE/agent_exchange_window.html",
        "RUNS/KIRO_DELTA_R2_AGENT_EXCHANGE_WINDOW_R1_20260516/OWNER_USAGE_GUIDE_RU.md",
        "AGENT_EXCHANGE/OUTBOX/KIRO/KIRO_RESPONSE_BUNDLE_DELTA_R2_AGENT_EXCHANGE_R1_20260516.md",
        "AUDITS/KIRO_SELF_AUDIT_DELTA_R2_AGENT_EXCHANGE_R1_20260516",
    ]
    exchange_missing = [rel for rel in required_exchange if not (tv_root / rel).exists()]

    strategic_verdict = str(strategic.get("final_verdict", "NOT_IMPLEMENTED"))
    scope_safe = strategic.get("scope_safe_to_commit")
    quality_green = strategic.get("quality_green")
    owner_ready = strategic.get("owner_ready_for_manual_review")

    missing_outputs = []
    if strategic:
        for rel in strategic.get("required_outputs", []):
            if not (tv_root / rel).exists():
                missing_outputs.append(rel)
    else:
        missing_outputs.append("RUNS/KIRO_REPAIR_R2_1_STRATEGIC_CAPABILITY_FOUNDATION_20260516/STRATEGIC_CAPABILITY_CHECK_REPORT.json")

    manual_items = [
        "Local LLM remains unverified until local_llm_health_check.py returns PASS with real configured command.",
        "Ubuntu laptop contour remains unverified until ssh_capability_check.ps1 real non-dry probe returns PASS.",
        "Freelance corridor remains foundation/sample until executable path is proven.",
        "Second Brain remains synthetic until real memory integration is explicitly confirmed.",
    ]

    html_text = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
<meta charset=\"UTF-8\" />
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
<title>IMPERIUM TEST VERSION DELTA WINDOW</title>
<style>{css()}</style>
</head>
<body>
<main class=\"wrap\">
  <section class=\"panel\">
    <h1>IMPERIUM TEST VERSION DELTA WINDOW</h1>
    <p class=\"meta\">Generated: {utc_now()} | Source report: {html.escape(str(report_path))}</p>
    <p class=\"truth\">scope_safe_to_commit is not quality_green. Manual verification is mandatory for local LLM and Ubuntu contour claims.</p>
    <div class=\"kv\"><div class=\"k\">Delta verdict</div><div class=\"v\"><span class=\"badge {html.escape(verdict)}\">{html.escape(verdict)}</span></div></div>
    <div class=\"kv\"><div class=\"k\">Strategic checker verdict</div><div class=\"v\"><span class=\"badge {html.escape(strategic_verdict)}\">{html.escape(strategic_verdict)}</span></div></div>
    <div class=\"kv\"><div class=\"k\">scope_safe_to_commit</div><div class=\"v\">{html.escape(str(scope_safe))}</div></div>
    <div class=\"kv\"><div class=\"k\">quality_green</div><div class=\"v\">{html.escape(str(quality_green))}</div></div>
    <div class=\"kv\"><div class=\"k\">owner_ready_for_manual_review</div><div class=\"v\">{html.escape(str(owner_ready))}</div></div>
  </section>

  <section class=\"grid\">
    <article class=\"panel\">
      <h2>Precommit Reasons</h2>
      <ul>{render_list([str(r) for r in reasons])}</ul>
    </article>

    <article class=\"panel\">
      <h2>Agent Exchange Status</h2>
      <div class=\"kv\"><div class=\"k\">Status</div><div class=\"v\"><span class=\"badge {'PASS' if not exchange_missing else 'REPAIR_REQUIRED'}\">{'PASS' if not exchange_missing else 'REPAIR_REQUIRED'}</span></div></div>
      <div class=\"kv\"><div class=\"k\">Missing outputs</div><div class=\"v\">{len(exchange_missing)}</div></div>
      <ul>{render_list(exchange_missing, 'All required Agent Exchange outputs found')}</ul>
    </article>

    <article class=\"panel\">
      <h2>Strategic Capability Foundation</h2>
      <div class=\"kv\"><div class=\"k\">Checker report</div><div class=\"v\">{html.escape(str(strategic_report_path))}</div></div>
      <div class=\"kv\"><div class=\"k\">Missing required outputs</div><div class=\"v\">{len(missing_outputs)}</div></div>
      <ul>{render_list(missing_outputs, 'No missing required outputs reported')}</ul>
    </article>

    <article class=\"panel\">
      <h2>Manual Confirmation Required</h2>
      <ul>{render_list(manual_items)}</ul>
    </article>
  </section>
</main>
</body>
</html>
"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_text, encoding="utf-8")
    print(f"Delta Window HTML generated: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
