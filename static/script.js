// ── STATE ──────────────────────────────────────────────────
let currentLang = 'en';
let currentConvId = null;
let isLoading = false;
let sidebarOpen = true;
let isDark = false;

// ── INIT ───────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  loadConversations();
  updateLang();
  checkDarkPref();

  document.getElementById('newChatBtn').addEventListener('click', newChat);
  document.getElementById('backHomeBtn').addEventListener('click', goHome);
  document.getElementById('sidebarToggle').addEventListener('click', () => toggleSidebar(false));

  const overlay = document.getElementById('sidebarOverlay');
  if (overlay) overlay.addEventListener('click', () => toggleSidebar(false));

  document.getElementById('chatInput').focus();
});

// ── DARK MODE ──────────────────────────────────────────────
function checkDarkPref() {
  const saved = localStorage.getItem('cf-theme');
  if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    setDark(true, false);
  }
}

function toggleDark() { setDark(!isDark); }

function setDark(dark, save = true) {
  isDark = dark;
  document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
  const btn = document.getElementById('darkToggle');
  if (btn) btn.textContent = dark ? '☀️' : '🌙';
  if (save) localStorage.setItem('cf-theme', dark ? 'dark' : 'light');
}

// ── LANGUAGE ───────────────────────────────────────────────
function setLang(lang) {
  currentLang = lang;
  document.getElementById('langEN').classList.toggle('active', lang === 'en');
  document.getElementById('langPT').classList.toggle('active', lang === 'pt');
  updateLang();
}

function updateLang() {
  const isEN = currentLang === 'en';
  document.querySelectorAll('[data-en]').forEach(el => {
    el.textContent = isEN ? el.dataset.en : el.dataset.pt;
  });
  document.getElementById('chatInput').placeholder = isEN
    ? 'Ask about Coverflex benefits...'
    : 'Pergunta sobre benefícios Coverflex...';
  const search = document.getElementById('searchInput');
  if (search) search.placeholder = isEN ? '🔍 Search chats...' : '🔍 Pesquisar conversas...';
}

// ── SIDEBAR ────────────────────────────────────────────────
function toggleSidebar(open) {
  const isMobile = window.innerWidth <= 768;
  sidebarOpen = (typeof open === 'boolean') ? open : !sidebarOpen;
  const sidebar = document.getElementById('sidebar');
  const openBtn = document.getElementById('sidebarOpenBtn');
  const overlay = document.getElementById('sidebarOverlay');
  sidebar.classList.toggle('collapsed', !sidebarOpen);
  openBtn.classList.toggle('visible', !sidebarOpen);
  if (overlay) overlay.classList.toggle('visible', sidebarOpen && isMobile);
}

// ── CONVERSATIONS ──────────────────────────────────────────
async function loadConversations() {
  try {
    const res = await fetch('/api/conversations');
    const convs = await res.json();
    renderChatList(convs);
  } catch (e) { console.error('Failed to load conversations', e); }
}

function renderChatList(convs) {
  const list = document.getElementById('chatList');
  if (!convs.length) {
    list.innerHTML = `<div class="chat-empty">${currentLang === 'en' ? 'No conversations yet' : 'Sem conversas ainda'}</div>`;
    return;
  }
  list.innerHTML = convs.map(c => `
    <button class="chat-list-item ${c.id === currentConvId ? 'active' : ''}" onclick="loadConversation('${c.id}')">
      <span class="chat-item-icon">${c.id === currentConvId ? '🟠' : '💬'}</span>
      <div class="chat-item-info">
        <div class="chat-item-title">${escapeHtml(c.title)}</div>
        <div class="chat-item-date">${c.date}</div>
      </div>
      <button class="chat-item-delete" onclick="deleteConv(event, '${c.id}')" title="Delete">✕</button>
    </button>
  `).join('');
}

async function loadConversation(convId) {
  try {
    const res = await fetch(`/api/conversations/${convId}`);
    const conv = await res.json();
    if (conv.error) return;
    currentConvId = convId;
    showChatScreen();
    document.getElementById('messages').innerHTML = '';
    conv.messages.forEach(msg => appendMessage(msg.role, msg.content, false));
    document.getElementById('breadcrumbCurrent').textContent = conv.title.substring(0, 30) + (conv.title.length > 30 ? '...' : '');
    loadConversations();
    const chat = document.getElementById('chatScreen');
    chat.scrollTop = chat.scrollHeight;
    if (window.innerWidth <= 768) toggleSidebar(false);
  } catch (e) { console.error('Failed to load conversation', e); }
}

async function deleteConv(event, convId) {
  event.stopPropagation();
  await fetch(`/api/conversations/${convId}`, { method: 'DELETE' });
  if (currentConvId === convId) newChat();
  loadConversations();
}

function filterChats(term) {
  document.querySelectorAll('.chat-list-item').forEach(item => {
    const title = item.querySelector('.chat-item-title')?.textContent.toLowerCase() || '';
    item.style.display = title.includes(term.toLowerCase()) ? 'flex' : 'none';
  });
}

// ── CHAT ───────────────────────────────────────────────────
function newChat() {
  currentConvId = null;
  goHome();
  loadConversations();
}

function goHome() {
  document.getElementById('welcomeScreen').classList.remove('hidden');
  document.getElementById('chatScreen').classList.add('hidden');
  document.getElementById('relatedSection').classList.add('hidden');
  document.getElementById('breadcrumbCurrent').textContent = 'New Chat';
  document.querySelectorAll('.kb-item').forEach((el, i) => el.classList.toggle('active', i === 0));
}

function showChatScreen() {
  document.getElementById('welcomeScreen').classList.add('hidden');
  document.getElementById('chatScreen').classList.remove('hidden');
}

function askQuestion(question, event) {
  if (event) event.preventDefault();
  document.querySelectorAll('.kb-item').forEach(el => el.classList.remove('active'));
  if (event?.currentTarget) event.currentTarget.classList.add('active');
  document.getElementById('chatInput').value = question;
  sendMessage();
}

function handleKey(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
}

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}

// ── TYPEWRITER EFFECT ──────────────────────────────────────
async function typeWriter(el, text, chatScreen) {
  const words = text.split(' ');
  let current = '';
  for (const word of words) {
    current += (current ? ' ' : '') + word;
    el.innerHTML = formatMessage(current) + '<span class="streaming-cursor"></span>';
    chatScreen.scrollTop = chatScreen.scrollHeight;
    await new Promise(r => setTimeout(r, 20));
  }
  el.innerHTML = formatMessage(text);
}

// ── SEND MESSAGE ───────────────────────────────────────────
async function sendMessage() {
  const input = document.getElementById('chatInput');
  const message = input.value.trim();
  if (!message || isLoading) return;

  isLoading = true;
  input.value = '';
  input.style.height = 'auto';
  document.getElementById('sendBtn').disabled = true;
  document.getElementById('relatedSection').classList.add('hidden');

  showChatScreen();
  if (window.innerWidth <= 768) toggleSidebar(false);

  // Get history from existing messages
  const messagesEl = document.getElementById('messages');
  const history = Array.from(messagesEl.querySelectorAll('.message')).map(el => ({
    role: el.classList.contains('user') ? 'user' : 'assistant',
    content: el.querySelector('.msg-bubble').innerText
  }));

  // Add user message
  appendMessage('user', message, true);

  // Add assistant placeholder with typing indicator
  const assistantDiv = document.createElement('div');
  assistantDiv.className = 'message assistant';
  const now = new Date();
  const timeStr = now.getHours().toString().padStart(2,'0') + ':' + now.getMinutes().toString().padStart(2,'0');
  assistantDiv.innerHTML = `
    <div class="msg-avatar">✦</div>
    <div class="msg-content">
      <div class="msg-bubble typing-bubble">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
      <div class="msg-footer">
        <span class="msg-time">${timeStr}</span>
        <button class="copy-btn" onclick="copyMsg(this)">📋 Copy</button>
      </div>
    </div>
  `;
  messagesEl.appendChild(assistantDiv);

  const chatScreen = document.getElementById('chatScreen');
  chatScreen.scrollTop = chatScreen.scrollHeight;

  try {
    const convId = currentConvId || generateId();
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, history, conv_id: convId, lang: currentLang })
    });

    const data = await res.json();
    const bubble = assistantDiv.querySelector('.msg-bubble');

    if (data.error) {
      bubble.innerHTML = `❌ Error: ${data.error}`;
    } else {
      currentConvId = data.conv_id;
      // Typewriter effect
      await typeWriter(bubble, data.response, chatScreen);
      showRelated(data.related);
      document.getElementById('breadcrumbCurrent').textContent = message.substring(0, 35) + (message.length > 35 ? '...' : '');
      loadConversations();
    }
  } catch (e) {
    const bubble = assistantDiv.querySelector('.msg-bubble');
    bubble.innerHTML = '❌ Connection error. Please try again.';
  }

  isLoading = false;
  document.getElementById('sendBtn').disabled = false;
  chatScreen.scrollTop = chatScreen.scrollHeight;
  input.focus();
}

// ── MESSAGE HELPERS ────────────────────────────────────────
function appendMessage(role, content, animate) {
  const messages = document.getElementById('messages');
  const div = document.createElement('div');
  div.className = `message ${role}`;
  const now = new Date();
  const timeStr = now.getHours().toString().padStart(2,'0') + ':' + now.getMinutes().toString().padStart(2,'0');
  const avatar = role === 'user' ? 'M' : '✦';

  if (role === 'user') {
    div.innerHTML = `
      <div class="msg-avatar">${avatar}</div>
      <div class="msg-content">
        <div class="msg-bubble">${formatMessage(content)}</div>
        <div class="msg-footer"><span class="msg-time">${timeStr}</span></div>
      </div>
    `;
  } else {
    div.innerHTML = `
      <div class="msg-avatar">${avatar}</div>
      <div class="msg-content">
        <div class="msg-bubble">${formatMessage(content)}</div>
        <div class="msg-footer">
          <span class="msg-time">${timeStr}</span>
          <button class="copy-btn" onclick="copyMsg(this)">📋 Copy</button>
        </div>
      </div>
    `;
  }
  messages.appendChild(div);
  return div;
}

function copyMsg(btn) {
  const bubble = btn.closest('.msg-content').querySelector('.msg-bubble');
  navigator.clipboard.writeText(bubble.innerText).then(() => {
    btn.textContent = '✅ Copied!';
    btn.classList.add('copied');
    setTimeout(() => { btn.textContent = '📋 Copy'; btn.classList.remove('copied'); }, 2000);
  });
}

function showRelated(questions) {
  const section = document.getElementById('relatedSection');
  const btns = document.getElementById('relatedBtns');
  btns.innerHTML = questions.map(q => `
    <button class="related-btn" onclick="askRelated('${escapeHtml(q)}')">${escapeHtml(q)}</button>
  `).join('');
  section.classList.remove('hidden');
}

function askRelated(question) {
  document.getElementById('chatInput').value = question;
  sendMessage();
}

// ── UTILS ───────────────────────────────────────────────────
function formatMessage(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/^### (.*$)/gm, '<h3 style="font-size:14px;font-weight:600;margin:8px 0 4px;">$1</h3>')
    .replace(/^## (.*$)/gm, '<h3 style="font-size:15px;font-weight:600;margin:10px 0 4px;">$1</h3>')
    .replace(/^# (.*$)/gm, '<h3 style="font-size:16px;font-weight:700;margin:10px 0 6px;">$1</h3>')
    .replace(/^[\*\-] (.*$)/gm, '<li>$1</li>')
    .replace(/^\d+\. (.*$)/gm, '<li>$1</li>')
    .replace(/(<li>[\s\S]*?<\/li>)/g, '<ul style="padding-left:18px;margin:6px 0;">$1</ul>')
    .replace(/\n\n/g, '</p><p style="margin-bottom:6px;">')
    .replace(/\n/g, '<br>');
}

function escapeHtml(text) {
  return text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#039;');
}

function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
}
