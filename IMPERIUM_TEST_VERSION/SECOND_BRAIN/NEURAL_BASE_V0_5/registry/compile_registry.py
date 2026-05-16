"""Compile zone_registry_v0_5.json from parts."""
import json, os

BASE = os.path.dirname(os.path.abspath(__file__))

p1 = json.load(open(os.path.join(BASE, "zone_registry_part1.json"), encoding="utf-8"))
p2 = json.load(open(os.path.join(BASE, "zone_registry_part2.json"), encoding="utf-8"))
p3 = json.load(open(os.path.join(BASE, "zone_registry_part3.json"), encoding="utf-8"))
p4 = json.load(open(os.path.join(BASE, "zone_registry_part4.json"), encoding="utf-8"))

registry = {
    "schema_version": p1["schema_version"],
    "created": p1["created"],
    "scope": p1["scope"],
    "total_zones": p1["total_zones"],
    "zones": (
        p1["zones"] +
        p2["zones_part2"] +
        p3["zones_part3"] +
        p4["zones_part4"]
    )
}

assert len(registry["zones"]) == 12, f"Expected 12 zones, got {len(registry['zones'])}"

out = os.path.join(BASE, "zone_registry_v0_5.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(registry, f, indent=2, ensure_ascii=False)

print(f"OK: zone_registry_v0_5.json written with {len(registry['zones'])} zones")
for z in registry["zones"]:
    print(f"  {z['zone_id']:30s} {z['capability_state']}")
