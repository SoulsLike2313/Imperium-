"""Compile neural_map_v0_5.js from parts."""
import os
BASE = os.path.dirname(os.path.abspath(__file__))
parts = ["neural_map_v0_5_part1.js","neural_map_v0_5_part2.js","neural_map_v0_5_part3.js","neural_map_v0_5_part4.js"]
out_path = os.path.join(BASE, "neural_map_v0_5.js")
with open(out_path, "w", encoding="utf-8") as out:
    for p in parts:
        with open(os.path.join(BASE, p), encoding="utf-8") as f:
            out.write(f.read())
            out.write("\n")
print(f"OK: neural_map_v0_5.js compiled from {len(parts)} parts")
