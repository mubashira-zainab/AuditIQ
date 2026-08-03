import re

with open('app.js', 'r', encoding='utf-8') as f:
    text = f.read()

replacement = """let sessionCache = [];

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

function dateLabel(iso) {"""

text = re.sub(
    r'/\*\* Save a new session entry to localStorage \*/.*?function dateLabel\(iso\) \{',
    replacement,
    text,
    flags=re.DOTALL
)

replacement_render = """function renderRecentChats() {
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

/** Load full conversation from backend */"""

text = re.sub(
    r'/\*\* Load and render the recent chats sidebar list \*/.*?/\*\* Load full conversation from backend \*/',
    replacement_render,
    text,
    flags=re.DOTALL
)

# Replace fetch for loadChatHistory
text = re.sub(
    r'const res  = await fetch\(`\$\{apiBase\(\)\}/api/chat/history/\$\{id\}`\);',
    r'const res  = await fetch(`${apiBase()}/api/chat/history/${id}`, { headers: authHeader() });',
    text
)

text = re.sub(r'loadRecentChats', r'syncSessionsFromAPI', text)
text = text.replace('syncSessionsFromAPI();', 'syncSessionsFromAPI();')
text = text.replace('el(\'historySearch\')?.addEventListener(\'input\', syncSessionsFromAPI);', 'el(\'historySearch\')?.addEventListener(\'input\', renderRecentChats);')
text = text.replace('saveSessionLocally(sessionId, file.name);', 'syncSessionsFromAPI();')
text = text.replace('const res  = await fetch(`${apiBase()}/api/upload`, { method: \'POST\', body: formData });', 'const res  = await fetch(`${apiBase()}/api/upload`, { method: \'POST\', body: formData, headers: authHeader() });')
text = text.replace('const res = await fetch(`${apiBase()}/api/chat`, { method: \'POST\', body: formData });', 'const res = await fetch(`${apiBase()}/api/chat`, { method: \'POST\', body: formData, headers: authHeader() });')
text = text.replace('const res = await fetch(`${apiBase()}/api/analyze`, { method: \'POST\', body: formData });', 'const res = await fetch(`${apiBase()}/api/analyze`, { method: \'POST\', body: formData, headers: authHeader() });')

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(text)
print('Regex replace done.')
