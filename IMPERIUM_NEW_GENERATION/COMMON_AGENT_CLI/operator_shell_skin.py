from __future__ import annotations

from typing import Dict

SHELL_VERSION_V0_3 = "v0.3"

MECHANICUS_COLORS: Dict[str, str] = {
    "bg": "#05080d",
    "panel_border": "#8b2a24",
    "accent_cyan": "#2fdcff",
    "accent_amber": "#ffb347",
    "accent_red": "#ff4d4d",
    "accent_green": "#4cd964",
    "text_main": "#d7dce2",
    "text_dim": "#8f98a3",
}

STATE_STYLE_MAP: Dict[str, str] = {
    "OK": MECHANICUS_COLORS["accent_green"],
    "READY": MECHANICUS_COLORS["accent_green"],
    "IN_SYNC": MECHANICUS_COLORS["accent_green"],
    "LOADED": MECHANICUS_COLORS["accent_green"],
    "VERIFIED": MECHANICUS_COLORS["accent_cyan"],
    "FOCUS": MECHANICUS_COLORS["accent_cyan"],
    "INFO": MECHANICUS_COLORS["accent_cyan"],
    "WARN": MECHANICUS_COLORS["accent_amber"],
    "ERROR": MECHANICUS_COLORS["accent_red"],
    "BLOCK": MECHANICUS_COLORS["accent_red"],
}


def clip_text(value: str, limit: int = 96) -> str:
    text = value.strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def state_color(token: str) -> str:
    normalized = token.strip().upper().replace("-", "_")
    return STATE_STYLE_MAP.get(normalized, MECHANICUS_COLORS["text_main"])


def title_line(organ_name: str, mission: str, shell_version: str = SHELL_VERSION_V0_3) -> str:
    clipped_mission = clip_text(mission, 92)
    return (
        f"[bold {MECHANICUS_COLORS['accent_red']}]MECHANICUS_OPERATOR[/] "
        f"[{MECHANICUS_COLORS['text_dim']}]//[/] "
        f"[bold {MECHANICUS_COLORS['accent_cyan']}]{organ_name}[/] "
        f"[{MECHANICUS_COLORS['text_dim']}]//[/] "
        f"[{MECHANICUS_COLORS['accent_amber']}]shell {shell_version}[/]\n"
        f"[{MECHANICUS_COLORS['text_dim']}]{clipped_mission}[/]"
    )

