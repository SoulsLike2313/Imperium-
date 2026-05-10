async function loadStatus() {
  const box = document.getElementById("status");
  try {
    const r = await fetch("/api/status");
    const data = await r.json();
    box.textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    box.textContent = String(e);
  }
}

async function buildResumePack() {
  const btn = document.getElementById("buildBtn");
  const result = document.getElementById("result");
  btn.disabled = true;
  btn.textContent = "Building...";
  result.textContent = "running builder...";
  try {
    const r = await fetch("/api/build-resume-continuity-pack", { method: "POST" });
    const data = await r.json();
    result.textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    result.textContent = String(e);
  } finally {
    btn.disabled = false;
    btn.textContent = "Build Resume Continuity Pack v0.2";
  }
}

document.getElementById("buildBtn").addEventListener("click", buildResumePack);
loadStatus();