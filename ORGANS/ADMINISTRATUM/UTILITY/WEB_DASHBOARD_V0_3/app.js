const statusBox = document.getElementById("status");
const resultBox = document.getElementById("result");
const buildBtn = document.getElementById("buildBtn");
const buildState = document.getElementById("buildState");
const buildAnimation = document.getElementById("buildAnimation");
const steps = Array.from(document.querySelectorAll(".step"));

let stepTimer = null;

function setState(kind, text) {
  buildState.className = `build-state ${kind}`;
  buildState.textContent = text;
}

function setAnimation(running) {
  buildAnimation.classList.toggle("running", running);
  buildAnimation.classList.toggle("idle", !running);
}

function startSteps() {
  let index = 0;
  steps.forEach((step) => {
    step.classList.remove("active", "done");
  });

  steps[0]?.classList.add("active");

  stepTimer = window.setInterval(() => {
    steps.forEach((step, i) => {
      step.classList.toggle("done", i < index);
      step.classList.toggle("active", i === index);
    });
    index = (index + 1) % steps.length;
  }, 900);
}

function stopSteps(done) {
  if (stepTimer) {
    window.clearInterval(stepTimer);
    stepTimer = null;
  }

  steps.forEach((step) => {
    step.classList.remove("active");
    step.classList.toggle("done", Boolean(done));
  });
}

function renderJson(target, data) {
  target.textContent = JSON.stringify(data, null, 2);
}

async function loadStatus() {
  try {
    const response = await fetch("/api/status");
    const data = await response.json();
    renderJson(statusBox, data);
  } catch (error) {
    statusBox.textContent = String(error);
  }
}

async function buildResumePack() {
  buildBtn.disabled = true;
  setAnimation(true);
  startSteps();
  setState("running", "Сборка идет: собираю точку продолжения...");
  resultBox.textContent = "Запущен builder. Жду ответ от Администратума...";

  try {
    const response = await fetch("/api/build-resume-continuity-pack", { method: "POST" });
    const data = await response.json();
    renderJson(resultBox, data);

    if (response.ok && data.ok) {
      setState("done", "Готово: resume continuity pack собран.");
      stopSteps(true);
    } else {
      setState("failed", "Сборка завершилась с ошибкой. Смотри JSON ниже.");
      stopSteps(false);
    }
  } catch (error) {
    resultBox.textContent = String(error);
    setState("failed", "Ошибка запроса к dashboard server.");
    stopSteps(false);
  } finally {
    setAnimation(false);
    buildBtn.disabled = false;
  }
}

buildBtn.addEventListener("click", buildResumePack);
loadStatus();
