#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPen, QRadialGradient
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

APP_NAME = "IMPERIUM Sanctum v0.4 Visual Factory Prototype"
TASK_ID = "TASK-20260513-STEP7_1F-STEP7_2-BUNDLE-ROUTE-ASSET-REGISTRATION-SANCTUM-V0_4"

REPO_ROOT = Path(__file__).resolve().parents[1]
BUNDLE_ROUTE_REGISTRY_REL = "REGISTRY/BUNDLE_ROUTE_REGISTRY.json"
ASSET_MANIFEST_REL = "ASSETS/ASSET_MANIFEST.json"


@dataclass
class RoutePolicy:
    canonical_vm2_outbox: str
    canonical_pc_inbox: str
    legacy_scan_dirs: list[str]
    source_priority_order: list[str]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def normalize_paths(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    out: list[str] = []
    for value in values:
        if not isinstance(value, str):
            continue
        cleaned = value.strip()
        if cleaned and cleaned not in out:
            out.append(cleaned)
    return out


def load_route_policy(repo_root: Path) -> tuple[RoutePolicy, list[str]]:
    warnings: list[str] = []
    default_canonical = "/home/vboxuser2/IMPERIUM_WORK/VM2_BUNDLES/"
    default_legacy = [
        "/home/vboxuser2/IMPERIUM_WORK/_handoff_out/",
        "/home/vboxuser2/IMPERIUM_PRIVATE/OUTBOX/",
    ]
    default_priority = [default_canonical, *default_legacy]
    default_pc = "E:\\IMPERIUM\\INBOX\\VM2_BUNDLES\\"

    reg_path = repo_root / BUNDLE_ROUTE_REGISTRY_REL
    payload = read_json(reg_path)
    if payload is None:
        warnings.append("bundle_route_registry_missing_or_invalid_using_defaults")
        return (
            RoutePolicy(
                canonical_vm2_outbox=default_canonical,
                canonical_pc_inbox=default_pc,
                legacy_scan_dirs=default_legacy,
                source_priority_order=default_priority,
            ),
            warnings,
        )

    canonical = payload.get("canonical_vm2_outbox")
    pc_inbox = payload.get("canonical_pc_inbox")
    legacy = normalize_paths(payload.get("legacy_scan_dirs"))
    priority = normalize_paths(payload.get("source_priority_order"))

    if not isinstance(canonical, str) or not canonical.strip():
        canonical = default_canonical
        warnings.append("registry_missing_canonical_vm2_outbox_using_default")
    if not isinstance(pc_inbox, str) or not pc_inbox.strip():
        pc_inbox = default_pc
        warnings.append("registry_missing_canonical_pc_inbox_using_default")
    if not legacy:
        legacy = default_legacy
        warnings.append("registry_missing_legacy_dirs_using_default")
    if not priority:
        priority = [canonical, *legacy]
        warnings.append("registry_missing_priority_using_canonical_then_legacy")

    if priority[0].rstrip("/") != canonical.rstrip("/"):
        warnings.append("priority_first_is_not_canonical_auto_corrected")
        priority = [canonical] + [item for item in priority if item.rstrip("/") != canonical.rstrip("/")]

    return (
        RoutePolicy(
            canonical_vm2_outbox=canonical,
            canonical_pc_inbox=pc_inbox,
            legacy_scan_dirs=legacy,
            source_priority_order=priority,
        ),
        warnings,
    )


def scan_bundles(policy: RoutePolicy) -> tuple[list[dict[str, Any]], list[str]]:
    warnings: list[str] = []
    candidates: list[dict[str, Any]] = []

    for index, source_dir in enumerate(policy.source_priority_order):
        root = Path(source_dir)
        if not root.exists() or not root.is_dir():
            continue
        for file_path in root.glob("*.zip"):
            if not file_path.is_file():
                continue
            stat = file_path.stat()
            candidates.append(
                {
                    "name": file_path.name,
                    "path": file_path.as_posix(),
                    "source_dir": source_dir,
                    "source_priority_index": index,
                    "modified_epoch": int(stat.st_mtime),
                    "modified_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                    "size_bytes": stat.st_size,
                    "sha256_pair_present": file_path.with_suffix(file_path.suffix + ".sha256").exists(),
                }
            )

    deduped: dict[str, dict[str, Any]] = {}
    collisions: list[str] = []
    ordered = sorted(
        candidates,
        key=lambda item: (
            int(item.get("source_priority_index", 999)),
            -int(item.get("modified_epoch", 0)),
            str(item.get("name", "")),
        ),
    )
    for item in ordered:
        name = str(item.get("name", ""))
        if not name:
            continue
        if name not in deduped:
            deduped[name] = item
            continue
        kept = deduped[name]
        collisions.append(f"{name}:{kept.get('source_dir')}:{item.get('source_dir')}")
        kept_prio = int(kept.get("source_priority_index", 999))
        item_prio = int(item.get("source_priority_index", 999))
        if item_prio < kept_prio:
            deduped[name] = item
        elif item_prio == kept_prio and int(item.get("modified_epoch", 0)) > int(kept.get("modified_epoch", 0)):
            deduped[name] = item

    bundles = sorted(
        deduped.values(),
        key=lambda item: (
            int(item.get("source_priority_index", 999)),
            -int(item.get("modified_epoch", 0)),
            str(item.get("name", "")),
        ),
    )

    if collisions:
        warnings.append(f"bundle_name_collisions_detected:{len(collisions)}")
    return bundles, warnings


def load_asset_summary(repo_root: Path) -> dict[str, Any]:
    path = repo_root / ASSET_MANIFEST_REL
    payload = read_json(path)
    if payload is None:
        return {
            "manifest_found": False,
            "asset_count": 0,
            "status": "MISSING_OR_INVALID",
            "accepted": 0,
            "rejected": 0,
            "candidate": 0,
        }

    assets = payload.get("assets") if isinstance(payload.get("assets"), list) else []
    accepted = 0
    rejected = 0
    candidate = 0
    for item in assets:
        if not isinstance(item, dict):
            continue
        status = item.get("proposed_status")
        if status == "accepted":
            accepted += 1
        elif status == "rejected":
            rejected += 1
        else:
            candidate += 1

    return {
        "manifest_found": True,
        "asset_count": len(assets),
        "status": payload.get("status"),
        "accepted": accepted,
        "rejected": rejected,
        "candidate": candidate,
    }


class OrbitCoreWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setMinimumSize(480, 480)
        self.setAutoFillBackground(False)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        rect = self.rect()
        grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
        grad.setColorAt(0.0, QColor("#060b14"))
        grad.setColorAt(1.0, QColor("#102338"))
        painter.fillRect(rect, grad)

        cx = rect.center().x()
        cy = rect.center().y()

        core_radius = min(rect.width(), rect.height()) * 0.12
        core_grad = QRadialGradient(QPointF(cx, cy), core_radius * 1.5)
        core_grad.setColorAt(0.0, QColor("#f4a35a"))
        core_grad.setColorAt(0.35, QColor("#55d6ff"))
        core_grad.setColorAt(1.0, QColor(16, 35, 56, 0))
        painter.setBrush(core_grad)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(cx, cy), core_radius * 1.5, core_radius * 1.5)

        painter.setBrush(QColor("#0f2538"))
        painter.setPen(QPen(QColor("#59d9ff"), 2))
        painter.drawEllipse(QPointF(cx, cy), core_radius, core_radius)

        orbit_pen = QPen(QColor(94, 157, 214, 120), 1.2)
        orbit_pen.setStyle(Qt.SolidLine)
        painter.setPen(orbit_pen)
        painter.setBrush(Qt.NoBrush)

        orbit_radii = [core_radius * 2.2, core_radius * 3.4, core_radius * 4.6]
        for radius in orbit_radii:
            painter.drawEllipse(QPointF(cx, cy), radius, radius)

        nodes = [
            (orbit_radii[0], 15, "#55d6ff"),
            (orbit_radii[0], 170, "#5b88ff"),
            (orbit_radii[1], 70, "#f79a3e"),
            (orbit_radii[1], 235, "#40d79f"),
            (orbit_radii[2], 305, "#d5b15f"),
            (orbit_radii[2], 120, "#8fb9ff"),
        ]

        for radius, deg, color_hex in nodes:
            radians = deg * 3.141592653589793 / 180.0
            x = cx + radius * __import__("math").cos(radians)
            y = cy + radius * __import__("math").sin(radians)
            painter.setBrush(QColor(color_hex))
            painter.setPen(QPen(QColor("#091726"), 1))
            painter.drawEllipse(QPointF(x, y), 8, 8)


class MainWindow(QMainWindow):
    def __init__(self, repo_root: Path) -> None:
        super().__init__()
        self.repo_root = repo_root
        self.setWindowTitle(APP_NAME)
        self.resize(1500, 920)

        self.policy, self.route_warnings = load_route_policy(self.repo_root)
        self.bundle_data: list[dict[str, Any]] = []
        self.asset_summary = load_asset_summary(self.repo_root)

        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(8)

        self.header = QLabel("SANCTUM v0.4 Experimental Visual Factory Prototype")
        self.header.setStyleSheet("color:#e5f3ff; font-size: 20px; font-weight: 700;")
        root_layout.addWidget(self.header)

        self.status_strip = QLabel("")
        self.status_strip.setStyleSheet(
            "background:#0c1f31; color:#9fc4e0; border:1px solid #24405d; padding:6px; border-radius:6px;"
        )
        root_layout.addWidget(self.status_strip)

        splitter = QSplitter(Qt.Horizontal)
        root_layout.addWidget(splitter, 1)

        left = QFrame()
        left.setStyleSheet("QFrame{background:#0a1826; border:1px solid #20364f; border-radius:8px;}")
        left_layout = QVBoxLayout(left)
        left_layout.addWidget(QLabel("Route + Asset Truth"))
        self.route_view = QTextEdit()
        self.route_view.setReadOnly(True)
        self.route_view.setStyleSheet("background:#0b1e30; color:#d2e8ff; border:1px solid #2a4869;")
        left_layout.addWidget(self.route_view, 1)
        splitter.addWidget(left)

        center = QFrame()
        center.setStyleSheet("QFrame{background:#091420; border:1px solid #1f3652; border-radius:8px;}")
        center_layout = QVBoxLayout(center)
        center_layout.addWidget(QLabel("Core / Orbit Visual Map"))
        self.orbit = OrbitCoreWidget()
        center_layout.addWidget(self.orbit, 1)
        splitter.addWidget(center)

        right = QFrame()
        right.setStyleSheet("QFrame{background:#0a1826; border:1px solid #20364f; border-radius:8px;}")
        right_layout = QVBoxLayout(right)
        right_layout.addWidget(QLabel("Canonical Bundle Panel"))
        self.btn_refresh = QPushButton("Refresh Bundles")
        self.btn_refresh.clicked.connect(self.refresh)
        right_layout.addWidget(self.btn_refresh)
        self.bundle_list = QListWidget()
        self.bundle_list.currentItemChanged.connect(self.on_bundle_selected)
        right_layout.addWidget(self.bundle_list, 2)
        self.bundle_details = QTextEdit()
        self.bundle_details.setReadOnly(True)
        self.bundle_details.setStyleSheet("background:#0b1e30; color:#d2e8ff; border:1px solid #2a4869;")
        right_layout.addWidget(self.bundle_details, 1)
        splitter.addWidget(right)

        splitter.setSizes([380, 620, 500])

        self.evidence = QTextEdit()
        self.evidence.setReadOnly(True)
        self.evidence.setMinimumHeight(150)
        self.evidence.setStyleSheet("background:#0b1a2a; color:#cfe3f7; border:1px solid #264663; border-radius:8px;")
        root_layout.addWidget(self.evidence)

        self.setStyleSheet(
            "QLabel{color:#9dc7e6; font-family: 'Segoe UI'; font-size:12px;}"
            "QPushButton{background:#14304a; color:#d8ebff; border:1px solid #355876; padding:6px 10px; border-radius:6px;}"
            "QPushButton:hover{background:#1a3f62;}"
            "QListWidget{background:#0b1f31; color:#d8ecff; border:1px solid #2b4e6f;}"
        )

        self.refresh()

    def refresh(self) -> None:
        self.policy, self.route_warnings = load_route_policy(self.repo_root)
        self.bundle_data, scan_warnings = scan_bundles(self.policy)
        self.asset_summary = load_asset_summary(self.repo_root)

        self.bundle_list.clear()
        for bundle in self.bundle_data:
            source = bundle.get("source_dir", "")
            is_canonical = source.rstrip("/") == self.policy.canonical_vm2_outbox.rstrip("/")
            prefix = "[CANON]" if is_canonical else "[LEGACY]"
            item = QListWidgetItem(
                f"{prefix} {bundle.get('name')} | {bundle.get('modified_utc')}"
            )
            item.setData(Qt.UserRole, bundle)
            self.bundle_list.addItem(item)

        if self.bundle_list.count() > 0:
            self.bundle_list.setCurrentRow(0)
        else:
            self.bundle_details.setPlainText("No bundles discovered in configured source directories.")

        route_lines = [
            f"registry: {BUNDLE_ROUTE_REGISTRY_REL}",
            f"canonical_vm2_outbox: {self.policy.canonical_vm2_outbox}",
            f"canonical_pc_inbox: {self.policy.canonical_pc_inbox}",
            f"legacy_scan_dirs: {json.dumps(self.policy.legacy_scan_dirs, ensure_ascii=False)}",
            f"source_priority_order: {json.dumps(self.policy.source_priority_order, ensure_ascii=False)}",
            "",
            "asset_manifest:",
            f"  path: {ASSET_MANIFEST_REL}",
            f"  found: {self.asset_summary.get('manifest_found')}",
            f"  status: {self.asset_summary.get('status')}",
            f"  total_assets: {self.asset_summary.get('asset_count')}",
            f"  accepted/rejected/candidate: {self.asset_summary.get('accepted')}/{self.asset_summary.get('rejected')}/{self.asset_summary.get('candidate')}",
        ]
        self.route_view.setPlainText("\n".join(route_lines))

        warnings = [*self.route_warnings, *scan_warnings]
        warning_text = "none" if not warnings else "; ".join(warnings)
        self.status_strip.setText(
            f"task_id={TASK_ID} | generated={utc_now()} | bundles={len(self.bundle_data)} | warnings={warning_text}"
        )

        self.evidence.setPlainText(
            "Prototype intent:\n"
            "- keep v0.29 baseline untouched\n"
            "- use canonical bundle route policy\n"
            "- reflect Step 7.2 asset interpretation as proposal-only\n"
            "- preserve READY_FOR_AGENT=false and Act5 execution blocked\n"
        )

    def on_bundle_selected(self, current: QListWidgetItem | None, _previous: QListWidgetItem | None) -> None:
        if current is None:
            self.bundle_details.setPlainText("Select a bundle row to inspect details.")
            return
        payload = current.data(Qt.UserRole)
        if not isinstance(payload, dict):
            self.bundle_details.setPlainText("Invalid bundle payload")
            return

        lines = [
            f"name: {payload.get('name')}",
            f"source_dir: {payload.get('source_dir')}",
            f"source_priority_index: {payload.get('source_priority_index')}",
            f"path: {payload.get('path')}",
            f"modified_utc: {payload.get('modified_utc')}",
            f"size_bytes: {payload.get('size_bytes')}",
            f"sha256_pair_present: {payload.get('sha256_pair_present')}",
            "",
            "policy:",
            "- fetch latest is canonical-first",
            "- dedupe key is bundle filename",
            "- legacy sources cannot override canonical when duplicate names exist",
        ]
        self.bundle_details.setPlainText("\n".join(lines))


def run_smoke(repo_root: Path) -> int:
    policy, route_warnings = load_route_policy(repo_root)
    bundles, scan_warnings = scan_bundles(policy)
    asset_summary = load_asset_summary(repo_root)

    payload = {
        "task_id": TASK_ID,
        "repo_root": str(repo_root),
        "route_policy": {
            "canonical_vm2_outbox": policy.canonical_vm2_outbox,
            "canonical_pc_inbox": policy.canonical_pc_inbox,
            "legacy_scan_dirs": policy.legacy_scan_dirs,
            "source_priority_order": policy.source_priority_order,
        },
        "bundles_discovered": len(bundles),
        "asset_summary": asset_summary,
        "warnings": [*route_warnings, *scan_warnings],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Sanctum v0.4 visual factory prototype")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repo root path")
    parser.add_argument("--smoke", action="store_true", help="Run headless smoke output and exit")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    if args.smoke:
        return run_smoke(repo_root)

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    window = MainWindow(repo_root)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
