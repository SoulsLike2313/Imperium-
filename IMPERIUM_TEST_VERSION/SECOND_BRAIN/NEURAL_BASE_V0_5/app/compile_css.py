"""Compile neural_map_v0_5.css from parts."""
import os
BASE = os.path.dirname(os.path.abspath(__file__))
parts = ["neural_map_v0_5_part1.css","neural_map_v0_5_part2.css","neural_map_v0_5_part3.css","neural_map_v0_5_part4.css"]
out_path = os.path.join(BASE, "neural_map_v0_5.css")
with open(out_path, "w", encoding="utf-8") as out:
    for p in parts:
        with open(os.path.join(BASE, p), encoding="utf-8") as f:
            out.write(f.read())
            out.write("\n")
print(f"OK: neural_map_v0_5.css compiled from {len(parts)} parts")
