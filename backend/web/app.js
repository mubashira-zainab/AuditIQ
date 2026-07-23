// ============ STATE ============
let sessionId = null;
let uploadData = null;
let selectedFile = null;
let chartCounter = 0;

const el = (id) => document.getElementById(id);
const apiBase = () => el("apiBase").value.trim().replace(/\/$/, "");

// ============ THEME TOGGLE ============
const themeToggle = el("themeToggle");
const savedTheme = localStorage.getItem("auditiq-theme") || "dark";
document.body.setAttribute("data-theme", savedTheme);
themeToggle.textContent = savedTheme === "dark" ? "🌙" : "☀️";

function updateBrandLogo(theme) {
  el("brandLogo").src = theme === "dark" ? "logo-full-dark.svg" : "logo-full-light.svg";
}
updateBrandLogo(savedTheme);

themeToggle.addEventListener("click", () => {
  const current = document.body.getAttribute("data-theme");
  const next = current === "dark" ? "light" : "dark";
  document.body.setAttribute("data-theme", next);
  themeToggle.textContent = next === "dark" ? "🌙" : "☀️";
  localStorage.setItem("auditiq-theme", next);
  updateBrandLogo(next);
});

// ============ SETTINGS PANEL TOGGLE ============
el("settingsToggle").addEventListener("click", () => {
  el("settingsPanel").classList.toggle("open");
});

// ============ ATTACH MENU ============
const attachBtn = el("attachBtn");
const attachMenu = el("attachMenu");

attachBtn.addEventListener("click", (e) => {
  e.stopPropagation();
  attachMenu.classList.toggle("open");
});
document.addEventListener("click", () => attachMenu.classList.remove("open"));

attachMenu.querySelectorAll("button").forEach((btn) => {
  btn.addEventListener("click", () => {
    const action = btn.dataset.action;
    attachMenu.classList.remove("open");
    if (action === "file") el("fileInputGeneral").click();
    if (action === "photo") el("fileInputPhoto").click();
    if (action === "camera") el("fileInputCamera").click();
  });
});

[["fileInputGeneral"], ["fileInputPhoto"], ["fileInputCamera"]].forEach(([id]) => {
  el(id).addEventListener("change", (e) => {
    if (e.target.files[0]) onFileSelected(e.target.files[0]);
  });
});

function onFileSelected(file) {
  selectedFile = file;
  uploadFile(file);
}

// ============ CHAT HELPERS ============
function addUserMessage(html) {
  const thread = el("thread");
  const wrap = document.createElement("div");
  wrap.className = "msg user";
  wrap.innerHTML = `<div class="msg-avatar">U</div><div class="msg-bubble">${html}</div>`;
  thread.appendChild(wrap);
  thread.scrollTop = thread.scrollHeight;
  return wrap;
}

function addAssistantMessage(html) {
  const thread = el("thread");
  const wrap = document.createElement("div");
  wrap.className = "msg assistant";
  wrap.innerHTML = `<div class="msg-avatar">AI</div><div class="msg-bubble">${html}</div>`;
  thread.appendChild(wrap);
  thread.scrollTop = thread.scrollHeight;
  return wrap;
}

function typingIndicator() {
  return `<div class="typing-dots"><span></span><span></span><span></span></div>`;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

// ============ UPLOAD ============
async function uploadFile(file) {
  addUserMessage(`<div class="file-chip">📎 <strong>${escapeHtml(file.name)}</strong></div>`);
  const thinking = addAssistantMessage(`<p>Uploading &amp; parsing <strong>${escapeHtml(file.name)}</strong>…</p>`);

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch(`${apiBase()}/api/upload`, { method: "POST", body: formData });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Upload failed");

    uploadData = data;
    sessionId = data.session_id;

    thinking.querySelector(".msg-bubble").innerHTML =
      `<p>✓ Parsed <strong>${escapeHtml(data.filename)}</strong> — ${data.row_count} rows found.</p>
       <p>Check ⚙ Settings (ticker, report language) if needed, then run the analysis.</p>
       <div class="bubble-actions">
         <button class="mini-btn" data-role="run-analysis">▶ Run Analysis</button>
       </div>`;

    thinking.querySelector('[data-role="run-analysis"]').addEventListener("click", (e) => runAnalysis(e.target));

    el("kpiTotal").textContent = data.total ? formatMoney(data.total) : "—";
  } catch (err) {
    thinking.querySelector(".msg-bubble").innerHTML = `<p>✗ Error: ${escapeHtml(err.message)}</p>`;
  }
}

function formatMoney(val) {
  return `₨ ${Number(val).toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
}

// ============ ANALYZE ============
async function runAnalysis(triggerBtn) {
  if (!sessionId) return;
  if (triggerBtn) {
    triggerBtn.disabled = true;
    triggerBtn.textContent = "Analyzing…";
  }

  addUserMessage(`<p>Run Analysis</p>`);
  const thinking = addAssistantMessage(typingIndicator());

  const formData = new FormData();
  formData.append("session_id", sessionId);
  formData.append("ticker", el("ticker").value.trim());
  formData.append("language", el("language").value);
  formData.append("api_key", el("apiKey").value.trim());
  formData.append("horizon", 3);

  try {
    const res = await fetch(`${apiBase()}/api/analyze`, { method: "POST", body: formData });
    const analysis = await res.json();
    if (!res.ok) throw new Error(analysis.detail || "Analysis failed");

    renderAnalysisBubble(thinking, analysis);
    updateKpis(analysis);
  } catch (err) {
    thinking.querySelector(".msg-bubble").innerHTML = `<p>✗ Error: ${escapeHtml(err.message)}</p>`;
  }
}

function updateKpis(analysis) {
  const nextVal = analysis.forecast?.next_points?.[0];
  el("kpiForecast").textContent = nextVal !== undefined ? formatMoney(nextVal) : "—";

  const market = analysis.market_data;
  el("kpiMarket").textContent = market?.resolved
    ? `${market.symbol_used} · ${market.current_price}`
    : "Unresolved";
}

function renderAnalysisBubble(msgEl, analysis) {
  chartCounter += 1;
  const chartId = `chart-${chartCounter}`;
  const { report, forecast } = analysis;

  const offlineBadge = report.mode === "offline" ? `<span class="badge-offline">Offline preview mode</span><br>` : "";

  msgEl.querySelector(".msg-bubble").innerHTML = `
    ${offlineBadge}
    <p><strong>Report ready.</strong></p>
    <canvas class="bubble-chart" id="${chartId}" height="140"></canvas>
    <div class="report-tabs">
      <button class="report-tab active" data-tab="compliance-${chartCounter}">Compliance</button>
      <button class="report-tab" data-tab="forecast-${chartCounter}">Forecast Narrative</button>
    </div>
    <div id="compliance-${chartCounter}" class="report-panel active"><pre>${escapeHtml(report.compliance_report)}</pre></div>
    <div id="forecast-${chartCounter}" class="report-panel"><pre>${escapeHtml(report.narrative_report)}</pre></div>
    <div class="bubble-actions">
      <button class="mini-btn" data-role="audio">🔊 Listen to briefing</button>
      <button class="mini-btn" data-role="download">⬇ Download Report</button>
    </div>
    <audio class="bubble-audio" controls style="display:none;"></audio>
  `;

  wireTabs(msgEl);
  wireBubbleActions(msgEl);

  try {
    drawChart(chartId, uploadData?.series || [], forecast?.next_points || []);
  } catch (err) {
    console.warn("Chart rendering failed (report and buttons are unaffected):", err);
    const canvas = el(chartId);
    if (canvas) canvas.outerHTML = `<p style="color:var(--text-mid); font-size:12px;">Chart unavailable (couldn't load the charting library).</p>`;
  }
}

function wireTabs(msgEl) {
  msgEl.querySelectorAll(".report-tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      const bubble = tab.closest(".msg-bubble");
      bubble.querySelectorAll(".report-tab").forEach((t) => t.classList.remove("active"));
      bubble.querySelectorAll(".report-panel").forEach((p) => p.classList.remove("active"));
      tab.classList.add("active");
      bubble.querySelector(`#${tab.dataset.tab}`).classList.add("active");
    });
  });
}

function wireBubbleActions(msgEl) {
  const audioBtn = msgEl.querySelector('[data-role="audio"]');
  const downloadBtn = msgEl.querySelector('[data-role="download"]');
  const audioPlayer = msgEl.querySelector("audio");

  audioBtn.addEventListener("click", async () => {
    audioBtn.disabled = true;
    audioBtn.textContent = "Generating…";
    try {
      const formData = new FormData();
      formData.append("session_id", sessionId);
      formData.append("speed", 1.25);
      const res = await fetch(`${apiBase()}/api/audio`, { method: "POST", body: formData });
      if (!res.ok) throw new Error((await res.json()).detail || "Audio failed");
      const blob = await res.blob();
      audioPlayer.src = URL.createObjectURL(blob);
      audioPlayer.style.display = "block";
      audioPlayer.play();
    } catch (err) {
      alert(err.message);
    } finally {
      audioBtn.disabled = false;
      audioBtn.textContent = "🔊 Listen to briefing";
    }
  });

  downloadBtn.addEventListener("click", () => {
    window.open(`${apiBase()}/api/report/${sessionId}/download`, "_blank");
  });
}

// ============ CHAT TEXT INPUT ============
const messageInput = el("messageInput");
const sendBtn = el("sendBtn");

async function sendTypedMessage() {
  const text = messageInput.value.trim();
  if (!text) return;

  addUserMessage(`<p>${escapeHtml(text)}</p>`);
  messageInput.value = "";
  sendBtn.disabled = true;

  const thinking = addAssistantMessage(typingIndicator());

  const formData = new FormData();
  formData.append("message", text);
  formData.append("session_id", sessionId || "");
  formData.append("language", el("language").value);
  formData.append("api_key", el("apiKey").value.trim());

  try {
    const res = await fetch(`${apiBase()}/api/chat`, { method: "POST", body: formData });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Chat request failed");

    const offlineBadge = data.mode === "offline" ? `<span class="badge-offline">Offline preview mode</span><br>` : "";
    thinking.querySelector(".msg-bubble").innerHTML = `${offlineBadge}<p>${escapeHtml(data.reply)}</p>`;
  } catch (err) {
    thinking.querySelector(".msg-bubble").innerHTML = `<p>✗ Couldn't reach the backend: ${escapeHtml(err.message)}. Is the server running at ${escapeHtml(apiBase())}?</p>`;
  } finally {
    sendBtn.disabled = false;
  }
}

sendBtn.addEventListener("click", sendTypedMessage);
messageInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendTypedMessage();
});

// ============ VOICE INPUT (speech-to-text) ============
const micBtn = el("micBtn");
const SpeechRecognitionClass = window.SpeechRecognition || window.webkitSpeechRecognition;

if (!SpeechRecognitionClass) {
  micBtn.disabled = true;
  micBtn.title = "Voice input isn't supported in this browser (try Chrome or Edge)";
} else {
  const recognition = new SpeechRecognitionClass();
  recognition.continuous = false;
  recognition.interimResults = false;
  let isRecording = false;

  function speechLangCode() {
    const language = el("language").value;
    return language === "Urdu" ? "ur-PK" : "en-US";
  }

  micBtn.addEventListener("click", () => {
    if (isRecording) {
      recognition.stop();
      return;
    }
    recognition.lang = speechLangCode();
    try {
      recognition.start();
    } catch (err) {
      console.warn("Could not start voice input:", err);
    }
  });

  recognition.addEventListener("start", () => {
    isRecording = true;
    micBtn.classList.add("recording");
    micBtn.title = "Listening… click to stop";
  });

  recognition.addEventListener("end", () => {
    isRecording = false;
    micBtn.classList.remove("recording");
    micBtn.title = "Speak instead of typing";
  });

  recognition.addEventListener("result", (event) => {
    const transcript = event.results[0][0].transcript;
    messageInput.value = transcript;
    messageInput.focus();
  });

  recognition.addEventListener("error", (event) => {
    console.warn("Voice input error:", event.error);
    if (event.error === "not-allowed" || event.error === "service-not-allowed") {
      addAssistantMessage(`<p>Microphone access was blocked. Please allow microphone permission in your browser to use voice input.</p>`);
    }
  });
}
// ============ CHART ============
function drawChart(canvasId, historical, forecastPoints) {
  const ctx = el(canvasId).getContext("2d");
  const labels = [...historical.map((_, i) => `T${i + 1}`), ...forecastPoints.map((_, i) => `F${i + 1}`)];
  const historicalData = [...historical, ...Array(forecastPoints.length).fill(null)];
  const forecastData = [
    ...Array(Math.max(historical.length - 1, 0)).fill(null),
    ...(historical.length ? [historical[historical.length - 1]] : []),
    ...forecastPoints,
  ];

  const styles = getComputedStyle(document.body);

  new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        { label: "Recorded", data: historicalData, borderColor: styles.getPropertyValue("--primary"), tension: 0.25, pointRadius: 2, fill: false },
        { label: "Forecast", data: forecastData, borderColor: styles.getPropertyValue("--accent"), borderDash: [5, 4], tension: 0.25, pointRadius: 2, fill: false },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { labels: { color: styles.getPropertyValue("--text-mid") } } },
      scales: {
        x: { ticks: { color: styles.getPropertyValue("--text-mid") }, grid: { color: styles.getPropertyValue("--border") } },
        y: { ticks: { color: styles.getPropertyValue("--text-mid") }, grid: { color: styles.getPropertyValue("--border") } },
      },
    },
  });
}
