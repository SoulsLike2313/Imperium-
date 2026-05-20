from __future__ import annotations

import json
from typing import Any, Iterable

from rich.box import SIMPLE_HEAVY
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from operator_shell_skin import MECHANICUS_COLORS, clip_text, state_color, title_line


def _as_rows(values: Iterable[tuple[str, str, str, str]]) -> Table:
    table = Table(box=SIMPLE_HEAVY, show_header=True, expand=True, padding=(0, 1))
    table.add_column("TIME", style=MECHANICUS_COLORS["text_dim"], width=10)
    table.add_column("ITEM", style=MECHANICUS_COLORS["text_main"], width=22)
    table.add_column("DETAIL", style=MECHANICUS_COLORS["text_main"])
    table.add_column("STATE", width=11)
    for t_value, item, detail, state in values:
        style = state_color(state)
        table.add_row(t_value, item, clip_text(detail, 92), f"[{style}]{state}[/]")
    return table


def top_status_panel(payload: dict[str, Any], organ_name: str, mission: str, shell_version: str) -> Panel:
    text = Text.from_markup(title_line(organ_name=organ_name, mission=mission, shell_version=shell_version))
    return Panel(
        text,
        title="TOP STATUS BAR",
        border_style=MECHANICUS_COLORS["panel_border"],
        padding=(0, 1),
    )


def activity_panel(payload: dict[str, Any]) -> Panel:
    rows = payload.get("activity_rows", [])
    safe_rows: list[tuple[str, str, str, str]] = []
    for row in rows:
        if isinstance(row, tuple) and len(row) == 4:
            safe_rows.append((str(row[0]), str(row[1]), str(row[2]), str(row[3])))
        elif isinstance(row, list) and len(row) == 4:
            safe_rows.append((str(row[0]), str(row[1]), str(row[2]), str(row[3])))
    return Panel(
        _as_rows(safe_rows),
        title="LEFT WORK ZONE // CURRENT ACTIVITY",
        border_style=MECHANICUS_COLORS["panel_border"],
    )


def mission_panel(payload: dict[str, Any], mission: str) -> Panel:
    latest_output = str(payload.get("latest_output", "")).strip() or "shell_ready"
    content = Text.from_markup(
        f"[bold {MECHANICUS_COLORS['accent_amber']}]MISSION FOCUS[/]\n"
        f"[{MECHANICUS_COLORS['text_main']}]{clip_text(mission, 110)}[/]\n\n"
        f"[{MECHANICUS_COLORS['text_dim']}]latest_output: {clip_text(latest_output, 110)}[/]"
    )
    return Panel(
        content,
        title="LEFT WORK ZONE // MISSION FOCUS",
        border_style=MECHANICUS_COLORS["panel_border"],
        padding=(0, 1),
    )


def command_palette_panel(payload: dict[str, Any]) -> Panel:
    table = Table(box=SIMPLE_HEAVY, show_header=True, expand=True, padding=(0, 1))
    table.add_column("CMD", style=MECHANICUS_COLORS["accent_cyan"], width=14)
    table.add_column("SUMMARY", style=MECHANICUS_COLORS["text_main"])
    table.add_column("KEY", style=MECHANICUS_COLORS["accent_amber"], width=9)
    for cmd, summary, key in payload.get("palette", [])[:16]:
        table.add_row(str(cmd), clip_text(str(summary), 62), str(key))
    return Panel(
        table,
        title="COMMAND ZONE // OPERATOR PALETTE",
        border_style=MECHANICUS_COLORS["panel_border"],
    )


def tool_registry_panel(payload: dict[str, Any]) -> Panel:
    tool_summary = payload.get("tool_summary", {}) if isinstance(payload.get("tool_summary"), dict) else {}
    table = Table(box=SIMPLE_HEAVY, show_header=True, expand=True, padding=(0, 1))
    table.add_column("TOOL", style=MECHANICUS_COLORS["accent_cyan"], width=24)
    table.add_column("OWNER", style=MECHANICUS_COLORS["text_main"], width=21)
    table.add_column("STATUS", style=MECHANICUS_COLORS["text_main"], width=18)

    rows = payload.get("tool_rows", [])
    if rows:
        for row in rows[:12]:
            if not isinstance(row, (list, tuple)) or len(row) != 3:
                continue
            status_value = str(row[2]).upper()
            status_style = state_color(status_value)
            table.add_row(str(row[0]), str(row[1]), f"[{status_style}]{status_value}[/]")
    else:
        preview = tool_summary.get("preview", []) if isinstance(tool_summary.get("preview"), list) else []
        for token in preview[:10]:
            table.add_row(str(token), "MECHANICUS_AGENT", f"[{MECHANICUS_COLORS['accent_cyan']}]SUMMARY[/]")

    caption = (
        "registered="
        f"{tool_summary.get('registered_tool_count', 0)} "
        f"available={tool_summary.get('available_tool_count', 0)} "
        f"missing={tool_summary.get('missing_tool_count', 0)}"
    )
    return Panel(
        table,
        title=f"TOOL REGISTRY // CAPABILITY OVERVIEW [{caption}]",
        border_style=MECHANICUS_COLORS["panel_border"],
    )


def bottom_event_panel(payload: dict[str, Any]) -> Panel:
    lines = payload.get("bottom", []) if isinstance(payload.get("bottom"), list) else []
    text = Text()
    for line in lines:
        text.append(f"{line}\n", style=MECHANICUS_COLORS["text_dim"])
    text.append(
        f"event_summary: WARN={payload.get('warn_count', 0)} "
        f"ERROR={payload.get('error_count', 0)} "
        f"BLOCK={payload.get('block_count', 0)}",
        style=MECHANICUS_COLORS["accent_amber"],
    )
    return Panel(
        text,
        title="BOTTOM EVENT BAR",
        border_style=MECHANICUS_COLORS["panel_border"],
        padding=(0, 1),
    )


def raw_detail_panel(payload: dict[str, Any]) -> Panel:
    raw = payload.get("raw_payload", {})
    dump = json.dumps(raw, ensure_ascii=True, indent=2)
    if len(dump) > 8000:
        dump = dump[:8000] + "\n...<truncated>..."
    return Panel(
        Text(dump, style=MECHANICUS_COLORS["text_main"]),
        title="RAW DETAIL MODE (EXPLICIT)",
        border_style=MECHANICUS_COLORS["accent_amber"],
        padding=(0, 1),
    )

