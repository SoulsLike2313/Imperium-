const $ = (id) => document.getElementById(id);

function fmt(obj) {
  return JSON.stringify(obj, null, 2);
}

function setLog(text) {
  $("actionLog").textContent = text;
}

async function loadData() {
  const res = await fetch("/api/data?ts=" + Date.now());
  const data = await res.json();

  $("organStatus").textContent = fmt(data.organ_status || {});
  $("continuityHealth").textContent = fmt(data.continuity_health || {});
  $("latestPack").textContent = data.latest_continuity_pack_path || "none";
  $("latestComparison").textContent = data.latest_continuity_comparison_path || "none";
  $("missingEvidence").textContent = fmt(data.missing_evidence || []);
}

async function buildContinuityPack() {
  setLog("Running continuity pack build...");
  const res = await fetch("/api/build-continuity-pack", { method: "POST" });
  const data = await res.json();

  let msg = [];
  msg.push(`build_ok=${data.ok}`);
  msg.push(`build_exit_code=${data.build_exit_code}`);
  if (data.build_result) msg.push("build_result=" + fmt(data.build_result));
  if (data.compare_ran) {
    msg.push(`compare_ok=${data.compare_ok}`);
    msg.push(`compare_exit_code=${data.compare_exit_code}`);
    if (data.compare_result) msg.push("compare_result=" + fmt(data.compare_result));
  }
  if (data.build_stderr) msg.push("build_stderr=" + data.build_stderr);
  if (data.compare_stderr) msg.push("compare_stderr=" + data.compare_stderr);

  setLog(msg.join("\n\n"));
  await loadData();
}

async function openTarget(target) {
  const res = await fetch("/api/open?target=" + encodeURIComponent(target), { method: "POST" });
  const data = await res.json();
  if (!data.ok) {
    setLog("open target failed: " + (data.error || "unknown"));
  }
}

$("btnBuild").addEventListener("click", buildContinuityPack);
$("btnReload").addEventListener("click", loadData);

document.querySelectorAll("[data-open]").forEach((btn) => {
  btn.addEventListener("click", () => openTarget(btn.dataset.open));
});

loadData().catch((err) => setLog("initial load error: " + String(err)));
