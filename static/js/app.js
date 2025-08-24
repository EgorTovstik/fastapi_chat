document.addEventListener('DOMContentLoaded', () => { 
    const socket = io();

    // --- Элементы DOM ---
    const loginPanel = document.getElementById('login');
    const chatWindow = document.querySelector('.chat-window');
    const loginUsername = document.getElementById('login-username');
    const loginPassword = document.getElementById('login-password');
    const loginBtn = document.getElementById('login-btn');
    const registerBtn = document.getElementById('register-btn');
    const chatList = document.getElementById('chat-list');
    const form = document.getElementById('form');
    const input = document.getElementById('input');
    const addChatBtn = document.getElementById('add-chat-button');
    const overlay = document.querySelector('.overlay');
    const newChatModal = document.getElementById('new-chat');
    const userSelect = document.getElementById('user-select');
    const createChatBtn = document.getElementById('create-chat-btn');
    const closeChatBtn = document.getElementById('close-chat-btn');
    const loginErrorEl = document.getElementById('login-error');
    const newChatErrorEl = document.getElementById('new-chat-error');

    let myName = '';
    let myId = localStorage.getItem('id') || null;
    let currentChatId = null;
    let currentChat = null;
    let chats = {}; // { chatId: { withUser, messages: [] } }

    // --- ЛОГИН ---
    loginBtn.addEventListener('click', async () => {
        const username = loginUsername.value.trim();
        const password = loginPassword.value.trim();

        if (!username || !password) {
            loginErrorEl.textContent = 'Введите логин и пароль';
            return;
        } else {
            loginErrorEl.textContent = '';
        }

        try {
            const res = await fetch('/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await res.json();
            if (data.error) return alert(data.error);

            myName = username;
            myId = data.userId;
            localStorage.setItem('name', myName);
            localStorage.setItem('id', myId);
            
            hideAuthModal();
            chatWindow.style.display = 'flex';
            socket.emit('set_user', { username: myName, userId: myId });
            await loadUserChats();
        } catch (err) {
            console.error(err);
            alert('Ошибка подключения');
        }
    });

    // --- РЕГИСТРАЦИЯ ---
    registerBtn.addEventListener('click', async () => {
        const username = loginUsername.value.trim();
        const password = loginPassword.value.trim();

        if (!username || !password) {
            loginErrorEl.textContent = 'Введите логин и пароль';
            return;
        } else {
            loginErrorEl.textContent = '';
        }

        try {
            const res = await fetch('/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await res.json();
            if (data.error) alert(data.error);
            loginErrorEl.textContent = 'Пользователь успешно добавлен';
        } catch (err) {
            loginErrorEl.textContent = 'Ошибка регистрации';
        }
    });

    // --- Автовход ---
    if (myName && myId) {
        hideAuthModal();
        chatWindow.style.display = 'flex';
        socket.emit('set_user', { username: myName, userId: myId });
        loadUserChats();
    } else {
        showAuthModal();                      
        chatWindow.style.display = 'none';
    }

    // --- Загрузка чатов пользователя ---
    async function loadUserChats() {
        try {
            const res = await fetch(`/api/chats?userId=${myId}`);
            const data = await res.json();
            if (!Array.isArray(data)) return;

            chatList.innerHTML = '';
            chats = {};

            data.forEach(chat => {
                chats[chat.chat_id] = {
                    lastMessage: chat.last_message,
                    messages: [],
                    with_user: chat.with_user
                };

                const li = document.createElement('li');
                li.textContent = `${chat.with_user}: ${chat.last_message || 'Нет сообщений'} ${renderTime(chat.last_ts)}`;
                li.dataset.chatId = chat.chat_id;
                li.addEventListener('click', () => openChat(chat.chat_id));
                chatList.appendChild(li);
            });

            setActiveChat(currentChatId);
        } catch (err) {
            console.error('Ошибка загрузки чатов:', err);
        }
    }

    // --- Создание нового чата ---
    addChatBtn.addEventListener('click', showNewChatModal);
    closeChatBtn.addEventListener('click', hideNewChatModal);

    createChatBtn.addEventListener('click', async () => {
        const selectedUserId = userSelect.value;
        if (!selectedUserId) {
            newChatErrorEl.textContent = 'Выберите пользователя';
            return;
        }

        try {
            const res = await fetch('/api/chats', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ users: [selectedUserId], creatorId: myId })
            });
            const data = await res.json();
            if (data.error) {
                newChatErrorEl.textContent = data.error;
                return;
            }

            hideNewChatModal();
            await loadUserChats();
        } catch (err) {
            console.error(err);
            newChatErrorEl.textContent = 'Не удалось создать чат';
        }
    });

    // --- Загрузка пользователей для выбора ---
    async function loadUsersList() {
        try {
            const res = await fetch(`/api/users?excludeId=${myId}`);
            const users = await res.json();

            userSelect.innerHTML = '<option value="">Выберите пользователя</option>';
            users.forEach(u => {
                const option = document.createElement('option');
                option.value = u.id;
                option.textContent = u.username;
                userSelect.appendChild(option);
            });
        } catch (err) {
            console.error('Ошибка загрузки пользователей:', err);
        }
    }

    // --- Открытие конкретного чата ---
    async function openChat(chatId) {
        currentChatId = chatId;
        currentChat = chats[chatId];
        setActiveChat(chatId);
        showChat();

        try {
            const res = await fetch(`/api/messages/${chatId}?userId=${myId}`);
            const data = await res.json();
            chats[chatId].messages = data;
            renderMessages(chatId);
        } catch (err) {
            console.error('Ошибка загрузки сообщений:', err);
        }
    }

    // --- Рендер сообщений ---
    function renderMessages(chatId, smooth = false) {
        const messagesEl = document.getElementById('messages');
        const currentUserEl = document.getElementById('current-chat-user');
        messagesEl.innerHTML = '';

        currentChat = chats[chatId];
        currentUserEl.textContent = currentChat?.with_user || 'Unknown User';

        currentChat.messages.forEach(msg => {
            const div = document.createElement('div');
            const isMine = msg.username === myName;
            div.classList.add(isMine ? 'message-sent' : 'message-received');
            div.innerHTML = `
                <div class="message-content">
                    <span class="message-text">${escapeHtml(msg.text)}</span>
                    <span class="msg-time">${renderTime(msg.ts)}</span>
                </div>
            `;
            messagesEl.appendChild(div);
        });

        requestAnimationFrame(() => {
            messagesEl.scrollTo({ 
                top: messagesEl.scrollHeight, 
                behavior: smooth ? 'smooth' : 'auto' 
            });
        });
    }

    // --- Отправка сообщений ---
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const text = input.value.trim();
        if (!text || !currentChatId) return;

        try {
            const res = await fetch(`/api/messages/${currentChatId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text, userId: myId })
            });

            const msg = await res.json();
            if (msg.error) return alert(msg.error);

            currentChat.messages.push({ username: myName, text: msg.text, ts: msg.ts });
            renderMessages(currentChatId);
            await loadUserChats();
            setActiveChat(currentChatId);

            scrollMessagesSmooth();

            input.value = '';
            input.style.height = 'auto';
        } catch (err) {
            console.error('Ошибка отправки сообщения:', err);
            alert('Не удалось отправить сообщение');
        }
    });

    input.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            form.requestSubmit();
        }
    });

    // --- Вспомогательные функции ---
    function showAuthModal() {
        overlay.classList.remove('hidden');
        loginPanel.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }

    function hideAuthModal() {
        overlay.classList.add('hidden');
        document.body.style.overflow = '';
    }

    function showNewChatModal() {
        overlay.classList.remove('hidden');
        document.body.style.overflow = 'hidden';

        overlay.querySelectorAll('div').forEach(m => m.classList.add('hidden'));
        newChatModal.classList.remove('hidden');

        newChatErrorEl.textContent = '';
        userSelect.innerHTML = '<option value="">Выберите пользователя</option>';

        loadUsersList();
    }

    function hideNewChatModal() {
        overlay.classList.add('hidden');
        document.body.style.overflow = '';
    }

    function showChat() {
        chatWindow.classList.remove('hidden');
    }

    function setActiveChat(chatId) {
        if (!chatId) return;
        document.querySelectorAll('#chat-list li').forEach(li => {
            li.classList.toggle('active', String(li.dataset.chatId) === String(chatId));
        });
    }

    function renderTime(msg_time) {
        if (!msg_time) {return ''}
        let timestamp = typeof msg_time === 'string' ? parseInt(msg_time) : msg_time;
        if (timestamp < 1000000000000) timestamp *= 1000;
        const date = new Date(timestamp);
        if (isNaN(date.getTime())) return '--:--';
        return `${String(date.getHours()).padStart(2,'0')}:${String(date.getMinutes()).padStart(2,'0')}`;
    }

    function scrollMessagesSmooth() {
        const messagesEl = document.getElementById('messages');
        messagesEl.scrollTo({ top: messagesEl.scrollHeight, behavior: 'smooth' });
    }

    function escapeHtml(s) {
        const str = String(s ?? "");
        const map = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
        return str.replace(/[&<>"']/g, ch => map[ch]);
    }
});
