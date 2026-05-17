from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID = "TASK-SECOND-BRAIN-V07-ASSET-BUDGET-CLASSIFICATION"
CURRENT_TASK_HEAD = "f6fddf184b7ea0160d32ad6a17c490ffe0dbc4d8"
MAX_REF_SAMPLE = 50
MAX_HEAVY_SAMPLE = 20

REPO_ROOT = Path.cwd()
V6_APP_DIR = REPO_ROOT / "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app"
REPORTS_DIR = REPO_ROOT / "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports"

HTML_PATH = V6_APP_DIR / "neural_map_v0_6.html"
CSS_PATH = V6_APP_DIR / "neural_map_v0_6.css"
JS_PATH = V6_APP_DIR / "neural_map_v0_6.js"

PERF_BUDGET_PATH = (
    REPO_ROOT
    / "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/VISUAL_SYSTEM/PERFORMANCE_BUDGET_V0_1.json"
)
RECEIPT_PATH = (
    REPO_ROOT
    / "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/FULL_RUNTIME_PERFORMANCE_AUDIT_RECEIPT_V0_1.json"
)
BASELINE_INTERPRET_PATH = (
    REPO_ROOT
    / "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/FULL_RUNTIME_PERFORMANCE_BASELINE_INTERPRETATION_V0_1.json"
)
SOURCE_MAP_PATH = (
    REPO_ROOT
    / "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/PERFORMANCE_BLOCKER_SOURCE_MAP_V0_1.json"
)
SOURCE_MAP_DETAILS_PATH = (
    REPO_ROOT
    / "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/PERFORMANCE_BLOCKER_SOURCE_MAP_DETAILS_V0_1.json"
)

OUTPUT_CLASSIFICATION_JSON = REPORTS_DIR / "ASSET_BUDGET_CLASSIFICATION_V0_1.json"
OUTPUT_CLASSIFICATION_MD = REPORTS_DIR / "ASSET_BUDGET_CLASSIFICATION_V0_1.md"
OUTPUT_DETAILS_JSON = REPORTS_DIR / "ASSET_BUDGET_CLASSIFICATION_DETAILS_V0_1.json"
OUTPUT_DETAILS_MD = REPORTS_DIR / "ASSET_BUDGET_CLASSIFICATION_DETAILS_V0_1.md"
OUTPUT_DECISION_JSON = REPORTS_DIR / "ASSET_BUDGET_CLASSIFICATION_DECISION_V0_1.json"
OUTPUT_DECISION_MD = REPORTS_DIR / "ASSET_BUDGET_CLASSIFICATION_DECISION_V0_1.md"

IMAGE_EXTS = {".svg", ".webp", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".bmp", ".avif"}
FONT_EXTS = {".woff", ".woff2", ".ttf", ".otf"}
VIDEO_EXTS = {".mp4", ".webm", ".mkv", ".mov"}
AUDIO_EXTS = {".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a"}
DATA_EXTS = {".json"}
CODE_EXTS = {".css", ".js"}
TRACKED_EXTS = IMAGE_EXTS | FONT_EXTS | VIDEO_EXTS | AUDIO_EXTS | DATA_EXTS | CODE_EXTS


@dataclass(frozen=True)
class ReferenceRecord:
    source_file: str
    source_kind: str
    raw_reference: str
    normalized_reference: str
    extension: str
    asset_kind: str
    local_candidate_path: str | None
    local_exists: bool | None
    local_size_bytes: int | None


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def round_kb(value_bytes: int) -> float:
    return round(value_bytes / 1024, 2)


def round_mb(value_bytes: int) -> float:
    return round(value_bytes / (1024 * 1024), 4)


def normalize_ref(raw: str) -> str:
    trimmed = raw.strip().strip("'").strip('"')
    no_hash = trimmed.split("#", 1)[0]
    no_query = no_hash.split("?", 1)[0]
    return no_query.strip()


def is_external_ref(ref: str) -> bool:
    lowered = ref.lower()
    return (
        lowered.startswith("http://")
        or lowered.startswith("https://")
        or lowered.startswith("//")
        or lowered.startswith("data:")
        or lowered.startswith("mailto:")
        or lowered.startswith("javascript:")
        or lowered == ""
    )


def infer_asset_kind(ext: str) -> str:
    if ext in IMAGE_EXTS:
        return "IMAGE_OR_SVG"
    if ext in FONT_EXTS:
        return "FONT"
    if ext in VIDEO_EXTS:
        return "VIDEO"
    if ext in AUDIO_EXTS:
        return "AUDIO"
    if ext in DATA_EXTS:
        return "DATA_JSON"
    if ext in CODE_EXTS:
        return "ROUTE_CODE_FILE"
    return "OTHER"


def resolve_local_reference(normalized_ref: str, base_dir: Path) -> Path | None:
    if is_external_ref(normalized_ref):
        return None
    if normalized_ref.startswith("/"):
        candidate = V6_APP_DIR / normalized_ref.lstrip("/")
    else:
        candidate = base_dir / normalized_ref
    return candidate.resolve()


def extract_html_references(html_text: str) -> list[str]:
    refs: list[str] = []
    refs.extend(re.findall(r"""(?:src|href)\s*=\s*["']([^"']+)["']""", html_text, flags=re.IGNORECASE))
    refs.extend(re.findall(r"""url\(\s*["']?([^)'" ]+)["']?\s*\)""", html_text, flags=re.IGNORECASE))
    return refs


def extract_css_references(css_text: str) -> list[str]:
    return re.findall(r"""url\(\s*["']?([^)'" ]+)["']?\s*\)""", css_text, flags=re.IGNORECASE)


def extract_js_references(js_text: str) -> list[str]:
    exts_pattern = r"(?:svg|webp|png|jpe?g|gif|ico|bmp|avif|woff2?|ttf|otf|mp4|webm|mp3|wav|ogg|flac|aac|m4a|json|css|js)"
    regex = re.compile(
        rf"""["']([^"']+\.{exts_pattern}(?:\?[^"']*)?(?:#[^"']*)?)["']""",
        flags=re.IGNORECASE,
    )
    return [m.group(1) for m in regex.finditer(js_text)]


def scan_references(html_text: str, css_text: str, js_text: str) -> list[ReferenceRecord]:
    candidates: list[tuple[str, str, str, Path]] = []

    for raw in extract_html_references(html_text):
        candidates.append(("html", rel(HTML_PATH), raw, HTML_PATH.parent))
    for raw in extract_css_references(css_text):
        candidates.append(("css", rel(CSS_PATH), raw, CSS_PATH.parent))
    for raw in extract_js_references(js_text):
        candidates.append(("js", rel(JS_PATH), raw, JS_PATH.parent))

    seen: set[tuple[str, str, str]] = set()
    records: list[ReferenceRecord] = []
    for source_kind, source_file, raw_reference, base_dir in candidates:
        normalized = normalize_ref(raw_reference)
        key = (source_kind, source_file, normalized)
        if not normalized or key in seen:
            continue
        seen.add(key)
        extension = Path(normalized).suffix.lower()
        asset_kind = infer_asset_kind(extension)
        local_path = resolve_local_reference(normalized, base_dir)
        exists: bool | None = None
        size_bytes: int | None = None
        local_candidate: str | None = None
        if local_path is not None:
            local_candidate = local_path.as_posix()
            exists = local_path.exists() and local_path.is_file()
            if exists:
                size_bytes = local_path.stat().st_size
        records.append(
            ReferenceRecord(
                source_file=source_file,
                source_kind=source_kind,
                raw_reference=raw_reference,
                normalized_reference=normalized,
                extension=extension,
                asset_kind=asset_kind,
                local_candidate_path=local_candidate,
                local_exists=exists,
                local_size_bytes=size_bytes,
            )
        )
    return records


def indicator_counts(css_text: str, js_text: str, html_text: str) -> dict[str, Any]:
    selector_defs = re.findall(r"([^{}]+)\{", css_text)
    complex_selector_count = 0
    for sel in selector_defs:
        if any(token in sel for token in (":", ">", "+", "~", "[", ",")):
            complex_selector_count += 1

    return {
        "css": {
            "keyframes_count": len(re.findall(r"@keyframes", css_text, flags=re.IGNORECASE)),
            "animation_declarations_count": len(re.findall(r"(?<!-)animation\s*:", css_text, flags=re.IGNORECASE)),
            "transition_declarations_count": len(re.findall(r"transition\s*:", css_text, flags=re.IGNORECASE)),
            "filter_declarations_count": len(re.findall(r"(?<!-)filter\s*:", css_text, flags=re.IGNORECASE)),
            "backdrop_filter_declarations_count": len(
                re.findall(r"backdrop-filter\s*:", css_text, flags=re.IGNORECASE)
            ),
            "box_shadow_count": len(re.findall(r"box-shadow\s*:", css_text, flags=re.IGNORECASE)),
            "text_shadow_count": len(re.findall(r"text-shadow\s*:", css_text, flags=re.IGNORECASE)),
            "blur_marker_count": len(re.findall(r"blur\(", css_text, flags=re.IGNORECASE)),
            "transform_declarations_count": len(re.findall(r"transform\s*:", css_text, flags=re.IGNORECASE)),
            "will_change_count": len(re.findall(r"will-change\s*:", css_text, flags=re.IGNORECASE)),
            "position_fixed_count": len(re.findall(r"position\s*:\s*fixed", css_text, flags=re.IGNORECASE)),
            "position_sticky_count": len(re.findall(r"position\s*:\s*sticky", css_text, flags=re.IGNORECASE)),
            "large_z_index_count": len(
                re.findall(r"z-index\s*:\s*(?:[5-9]\d{2,}|\d{4,})", css_text, flags=re.IGNORECASE)
            ),
            "linear_gradient_count": len(re.findall(r"linear-gradient\(", css_text, flags=re.IGNORECASE)),
            "radial_gradient_count": len(re.findall(r"radial-gradient\(", css_text, flags=re.IGNORECASE)),
            "conic_gradient_count": len(re.findall(r"conic-gradient\(", css_text, flags=re.IGNORECASE)),
            "complex_selector_count": complex_selector_count,
            "prefers_reduced_motion_count": len(
                re.findall(r"prefers-reduced-motion", css_text, flags=re.IGNORECASE)
            ),
            "css_data_url_count": len(re.findall(r"url\(\s*[\"']?data:", css_text, flags=re.IGNORECASE)),
        },
        "js": {
            "request_animation_frame_count": len(re.findall(r"requestAnimationFrame\s*\(", js_text)),
            "set_interval_count": len(re.findall(r"setInterval\s*\(", js_text)),
            "set_timeout_count": len(re.findall(r"setTimeout\s*\(", js_text)),
            "event_listener_count": len(re.findall(r"addEventListener\s*\(", js_text)),
            "query_selector_all_count": len(re.findall(r"querySelectorAll\s*\(", js_text)),
            "inner_html_writes_count": len(re.findall(r"innerHTML\s*=", js_text)),
            "create_element_count": len(re.findall(r"createElement\s*\(", js_text)),
            "dom_append_count": len(re.findall(r"(?:appendChild|append)\s*\(", js_text)),
            "style_write_count": len(re.findall(r"\.style\.", js_text)),
            "classlist_mutation_count": len(
                re.findall(r"classList\.(?:add|remove|toggle|replace)\s*\(", js_text)
            ),
            "layout_read_count": len(
                re.findall(
                    r"(?:getBoundingClientRect\s*\(|offsetWidth\b|offsetHeight\b|scrollWidth\b|scrollHeight\b)",
                    js_text,
                )
            ),
            "local_storage_count": len(re.findall(r"(?:localStorage|sessionStorage)\.", js_text)),
            "fetch_count": len(re.findall(r"fetch\s*\(", js_text)),
            "svg_canvas_marker_count": len(re.findall(r"(?:svg|canvas)", js_text, flags=re.IGNORECASE)),
            "function_count": len(re.findall(r"\bfunction\b|=>", js_text)),
        },
        "html": {
            "inline_style_blocks_count": len(re.findall(r"<style\b", html_text, flags=re.IGNORECASE)),
            "inline_script_blocks_count": len(re.findall(r"<script\b(?![^>]*\bsrc=)", html_text, flags=re.IGNORECASE)),
            "svg_tag_count": len(re.findall(r"<svg\b", html_text, flags=re.IGNORECASE)),
            "canvas_tag_count": len(re.findall(r"<canvas\b", html_text, flags=re.IGNORECASE)),
            "img_tag_count": len(re.findall(r"<img\b", html_text, flags=re.IGNORECASE)),
            "dom_like_tag_count": len(re.findall(r"<[a-zA-Z][^>]*>", html_text)),
        },
    }


def as_list_dict(records: list[ReferenceRecord]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for rec in records:
        item = {
            "source_file": rec.source_file,
            "source_kind": rec.source_kind,
            "reference": rec.normalized_reference,
            "asset_kind": rec.asset_kind,
            "extension": rec.extension,
            "local_candidate_path": rec.local_candidate_path,
            "local_exists": rec.local_exists,
            "local_size_kb": round_kb(rec.local_size_bytes) if rec.local_size_bytes is not None else None,
        }
        out.append(item)
    return out


def build_payload() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    for path in (HTML_PATH, CSS_PATH, JS_PATH, PERF_BUDGET_PATH, RECEIPT_PATH):
        if not path.exists():
            raise FileNotFoundError(f"Required source is missing: {path}")

    html_text = read_text(HTML_PATH)
    css_text = read_text(CSS_PATH)
    js_text = read_text(JS_PATH)

    perf_budget = load_json(PERF_BUDGET_PATH)
    receipt = load_json(RECEIPT_PATH)
    baseline_interpret = load_json(BASELINE_INTERPRET_PATH)
    source_map = load_json(SOURCE_MAP_PATH)
    source_map_details = load_json(SOURCE_MAP_DETAILS_PATH)

    refs = scan_references(html_text, css_text, js_text)
    ref_dicts = as_list_dict(refs)

    route_required_files = [
        "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.html",
        "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.css",
        "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app/neural_map_v0_6.js",
    ]
    route_sizes = {
        "html_bytes": HTML_PATH.stat().st_size,
        "css_bytes": CSS_PATH.stat().st_size,
        "js_bytes": JS_PATH.stat().st_size,
    }
    route_total_bytes = route_sizes["html_bytes"] + route_sizes["css_bytes"] + route_sizes["js_bytes"]

    local_existing_refs = [
        r for r in refs if r.local_exists and r.local_size_bytes is not None and r.asset_kind != "ROUTE_CODE_FILE"
    ]
    missing_refs = [
        {
            "source_file": r.source_file,
            "source_kind": r.source_kind,
            "reference": r.normalized_reference,
            "asset_kind": r.asset_kind,
            "extension": r.extension,
            "local_candidate_path": r.local_candidate_path,
        }
        for r in refs
        if r.local_exists is False
    ]

    unique_payload_assets: dict[str, int] = {}
    for r in local_existing_refs:
        if r.local_candidate_path and r.local_size_bytes is not None:
            unique_payload_assets[r.local_candidate_path] = r.local_size_bytes

    additional_assets_bytes = sum(unique_payload_assets.values())
    payload_bytes = route_total_bytes + additional_assets_bytes
    payload_mb = round_mb(payload_bytes)
    target_mb = float(perf_budget.get("compressed_visual_assets_target_mb", 0.0))
    blocker_mb = float(perf_budget.get("compressed_visual_assets_blocker_mb", 0.0))

    if payload_mb >= blocker_mb > 0:
        payload_status = "BLOCKED"
        asset_pressure_status = "FILE_ASSET_PRESSURE_BLOCKER"
    elif payload_mb >= target_mb > 0:
        payload_status = "WARN"
        asset_pressure_status = "FILE_ASSET_PRESSURE_WARN"
    else:
        payload_status = "PASS"
        asset_pressure_status = "FILE_ASSET_PRESSURE_NOT_PRIMARY"

    counts = indicator_counts(css_text, js_text, html_text)
    likely_categories = source_map.get("likely_blocker_categories", [])
    strong_categories = [c.get("name") for c in likely_categories if c.get("likelihood") == "EVIDENCE_STRONG"]
    css_js_effect_pressure_status = "LIKELY_PRIMARY" if strong_categories else "POSSIBLE"

    top_heavy = sorted(
        [
            {
                "resolved_path": k,
                "size_kb": round_kb(v),
            }
            for k, v in unique_payload_assets.items()
        ],
        key=lambda x: x["size_kb"],
        reverse=True,
    )[:MAX_HEAVY_SAMPLE]

    ext_breakdown: dict[str, int] = {}
    for r in refs:
        key = r.extension or "<none>"
        ext_breakdown[key] = ext_breakdown.get(key, 0) + 1

    local_loaded_files = {
        "runtime_route_url": receipt.get("browser_target_url"),
        "runtime_route_http_status": receipt.get("browser_target_http_status"),
        "html_loaded": bool(receipt.get("html_loaded")),
        "css_loaded": bool(receipt.get("css_loaded")),
        "js_loaded": bool(receipt.get("js_loaded")),
        "failed_required_requests": receipt.get("failed_required_requests"),
    }

    classification_json = {
        "task_id": TASK_ID,
        "generated_at": utc_now(),
        "current_head": CURRENT_TASK_HEAD,
        "source_files": {
            "html": rel(HTML_PATH),
            "css": rel(CSS_PATH),
            "js": rel(JS_PATH),
        },
        "performance_budget_ref": rel(PERF_BUDGET_PATH),
        "route_required_files": route_required_files,
        "route_required_file_sizes": {
            **route_sizes,
            "route_required_total_bytes": route_total_bytes,
            "route_required_total_kb": round_kb(route_total_bytes),
        },
        "runtime_loaded_route_truth": local_loaded_files,
        "referenced_assets_summary": {
            "total_references_detected": len(refs),
            "tracked_extension_references": sum(1 for r in refs if r.extension in TRACKED_EXTS),
            "resolvable_existing_local_references": sum(1 for r in refs if r.local_exists),
            "missing_or_unresolved_local_references": len(missing_refs),
            "images_or_svg_references": sum(1 for r in refs if r.extension in IMAGE_EXTS),
            "font_references": sum(1 for r in refs if r.extension in FONT_EXTS),
            "video_references": sum(1 for r in refs if r.extension in VIDEO_EXTS),
            "audio_references": sum(1 for r in refs if r.extension in AUDIO_EXTS),
            "data_json_references": sum(1 for r in refs if r.extension in DATA_EXTS),
            "route_code_references": sum(1 for r in refs if r.extension in CODE_EXTS),
        },
        "local_estimated_initial_payload": {
            "estimated_payload_bytes": payload_bytes,
            "estimated_payload_mb": payload_mb,
            "route_required_bytes": route_total_bytes,
            "additional_resolved_asset_bytes": additional_assets_bytes,
            "method": "LOCAL_ESTIMATE_FROM_SOURCE_REFERENCES_NOT_RUNTIME_TRANSFER_MEASUREMENT",
        },
        "budget_comparison": {
            "compressed_visual_assets_target_mb": target_mb,
            "compressed_visual_assets_blocker_mb": blocker_mb,
            "estimated_payload_mb": payload_mb,
            "estimated_payload_vs_budget_status": payload_status,
        },
        "missing_referenced_assets": missing_refs[:MAX_REF_SAMPLE],
        "top_heaviest_referenced_assets": top_heavy,
        "non_file_visual_complexity_summary": {
            "css_indicator_counts": counts["css"],
            "js_indicator_counts": counts["js"],
            "html_indicator_counts": counts["html"],
            "source_map_strong_categories": strong_categories,
            "source_map_verdict_ref": source_map.get("verdict"),
            "source_map_details_ref": rel(SOURCE_MAP_DETAILS_PATH),
            "warning": "High CSS/JS visual complexity can block FPS even when file payload is moderate.",
        },
        "asset_pressure_verdict": asset_pressure_status,
        "limitations": [
            "This is metadata/source classification only; no browser/runtime execution.",
            "Payload is a local estimated payload, not actual compressed transfer bytes.",
            "Some references may be runtime-generated or API-fed and cannot be resolved statically.",
            "Exact root cause cannot be proven from asset metadata alone.",
        ],
        "recommended_next_task": (
            "TASK-SECOND-BRAIN-V07-ASSET-SLIMMING-PLAN-V0_1"
            if asset_pressure_status == "FILE_ASSET_PRESSURE_BLOCKER"
            else "TASK-SECOND-BRAIN-V07-PERFORMANCE-OPTIMIZATION-PLAN-V0_1"
        ),
        "verdict": "ASSET_BUDGET_CLASSIFIED_WITH_TRUTHFUL_LIMITATIONS",
        "evidence_refs": {
            "full_runtime_receipt": rel(RECEIPT_PATH),
            "baseline_interpretation": rel(BASELINE_INTERPRET_PATH),
            "source_map": rel(SOURCE_MAP_PATH),
            "source_map_details": rel(SOURCE_MAP_DETAILS_PATH),
            "baseline_interpretation_verdict": baseline_interpret.get("interpretation_verdict")
            or baseline_interpret.get("verdict"),
            "source_map_verdict": source_map.get("verdict"),
            "source_map_details_verdict": source_map_details.get("verdict"),
        },
    }

    details_json = {
        "task_id": TASK_ID,
        "generated_at": classification_json["generated_at"],
        "current_head": CURRENT_TASK_HEAD,
        "route_file_sizes": classification_json["route_required_file_sizes"],
        "referenced_assets_list_sample": ref_dicts[:MAX_REF_SAMPLE],
        "top_local_referenced_assets_by_size": top_heavy,
        "missing_referenced_assets": missing_refs[:MAX_REF_SAMPLE],
        "extension_breakdown": dict(sorted(ext_breakdown.items(), key=lambda kv: kv[0])),
        "omitted_count": {
            "referenced_assets_omitted": max(0, len(ref_dicts) - MAX_REF_SAMPLE),
            "missing_assets_omitted": max(0, len(missing_refs) - MAX_REF_SAMPLE),
            "heavy_assets_omitted": max(0, len(unique_payload_assets) - MAX_HEAVY_SAMPLE),
        },
        "verdict": "ASSET_BUDGET_DETAILS_COMPACT",
    }

    decision_next_task = classification_json["recommended_next_task"]
    decision_reason = (
        "Estimated local payload crosses blocker threshold."
        if asset_pressure_status == "FILE_ASSET_PRESSURE_BLOCKER"
        else "Asset file payload does not dominate blocker threshold; CSS/JS/effect pressure remains likely primary."
    )
    decision_json = {
        "task_id": TASK_ID,
        "generated_at": classification_json["generated_at"],
        "current_head": CURRENT_TASK_HEAD,
        "baseline_valid": True,
        "performance_blocked": True,
        "asset_budget_classified": True,
        "asset_file_pressure_status": asset_pressure_status,
        "css_js_effect_pressure_status": css_js_effect_pressure_status,
        "optimization_admitted_now": False,
        "visual_construction_admitted_now": False,
        "next_task_decision": decision_next_task,
        "reason": decision_reason,
        "verdict": "PERFORMANCE_BLOCKED_CLASSIFICATION_DIAGNOSTIC_ONLY",
    }

    return classification_json, details_json, decision_json


def to_markdown_classification(data: dict[str, Any]) -> str:
    route = data["route_required_file_sizes"]
    payload = data["local_estimated_initial_payload"]
    refs = data["referenced_assets_summary"]
    budget = data["budget_comparison"]
    non_file = data["non_file_visual_complexity_summary"]
    missing = data["missing_referenced_assets"]

    lines = [
        "# Asset Budget Classification V0.1",
        "",
        "## Baseline Truth",
        f"- task_id: `{data['task_id']}`",
        "- baseline performance remains blocked by FPS despite valid runtime route and successful HTML/CSS/JS/API loading.",
        "",
        "## Source Files Inspected",
        f"- html: `{data['source_files']['html']}`",
        f"- css: `{data['source_files']['css']}`",
        f"- js: `{data['source_files']['js']}`",
        "",
        "## Route Required File Sizes",
        f"- html_bytes: `{route['html_bytes']}`",
        f"- css_bytes: `{route['css_bytes']}`",
        f"- js_bytes: `{route['js_bytes']}`",
        f"- route_required_total_kb: `{route['route_required_total_kb']}`",
        "",
        "## Referenced Assets Summary",
        f"- total_references_detected: `{refs['total_references_detected']}`",
        f"- resolvable_existing_local_references: `{refs['resolvable_existing_local_references']}`",
        f"- missing_or_unresolved_local_references: `{refs['missing_or_unresolved_local_references']}`",
        f"- images_or_svg_references: `{refs['images_or_svg_references']}`",
        f"- font_references: `{refs['font_references']}`",
        f"- video_references: `{refs['video_references']}`",
        f"- audio_references: `{refs['audio_references']}`",
        "",
        "## Estimated Payload vs Budget",
        f"- estimated_payload_mb: `{payload['estimated_payload_mb']}`",
        f"- compressed_visual_assets_target_mb: `{budget['compressed_visual_assets_target_mb']}`",
        f"- compressed_visual_assets_blocker_mb: `{budget['compressed_visual_assets_blocker_mb']}`",
        f"- estimated_payload_vs_budget_status: `{budget['estimated_payload_vs_budget_status']}`",
        "",
        "## Verdict",
        f"- asset_pressure_verdict: `{data['asset_pressure_verdict']}`",
        "- assessment scope: diagnostic classification only, no optimization and no source edits.",
        "",
        "## Non-File Complexity Warning",
        f"- source_map_strong_categories: `{', '.join(non_file['source_map_strong_categories']) if non_file['source_map_strong_categories'] else 'none'}`",
        f"- css_keyframes: `{non_file['css_indicator_counts']['keyframes_count']}`",
        f"- css_animation_declarations: `{non_file['css_indicator_counts']['animation_declarations_count']}`",
        f"- css_filter_declarations: `{non_file['css_indicator_counts']['filter_declarations_count']}`",
        f"- js_requestAnimationFrame: `{non_file['js_indicator_counts']['request_animation_frame_count']}`",
        f"- js_dom_append_count: `{non_file['js_indicator_counts']['dom_append_count']}`",
        f"- js_style_write_count: `{non_file['js_indicator_counts']['style_write_count']}`",
        "",
        "## Unknowns",
        "- exact runtime transfer/compression/decode costs are not measured here;",
        "- dynamic/runtime-only references may exist beyond static source scan.",
        "",
        "## Missing Referenced Assets (sample)",
    ]
    if not missing:
        lines.append("- none")
    else:
        for item in missing[:10]:
            lines.append(
                f"- `{item['reference']}` from `{item['source_kind']}` -> missing at `{item['local_candidate_path']}`"
            )
    lines.extend(
        [
            "",
            f"## Next Recommended Task",
            f"- `{data['recommended_next_task']}`",
            "",
            "## Limitations",
        ]
    )
    for item in data["limitations"]:
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def to_markdown_details(data: dict[str, Any]) -> str:
    lines = [
        "# Asset Budget Classification Details V0.1",
        "",
        "## Route File Sizes",
        f"- html_bytes: `{data['route_file_sizes']['html_bytes']}`",
        f"- css_bytes: `{data['route_file_sizes']['css_bytes']}`",
        f"- js_bytes: `{data['route_file_sizes']['js_bytes']}`",
        f"- route_required_total_kb: `{data['route_file_sizes']['route_required_total_kb']}`",
        "",
        "## Referenced Assets Sample",
    ]
    sample = data["referenced_assets_list_sample"][:20]
    if not sample:
        lines.append("- no references captured")
    else:
        for item in sample:
            lines.append(
                f"- `{item['reference']}` [{item['asset_kind']}] exists={item['local_exists']} size_kb={item['local_size_kb']}"
            )
    lines.extend(["", "## Top Local Referenced Assets By Size"])
    if not data["top_local_referenced_assets_by_size"]:
        lines.append("- none")
    else:
        for item in data["top_local_referenced_assets_by_size"]:
            lines.append(f"- `{item['resolved_path']}` -> `{item['size_kb']} KB`")
    lines.extend(["", "## Missing Referenced Assets (sample)"])
    if not data["missing_referenced_assets"]:
        lines.append("- none")
    else:
        for item in data["missing_referenced_assets"][:20]:
            lines.append(f"- `{item['reference']}` -> `{item['local_candidate_path']}`")
    lines.extend(["", "## Extension Breakdown"])
    for ext, count in data["extension_breakdown"].items():
        lines.append(f"- `{ext}`: `{count}`")
    lines.extend(["", "## Omitted Count"])
    for key, value in data["omitted_count"].items():
        lines.append(f"- {key}: `{value}`")
    return "\n".join(lines) + "\n"


def to_markdown_decision(data: dict[str, Any]) -> str:
    lines = [
        "# Asset Budget Classification Decision V0.1",
        "",
        f"- baseline_valid: `{str(data['baseline_valid']).lower()}`",
        f"- performance_blocked: `{str(data['performance_blocked']).lower()}`",
        f"- asset_budget_classified: `{str(data['asset_budget_classified']).lower()}`",
        f"- asset_file_pressure_status: `{data['asset_file_pressure_status']}`",
        f"- css_js_effect_pressure_status: `{data['css_js_effect_pressure_status']}`",
        "",
        "## Guardrails",
        "- classification is diagnostic, not a fix;",
        "- performance remains blocked;",
        "- visual construction remains blocked;",
        "- next task is planning/analysis, not direct optimization implementation.",
        "",
        f"- optimization_admitted_now: `{str(data['optimization_admitted_now']).lower()}`",
        f"- visual_construction_admitted_now: `{str(data['visual_construction_admitted_now']).lower()}`",
        f"- next_task_decision: `{data['next_task_decision']}`",
        f"- reason: {data['reason']}",
        f"- verdict: `{data['verdict']}`",
    ]
    return "\n".join(lines) + "\n"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    classification_json, details_json, decision_json = build_payload()

    write_json(OUTPUT_CLASSIFICATION_JSON, classification_json)
    write_json(OUTPUT_DETAILS_JSON, details_json)
    write_json(OUTPUT_DECISION_JSON, decision_json)

    OUTPUT_CLASSIFICATION_MD.write_text(to_markdown_classification(classification_json), encoding="utf-8")
    OUTPUT_DETAILS_MD.write_text(to_markdown_details(details_json), encoding="utf-8")
    OUTPUT_DECISION_MD.write_text(to_markdown_decision(decision_json), encoding="utf-8")

    print("CLASSIFICATION_JSON", rel(OUTPUT_CLASSIFICATION_JSON))
    print("CLASSIFICATION_MD", rel(OUTPUT_CLASSIFICATION_MD))
    print("DETAILS_JSON", rel(OUTPUT_DETAILS_JSON))
    print("DETAILS_MD", rel(OUTPUT_DETAILS_MD))
    print("DECISION_JSON", rel(OUTPUT_DECISION_JSON))
    print("DECISION_MD", rel(OUTPUT_DECISION_MD))
    print("NEXT_TASK", decision_json["next_task_decision"])


if __name__ == "__main__":
    main()
