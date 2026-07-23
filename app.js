// ============ PERMANENT DEFAULT SETTINGS ============
window.addEventListener('DOMContentLoaded', () => {
const apiBaseInput = el("apiBase");
if (apiBaseInput && !apiBaseInput.value) {
  apiBaseInput.value = "http://127.0.0.1:8000";
}

  const apiKeyInput = el("apiKey");
  if (apiKeyInput && !apiKeyInput.value) {
    apiKeyInput.value = " ";
  }

  checkExistingSession();
});

// ============ STATE ============
let sessionId = null;
let uploadData = null;
let selectedFile = null;
let chartCounter = 0;

const el = (id) => document.getElementById(id);
const apiBase = () => el("apiBase")?.value.trim().replace(/\/$/, "") || "http://127.0.0.1:8000";

// ============ AUTHENTICATION & USER MANAGEMENT ============
const loginScreen = el("loginScreen");
const appRoot = el("appRoot");
const tabLogin = el("tabLogin");
const tabSignup = el("tabSignup");
const authTitle = el("authTitle");
const authSubtitle = el("authSubtitle");
const authForm = el("authForm");
const authEmail = el("authEmail");
const authPassword = el("authPassword");
const authSubmitBtn = el("authSubmitBtn");
const authErrorMsg = el("authErrorMsg");
const togglePasswordBtn = el("togglePasswordBtn");
const logoutBtn = el("logoutBtn");

let authMode = "login"; 

const eyeOpenSvg = `
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon-svg">
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
    <circle cx="12" cy="12" r="3"></circle>
  </svg>
`;
const eyeClosedSvg = `
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon-svg">
    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
    <line x1="1" y1="1" x2="23" y2="23"></line>
  </svg>
`;

function getLoggedInUser() {
  return localStorage.getItem("auditiq-logged-in") || "";
}

function applyPersonalizedGreeting(emailOrName) {
  const users = JSON.parse(localStorage.getItem("auditiq-users") || "{}");
  let name = emailOrName;
  let userObj = users[emailOrName];
  if (userObj && typeof userObj === "object" && userObj.username) {
    name = userObj.username;
  } else if (emailOrName.includes("@")) {
    name = emailOrName.split("@")[0];
  }
  name = name.charAt(0).toUpperCase() + name.slice(1);

  const initialBubbleText = el("initialWelcomeText");
  if (initialBubbleText) {
    initialBubbleText.textContent = `Welcome ${name}! Upload your financial ledger file or ask a question to start a new analysis session.`;
  }
}

function updateAccountButtonAvatar(email) {
  const accountBtn = el("accountBtn");
  if (!accountBtn) return;
  const users = JSON.parse(localStorage.getItem("auditiq-users") || "{}");
  const userObj = users[email];
  const accountImg = accountBtn.querySelector("img");
  if (accountImg) {
    if (userObj && typeof userObj === "object" && userObj.avatar) {
      accountImg.src = userObj.avatar;
    } else {
      accountImg.src = "/static/user-icon.png";
    }
  }
}

function checkExistingSession() {
  const loggedInUser = getLoggedInUser();
  if (loggedInUser && loginScreen && appRoot) {
    loginScreen.classList.add("hidden");
    appRoot.classList.remove("hidden");
    applyPersonalizedGreeting(loggedInUser);
    updateAccountButtonAvatar(loggedInUser);
    loadRecentChats();
  }
}

if (togglePasswordBtn) {
  togglePasswordBtn.addEventListener("click", () => {
    const isPassword = authPassword.type === "password";
    authPassword.type = isPassword ? "text" : "password";
    togglePasswordBtn.innerHTML = isPassword ? eyeClosedSvg : eyeOpenSvg;
  });
}

if (tabLogin && tabSignup) {
  tabLogin.addEventListener("click", () => {
    authMode = "login";
    tabLogin.classList.add("active");
    tabSignup.classList.remove("active");
    authTitle.textContent = "Welcome Back";
    authSubtitle.textContent = "Enter your credentials to access your financial intelligence desk.";
    authSubmitBtn.textContent = "Sign In";
    authErrorMsg.textContent = "";
  });

  tabSignup.addEventListener("click", () => {
    authMode = "signup";
    tabSignup.classList.add("active");
    tabLogin.classList.remove("active");
    authTitle.textContent = "Create Account";
    authSubtitle.textContent = "Sign up with your email to start auditing and forecasting.";
    authSubmitBtn.textContent = "Get Started";
    authErrorMsg.textContent = "";
  });
}

if (authForm) {
  authForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const email = authEmail.value.trim().toLowerCase();
    const password = authPassword.value;
    const usernameInput = el("authUsername")?.value.trim() || "";

    if (!email || !password) {
      authErrorMsg.textContent = "Please fill in all fields.";
      return;
    }

    const users = JSON.parse(localStorage.getItem("auditiq-users") || "{}");

    if (authMode === "login") {
      let userObj = users[email];
      let valid = false;
      if (typeof userObj === "string") {
        valid = userObj === password;
      } else if (userObj && typeof userObj === "object") {
        valid = userObj.password === password;
      }
      
      if (valid) {
        localStorage.setItem("auditiq-logged-in", email);
        loginScreen.classList.add("hidden");
        appRoot.classList.remove("hidden");
        authErrorMsg.textContent = "";
        applyPersonalizedGreeting(email);
        updateAccountButtonAvatar(email);
        loadRecentChats();
      } else {
        authErrorMsg.textContent = "Invalid email or password.";
      }
    } else {
      if (users[email]) {
        authErrorMsg.textContent = "An account with this email already exists.";
      } else {
        users[email] = { password: password, username: usernameInput, avatar: "" };
        localStorage.setItem("auditiq-users", JSON.stringify(users));
        localStorage.setItem("auditiq-logged-in", email);
        loginScreen.classList.add("hidden");
        appRoot.classList.remove("hidden");
        authErrorMsg.textContent = "";
        applyPersonalizedGreeting(email);
        updateAccountButtonAvatar(email);
        loadRecentChats();
      }
    }
  });
}

if (logoutBtn) {
  logoutBtn.addEventListener("click", () => {
    localStorage.removeItem("auditiq-logged-in");
    authEmail.value = "";
    authPassword.value = "";
    loginScreen.classList.remove("hidden");
    appRoot.classList.add("hidden");
  });
}

// ============ ACCOUNT MODAL ============
const accountBtn = el("accountBtn");
const accountModal = el("accountModal");
const closeAccountModal = el("closeAccountModal");
const profileAvatarPreview = el("profileAvatarPreview");
const avatarUpload = el("avatarUpload");
const profileUsername = el("profileUsername");
const profileEmail = el("profileEmail");

if (accountBtn && accountModal) {
  accountBtn.addEventListener("click", () => {
    const email = getLoggedInUser();
    const users = JSON.parse(localStorage.getItem("auditiq-users") || "{}");
    let userObj = users[email] || {};
    
    let username = email.split("@")[0];
    if (typeof userObj === "object" && userObj.username) {
      username = userObj.username;
    }
    
    profileEmail.textContent = email;
    profileUsername.value = username;
    
    if (typeof userObj === "object" && userObj.avatar) {
      profileAvatarPreview.src = userObj.avatar;
    } else {
      profileAvatarPreview.src = "/static/user-icon.png";
    }
    
    accountModal.classList.remove("hidden");
  });
  
  closeAccountModal?.addEventListener("click", () => {
    accountModal.classList.add("hidden");
  });
  
  profileUsername?.addEventListener("change", (e) => {
    const newUsername = e.target.value.trim();
    if (!newUsername) return;
    
    const email = getLoggedInUser();
    const users = JSON.parse(localStorage.getItem("auditiq-users") || "{}");
    
    if (users[email]) {
      if (typeof users[email] === "string") {
        users[email] = { password: users[email], username: newUsername, avatar: "" };
      } else {
        users[email].username = newUsername;
      }
      localStorage.setItem("auditiq-users", JSON.stringify(users));
      
      // Update welcome message if thread is empty/new
      applyPersonalizedGreeting(email);
    }
  });
  
  avatarUpload?.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const base64 = e.target.result;
        profileAvatarPreview.src = base64;
        
        // Save to user object
        const email = getLoggedInUser();
        const users = JSON.parse(localStorage.getItem("auditiq-users") || "{}");
        if (users[email]) {
          if (typeof users[email] === "string") {
            users[email] = { password: users[email], username: email.split("@")[0], avatar: base64 };
          } else {
            users[email].avatar = base64;
          }
          localStorage.setItem("auditiq-users", JSON.stringify(users));
        }
        
        updateAccountButtonAvatar(email);
      };
      reader.readAsDataURL(file);
    }
  });
}

// ============ USER-SPECIFIC RECENT CHAT HISTORY ============
function getUserSessionKey() {
  const user = getLoggedInUser() || "guest";
  return `auditiq-sessions-${user}`;
}

function deleteSessionLocally(id) {
  const key = getUserSessionKey();
  let localSessions = JSON.parse(localStorage.getItem(key) || "[]");
  localSessions = localSessions.filter(s => s.id !== id);
  localStorage.setItem(key, JSON.stringify(localSessions));
  
  if (sessionId === id) {
    el("newChatBtn")?.click();
  } else {
    loadRecentChats();
  }
}

function loadRecentChats() {
  const recentsList = el("recentsList");
  if (!recentsList) return;

  const localSessions = JSON.parse(localStorage.getItem(getUserSessionKey()) || "[]");
  recentsList.innerHTML = "";

  if (localSessions.length > 0) {
    localSessions.forEach((s) => {
      const li = document.createElement("li");
      li.className = "recent-item";
      if (s.id === sessionId) li.classList.add("active");
      li.dataset.sessionId = s.id;
      
      const titleSpan = document.createElement("span");
      titleSpan.className = "recent-item-title";
      titleSpan.textContent = s.title || `Audit Session #${s.id}`;
      titleSpan.addEventListener("click", () => loadChatHistory(s.id, li));
      
      const deleteBtn = document.createElement("button");
      deleteBtn.className = "recent-item-delete";
      deleteBtn.innerHTML = "&times;";
      deleteBtn.title = "Delete Chat";
      deleteBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        if (confirm("Are you sure you want to delete this session?")) {
          deleteSessionLocally(s.id);
        }
      });
      
      li.appendChild(titleSpan);
      li.appendChild(deleteBtn);
      
      recentsList.appendChild(li);
    });
  } else {
    recentsList.innerHTML = `<li class="recent-item" style="color:var(--text-mid); pointer-events:none;">No recent chats</li>`;
  }
}

function saveSessionLocally(id, title) {
  const key = getUserSessionKey();
  let localSessions = JSON.parse(localStorage.getItem(key) || "[]");
  if (!localSessions.some(s => s.id === id)) {
    localSessions.unshift({ id, title: title || `Audit Session #${id}` });
    localStorage.setItem(key, JSON.stringify(localSessions));
  }
  loadRecentChats();
}

async function loadChatHistory(id, targetElement) {
  sessionId = id;
  const thread = el("thread");
  if (thread) thread.innerHTML = "";

  document.querySelectorAll(".recent-item").forEach((item) => item.classList.remove("active"));
  if (targetElement) targetElement.classList.add("active");

  try {
    const res = await fetch(`${apiBase()}/api/chat/history/${id}`);
    const data = await res.json();
    
    if (!res.ok) throw new Error(data.detail || "Failed to load history");

    if (data.upload) {
        uploadData = data.upload;
        addUserMessage(`<div class="file-chip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon-svg"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg> <strong>${escapeHtml(uploadData.filename || 'Uploaded File')}</strong></div>`, false);
        
        const thinking = addAssistantMessage(`<p>✓ Successfully parsed &amp; read <strong>${escapeHtml(uploadData.filename || 'file')}</strong> — ${uploadData.row_count || 0} rows/data elements found.</p>
       <p>You can adjust settings (ticker, report language) if needed, then run the deep financial audit analysis.</p>
       <div class="bubble-actions">
         <button class="mini-btn" data-role="run-analysis">
           <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon-svg"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
           Run Analysis &amp; Generate Reports
         </button>
       </div>`, false);
       thinking.querySelector('[data-role="run-analysis"]').addEventListener("click", (e) => runAnalysis(e.target));
       if (el("kpiTotal")) el("kpiTotal").textContent = uploadData.total ? formatMoney(uploadData.total) : "—";
    }

    if (data.analysis) {
        addUserMessage(`<p>Run Deep Analysis &amp; Generate Reports</p>`, false);
        const analysisBubble = addAssistantMessage(`<p>Loading analysis...</p>`, false);
        renderAnalysisBubble(analysisBubble, data.analysis);
        updateKpis(data.analysis);
    }
  } catch (err) {
    console.error("Failed to fetch history for session:", id, err);
    addAssistantMessage(`<p>✗ Could not load session history: ${escapeHtml(err.message)}</p>`, false);
  }
}

const newChatBtn = el("newChatBtn");
if (newChatBtn) {
  newChatBtn.addEventListener("click", () => {
    sessionId = null;
    uploadData = null;
    selectedFile = null;
    const thread = el("thread");
    const loggedInUser = getLoggedInUser();
    const users = JSON.parse(localStorage.getItem("auditiq-users") || "{}");
    const userObj = users[loggedInUser];
    let name = loggedInUser || "there";
    if (userObj && typeof userObj === "object" && userObj.username) {
      name = userObj.username;
    } else if (loggedInUser.includes("@")) {
      name = loggedInUser.split("@")[0];
    }
    name = name.charAt(0).toUpperCase() + name.slice(1);

    if (thread) {
      thread.innerHTML = `
        <div class="msg assistant">
          <div class="msg-avatar">AI</div>
          <div class="msg-bubble animate-bubble" id="initialWelcomeText">
            Welcome ${name}! Upload your financial ledger file or ask a question to start a new analysis session.
          </div>
        </div>`;
    }
    document.querySelectorAll(".recent-item").forEach((item) => item.classList.remove("active"));
  });
}

// ============ THEME & ATTACHMENTS ============
const themeToggle = el("themeToggle");
const savedTheme = localStorage.getItem("auditiq-theme") || "dark";
document.body.setAttribute("data-theme", savedTheme);

const moonIconSvg = `<svg id="themeIcon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>`;
const sunIconSvg = `<svg id="themeIcon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>`;

function updateBrandLogo(theme) {
  if (el("brandLogo")) el("brandLogo").src = theme === "dark" ? "logo-full-dark.svg" : "logo-full-light.svg";
  if (el("loginLogo")) el("loginLogo").src = theme === "dark" ? "logo-full-dark.svg" : "logo-full-light.svg";
  if (themeToggle) themeToggle.innerHTML = theme === "dark" ? moonIconSvg : sunIconSvg;
}
updateBrandLogo(savedTheme);

if (themeToggle) {
  themeToggle.addEventListener("click", () => {
    const current = document.body.getAttribute("data-theme");
    const next = current === "dark" ? "light" : "dark";
    document.body.setAttribute("data-theme", next);
    localStorage.setItem("auditiq-theme", next);
    updateBrandLogo(next);
  });
}

if (el("settingsToggle")) {
  el("settingsToggle").addEventListener("click", () => {
    el("settingsPanel")?.classList.toggle("open");
  });
}

const attachBtn = el("attachBtn");
const attachMenu = el("attachMenu");

if (attachBtn && attachMenu) {
  attachBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    attachMenu.classList.toggle("open");
  });
  document.addEventListener("click", () => attachMenu.classList.remove("open"));

  attachMenu.querySelectorAll("button").forEach((btn) => {
    btn.addEventListener("click", () => {
      const action = btn.dataset.action;
      attachMenu.classList.remove("open");
      if (action === "file") el("fileInputGeneral")?.click();
      if (action === "photo") el("fileInputPhoto")?.click();
      if (action === "camera") el("fileInputCamera")?.click();
    });
  });
}

["fileInputGeneral", "fileInputPhoto", "fileInputCamera"].forEach((id) => {
  const inputEl = el(id);
  if (inputEl) {
    inputEl.removeAttribute("accept"); // Allow all files including images (.png, .jpg)
    inputEl.addEventListener("change", (e) => {
      if (e.target.files[0]) onFileSelected(e.target.files[0]);
    });
  }
});

function onFileSelected(file) {
  selectedFile = file;
  uploadFile(file);
}

function addUserMessage(html, animate = true) {
  const thread = el("thread");
  const wrap = document.createElement("div");
  wrap.className = "msg user";
  wrap.innerHTML = `<div class="msg-avatar">U</div><div class="msg-bubble ${animate ? "animate-bubble" : ""}">${html}</div>`;
  if (thread) {
    thread.appendChild(wrap);
    thread.scrollTop = thread.scrollHeight;
  }
  return wrap;
}

function addAssistantMessage(html, animate = true) {
  const thread = el("thread");
  const wrap = document.createElement("div");
  wrap.className = "msg assistant";
  wrap.innerHTML = `<div class="msg-avatar">AI</div><div class="msg-bubble ${animate ? "animate-bubble" : ""}">${html}</div>`;
  if (thread) {
    thread.appendChild(wrap);
    thread.scrollTop = thread.scrollHeight;
  }
  return wrap;
}

function typingIndicator() {
  return `<div class="typing-dots"><span></span><span></span><span></span></div>`;
}

function loadingSkeleton() {
  return `<div class="skeleton-block skeleton-text"></div>
          <div class="skeleton-block skeleton-text" style="width: 80%;"></div>
          <div class="skeleton-block skeleton-chart"></div>`;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

function formatChatReply(text) {
  if (!text) return "";

  // Step 1: Extract markdown images and links with placeholder tokens
  // so they don't get HTML-escaped, preserving their URLs intact.
  const tokens = [];
  const addToken = (html) => {
    const key = `\x00T${tokens.length}\x00`;
    tokens.push(html);
    return key;
  };

  // Markdown image: ![alt](url)
  text = text.replace(/!\[([^\]]*)\]\((https?:\/\/[^\)]+)\)/g, (_, alt, url) =>
    addToken(`<div style="margin:8px 0;"><img src="${url}" alt="${escapeHtml(alt)}" style="max-width:100%;border-radius:8px;display:block;"/><a href="${url}" target="_blank" rel="noopener" style="font-size:12px;color:var(--accent);text-decoration:underline;">📥 Download High-Res</a></div>`)
  );

  // Markdown link: [text](url)
  text = text.replace(/\[([^\]]+)\]\((https?:\/\/[^\)]+)\)/g, (_, linkText, url) =>
    addToken(`<a href="${url}" target="_blank" rel="noopener" style="color:var(--accent);text-decoration:underline;font-weight:600;">${escapeHtml(linkText)}</a>`)
  );

  // Step 2: Escape remaining HTML-unsafe characters
  let html = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  // Step 3: Restore the token HTML blocks
  tokens.forEach((tok, idx) => {
    html = html.replace(`\x00T${idx}\x00`, tok);
  });

  // Step 4: Apply remaining markdown
  html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/(?:^|\n)[-*]\s+(.*?)(?=\n|$)/g, '\n<div class="bullet-item">• $1</div>');
  html = html.replace(/\n\n/g, "</p><p>");
  html = html.replace(/\n/g, "<br>");

  return `<p>${html}</p>`;
}

// ============ UPLOAD ============
async function uploadFile(file) {
  addUserMessage(`<div class="file-chip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon-svg"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg> <strong>${escapeHtml(file.name)}</strong></div>`);
  const thinking = addAssistantMessage(`<div class="skeleton-block skeleton-text" style="width: 60%;"></div><div class="skeleton-block skeleton-text" style="width: 80%;"></div>`);

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch(`${apiBase()}/api/upload`, { method: "POST", body: formData });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Upload failed");

    uploadData = data;
    sessionId = data.session_id;

    saveSessionLocally(sessionId, file.name);

    thinking.querySelector(".msg-bubble").innerHTML =
      `<p>✓ Successfully parsed &amp; read <strong>${escapeHtml(data.filename)}</strong> — ${data.row_count || 0} rows/data elements found.</p>
       <p>You can adjust settings (ticker, report language) if needed, then run the deep financial audit analysis.</p>
       <div class="bubble-actions">
         <button class="mini-btn" data-role="run-analysis">
           <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon-svg"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
           Run Analysis &amp; Generate Reports
         </button>
       </div>`;

    thinking.querySelector('[data-role="run-analysis"]').addEventListener("click", (e) => runAnalysis(e.target));
    if (el("kpiTotal")) el("kpiTotal").textContent = data.total ? formatMoney(data.total) : "—";
  } catch (err) {
    thinking.querySelector(".msg-bubble").innerHTML = `<p>✗ Error processing document: ${escapeHtml(err.message)}</p>`;
  }
}

function formatMoney(val) {
  return `₨ ${Number(val).toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
}

// ============ ANALYZE & CHAT ============
async function runAnalysis(triggerBtn) {
  if (!sessionId) return;
  
  // Smart Caching Check
  if (uploadData && uploadData.analysis) {
    if (triggerBtn) {
      triggerBtn.disabled = true;
      triggerBtn.textContent = "Analysis Loaded (Cached)";
    }
    addUserMessage(`<p>Run Deep Analysis &amp; Generate Reports (Cached)</p>`);
    const thinking = addAssistantMessage(`<p>Loading analysis...</p>`, false);
    renderAnalysisBubble(thinking, uploadData.analysis);
    updateKpis(uploadData.analysis);
    return;
  }

  if (triggerBtn) {
    triggerBtn.disabled = true;
    triggerBtn.textContent = "Analyzing & Generating Reports…";
  }

  addUserMessage(`<p>Run Deep Analysis &amp; Generate Reports</p>`);
  const thinking = addAssistantMessage(loadingSkeleton());

  const formData = new FormData();
  formData.append("session_id", sessionId);
  formData.append("ticker", el("ticker")?.value.trim() || "");
  formData.append("language", el("language")?.value || "English");
  formData.append("api_key", el("apiKey")?.value.trim() || "");
  formData.append("horizon", 3);

  try {
    const res = await fetch(`${apiBase()}/api/analyze`, { method: "POST", body: formData });
    const analysis = await res.json();
    if (!res.ok) throw new Error(analysis.detail || "Analysis failed");

    // Cache the analysis
    if (uploadData) uploadData.analysis = analysis;

    renderAnalysisBubble(thinking, analysis);
    updateKpis(analysis);
  } catch (err) {
    thinking.querySelector(".msg-bubble").innerHTML = `<p>✗ Error: ${escapeHtml(err.message)}</p>`;
  }
}

function updateKpis(analysis) {
  const nextVal = analysis.forecast?.next_points?.[0];
  if (el("kpiForecast")) el("kpiForecast").textContent = nextVal !== undefined ? formatMoney(nextVal) : "—";

  const market = analysis.market_data;
  if (el("kpiMarket")) {
    el("kpiMarket").textContent = market?.resolved
      ? `${market.symbol_used} · ${market.current_price}`
      : "Unresolved";
  }
}

function renderAnalysisBubble(msgEl, analysis) {
  chartCounter += 1;
  const chartId = `chart-${chartCounter}`;
  const { report, forecast } = analysis;

  msgEl.querySelector(".msg-bubble").innerHTML = `
    <p><strong>Comprehensive Audit Report &amp; Forecast Ready.</strong></p>
    <canvas class="bubble-chart" id="${chartId}" height="140"></canvas>
    <div class="report-tabs">
      <button class="report-tab active" data-tab="compliance-${chartCounter}">Compliance Audit</button>
      <button class="report-tab" data-tab="forecast-${chartCounter}">Forecast Narrative</button>
    </div>
    <div id="compliance-${chartCounter}" class="report-panel active"><pre>${escapeHtml(report.compliance_report)}</pre></div>
    <div id="forecast-${chartCounter}" class="report-panel"><pre>${escapeHtml(report.narrative_report)}</pre></div>
    <div class="bubble-actions">
      <button class="mini-btn" data-role="audio">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon-svg"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>
        Listen to briefing
      </button>
      <button class="mini-btn" data-role="download">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon-svg"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
        Download Official PDF Report
      </button>
      <button class="mini-btn" data-role="download-csv">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon-svg"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
        Download CSV Data
      </button>
    </div>
    <audio class="bubble-audio" controls style="display:none;"></audio>
  `;

  wireTabs(msgEl);
  wireBubbleActions(msgEl, analysis);

  try {
    drawChart(chartId, uploadData?.series || [], forecast?.next_points || []);
  } catch (err) {
    console.warn("Chart rendering failed:", err);
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

function wireBubbleActions(msgEl, analysis) {
  const audioBtn = msgEl.querySelector('[data-role="audio"]');
  const downloadBtn = msgEl.querySelector('[data-role="download"]');
  const downloadCsvBtn = msgEl.querySelector('[data-role="download-csv"]');
  const audioPlayer = msgEl.querySelector("audio");

  downloadCsvBtn?.addEventListener("click", () => {
    downloadCSV(analysis);
  });

  audioBtn?.addEventListener("click", async () => {
    audioBtn.disabled = true;
    audioBtn.textContent = "Generating Audio…";
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
      audioBtn.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon-svg"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>
        Listen to briefing
      `;
    }
  });

  downloadBtn?.addEventListener("click", () => {
    window.open(`${apiBase()}/api/report/${sessionId}/download`, "_blank");
  });
}

function downloadCSV(analysis) {
  const { forecast } = analysis;
  if (!forecast || !forecast.next_points) return;
  
  let csvContent = "data:text/csv;charset=utf-8,Period,Value\n";
  
  let totalData = uploadData?.series || [];
  totalData.forEach((val, index) => {
    csvContent += `T${index + 1},${val}\n`;
  });
  
  forecast.next_points.forEach((val, index) => {
    csvContent += `F${index + 1} (Forecast),${val}\n`;
  });
  
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", `AuditIQ_Data_${sessionId}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

const messageInput = el("messageInput");
const sendBtn = el("sendBtn");

async function sendChatMessage(text, isVoice = false) {
  if (!text) return;

  addUserMessage(`<p>${escapeHtml(text)}</p>`);
  if (messageInput) messageInput.value = "";
  if (sendBtn) sendBtn.disabled = true;

  const thinking = addAssistantMessage(typingIndicator());

  const formData = new FormData();
  formData.append("message", text);
  formData.append("session_id", sessionId || "");
  formData.append("language", el("language")?.value || "English");
  formData.append("api_key", el("apiKey")?.value.trim() || "");

  try {
    const res = await fetch(`${apiBase()}/api/chat`, { method: "POST", body: formData });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Chat request failed");

    if (data.session_id && !sessionId) {
      sessionId = data.session_id;
      saveSessionLocally(sessionId, text.slice(0, 30));
    }

    const replyHtml = formatChatReply(data.reply);
    thinking.querySelector(".msg-bubble").innerHTML = `
      <p>${replyHtml}</p>
      <div class="bubble-actions">
        <button class="mini-btn" data-role="speak-reply">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon-svg"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>
          Speak Response
        </button>
      </div>
      <audio class="bubble-audio" controls style="display:none;"></audio>
    `;

    wireSpeakReply(thinking, data.reply);

    if (isVoice) {
      const speakBtn = thinking.querySelector('[data-role="speak-reply"]');
      if (speakBtn) speakBtn.click();
    }
  } catch (err) {
    thinking.querySelector(".msg-bubble").innerHTML = `<p>✗ Couldn't reach backend: ${escapeHtml(err.message)}</p>`;
  } finally {
    if (sendBtn) sendBtn.disabled = false;
  }
}

function wireSpeakReply(msgEl, text) {
  const speakBtn = msgEl.querySelector('[data-role="speak-reply"]');
  const audioPlayer = msgEl.querySelector("audio");

  speakBtn?.addEventListener("click", async () => {
    speakBtn.disabled = true;
    speakBtn.textContent = "Generating Speech…";
    try {
      const formData = new FormData();
      formData.append("text", text);
      formData.append("language", el("language")?.value || "English");
      formData.append("speed", 1.25);
      
      const res = await fetch(`${apiBase()}/api/audio-text`, { method: "POST", body: formData });
      if (!res.ok) throw new Error((await res.json()).detail || "Audio generation failed");
      
      const blob = await res.blob();
      audioPlayer.src = URL.createObjectURL(blob);
      audioPlayer.style.display = "block";
      audioPlayer.play();
    } catch (err) {
      alert(err.message);
    } finally {
      speakBtn.disabled = false;
      speakBtn.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon-svg"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>
        Speak Response
      `;
    }
  });
}

function sendTypedMessage() {
  const text = messageInput?.value.trim();
  if (text) sendChatMessage(text, false);
}

if (sendBtn) sendBtn.addEventListener("click", sendTypedMessage);
if (messageInput) {
  messageInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendTypedMessage();
  });
}

// ============ VOICE INPUT ============
const micBtn = el("micBtn");
const SpeechRecognitionClass = window.SpeechRecognition || window.webkitSpeechRecognition;

if (micBtn) {
  if (!SpeechRecognitionClass) {
    micBtn.disabled = true;
  } else {
    const recognition = new SpeechRecognitionClass();
    recognition.continuous = false;
    recognition.interimResults = false;
    let isRecording = false;

    micBtn.addEventListener("click", () => {
      if (isRecording) {
        recognition.stop();
        return;
      }
      recognition.lang = el("language")?.value === "Urdu" ? "ur-PK" : "en-US";
      try { recognition.start(); } catch (err) {}
    });

    recognition.addEventListener("start", () => { isRecording = true; micBtn.classList.add("recording"); });
    recognition.addEventListener("end", () => { isRecording = false; micBtn.classList.remove("recording"); });
    recognition.addEventListener("result", (event) => {
      const transcript = event.results[0][0].transcript;
      if (messageInput) messageInput.value = transcript;
      sendChatMessage(transcript, true);
    });
  }
}

function drawChart(canvasId, historical, forecastPoints) {
  const canvas = el(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
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
        { label: "Recorded", data: historicalData, borderColor: styles.getPropertyValue("--primary") || "#6366f1", tension: 0.25, pointRadius: 2, fill: false },
        { label: "Forecast", data: forecastData, borderColor: styles.getPropertyValue("--accent") || "#a855f7", borderDash: [5, 4], tension: 0.25, pointRadius: 2, fill: false },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { labels: { color: styles.getPropertyValue("--text-mid") || "#ccc" } } },
      scales: {
        x: { ticks: { color: styles.getPropertyValue("--text-mid") || "#ccc" }, grid: { color: styles.getPropertyValue("--border") || "#333" } },
        y: { ticks: { color: styles.getPropertyValue("--text-mid") || "#ccc" }, grid: { color: styles.getPropertyValue(_, i) || "#333" } },
      },
    },
  });
}
