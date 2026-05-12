#!/usr/bin/env python3
"""IMPERIUM visual mood prototype for future AI Operator Console."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import math
import random
import sys

try:
    from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
    from PySide6.QtGui import (
        QColor,
        QBrush,
        QFont,
        QLinearGradient,
        QPainter,
        QPainterPath,
        QPen,
        QRadialGradient,
    )
    from PySide6.QtWidgets import (
        QApplication,
        QCheckBox,
        QFrame,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QPushButton,
        QSizePolicy,
        QVBoxLayout,
        QWidget,
    )

    PYSIDE6_AVAILABLE = True
    PYSIDE6_IMPORT_ERROR = ""
except Exception as exc:  # pragma: no cover - runtime dependency guard
    PYSIDE6_AVAILABLE = False
    PYSIDE6_IMPORT_ERROR = str(exc)


APP_TITLE = "IMPERIUM - AI Operator Console Mood v0.1"
PROTOTYPE_BANNER = "VISUAL PROTOTYPE / MOCK DATA / NO OPERATOR ACTIONS"

PARTICLE_COUNT = 72
ANIMATION_INTERVAL_MS = 16
ENABLE_HEAVY_GLOW = True

PERF_PARTICLE_COUNT = 28
PERF_ANIMATION_INTERVAL_MS = 40

ORB_PULSE_SPEED = 0.010
ORB_ROTATION_SPEED = 0.045
ARC_COUNT = 6
CAVE_CURVE_COUNT = 9

PALETTE = {
    "void": QColor(6, 4, 18),
    "deep": QColor(10, 8, 30),
    "cave": QColor(16, 10, 40),
    "violet": QColor(132, 78, 238),
    "magenta": QColor(208, 96, 220),
    "cyan": QColor(90, 230, 255),
    "cyan_dim": QColor(64, 152, 206),
    "core": QColor(255, 248, 246),
    "panel_bg_top": QColor(18, 12, 42, 186),
    "panel_bg_bottom": QColor(10, 8, 26, 212),
    "panel_border": QColor(130, 86, 236, 160),
    "panel_border_bright": QColor(182, 142, 255, 196),
    "text": QColor(230, 224, 255),
    "text_dim": QColor(154, 136, 186),
    "accent": QColor(186, 255, 255),
    "ok": QColor(92, 240, 176),
    "warn": QColor(255, 202, 104),
    "need": QColor(188, 214, 255),
}


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    size: float
    alpha: float
    ttl: float
    ttl_max: float
    tint: float


if PYSIDE6_AVAILABLE:

    class OperatorButton(QPushButton):
        def __init__(self, text: str, parent: QWidget | None = None):
            super().__init__(text, parent)
            self.setFixedHeight(36)
            self.setCursor(Qt.PointingHandCursor)
            self.setStyleSheet(
                """
                QPushButton {
                    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                        stop:0 rgba(44, 22, 92, 222),
                        stop:1 rgba(24, 12, 58, 232));
                    color: rgba(230, 218, 255, 236);
                    border: 1px solid rgba(126, 84, 224, 178);
                    border-radius: 9px;
                    padding: 4px 12px;
                    font-family: 'Segoe UI Semibold';
                    font-size: 9pt;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                        stop:0 rgba(76, 40, 154, 230),
                        stop:1 rgba(38, 19, 88, 238));
                    border: 1px solid rgba(182, 142, 255, 224);
                    color: rgba(248, 242, 255, 255);
                }
                QPushButton:pressed {
                    background: rgba(96, 54, 174, 240);
                }
                """
            )


    class StatusChip(QWidget):
        def __init__(self, text: str, color: QColor, parent: QWidget | None = None):
            super().__init__(parent)
            self.text = text
            self.color = color
            self.setFixedHeight(24)

        def paintEvent(self, _event) -> None:  # noqa: N802
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(self.color))
            painter.drawEllipse(QRectF(6, 8, 8, 8))

            painter.setPen(QPen(PALETTE["text"], 1))
            painter.setFont(QFont("Consolas", 8))
            painter.drawText(20, 16, self.text)


    class GlassPanel(QFrame):
        def __init__(self, title: str, parent: QWidget | None = None):
            super().__init__(parent)
            self.title = title
            self.setStyleSheet("background: transparent; border: none;")

        def paintEvent(self, event) -> None:  # noqa: N802
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing, True)
            rect = QRectF(1, 1, self.width() - 2, self.height() - 2)

            bg = QLinearGradient(rect.topLeft(), rect.bottomLeft())
            bg.setColorAt(0.0, PALETTE["panel_bg_top"])
            bg.setColorAt(1.0, PALETTE["panel_bg_bottom"])
            painter.setBrush(QBrush(bg))
            painter.setPen(QPen(PALETTE["panel_border"], 1.2))
            painter.drawRoundedRect(rect, 12, 12)

            painter.setPen(QPen(PALETTE["panel_border_bright"], 0.9))
            painter.drawLine(int(rect.left()) + 14, int(rect.top()) + 28, int(rect.right()) - 14, int(rect.top()) + 28)

            painter.setPen(QPen(PALETTE["accent"], 1))
            painter.setFont(QFont("Segoe UI Semibold", 10))
            painter.drawText(rect.adjusted(14, 8, -14, 0), Qt.AlignLeft | Qt.AlignTop, self.title)
            super().paintEvent(event)


    class PortalCanvas(QWidget):
        def __init__(self, parent: QWidget | None = None):
            super().__init__(parent)
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.setMinimumSize(500, 340)
            self.animation_enabled = True
            self.performance_mode = False
            self.heavy_glow_enabled = ENABLE_HEAVY_GLOW
            self.tick = 0.0
            self._fps_acc = 0
            self.current_fps = 0
            self.particles: list[Particle] = []
            self.target_particle_count = PARTICLE_COUNT

            self.timer = QTimer(self)
            self.timer.timeout.connect(self._on_frame)
            self.timer.start(ANIMATION_INTERVAL_MS)

            self.fps_timer = QTimer(self)
            self.fps_timer.timeout.connect(self._flush_fps)
            self.fps_timer.start(1000)

            self._reset_particles(self.target_particle_count)

        def set_animation(self, enabled: bool) -> None:
            self.animation_enabled = enabled

        def set_performance_mode(self, enabled: bool) -> None:
            self.performance_mode = enabled
            if enabled:
                self.target_particle_count = PERF_PARTICLE_COUNT
                self.heavy_glow_enabled = False
                self.timer.setInterval(PERF_ANIMATION_INTERVAL_MS)
            else:
                self.target_particle_count = PARTICLE_COUNT
                self.heavy_glow_enabled = ENABLE_HEAVY_GLOW
                self.timer.setInterval(ANIMATION_INTERVAL_MS)
            self._reset_particles(self.target_particle_count)
            self.update()

        def _reset_particles(self, count: int) -> None:
            self.particles = [self._spawn_particle(random_life=True) for _ in range(max(1, count))]

        def _spawn_particle(self, random_life: bool = False) -> Particle:
            angle = random.uniform(0.0, math.tau)
            radius = random.uniform(0.05, 0.48)
            speed = random.uniform(0.08, 0.46)
            ttl_max = random.uniform(90, 280)
            ttl = random.uniform(0, ttl_max) if random_life else 0.0
            return Particle(
                x=0.5 + math.cos(angle) * radius,
                y=0.5 + math.sin(angle) * radius,
                vx=math.cos(angle) * speed * 0.0018,
                vy=-abs(speed) * 0.003 + random.uniform(-0.0012, 0.0008),
                size=random.uniform(1.0, 3.4),
                alpha=random.uniform(0.24, 0.9),
                ttl=ttl,
                ttl_max=ttl_max,
                tint=random.uniform(0.0, 1.0),
            )

        def _on_frame(self) -> None:
            if not self.animation_enabled:
                return
            self.tick += 1.0
            self._update_particles()
            self._fps_acc += 1
            self.update()

        def _flush_fps(self) -> None:
            self.current_fps = self._fps_acc
            self._fps_acc = 0

        def _update_particles(self) -> None:
            for idx, p in enumerate(self.particles):
                p.x += p.vx
                p.y += p.vy
                p.ttl += 1.0
                if p.ttl >= p.ttl_max or p.x < -0.12 or p.x > 1.12 or p.y < -0.12 or p.y > 1.12:
                    self.particles[idx] = self._spawn_particle(random_life=False)

        def paintEvent(self, _event) -> None:  # noqa: N802
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

            w = float(self.width())
            h = float(self.height())
            cx = w / 2.0
            cy = h / 2.0
            scale = min(w, h)

            self._draw_background(painter, w, h, cx, cy)
            self._draw_cave_frame(painter, cx, cy, w, h)
            self._draw_orbit_arcs(painter, cx, cy, scale)
            self._draw_core(painter, cx, cy, scale)
            self._draw_particles(painter, w, h)
            self._draw_overlay_text(painter, w)

        def _draw_background(self, painter: QPainter, w: float, h: float, cx: float, cy: float) -> None:
            grad = QRadialGradient(QPointF(cx, cy), max(w, h) * 0.70)
            grad.setColorAt(0.0, PALETTE["cave"])
            grad.setColorAt(0.5, PALETTE["deep"])
            grad.setColorAt(1.0, PALETTE["void"])
            painter.fillRect(self.rect(), QBrush(grad))

        def _draw_cave_frame(self, painter: QPainter, cx: float, cy: float, w: float, h: float) -> None:
            for i in range(CAVE_CURVE_COUNT):
                phase = (i / CAVE_CURVE_COUNT) * math.tau
                wobble = math.sin(self.tick * 0.010 + i * 1.1) * 0.055

                edge_x = cx + math.cos(phase) * w * 0.63
                edge_y = cy + math.sin(phase) * h * 0.63
                in1_x = cx + math.cos(phase + 0.36) * w * (0.28 + wobble)
                in1_y = cy + math.sin(phase + 0.36) * h * (0.28 + wobble)
                in2_x = cx + math.cos(phase - 0.36) * w * (0.32 + wobble)
                in2_y = cy + math.sin(phase - 0.36) * h * (0.32 + wobble)
                dst_x = cx + math.cos(phase + math.pi) * w * 0.58
                dst_y = cy + math.sin(phase + math.pi) * h * 0.58

                path = QPainterPath()
                path.moveTo(edge_x, edge_y)
                path.cubicTo(in1_x, in1_y, in2_x, in2_y, dst_x, dst_y)

                dark = QColor(34, 20, 72, 58 + int(18 * math.sin(self.tick * 0.015 + i)))
                edge = QColor(112, 70, 212, 28 + int(14 * math.sin(self.tick * 0.012 + i * 0.8)))

                painter.setBrush(Qt.NoBrush)
                painter.setPen(QPen(dark, 16 + i * 1.7, Qt.SolidLine, Qt.RoundCap))
                painter.drawPath(path)
                painter.setPen(QPen(edge, 1.3))
                painter.drawPath(path)

        def _draw_orbit_arcs(self, painter: QPainter, cx: float, cy: float, scale: float) -> None:
            painter.setBrush(Qt.NoBrush)
            for i in range(ARC_COUNT):
                radius = scale * (0.12 + i * 0.058)
                spin = self.tick * ORB_ROTATION_SPEED * (1 if i % 2 == 0 else -1)
                alpha = int(40 + 35 * math.sin(self.tick * 0.013 + i * 0.9))
                color = QColor(PALETTE["cyan_dim"])
                color.setAlpha(max(12, min(120, alpha)))
                painter.setPen(QPen(color, 1.0 + i * 0.22))

                painter.save()
                painter.translate(cx, cy)
                painter.rotate(i * 16.0 + spin)
                painter.scale(1.0, 0.55 + i * 0.07)
                painter.drawEllipse(QRectF(-radius, -radius, radius * 2.0, radius * 2.0))
                painter.restore()

        def _draw_core(self, painter: QPainter, cx: float, cy: float, scale: float) -> None:
            pulse = math.sin(self.tick * ORB_PULSE_SPEED)
            core_r = scale * 0.067 + pulse * 1.8

            if self.heavy_glow_enabled:
                for layer in range(7):
                    layer_r = core_r * (4.0 - layer * 0.42)
                    alpha = max(8, 36 - layer * 4)
                    glow = QRadialGradient(QPointF(cx, cy), layer_r)
                    glow.setColorAt(0.0, QColor(232, 178, 255, alpha))
                    glow.setColorAt(0.5, QColor(146, 72, 220, alpha // 2))
                    glow.setColorAt(1.0, QColor(0, 0, 0, 0))
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(QBrush(glow))
                    painter.drawEllipse(QRectF(cx - layer_r, cy - layer_r, layer_r * 2.0, layer_r * 2.0))

            mid_r = core_r * 1.8
            mid = QRadialGradient(QPointF(cx, cy), mid_r)
            mid.setColorAt(0.0, QColor(255, 238, 255, 180))
            mid.setColorAt(0.36, QColor(226, 166, 255, 120))
            mid.setColorAt(0.74, QColor(136, 68, 214, 42))
            mid.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(mid))
            painter.drawEllipse(QRectF(cx - mid_r, cy - mid_r, mid_r * 2.0, mid_r * 2.0))

            core = QRadialGradient(QPointF(cx - core_r * 0.20, cy - core_r * 0.28), core_r)
            core.setColorAt(0.0, PALETTE["core"])
            core.setColorAt(0.42, QColor(226, 182, 255))
            core.setColorAt(0.85, QColor(132, 60, 198))
            core.setColorAt(1.0, QColor(78, 30, 132, 0))
            painter.setPen(QPen(QColor(210, 168, 255, 112), 1.4))
            painter.setBrush(QBrush(core))
            painter.drawEllipse(QRectF(cx - core_r, cy - core_r, core_r * 2.0, core_r * 2.0))

            highlight_r = core_r * 0.42
            hx = cx - core_r * 0.28
            hy = cy - core_r * 0.30
            hl = QRadialGradient(QPointF(hx, hy), highlight_r)
            hl.setColorAt(0.0, QColor(255, 255, 255, 160))
            hl.setColorAt(1.0, QColor(255, 255, 255, 0))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(hl))
            painter.drawEllipse(QRectF(hx - highlight_r, hy - highlight_r, highlight_r * 2.0, highlight_r * 2.0))

        def _draw_particles(self, painter: QPainter, w: float, h: float) -> None:
            painter.setPen(Qt.NoPen)
            for p in self.particles:
                ratio = p.ttl / max(1.0, p.ttl_max)
                fade = max(0.0, 1.0 - abs(ratio * 2.0 - 1.0))
                alpha = int(p.alpha * fade * 220)
                if alpha <= 1:
                    continue

                if p.tint < 0.5:
                    color = QColor(84 + int(90 * p.tint), 180 + int(70 * p.tint), 255, alpha)
                else:
                    color = QColor(148 + int(70 * (p.tint - 0.5)), 92 + int(90 * (1.0 - p.tint)), 255, alpha)

                px = p.x * w
                py = p.y * h
                r = p.size * (0.82 + 0.46 * fade)
                painter.setBrush(QBrush(color))
                painter.drawEllipse(QRectF(px - r, py - r, r * 2.0, r * 2.0))

        def _draw_overlay_text(self, painter: QPainter, w: float) -> None:
            painter.setPen(QPen(PALETTE["text_dim"], 1))
            painter.setFont(QFont("Consolas", 8))
            mode = "PERF" if self.performance_mode else "FULL"
            anim = "ON" if self.animation_enabled else "OFF"
            painter.drawText(int(w - 206), 18, f"FPS {self.current_fps:02d} | MODE {mode} | ANIM {anim}")


    class ImperiumOperatorWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle(APP_TITLE)
            self.setMinimumSize(1300, 840)
            self.setStyleSheet(
                """
                QMainWindow { background: rgb(6, 4, 18); }
                QWidget { color: rgba(230, 224, 255, 230); }
                QLabel { background: transparent; }
                QCheckBox { color: rgba(164, 146, 198, 216); font-size: 8pt; }
                """
            )

            root = QWidget()
            self.setCentralWidget(root)
            main = QVBoxLayout(root)
            main.setContentsMargins(0, 0, 0, 0)
            main.setSpacing(0)

            self.mock_action_label = QLabel("mock action: idle")
            self.portal = PortalCanvas()

            main.addWidget(self._build_header())

            body = QHBoxLayout()
            body.setContentsMargins(8, 6, 8, 6)
            body.setSpacing(8)
            body.addWidget(self._build_left_panel(), stretch=1)
            body.addWidget(self.portal, stretch=3)
            body.addWidget(self._build_right_panel(), stretch=1)
            main.addLayout(body, stretch=1)

            main.addWidget(self._build_bottom_bar())

        def _build_header(self) -> QWidget:
            panel = QWidget()
            panel.setFixedHeight(72)
            panel.setStyleSheet("background: rgba(10, 8, 24, 238);")
            h = QHBoxLayout(panel)
            h.setContentsMargins(18, 8, 18, 8)
            h.setSpacing(10)

            title_col = QVBoxLayout()
            title = QLabel("IMPERIUM / Freelance + AI Operator Console")
            title.setFont(QFont("Segoe UI Semibold", 14))
            title.setStyleSheet("color: rgba(202, 182, 255, 242);")
            subtitle = QLabel(PROTOTYPE_BANNER)
            subtitle.setFont(QFont("Consolas", 8))
            subtitle.setStyleSheet("color: rgba(136, 114, 176, 196);")
            title_col.addWidget(title)
            title_col.addWidget(subtitle)
            h.addLayout(title_col)

            h.addStretch()

            self.chk_animation = QCheckBox("Animation")
            self.chk_animation.setChecked(True)
            self.chk_animation.toggled.connect(self.portal.set_animation)
            h.addWidget(self.chk_animation)

            self.chk_performance = QCheckBox("Performance mode")
            self.chk_performance.setChecked(False)
            self.chk_performance.toggled.connect(self._on_perf_toggled)
            h.addWidget(self.chk_performance)

            return panel

        def _build_left_panel(self) -> GlassPanel:
            panel = GlassPanel("Freelance Acquisition")
            v = QVBoxLayout(panel)
            v.setContentsMargins(14, 36, 14, 14)
            v.setSpacing(7)

            cards = [
                ("Leads", "Upwork / Fiverr / direct channels (mock view)"),
                ("Proposals", "draft / submit / follow-up pipeline (mock)"),
                ("Client Dialogues", "active negotiation lanes (mock)"),
                ("Portfolio", "assets, demos, CTA hooks (mock)"),
                ("Social Cadence", "short-form + outreach rhythm (mock)"),
                ("Evidence Pack", "deliverables timeline (mock)"),
            ]

            for title, desc in cards:
                cap = QLabel(title)
                cap.setFont(QFont("Segoe UI Semibold", 9))
                cap.setStyleSheet("color: rgba(214, 204, 255, 226);")
                txt = QLabel(desc)
                txt.setFont(QFont("Segoe UI", 8))
                txt.setWordWrap(True)
                txt.setStyleSheet("color: rgba(152, 136, 186, 204); margin-bottom: 4px;")
                v.addWidget(cap)
                v.addWidget(txt)

            v.addStretch()
            return panel

        def _build_right_panel(self) -> GlassPanel:
            panel = GlassPanel("Imperium Control")
            v = QVBoxLayout(panel)
            v.setContentsMargins(14, 36, 14, 14)
            v.setSpacing(6)

            chips = [
                ("MOCK Git Truth: PASS", PALETTE["ok"]),
                ("MOCK Verification: PASS_WITH_WARNINGS", PALETTE["warn"]),
                ("MOCK Owner Approval: REQUIRED", PALETTE["need"]),
                ("MOCK Agent Mode: DRAFT_ONLY", PALETTE["cyan_dim"]),
                ("MOCK Risk Level: LOW", PALETTE["ok"]),
                ("MOCK Push Status: BLOCKED", PALETTE["warn"]),
            ]
            for text, color in chips:
                v.addWidget(StatusChip(text, color))

            v.addSpacing(10)

            explain = QLabel(
                "Этот экран показывает только визуальный mood.\n"
                "Данные фиксированы и не читают runtime.\n"
                "Операторские действия не выполняются."
            )
            explain.setWordWrap(True)
            explain.setFont(QFont("Segoe UI", 8))
            explain.setStyleSheet("color: rgba(170, 152, 206, 204);")
            v.addWidget(explain)

            v.addStretch()
            return panel

        def _build_bottom_bar(self) -> QWidget:
            bar = QWidget()
            bar.setFixedHeight(92)
            bar.setStyleSheet("background: rgba(10, 8, 24, 226);")
            v = QVBoxLayout(bar)
            v.setContentsMargins(16, 8, 16, 8)
            v.setSpacing(6)

            row = QHBoxLayout()
            row.setSpacing(10)
            actions = [
                "Scan Leads",
                "Draft Proposal",
                "Build Offer",
                "Review Evidence",
                "Owner Gate",
                "Publish Packet",
            ]
            for action in actions:
                btn = OperatorButton(action)
                btn.clicked.connect(lambda _=False, name=action: self._set_mock_action(name))
                row.addWidget(btn)

            row.addStretch()
            v.addLayout(row)

            self.mock_action_label.setFont(QFont("Consolas", 9))
            self.mock_action_label.setStyleSheet("color: rgba(168, 244, 244, 214);")
            v.addWidget(self.mock_action_label)
            return bar

        def _set_mock_action(self, action_name: str) -> None:
            stamp = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
            self.mock_action_label.setText(f"mock action: {action_name} / {stamp}")

        def _on_perf_toggled(self, enabled: bool) -> None:
            self.portal.set_performance_mode(enabled)
            if enabled:
                self.mock_action_label.setText(
                    "mock action: performance mode enabled (reduced particles, slower frame interval)"
                )
            else:
                self.mock_action_label.setText(
                    "mock action: performance mode disabled (full visual profile)"
                )


def main() -> int:
    if not PYSIDE6_AVAILABLE:
        print(
            "PySide6 is not available on this environment. "
            "This visual mood prototype requires PySide6 for GUI run.",
            file=sys.stderr,
        )
        if PYSIDE6_IMPORT_ERROR:
            print(f"Import detail: {PYSIDE6_IMPORT_ERROR}", file=sys.stderr)
        return 2

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ImperiumOperatorWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
