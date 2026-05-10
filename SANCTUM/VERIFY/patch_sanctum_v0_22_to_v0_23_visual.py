from pathlib import Path

src = Path(r"E:\IMPERIUM\SANCTUM\sanctum_v0_22.py")
dst = Path(r"E:\IMPERIUM\SANCTUM\sanctum_v0_23.py")

code = src.read_text(encoding="utf-8")

code = code.replace(
    'APP_NAME = "IMPERIUM Sanctum v0.22 — Orbital Route Shell"',
    'APP_NAME = "IMPERIUM Sanctum v0.23 — Premium Orbital Shell"'
)

code = code.replace(
    '"bg": "#050c18",',
    '"bg": "#030815",'
)

code = code.replace(
    '"panel": "#08182b",',
    '"panel": "#071629",'
)

code = code.replace(
    '"panel2": "#0c2036",',
    '"panel2": "#091d33",'
)

code = code.replace(
    '"panel3": "#123758",',
    '"panel3": "#103456",'
)

code = code.replace(
    'self.title(APP_NAME)\n        self.geometry("1700x1000")',
    'self.title(APP_NAME)\n        self.geometry("1760x1020")'
)

# Make scrollbars dark-ish by replacing ScrollCanvas implementation.
old_scroll = '''class ScrollCanvas(tk.Frame):
    def __init__(self, master, bg):
        super().__init__(master, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        self.vbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def clear(self):
        self.canvas.delete("all")

    def set_scroll(self, width, height):
        self.canvas.configure(scrollregion=(0, 0, width, height))
'''

new_scroll = '''class ScrollCanvas(tk.Frame):
    def __init__(self, master, bg):
        super().__init__(master, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        self.vbar = tk.Scrollbar(
            self,
            orient=tk.VERTICAL,
            command=self.canvas.yview,
            bg=COLORS["panel"],
            troughcolor=COLORS["panel4"],
            activebackground=COLORS["accent"],
            relief="flat",
            bd=0,
            width=12
        )
        self.canvas.configure(yscrollcommand=self.vbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def clear(self):
        self.canvas.delete("all")

    def set_scroll(self, width, height):
        self.canvas.configure(scrollregion=(0, 0, width, height))
'''

code = code.replace(old_scroll, new_scroll)

# Add HUD metrics function after _draw_grid.
insert_after = '''    def _draw_grid(self, c, w, h):
        for x in range(0, w, 32):
            c.create_line(x, 0, x, h, fill="#0d2438")
        for y in range(0, h, 32):
            c.create_line(0, y, w, y, fill="#0d2438")
        c.create_rectangle(18, 18, w - 18, h - 18, outline=COLORS["line"], width=1)
'''

hud_func = '''    def _draw_grid(self, c, w, h):
        for x in range(0, w, 32):
            c.create_line(x, 0, x, h, fill="#0a2035")
        for y in range(0, h, 32):
            c.create_line(0, y, w, y, fill="#0a2035")
        # soft frame stack
        c.create_rectangle(14, 14, w - 14, h - 14, outline="#102b44", width=1)
        c.create_rectangle(22, 22, w - 22, h - 22, outline=COLORS["line"], width=1)

    def _stage_metrics(self, stages):
        total = len(stages or [])
        passed = len([s for s in stages if "PASS" in str(s.get("status", "")).upper()])
        active = len([s for s in stages if "ACTIVE" in str(s.get("status", "")).upper()])
        planned = len([s for s in stages if "PLAN" in str(s.get("status", "")).upper()])
        blocked = len([s for s in stages if "BLOCK" in str(s.get("status", "")).upper() or "FAIL" in str(s.get("status", "")).upper()])
        return {
            "total": total,
            "passed": passed,
            "active": active,
            "planned": planned,
            "blocked": blocked,
        }

    def _draw_hud_metric(self, c, x, y, label, value, color):
        c.create_rectangle(x, y, x + 132, y + 54, fill="#07111f", outline=COLORS["line"], width=1)
        c.create_text(x + 12, y + 9, anchor="nw", fill=COLORS["muted"], font=("Consolas", 8, "bold"), text=label)
        c.create_text(x + 12, y + 26, anchor="nw", fill=color, font=("Consolas", 15, "bold"), text=str(value))
'''

code = code.replace(insert_after, hud_func)

# Make header lower and add metrics in route map.
old_header = '''        c.create_rectangle(34, 34, w - 34, 176, fill=COLORS["panel3"], outline=COLORS["line"], width=1)
        c.create_text(58, 58, anchor="nw", fill=COLORS["accent2"], font=("Consolas", 18, "bold"), text="TASK ROUTE CORE")
        c.create_text(58, 94, anchor="nw", fill=COLORS["text"], font=("Consolas", 11, "bold"), text=model["task_id"], width=w-120)
        c.create_text(
            58, 126, anchor="nw", fill=COLORS["muted"], font=("Consolas", 10),
            text=f"route_status: {model['route_status']}     current_stage: {model['current_stage']}",
            width=w-120
        )
        c.create_text(58, 148, anchor="nw", fill=COLORS["muted"], font=("Consolas", 10), text=f"profile: {safe_text(model['pipeline_profile'])}", width=w-120)

        cx = 255
        core_y = 310
'''

new_header = '''        c.create_rectangle(34, 34, w - 34, 214, fill=COLORS["panel3"], outline=COLORS["line"], width=1)
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

code = code.replace(old_header, new_header)

# Shift route start lower after header.
code = code.replace('        start_y = 445', '        start_y = 505')

# Make route cards shorter and cleaner.
code = code.replace(
    '                card_x1 = 340\n            card_x2 = w - 60',
    '                card_x1 = 332\n            card_x2 = w - 76'
)

code = code.replace(
    '            c.create_text(card_x1+16, card_y1+64, anchor="nw", fill=COLORS["muted"], font=("Consolas", 9), text="ENTRY → DO STAGE → VALIDATE → RECEIPT → NEXT", width=card_x2-card_x1-32)',
    '            c.create_text(card_x1+16, card_y1+64, anchor="nw", fill=COLORS["muted"], font=("Consolas", 9), text="ENTRY → VALIDATE → RECEIPT → NEXT", width=card_x2-card_x1-32)'
)

# Make orbital core stronger by increasing radii and adding title near it.
code = code.replace(
    '        self._draw_orbital_core(c, cx, core_y, radius=82)',
    '        self._draw_orbital_core(c, cx, core_y, radius=104)\n        c.create_text(cx, core_y + 132, anchor="n", fill=COLORS["accent2"], font=("Consolas", 10, "bold"), text="ACTIVE TASK CORE")'
)

code = code.replace(
    '                if i == 0:\n                c.create_line(cx, core_y + 82, cx, y - 28, fill=COLORS["accent"], width=2)',
    '                if i == 0:\n                c.create_line(cx, core_y + 124, cx, y - 28, fill=COLORS["accent"], width=2)'
)

# Simplify right stage cards expected artifact placement, avoid text overlap.
old_expected = '''            c.create_text(60, y+100, anchor="nw", fill=COLORS["accent"], font=("Consolas", 9, "bold"), text="expected artifacts:")
            for i, art in enumerate(expected):
                x = 220 + (i % 2) * 250
                yy = y + 100 + (i // 2) * 17
                c.create_text(x, yy, anchor="nw", fill=COLORS["text"], font=("Consolas", 9), text=f"• {art}", width=235)

            y += card_h + 18
'''

new_expected = '''            c.create_text(60, y+100, anchor="nw", fill=COLORS["accent"], font=("Consolas", 9, "bold"), text="expected:")
            compact = "  •  ".join(expected[:4])
            if len(compact) > 115:
                compact = compact[:112] + "..."
            c.create_text(150, y+100, anchor="nw", fill=COLORS["text"], font=("Consolas", 9), text=compact, width=w-230)

            y += card_h + 18
'''

code = code.replace(old_expected, new_expected)

# Add premium bottom legend status by changing status label text.
code = code.replace(
    'value="Status: SANCTUM_CLIENT_SHELL_ONLY | ORBITAL_ROUTE_MAP_V0_22 | NOT_SOURCE_OF_TRUTH"',
    'value="Status: SANCTUM_CLIENT_SHELL_ONLY | PREMIUM_ROUTE_MAP_V0_23 | NOT_SOURCE_OF_TRUTH | FILES_ARE_TRUTH"'
)

code = code.replace(
    '"sanctum_version": "0.22",',
    '"sanctum_version": "0.23",'
)

code = code.replace(
    '"status": "ORBITAL_ROUTE_SHELL_EXPERIMENT",',
    '"status": "PREMIUM_ORBITAL_ROUTE_SHELL_EXPERIMENT",'
)

code = code.replace(
    'ORBITAL_ROUTE_SHELL_EXPERIMENT',
    'PREMIUM_ORBITAL_ROUTE_SHELL_EXPERIMENT'
)

code = code.replace(
    '# IMPERIUM Sanctum v0.22',
    '# IMPERIUM Sanctum v0.23'
)

code = code.replace(
    'Changes:\n- animated orbital task core;',
    'Changes:\n- stronger premium HUD metrics;\n- darker scrollbars;\n- bigger animated orbital task core;'
)

dst.write_text(code, encoding="utf-8")

print("Created:", dst)
print("Run:")
print("python E:\\IMPERIUM\\SANCTUM\\sanctum_v0_23.py")
