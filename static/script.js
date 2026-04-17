// ── STATE ──────────────────────────────────────────────────
let currentLang = 'en';
let currentConvId = null;
let isLoading = false;
let sidebarOpen = true;

// ── INIT ───────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  loadConversations();
  updateLang();

  document.getElementById('newChatBtn').addEventListener('click', newChat);
  document.getElementById('backHomeBtn').addEventListener('click', goHome);
  document.getElementById('sidebarToggle').addEventListener('click', toggleSidebar);

  // Auto-focus input
  document.getElementById('chatInput').focus();
});

// ── LANGUAGE ───────────────────────────────────────────────
function setLang(lang) {
  currentLang = lang;
  document.getElementById('langEN').classList.toggle('active', lang === 'en');
  document.getElementById('langPT').classList.toggle('active', lang === 'pt');
  updateLang();
}

function updateLang() {
  const isEN = currentLang === 'en';

  // Update all data-en/data-pt elements
  document.querySelectorAll('[data-en]').forEach(el => {
    el.textContent = isEN ? el.dataset.en : el.dataset.pt;
  });

  // Update placeholder
  const input = document.getElementById('chatInput');
  input.placeholder = isEN
    ? 'Ask about Coverflex benefits...'
    : 'Pergunta sobre benefícios Coverflex...';

  // Update search placeholder
  const search = document.getElementById('searchInput');
  if (search) search.placeholder = isEN ? '🔍 Search chats...' : '🔍 Pesquisar conversas...';
}

// ── SIDEBAR ────────────────────────────────────────────────
function toggleSidebar() {
  sidebarOpen = !sidebarOpen;
  const sidebar = document.getElementById('sidebar');
  const openBtn = document.getElementById('sidebarOpenBtn');
  sidebar.classList.toggle('collapsed', !sidebarOpen);
  openBtn.classList.toggle('visible', !sidebarOpen);
}

// ── CONVERSATIONS ──────────────────────────────────────────
async function loadConversations() {
  try {
    const res = await fetch('/api/conversations');
    const convs = await res.json();
    renderChatList(convs);
  } catch (e) {
    console.error('Failed to load conversations', e);
  }
}

function renderChatList(convs) {
  const list = document.getElementById('chatList');
  if (!convs.length) {
    list.innerHTML = `<div class="chat-empty" data-en="No conversations yet" data-pt="Sem conversas ainda">${currentLang === 'en' ? 'No conversations yet' : 'Sem conversas ainda'}</div>`;
    return;
  }

  list.innerHTML = convs.map(c => `
    <button class="chat-list-item ${c.id === currentConvId ? 'active' : ''}"
            onclick="loadConversation('${c.id}')">
      <span class="chat-item-icon">${c.id === currentConvId ? '🟠' : '💬'}</span>
      <div class="chat-item-info">
        <div class="chat-item-title">${escapeHtml(c.title)}</div>
        <div class="chat-item-date">${c.date}</div>
      </div>
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

    const messagesEl = document.getElementById('messages');
    messagesEl.innerHTML = '';

    conv.messages.forEach(msg => {
      appendMessage(msg.role, msg.content, false);
    });

    document.getElementById('breadcrumbCurrent').textContent = conv.title.substring(0, 30) + (conv.title.length > 30 ? '...' : '');
    loadConversations();

    // Scroll to bottom
    const chat = document.getElementById('chatScreen');
    chat.scrollTop = chat.scrollHeight;

  } catch (e) {
    console.error('Failed to load conversation', e);
  }
}

function filterChats(term) {
  const items = document.querySelectorAll('.chat-list-item');
  items.forEach(item => {
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

  // Remove active from all kb items, set General active
  document.querySelectorAll('.kb-item').forEach((el, i) => {
    el.classList.toggle('active', i === 0);
  });
}

function showChatScreen() {
  document.getElementById('welcomeScreen').classList.add('hidden');
  document.getElementById('chatScreen').classList.remove('hidden');
}

function askQuestion(question, event) {
  if (event) event.preventDefault();

  // Update active kb item
  document.querySelectorAll('.kb-item').forEach(el => el.classList.remove('active'));
  if (event && event.currentTarget) event.currentTarget.classList.add('active');

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

  // Get current history
  const messages = document.getElementById('messages');
  const history = Array.from(messages.querySelectorAll('.message')).map(el => ({
    role: el.classList.contains('user') ? 'user' : 'assistant',
    content: el.querySelector('.msg-bubble').innerText
  }));

  // Add user message
  appendMessage('user', message, true);

  // Add typing indicator
  const typingEl = addTyping();

  // Scroll to bottom
  const chatScreen = document.getElementById('chatScreen');
  chatScreen.scrollTop = chatScreen.scrollHeight;

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        history,
        conv_id: currentConvId || generateId(),
        lang: currentLang
      })
    });

    const data = await res.json();
    typingEl.remove();

    if (data.error) {
      appendMessage('assistant', `❌ Error: ${data.error}`, true);
    } else {
      currentConvId = data.conv_id;
      appendMessage('assistant', data.response, true);

      // Show related questions
      showRelated(data.related);

      // Update breadcrumb
      document.getElementById('breadcrumbCurrent').textContent = message.substring(0, 35) + (message.length > 35 ? '...' : '');

      // Refresh chat list
      loadConversations();
    }
  } catch (e) {
    typingEl.remove();
    appendMessage('assistant', '❌ Connection error. Please try again.', true);
  }

  isLoading = false;
  document.getElementById('sendBtn').disabled = false;
  chatScreen.scrollTop = chatScreen.scrollHeight;
  input.focus();
}

function appendMessage(role, content, animate) {
  const messages = document.getElementById('messages');
  const div = document.createElement('div');
  div.className = `message ${role}${animate ? '' : ''}`;

  const avatar = role === 'user' ? 'M' : '✦';
  const formattedContent = formatMessage(content);

  div.innerHTML = `
    <div class="msg-avatar">${avatar}</div>
    <div class="msg-bubble">${formattedContent}</div>
  `;

  messages.appendChild(div);
  return div;
}

function addTyping() {
  const messages = document.getElementById('messages');
  const div = document.createElement('div');
  div.className = 'message assistant typing';
  div.innerHTML = `
    <div class="msg-avatar">✦</div>
    <div class="msg-bubble">
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    </div>
  `;
  messages.appendChild(div);
  return div;
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
    .replace(/^### (.*$)/gm, '<h3>$1</h3>')
    .replace(/^## (.*$)/gm, '<h3>$1</h3>')
    .replace(/^# (.*$)/gm, '<h3>$1</h3>')
    .replace(/^\* (.*$)/gm, '<li>$1</li>')
    .replace(/^- (.*$)/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>')
    .replace(/^(.+)$/gm, (match) => {
      if (match.startsWith('<')) return match;
      return match;
    });
}

function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
}
