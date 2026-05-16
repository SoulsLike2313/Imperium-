/* ═══════════════════════════════════════════════════════════════
   JS Part 2: Neural Canvas — SVG rendering, zones, strands
   ═══════════════════════════════════════════════════════════════ */

const SVG_NS = "http://www.w3.org/2000/svg";

function svgEl(tag, attrs = {}) {
  const el = document.createElementNS(SVG_NS, tag);
  for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
  return el;
}

function renderNeuralCanvas() {
  const svg = document.getElementById("neural-canvas");
  const W = svg.clientWidth  || svg.parentElement.clientWidth  || 800;
  const H = svg.clientHeight || svg.parentElement.clientHeight || 600;

  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);

  const strandsLayer = document.getElementById("strands-layer");
  const zonesLayer   = document.getElementById("zones-layer");
  strandsLayer.innerHTML = "";
  zonesLayer.innerHTML   = "";

  if (!STATE.snapshot || !STATE.snapshot.zones) {
    renderOfflineState(svg, W, H);
    return;
  }

  const zones = STATE.snapshot.zones;
  const strands = STATE.snapshot.strands || [];

  // Build zone position map
  const posMap = {};
  for (const z of zones) {
    const layout = z.layout || {};
    posMap[z.zone_id] = {
      cx: (layout.x / 100) * W,
      cy: (layout.y / 100) * H,
      r:  layout.r || 28
    };
  }

  // ── Render strands ──────────────────────────────────────────────────────────
  for (const strand of strands) {
    const from = posMap[strand.from];
    const to   = posMap[strand.to];
    if (!from || !to) continue;

    const fromZone = zones.find(z => z.zone_id === strand.from);
    const toZone   = zones.find(z => z.zone_id === strand.to);

    // Determine strand color based on zone health
    let strandColor = "rgba(0,215,255,0.15)";
    let strandClass = "strand-primary";
    if (strand.type === "data") {
      strandColor = "rgba(255,179,71,0.12)";
      strandClass = "strand-data";
    } else if (strand.type === "secondary") {
      strandColor = "rgba(122,132,255,0.1)";
      strandClass = "strand-secondary";
    }

    // Dim strand if either zone is MISSING/BLOCKED
    const fromHealth = fromZone ? fromZone.health : "WORKING";
    const toHealth   = toZone   ? toZone.health   : "WORKING";
    if (fromHealth === "MISSING" || toHealth === "MISSING") {
      strandColor = "rgba(61,90,120,0.08)";
    }

    // Calculate control point for curved strand
    const mx = (from.cx + to.cx) / 2;
    const my = (from.cy + to.cy) / 2;
    const dx = to.cx - from.cx;
    const dy = to.cy - from.cy;
    const len = Math.sqrt(dx*dx + dy*dy);
    const curve = len * 0.15;
    const cpx = mx - (dy / len) * curve;
    const cpy = my + (dx / len) * curve;

    // Start/end points on circle edges
    const angle1 = Math.atan2(to.cy - from.cy, to.cx - from.cx);
    const angle2 = Math.atan2(from.cy - to.cy, from.cx - to.cx);
    const sx = from.cx + Math.cos(angle1) * from.r;
    const sy = from.cy + Math.sin(angle1) * from.r;
    const ex = to.cx   + Math.cos(angle2) * to.r;
    const ey = to.cy   + Math.sin(angle2) * to.r;

    const path = svgEl("path", {
      d: `M ${sx} ${sy} Q ${cpx} ${cpy} ${ex} ${ey}`,
      stroke: strandColor,
      "stroke-width": strand.type === "primary" ? "1.5" : "1",
      fill: "none",
      class: strandClass
    });
    strandsLayer.appendChild(path);
  }

  // ── Render zones ────────────────────────────────────────────────────────────
  for (const zone of zones) {
    const pos = posMap[zone.zone_id];
    if (!pos) continue;

    const color = HEALTH_COLOR[zone.health] || "#3d5a78";
    const token = TOKEN_COLOR[zone.visual_token] || color;
    const pulseClass = HEALTH_PULSE_CLASS[zone.health] || "";
    const icon = ZONE_ICONS[zone.zone_id] || "●";
    const isCore = zone.zone_id === "core_brain";

    const g = svgEl("g", {
      class: "zone-node",
      "data-zone-id": zone.zone_id,
      transform: `translate(0,0)`
    });

    if (isCore) {
      // ── Core brain special rendering ──────────────────────────────────────
      // Outer glow
      const outerGlow = svgEl("circle", {
        cx: pos.cx, cy: pos.cy, r: pos.r + 20,
        fill: "url(#grad-core)",
        class: "core-glow-ring",
        opacity: "0.5"
      });
      g.appendChild(outerGlow);

      // Spinning rings
      const ring1 = svgEl("circle", {
        cx: pos.cx, cy: pos.cy, r: pos.r + 8,
        fill: "none",
        stroke: "rgba(0,215,255,0.25)",
        "stroke-width": "1",
        "stroke-dasharray": "4 6",
        class: "ring-spin-cw"
      });
      const ring2 = svgEl("circle", {
        cx: pos.cx, cy: pos.cy, r: pos.r + 16,
        fill: "none",
        stroke: "rgba(255,79,216,0.15)",
        "stroke-width": "1",
        "stroke-dasharray": "3 8",
        class: "ring-spin-ccw"
      });
      g.appendChild(ring1);
      g.appendChild(ring2);

      // Core fill
      const coreFill = svgEl("circle", {
        cx: pos.cx, cy: pos.cy, r: pos.r,
        fill: "url(#grad-core)",
        stroke: "rgba(0,215,255,0.5)",
        "stroke-width": "1.5",
        filter: "url(#glow-strong)",
        class: "zone-circle"
      });
      g.appendChild(coreFill);

      // Health indicator dots around core
      const healthScore = parseInt((STATE.snapshot.health_score || "0/12").split("/")[0]) || 0;
      for (let i = 0; i < 12; i++) {
        const angle = (i / 12) * Math.PI * 2 - Math.PI / 2;
        const dotR = pos.r + 4;
        const dx = pos.cx + Math.cos(angle) * dotR;
        const dy = pos.cy + Math.sin(angle) * dotR;
        const dotColor = i < healthScore ? "#29c272" : "#1a2d4a";
        const dot = svgEl("circle", {
          cx: dx, cy: dy, r: "3",
          fill: dotColor,
          opacity: i < healthScore ? "0.9" : "0.4"
        });
        g.appendChild(dot);
      }

    } else {
      // ── Regular zone ──────────────────────────────────────────────────────
      // Pulse ring (animated)
      if (pulseClass) {
        const pulseRing = svgEl("circle", {
          cx: pos.cx, cy: pos.cy, r: "0",
          fill: color,
          opacity: "0",
          class: pulseClass
        });
        g.appendChild(pulseRing);
      }

      // Zone fill
      const fill = svgEl("circle", {
        cx: pos.cx, cy: pos.cy, r: pos.r,
        fill: `rgba(${hexToRgb(color)},0.12)`,
        stroke: color,
        "stroke-width": zone.health === "WORKING" ? "1.5" : "1",
        opacity: zone.health === "DISABLED" ? "0.3" : "0.85",
        class: "zone-circle"
      });
      g.appendChild(fill);

      // Status dot (top-right)
      const sdAngle = -Math.PI / 4;
      const sdx = pos.cx + Math.cos(sdAngle) * pos.r;
      const sdy = pos.cy + Math.sin(sdAngle) * pos.r;
      const statusDot = svgEl("circle", {
        cx: sdx, cy: sdy, r: "5",
        fill: color,
        stroke: "#04080f",
        "stroke-width": "1.5",
        class: "zone-status-dot"
      });
      g.appendChild(statusDot);
    }

    // Icon text
    const iconText = svgEl("text", {
      x: pos.cx, y: pos.cy + (isCore ? 6 : 5),
      "text-anchor": "middle",
      "dominant-baseline": "middle",
      "font-size": isCore ? "28" : "18",
      "pointer-events": "none",
      opacity: zone.health === "DISABLED" ? "0.3" : "1"
    });
    iconText.textContent = icon;
    g.appendChild(iconText);

    // Label
    const labelY = pos.cy + pos.r + 16;
    const label = svgEl("text", {
      x: pos.cx, y: labelY,
      class: "zone-label",
      fill: zone.health === "DISABLED" ? "#2a3a50" : color,
      "font-size": isCore ? "11" : "9"
    });
    label.textContent = zone.display_name.toUpperCase().replace(" / ", "/");
    g.appendChild(label);

    // Invisible hit area
    const hitArea = svgEl("circle", {
      cx: pos.cx, cy: pos.cy, r: pos.r + 10,
      fill: "transparent",
      cursor: "pointer"
    });
    hitArea.addEventListener("click",      () => openZoneDetail(zone.zone_id));
    hitArea.addEventListener("mouseenter", (e) => showTooltip(e, zone));
    hitArea.addEventListener("mousemove",  (e) => moveTooltip(e));
    hitArea.addEventListener("mouseleave", ()  => hideTooltip());
    g.appendChild(hitArea);

    zonesLayer.appendChild(g);
  }
}

function hexToRgb(hex) {
  const r = parseInt(hex.slice(1,3),16);
  const g = parseInt(hex.slice(3,5),16);
  const b = parseInt(hex.slice(5,7),16);
  return `${r},${g},${b}`;
}

function renderOfflineState(svg, W, H) {
  const zonesLayer = document.getElementById("zones-layer");
  const text = svgEl("text", {
    x: W/2, y: H/2,
    "text-anchor": "middle",
    fill: "#3d5a78",
    "font-size": "16",
    "font-family": "Segoe UI, sans-serif"
  });
  text.textContent = "Сервер недоступен. Запустите server_v0_5.py";
  zonesLayer.appendChild(text);
}

function triggerReceiptSpark() {
  const svg = document.getElementById("neural-canvas");
  const sparksLayer = document.getElementById("sparks-layer");
  const W = svg.clientWidth || 800;
  const H = svg.clientHeight || 600;
  // Find evidence_receipts zone position
  if (STATE.snapshot && STATE.snapshot.zones) {
    const ez = STATE.snapshot.zones.find(z => z.zone_id === "evidence_receipts");
    if (ez && ez.layout) {
      const cx = (ez.layout.x / 100) * W;
      const cy = (ez.layout.y / 100) * H;
      const spark = svgEl("circle", {
        cx, cy, r: "0",
        fill: "rgba(41,194,114,0.5)",
        stroke: "#29c272",
        "stroke-width": "1",
        class: "receipt-spark"
      });
      sparksLayer.appendChild(spark);
      setTimeout(() => spark.remove(), 700);
    }
  }
}

// ── Resize handler ─────────────────────────────────────────────────────────────
let resizeTimer;
window.addEventListener("resize", () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(renderNeuralCanvas, 150);
});
