from pathlib import Path

src_candidates = [
    Path(r"E:\IMPERIUM\SANCTUM\sanctum_v0_23.py"),
    Path(r"E:\IMPERIUM\SANCTUM\sanctum_v0_22.py"),
]

src = None
for p in src_candidates:
    if p.exists():
        src = p
        break

if src is None:
    raise FileNotFoundError("No sanctum_v0_23.py or sanctum_v0_22.py found")

dst = Path(r"E:\IMPERIUM\SANCTUM\sanctum_v0_24.py")
code = src.read_text(encoding="utf-8")

code = code.replace(
    'APP_NAME = "IMPERIUM Sanctum v0.23 — Premium Orbital Shell"',
    'APP_NAME = "IMPERIUM Sanctum v0.24 — Mission Control HUD"'
)
code = code.replace(
    'APP_NAME = "IMPERIUM Sanctum v0.22 — Orbital Route Shell"',
    'APP_NAME = "IMPERIUM Sanctum v0.24 — Mission Control HUD"'
)

# Ensure window title/version markers update even if source title mismatch exists.
code = code.replace("v0.23", "v0.24")
code = code.replace("v0.22", "v0.24")
code = code.replace("Premium Orbital Shell", "Mission Control HUD")
code = code.replace("Orbital Route Shell", "Mission Control HUD")

# Add readiness helpers after _stage_metrics if not already present.
needle = '''    def _draw_hud_metric(self, c, x, y, label, value, color):
        c.create_rectangle(x, y, x + 132, y + 54, fill="#07111f", outline=COLORS["line"], width=1)
        c.create_text(x + 12, y + 9, anchor="nw", fill=COLORS["muted"], font=("Consolas", 8, "bold"), text=label)
        c.create_text(x + 12, y + 26, anchor="nw", fill=color, font=("Consolas", 15, "bold"), text=str(value))
'''

insert = '''    def _draw_hud_metric(self, c, x, y, label, value, color):
        c.create_rectangle(x + 3, y + 3, x + 135, y + 57, fill=COLORS["shadow"], outline="")
        c.create_rectangle(x, y, x + 132, y + 54, fill="#07111f", outline=COLORS["line"], width=1)
        c.create_text(x + 12, y + 9, anchor="nw", fill=COLORS["muted"], font=("Consolas", 8, "bold"), text=label)
        c.create_text(x + 12, y + 26, anchor="nw", fill=color, font=("Consolas", 15, "bold"), text=str(value))

    def _compute_readiness(self, metrics):
        total = max(metrics.get("total", 0), 1)
        passed = metrics.get("passed", 0)
        active = metrics.get("active", 0)
        blocked = metrics.get("blocked", 0)
        readiness = int(((passed + active * 0.5) / total) * 100)
        risk = min(100, blocked * 35)
        return readiness, risk

    def _draw_progress_bar(self, c, x, y, w, label, value, color):
        value = max(0, min(100, int(value)))
        c.create_rectangle(x, y, x + w, y + 34, fill="#07111f", outline=COLORS["line"], width=1)
        c.create_text(x + 10, y + 8, anchor="nw", fill=COLORS["muted"], font=("Consolas", 8, "bold"), text=label)
        fill_w = int((w - 20) * value / 100)
        c.create_rectangle(x + 10, y + 22, x + 10 + fill_w, y + 26, fill=color, outline=color)
        c.create_text(x + w - 42, y + 8, anchor="nw", fill=color, font=("Consolas", 10, "bold"), text=f"{value}%")
'''

if needle in code:
    code = code.replace(needle, insert)

# Replace header area with bigger Mission Control deck.
old = '''        c.create_rectangle(34, 34, w - 34, 214, fill=COLORS["panel3"], outline=COLORS["line"], width=1)
        c.create_text(58, 56, anchor="nw", fill=COLORS["accent2"], font=("Consolas", 18, "bold"), text="TASK ROUTE CORE")
        c.create_text(58, 91, anchor="nw", fill=COLORS["text"], font=("Consolas", 11, "bold"), text=model["task_id"], width=w-120)
        c.create_text(
            58, 122, anchor="nw", fill=COLORS["muted"], font=("Consolas", 10),
            text=f"route_status: {model['route_status']}     current_stage: {model['current_stage']}",
            width=w-120
        )
        c.create_text(58, 144, anchor="nw", fill=COLORS["muted"], font=("Consolas", 10), text=f"profile: {safe_text(model['pipeline_profile'])}", width=w-120)

        metrics = self._stage_metrics(model.get("stages", []))
        mx = 58
        my = 166
        self._draw_hud_metric(c, mx, my, "STAGES", metrics["total"], COLORS["accent2"])
        self._draw_hud_metric(c, mx + 144, my, "PASS", metrics["passed"], COLORS["good"])
        self._draw_hud_metric(c, mx + 288, my, "ACTIVE", metrics["active"], COLORS["accent"])
        self._draw_hud_metric(c, mx + 432, my, "BLOCK", metrics["blocked"], COLORS["bad"])

        cx = 255
        core_y = 360
'''

new = '''        c.create_rectangle(34, 34, w - 34, 274, fill=COLORS["panel3"], outline=COLORS["line"], width=1)
        c.create_text(58, 56, anchor="nw", fill=COLORS["accent2"], font=("Consolas", 18, "bold"), text="TASK ROUTE CORE")
        c.create_text(58, 91, anchor="nw", fill=COLORS["text"], font=("Consolas", 11, "bold"), text=model["task_id"], width=w-120)
        c.create_text(
            58, 122, anchor="nw", fill=COLORS["muted"], font=("Consolas", 10),
            text=f"route_status: {model['route_status']}     current_stage: {model['current_stage']}",
            width=w-120
        )
        c.create_text(58, 144, anchor="nw", fill=COLORS["muted"], font=("Consolas", 10), text=f"profile: {safe_text(model['pipeline_profile'])}", width=w-120)

        metrics = self._stage_metrics(model.get("stages", []))
        readiness, risk = self._compute_readiness(metrics)

        mx = 58
        my = 166
        self._draw_hud_metric(c, mx, my, "STAGES", metrics["total"], COLORS["accent2"])
        self._draw_hud_metric(c, mx + 144, my, "PASS", metrics["passed"], COLORS["good"])
        self._draw_hud_metric(c, mx + 288, my, "ACTIVE", metrics["active"], COLORS["accent"])
        self._draw_hud_metric(c, mx + 432, my, "BLOCK", metrics["blocked"], COLORS["bad"])

        self._draw_progress_bar(c, 58, 232, 238, "READINESS", readiness, COLORS["good"] if readiness >= 50 else COLORS["warn"])
        self._draw_progress_bar(c, 314, 232, 238, "RISK", risk, COLORS["bad"] if risk > 0 else COLORS["accent"])
        c.create_rectangle(570, 232, w - 58, 266, fill="#07111f", outline=COLORS["line"], width=1)
        c.create_text(584, 241, anchor="nw", fill=COLORS["accent2"], font=("Consolas", 9, "bold"), text="NEXT")
        c.create_text(640, 241, anchor="nw", fill=COLORS["text"], font=("Consolas", 9), text=str((model.get("next_allowed_action") or {}).get("action", "UNKNOWN")), width=w-700)

        cx = 255
        core_y = 425
'''

if old in code:
    code = code.replace(old, new)

# Shift route start lower after bigger header.
code = code.replace('        start_y = 505', '        start_y = 575')
code = code.replace('        start_y = 445', '        start_y = 575')

# Add active-stage spotlight around current stage nodes/card.
old_stage_color = '''            status = st.get("status", "UNKNOWN")
            color = stage_status_color(status)
            stage_id = st.get("stage_id", f"STAGE-{i+1:03d}")
            title = st.get("title", "")
            organ = st.get("organ_or_executor") or st.get("organ") or "UNKNOWN"
'''

new_stage_color = '''            status = st.get("status", "UNKNOWN")
            color = stage_status_color(status)
            stage_id = st.get("stage_id", f"STAGE-{i+1:03d}")
            is_current = stage_id == model.get("current_stage")
            if is_current:
                color = COLORS["accent2"]
            title = st.get("title", "")
            organ = st.get("organ_or_executor") or st.get("organ") or "UNKNOWN"
'''
code = code.replace(old_stage_color, new_stage_color, 1)

old_card = '''            c.create_rectangle(card_x1+6, card_y1+6, card_x2+6, card_y2+6, fill=COLORS["shadow"], outline="")
            c.create_rectangle(card_x1, card_y1, card_x2, card_y2, fill=COLORS["panel"], outline=COLORS["line"], width=1)
'''

new_card = '''            c.create_rectangle(card_x1+6, card_y1+6, card_x2+6, card_y2+6, fill=COLORS["shadow"], outline="")
            outline_color = COLORS["accent2"] if is_current else COLORS["line"]
            fill_color = "#0d2941" if is_current else COLORS["panel"]
            c.create_rectangle(card_x1, card_y1, card_x2, card_y2, fill=fill_color, outline=outline_color, width=2 if is_current else 1)
            if is_current:
                c.create_text(card_x2 - 110, card_y1 + 12, anchor="nw", fill=COLORS["accent2"], font=("Consolas", 9, "bold"), text="CURRENT")
'''
code = code.replace(old_card, new_card, 1)

# Stage board: add top metrics row.
old_stage_header = '''        c.create_rectangle(34, 34, w - 34, 148, fill=COLORS["panel3"], outline=COLORS["line"], width=1)
        c.create_text(58, 58, anchor="nw", fill=COLORS["accent2"], font=("Consolas", 18, "bold"), text="STAGE STATE BOARD")
        c.create_text(
            58, 96, anchor="nw", fill=COLORS["muted"], font=("Consolas", 10),
            text="Карта stage-переходов: что должно произойти, что должно появиться, где PASS / FAIL / BLOCK.",
            width=w-120
        )

        y = 184
'''

new_stage_header = '''        c.create_rectangle(34, 34, w - 34, 186, fill=COLORS["panel3"], outline=COLORS["line"], width=1)
        c.create_text(58, 58, anchor="nw", fill=COLORS["accent2"], font=("Consolas", 18, "bold"), text="STAGE STATE BOARD")
        c.create_text(
            58, 96, anchor="nw", fill=COLORS["muted"], font=("Consolas", 10),
            text="Карта stage-переходов: что должно произойти, что должно появиться, где PASS / FAIL / BLOCK.",
            width=w-120
        )
        metrics = self._stage_metrics(model.get("stages", []))
        self._draw_hud_metric(c, 58, 126, "PASS", metrics["passed"], COLORS["good"])
        self._draw_hud_metric(c, 202, 126, "ACTIVE", metrics["active"], COLORS["accent"])
        self._draw_hud_metric(c, 346, 126, "PLANNED", metrics["planned"], COLORS["warn"])
        self._draw_hud_metric(c, 490, 126, "BLOCK", metrics["blocked"], COLORS["bad"])

        y = 224
'''

if old_stage_header in code:
    code = code.replace(old_stage_header, new_stage_header)

# Make status file version.
code = code.replace('"sanctum_version": "0.23"', '"sanctum_version": "0.24"')
code = code.replace('"sanctum_version": "0.22"', '"sanctum_version": "0.24"')
code = code.replace("PREMIUM_ORBITAL_ROUTE_SHELL_EXPERIMENT", "MISSION_CONTROL_HUD_EXPERIMENT")
code = code.replace("ORBITAL_ROUTE_SHELL_EXPERIMENT", "MISSION_CONTROL_HUD_EXPERIMENT")
code = code.replace("# IMPERIUM Sanctum v0.23", "# IMPERIUM Sanctum v0.24")
code = code.replace("# IMPERIUM Sanctum v0.22", "# IMPERIUM Sanctum v0.24")

dst.write_text(code, encoding="utf-8")

print("Created:", dst)
print("Run:")
print("python E:\\IMPERIUM\\SANCTUM\\sanctum_v0_24.py")
