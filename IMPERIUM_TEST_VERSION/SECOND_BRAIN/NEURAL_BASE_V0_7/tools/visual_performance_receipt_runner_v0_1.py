#!/usr/bin/env python3
"""Second Brain V0.7 visual performance receipt runner (measurement instrument)."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TASK_ID = "TASK-SECOND-BRAIN-V07-VISUAL-PERFORMANCE-RECEIPT-RUNNER"
V07_ROOT = Path("IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7")
V06_ROOT = Path("IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6")
BUDGET_PATH = V07_ROOT / "VISUAL_SYSTEM" / "PERFORMANCE_BUDGET_V0_1.json"
DEFAULT_JSON_OUT = V07_ROOT / "reports" / "VISUAL_PERFORMANCE_RECEIPT_V0_1.json"
DEFAULT_MD_OUT = V07_ROOT / "reports" / "VISUAL_PERFORMANCE_RECEIPT_V0_1.md"

HTML_EXT = {".html", ".htm"}
CSS_EXT = {".css"}
JS_EXT = {".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx"}
VISUAL_ASSET_EXT = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".svg",
    ".bmp",
    ".ico",
    ".avif",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_text_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:  # noqa: BLE001
        return ""


def ensure_in_reports(path: Path) -> None:
    reports_root = (V07_ROOT / "reports").resolve()
    resolved = path.resolve()
    if reports_root not in resolved.parents and resolved != reports_root:
        raise ValueError(f"Output path must stay under {reports_root}")


def collect_files(root: Path) -> dict[str, list[Path]]:
    data: dict[str, list[Path]] = {
        "html": [],
        "css": [],
        "js": [],
        "assets": [],
    }
    if not root.exists():
        return data
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        ext = p.suffix.lower()
        if ext in HTML_EXT:
            data["html"].append(p)
        if ext in CSS_EXT:
            data["css"].append(p)
        if ext in JS_EXT:
            data["js"].append(p)
        if ext in VISUAL_ASSET_EXT:
            data["assets"].append(p)
    return data


def file_size_index(paths: list[Path], repo_root: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for p in sorted(paths):
        try:
            size = p.stat().st_size
        except OSError:
            size = -1
        out.append({"path": str(p.relative_to(repo_root)).replace("\\", "/"), "size_bytes": size})
    return out


def css_metrics(css_files: list[Path]) -> dict[str, int]:
    joined = "\n".join(read_text_safe(p) for p in css_files)
    lowered = joined.lower()
    return {
        "css_files_count": len(css_files),
        "keyframes_count": len(re.findall(r"@keyframes\b", lowered)),
        "animation_property_count": len(re.findall(r"\banimation\s*:", lowered)),
        "filter_property_count": len(re.findall(r"\bfilter\s*:", lowered)),
        "drop_shadow_count": len(re.findall(r"drop-shadow\s*\(", lowered)),
        "box_shadow_count": len(re.findall(r"\bbox-shadow\s*:", lowered)),
        "radial_gradient_count": len(re.findall(r"radial-gradient\s*\(", lowered)),
        "linear_gradient_count": len(re.findall(r"linear-gradient\s*\(", lowered)),
    }


def html_metrics(html_files: list[Path]) -> dict[str, Any]:
    tag_counter: dict[str, int] = {}
    total_tags = 0
    svg_related_string_count = 0
    for p in html_files:
        txt = read_text_safe(p)
        tags = re.findall(r"<([a-zA-Z][a-zA-Z0-9:_-]*)\b", txt)
        total_tags += len(tags)
        for t in tags:
            key = t.lower()
            tag_counter[key] = tag_counter.get(key, 0) + 1
        lowered = txt.lower()
        svg_related_string_count += lowered.count("<svg")
        svg_related_string_count += lowered.count("viewbox")
        svg_related_string_count += lowered.count("path d=")
    top_tags = sorted(tag_counter.items(), key=lambda x: x[1], reverse=True)[:25]
    return {
        "html_files_count": len(html_files),
        "approx_total_tag_count": total_tags,
        "top_tags": [{"tag": k, "count": v} for k, v in top_tags],
        "svg_related_string_count_from_html": svg_related_string_count,
    }


def js_svg_metrics(js_files: list[Path]) -> dict[str, int]:
    txt = "\n".join(read_text_safe(p).lower() for p in js_files)
    return {
        "js_files_count": len(js_files),
        "svg_related_string_count_from_js": txt.count("svg") + txt.count("viewbox") + txt.count("path"),
    }


def visual_asset_metrics(asset_files: list[Path]) -> dict[str, Any]:
    total_bytes = 0
    by_ext: dict[str, int] = {}
    for p in asset_files:
        ext = p.suffix.lower() or "<none>"
        by_ext[ext] = by_ext.get(ext, 0) + 1
        try:
            total_bytes += p.stat().st_size
        except OSError:
            continue
    return {
        "visual_asset_count": len(asset_files),
        "visual_asset_total_bytes": total_bytes,
        "visual_asset_total_mb": round(total_bytes / (1024 * 1024), 3),
        "visual_asset_count_by_ext": by_ext,
    }


def optional_browser_audit(run_browser: bool) -> dict[str, Any]:
    if not run_browser:
        return {
            "status": "NOT_MEASURED",
            "audit_type": "OPTIONAL_BROWSER_AUDIT",
            "browser_audit_status": "BROWSER_AUDIT_NOT_RUN",
            "reason": "Run without --browser-audit flag.",
            "fps_measurement_available": False,
        }
    try:
        import playwright  # type: ignore # noqa: F401

        return {
            "status": "NOT_MEASURED",
            "audit_type": "OPTIONAL_BROWSER_AUDIT",
            "browser_audit_status": "BROWSER_AUDIT_NOT_IMPLEMENTED_IN_V0_1",
            "reason": "Playwright detected but browser flow intentionally deferred in this minimal runner.",
            "fps_measurement_available": False,
        }
    except Exception:  # noqa: BLE001
        return {
            "status": "NOT_MEASURED",
            "audit_type": "OPTIONAL_BROWSER_AUDIT",
            "browser_audit_status": "BROWSER_AUDIT_NOT_RUN",
            "reason": "Playwright not available in environment.",
            "fps_measurement_available": False,
        }


def budget_compare(
    budget: dict[str, Any],
    html_tag_count: int,
    svg_string_count: int,
    asset_total_mb: float,
) -> dict[str, Any]:
    checks = []
    dom_target = budget.get("dom_nodes_target")
    dom_blocker = budget.get("dom_nodes_blocker")
    svg_target = budget.get("svg_elements_target")
    svg_blocker = budget.get("svg_elements_blocker")
    asset_target = budget.get("compressed_visual_assets_target_mb")
    asset_blocker = budget.get("compressed_visual_assets_blocker_mb")

    def chk(name: str, value: float, target: Any, blocker: Any) -> dict[str, Any]:
        status = "PASS"
        if isinstance(blocker, (int, float)) and value > blocker:
            status = "BLOCKED"
        elif isinstance(target, (int, float)) and value > target:
            status = "WARN"
        return {
            "metric": name,
            "value": value,
            "target": target,
            "blocker": blocker,
            "status": status,
        }

    checks.append(chk("approx_dom_nodes_from_html_tags", html_tag_count, dom_target, dom_blocker))
    checks.append(chk("svg_related_strings", svg_string_count, svg_target, svg_blocker))
    checks.append(chk("compressed_visual_assets_mb", asset_total_mb, asset_target, asset_blocker))

    worst = "PASS"
    if any(c["status"] == "BLOCKED" for c in checks):
        worst = "BLOCKED"
    elif any(c["status"] == "WARN" for c in checks):
        worst = "WARN"

    return {"checks": checks, "static_budget_status": worst}


def derive_verdict(static_status: str, browser: dict[str, Any]) -> tuple[str, str]:
    if static_status == "BLOCKED":
        return "BLOCKED", "Static budget blockers detected. Do not claim visual-performance PASS."
    if browser.get("fps_measurement_available") is not True:
        if static_status == "WARN":
            return "WARN", "Static audit warns and browser FPS is not measured."
        return "NOT_MEASURED", "Static audit completed but browser FPS was not measured."
    if static_status == "WARN":
        return "WARN", "Browser measured but static warnings remain."
    return "PASS", "Static and browser metrics satisfy current budget checks."


def render_md(report: dict[str, Any]) -> str:
    lines = [
        "# VISUAL PERFORMANCE RECEIPT V0.1",
        "",
        f"- task_id: `{report['task_id']}`",
        f"- generated_at: `{report['generated_at']}`",
        f"- current_head: `{report['current_head']}`",
        f"- verdict: `{report['verdict']}`",
        "",
        "## Inspected Paths",
    ]
    for p in report["inspected_paths"]:
        lines.append(f"- `{p}`")
    lines.extend(
        [
            "",
            "## Static Audit",
            f"- status: `{report['static_audit']['status']}`",
            f"- html_files: `{report['static_audit']['html_file_count']}`",
            f"- css_files: `{report['static_audit']['css_file_count']}`",
            f"- js_files: `{report['static_audit']['js_file_count']}`",
            f"- visual_assets: `{report['static_audit']['visual_asset_count']}`",
            f"- visual_assets_total_mb: `{report['static_audit']['visual_asset_total_mb']}`",
            "",
            "## Optional Browser Audit",
            f"- status: `{report['optional_browser_audit']['status']}`",
            f"- browser_audit_status: `{report['optional_browser_audit']['browser_audit_status']}`",
            f"- reason: {report['optional_browser_audit']['reason']}",
            "",
            "## Budget Comparison",
        ]
    )
    for chk in report["budget_comparison"]["checks"]:
        lines.append(
            f"- {chk['metric']}: value={chk['value']} target={chk['target']} blocker={chk['blocker']} status={chk['status']}"
        )
    lines.extend(
        [
            "",
            "## Limitations",
        ]
    )
    for lim in report["limitations"]:
        lines.append(f"- {lim}")
    lines.extend(
        [
            "",
            f"## Next Recommended Action\n- {report['next_recommended_action']}",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate visual performance receipt for Second Brain V0.7.")
    parser.add_argument("--json-out", default=str(DEFAULT_JSON_OUT))
    parser.add_argument("--md-out", default=str(DEFAULT_MD_OUT))
    parser.add_argument("--browser-audit", action="store_true", help="Try optional browser audit if environment supports it.")
    args = parser.parse_args()

    repo_root = Path.cwd()
    if not (repo_root / ".git").exists():
        raise SystemExit("Run from repository root.")

    budget_path = repo_root / BUDGET_PATH
    if not budget_path.exists():
        raise SystemExit(f"Budget file missing: {budget_path}")

    try:
        budget = json.loads(budget_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f"Invalid budget JSON: {exc}") from exc

    json_out = Path(args.json_out)
    md_out = Path(args.md_out)
    ensure_in_reports(json_out)
    ensure_in_reports(md_out)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.parent.mkdir(parents=True, exist_ok=True)

    v07_files = collect_files(repo_root / V07_ROOT)
    v06_files = collect_files(repo_root / V06_ROOT)

    css_data = css_metrics(v07_files["css"] + v06_files["css"])
    html_data = html_metrics(v07_files["html"] + v06_files["html"])
    js_data = js_svg_metrics(v07_files["js"] + v06_files["js"])
    asset_data = visual_asset_metrics(v07_files["assets"] + v06_files["assets"])

    expected_paths = [
        str((repo_root / V07_ROOT).resolve()),
        str((repo_root / V06_ROOT).resolve()),
        str((repo_root / V07_ROOT / "VISUAL_SYSTEM").resolve()),
    ]
    missing_expected_paths = [p for p in expected_paths if not Path(p).exists()]

    budget_data = budget_compare(
        budget=budget,
        html_tag_count=html_data["approx_total_tag_count"],
        svg_string_count=html_data["svg_related_string_count_from_html"] + js_data["svg_related_string_count_from_js"],
        asset_total_mb=asset_data["visual_asset_total_mb"],
    )
    browser_data = optional_browser_audit(args.browser_audit)
    verdict, next_action_reason = derive_verdict(budget_data["static_budget_status"], browser_data)

    static_audit = {
        "status": "STATIC_AUDIT",
        "target_paths_inspected": [
            str((repo_root / V07_ROOT).resolve()),
            str((repo_root / V06_ROOT).resolve()),
        ],
        "html_file_count": len(v07_files["html"]) + len(v06_files["html"]),
        "css_file_count": len(v07_files["css"]) + len(v06_files["css"]),
        "js_file_count": len(v07_files["js"]) + len(v06_files["js"]),
        "source_file_sizes": {
            "html": file_size_index(v07_files["html"] + v06_files["html"], repo_root),
            "css": file_size_index(v07_files["css"] + v06_files["css"], repo_root),
            "js": file_size_index(v07_files["js"] + v06_files["js"], repo_root),
        },
        "css_metrics": css_data,
        "html_metrics": html_data,
        "js_metrics": js_data,
        "visual_asset_count": asset_data["visual_asset_count"],
        "visual_asset_total_bytes": asset_data["visual_asset_total_bytes"],
        "visual_asset_total_mb": asset_data["visual_asset_total_mb"],
        "visual_asset_count_by_ext": asset_data["visual_asset_count_by_ext"],
        "missing_expected_paths": missing_expected_paths,
    }

    report = {
        "task_id": TASK_ID,
        "generated_at": now_utc(),
        "current_head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "budget_source": str(BUDGET_PATH).replace("\\", "/"),
        "inspected_paths": [
            str(V07_ROOT).replace("\\", "/"),
            str(V06_ROOT).replace("\\", "/"),
        ],
        "static_audit": static_audit,
        "optional_browser_audit": browser_data,
        "budget_comparison": budget_data,
        "console_errors": {"status": "NOT_MEASURED", "value": None},
        "failed_requests": {"status": "NOT_MEASURED", "value": None},
        "limitations": [
            "No runtime mutation performed; static audit only by default.",
            "FPS and load timings cannot be claimed without executable browser probe.",
            "BROWSER_AUDIT_NOT_RUN is honest outcome when probe is unavailable or disabled.",
        ],
        "verdict": verdict,
        "next_recommended_action": (
            "TASK-SECOND-BRAIN-V07-VISUAL-FAKE-GREEN-SCANNER"
            if verdict != "BLOCKED"
            else "TASK-SECOND-BRAIN-V07-PERFORMANCE-BASELINE-INTERPRETATION"
        ),
        "verdict_reason": next_action_reason,
    }

    json_out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_out.write_text(render_md(report), encoding="utf-8")
    print(str(json_out))
    print(str(md_out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
