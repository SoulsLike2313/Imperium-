#!/usr/bin/env python3
"""Second Brain V0.7 performance blocker source mapper (read-only source analysis)."""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

TASK_ID = "TASK-SECOND-BRAIN-V07-PERFORMANCE-BLOCKER-SOURCE-MAP"

V06_APP_DIR = Path("IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app")
V06_HTML = V06_APP_DIR / "neural_map_v0_6.html"
V06_CSS = V06_APP_DIR / "neural_map_v0_6.css"
V06_JS = V06_APP_DIR / "neural_map_v0_6.js"

BASELINE_RECEIPT = Path(
    "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/FULL_RUNTIME_PERFORMANCE_AUDIT_RECEIPT_V0_1.json"
)
BASELINE_INTERPRETATION = Path(
    "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/FULL_RUNTIME_PERFORMANCE_BASELINE_INTERPRETATION_V0_1.json"
)
BASELINE_BLOCKER_MAP = Path(
    "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/FULL_RUNTIME_PERFORMANCE_BUDGET_BLOCKER_MAP_V0_1.json"
)
BASELINE_ACCEPTANCE = Path(
    "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/FULL_RUNTIME_PERFORMANCE_ACCEPTANCE_DECISION_V0_1.json"
)

SOURCE_MAP_JSON = Path(
    "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/PERFORMANCE_BLOCKER_SOURCE_MAP_V0_1.json"
)
SOURCE_MAP_MD = Path(
    "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/PERFORMANCE_BLOCKER_SOURCE_MAP_V0_1.md"
)
DETAILS_JSON = Path(
    "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/PERFORMANCE_BLOCKER_SOURCE_MAP_DETAILS_V0_1.json"
)
DETAILS_MD = Path(
    "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/PERFORMANCE_BLOCKER_SOURCE_MAP_DETAILS_V0_1.md"
)
DECISION_JSON = Path(
    "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/PERFORMANCE_BLOCKER_SOURCE_MAP_DECISION_V0_1.json"
)
DECISION_MD = Path(
    "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/PERFORMANCE_BLOCKER_SOURCE_MAP_DECISION_V0_1.md"
)

MAX_ASSET_SAMPLE = 50
MAX_HEAVY_SAMPLE = 12

IGNORE_REF_PREFIXES = (
    "http://",
    "https://",
    "//",
    "data:",
    "blob:",
    "javascript:",
    "mailto:",
    "#",
)

ASSET_EXTENSIONS = (
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".svg",
    ".ico",
    ".mp4",
    ".webm",
    ".wav",
    ".mp3",
    ".ogg",
    ".json",
    ".css",
    ".js",
    ".woff",
    ".woff2",
    ".ttf",
)


@dataclass
class AssetEntry:
    reference: str
    resolved_path: Optional[str]
    exists: bool
    size_kb: Optional[float]
    reason: Optional[str]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(read_text(path))


def count_regex(pattern: str, text: str, flags: int = 0) -> int:
    return len(re.findall(pattern, text, flags=flags))


def safe_rel(path: Path) -> str:
    return str(path).replace("\\", "/")


def extract_html_indicators(html: str) -> Dict[str, Any]:
    css_refs = re.findall(r"""<link[^>]+href=["']([^"']+)["']""", html, flags=re.IGNORECASE)
    script_refs = re.findall(r"""<script[^>]+src=["']([^"']+)["']""", html, flags=re.IGNORECASE)
    img_refs = re.findall(r"""<img[^>]+src=["']([^"']+)["']""", html, flags=re.IGNORECASE)
    inline_style_blocks = count_regex(r"<style\b[^>]*>", html, flags=re.IGNORECASE)
    inline_script_blocks = count_regex(r"<script\b(?![^>]*\bsrc=)[^>]*>", html, flags=re.IGNORECASE)
    dom_tag_count = count_regex(r"<[a-zA-Z][^>/\s]*", html)
    svg_markers = count_regex(r"<svg\b|</svg>|url\(#", html, flags=re.IGNORECASE)
    canvas_markers = count_regex(r"<canvas\b", html, flags=re.IGNORECASE)
    background_markers = count_regex(r"background(?:-image)?\s*:", html, flags=re.IGNORECASE)
    return {
        "linked_css_refs_count": len(css_refs),
        "linked_js_refs_count": len(script_refs),
        "image_refs_count": len(img_refs),
        "inline_style_blocks_count": inline_style_blocks,
        "inline_script_blocks_count": inline_script_blocks,
        "dom_tag_count": dom_tag_count,
        "svg_marker_count": svg_markers,
        "canvas_marker_count": canvas_markers,
        "background_style_markers_count": background_markers,
        "linked_css_refs": sorted(set(css_refs)),
        "linked_js_refs": sorted(set(script_refs)),
        "image_refs": sorted(set(img_refs)),
    }


def extract_css_indicators(css: str) -> Dict[str, Any]:
    z_values = [int(x) for x in re.findall(r"z-index\s*:\s*(-?\d+)", css, flags=re.IGNORECASE)]
    selector_heads = re.findall(r"(^|})\s*([^{]+)\{", css, flags=re.MULTILINE)
    selectors: List[str] = []
    for _, raw in selector_heads:
        cleaned = " ".join(raw.strip().split())
        if cleaned:
            selectors.append(cleaned)
    complex_selector_count = 0
    for s in selectors:
        if any(token in s for token in (":", ">", "+", "~", "*", "[", "nth-")):
            complex_selector_count += 1
    duplicate_complex = Counter([s for s in selectors if any(t in s for t in (":", ">", "+", "~", "*", "[", "nth-"))])
    repeated_expensive_selector_count = sum(1 for _, c in duplicate_complex.items() if c > 1)
    return {
        "keyframes_count": count_regex(r"@keyframes\b", css, flags=re.IGNORECASE),
        "animation_declarations_count": count_regex(r"\banimation(?:-[a-z-]+)?\s*:", css, flags=re.IGNORECASE),
        "transition_declarations_count": count_regex(r"\btransition(?:-[a-z-]+)?\s*:", css, flags=re.IGNORECASE),
        "filter_declarations_count": count_regex(r"\bfilter\s*:", css, flags=re.IGNORECASE),
        "backdrop_filter_declarations_count": count_regex(r"\bbackdrop-filter\s*:", css, flags=re.IGNORECASE),
        "box_shadow_declarations_count": count_regex(r"\bbox-shadow\s*:", css, flags=re.IGNORECASE),
        "text_shadow_declarations_count": count_regex(r"\btext-shadow\s*:", css, flags=re.IGNORECASE),
        "blur_usage_count": count_regex(r"blur\s*\(", css, flags=re.IGNORECASE),
        "transform_declarations_count": count_regex(r"\btransform(?:-[a-z-]+)?\s*:", css, flags=re.IGNORECASE),
        "will_change_declarations_count": count_regex(r"\bwill-change\s*:", css, flags=re.IGNORECASE),
        "position_fixed_count": count_regex(r"\bposition\s*:\s*fixed\b", css, flags=re.IGNORECASE),
        "position_sticky_count": count_regex(r"\bposition\s*:\s*sticky\b", css, flags=re.IGNORECASE),
        "large_z_index_count": sum(1 for z in z_values if abs(z) >= 100),
        "gradient_count": count_regex(r"\b(?:linear|radial|conic)-gradient\s*\(", css, flags=re.IGNORECASE),
        "radial_gradient_count": count_regex(r"\bradial-gradient\s*\(", css, flags=re.IGNORECASE),
        "conic_gradient_count": count_regex(r"\bconic-gradient\s*\(", css, flags=re.IGNORECASE),
        "complex_selector_count": complex_selector_count,
        "repeated_expensive_selector_count": repeated_expensive_selector_count,
        "reduced_motion_media_support_count": count_regex(
            r"@media[^{]*prefers-reduced-motion", css, flags=re.IGNORECASE
        ),
    }


def extract_js_indicators(js: str) -> Dict[str, Any]:
    return {
        "request_animation_frame_count": count_regex(r"\brequestAnimationFrame\s*\(", js),
        "set_interval_count": count_regex(r"\bsetInterval\s*\(", js),
        "set_timeout_count": count_regex(r"\bsetTimeout\s*\(", js),
        "event_listener_count": count_regex(r"\baddEventListener\s*\(", js),
        "query_selector_all_count": count_regex(r"\bquerySelectorAll\s*\(", js),
        "inner_html_write_count": count_regex(r"\.innerHTML\s*=", js),
        "dom_create_element_count": count_regex(r"\bcreateElement(?:NS)?\s*\(", js),
        "dom_append_count": count_regex(r"\.(?:appendChild|append|prepend|insertBefore)\s*\(", js),
        "style_write_count": count_regex(r"\.style\.[A-Za-z_][A-Za-z0-9_]*\s*=|\.style\.setProperty\s*\(", js),
        "classlist_mutation_count": count_regex(r"\.classList\.(?:add|remove|toggle|replace)\s*\(", js),
        "layout_read_count": count_regex(
            r"\bgetBoundingClientRect\s*\(|\boffsetWidth\b|\boffsetHeight\b|\bscrollWidth\b|\bscrollHeight\b|\bclientWidth\b|\bclientHeight\b",
            js,
        ),
        "storage_access_count": count_regex(r"\blocalStorage\b|\bsessionStorage\b", js),
        "fetch_call_count": count_regex(r"\bfetch\s*\(", js),
        "api_path_marker_count": count_regex(r"['\"]/api/", js),
        "svg_canvas_manipulation_count": count_regex(
            r"\bcreateElementNS\s*\(|\bgetContext\s*\(|\bbeginPath\s*\(|\bstroke\s*\(|\bfill\s*\(",
            js,
        ),
        "large_literal_arrays_count": count_regex(r"\[[^\]]{300,}\]", js, flags=re.DOTALL),
        "large_literal_objects_count": count_regex(r"\{[^{}]{500,}\}", js, flags=re.DOTALL),
        "functions_count": count_regex(r"\bfunction\b|=>", js),
    }


def normalize_asset_ref(ref: str) -> Optional[str]:
    cleaned = ref.strip().strip('"').strip("'")
    if not cleaned:
        return None
    lowered = cleaned.lower()
    if lowered.startswith(IGNORE_REF_PREFIXES):
        return None
    return cleaned


def extract_asset_refs(html: str, css: str, js: str) -> List[str]:
    refs: List[str] = []
    refs.extend(re.findall(r"""<link[^>]+href=["']([^"']+)["']""", html, flags=re.IGNORECASE))
    refs.extend(re.findall(r"""<script[^>]+src=["']([^"']+)["']""", html, flags=re.IGNORECASE))
    refs.extend(re.findall(r"""<img[^>]+src=["']([^"']+)["']""", html, flags=re.IGNORECASE))
    refs.extend(re.findall(r"url\(([^)]+)\)", css, flags=re.IGNORECASE))
    js_strings = re.findall(r"""['"]([^'"]+)['"]""", js)
    for val in js_strings:
        low = val.lower()
        if any(ext in low for ext in ASSET_EXTENSIONS) or low.startswith("/api/"):
            refs.append(val)

    normalized: List[str] = []
    for ref in refs:
        n = normalize_asset_ref(ref)
        if n is not None:
            normalized.append(n)
    return sorted(set(normalized))


def resolve_asset_ref(reference: str, app_dir: Path, repo_root: Path) -> AssetEntry:
    ref = reference.split("?", 1)[0].split("#", 1)[0]
    if ref.lower().startswith("/api/"):
        return AssetEntry(reference=reference, resolved_path=None, exists=False, size_kb=None, reason="API_PATH")

    candidate = app_dir / ref.lstrip("/") if ref.startswith("/") else app_dir / ref
    try:
        resolved = candidate.resolve()
    except Exception:
        return AssetEntry(reference=reference, resolved_path=None, exists=False, size_kb=None, reason="RESOLVE_FAILED")

    try:
        resolved.relative_to(repo_root.resolve())
    except Exception:
        return AssetEntry(
            reference=reference,
            resolved_path=str(resolved).replace("\\", "/"),
            exists=False,
            size_kb=None,
            reason="OUTSIDE_REPO",
        )

    if not resolved.exists() or not resolved.is_file():
        return AssetEntry(
            reference=reference,
            resolved_path=str(resolved).replace("\\", "/"),
            exists=False,
            size_kb=None,
            reason="MISSING_LOCAL_FILE",
        )
    size_kb = round(resolved.stat().st_size / 1024, 2)
    return AssetEntry(
        reference=reference,
        resolved_path=str(resolved).replace("\\", "/"),
        exists=True,
        size_kb=size_kb,
        reason=None,
    )


def likelihood_from_score(score: float, strong: float, moderate: float, weak: float) -> str:
    if score >= strong:
        return "EVIDENCE_STRONG"
    if score >= moderate:
        return "EVIDENCE_MODERATE"
    if score >= weak:
        return "EVIDENCE_WEAK"
    return "UNKNOWN_REQUIRES_MEASUREMENT"


def make_likely_categories(
    css_i: Dict[str, Any],
    js_i: Dict[str, Any],
    html_i: Dict[str, Any],
    assets: List[AssetEntry],
    baseline: Dict[str, Any],
) -> List[Dict[str, Any]]:
    existing_sizes = [a.size_kb for a in assets if a.exists and isinstance(a.size_kb, (int, float))]
    total_asset_kb = float(sum(existing_sizes)) if existing_sizes else 0.0
    max_asset_kb = float(max(existing_sizes)) if existing_sizes else 0.0
    missing_assets = sum(1 for a in assets if not a.exists and a.reason == "MISSING_LOCAL_FILE")

    score_a = (
        css_i["animation_declarations_count"]
        + css_i["keyframes_count"]
        + css_i["filter_declarations_count"] * 2
        + css_i["backdrop_filter_declarations_count"] * 3
        + css_i["box_shadow_declarations_count"]
        + css_i["text_shadow_declarations_count"]
        + css_i["gradient_count"]
    )
    score_b = html_i["dom_tag_count"] + html_i["svg_marker_count"] + js_i["query_selector_all_count"] * 3
    score_c = (
        js_i["request_animation_frame_count"] * 12
        + js_i["set_interval_count"] * 8
        + js_i["set_timeout_count"] * 2
        + css_i["animation_declarations_count"]
    )
    score_d = total_asset_kb + max_asset_kb * 2 + missing_assets * 50
    score_e = js_i["layout_read_count"] * 5 + js_i["style_write_count"] * 4 + js_i["dom_append_count"] * 3
    score_f = js_i["layout_read_count"] * 4 + js_i["classlist_mutation_count"] * 2 + css_i["position_fixed_count"] * 2

    fps_blocked = False
    for m in baseline.get("budget_comparison", {}).get("metrics", []):
        if m.get("metric") in {"average_fps", "fps_1pct_low"} and m.get("status") == "BLOCKED":
            fps_blocked = True
            break

    categories = [
        {
            "category_id": "A",
            "name": "heavy_visual_effects",
            "likelihood": likelihood_from_score(float(score_a), strong=120.0, moderate=75.0, weak=35.0),
            "score": round(float(score_a), 2),
            "evidence": "CSS animation/filter/shadow/gradient indicator density.",
        },
        {
            "category_id": "B",
            "name": "excessive_dom_svg",
            "likelihood": likelihood_from_score(float(score_b), strong=1600.0, moderate=900.0, weak=300.0),
            "score": round(float(score_b), 2),
            "evidence": "DOM/SVG structural markers plus querySelectorAll usage.",
        },
        {
            "category_id": "C",
            "name": "animation_frame_pressure",
            "likelihood": likelihood_from_score(float(score_c), strong=120.0, moderate=70.0, weak=25.0),
            "score": round(float(score_c), 2),
            "evidence": "rAF/timers combined with animation declarations under blocked FPS baseline.",
        },
        {
            "category_id": "D",
            "name": "asset_weight_pressure",
            "likelihood": likelihood_from_score(float(score_d), strong=6000.0, moderate=2500.0, weak=800.0),
            "score": round(float(score_d), 2),
            "evidence": "Resolvable local referenced asset size signals and missing references.",
        },
        {
            "category_id": "E",
            "name": "js_main_thread_work",
            "likelihood": likelihood_from_score(float(score_e), strong=220.0, moderate=120.0, weak=45.0),
            "score": round(float(score_e), 2),
            "evidence": "Layout reads + style writes + DOM mutations heuristics from JS source.",
        },
        {
            "category_id": "F",
            "name": "layout_reflow_pressure",
            "likelihood": likelihood_from_score(float(score_f), strong=180.0, moderate=95.0, weak=35.0),
            "score": round(float(score_f), 2),
            "evidence": "Reflow-related source markers (layout reads/classList/fixed-layer hints).",
        },
        {
            "category_id": "G",
            "name": "measurement_environment_limitation",
            "likelihood": "EVIDENCE_WEAK" if fps_blocked else "UNKNOWN_REQUIRES_MEASUREMENT",
            "score": 0.0,
            "evidence": "Environment can influence absolute FPS but does not invalidate baseline truth.",
        },
    ]
    return categories


def sort_categories(categories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rank = {
        "EVIDENCE_STRONG": 0,
        "EVIDENCE_MODERATE": 1,
        "EVIDENCE_WEAK": 2,
        "UNKNOWN_REQUIRES_MEASUREMENT": 3,
    }
    return sorted(categories, key=lambda x: (rank.get(str(x.get("likelihood")), 9), -float(x.get("score", 0.0))))


def to_md_list(title: str, items: Iterable[str]) -> List[str]:
    out = [title]
    for item in items:
        out.append(f"- {item}")
    return out


def main() -> int:
    repo_root = Path.cwd()
    required_paths = [
        V06_HTML,
        V06_CSS,
        V06_JS,
        BASELINE_RECEIPT,
        BASELINE_INTERPRETATION,
        BASELINE_BLOCKER_MAP,
        BASELINE_ACCEPTANCE,
    ]
    for path in required_paths:
        if not path.exists():
            raise RuntimeError(f"Missing required input: {path}")

    html_text = read_text(V06_HTML)
    css_text = read_text(V06_CSS)
    js_text = read_text(V06_JS)

    baseline_receipt = load_json(BASELINE_RECEIPT)
    baseline_interpretation = load_json(BASELINE_INTERPRETATION)
    baseline_blocker_map = load_json(BASELINE_BLOCKER_MAP)
    baseline_acceptance = load_json(BASELINE_ACCEPTANCE)

    html_ind = extract_html_indicators(html_text)
    css_ind = extract_css_indicators(css_text)
    js_ind = extract_js_indicators(js_text)

    asset_refs = extract_asset_refs(html_text, css_text, js_text)
    asset_entries = [resolve_asset_ref(ref, V06_APP_DIR, repo_root) for ref in asset_refs]
    existing_assets = [a for a in asset_entries if a.exists]
    missing_assets = [a for a in asset_entries if not a.exists]
    heaviest = sorted(existing_assets, key=lambda x: float(x.size_kb or 0.0), reverse=True)[:MAX_HEAVY_SAMPLE]

    truncated_refs = asset_refs[:MAX_ASSET_SAMPLE]
    omitted_asset_refs = max(0, len(asset_refs) - len(truncated_refs))

    categories = sort_categories(
        make_likely_categories(css_ind, js_ind, html_ind, asset_entries, baseline_receipt)
    )
    strong_or_moderate = [
        c["name"] for c in categories if c.get("likelihood") in {"EVIDENCE_STRONG", "EVIDENCE_MODERATE"}
    ]
    if not strong_or_moderate:
        strong_or_moderate = [categories[0]["name"]] if categories else []

    details_payload: Dict[str, Any] = {
        "task_id": TASK_ID,
        "generated_at": utc_now(),
        "current_head": str(baseline_interpretation.get("current_head") or baseline_receipt.get("current_head")),
        "html_indicator_counts": html_ind,
        "css_indicator_counts": css_ind,
        "js_indicator_counts": js_ind,
        "referenced_assets_sample": truncated_refs,
        "top_local_referenced_assets_by_size": [
            {"reference": a.reference, "resolved_path": a.resolved_path, "size_kb": a.size_kb} for a in heaviest
        ],
        "missing_referenced_assets_sample": [
            {"reference": a.reference, "resolved_path": a.resolved_path, "reason": a.reason}
            for a in missing_assets[:MAX_HEAVY_SAMPLE]
        ],
        "omitted_count": {
            "referenced_assets_omitted": omitted_asset_refs,
            "missing_assets_omitted": max(0, len(missing_assets) - min(len(missing_assets), MAX_HEAVY_SAMPLE)),
        },
    }

    source_map_payload: Dict[str, Any] = {
        "task_id": TASK_ID,
        "generated_at": utc_now(),
        "current_head": str(baseline_interpretation.get("current_head") or baseline_receipt.get("current_head")),
        "source_files": {
            "html": safe_rel(V06_HTML),
            "css": safe_rel(V06_CSS),
            "js": safe_rel(V06_JS),
        },
        "baseline_metrics_ref": {
            "receipt_path": safe_rel(BASELINE_RECEIPT),
            "interpretation_path": safe_rel(BASELINE_INTERPRETATION),
            "blocker_map_path": safe_rel(BASELINE_BLOCKER_MAP),
            "acceptance_decision_path": safe_rel(BASELINE_ACCEPTANCE),
            "receipt_verdict": baseline_receipt.get("verdict"),
            "fps_average": (baseline_receipt.get("fps_measurement") or {}).get("fps_estimate"),
            "fps_1pct_low": (baseline_receipt.get("fps_measurement") or {}).get("fps_1pct_low"),
            "performance_acceptance": baseline_acceptance.get("performance_acceptance"),
        },
        "css_pressure_summary": {
            "animation_and_effect_indicators": {
                "keyframes_count": css_ind["keyframes_count"],
                "animation_declarations_count": css_ind["animation_declarations_count"],
                "filter_declarations_count": css_ind["filter_declarations_count"],
                "backdrop_filter_declarations_count": css_ind["backdrop_filter_declarations_count"],
                "shadow_declarations_count": css_ind["box_shadow_declarations_count"]
                + css_ind["text_shadow_declarations_count"],
                "gradient_count": css_ind["gradient_count"],
            },
            "layout_layer_indicators": {
                "position_fixed_count": css_ind["position_fixed_count"],
                "position_sticky_count": css_ind["position_sticky_count"],
                "large_z_index_count": css_ind["large_z_index_count"],
                "will_change_declarations_count": css_ind["will_change_declarations_count"],
            },
            "reduced_motion_support_count": css_ind["reduced_motion_media_support_count"],
        },
        "js_pressure_summary": {
            "animation_loop_indicators": {
                "request_animation_frame_count": js_ind["request_animation_frame_count"],
                "set_interval_count": js_ind["set_interval_count"],
                "set_timeout_count": js_ind["set_timeout_count"],
            },
            "dom_mutation_indicators": {
                "dom_create_element_count": js_ind["dom_create_element_count"],
                "dom_append_count": js_ind["dom_append_count"],
                "classlist_mutation_count": js_ind["classlist_mutation_count"],
                "style_write_count": js_ind["style_write_count"],
            },
            "layout_read_indicators": {
                "layout_read_count": js_ind["layout_read_count"],
                "query_selector_all_count": js_ind["query_selector_all_count"],
            },
            "function_and_listener_indicators": {
                "functions_count": js_ind["functions_count"],
                "event_listener_count": js_ind["event_listener_count"],
            },
        },
        "dom_svg_source_summary": {
            "dom_tag_count": html_ind["dom_tag_count"],
            "svg_marker_count": html_ind["svg_marker_count"],
            "canvas_marker_count": html_ind["canvas_marker_count"],
            "linked_css_refs_count": html_ind["linked_css_refs_count"],
            "linked_js_refs_count": html_ind["linked_js_refs_count"],
        },
        "asset_reference_summary": {
            "referenced_assets_count": len(asset_refs),
            "resolvable_local_assets_count": len(existing_assets),
            "missing_or_unresolved_assets_count": len(missing_assets),
            "top_local_referenced_assets_by_size": [
                {"reference": a.reference, "resolved_path": a.resolved_path, "size_kb": a.size_kb} for a in heaviest
            ],
        },
        "likely_blocker_categories": categories,
        "unknowns": [
            "Exact runtime frame-time split between CSS animation, JS update cost, and compositor behavior is not measurable from static source only.",
            "Asset payload runtime decode/render cost requires dedicated asset budget classification and runtime profiling.",
            "Environment variance contribution cannot be isolated without repeated controlled baseline runs.",
        ],
        "recommended_next_measurements": [
            "Task-level asset budget classification with resolved file weights and priority impact.",
            "Frame-phase source map with targeted runtime profiling per animation/update zone.",
            "Controlled repeated FPS baselines across comparable environment conditions.",
        ],
        "recommended_next_task": "TASK-SECOND-BRAIN-V07-ASSET-BUDGET-CLASSIFICATION",
        "limitations": [
            "Read-only static source analysis; no runtime/browser execution.",
            "Heuristic indicators cannot prove an exact root cause alone.",
            "Binary assets are inspected by metadata only when locally resolvable.",
        ],
        "verdict": "PERFORMANCE_BLOCKER_SOURCES_LIKELY_MAPPED_NOT_CONFIRMED_AS_EXACT_ROOT_CAUSE",
    }

    decision_payload: Dict[str, Any] = {
        "task_id": TASK_ID,
        "generated_at": utc_now(),
        "current_head": str(baseline_interpretation.get("current_head") or baseline_receipt.get("current_head")),
        "baseline_valid": True,
        "performance_blocked": True,
        "optimization_admitted_now": False,
        "visual_construction_admitted_now": False,
        "strongest_evidence_categories": strong_or_moderate,
        "next_task_decision": "TASK-SECOND-BRAIN-V07-ASSET-BUDGET-CLASSIFICATION",
        "reason": (
            "Valid baseline remains blocked by FPS metrics; source-map provides likely categories but asset-weight classification "
            "is the next safest narrowing step before any optimization planning."
        ),
    }

    SOURCE_MAP_JSON.parent.mkdir(parents=True, exist_ok=True)
    SOURCE_MAP_JSON.write_text(json.dumps(source_map_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    DETAILS_JSON.write_text(json.dumps(details_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    DECISION_JSON.write_text(json.dumps(decision_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    source_md = [
        "# PERFORMANCE BLOCKER SOURCE MAP V0.1",
        "",
        "## Baseline Truth Summary",
        f"- receipt_verdict: `{source_map_payload['baseline_metrics_ref']['receipt_verdict']}`",
        f"- performance_acceptance: `{source_map_payload['baseline_metrics_ref']['performance_acceptance']}`",
        f"- full_runtime_fps_average: `{source_map_payload['baseline_metrics_ref']['fps_average']}`",
        f"- full_runtime_fps_1pct_low: `{source_map_payload['baseline_metrics_ref']['fps_1pct_low']}`",
        "",
        "## Source Files Inspected",
        f"- {source_map_payload['source_files']['html']}",
        f"- {source_map_payload['source_files']['css']}",
        f"- {source_map_payload['source_files']['js']}",
        "",
        "## Strongest Source Indicators",
        f"- CSS animation declarations: `{css_ind['animation_declarations_count']}`",
        f"- CSS keyframes: `{css_ind['keyframes_count']}`",
        f"- JS requestAnimationFrame: `{js_ind['request_animation_frame_count']}`",
        f"- JS style writes: `{js_ind['style_write_count']}`",
        f"- JS layout reads: `{js_ind['layout_read_count']}`",
        "",
        "## Likely Blocker Categories",
    ]
    for cat in categories:
        source_md.append(
            f"- {cat['category_id']} `{cat['name']}` -> `{cat['likelihood']}` (score={cat['score']}): {cat['evidence']}"
        )
    source_md += [
        "",
        "## Unknowns",
    ]
    for item in source_map_payload["unknowns"]:
        source_md.append(f"- {item}")
    source_md += [
        "",
        "## Why No Optimization Is Done Yet",
        "- This report is a diagnostic source map only.",
        "- Optimization remains blocked until source-map and asset classification are interpreted together.",
        "",
        f"- recommended_next_task: `{source_map_payload['recommended_next_task']}`",
        f"- verdict: `{source_map_payload['verdict']}`",
    ]
    SOURCE_MAP_MD.write_text("\n".join(source_md) + "\n", encoding="utf-8")

    details_md = [
        "# PERFORMANCE BLOCKER SOURCE MAP DETAILS V0.1",
        "",
        "## HTML Indicator Counts",
    ]
    for k, v in html_ind.items():
        if isinstance(v, (int, float)):
            details_md.append(f"- {k}: `{v}`")
    details_md += [
        "",
        "## CSS Indicator Counts",
    ]
    for k, v in css_ind.items():
        details_md.append(f"- {k}: `{v}`")
    details_md += [
        "",
        "## JS Indicator Counts",
    ]
    for k, v in js_ind.items():
        details_md.append(f"- {k}: `{v}`")
    details_md += [
        "",
        "## Referenced Assets Sample",
    ]
    for ref in truncated_refs:
        details_md.append(f"- {ref}")
    details_md += [
        "",
        "## Top Local Referenced Assets By Size",
    ]
    for row in details_payload["top_local_referenced_assets_by_size"]:
        details_md.append(f"- {row['reference']} -> {row['size_kb']} KB")
    details_md += [
        "",
        "## Omitted Count",
        f"- referenced_assets_omitted: `{details_payload['omitted_count']['referenced_assets_omitted']}`",
        f"- missing_assets_omitted: `{details_payload['omitted_count']['missing_assets_omitted']}`",
    ]
    DETAILS_MD.write_text("\n".join(details_md) + "\n", encoding="utf-8")

    decision_md = [
        "# PERFORMANCE BLOCKER SOURCE MAP DECISION V0.1",
        "",
        f"- baseline_valid: `{decision_payload['baseline_valid']}`",
        f"- performance_blocked: `{decision_payload['performance_blocked']}`",
        f"- optimization_admitted_now: `{decision_payload['optimization_admitted_now']}`",
        f"- visual_construction_admitted_now: `{decision_payload['visual_construction_admitted_now']}`",
        f"- strongest_evidence_categories: `{decision_payload['strongest_evidence_categories']}`",
        f"- next_task_decision: `{decision_payload['next_task_decision']}`",
        "",
        "## Decision Statement",
        "- Performance is truthfully blocked by valid FPS evidence.",
        "- Source map is diagnostic, not a fix.",
        "- Optimization remains blocked until source-map plus asset classification interpretation is complete.",
        "- Visual construction remains blocked.",
        "",
        f"- reason: {decision_payload['reason']}",
    ]
    DECISION_MD.write_text("\n".join(decision_md) + "\n", encoding="utf-8")

    print("SOURCE_MAP_JSON", safe_rel(SOURCE_MAP_JSON))
    print("SOURCE_MAP_MD", safe_rel(SOURCE_MAP_MD))
    print("DETAILS_JSON", safe_rel(DETAILS_JSON))
    print("DETAILS_MD", safe_rel(DETAILS_MD))
    print("DECISION_JSON", safe_rel(DECISION_JSON))
    print("DECISION_MD", safe_rel(DECISION_MD))
    print("LIKELY_TOP", [c["name"] for c in categories[:3]])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
