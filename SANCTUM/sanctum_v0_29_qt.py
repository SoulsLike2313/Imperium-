from __future__ import annotations

import json
import math
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QPen,
    QBrush,
    QLinearGradient,
    QRadialGradient,
)
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QLineEdit,
    QVBoxLayout,
    QWidget,
    QFrame,
    QListWidgetItem,
)


APP_NAME = "IMPERIUM Sanctum v0.29 Qt — 60 FPS Command Dashboard"
IMPERIUM_ROOT = Path(r"E:\IMPERIUM")


COLORS = {
    "bg": QColor("#06111d"),
    "bg2": QColor("#081a2b"),
    "panel": QColor("#092033"),
    "panel2": QColor("#0d2b41"),
    "panel3": QColor("#123b58"),
    "panel4": QColor("#163d5b"),
    "line": QColor("#1c6c96"),
    "line_soft": QColor(28, 108, 150, 80),
    "line2": QColor("#28e8ff"),
    "line3": QColor("#7ffcff"),
    "text": QColor("#defcff"),
    "muted": QColor("#7eb8c7"),
    "muted2": QColor("#4d90a8"),
    "accent": QColor("#30f7ff"),
    "accent2": QColor("#7ffcff"),
    "good": QColor("#28ffb7"),
    "warn": QColor("#ffcf4a"),
    "bad": QColor("#ff5f86"),
    "core": QColor("#39ffbe"),
    "gold": QColor("#ffdd40"),
    "chip_bg": QColor("#0a1b2a"),
}


@dataclass
class TransferRoute:
    route_id: str = "PC_WINDOWS_TO_VM2_UBUNTU"
    ssh_user_host: str = "vboxuser2@127.0.0.1"
    ssh_port: str = "2223"
    ssh_key: Path = Path.home() / ".ssh" / "imperium_pc_to_vm2_ed25519_20260418"
    pc_prompt_outbox: Path = IMPERIUM_ROOT / "OUTBOX" / "VM2_PROMPTS"
    pc_bundle_inbox: Path = IMPERIUM_ROOT / "INBOX" / "VM2_BUNDLES"
    runtime_receipts: Path = IMPERIUM_ROOT / ".imperium_runtime" / "transfer" / "receipts"
    vm2_workdrop: str = "/home/vboxuser2/IMPERIUM_PRIVATE/WORKDROP"
    vm2_bundle_outbox: str = "/home/vboxuser2/IMPERIUM_PRIVATE/OUTBOX_BUNDLES"


class ReceiptWriter:
    def __init__(self, route: TransferRoute):
        self.route = route
        self.route.runtime_receipts.mkdir(parents=True, exist_ok=True)

    def write(self, action: str, status: str, details: dict) -> Path:
        payload = {
            "schema": "SANCTUM_QT_TRANSFER_RECEIPT_V1",
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "action": action,
            "status": status,
            "route_id": self.route.route_id,
            "pc_prompt_outbox": str(self.route.pc_prompt_outbox),
            "pc_bundle_inbox": str(self.route.pc_bundle_inbox),
            "vm2_workdrop": self.route.vm2_workdrop,
            "vm2_bundle_outbox": self.route.vm2_bundle_outbox,
            "details": details,
        }
        path = self.route.runtime_receipts / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{action}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return path


class TransferService:
    def __init__(self, route: TransferRoute):
        self.route = route
        self.receipts = ReceiptWriter(route)

    def ssh_base(self) -> list[str]:
        return [
            "ssh",
            "-i",
            str(self.route.ssh_key),
            "-p",
            self.route.ssh_port,
            self.route.ssh_user_host,
        ]

    def scp_base(self) -> list[str]:
        return [
            "scp",
            "-i",
            str(self.route.ssh_key),
            "-P",
            self.route.ssh_port,
        ]

    def run(self, args: list[str], action: str, timeout: int = 90) -> tuple[bool, subprocess.CompletedProcess | None]:
        try:
            result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
            ok = result.returncode == 0
            self.receipts.write(
                action,
                "PASS" if ok else "FAIL",
                {
                    "command": args,
                    "returncode": result.returncode,
                    "stdout_tail": result.stdout[-4000:],
                    "stderr_tail": result.stderr[-4000:],
                },
            )
            return ok, result
        except Exception as exc:
            self.receipts.write(action, "ERROR", {"command": args, "error": repr(exc)})
            return False, None

    def test_route(self) -> tuple[bool, str]:
        cmd = self.ssh_base() + [
            f"mkdir -p {self.route.vm2_workdrop} {self.route.vm2_bundle_outbox} && echo VM2_ROUTE_OK"
        ]
        ok, result = self.run(cmd, "test_route")
        if ok:
            return True, result.stdout.strip()
        return False, (result.stderr.strip() if result else "route error")

    def lock_route(self) -> tuple[bool, str]:
        ok, msg = self.test_route()
        if not ok:
            return False, msg

        lock_path = IMPERIUM_ROOT / ".imperium_runtime" / "transfer" / "VM2_ROUTE_LOCK.json"
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        lock_payload = {
            "route_id": self.route.route_id,
            "locked_at": datetime.now().isoformat(timespec="seconds"),
            "ssh_user_host": self.route.ssh_user_host,
            "ssh_port": self.route.ssh_port,
            "ssh_key_path": str(self.route.ssh_key),
            "pc_prompt_outbox": str(self.route.pc_prompt_outbox),
            "vm2_workdrop": self.route.vm2_workdrop,
            "vm2_bundle_outbox": self.route.vm2_bundle_outbox,
            "pc_bundle_inbox": str(self.route.pc_bundle_inbox),
            "secret_policy": "Path to private key only. Private key material is not stored in Git.",
        }
        lock_path.write_text(json.dumps(lock_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        self.receipts.write("lock_route", "PASS", {"lock_path": str(lock_path)})
        return True, str(lock_path)

    def safe_prompt_name(self, raw: str) -> str:
        value = (raw or "").strip() or "TASK-VM2-PROMPT"
        safe = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in value)
        if not safe.endswith(".txt"):
            safe += ".txt"
        return safe

    def send_prompt(self, prompt_name: str, prompt_text: str) -> tuple[bool, str]:
        self.route.pc_prompt_outbox.mkdir(parents=True, exist_ok=True)

        name = self.safe_prompt_name(prompt_name)
        local_file = self.route.pc_prompt_outbox / name
        remote_file = f"{self.route.vm2_workdrop}/{name}"

        local_file.write_text(prompt_text.strip() + "\n", encoding="utf-8")

        ok, result = self.run(self.ssh_base() + [f"mkdir -p {self.route.vm2_workdrop}"], "send_prompt_mkdir")
        if not ok:
            return False, result.stderr if result else "mkdir failed"

        ok, result = self.run(
            self.scp_base() + [str(local_file), f"{self.route.ssh_user_host}:{remote_file}"],
            "send_prompt_scp",
        )
        if not ok:
            return False, result.stderr if result else "scp failed"

        open_cmd = (
            "bash -lc '"
            "export DISPLAY=:0; "
            "export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus; "
            f"nohup xdg-open \"{remote_file}\" >/tmp/vm2_prompt_open.log 2>&1 &"
            "'"
        )
        ok_open, _ = self.run(self.ssh_base() + [open_cmd], "send_prompt_auto_open")

        self.receipts.write(
            "send_prompt",
            "PASS" if ok_open else "PASS_WITH_OPEN_WARNING",
            {
                "local_file": str(local_file),
                "remote_file": remote_file,
                "auto_open_ok": ok_open,
            },
        )
        return True, remote_file

    def list_bundles(self) -> list[str]:
        cmd = self.ssh_base() + [f"ls -t {self.route.vm2_bundle_outbox}/*.zip 2>/dev/null | head -100"]
        ok, result = self.run(cmd, "list_remote_bundles")
        if not ok or result is None:
            return []
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]

    def fetch_bundle(self, remote_bundle: str) -> tuple[bool, str]:
        self.route.pc_bundle_inbox.mkdir(parents=True, exist_ok=True)
        ok, result = self.run(
            self.scp_base() + [f"{self.route.ssh_user_host}:{remote_bundle}", str(self.route.pc_bundle_inbox) + "\\"],
            "fetch_bundle_zip",
            timeout=180,
        )
        if not ok:
            return False, result.stderr if result else "scp failed"

        self.run(
            self.scp_base() + [f"{self.route.ssh_user_host}:{remote_bundle}.sha256", str(self.route.pc_bundle_inbox) + "\\"],
            "fetch_bundle_sha256_optional",
            timeout=60,
        )

        self.receipts.write(
            "fetch_bundle",
            "PASS",
            {"remote_bundle": remote_bundle, "pc_bundle_inbox": str(self.route.pc_bundle_inbox)},
        )
        return True, str(self.route.pc_bundle_inbox)



class PlanetMapWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(980, 680)
        self.tick = 0.0

        # v0.29 visual/perf pass:
        # Do not let render complexity scale endlessly when the transfer panel is closed.
        # The scene is centered in a bounded command-map viewport.
        self.max_scene_width = 1080
        self.max_scene_height = 720

        self.setAttribute(Qt.WA_OpaquePaintEvent, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)

        self.timer = QTimer(self)
        self.timer.setTimerType(Qt.PreciseTimer)
        self.timer.timeout.connect(self.frame)
        self.timer.start(16)

        self.fps_timer = QTimer(self)
        self.fps_timer.timeout.connect(self.update_fps_label)
        self.fps_timer.start(1000)

        self.frame_count = 0
        self.current_fps = 0

    def frame(self):
        self.tick += 1.0
        self.frame_count += 1
        self.update()

    def update_fps_label(self):
        self.current_fps = self.frame_count
        self.frame_count = 0

    def draw_chip(self, painter: QPainter, rect: QRectF, label: str, value: str, accent: QColor):
        painter.setPen(QPen(COLORS["line"], 1))
        painter.setBrush(QBrush(COLORS["chip_bg"]))
        painter.drawRoundedRect(rect, 8, 8)

        painter.setPen(QPen(COLORS["muted"], 1))
        painter.setFont(QFont("Segoe UI", 8, QFont.Medium))
        painter.drawText(rect.adjusted(10, 6, -10, -22), Qt.AlignLeft | Qt.AlignTop, label.upper())

        painter.setPen(QPen(accent, 1))
        painter.setFont(QFont("Segoe UI", 13, QFont.Bold))
        painter.drawText(rect.adjusted(10, 20, -10, -7), Qt.AlignLeft | Qt.AlignBottom, value)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        w = self.width()
        h = self.height()

        bg = QLinearGradient(0, 0, w, h)
        bg.setColorAt(0.0, QColor("#06101a"))
        bg.setColorAt(0.42, QColor("#081827"))
        bg.setColorAt(1.0, QColor("#050c15"))
        painter.fillRect(self.rect(), bg)

        scene_w = min(w - 28, self.max_scene_width)
        scene_h = min(h - 28, self.max_scene_height)
        scene_x = (w - scene_w) / 2
        scene_y = 14
        outer = QRectF(scene_x, scene_y, scene_w, scene_h)

        # side dark margins when transfer panel is closed and viewport becomes huge
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(2, 8, 14, 90)))
        if scene_x > 20:
            painter.drawRect(QRectF(0, 0, scene_x - 8, h))
            painter.drawRect(QRectF(scene_x + scene_w + 8, 0, w - scene_x - scene_w - 8, h))

        frame_grad = QLinearGradient(outer.left(), outer.top(), outer.left(), outer.bottom())
        frame_grad.setColorAt(0.0, QColor("#0a2233"))
        frame_grad.setColorAt(1.0, QColor("#07131f"))
        painter.setPen(QPen(COLORS["line"], 1))
        painter.setBrush(QBrush(frame_grad))
        painter.drawRoundedRect(outer, 14, 14)

        inner = outer.adjusted(12, 12, -12, -12)
        painter.setPen(QPen(QColor(38, 145, 198, 90), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(inner, 12, 12)

        # Static grid only inside bounded scene
        painter.setClipRect(inner)
        painter.setPen(QPen(QColor(32, 86, 110, 34), 1))
        step = 38
        x0 = int(inner.left()) - (int(inner.left()) % step)
        y0 = int(inner.top()) - (int(inner.top()) % step)
        for x in range(x0, int(inner.right()), step):
            painter.drawLine(x, int(inner.top()), x, int(inner.bottom()))
        for y in range(y0, int(inner.bottom()), step):
            painter.drawLine(int(inner.left()), y, int(inner.right()), y)
        painter.setClipping(False)

        title_rect = QRectF(inner.left() + 18, inner.top() + 14, 450, 38)
        painter.setPen(QPen(COLORS["accent2"], 1))
        painter.setFont(QFont("Segoe UI Semibold", 13))
        painter.drawText(title_rect, Qt.AlignLeft | Qt.AlignVCenter, "MISSION CONTROL CORE")

        sub_rect = QRectF(inner.left() + 18, inner.top() + 42, 600, 26)
        painter.setPen(QPen(COLORS["muted"], 1))
        painter.setFont(QFont("Segoe UI", 8))
        painter.drawText(
            sub_rect,
            Qt.AlignLeft | Qt.AlignVCenter,
            "TASK-20260509-SANCTUM-V0_1-OWNER-ACCEPTABLE-VERSION-ACTIVE-V1",
        )

        chip_y = inner.top() + 64
        chip_w = 102
        chip_h = 52
        chip_gap = 9
        chip_x = inner.left() + 18
        chips = [
            ("Stages", "6", COLORS["accent2"]),
            ("Pass", "1", COLORS["good"]),
            ("Active", "1", COLORS["accent"]),
            ("Planned", "4", COLORS["warn"]),
            ("Block", "0", COLORS["bad"]),
            ("Readiness", "25%", COLORS["warn"]),
            ("Risk", "0%", COLORS["accent"]),
        ]
        for label, value, accent in chips:
            self.draw_chip(painter, QRectF(chip_x, chip_y, chip_w, chip_h), label, value, accent)
            chip_x += chip_w + chip_gap

        map_rect = QRectF(inner.left() + 18, inner.top() + 132, inner.width() - 36, inner.height() - 180)
        painter.setPen(QPen(QColor(24, 116, 156, 120), 1))
        painter.setBrush(QBrush(QColor(4, 16, 28, 210)))
        painter.drawRoundedRect(map_rect, 12, 12)

        cx = map_rect.center().x()
        cy = map_rect.center().y() + 2
        radius = min(map_rect.width(), map_rect.height()) * 0.245

        # FPS
        painter.setPen(QPen(COLORS["warn"], 1))
        painter.setFont(QFont("Consolas", 11, QFont.Bold))
        painter.drawText(int(map_rect.right()) - 102, int(map_rect.top()) + 28, f"FPS {self.current_fps:02d}")

        # Central glow
        glow = QRadialGradient(QPointF(cx, cy), radius * 1.85)
        glow.setColorAt(0.0, QColor(57, 255, 190, 100))
        glow.setColorAt(0.15, QColor(40, 210, 225, 55))
        glow.setColorAt(0.45, QColor(20, 110, 160, 22))
        glow.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(glow))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QRectF(cx - radius * 1.85, cy - radius * 1.85, radius * 3.7, radius * 3.7))

        # Organ orbit system: clear orbital rings around the core
        painter.setBrush(Qt.NoBrush)
        orbit_specs = [
            (0.78, QColor(45, 232, 255, 88), 1.2),
            (1.02, QColor(45, 232, 255, 62), 1.0),
            (1.28, QColor(255, 221, 64, 48), 1.0),
            (1.52, QColor(45, 232, 255, 34), 1.0),
        ]
        for scale, color, width_pen in orbit_specs:
            rr = radius * scale
            painter.setPen(QPen(color, width_pen))
            painter.save()
            painter.translate(cx, cy)
            painter.scale(1.0, 0.64)
            painter.drawEllipse(QRectF(-rr, -rr, rr * 2, rr * 2))
            painter.restore()

        # orbital longitude/latitude arcs for planet feeling
        painter.setPen(QPen(QColor(112, 252, 255, 50), 1))
        for tilt in [-0.58, -0.28, 0.0, 0.28, 0.58]:
            painter.save()
            painter.translate(cx, cy)
            painter.rotate(math.degrees(tilt))
            painter.scale(1.0, 0.30)
            painter.drawEllipse(QRectF(-radius * 0.82, -radius * 0.82, radius * 1.64, radius * 1.64))
            painter.restore()

        painter.setPen(QPen(QColor(112, 252, 255, 38), 1))
        for i in range(8):
            a = i * math.tau / 8 + self.tick * 0.002
            x = cx + math.cos(a) * radius * 1.55
            y = cy + math.sin(a) * radius * 1.55 * 0.64
            painter.drawLine(int(cx), int(cy), int(x), int(y))

        # dynamic defensive lattice around the planet
        painter.setPen(QPen(COLORS["line2"], 2))
        pts = []
        count = 12
        for i in range(count):
            a = self.tick * 0.018 + i * (math.tau / count)
            rr = radius * (0.88 + 0.13 * math.sin(self.tick * 0.032 + i * 1.31))
            x = cx + math.cos(a) * rr
            y = cy + math.sin(a) * rr * 0.52
            pts.append(QPointF(x, y))
        for i in range(count):
            painter.drawLine(pts[i], pts[(i + 4) % count])

        painter.setPen(QPen(QColor(127, 252, 255, 125), 1))
        pts2 = []
        count2 = 10
        for i in range(count2):
            a = -self.tick * 0.014 + i * (math.tau / count2)
            rr = radius * (0.64 + 0.09 * math.cos(self.tick * 0.027 + i))
            x = cx + math.cos(a) * rr
            y = cy + math.sin(a) * rr * 0.47
            pts2.append(QPointF(x, y))
        for i in range(count2):
            painter.drawLine(pts2[i], pts2[(i + 3) % count2])

        # moving particles, reduced count for performance but visually even
        for ring_idx, scale in enumerate([0.78, 1.02, 1.28, 1.52]):
            particle_count = 10 if ring_idx < 2 else 8
            for i in range(particle_count):
                a = self.tick * (0.010 + ring_idx * 0.0025) + i * (math.tau / particle_count)
                rr = radius * scale
                x = cx + math.cos(a) * rr
                y = cy + math.sin(a) * rr * 0.64
                r = 2.2 + ring_idx * 0.25
                color = QColor(127, 252, 255, 155 - ring_idx * 22)
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(color))
                painter.drawEllipse(QRectF(x - r, y - r, r * 2, r * 2))

        # real central planet: layered sphere + equator + meridians
        planet_r = 42
        planet_glow = QRadialGradient(QPointF(cx - 10, cy - 12), planet_r * 1.35)
        planet_glow.setColorAt(0.0, QColor("#b8fff2"))
        planet_glow.setColorAt(0.22, QColor("#55ffd1"))
        planet_glow.setColorAt(0.55, QColor("#20cfa8"))
        planet_glow.setColorAt(1.0, QColor("#0b6f70"))

        painter.setPen(Qt.NoPen)
        for gr, alpha in [(78, 24), (61, 42), (51, 70)]:
            painter.setBrush(QBrush(QColor(57, 255, 190, alpha)))
            painter.drawEllipse(QRectF(cx - gr, cy - gr, gr * 2, gr * 2))

        painter.setBrush(QBrush(planet_glow))
        painter.setPen(QPen(QColor(165, 255, 238, 180), 1.5))
        painter.drawEllipse(QRectF(cx - planet_r, cy - planet_r, planet_r * 2, planet_r * 2))

        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(8, 80, 86, 90), 1))
        for j in [-0.45, -0.2, 0.0, 0.2, 0.45]:
            painter.save()
            painter.translate(cx, cy)
            painter.scale(1.0, 0.28 + abs(j) * 0.2)
            painter.drawEllipse(QRectF(-planet_r * 0.85, -planet_r * (0.38 + abs(j)), planet_r * 1.7, planet_r * (0.76 + abs(j) * 2)))
            painter.restore()

        painter.setPen(QPen(QColor(210, 255, 245, 65), 1))
        painter.drawArc(QRectF(cx - planet_r * 0.8, cy - planet_r * 0.18, planet_r * 1.6, planet_r * 0.36), 0, 360 * 16)

        highlight = QRadialGradient(QPointF(cx - 16, cy - 18), 24)
        highlight.setColorAt(0.0, QColor(255, 255, 255, 110))
        highlight.setColorAt(0.6, QColor(255, 255, 255, 22))
        highlight.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(highlight))
        painter.drawEllipse(QRectF(cx - 35, cy - 34, 38, 32))

        # organs on clearly separated orbit lanes
        organs = [
            ("ASTRA", -math.pi / 2, COLORS["good"], 1.52),
            ("ADMINISTRATUM", 0.0, COLORS["gold"], 1.48),
            ("MECHANICUS", math.pi * 0.30, COLORS["gold"], 1.42),
            ("INQUISITION", math.pi / 2, COLORS["gold"], 1.30),
            ("PC", math.pi * 0.86, COLORS["accent2"], 1.46),
            ("SPECULUM", math.pi * 1.18, COLORS["gold"], 1.40),
        ]

        painter.setFont(QFont("Segoe UI Semibold", 8))
        for idx, (label, base_a, color, lane) in enumerate(organs):
            pulse = math.sin(self.tick * 0.035 + idx * 0.9)
            a = base_a + pulse * 0.035
            rr = radius * lane
            x = cx + math.cos(a) * rr
            y = cy + math.sin(a) * rr * 0.64

            painter.setPen(QPen(QColor(23, 96, 132, 100), 1))
            painter.drawLine(int(cx), int(cy), int(x), int(y))

            halo_r = 19 + pulse * 1.5
            painter.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 205), 2))
            painter.setBrush(QBrush(QColor(8, 18, 28, 220)))
            painter.drawEllipse(QRectF(x - halo_r, y - halo_r, halo_r * 2, halo_r * 2))

            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(color.red(), color.green(), color.blue(), 42)))
            painter.drawEllipse(QRectF(x - 28, y - 28, 56, 56))

            painter.setBrush(QBrush(color))
            painter.drawEllipse(QRectF(x - 7, y - 7, 14, 14))

            label_w = max(78, len(label) * 7 + 18)
            label_rect = QRectF(x - label_w / 2, y + 18, label_w, 19)
            painter.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 120), 1))
            painter.setBrush(QBrush(QColor(5, 18, 28, 210)))
            painter.drawRoundedRect(label_rect, 6, 6)
            painter.setPen(QPen(color, 1))
            painter.drawText(label_rect, Qt.AlignCenter, label)

        # footer cards
        law_card = QRectF(map_rect.left() + 20, map_rect.bottom() - 88, min(450, map_rect.width() * 0.45), 66)
        painter.setPen(QPen(COLORS["line"], 1))
        painter.setBrush(QBrush(QColor(8, 20, 32, 220)))
        painter.drawRoundedRect(law_card, 8, 8)
        painter.setPen(QPen(COLORS["accent2"], 1))
        painter.setFont(QFont("Segoe UI Semibold", 9))
        painter.drawText(law_card.adjusted(14, 9, -14, -36), Qt.AlignLeft | Qt.AlignTop, "STAGE LOOP LAW")
        painter.setPen(QPen(COLORS["text"], 1))
        painter.setFont(QFont("Consolas", 8))
        painter.drawText(
            law_card.adjusted(14, 29, -14, -8),
            Qt.AlignLeft | Qt.AlignTop,
            "1. PREFLIGHT → 2. MAP → 3. WORK_PACKET → 4. EXECUTE → 5. RECEIPT"
        )

        action_card = QRectF(law_card.right() + 14, map_rect.bottom() - 88, map_rect.right() - law_card.right() - 34, 66)
        if action_card.width() > 260:
            painter.setPen(QPen(COLORS["line"], 1))
            painter.setBrush(QBrush(QColor(8, 20, 32, 220)))
            painter.drawRoundedRect(action_card, 8, 8)
            painter.setPen(QPen(COLORS["muted"], 1))
            painter.setFont(QFont("Segoe UI", 9))
            painter.drawText(action_card.adjusted(14, 9, -14, -36), Qt.AlignLeft | Qt.AlignTop, "NEXT ALLOWED ACTION")
            painter.setPen(QPen(COLORS["text"], 1))
            painter.setFont(QFont("Consolas", 9, QFont.Bold))
            painter.drawText(action_card.adjusted(14, 27, -14, -8), Qt.AlignLeft | Qt.AlignTop, "CONTINUE_SANCTUM_ITERATION")


class TransferPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.route = TransferRoute()
        self.service = TransferService(self.route)

        self.setStyleSheet("""
            QFrame {
                background: #0a1f31;
                border: 1px solid #1f6d95;
                border-radius: 10px;
            }
            QLabel {
                color: #dffcff;
                font-family: Segoe UI;
                border: none;
            }
            QLineEdit, QTextEdit, QListWidget {
                background: #0d2a40;
                color: #defcff;
                border: 1px solid #206f98;
                border-radius: 8px;
                padding: 6px;
                font-family: Consolas;
                selection-background-color: #25dfff;
                selection-color: #07111d;
            }
            QPushButton {
                background: #15405f;
                color: #e7fdff;
                border: 1px solid #2378a2;
                border-radius: 8px;
                padding: 8px;
                font-family: Segoe UI Semibold;
                font-size: 9pt;
            }
            QPushButton:hover {
                background: #1a5377;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        title = QLabel("TRANSFER CONTROL  —  PC ⇄ VM2")
        title.setFont(QFont("Segoe UI Semibold", 12))
        layout.addWidget(title)

        self.route_label = QLabel("Route: PC_WINDOWS → VM2_UBUNTU | unlocked")
        self.route_label.setFont(QFont("Consolas", 9))
        layout.addWidget(self.route_label)

        caption = QLabel("Prompt file name")
        caption.setFont(QFont("Segoe UI", 9))
        layout.addWidget(caption)

        self.prompt_name = QLineEdit("TASK-VM2-PROMPT")
        layout.addWidget(self.prompt_name)

        self.prompt_text = QTextEdit()
        self.prompt_text.setPlainText(
            "FINAL RESPONSE FORMAT:\n"
            "Reply only with:\n"
            "STEP_NAME: <short step name>\n"
            "BUNDLE_PATH: <absolute VM2 bundle path>\n\n"
        )
        layout.addWidget(self.prompt_text, 2)

        row1 = QHBoxLayout()
        self.btn_test = QPushButton("Test Route")
        self.btn_lock = QPushButton("Lock Route")
        self.btn_send = QPushButton("Send Prompt + Auto Open")
        row1.addWidget(self.btn_test)
        row1.addWidget(self.btn_lock)
        row1.addWidget(self.btn_send)
        layout.addLayout(row1)

        section = QLabel("VM2 Remote Bundles")
        section.setFont(QFont("Segoe UI Semibold", 10))
        layout.addWidget(section)

        self.bundle_list = QListWidget()
        self.bundle_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        layout.addWidget(self.bundle_list, 1)

        row2 = QHBoxLayout()
        self.btn_refresh = QPushButton("Refresh Bundles")
        self.btn_fetch = QPushButton("Fetch Selected")
        self.btn_fetch_latest = QPushButton("Fetch Latest")
        row2.addWidget(self.btn_refresh)
        row2.addWidget(self.btn_fetch)
        row2.addWidget(self.btn_fetch_latest)
        layout.addLayout(row2)

        self.status = QLabel("Ready.")
        self.status.setFont(QFont("Consolas", 9))
        layout.addWidget(self.status)

        self.btn_test.clicked.connect(self.test_route)
        self.btn_lock.clicked.connect(self.lock_route)
        self.btn_send.clicked.connect(self.send_prompt)
        self.btn_refresh.clicked.connect(self.refresh_bundles)
        self.btn_fetch.clicked.connect(self.fetch_selected)
        self.btn_fetch_latest.clicked.connect(self.fetch_latest)

    def info(self, title: str, text: str):
        QMessageBox.information(self, title, text)

    def warn(self, title: str, text: str):
        QMessageBox.warning(self, title, text)

    def test_route(self):
        ok, msg = self.service.test_route()
        self.status.setText(msg)
        if ok:
            self.route_label.setText("Route: PC_WINDOWS → VM2_UBUNTU | tested")
            self.info("Route", "Route test PASS.")
        else:
            self.warn("Route", msg)

    def lock_route(self):
        ok, msg = self.service.lock_route()
        self.status.setText(msg)
        if ok:
            self.route_label.setText("Route: PC_WINDOWS → VM2_UBUNTU | LOCKED")
            self.info("Route lock", f"Route locked:\n{msg}")
        else:
            self.warn("Route lock", msg)

    def send_prompt(self):
        text = self.prompt_text.toPlainText().strip()
        if not text:
            self.warn("Send prompt", "Prompt is empty.")
            return
        ok, msg = self.service.send_prompt(self.prompt_name.text(), text)
        self.status.setText(msg)
        if ok:
            self.info("Send prompt", f"Prompt sent:\n{msg}")
        else:
            self.warn("Send prompt", msg)

    def refresh_bundles(self):
        self.bundle_list.clear()
        bundles = self.service.list_bundles()
        for idx, remote_path in enumerate(bundles):
            name = Path(remote_path).name
            if idx == 0:
                label = f"[NEWEST] {name}"
            elif idx < 3:
                label = f"[RECENT] {name}"
            else:
                label = f"[OLDER]  {name}"

            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, remote_path)
            item.setToolTip(remote_path)

            if idx == 0:
                item.setBackground(QColor("#55ffd8"))
                item.setForeground(QColor("#07111d"))
            elif idx < 3:
                item.setBackground(QColor("#11384f"))
                item.setForeground(QColor("#9ef8ff"))
            else:
                item.setBackground(QColor("#0d2234"))
                item.setForeground(QColor("#6fb4c7"))

            self.bundle_list.addItem(item)

        self.status.setText(f"Bundles: {len(bundles)}")

    def fetch_selected(self):
        item = self.bundle_list.currentItem()
        if not item:
            self.warn("Fetch", "Select bundle first.")
            return
        remote_bundle = item.data(Qt.UserRole) or item.text()
        ok, msg = self.service.fetch_bundle(remote_bundle)
        self.status.setText(msg)
        if ok:
            self.info("Fetch", f"Fetched to:\n{msg}")
        else:
            self.warn("Fetch", msg)

    def fetch_latest(self):
        self.refresh_bundles()
        if self.bundle_list.count() == 0:
            self.warn("Fetch latest", "No bundles found.")
            return
        self.bundle_list.setCurrentRow(0)
        self.fetch_selected()


class SanctumMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1820, 1020)
        self.setStyleSheet("""
            QMainWindow {
                background: #06111d;
            }
            QLabel {
                color: #defcff;
                font-family: Segoe UI;
            }
            QPushButton {
                background: #143f5d;
                color: #e6fdff;
                border: 1px solid #2378a2;
                border-radius: 8px;
                padding: 8px 10px;
                font-family: Segoe UI Semibold;
                font-size: 9pt;
            }
            QPushButton:hover {
                background: #1b5679;
            }
            QListWidget {
                background: #0a1f31;
                color: #defcff;
                border: 1px solid #206e97;
                border-radius: 8px;
                padding: 6px;
                font-family: Consolas;
            }
        """)

        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)
        self.setCentralWidget(central)

        top_wrap = QFrame()
        top_wrap.setStyleSheet("QFrame { background: #081a2a; border: 1px solid #1f6c94; border-radius: 10px; }")
        top_layout = QHBoxLayout(top_wrap)
        top_layout.setContentsMargins(10, 8, 10, 8)
        top_layout.setSpacing(8)
        root.addWidget(top_wrap)

        self.btn_astra = QPushButton("Open Astra Utility")
        self.btn_explorer = QPushButton("Open Explorer")
        self.btn_task_folder = QPushButton("Open Task Folder")
        self.btn_notes = QPushButton("Open Notes")
        self.btn_refresh_tasks = QPushButton("Refresh Tasks")

        for btn in [
            self.btn_astra,
            self.btn_explorer,
            self.btn_task_folder,
            self.btn_notes,
            self.btn_refresh_tasks,
        ]:
            top_layout.addWidget(btn)

        self.btn_astra.clicked.connect(self.open_astra_utility)
        self.btn_explorer.clicked.connect(self.open_explorer_area)
        self.btn_task_folder.clicked.connect(self.open_selected_task_folder)
        self.btn_notes.clicked.connect(self.open_notes_area)
        self.btn_refresh_tasks.clicked.connect(self.refresh_tasks)

        self.transfer_button = QPushButton("Transfer Control")
        top_layout.addWidget(self.transfer_button)

        top_layout.addSpacing(14)
        selected = QLabel("Selected task: TASK-20260509-SANCTUM-V0_1-OWNER-ACCEPTABLE-VERSION-ACTIVE-V1")
        selected.setFont(QFont("Consolas", 10, QFont.Bold))
        top_layout.addWidget(selected, 1)

        splitter = QSplitter(Qt.Horizontal)
        root.addWidget(splitter, 1)

        left = QFrame()
        left.setStyleSheet("""
            QFrame { background: #0a1f31; border: 1px solid #1f6d95; border-radius: 10px; }
            QLabel { border: none; }
        """)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(8)

        left_title = QLabel("ACTIVE TASK")
        left_title.setFont(QFont("Segoe UI Semibold", 11))
        left_layout.addWidget(left_title)

        active = QLabel(
            "TASK-20260509-SANCTUM-V0_1-OWNER-ACCEPTABLE-VERSION-ACTIVE-V1\n\n"
            "route_status: ACTIVE_OWNER_MANUAL_BUILD\n"
            "current_stage: PC-STAGE-001"
        )
        active.setStyleSheet("""
            background: #14334b;
            border: 1px solid #236f98;
            border-radius: 8px;
            padding: 12px;
        """)
        active.setFont(QFont("Consolas", 9))
        active.setWordWrap(True)
        left_layout.addWidget(active)

        tasks_label = QLabel("Astronomicon Tasks")
        tasks_label.setFont(QFont("Segoe UI Semibold", 10))
        left_layout.addWidget(tasks_label)

        self.task_list = QListWidget()
        left_layout.addWidget(self.task_list, 1)
        self.refresh_tasks()

        self.map_widget = PlanetMapWidget()
        self.transfer_panel = TransferPanel()
        self.transfer_panel.setVisible(True)

        splitter.addWidget(left)
        splitter.addWidget(self.map_widget)
        splitter.addWidget(self.transfer_panel)
        splitter.setSizes([360, 1040, 420])

        self.splitter = splitter
        self.transfer_button.clicked.connect(self.toggle_transfer)

    def open_path(self, target: Path, label: str = "path"):
        try:
            target = Path(target)
            if not target.exists():
                QMessageBox.warning(self, "Open path", f"Missing {label}:\n{target}")
                return
            subprocess.Popen(["explorer.exe", str(target)])
        except Exception as exc:
            QMessageBox.warning(self, "Open path", f"Failed to open {label}:\n{target}\n\n{exc}")

    def open_astra_utility(self):
        # Minimal practical behavior for Qt shell:
        # open Astronomicon/Astra area. Later this can launch a dedicated Astra utility.
        self.open_path(IMPERIUM_ROOT / "ASTRONOMICON", "Astronomicon / Astra area")

    def open_explorer_area(self):
        self.open_path(IMPERIUM_ROOT / "EXPLORER", "Explorer area")

    def open_notes_area(self):
        notes = IMPERIUM_ROOT / "CHAT_COMPILATIONS_LOCAL"
        if not notes.exists():
            notes = IMPERIUM_ROOT / "DOCS"
        self.open_path(notes, "Notes area")

    def selected_task_id(self) -> str | None:
        item = self.task_list.currentItem()
        if item:
            return item.text().strip()
        if self.task_list.count() > 0:
            return self.task_list.item(0).text().strip()
        return None

    def open_selected_task_folder(self):
        task_id = self.selected_task_id()
        artifacts_root = IMPERIUM_ROOT / "ARTIFACTS"
        if not task_id:
            self.open_path(artifacts_root, "Artifacts root")
            return

        task_path = artifacts_root / task_id
        if task_path.exists():
            self.open_path(task_path, "selected task folder")
        else:
            QMessageBox.information(
                self,
                "Task folder",
                f"No exact artifact folder found for:\n{task_id}\n\nOpening ARTIFACTS root instead.",
            )
            self.open_path(artifacts_root, "Artifacts root")

    def refresh_tasks(self):
        try:
            artifacts_root = IMPERIUM_ROOT / "ARTIFACTS"
            self.task_list.clear()

            if artifacts_root.exists():
                task_dirs = sorted(
                    [p.name for p in artifacts_root.iterdir() if p.is_dir() and p.name.startswith("TASK-")],
                    reverse=True,
                )
            else:
                task_dirs = []

            fallback = [
                "TASK-20260509-SANCTUM-V0_1-OWNER-ACCEPTABLE-VERSION-ACTIVE-V1",
                "TASK-20260511-VM2-UBUNTU-CONTOUR-ONBOARDING",
                "TASK-20260511-SANCTUM-QT-60FPS-SHELL",
                "TASK-20260511-SANCTUM-V0_28-TRANSFER-CONTROL",
            ]

            for name in task_dirs or fallback:
                self.task_list.addItem(name)

            if self.task_list.count() > 0:
                self.task_list.setCurrentRow(0)
        except Exception as exc:
            QMessageBox.warning(self, "Refresh Tasks", f"Failed to refresh tasks:\n{exc}")

    def toggle_transfer(self):
        visible = not self.transfer_panel.isVisible()
        self.transfer_panel.setVisible(visible)
        if visible:
            self.splitter.setSizes([340, 980, 430])
        else:
            self.splitter.setSizes([360, 1400, 0])


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    window = SanctumMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
