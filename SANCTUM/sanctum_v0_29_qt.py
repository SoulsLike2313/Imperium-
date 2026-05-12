from __future__ import annotations

import json
import math
import hashlib
import shlex
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

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
    QDialog,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QTabWidget,
    QLineEdit,
    QVBoxLayout,
    QWidget,
    QFrame,
    QListWidgetItem,
)

from sanctum_git_cli_check_service_v0_1 import GitCliCheckService, GitCliCheckServiceError


APP_NAME = "IMPERIUM Sanctum v0.30 Adaptive Operator Dashboard"
APP_LAYER_LABEL = "Sanctum v0.30 UI shell + Adaptive Operator Layer v0.1"
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
    vm2_bundle_outbox: str = "/home/vboxuser2/IMPERIUM_WORK/_handoff_out"
    vm2_bundle_outbox_fallback: str = "/home/vboxuser2/IMPERIUM_PRIVATE/OUTBOX"


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
            "vm2_bundle_outbox_fallback": self.route.vm2_bundle_outbox_fallback,
            "details": details,
        }
        path = self.route.runtime_receipts / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{action}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return path


class TransferService:
    def __init__(self, route: TransferRoute):
        self.route = route
        self.receipts = ReceiptWriter(route)
        self.last_bundle_list_error = ""

    def _host_is_windows(self) -> bool:
        return sys.platform.startswith("win")

    def _pc_inbox_scp_target(self) -> str:
        return str(self.route.pc_bundle_inbox).replace("\\", "/")

    def _bundle_dirs(self) -> list[str]:
        dirs = [self.route.vm2_bundle_outbox, self.route.vm2_bundle_outbox_fallback]
        out: list[str] = []
        for item in dirs:
            if item and item not in out:
                out.append(item)
        return out

    def _sha256_path(self, file_path: Path) -> str:
        digest = hashlib.sha256()
        with file_path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _parse_expected_sha(self, sha_path: Path) -> str:
        raw = sha_path.read_text(encoding="utf-8", errors="replace").strip()
        return raw.split()[0] if raw else ""

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
        bundle_dirs = " ".join(shlex.quote(item) for item in self._bundle_dirs())
        cmd = self.ssh_base() + ["bash", "-lc", f"mkdir -p {shlex.quote(self.route.vm2_workdrop)} {bundle_dirs} && echo VM2_ROUTE_OK"]
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
            "vm2_bundle_outbox_fallback": self.route.vm2_bundle_outbox_fallback,
            "vm2_bundle_outboxes": self._bundle_dirs(),
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

    def list_bundles(self) -> list[dict[str, Any]]:
        dirs = self._bundle_dirs()
        quoted_dirs = " ".join(shlex.quote(item) for item in dirs)
        remote_cmd = (
            "set -euo pipefail; "
            f"for d in {quoted_dirs}; do "
            "[ -d \"$d\" ] || continue; "
            "while IFS= read -r -d '' f; do "
            "ts=$(stat -c %Y \"$f\" 2>/dev/null || echo 0); "
            "sz=$(stat -c %s \"$f\" 2>/dev/null || echo 0); "
            "if [ -f \"$f.sha256\" ]; then sha=1; else sha=0; fi; "
            "printf \"%s|%s|%s|%s\\n\" \"$ts\" \"$sz\" \"$f\" \"$sha\"; "
            "done < <(find \"$d\" -maxdepth 1 -type f -name '*.zip' -print0); "
            "done | sort -t'|' -k1,1nr | head -100"
        )
        cmd = self.ssh_base() + ["bash", "-lc", remote_cmd]
        ok, result = self.run(cmd, "list_remote_bundles")
        if not ok or result is None:
            self.last_bundle_list_error = (
                result.stderr.strip() if result and result.stderr else "remote bundle list unavailable"
            )
            return []

        self.last_bundle_list_error = ""
        bundles: list[dict[str, Any]] = []
        for line in result.stdout.splitlines():
            parts = line.strip().split("|", 3)
            if len(parts) != 4:
                continue
            ts_raw, size_raw, remote_path, sha_raw = parts
            try:
                ts = int(float(ts_raw))
            except ValueError:
                ts = 0
            try:
                size = int(size_raw)
            except ValueError:
                size = 0
            modified = datetime.utcfromtimestamp(ts).isoformat() + "Z" if ts > 0 else "UNKNOWN"
            bundles.append(
                {
                    "remote_path": remote_path,
                    "name": Path(remote_path).name,
                    "modified_epoch": ts,
                    "modified_utc": modified,
                    "size_bytes": size,
                    "sha256_remote_present": sha_raw == "1",
                }
            )
        return bundles

    def fetch_bundle(self, remote_bundle: str) -> tuple[bool, str]:
        if not self._host_is_windows():
            command_hint = (
                "powershell -ExecutionPolicy Bypass -NoProfile -File "
                "E:\\IMPERIUM\\TOOLS\\review_worker_bundle_intake.ps1 "
                f"-Bundle \"E:\\IMPERIUM\\INBOX\\VM2_BUNDLES\\{Path(remote_bundle).name}\" "
                "-RepoRoot \"E:\\IMPERIUM\" -IncomingRoot \"E:\\IMPERIUM_LOCAL_HANDOFF\\BUNDLE_INTAKE\" -NoApply"
            )
            self.receipts.write(
                "fetch_bundle",
                "COMMAND_PREP_ONLY",
                {"remote_bundle": remote_bundle, "reason": "non_windows_contour", "command_hint": command_hint},
            )
            return False, (
                "COMMAND_PREP_ONLY: PC fetch недоступен на non-Windows контуре.\n"
                f"Use on PC:\n{command_hint}"
            )

        self.route.pc_bundle_inbox.mkdir(parents=True, exist_ok=True)
        inbox_target = self._pc_inbox_scp_target()
        ok, result = self.run(
            self.scp_base() + [f"{self.route.ssh_user_host}:{remote_bundle}", inbox_target],
            "fetch_bundle_zip",
            timeout=180,
        )
        if not ok:
            return False, (result.stderr.strip() if result and result.stderr else "scp zip fetch failed")

        ok_sha, _ = self.run(
            self.scp_base() + [f"{self.route.ssh_user_host}:{remote_bundle}.sha256", inbox_target],
            "fetch_bundle_sha256_optional",
            timeout=60,
        )

        local_zip = self.route.pc_bundle_inbox / Path(remote_bundle).name
        local_sha = local_zip.with_suffix(local_zip.suffix + ".sha256")
        sha_status = "SHA_MISSING"
        sha_details: dict[str, Any] = {"sha_file_present": local_sha.exists(), "sha_copy_ok": ok_sha}
        if local_sha.exists() and local_zip.exists():
            expected = self._parse_expected_sha(local_sha)
            actual = self._sha256_path(local_zip)
            sha_details["expected_sha256"] = expected
            sha_details["actual_sha256"] = actual
            if expected and expected == actual:
                sha_status = "SHA_PASS"
            elif expected:
                sha_status = "SHA_FAIL"
            else:
                sha_status = "UNKNOWN"

        receipt_status = "PASS"
        if sha_status == "SHA_FAIL":
            receipt_status = "FAIL"
        elif sha_status in {"SHA_MISSING", "UNKNOWN"}:
            receipt_status = "PASS_WITH_WARNINGS"
        self.receipts.write(
            "fetch_bundle",
            receipt_status,
            {
                "remote_bundle": remote_bundle,
                "pc_bundle_inbox": str(self.route.pc_bundle_inbox),
                "sha_status": sha_status,
                "sha_details": sha_details,
            },
        )
        if sha_status == "SHA_FAIL":
            return (
                False,
                "BLOCKED SHA_FAIL: fetched zip, but local sha256 verification failed.\n"
                f"zip={local_zip}\nsha={local_sha}",
            )
        if sha_status == "SHA_PASS":
            return True, f"FETCHED + SHA_PASS\nzip={local_zip}\nsha={local_sha}"
        if sha_status == "SHA_MISSING":
            return True, f"FETCHED + SHA_MISSING\nzip={local_zip}"
        return True, f"FETCHED + UNKNOWN_SHA\nzip={local_zip}\nsha={local_sha}"



class PlanetMapWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(760, 560)
        self.tick = 0.0
        self.state_snapshot: dict[str, Any] | None = None

        # v0.29 visual/perf pass:
        # Do not let render complexity scale endlessly when the transfer panel is closed.
        # The scene is centered in a bounded command-map viewport.
        self.max_scene_width = 1180
        self.max_scene_height = 760

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

    def set_runtime_state(self, state: dict[str, Any] | None) -> None:
        self.state_snapshot = state if isinstance(state, dict) else None
        self.update()

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
        painter.drawText(title_rect, Qt.AlignLeft | Qt.AlignVCenter, "ADAPTIVE OPERATOR CORE")

        sub_rect = QRectF(inner.left() + 18, inner.top() + 42, 600, 26)
        painter.setPen(QPen(COLORS["muted"], 1))
        painter.setFont(QFont("Segoe UI", 8))
        if isinstance(self.state_snapshot, dict):
            git_truth = self.state_snapshot.get("git_truth", {})
            generated = str(self.state_snapshot.get("generated_at_utc", "unknown"))
            head = str(git_truth.get("local_head", ""))[:7] or "UNKNOWN"
            verdict = str(self.state_snapshot.get("verdict", "UNKNOWN"))
            sub_text = f"STATE {verdict} | HEAD {head} | generated {generated}"
        else:
            sub_text = "STATE UNKNOWN | run Refresh State to bind live truth"
        painter.drawText(sub_rect, Qt.AlignLeft | Qt.AlignVCenter, sub_text)

        chip_y = inner.top() + 64
        chip_w = 102
        chip_h = 52
        chip_gap = 9
        chip_x = inner.left() + 18
        chips = [
            ("State", "UNKNOWN", COLORS["warn"]),
            ("Git", "UNKNOWN", COLORS["warn"]),
            ("Warn", "0", COLORS["accent2"]),
            ("Bundles", "0", COLORS["accent"]),
            ("Scripts", "0", COLORS["accent2"]),
            ("Tools", "0", COLORS["accent"]),
            ("Act3", "UNKNOWN", COLORS["warn"]),
        ]
        if isinstance(self.state_snapshot, dict):
            git_truth = self.state_snapshot.get("git_truth", {})
            bundles = self.state_snapshot.get("bundles", {})
            scriptorium = self.state_snapshot.get("scriptorium", {})
            arsenal = self.state_snapshot.get("arsenal", {})
            act3 = self.state_snapshot.get("act3_spine", {})
            warnings_list = self.state_snapshot.get("warnings", [])
            state_verdict = str(self.state_snapshot.get("verdict", "UNKNOWN"))
            git_verdict = str(git_truth.get("verdict", "UNKNOWN"))
            warn_count = len(warnings_list) if isinstance(warnings_list, list) else 0
            bundle_count = len(bundles.get("discovered_bundles", [])) if isinstance(bundles.get("discovered_bundles"), list) else 0
            script_count = str(scriptorium.get("entry_count", "0"))
            tool_count = str(arsenal.get("known_tools_count", "0"))
            act3_status = str(act3.get("truth_source_registry_status", "UNKNOWN"))

            state_color = COLORS["good"] if state_verdict == "PASS" else COLORS["warn"] if state_verdict == "PASS_WITH_WARNINGS" else COLORS["bad"]
            git_color = COLORS["good"] if git_verdict == "PASS" else COLORS["bad"] if git_verdict == "BLOCKED" else COLORS["warn"]
            warn_color = COLORS["good"] if warn_count == 0 else COLORS["warn"] if warn_count < 6 else COLORS["bad"]
            act3_color = COLORS["good"] if act3_status == "PROVEN" else COLORS["warn"] if act3_status == "WARNING" else COLORS["bad"] if act3_status == "BLOCKED" else COLORS["accent2"]

            chips = [
                ("State", state_verdict, state_color),
                ("Git", git_verdict, git_color),
                ("Warn", str(warn_count), warn_color),
                ("Bundles", str(bundle_count), COLORS["accent"]),
                ("Scripts", script_count, COLORS["accent2"]),
                ("Tools", tool_count, COLORS["accent"]),
                ("Act3", act3_status, act3_color),
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

        # organs on clearly separated orbit lanes + status colors from runtime truth
        def status_color(value: str) -> QColor:
            if value in {"PASS", "PROVEN", "SHA_PASS"}:
                return COLORS["good"]
            if value in {"BLOCKED", "SHA_FAIL"}:
                return COLORS["bad"]
            if value in {"WARNING", "PASS_WITH_WARNINGS", "STALE", "UNKNOWN"}:
                return COLORS["warn"]
            return COLORS["accent2"]

        org_status: dict[str, str] = {
            "ASTRA": "UNKNOWN",
            "ADMINISTRATUM": "UNKNOWN",
            "MECHANICUS": "UNKNOWN",
            "INQUISITION": "UNKNOWN",
            "PC": "UNKNOWN",
            "SPECULUM": "UNKNOWN",
        }
        if isinstance(self.state_snapshot, dict):
            git_truth = self.state_snapshot.get("git_truth", {})
            receipts = self.state_snapshot.get("receipts", {})
            act3 = self.state_snapshot.get("act3_spine", {})
            arsenal = self.state_snapshot.get("arsenal", {})
            warnings = self.state_snapshot.get("warnings", [])
            def pick_verdict(payload: Any) -> str:
                if isinstance(payload, dict):
                    return str(payload.get("verdict", "UNKNOWN"))
                return "UNKNOWN"
            org_status["ASTRA"] = str(git_truth.get("verdict", "UNKNOWN"))
            org_status["ADMINISTRATUM"] = pick_verdict(receipts.get("latest_git_cli_check"))
            org_status["MECHANICUS"] = "WARNING" if int(arsenal.get("unknown_count", 0) or 0) > 0 else "PASS"
            org_status["INQUISITION"] = "UNKNOWN"
            org_status["PC"] = pick_verdict(receipts.get("latest_bundle_intake_review"))
            advisory_status = str(act3.get("advisory_status", "UNKNOWN"))
            if advisory_status in {"RAW_ADVISORY_INPUT_NOT_YET_RECONCILED", "REGISTERED_RAW_ADVISORY_NOT_RECONCILED"}:
                org_status["SPECULUM"] = "WARNING"
            elif advisory_status:
                org_status["SPECULUM"] = advisory_status
            if isinstance(warnings, list) and len(warnings) > 8:
                org_status["MECHANICUS"] = "WARNING"

        organs = [
            ("ASTRA", -math.pi / 2, 1.52),
            ("ADMINISTRATUM", 0.0, 1.48),
            ("MECHANICUS", math.pi * 0.30, 1.42),
            ("INQUISITION", math.pi / 2, 1.30),
            ("PC", math.pi * 0.86, 1.46),
            ("SPECULUM", math.pi * 1.18, 1.40),
        ]

        node_points: list[tuple[str, QPointF, QColor]] = []
        painter.setFont(QFont("Segoe UI Semibold", 8))
        for idx, (label, base_a, lane) in enumerate(organs):
            pulse = math.sin(self.tick * 0.035 + idx * 0.9)
            a = base_a + pulse * 0.035
            rr = radius * lane
            x = cx + math.cos(a) * rr
            y = cy + math.sin(a) * rr * 0.64
            status_value = org_status.get(label, "UNKNOWN")
            color = status_color(status_value)
            node_points.append((label, QPointF(x, y), color))

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

            label_full = f"{label} {status_value}"
            label_w = max(108, len(label_full) * 7 + 18)
            label_rect = QRectF(x - label_w / 2, y + 18, label_w, 19)
            painter.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 120), 1))
            painter.setBrush(QBrush(QColor(5, 18, 28, 210)))
            painter.drawRoundedRect(label_rect, 6, 6)
            painter.setPen(QPen(color, 1))
            painter.drawText(label_rect, Qt.AlignCenter, label_full)

        # synapse-like inter-organ links
        link_pairs = [(0, 1), (1, 2), (2, 4), (4, 5), (5, 0), (1, 3)]
        for idx, (a_idx, b_idx) in enumerate(link_pairs):
            _, p1, c1 = node_points[a_idx]
            _, p2, _ = node_points[b_idx]
            alpha = 58 + int((math.sin(self.tick * 0.06 + idx) + 1) * 42)
            painter.setPen(QPen(QColor(c1.red(), c1.green(), c1.blue(), alpha), 1.5))
            painter.drawLine(p1, p2)

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
    def __init__(self, state_provider: Callable[[], dict[str, Any] | None] | None = None):
        super().__init__()
        self.state_provider = state_provider
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

        self.bundle_details = QTextEdit()
        self.bundle_details.setReadOnly(True)
        self.bundle_details.setLineWrapMode(QTextEdit.NoWrap)
        self.bundle_details.setMaximumHeight(140)
        self.bundle_details.setPlainText("Bundle details: select or refresh to inspect status.")
        layout.addWidget(self.bundle_details)

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
        self.bundle_list.currentItemChanged.connect(self.on_bundle_selected)

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

    def _current_state_head(self) -> str | None:
        if self.state_provider is None:
            return None
        payload = self.state_provider()
        if not isinstance(payload, dict):
            return None
        git_truth = payload.get("git_truth")
        if not isinstance(git_truth, dict):
            return None
        head = git_truth.get("local_head")
        if isinstance(head, str) and head:
            return head
        return None

    def _status_color(self, status: str) -> tuple[QColor, QColor]:
        if status in {"SHA_FAIL", "BLOCKED"}:
            return QColor("#4b1624"), QColor("#ffd5df")
        if status in {"SHA_PASS", "FETCHED", "REVIEWED", "COMMITTED"}:
            return QColor("#0d3f32"), QColor("#d7ffed")
        if status in {"SHA_MISSING", "STALE", "NEEDS_OWNER_DECISION", "APPLIED"}:
            return QColor("#4d3a10"), QColor("#fff5c9")
        if status == "REMOTE_ONLY":
            return QColor("#14344b"), QColor("#c9f4ff")
        return QColor("#1f2d3a"), QColor("#d7e9f7")

    def _inspect_local_bundle_status(self, bundle: dict[str, Any]) -> tuple[str, str]:
        local_zip = self.route.pc_bundle_inbox / str(bundle.get("name", ""))
        remote_sha_present = bool(bundle.get("sha256_remote_present"))
        if not local_zip.exists():
            return ("SHA_MISSING", "Remote bundle has no .sha256 pair.") if not remote_sha_present else ("REMOTE_ONLY", "Bundle is available on VM2; not fetched to PC inbox.")

        local_sha = local_zip.with_suffix(local_zip.suffix + ".sha256")
        if local_sha.exists():
            expected = self.service._parse_expected_sha(local_sha)
            actual = self.service._sha256_path(local_zip)
            if expected and expected != actual:
                return "SHA_FAIL", f"Local SHA mismatch: expected {expected}, actual {actual}"
            if expected and expected == actual:
                status = "SHA_PASS"
                detail = "Local SHA verification passed."
            else:
                status = "UNKNOWN"
                detail = "SHA file exists but expected digest is empty."
        else:
            status = "SHA_MISSING"
            detail = "Fetched zip exists but local .sha256 file is missing."

        current_head = self._current_state_head()
        source_head = None
        try:
            with zipfile.ZipFile(local_zip, "r") as zf:
                candidates = [name for name in zf.namelist() if name.endswith("MANIFEST.json")]
                if candidates:
                    payload = json.loads(zf.read(sorted(candidates, key=len)[0]).decode("utf-8"))
                    if isinstance(payload, dict):
                        source_git = payload.get("source_git_truth")
                        if isinstance(source_git, dict):
                            source_head = source_git.get("head")
        except Exception:
            source_head = None

        if isinstance(current_head, str) and isinstance(source_head, str) and source_head and source_head != current_head:
            return "STALE", f"Bundle source head is stale: {source_head} (current {current_head})"

        return status, detail

    def on_bundle_selected(self, *_args):
        item = self.bundle_list.currentItem()
        if not item:
            self.bundle_details.setPlainText("Bundle details: select or refresh to inspect status.")
            return
        payload = item.data(Qt.UserRole)
        if not isinstance(payload, dict):
            self.bundle_details.setPlainText("Selected entry payload is invalid.")
            return
        lines = [
            f"name: {payload.get('name')}",
            f"status: {payload.get('bundle_status')}",
            f"modified_utc: {payload.get('modified_utc')}",
            f"size_bytes: {payload.get('size_bytes')}",
            f"remote_path: {payload.get('remote_path')}",
            f"sha256_remote_present: {payload.get('sha256_remote_present')}",
            f"detail: {payload.get('status_detail')}",
        ]
        self.bundle_details.setPlainText("\n".join(lines))

    def refresh_bundles(self):
        self.bundle_list.clear()
        bundles = self.service.list_bundles()
        if not bundles and self.service.last_bundle_list_error:
            self.status.setText("Bundles refresh failed.")
            self.bundle_details.setPlainText(
                "Bundle refresh error:\n"
                f"{self.service.last_bundle_list_error}\n\n"
                "Truth policy: UNKNOWN until remote list command succeeds."
            )
            return

        for idx, bundle in enumerate(bundles):
            if not isinstance(bundle, dict):
                continue
            status, detail = self._inspect_local_bundle_status(bundle)
            bundle["bundle_status"] = status
            bundle["status_detail"] = detail
            name = str(bundle.get("name", "UNKNOWN.zip"))
            modified = str(bundle.get("modified_utc", "UNKNOWN"))
            age_tag = "[NEWEST]" if idx == 0 else "[RECENT]" if idx < 3 else "[OLDER]"
            flavor = "[SANCTUM]" if "SANCTUM" in name.upper() else "[ACT3]" if "ACT3" in name.upper() else ""
            label = f"{age_tag} [{status}] {flavor} {name} | {modified}"

            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, bundle)
            item.setToolTip(bundle.get("remote_path") or name)
            bg, fg = self._status_color(status)
            item.setBackground(bg)
            item.setForeground(fg)
            self.bundle_list.addItem(item)

        if self.bundle_list.count() > 0:
            self.bundle_list.setCurrentRow(0)
            self.on_bundle_selected()
        self.status.setText(
            f"Bundles: {len(bundles)} | source dirs: {', '.join(self.service._bundle_dirs())}"
        )

    def fetch_selected(self):
        item = self.bundle_list.currentItem()
        if not item:
            self.warn("Fetch", "Select bundle first.")
            return
        payload = item.data(Qt.UserRole)
        if not isinstance(payload, dict):
            self.warn("Fetch", "Selected bundle payload is invalid.")
            return
        remote_bundle = str(payload.get("remote_path") or "")
        if not remote_bundle:
            self.warn("Fetch", "Selected bundle has no remote path.")
            return
        ok, msg = self.service.fetch_bundle(remote_bundle)
        self.status.setText(msg)
        if ok:
            self.info("Fetch", f"Fetched to:\n{msg}")
            self.refresh_bundles()
        else:
            if msg.startswith("COMMAND_PREP_ONLY"):
                self.info("Fetch (command prep)", msg)
            else:
                self.warn("Fetch", msg)

    def fetch_latest(self):
        self.refresh_bundles()
        if self.bundle_list.count() == 0:
            self.warn("Fetch latest", "No bundles found.")
            return
        self.bundle_list.setCurrentRow(0)
        self.fetch_selected()


class AdaptiveOperatorPanel(QFrame):
    def __init__(self, repo_root: Path, on_state_updated: Callable[[dict[str, Any] | None], None] | None = None):
        super().__init__()
        self.repo_root = Path(repo_root)
        self.on_state_updated = on_state_updated
        self.state_path = self.repo_root / ".imperium_runtime" / "sanctum" / "state" / "SANCTUM_STATE_V0_1.json"
        self.latest_state: dict | None = None

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
            QTextEdit {
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
            QTabWidget::pane {
                border: 1px solid #206f98;
                border-radius: 8px;
                background: #0d2a40;
            }
            QTabBar::tab {
                background: #12364f;
                color: #cfeef6;
                padding: 6px 10px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background: #1a4f70;
                color: #e7fdff;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        title = QLabel("ADAPTIVE OPERATOR LAYER v0.1  —  Sanctum v0.30")
        title.setFont(QFont("Segoe UI Semibold", 12))
        layout.addWidget(title)

        self.mode_label = QLabel("Mode: COMMAND_PREP_ONLY for owner-gated actions; SAFE_LOCAL for read-only checks")
        self.mode_label.setFont(QFont("Consolas", 9))
        layout.addWidget(self.mode_label)

        row = QHBoxLayout()
        self.btn_refresh_state = QPushButton("Refresh State")
        self.btn_check_script = QPushButton("Run Script Registry Check")
        self.btn_check_act3 = QPushButton("Run Act3 Spine Check")
        row.addWidget(self.btn_refresh_state)
        row.addWidget(self.btn_check_script)
        row.addWidget(self.btn_check_act3)
        layout.addLayout(row)

        row2 = QHBoxLayout()
        self.btn_check_intake = QPushButton("Run Intake Regression Check")
        self.btn_copy_pc_cmd = QPushButton("Copy PC Intake Cmd")
        row2.addWidget(self.btn_check_intake)
        row2.addWidget(self.btn_copy_pc_cmd)
        layout.addLayout(row2)

        self.status = QLabel("Sanctum state not loaded yet.")
        self.status.setFont(QFont("Consolas", 9))
        layout.addWidget(self.status)

        self.last_refresh_label = QLabel("UI state refresh: never")
        self.last_refresh_label.setFont(QFont("Consolas", 9))
        layout.addWidget(self.last_refresh_label)

        self.tabs = QTabWidget()
        self.views: dict[str, QTextEdit] = {}
        self._add_tab("git_truth", "Git Truth")
        self._add_tab("bundle_index", "Bundle Index")
        self._add_tab("receipts", "Latest Receipts")
        self._add_tab("scriptorium", "SCRIPTORIUM")
        self._add_tab("arsenal", "ARSENAL")
        self._add_tab("act3", "Act3 Spine")
        self._add_tab("warnings", "Warning / Stale")
        self._add_tab("actions", "Operator Actions")
        layout.addWidget(self.tabs, 1)

        self.btn_refresh_state.clicked.connect(self.refresh_state)
        self.btn_check_script.clicked.connect(self.run_script_registry_check)
        self.btn_check_act3.clicked.connect(self.run_act3_check)
        self.btn_check_intake.clicked.connect(self.run_intake_regression_check)
        self.btn_copy_pc_cmd.clicked.connect(self.copy_pc_intake_command)

        self.load_state_from_disk()

    def _add_tab(self, key: str, title: str) -> None:
        view = QTextEdit()
        view.setReadOnly(True)
        view.setLineWrapMode(QTextEdit.NoWrap)
        self.views[key] = view
        self.tabs.addTab(view, title)

    def _set_status(self, text: str) -> None:
        self.status.setText(text)

    def _emit_state_update(self, state: dict[str, Any] | None) -> None:
        if self.on_state_updated is None:
            return
        try:
            self.on_state_updated(state)
        except Exception:
            # UI callback must never break operator panel flow.
            pass

    def _resolve_python_command(self) -> list[str] | None:
        candidates = [["py", "-3"], ["python"], ["python3"], [sys.executable]]
        seen: set[str] = set()
        for candidate in candidates:
            key = " ".join(candidate)
            if key in seen:
                continue
            seen.add(key)
            exe = candidate[0]
            if shutil.which(exe) is None and exe != sys.executable:
                continue
            try:
                result = subprocess.run(
                    [*candidate, "-c", "print('ok')"],
                    capture_output=True,
                    text=True,
                    timeout=12,
                )
                if result.returncode == 0:
                    return candidate
            except Exception:
                continue
        return None

    def _run_command(self, command: list[str], timeout: int = 300) -> tuple[bool, str]:
        try:
            result = subprocess.run(
                command,
                cwd=str(self.repo_root),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except Exception as exc:
            return False, f"Execution error: {exc}"
        output = "\n".join(
            [
                f"command: {' '.join(command)}",
                f"exit_code: {result.returncode}",
                "",
                "stdout:",
                result.stdout[-5000:],
                "",
                "stderr:",
                result.stderr[-5000:],
            ]
        )
        return result.returncode == 0, output

    def refresh_state(self):
        python_cmd = self._resolve_python_command()
        if python_cmd is None:
            QMessageBox.warning(self, "Refresh State", "Python runtime not found (tried py -3 / python / python3).")
            return

        command = [
            *python_cmd,
            str(self.repo_root / "TOOLS" / "build_sanctum_state_v0_1.py"),
            "--repo-root",
            str(self.repo_root),
            "--out",
            str(self.state_path),
            "--human",
        ]
        ok, output = self._run_command(command, timeout=420)
        self._set_status("State refreshed." if ok else "State refresh returned nonzero.")
        if not ok:
            QMessageBox.warning(self, "Refresh State", output)
        self.load_state_from_disk()

    def run_script_registry_check(self):
        python_cmd = self._resolve_python_command()
        if python_cmd is None:
            QMessageBox.warning(self, "SCRIPTORIUM Check", "Python runtime not found.")
            return
        command = [
            *python_cmd,
            str(self.repo_root / "TOOLS" / "check_script_registry_v0_1.py"),
            "--repo-root",
            str(self.repo_root),
            "--human",
        ]
        ok, output = self._run_command(command, timeout=180)
        self._set_status("SCRIPTORIUM check PASS." if ok else "SCRIPTORIUM check returned nonzero.")
        if ok:
            QMessageBox.information(self, "SCRIPTORIUM Check", output)
        else:
            QMessageBox.warning(self, "SCRIPTORIUM Check", output)
        self.load_state_from_disk()

    def run_act3_check(self):
        python_cmd = self._resolve_python_command()
        if python_cmd is None:
            QMessageBox.warning(self, "Act3 Check", "Python runtime not found.")
            return
        command = [
            *python_cmd,
            str(self.repo_root / "TOOLS" / "check_act3_address_truth_capability_spine_v0_1.py"),
            "--repo-root",
            str(self.repo_root),
            "--human",
        ]
        ok, output = self._run_command(command, timeout=240)
        self._set_status("Act3 check PASS/PASS_WITH_WARNINGS." if ok else "Act3 check returned nonzero.")
        if ok:
            QMessageBox.information(self, "Act3 Check", output)
        else:
            QMessageBox.warning(self, "Act3 Check", output)
        self.load_state_from_disk()

    def run_intake_regression_check(self):
        powershell = shutil.which("powershell")
        script_path = self.repo_root / "TOOLS" / "test_bundle_intake_regression.ps1"
        command_text = (
            "powershell -ExecutionPolicy Bypass -NoProfile "
            f"-File {script_path}"
        )
        if not powershell:
            QMessageBox.information(
                self,
                "Intake Regression",
                "COMMAND_PREP_ONLY mode:\n\n" + command_text,
            )
            self._set_status("Intake regression: command prepared only.")
            return

        command = [
            powershell,
            "-ExecutionPolicy",
            "Bypass",
            "-NoProfile",
            "-File",
            str(script_path),
            "-RepoRoot",
            str(self.repo_root),
        ]
        ok, output = self._run_command(command, timeout=300)
        self._set_status("Intake regression check finished." if ok else "Intake regression returned nonzero.")
        if ok:
            QMessageBox.information(self, "Intake Regression", output)
        else:
            QMessageBox.warning(self, "Intake Regression", output)
        self.load_state_from_disk()

    def _pc_intake_preview_command(self) -> str:
        bundle_name = "<BUNDLE>.zip"
        if isinstance(self.latest_state, dict):
            latest_bundle = self.latest_state.get("bundles", {}).get("latest_bundle")
            if isinstance(latest_bundle, dict):
                name = latest_bundle.get("name")
                if isinstance(name, str) and name:
                    bundle_name = name
        return (
            "powershell -ExecutionPolicy Bypass -NoProfile -File "
            "E:\\IMPERIUM\\TOOLS\\review_worker_bundle_intake.ps1 "
            f"-Bundle \"E:\\IMPERIUM\\INBOX\\VM2_BUNDLES\\{bundle_name}\" "
            "-RepoRoot \"E:\\IMPERIUM\" "
            "-IncomingRoot \"E:\\IMPERIUM_LOCAL_HANDOFF\\BUNDLE_INTAKE\" "
            "-NoApply"
        )

    def copy_pc_intake_command(self):
        command = self._pc_intake_preview_command()
        QApplication.clipboard().setText(command)
        self._set_status("PC intake preview command copied to clipboard.")
        QMessageBox.information(self, "PC Intake Command", command)

    def load_state_from_disk(self):
        if not self.state_path.exists():
            placeholder = (
                "State file not found.\n\n"
                "Run: python3 TOOLS/build_sanctum_state_v0_1.py "
                "--repo-root . --out .imperium_runtime/sanctum/state/SANCTUM_STATE_V0_1.json --human"
            )
            for key in self.views:
                self.views[key].setPlainText(placeholder)
            self._set_status("State file missing (UNKNOWN).")
            self.last_refresh_label.setText(f"UI state refresh: {datetime.now().isoformat(timespec='seconds')} | source missing")
            self.latest_state = None
            self._emit_state_update(None)
            return

        try:
            payload = json.loads(self.state_path.read_text(encoding="utf-8"))
        except Exception as exc:
            msg = f"Failed to parse state JSON:\n{exc}"
            for key in self.views:
                self.views[key].setPlainText(msg)
            self._set_status("State parse failed.")
            self.last_refresh_label.setText(f"UI state refresh: {datetime.now().isoformat(timespec='seconds')} | parse failed")
            self.latest_state = None
            self._emit_state_update(None)
            return

        if not isinstance(payload, dict):
            msg = "State JSON root is not an object."
            for key in self.views:
                self.views[key].setPlainText(msg)
            self._set_status("State structure invalid.")
            self.last_refresh_label.setText(f"UI state refresh: {datetime.now().isoformat(timespec='seconds')} | invalid structure")
            self.latest_state = None
            self._emit_state_update(None)
            return

        self.latest_state = payload
        self.render_state(payload)
        self.last_refresh_label.setText(
            f"UI state refresh: {datetime.now().isoformat(timespec='seconds')} | source {self.state_path}"
        )
        self._emit_state_update(payload)

    def render_state(self, state: dict):
        git_truth = state.get("git_truth", {})
        bundles = state.get("bundles", {})
        receipts = state.get("receipts", {})
        scriptorium = state.get("scriptorium", {})
        arsenal = state.get("arsenal", {})
        act3 = state.get("act3_spine", {})
        warnings = state.get("warnings", [])
        actions = state.get("operator_actions", {})
        generated = state.get("generated_at_utc")

        local_head = git_truth.get("local_head")
        origin_head = git_truth.get("origin_master_head")
        remote_head = git_truth.get("remote_master_head")
        heads_match = (
            isinstance(local_head, str)
            and isinstance(origin_head, str)
            and isinstance(remote_head, str)
            and local_head == origin_head == remote_head
        )

        self.views["git_truth"].setPlainText(
            "\n".join(
                [
                    f"generated_at_utc: {generated}",
                    f"verdict: {git_truth.get('verdict')}",
                    f"local_head: {git_truth.get('local_head')}",
                    f"origin_master_head: {git_truth.get('origin_master_head')}",
                    f"remote_master_head: {git_truth.get('remote_master_head')}",
                    f"local_origin_remote_match: {heads_match}",
                    f"commit_count: {git_truth.get('commit_count')}",
                    f"latest_commit_oneline: {git_truth.get('latest_commit_oneline')}",
                    f"exact_tree_url: {git_truth.get('exact_tree_url')}",
                    f"worktree_clean: {git_truth.get('worktree_clean')}",
                ]
            )
        )

        discovered = bundles.get("discovered_bundles", [])
        bundle_lines = [
            f"handoff_out: {bundles.get('handoff_out', {}).get('path')}",
            f"handoff_out_exists: {bundles.get('handoff_out', {}).get('exists')}",
            f"discovered_bundles_count: {len(discovered) if isinstance(discovered, list) else 0}",
            "",
            "latest_bundle:",
            json.dumps(bundles.get("latest_bundle"), ensure_ascii=False, indent=2),
            "",
            "inboxes:",
            json.dumps(bundles.get("inboxes"), ensure_ascii=False, indent=2),
            "",
            "recent_discovered:",
        ]
        if isinstance(discovered, list):
            for item in discovered[:8]:
                if isinstance(item, dict):
                    bundle_lines.append(
                        f"{item.get('name')} | status={item.get('bundle_status')} "
                        f"| sha={item.get('sha256_pair_status')} | modified={item.get('modified_at_utc')}"
                    )
                else:
                    bundle_lines.append(json.dumps(item, ensure_ascii=False))
        self.views["bundle_index"].setPlainText("\n".join(bundle_lines))

        self.views["receipts"].setPlainText(
            json.dumps(
                {
                    "latest_git_cli_check": receipts.get("latest_git_cli_check"),
                    "latest_bundle_intake_review": receipts.get("latest_bundle_intake_review"),
                    "latest_act3_check": receipts.get("latest_act3_check"),
                    "latest_sanctum_state_receipt": receipts.get("latest_sanctum_state_receipt"),
                    "latest_sanctum_adaptive_check": receipts.get("latest_sanctum_adaptive_check"),
                },
                ensure_ascii=False,
                indent=2,
            )
        )

        self.views["scriptorium"].setPlainText(
            json.dumps(
                {
                    "registry_path": scriptorium.get("registry_path"),
                    "entry_count": scriptorium.get("entry_count"),
                    "safe_script_count": scriptorium.get("safe_script_count"),
                    "owner_gated_count": scriptorium.get("owner_gated_count"),
                    "runtime_only_count": scriptorium.get("runtime_only_count"),
                    "scripts_summary": scriptorium.get("scripts_summary"),
                },
                ensure_ascii=False,
                indent=2,
            )
        )

        self.views["arsenal"].setPlainText(
            json.dumps(
                {
                    "tool_index_path": arsenal.get("tool_index_path"),
                    "install_status_path": arsenal.get("install_status_path"),
                    "known_tools_count": arsenal.get("known_tools_count"),
                    "installed_count": arsenal.get("installed_count"),
                    "unknown_count": arsenal.get("unknown_count"),
                    "not_installed_count": arsenal.get("not_installed_count"),
                    "install_status_git_head": arsenal.get("install_status_git_head"),
                },
                ensure_ascii=False,
                indent=2,
            )
        )

        self.views["act3"].setPlainText(
            json.dumps(
                {
                    "zone_registry_status": act3.get("zone_registry_status"),
                    "truth_source_registry_status": act3.get("truth_source_registry_status"),
                    "capability_spine_status": act3.get("capability_spine_status"),
                    "warning_stale_baseline_status": act3.get("warning_stale_baseline_status"),
                    "truth_registry_baseline_head": act3.get("truth_registry_baseline_head"),
                    "advisory_status": act3.get("advisory_status"),
                    "advisory_is_raw_not_doctrine": act3.get("advisory_is_raw_not_doctrine"),
                },
                ensure_ascii=False,
                indent=2,
            )
        )

        self.views["warnings"].setPlainText(json.dumps(warnings, ensure_ascii=False, indent=2))

        self.views["actions"].setPlainText(
            json.dumps(
                {
                    "mode": actions.get("mode"),
                    "safe_actions": actions.get("safe_actions"),
                    "dangerous_actions": actions.get("dangerous_actions"),
                    "command_templates": actions.get("command_templates"),
                    "pc_intake_preview": self._pc_intake_preview_command(),
                },
                ensure_ascii=False,
                indent=2,
            )
        )

        state_verdict = state.get("verdict", "UNKNOWN")
        generated = state.get("generated_at_utc", "unknown time")
        self._set_status(f"State: {state_verdict} | generated_at_utc: {generated}")


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
        top_layout = QVBoxLayout(top_wrap)
        top_layout.setContentsMargins(10, 8, 10, 8)
        top_layout.setSpacing(6)
        root.addWidget(top_wrap)

        actions_row = QHBoxLayout()
        actions_row.setSpacing(8)

        self.btn_astra = QPushButton("Open Astra Utility")
        self.btn_explorer = QPushButton("Open Explorer")
        self.btn_task_folder = QPushButton("Open Task Folder")
        self.btn_notes = QPushButton("Open Notes")
        self.btn_refresh_tasks = QPushButton("Refresh Tasks")
        self.btn_git_cli_check = QPushButton("Check Git CLI")

        for btn in [
            self.btn_astra,
            self.btn_explorer,
            self.btn_task_folder,
            self.btn_notes,
            self.btn_refresh_tasks,
            self.btn_git_cli_check,
        ]:
            actions_row.addWidget(btn)

        self.btn_astra.clicked.connect(self.open_astra_utility)
        self.btn_explorer.clicked.connect(self.open_explorer_area)
        self.btn_task_folder.clicked.connect(self.open_selected_task_folder)
        self.btn_notes.clicked.connect(self.open_notes_area)
        self.btn_refresh_tasks.clicked.connect(self.refresh_tasks)
        self.btn_git_cli_check.clicked.connect(self.check_git_cli)

        self.transfer_button = QPushButton("Operator / Transfer")
        actions_row.addWidget(self.transfer_button)

        self.git_cli_status = QLabel("Git CLI: not checked")
        self.git_cli_status.setFont(QFont("Consolas", 9))
        actions_row.addWidget(self.git_cli_status)
        actions_row.addStretch(1)
        top_layout.addLayout(actions_row)

        truth_row = QHBoxLayout()
        truth_row.setSpacing(8)
        self.version_badge = QLabel(APP_LAYER_LABEL)
        self.version_badge.setFont(QFont("Segoe UI Semibold", 9))
        self.version_badge.setStyleSheet(
            "background: #12324a; border: 1px solid #2678a0; border-radius: 8px; padding: 4px 8px;"
        )
        truth_row.addWidget(self.version_badge)

        self.truth_status_label = QLabel("Truth: UNKNOWN (refresh state)")
        self.truth_status_label.setFont(QFont("Consolas", 9))
        truth_row.addWidget(self.truth_status_label, 1)

        self.selected_task_label = QLabel("Selected artifact task: (none)")
        self.selected_task_label.setFont(QFont("Consolas", 9, QFont.Bold))
        truth_row.addWidget(self.selected_task_label)
        top_layout.addLayout(truth_row)

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
            "Artifact selection panel.\n\n"
            "Truth source is Git/receipt/state evidence,\n"
            "not this static card."
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
        self.task_list.currentItemChanged.connect(self.update_selected_task_label)

        self.map_widget = PlanetMapWidget()
        self.operator_panel = AdaptiveOperatorPanel(IMPERIUM_ROOT, on_state_updated=self.on_operator_state_updated)
        self.transfer_panel = TransferPanel(state_provider=lambda: self.operator_panel.latest_state)
        self.side_tabs = QTabWidget()
        self.side_tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #206f98; border-radius: 8px; background: #0a1f31; }
            QTabBar::tab {
                background: #143b55;
                color: #dff6ff;
                border: 1px solid #2a7ea8;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 6px 10px;
                margin-right: 2px;
            }
            QTabBar::tab:selected { background: #1f5475; color: #ffffff; }
        """)
        self.side_tabs.addTab(self.transfer_panel, "Transfer Control")
        self.side_tabs.addTab(self.operator_panel, "Operator Layer")
        self.git_cli_service = GitCliCheckService(IMPERIUM_ROOT)

        splitter.addWidget(left)
        splitter.addWidget(self.map_widget)
        splitter.addWidget(self.side_tabs)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(8)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        splitter.setStretchFactor(2, 2)
        splitter.setSizes([320, 980, 520])

        self.splitter = splitter
        self.transfer_button.clicked.connect(self.toggle_transfer)
        self.update_selected_task_label()

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

    def on_operator_state_updated(self, state: dict[str, Any] | None) -> None:
        self.map_widget.set_runtime_state(state)
        if not isinstance(state, dict):
            self.truth_status_label.setText("Truth: UNKNOWN | state not loaded")
            self.truth_status_label.setStyleSheet("color: #ffcf4a;")
            return

        git_truth = state.get("git_truth", {})
        local_head = str(git_truth.get("local_head", "UNKNOWN"))
        origin_head = str(git_truth.get("origin_master_head", "UNKNOWN"))
        remote_head = str(git_truth.get("remote_master_head", "UNKNOWN"))
        match = local_head == origin_head == remote_head and local_head != "UNKNOWN"
        commit_count = git_truth.get("commit_count")
        state_verdict = str(state.get("verdict", "UNKNOWN"))
        generated = str(state.get("generated_at_utc", "unknown"))
        tree_url = str(git_truth.get("exact_tree_url", "UNKNOWN"))
        self.truth_status_label.setText(
            f"Truth: {state_verdict} | HEAD {local_head[:7]} | count {commit_count} | "
            f"match {match} | generated {generated} | tree {tree_url}"
        )
        if state_verdict == "PASS":
            self.truth_status_label.setStyleSheet("color: #3dffbf;")
        elif state_verdict == "PASS_WITH_WARNINGS":
            self.truth_status_label.setStyleSheet("color: #ffcf4a;")
        else:
            self.truth_status_label.setStyleSheet("color: #ff5f86;")

    def update_selected_task_label(self) -> None:
        task_id = self.selected_task_id()
        if task_id:
            self.selected_task_label.setText(f"Selected artifact task: {task_id}")
        else:
            self.selected_task_label.setText("Selected artifact task: (none)")

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
                "TASK-20260513-SANCTUM-V0_30-TRUTH-DASHBOARD-LAYOUT-AND-BUNDLE-FETCH-FIX-V0_1",
                "TASK-20260513-SANCTUM-ADAPTIVE-OPERATOR-LAYER-V0_1",
                "TASK-20260513-ACT3-ADDRESS-TRUTH-CAPABILITY-SPINE-SEED-V0_1",
                "TASK-20260512-BUNDLE-RECEIPT-PROVENANCE-SPINE-V0_1",
            ]

            for name in task_dirs or fallback:
                self.task_list.addItem(name)

            if self.task_list.count() > 0:
                self.task_list.setCurrentRow(0)
        except Exception as exc:
            QMessageBox.warning(self, "Refresh Tasks", f"Failed to refresh tasks:\n{exc}")

    def check_git_cli(self):
        try:
            process_result = self.git_cli_service.run_wrapper()
        except FileNotFoundError as exc:
            self.git_cli_status.setText("Git CLI: wrapper missing")
            QMessageBox.warning(self, "Check Git CLI", str(exc))
            return
        except GitCliCheckServiceError as exc:
            self.git_cli_status.setText("Git CLI: PowerShell/runtime error")
            QMessageBox.warning(self, "Check Git CLI", str(exc))
            return
        except Exception as exc:
            self.git_cli_status.setText("Git CLI: unexpected error")
            QMessageBox.warning(self, "Check Git CLI", f"Unexpected error while running checker:\n{exc}")
            return

        if process_result.returncode != 0:
            self.git_cli_status.setText("Git CLI: checker returned nonzero")
            details = (
                "Checker returned nonzero exit code.\n\n"
                f"returncode: {process_result.returncode}\n\n"
                f"stdout:\n{process_result.stdout[-3000:]}\n\n"
                f"stderr:\n{process_result.stderr[-3000:]}"
            )
            QMessageBox.warning(self, "Check Git CLI", details)
            return

        try:
            result_payload = self.git_cli_service.load_result_json()
        except FileNotFoundError as exc:
            self.git_cli_status.setText("Git CLI: result JSON missing")
            QMessageBox.warning(self, "Check Git CLI", str(exc))
            return
        except ValueError as exc:
            self.git_cli_status.setText("Git CLI: JSON parse failed")
            QMessageBox.warning(self, "Check Git CLI", str(exc))
            return

        try:
            self.git_cli_service.load_verdict_md()
        except FileNotFoundError as exc:
            self.git_cli_status.setText("Git CLI: verdict file missing")
            QMessageBox.warning(self, "Check Git CLI", str(exc))
            return

        summary = self.git_cli_service.summarize(result_payload)
        verdict = summary.get("verdict", "UNKNOWN")
        head_short = str(summary.get("local_head", ""))[:7]
        self.git_cli_status.setText(f"Git CLI: {verdict} ({head_short})")

        details = self.git_cli_service.format_summary_text(summary)
        self.show_git_cli_result_dialog(details)

    def show_git_cli_result_dialog(self, details: str):
        dialog = QDialog(self)
        dialog.setWindowTitle("Check Git CLI")
        dialog.resize(820, 560)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #06111D;
                color: #E8FCFF;
            }
            QTextEdit {
                background-color: #020812;
                color: #E8FCFF;
                border: 1px solid #28D7FF;
                border-radius: 8px;
                padding: 10px;
                selection-background-color: #0B5C86;
                selection-color: #FFFFFF;
            }
            QPushButton {
                color: #E8FCFF;
                background-color: #0B5C86;
                border: 1px solid #4DDFFF;
                border-radius: 8px;
                padding: 7px 18px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1178A8;
            }
        """)

        layout = QVBoxLayout(dialog)

        text = QTextEdit(dialog)
        text.setReadOnly(True)
        text.setPlainText(details)
        text.setFont(QFont("Consolas", 10))
        layout.addWidget(text)

        row = QHBoxLayout()
        row.addStretch(1)

        ok = QPushButton("OK", dialog)
        ok.clicked.connect(dialog.accept)
        row.addWidget(ok)

        layout.addLayout(row)
        dialog.exec()

    def toggle_transfer(self):
        visible = not self.side_tabs.isVisible()
        self.side_tabs.setVisible(visible)
        if visible:
            self.splitter.setSizes([320, 980, 520])
        else:
            self.splitter.setSizes([320, 1500, 0])


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    window = SanctumMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
