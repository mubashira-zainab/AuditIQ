/* =========================================================
   AuditIQ — Financial Intelligence Desk
   app.js  — Full professional rewrite
   ========================================================= */

'use strict';

// ─── HELPERS ───────────────────────────────────────────────────────────────

const el  = (id)   => document.getElementById(id);
const qs  = (sel)  => document.querySelector(sel);
const qsa = (sel)  => document.querySelectorAll(sel);

const apiBase = () =>
  (el('apiBase')?.value.trim().replace(/\/$/, '')) || 'http://127.0.0.1:8000';

function escapeHtml(str) {
  const d = document.createElement('div');
  d.textContent = str ?? '';
  return d.innerHTML;
}

// ─── ICONS (SVG, replaces emoji everywhere in the UI) ──────────────────────
const ICON_DOC      = `<svg class="inline-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>`;
const ICON_IMAGE     = `<svg class="inline-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>`;
const ICON_DOWNLOAD  = `<svg class="inline-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>`;
const ICON_CHECK     = `<svg class="inline-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>`;
const ICON_X         = `<svg class="inline-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>`;
const ICON_PLAY      = `<svg class="inline-icon" viewBox="0 0 24 24" fill="currentColor" stroke="none"><polygon points="5 3 19 12 5 21 5 3"/></svg>`;
const ICON_GEAR      = `<svg class="inline-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>`;
const ICON_INFO      = `<svg class="inline-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>`;
const ICON_WARNING   = `<svg class="inline-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`;
const ICON_SPEAKER   = `<svg class="inline-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>`;
const ICON_CLIPBOARD = `<svg class="inline-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 2h6a1 1 0 0 1 1 1v2H8V3a1 1 0 0 1 1-1z"/><rect x="6" y="4" width="12" height="18" rx="2"/><line x1="9" y1="11" x2="15" y2="11"/><line x1="9" y1="15" x2="15" y2="15"/></svg>`;
const ICON_TRENDING  = `<svg class="inline-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>`;

// ─── TOAST SYSTEM ──────────────────────────────────────────────────────────

/**
 * showToast(message, type, duration)
 * type: 'success' | 'error' | 'info' | 'warning'
 */
function showToast(message, type = 'info', duration = 3500) {
  const container = el('toastContainer');
  if (!container) return;

  const icons = {
    success: ICON_CHECK,
    error:   ICON_X,
    info:    ICON_INFO,
    warning: ICON_WARNING,
  };

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.setAttribute('role', 'alert');
  toast.innerHTML = `
    <span class="toast-icon">${icons[type] || 'ℹ'}</span>
    <span class="toast-msg">${escapeHtml(message)}</span>
    <button class="toast-close" aria-label="Dismiss">×</button>
  `;

  const dismiss = () => {
    toast.classList.add('toast-out');
    toast.addEventListener('animationend', () => toast.remove(), { once: true });
  };

  toast.querySelector('.toast-close').addEventListener('click', dismiss);
  container.appendChild(toast);

  // Force reflow so animation plays
  toast.getBoundingClientRect();
  toast.classList.add('toast-in');

  setTimeout(dismiss, duration);
}

// ─── CUSTOM CONFIRM MODAL ──────────────────────────────────────────────────

function showConfirm(message, title = 'Confirm') {
  return new Promise((resolve) => {
    const modal  = el('confirmModal');
    const msgEl  = el('confirmMsg');
    const titleEl = el('confirmTitle');
    const okBtn  = el('confirmOk');
    const cancelBtn = el('confirmCancel');

    if (!modal) { resolve(window.confirm(message)); return; }

    titleEl.textContent = title;
    msgEl.textContent   = message;
    modal.classList.remove('hidden');

    const cleanup = (result) => {
      modal.classList.add('hidden');
      okBtn.removeEventListener('click', onOk);
      cancelBtn.removeEventListener('click', onCancel);
      resolve(result);
    };
    const onOk     = () => cleanup(true);
    const onCancel = () => cleanup(false);

    okBtn.addEventListener('click', onOk);
    cancelBtn.addEventListener('click', onCancel);
  });
}

// ─── STATE ────────────────────────────────────────────────────────────────

let sessionId   = null;
let uploadData  = null;
let chartCounter = 0;
let authMode    = 'login';

// ─── THEME ────────────────────────────────────────────────────────────────

const savedTheme = localStorage.getItem('auditiq-theme') || 'dark';
document.body.setAttribute('data-theme', savedTheme);

function updateBrandLogo(theme) {
  const dark = 'logo-full-dark.svg';
  const light = 'logo-full-light.svg';
  const logo = el('brandLogo');
  if (logo) logo.src = theme === 'dark' ? dark : light;
  const loginLogo = el('loginLogo');
  if (loginLogo) loginLogo.src = theme === 'dark' ? dark : light;
}
updateBrandLogo(savedTheme);

el('themeToggle')?.addEventListener('click', () => {
  const next = document.body.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  document.body.setAttribute('data-theme', next);
  localStorage.setItem('auditiq-theme', next);
  updateBrandLogo(next);
});

// ─── AUTH HELPERS ────────────────────────────────────────────────────────

function getAuthToken()     { return localStorage.getItem('auditiq-token') || ''; }
function getLoggedInUser()  { return localStorage.getItem('auditiq-logged-in') || ''; }
function getUsername()      { return localStorage.getItem('auditiq-username') || ''; }
function getAvatar()        { return localStorage.getItem('auditiq-avatar') || ''; }

function authHeader() {
  const token = getAuthToken();
  return token ? { 'Authorization': `Bearer ${token}` } : {};
}

function getUserDisplayName(email) {
  const uname = getUsername();
  if (uname) return uname.charAt(0).toUpperCase() + uname.slice(1);
  if (email.includes('@')) return email.split('@')[0].charAt(0).toUpperCase() + email.split('@')[0].slice(1);
  return email;
}

function getUserSessionKey() {
  return `auditiq-sessions-${getLoggedInUser() || 'guest'}`;
}

// ─── AUTH FORM ────────────────────────────────────────────────────────────

el('tabLogin')?.addEventListener('click', () => {
  authMode = 'login';
  el('tabLogin').classList.add('active');
  el('tabSignup').classList.remove('active');
  el('authTitle').textContent    = 'Welcome Back';
  el('authSubtitle').textContent = 'Enter your credentials to access your financial intelligence desk.';
  el('authSubmitBtn').textContent = 'Sign In';
  el('authErrorMsg').textContent = '';
  el('usernameGroup').style.display = 'none';
});

el('tabSignup')?.addEventListener('click', () => {
  authMode = 'signup';
  el('tabSignup').classList.add('active');
  el('tabLogin').classList.remove('active');
  el('authTitle').textContent    = 'Create Account';
  el('authSubtitle').textContent = 'Sign up to start auditing and forecasting with AI.';
  el('authSubmitBtn').textContent = 'Get Started';
  el('authErrorMsg').textContent = '';
  el('usernameGroup').style.display = 'block';
});

// Password toggle
el('togglePasswordBtn')?.addEventListener('click', () => {
  const pwd = el('authPassword');
  if (!pwd) return;
  const show = pwd.type === 'password';
  pwd.type = show ? 'text' : 'password';
  el('eyeIcon').innerHTML = show
    ? '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/>'
    : '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>';
});

el('authForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const email    = el('authEmail')?.value.trim().toLowerCase();
  const password = el('authPassword')?.value;
  const username = el('authUsername')?.value.trim() || '';
  const errEl    = el('authErrorMsg');

  if (!email || !password) { errEl.textContent = 'Please fill in all fields.'; return; }

  const btn = el('authSubmitBtn');
  const originalText = btn.textContent;
  btn.textContent = 'Please wait...';
  btn.disabled = true;

  try {
    const endpoint = authMode === 'login' ? '/api/auth/login' : '/api/auth/register';
    const body = authMode === 'login' ? { email, password } : { email, password, username };
    
    const res = await fetch(`${apiBase()}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Authentication failed');
    
    loginUser(data.token, data.user);
  } catch (err) {
    errEl.textContent = err.message;
  } finally {
    btn.textContent = originalText;
    btn.disabled = false;
  }
});

function loginUser(token, user) {
  localStorage.setItem('auditiq-token', token);
  localStorage.setItem('auditiq-logged-in', user.email);
  localStorage.setItem('auditiq-username', user.username || '');
  localStorage.setItem('auditiq-avatar', user.avatar || '');
  
  el('loginScreen').classList.add('hidden');
  el('appRoot').classList.remove('hidden');
  el('authErrorMsg').textContent = '';
  
  applyUserUI(user.email);
  syncSessionsFromAPI();
  showToast('Welcome back!', 'success');
}

function applyUserUI(email) {
  const name = getUserDisplayName(email);
  if (el('displayUsername')) el('displayUsername').textContent = name;
  if (el('displayEmail'))    el('displayEmail').textContent    = email;

  const welcomeEl = el('initialWelcomeText');
  if (welcomeEl) {
    welcomeEl.innerHTML = `<p>Welcome <strong>${escapeHtml(name)}</strong>! Upload your financial ledger or ask a question to start a new analysis session.</p>
    <p class="sub-text">Reports can be generated in English, Roman Urdu, or Urdu. Configure in ${ICON_GEAR} Settings.</p>`;
  }

  // Avatar
  const avatar = getAvatar();
  if (avatar && el('userAvatarImg')) el('userAvatarImg').src = avatar;
}

// Logout
el('logoutBtn')?.addEventListener('click', () => {
  localStorage.removeItem('auditiq-token');
  localStorage.removeItem('auditiq-logged-in');
  localStorage.removeItem('auditiq-username');
  localStorage.removeItem('auditiq-avatar');
  
  el('appRoot').classList.add('hidden');
  el('loginScreen').classList.remove('hidden');
  if(el('authEmail')) el('authEmail').value = '';
  if(el('authPassword')) el('authPassword').value = '';
  sessionId  = null;
  uploadData = null;
  showToast('Logged out successfully.', 'info');
});

// ─── ACCOUNT MODAL ────────────────────────────────────────────────────────

el('accountBtn')?.addEventListener('click', () => {
  const email = getLoggedInUser();
  el('profileEmail').textContent  = email;
  el('profileUsername').value     = getUsername();
  el('profileAvatarPreview').src  = getAvatar() || 'user-icon.png';
  el('accountModal').classList.remove('hidden');
});

el('closeAccountModal')?.addEventListener('click', () => {
  el('accountModal').classList.add('hidden');
});

el('avatarUpload')?.addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = async (ev) => {
    const b64 = ev.target.result;
    try {
      const res = await fetch(`${apiBase()}/api/auth/profile`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', ...authHeader() },
        body: JSON.stringify({ avatar: b64 })
      });
      if (res.ok) {
        localStorage.setItem('auditiq-avatar', b64);
        el('profileAvatarPreview').src = b64;
        applyUserUI(getLoggedInUser());
        showToast('Avatar updated!', 'success');
      } else {
        showToast('Failed to update avatar.', 'error');
      }
    } catch {
      showToast('Failed to connect to server.', 'error');
    }
  };
  reader.readAsDataURL(file);
});

el('saveProfileBtn')?.addEventListener('click', async () => {
  const newName = el('profileUsername').value.trim();
  const btn = el('saveProfileBtn');
  const originalText = btn.textContent;
  btn.textContent = 'Saving...';
  btn.disabled = true;

  try {
    const res = await fetch(`${apiBase()}/api/auth/profile`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', ...authHeader() },
      body: JSON.stringify({ username: newName })
    });
    
    if (res.ok) {
      localStorage.setItem('auditiq-username', newName);
      applyUserUI(getLoggedInUser());
      el('accountModal').classList.add('hidden');
      showToast('Profile saved!', 'success');
    } else {
      showToast('Failed to save profile.', 'error');
    }
  } catch (err) {
    showToast('Failed to connect to server.', 'error');
  } finally {
    btn.textContent = originalText;
    btn.disabled = false;
  }
});

// Close modals on overlay click
['accountModal', 'settingsPanel', 'confirmModal'].forEach((id) => {
  el(id)?.addEventListener('click', (e) => {
    if (e.target === el(id)) el(id).classList.add('hidden');
  });
});

// ─── SETTINGS PANEL ────────────────────────────────────────────────────────

el('settingsToggle')?.addEventListener('click', () => {
  el('settingsPanel')?.classList.toggle('hidden');
  if (!el('settingsPanel').classList.contains('hidden')) fetchMetrics();
});

el('closeSettings')?.addEventListener('click', () => {
  el('settingsPanel').classList.add('hidden');
});

el('saveSettingsBtn')?.addEventListener('click', () => {
  localStorage.setItem('auditiq-api-base', el('apiBase')?.value.trim() || '');
  localStorage.setItem('auditiq-api-key',  el('apiKey')?.value.trim()  || '');
  localStorage.setItem('auditiq-ticker',   el('ticker')?.value.trim()  || '');
  localStorage.setItem('auditiq-language', el('language')?.value        || 'English');
  el('settingsPanel').classList.add('hidden');
  showToast('Settings saved!', 'success');
});

// Restore settings
(function restoreSettings() {
  const base = localStorage.getItem('auditiq-api-base');
  const key  = localStorage.getItem('auditiq-api-key');
  const tick = localStorage.getItem('auditiq-ticker');
  const lang = localStorage.getItem('auditiq-language');
  if (base && el('apiBase'))   el('apiBase').value   = base;
  if (key  && el('apiKey'))    el('apiKey').value    = key;
  if (tick && el('ticker'))    el('ticker').value    = tick;
  if (lang && el('language'))  el('language').value  = lang;
})();

// ─── METRICS / OBSERVABILITY ───────────────────────────────────────────────

async function fetchMetrics() {
  try {
    const res  = await fetch(`${apiBase()}/api/metrics`);
    const data = await res.json();
    el('metricRequests').textContent  = data.total_requests  ?? '—';
    el('metricErrors').textContent    = data.total_errors    ?? '—';
    el('metricErrorRate').textContent = data.error_rate      ?? '—';
    el('metricLatency').textContent   = data.avg_latency_seconds != null
      ? `${(data.avg_latency_seconds * 1000).toFixed(0)} ms`
      : '—';
  } catch {
    // silently ignore if backend unavailable
  }
}

el('refreshMetricsBtn')?.addEventListener('click', () => {
  fetchMetrics();
  showToast('Metrics refreshed', 'info', 2000);
});

// ─── SIDEBAR TOGGLE ────────────────────────────────────────────────────────

el('sidebarToggleBtn')?.addEventListener('click', () => {
  el('chatSidebar')?.classList.toggle('collapsed');
});

// ─── CHAT HISTORY ─────────────────────────────────────────────────────────

let sessionCache = [];

async function syncSessionsFromAPI() {
  const email = getLoggedInUser();
  if (!email) return;
  try {
    const res = await fetch(`${apiBase()}/api/chat/sessions/${encodeURIComponent(email)}`, { headers: authHeader() });
    if (res.ok) {
      sessionCache = await res.json();
      renderRecentChats();
    }
  } catch (err) { console.error(err); }
}

async function updateLocalSessionTitle(id, newTitle) {
  const s = sessionCache.find(s => s.session_id === id);
  if (s) { s.title = newTitle.slice(0, 80); renderRecentChats(); }
  try {
    await fetch(`${apiBase()}/api/chat/session/${id}/title`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', ...authHeader() },
      body: JSON.stringify({ title: newTitle })
    });
  } catch (err) { console.error(err); }
}

async function togglePinSession(id) {
  const s = sessionCache.find(s => s.session_id === id);
  if (!s) return;
  s.is_pinned = !s.is_pinned;
  renderRecentChats();
  try {
    await fetch(`${apiBase()}/api/chat/session/${id}/pin`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', ...authHeader() },
      body: JSON.stringify({ is_pinned: s.is_pinned })
    });
  } catch (err) { console.error(err); }
}

async function deleteSessionLocally(id) {
  sessionCache = sessionCache.filter(s => s.session_id !== id);
  try { await fetch(`${apiBase()}/api/chat/session/${id}`, { method: 'DELETE', headers: authHeader() }); } catch {}
  if (sessionId === id) { sessionId = null; uploadData = null; startNewChat(); }
  renderRecentChats();
}

function dateLabel(iso) {
  const now   = new Date();
  const d     = new Date(iso);
  const diffMs = now - d;
  const diffD  = diffMs / 86400000;
  if (diffD < 1)  return 'Today';
  if (diffD < 2)  return 'Yesterday';
  if (diffD < 7)  return 'Last 7 Days';
  if (diffD < 30) return 'This Month';
  return d.toLocaleString('default', { month: 'long', year: 'numeric' });
}

function renderRecentChats() {
  const listEl = el('recentsList');
  if (!listEl) return;
  const query = el('historySearch')?.value.trim().toLowerCase() || '';
  let displaySessions = sessionCache;
  if (query) displaySessions = displaySessions.filter(s => s.title.toLowerCase().includes(query));
  listEl.innerHTML = '';
  if (!displaySessions.length) {
    listEl.innerHTML = `<div class="recent-item empty" role="listitem">${query ? 'No results found' : 'No recent chats'}</div>`;
    return;
  }
  const pinned = displaySessions.filter(s => s.is_pinned);
  const unpinned = displaySessions.filter(s => !s.is_pinned);

  if (pinned.length > 0 && !query) {
    const header = document.createElement('div');
    header.className = 'history-group-header';
    header.textContent = 'Pinned';
    listEl.appendChild(header);
    pinned.forEach(s => listEl.appendChild(createSessionElement(s)));
  }

  const groups = {};
  unpinned.forEach(s => {
    const lbl = dateLabel(s.created_at || new Date().toISOString());
    if (!groups[lbl]) groups[lbl] = [];
    groups[lbl].push(s);
  });
  Object.entries(groups).forEach(([label, items]) => {
    const header = document.createElement('div');
    header.className = 'history-group-header';
    header.textContent = label;
    listEl.appendChild(header);
    items.forEach(s => listEl.appendChild(createSessionElement(s)));
  });
}

function createSessionElement(s) {
  const li = document.createElement('div');
  li.className = 'recent-item';
  li.setAttribute('role', 'listitem');
  if (s.session_id === sessionId) li.classList.add('active');
  li.dataset.sessionId = s.session_id;

  const pinIcon = s.is_pinned 
    ? `<svg viewBox="0 0 24 24" fill="currentColor" stroke="none" class="pinned-badge"><path d="M16 4h-8l-2 10-4 4v2h9v4h2v-4h9v-2l-4-4l-2-10z"/></svg>`
    : `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 4h-8l-2 10-4 4v2h9v4h2v-4h9v-2l-4-4l-2-10z"/></svg>`;

  li.innerHTML = `
    <svg class="recent-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
    </svg>
    <span class="recent-title" title="${escapeHtml(s.title)}">${escapeHtml(s.title)}</span>
    <input type="text" class="rename-input hidden" value="${escapeHtml(s.title)}" />
    <div class="recent-actions" style="display:flex; gap:4px; margin-left:auto;">
      <button class="action-btn pin-btn" title="${s.is_pinned ? 'Unpin' : 'Pin'}">${pinIcon}</button>
      <button class="action-btn edit-title-btn" title="Rename">✏️</button>
      <button class="recent-del-btn" title="Delete this chat">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
        </svg>
      </button>
    </div>
  `;

  const titleSpan = li.querySelector('.recent-title');
  const inputEl = li.querySelector('.rename-input');

  titleSpan.addEventListener('click', () => {
    loadChatHistory(s.session_id, li);
    if (window.innerWidth <= 768) el('chatSidebar')?.classList.add('collapsed');
  });

  titleSpan.addEventListener('dblclick', () => startRename(titleSpan, inputEl, s));
  li.querySelector('.edit-title-btn').addEventListener('click', (e) => {
    e.stopPropagation();
    startRename(titleSpan, inputEl, s);
  });

  inputEl.addEventListener('blur', () => finishRename(titleSpan, inputEl, s));
  inputEl.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') finishRename(titleSpan, inputEl, s);
    if (e.key === 'Escape') {
      inputEl.value = s.title;
      finishRename(titleSpan, inputEl, s);
    }
  });

  li.querySelector('.pin-btn').addEventListener('click', (e) => {
    e.stopPropagation();
    togglePinSession(s.session_id);
  });

  li.querySelector('.recent-del-btn').addEventListener('click', async (e) => {
    e.stopPropagation();
    const ok = await showConfirm(`Delete "${s.title}"?`, 'Delete Chat');
    if (!ok) return;
    li.style.transition = 'all 0.25s ease';
    li.style.opacity = '0';
    li.style.maxHeight = '0';
    li.style.padding = '0';
    setTimeout(() => {
      deleteSessionLocally(s.session_id);
      showToast('Chat deleted', 'success', 2000);
    }, 250);
  });

  return li;
}

function startRename(span, input, s) {
  span.classList.add('hidden');
  input.classList.remove('hidden');
  input.focus();
  input.select();
}

function finishRename(span, input, s) {
  const newTitle = input.value.trim();
  if (newTitle && newTitle !== s.title) {
    updateLocalSessionTitle(s.session_id, newTitle);
  }
  span.classList.remove('hidden');
  input.classList.add('hidden');
}

/** Load full conversation from backend */
async function loadChatHistory(id, targetEl) {
  sessionId = id;
  const threadEl = el('thread');
  if (threadEl) threadEl.innerHTML = '';

  qsa('.recent-item').forEach(i => i.classList.remove('active'));
  if (targetEl) targetEl.classList.add('active');

  uploadData = null;

  // Show skeleton
  const skeletonMsg = addAssistantMessage(
    `<div class="skeleton-block skeleton-text"></div>
     <div class="skeleton-block skeleton-text" style="width:70%"></div>`, false
  );

  try {
    const res  = await fetch(`${apiBase()}/api/chat/history/${id}`, { headers: authHeader() });
    const data = await res.json();

    skeletonMsg.remove();

    if (data.recovered) {
      const name = getUserDisplayName(getLoggedInUser());
      addAssistantMessage(`<p>Welcome back <strong>${escapeHtml(name)}</strong>! This session's data was not found on the server (it may have been cleared). You can start a new session below.</p>`);
      return;
    }

    if (data.upload) {
      uploadData = data.upload;
      addUserMessage(`<div class="file-chip">${ICON_DOC} <strong>${escapeHtml(uploadData.filename || 'Uploaded File')}</strong></div>`, false);
      const uploadMsg = addAssistantMessage(
        `<p>${ICON_CHECK} File <strong>${escapeHtml(uploadData.filename || 'file')}</strong> — ${uploadData.row_count || 0} rows/elements found.</p>
         <div class="bubble-actions"><button class="mini-btn" data-role="run-analysis">${ICON_PLAY} Run Analysis & Generate Reports</button></div>`,
        false
      );
      uploadMsg.querySelector('[data-role="run-analysis"]')?.addEventListener('click', (e) => runAnalysis(e.target));
      if (el('kpiTotal') && uploadData.total) el('kpiTotal').textContent = formatMoney(uploadData.total);
    }

    if (data.analysis) {
      addUserMessage('<p>Run Deep Analysis &amp; Generate Reports</p>', false);
      const anaMsg = addAssistantMessage('<p>Loading analysis…</p>', false);
      renderAnalysisBubble(anaMsg, data.analysis);
      updateKpis(data.analysis);
    }

    if (data.messages?.length) {
      data.messages.forEach(m => {
        if (m.role === 'user') {
          addUserMessage(`<p>${escapeHtml(m.content)}</p>`, false, m.content);
        } else {
          addAssistantMessage(formatChatReply(m.content), false, m.id);
        }
      });
    }

  } catch (err) {
    skeletonMsg?.remove();
    const name = getUserDisplayName(getLoggedInUser());
    addAssistantMessage(`<p>Welcome back <strong>${escapeHtml(name)}</strong>! Could not load this session (${escapeHtml(err.message)}). Upload a new file or ask a question.</p>`);
  }
}

// New Chat button
el('newChatBtn')?.addEventListener('click', startNewChat);

function startNewChat() {
  sessionId  = null;
  uploadData = null;
  const name = getUserDisplayName(getLoggedInUser());
  const threadEl = el('thread');
  if (threadEl) {
    threadEl.innerHTML = `
      <div class="msg assistant">
        <div class="msg-avatar">AI</div>
        <div class="msg-bubble animate-bubble">
          <p>Welcome <strong>${escapeHtml(name)}</strong>! Upload your financial ledger or ask a question to start a new analysis.</p>
          <p class="sub-text">Reports can be generated in English, Roman Urdu, or Urdu. Configure in ${ICON_GEAR} Settings.</p>
        </div>
      </div>`;
  }
  qsa('.recent-item').forEach(i => i.classList.remove('active'));
  if (el('kpiTotal'))    el('kpiTotal').textContent    = '—';
  if (el('kpiForecast')) el('kpiForecast').textContent = '—';
  if (el('kpiMarket'))   el('kpiMarket').textContent   = '—';
}

// Clear all history button
el('clearHistoryBtn')?.addEventListener('click', async () => {
  const ok = await showConfirm('This will permanently delete ALL your chat history. This action cannot be undone.', 'Clear All History');
  if (!ok) return;

  // Remove from localStorage (correct key)
  localStorage.removeItem(getUserSessionKey());

  // Delete from backend
  const email = getLoggedInUser();
  if (email) {
    try {
      await fetch(`${apiBase()}/api/chat/sessions/${encodeURIComponent(email)}`, { method: 'DELETE' });
    } catch { /* ignore */ }
  }

  startNewChat();
  syncSessionsFromAPI();
  showToast('All chat history deleted.', 'success');
});

// Search filter
el('historySearch')?.addEventListener('input', renderRecentChats);

// ─── SESSION CHECK ON LOAD ─────────────────────────────────────────────────

window.addEventListener('DOMContentLoaded', () => {
  const user = getLoggedInUser();
  if (user) {
    el('loginScreen').classList.add('hidden');
    el('appRoot').classList.remove('hidden');
    applyUserUI(user);
    syncSessionsFromAPI();
  }
});

// ─── ATTACH / FILE UPLOAD ─────────────────────────────────────────────────

el('attachBtn')?.addEventListener('click', (e) => {
  e.stopPropagation();
  const menu = el('attachMenu');
  const open = menu.classList.toggle('open');
  el('attachBtn').setAttribute('aria-expanded', open ? 'true' : 'false');
});

document.addEventListener('click', () => {
  el('attachMenu')?.classList.remove('open');
  el('attachBtn')?.setAttribute('aria-expanded', 'false');
});

el('attachMenu')?.addEventListener('click', (e) => {
  const btn = e.target.closest('button[data-action]');
  if (!btn) return;
  el('attachMenu').classList.remove('open');
  const action = btn.dataset.action;
  if (action === 'file')   el('fileInputGeneral')?.click();
  if (action === 'photo')  el('fileInputPhoto')?.click();
  if (action === 'sample') downloadSampleCSV();
});

['fileInputGeneral', 'fileInputPhoto'].forEach(id => {
  el(id)?.addEventListener('change', (e) => {
    if (e.target.files[0]) uploadFile(e.target.files[0]);
  });
});

async function uploadFile(file) {
  addUserMessage(`<div class="file-chip">${ICON_DOC} <strong>${escapeHtml(file.name)}</strong></div>`);
  const thinking = addAssistantMessage(
    `<div class="skeleton-block skeleton-text" style="width:60%"></div>
     <div class="skeleton-block skeleton-text" style="width:80%"></div>`
  );

  const formData = new FormData();
  formData.append('file', file);
  formData.append('username', getLoggedInUser());   // link session to user

  try {
    const res  = await fetch(`${apiBase()}/api/upload`, { method: 'POST', body: formData, headers: authHeader() });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Upload failed');

    uploadData = data;
    sessionId  = data.session_id;

    // Save with filename as initial title
    syncSessionsFromAPI();

    // Also save username to backend session
    const email = getLoggedInUser();
    if (email) {
      try {
        await fetch(`${apiBase()}/api/chat/session/${sessionId}/title`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title: file.name }),
        });
      } catch { /* ignore */ }
    }

    thinking.querySelector('.msg-bubble').innerHTML =
      `<p>${ICON_CHECK} Parsed <strong>${escapeHtml(data.filename)}</strong> — ${data.row_count || 0} rows/elements found.</p>
       <p>Adjust ticker and language in ${ICON_GEAR} Settings if needed, then run the deep audit analysis.</p>
       <div class="bubble-actions">
         <button class="mini-btn" data-role="run-analysis">
           ${ICON_PLAY} Run Analysis &amp; Generate Reports
         </button>
       </div>`;

    thinking.querySelector('[data-role="run-analysis"]')?.addEventListener('click', (e) => runAnalysis(e.target));

    if (el('kpiTotal') && data.total) el('kpiTotal').textContent = formatMoney(data.total);
    showToast(`File uploaded: ${file.name}`, 'success');

  } catch (err) {
    thinking.querySelector('.msg-bubble').innerHTML =
      `<p class="error-text">${ICON_X} Error: ${escapeHtml(err.message)}</p>`;
    showToast('Upload failed: ' + err.message, 'error');
  }
}

// ─── MESSAGE HELPERS ──────────────────────────────────────────────────────

function addUserMessage(html, animate = true, rawText = '') {
  const thread = el('thread');
  const wrap = document.createElement('div');
  wrap.className = 'msg user';

  const safe = escapeHtml(rawText || html.replace(/<[^>]+>/g, ''));

  wrap.innerHTML = `
    <div class="msg-avatar">U</div>
    <div class="msg-bubble ${animate ? 'animate-bubble' : ''}">
      ${html}
      <div class="msg-actions">
        <button class="action-btn copy-btn" title="Copy" data-text="${safe}">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
        </button>
        <button class="action-btn edit-btn" title="Edit" data-text="${safe}">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
        </button>
      </div>
    </div>`;

  thread?.appendChild(wrap);
  thread?.scrollTo({ top: thread.scrollHeight, behavior: 'smooth' });
  return wrap;
}

function addAssistantMessage(html, animate = true, messageId = null) {
  const thread = el('thread');
  const wrap = document.createElement('div');
  wrap.className = 'msg assistant';

  const feedbackHtml = messageId ? `
    <button class="action-btn like-btn"    title="Helpful"   data-id="${messageId}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/></svg></button>
    <button class="action-btn dislike-btn" title="Not helpful" data-id="${messageId}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h2a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-2"/></svg></button>` : '';

  wrap.innerHTML = `
    <div class="msg-avatar">AI</div>
    <div class="msg-bubble ${animate ? 'animate-bubble' : ''}">
      ${html}
      <div class="msg-actions">
        ${feedbackHtml}
        <button class="action-btn copy-btn" title="Copy">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
        </button>
      </div>
    </div>`;

  thread?.appendChild(wrap);
  thread?.scrollTo({ top: thread.scrollHeight, behavior: 'smooth' });
  return wrap;
}

// Global click delegation for message action buttons
el('appRoot')?.addEventListener('click', async (e) => {
  const target = e.target.closest('.action-btn');
  if (!target) return;

  if (target.classList.contains('copy-btn')) {
    let text = target.dataset.text;
    if (!text) {
      const clone = target.closest('.msg-bubble').cloneNode(true);
      clone.querySelectorAll('.msg-actions, .bubble-actions, audio').forEach(n => n.remove());
      text = clone.innerText.trim();
    }
    await navigator.clipboard.writeText(text);
    showToast('Copied to clipboard!', 'success', 1500);
  }

  if (target.classList.contains('edit-btn')) {
    const text = target.dataset.text;
    const inp  = el('messageInput');
    if (inp) { inp.value = text; inp.focus(); }
  }

  if (target.classList.contains('like-btn') || target.classList.contains('dislike-btn')) {
    const msgId    = target.dataset.id;
    const feedback = target.classList.contains('like-btn') ? 'like' : 'dislike';
    if (!msgId) return;

    target.classList.add('active');
    target.style.transform = 'scale(1.3)';
    setTimeout(() => target.style.transform = 'scale(1)', 200);

    try {
      const res  = await fetch(`${apiBase()}/api/chat/feedback`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ message_id: parseInt(msgId), feedback }),
      });
      const data = await res.json();
      if (res.ok && data.reply) {
        addAssistantMessage(`<p>${escapeHtml(data.reply)}</p>`, true);
      }
    } catch { /* ignore */ }
  }
});

// ─── TYPING INDICATOR ─────────────────────────────────────────────────────

function typingIndicator() {
  return `<div class="typing-dots"><span></span><span></span><span></span></div>`;
}

// ─── FORMAT CHAT REPLY ────────────────────────────────────────────────────

function formatChatReply(text) {
  if (!text) return '';

  const tokens = [];
  const addToken = (html) => {
    const key = `\x00T${tokens.length}\x00`;
    tokens.push(html);
    return key;
  };

  // Markdown images
  text = text.replace(/!\[([^\]]*)\]\((https?:\/\/[^)]+)\)/g, (_, alt, url) =>
    addToken(`<div class="inline-img-wrap"><img src="${url}" alt="${escapeHtml(alt)}" class="inline-img"><a href="${url}" target="_blank" rel="noopener" class="img-dl-link">${ICON_DOWNLOAD} Download</a></div>`)
  );

  // Markdown links
  text = text.replace(/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g, (_, txt, url) =>
    addToken(`<a href="${url}" target="_blank" rel="noopener" class="chat-link">${escapeHtml(txt)}</a>`)
  );

  // Escape
  let html = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

  // Restore tokens
  tokens.forEach((tok, i) => { html = html.replace(`\x00T${i}\x00`, tok); });

  // Markdown formatting
  html = html
    .replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
    .replace(/\*\*(.+?)\*\*/g,     '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g,         '<em>$1</em>')
    .replace(/`(.+?)`/g,           '<code class="inline-code">$1</code>')
    .replace(/^### (.+)$/gm,       '<h4 class="chat-h4">$1</h4>')
    .replace(/^## (.+)$/gm,        '<h3 class="chat-h3">$1</h3>')
    .replace(/^# (.+)$/gm,         '<h2 class="chat-h2">$1</h2>')
    .replace(/(?:^|\n)[-*•] (.+?)(?=\n|$)/g, '\n<div class="bullet-item">• $1</div>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g,  '<br>');

  return `<p>${html}</p>`;
}

// ─── SEND MESSAGE ─────────────────────────────────────────────────────────

const messageInput = el('messageInput');
const sendBtn      = el('sendBtn');

async function sendChatMessage(text, isVoice = false) {
  if (!text.trim()) return;

  addUserMessage(`<p>${escapeHtml(text)}</p>`);
  if (messageInput) messageInput.value = '';
  if (sendBtn) sendBtn.disabled = true;

  const thinking = addAssistantMessage(typingIndicator());

  const formData = new FormData();
  formData.append('message',    text);
  formData.append('session_id', sessionId || '');
  formData.append('username',   getUserDisplayName(getLoggedInUser()));
  formData.append('language',   el('language')?.value || 'English');
  formData.append('api_key',    el('apiKey')?.value.trim() || '');

  try {
    const res  = await fetch(`${apiBase()}/api/chat`, { method: 'POST', body: formData });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Chat request failed');

    // If this is the first message in a new session, create session entry
    if (data.session_id && !sessionId) {
      sessionId = data.session_id;
      saveSessionLocally(sessionId, text.slice(0, 60));
    } else if (sessionId) {
      // Update title with first real user message
      updateLocalSessionTitle(sessionId, text.slice(0, 60));
    }

    const replyHtml = formatChatReply(data.reply);
    const msgId     = data.message_id || null;

    thinking.querySelector('.msg-bubble').innerHTML = `
      ${replyHtml}
      <div class="msg-actions">
        ${msgId ? `
          <button class="action-btn like-btn"    title="Helpful"     data-id="${msgId}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/></svg></button>
          <button class="action-btn dislike-btn" title="Not helpful"  data-id="${msgId}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h2a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-2"/></svg></button>` : ''}
        <button class="action-btn copy-btn" title="Copy"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg></button>
      </div>
      <div class="bubble-actions">
        <button class="mini-btn" data-role="speak-reply">${ICON_SPEAKER} Speak Response</button>
      </div>
      <audio class="bubble-audio" controls style="display:none;"></audio>
    `;

    wireSpeakReply(thinking, data.reply);

    if (isVoice) {
      thinking.querySelector('[data-role="speak-reply"]')?.click();
    }

  } catch (err) {
    thinking.querySelector('.msg-bubble').innerHTML =
      `<p class="error-text">${ICON_X} Couldn't reach backend: ${escapeHtml(err.message)}</p>`;
    showToast('Message failed: ' + err.message, 'error');
  } finally {
    if (sendBtn) sendBtn.disabled = false;
  }
}

function sendTypedMessage() {
  const text = messageInput?.value.trim();
  if (text) sendChatMessage(text, false);
}

sendBtn?.addEventListener('click', sendTypedMessage);

messageInput?.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendTypedMessage();
  }
});

// Auto-resize textarea
messageInput?.addEventListener('input', () => {
  messageInput.style.height = 'auto';
  messageInput.style.height = Math.min(messageInput.scrollHeight, 160) + 'px';
});

// ─── SPEAK REPLY ─────────────────────────────────────────────────────────

function wireSpeakReply(msgEl, text) {
  const btn    = msgEl.querySelector('[data-role="speak-reply"]');
  const player = msgEl.querySelector('audio');

  btn?.addEventListener('click', async () => {
    btn.disabled    = true;
    btn.textContent = '⏳ Generating…';

    try {
      const fd = new FormData();
      fd.append('text',     text);
      fd.append('language', el('language')?.value || 'English');
      fd.append('speed',    1.25);

      const res = await fetch(`${apiBase()}/api/audio-text`, { method: 'POST', body: fd });
      if (!res.ok) throw new Error((await res.json()).detail || 'Audio failed');

      const blob = await res.blob();
      player.src = URL.createObjectURL(blob);
      player.style.display = 'block';
      player.play();
    } catch (err) {
      showToast('Audio: ' + err.message, 'error');
    } finally {
      btn.disabled    = false;
      btn.textContent = '🔊 Speak Response';
    }
  });
}

// ─── VOICE INPUT ──────────────────────────────────────────────────────────

const micBtn = el('micBtn');
const SpeechRecognitionClass = window.SpeechRecognition || window.webkitSpeechRecognition;

if (micBtn) {
  if (!SpeechRecognitionClass) {
    micBtn.disabled = true;
    micBtn.title    = 'Voice input not supported in this browser';
  } else {
    const recognition   = new SpeechRecognitionClass();
    recognition.continuous      = false;
    recognition.interimResults  = false;
    let isRecording = false;

    micBtn.addEventListener('click', () => {
      if (isRecording) { recognition.stop(); return; }
      recognition.lang = el('language')?.value === 'Urdu' ? 'ur-PK' : 'en-US';
      try { recognition.start(); } catch { /* ignore */ }
    });

    recognition.addEventListener('start', () => {
      isRecording = true;
      micBtn.classList.add('recording');
      showToast('Listening…', 'info', 2000);
    });
    recognition.addEventListener('end', () => {
      isRecording = false;
      micBtn.classList.remove('recording');
    });
    recognition.addEventListener('result', (ev) => {
      const transcript = ev.results[0][0].transcript;
      if (messageInput) messageInput.value = transcript;
      sendChatMessage(transcript, true);
    });
    recognition.addEventListener('error', (ev) => {
      showToast('Voice error: ' + ev.error, 'error');
    });
  }
}

// ─── ANALYSIS ────────────────────────────────────────────────────────────

async function runAnalysis(triggerBtn) {
  if (!sessionId) { showToast('Upload a file first.', 'warning'); return; }

  // Cached
  if (uploadData?.analysis) {
    if (triggerBtn) { triggerBtn.disabled = true; triggerBtn.textContent = 'Loaded (Cached)'; }
    addUserMessage('<p>Run Deep Analysis &amp; Generate Reports (Cached)</p>');
    const msg = addAssistantMessage('<p>Loading cached analysis…</p>', false);
    renderAnalysisBubble(msg, uploadData.analysis);
    updateKpis(uploadData.analysis);
    return;
  }

  if (triggerBtn) { triggerBtn.disabled = true; triggerBtn.textContent = 'Analyzing…'; }
  addUserMessage('<p>Run Deep Analysis &amp; Generate Reports</p>');
  const thinking = addAssistantMessage(
    `<div class="skeleton-block skeleton-text"></div>
     <div class="skeleton-block skeleton-text" style="width:80%"></div>
     <div class="skeleton-block skeleton-chart"></div>`
  );

  const fd = new FormData();
  fd.append('session_id', sessionId);
  fd.append('ticker',     el('ticker')?.value.trim()  || '');
  fd.append('language',   el('language')?.value        || 'English');
  fd.append('api_key',    el('apiKey')?.value.trim()   || '');
  fd.append('horizon',    3);

  try {
    const res      = await fetch(`${apiBase()}/api/analyze`, { method: 'POST', body: fd });
    const analysis = await res.json();
    if (!res.ok) throw new Error(analysis.detail || 'Analysis failed');

    if (uploadData) uploadData.analysis = analysis;
    renderAnalysisBubble(thinking, analysis);
    updateKpis(analysis);
    showToast('Analysis complete!', 'success');
  } catch (err) {
    thinking.querySelector('.msg-bubble').innerHTML =
      `<p class="error-text">${ICON_X} ${escapeHtml(err.message)}</p>`;
    showToast('Analysis failed: ' + err.message, 'error');
  }
}

function updateKpis(analysis) {
  const nextVal = analysis.forecast?.next_points?.[0];
  if (el('kpiForecast')) el('kpiForecast').textContent = nextVal != null ? formatMoney(nextVal) : '—';
  const market = analysis.market_data;
  if (el('kpiMarket')) {
    el('kpiMarket').textContent = market?.resolved
      ? `${market.symbol_used} · ${market.current_price}`
      : 'Unresolved';
  }
}

function renderAnalysisBubble(msgEl, analysis) {
  chartCounter += 1;
  const chartId = `chart-${chartCounter}`;
  const { report, forecast } = analysis;

  msgEl.querySelector('.msg-bubble').innerHTML = `
    <p><strong>${ICON_CHECK} Comprehensive Audit Report &amp; Forecast Ready.</strong></p>
    <canvas class="bubble-chart" id="${chartId}" height="140"></canvas>
    <div class="report-tabs">
      <button class="report-tab active" data-tab="compliance-${chartCounter}">${ICON_CLIPBOARD} Compliance Audit</button>
      <button class="report-tab"        data-tab="forecast-${chartCounter}">${ICON_TRENDING} Forecast Narrative</button>
    </div>
    <div id="compliance-${chartCounter}" class="report-panel active"><pre>${escapeHtml(report.compliance_report)}</pre></div>
    <div id="forecast-${chartCounter}"   class="report-panel"><pre>${escapeHtml(report.narrative_report)}</pre></div>
    <div class="bubble-actions">
      <button class="mini-btn" data-role="audio">${ICON_SPEAKER} Listen to Briefing</button>
      <button class="mini-btn" data-role="download">${ICON_DOWNLOAD} Download PDF Report</button>
      <button class="mini-btn" data-role="download-csv">${ICON_DOWNLOAD} Download CSV Data</button>
    </div>
    <audio class="bubble-audio" controls style="display:none;"></audio>
  `;

  wireTabs(msgEl);
  wireBubbleActions(msgEl, analysis);

  try {
    drawChart(chartId, uploadData?.series || [], forecast?.next_points || []);
  } catch (err) {
    console.warn('Chart error:', err);
  }
}

function wireTabs(msgEl) {
  msgEl.querySelectorAll('.report-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      const bubble = tab.closest('.msg-bubble');
      bubble.querySelectorAll('.report-tab').forEach(t => t.classList.remove('active'));
      bubble.querySelectorAll('.report-panel').forEach(p => p.classList.remove('active'));
      tab.classList.add('active');
      bubble.querySelector(`#${tab.dataset.tab}`)?.classList.add('active');
    });
  });
}

function wireBubbleActions(msgEl, analysis) {
  const audioBtn   = msgEl.querySelector('[data-role="audio"]');
  const dlBtn      = msgEl.querySelector('[data-role="download"]');
  const dlCsvBtn   = msgEl.querySelector('[data-role="download-csv"]');
  const player     = msgEl.querySelector('audio');

  dlCsvBtn?.addEventListener('click', () => downloadCSV(analysis));
  dlBtn?.addEventListener('click',    () => {
    window.open(`${apiBase()}/api/report/${sessionId}/download`, '_blank');
  });

  audioBtn?.addEventListener('click', async () => {
    audioBtn.disabled    = true;
    audioBtn.textContent = '⏳ Generating Audio…';
    try {
      const fd = new FormData();
      fd.append('session_id', sessionId);
      fd.append('speed', 1.25);
      const res = await fetch(`${apiBase()}/api/audio`, { method: 'POST', body: fd });
      if (!res.ok) throw new Error((await res.json()).detail || 'Audio failed');
      const blob = await res.blob();
      player.src = URL.createObjectURL(blob);
      player.style.display = 'block';
      player.play();
      showToast('Audio playing!', 'success', 2000);
    } catch (err) {
      showToast('Audio: ' + err.message, 'error');
    } finally {
      audioBtn.disabled    = false;
      audioBtn.textContent = '🔊 Listen to Briefing';
    }
  });
}

// ─── CHART ────────────────────────────────────────────────────────────────

function drawChart(canvasId, historical, forecastPoints) {
  const canvas = el(canvasId);
  if (!canvas) return;
  const ctx    = canvas.getContext('2d');
  const styles = getComputedStyle(document.body);
  const primary = styles.getPropertyValue('--primary').trim() || '#3B9CD9';
  const accent  = styles.getPropertyValue('--accent').trim()  || '#2DD4C6';
  const mid     = styles.getPropertyValue('--text-mid').trim() || '#94A9B3';
  const border  = styles.getPropertyValue('--border').trim()  || '#1E2E36';

  const labels  = [
    ...historical.map((_, i) => `T${i + 1}`),
    ...forecastPoints.map((_, i) => `F${i + 1}`),
  ];
  const histData = [...historical, ...Array(forecastPoints.length).fill(null)];
  const fcstData = [
    ...Array(Math.max(historical.length - 1, 0)).fill(null),
    ...(historical.length ? [historical[historical.length - 1]] : []),
    ...forecastPoints,
  ];

  new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        { label: 'Recorded', data: histData, borderColor: primary, tension: 0.3, pointRadius: 3, fill: false },
        { label: 'Forecast', data: fcstData, borderColor: accent,  borderDash: [5, 4], tension: 0.3, pointRadius: 3, fill: false },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { labels: { color: mid } } },
      scales: {
        x: { ticks: { color: mid }, grid: { color: border } },
        y: { ticks: { color: mid }, grid: { color: border } },
      },
    },
  });
}

// ─── DOWNLOAD HELPERS ─────────────────────────────────────────────────────

function formatMoney(val) {
  return `₨ ${Number(val).toLocaleString('en-PK', { maximumFractionDigits: 2 })}`;
}

function downloadSampleCSV() {
  const rows = [
    ['Transaction ID', 'Date', 'Account Head', 'Debit (PKR)', 'Credit (PKR)', 'Status'],
    ['TRX-001', '2026-01-10', 'Office Rent (IFRS 16)',   '150000', '0',      'Verified'],
    ['TRX-002', '2026-01-15', 'Accounts Receivable',     '0',      '350000', 'Pending Review'],
    ['TRX-003', '2026-01-20', 'SECP Annual Filing Fee',  '5000',   '0',      'Compliant'],
    ['TRX-004', '2026-01-25', 'Software Subscriptions',  '45000',  '0',      'Verified'],
    ['TRX-005', '2026-02-01', 'Payroll — Jan 2026',      '480000', '0',      'Verified'],
    ['TRX-006', '2026-02-10', 'Revenue — Project Alpha', '0',      '900000', 'Verified'],
  ];
  const csv  = 'data:text/csv;charset=utf-8,' + rows.map(r => r.join(',')).join('\n');
  const link = document.createElement('a');
  link.href     = encodeURI(csv);
  link.download = 'AuditIQ_Sample.csv';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  showToast('Sample CSV downloaded!', 'success', 2000);
}

function downloadCSV(analysis) {
  const { forecast } = analysis;
  if (!forecast?.next_points) return;
  let rows = 'Period,Value\n';
  (uploadData?.series || []).forEach((v, i) => { rows += `T${i + 1},${v}\n`; });
  forecast.next_points.forEach((v, i)        => { rows += `F${i + 1} (Forecast),${v}\n`; });
  const link = document.createElement('a');
  link.href     = 'data:text/csv;charset=utf-8,' + encodeURI(rows);
  link.download = `AuditIQ_Data_${sessionId || 'export'}.csv`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  showToast('CSV downloaded!', 'success', 2000);
}
