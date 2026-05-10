from pathlib import Path
import re

src = Path(r"E:\IMPERIUM\SANCTUM\sanctum_v0_26.py")
dst = Path(r"E:\IMPERIUM\SANCTUM\sanctum_v0_27.py")

if not src.exists():
    raise FileNotFoundError(src)

code = src.read_text(encoding="utf-8")

code = code.replace(
    'APP_NAME = "IMPERIUM Sanctum v0.26 - Unified Planet Map"',
    'APP_NAME = "IMPERIUM Sanctum v0.27 - Stable Planet Map"'
)

# Disable full-canvas animation redraw. This was causing flicker/blank frames.
code = code.replace(
    '        self.animate()',
    '        # v0.27: no continuous full-canvas redraw; prevents flicker/blank frames.\n        self.after(250, self.draw_all)'
)

# Replace animate method with a safe no-op.
code = re.sub(
    r'    def animate\(self\):\n'
    r'        self\.tick \+= 1\n'
    r'        if self\.current_model:\n'
    r'            self\.draw_unified_map\(self\.current_model\)\n'
    r'        self\.after\(150, self\.animate\)\n',
    '    def animate(self):\n'
    '        # v0.27 stable mode: animation disabled to prevent canvas flicker.\n'
    '        return\n',
    code
)

# Make hover less flickery: only redraw when hover target really changes.
code = code.replace(
    '''        changed = (found != self.hover_stage)
        self.hover_stage = found
        if changed and self.current_model:
            self.draw_unified_map(self.current_model)''',
    '''        changed = (found is not self.hover_stage)
        if changed:
            self.hover_stage = found
            if self.current_model:
                self.draw_unified_map(self.current_model)'''
)

# Update status files.
code = code.replace('"sanctum_version": "0.26"', '"sanctum_version": "0.27"')
code = code.replace(
    '"status": "UNIFIED_PLANET_MAP_EXPERIMENT"',
    '"status": "STABLE_PLANET_MAP_EXPERIMENT"'
)
code = code.replace(
    '"single_unified_map",',
    '"single_unified_map",\n                "stable_render_no_full_canvas_animation",'
)
code = code.replace(
    '# IMPERIUM Sanctum v0.26',
    '# IMPERIUM Sanctum v0.27'
)
code = code.replace(
    'STATUS: UNIFIED_PLANET_MAP_EXPERIMENT',
    'STATUS: STABLE_PLANET_MAP_EXPERIMENT'
)
code = code.replace(
    '- hover metallic detail tooltip;',
    '- hover metallic detail tooltip;\n- stable render: continuous full-canvas animation disabled to prevent flicker;'
)

dst.write_text(code, encoding="utf-8")

print("Created:", dst)
print("Run:")
print(r"python E:\IMPERIUM\SANCTUM\sanctum_v0_27.py")
