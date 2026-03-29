(function() {
    const scriptTag = document.currentScript;
    const scriptSrc = scriptTag ? scriptTag.src : "";
    const backendOrigin = scriptSrc ? new URL(scriptSrc).origin : 'https://chatbot-production-e910.up.railway.app';
    const clientId = scriptSrc.includes('?') ? new URLSearchParams(scriptSrc.split('?')[1]).get('id') : new URLSearchParams(window.location.search).get('id');

    // Inject CSS
    const style = document.createElement('style');
    style.innerHTML = `
        #chatbot-widget-container {
            position: fixed;
            bottom: 24px;
            right: 24px;
            z-index: 999999;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
        }
        #chatbot-toggle-btn {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background-color: #3b82f6;
            color: #fff;
            border: none;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.2s ease;
        }
        #chatbot-toggle-btn:hover {
            transform: scale(1.05);
        }
        #chatbot-toggle-btn svg {
            width: 32px;
            height: 32px;
        }
        #chatbot-window {
            position: absolute;
            bottom: 80px;
            right: 0;
            width: 350px;
            height: 500px;
            background: #fff;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            display: none;
            flex-direction: column;
            overflow: hidden;
            border: 1px solid #e5e7eb;
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.3s ease, transform 0.3s ease;
        }
        #chatbot-window.open {
            display: flex;
            opacity: 1;
            transform: translateY(0);
        }
        #chatbot-header {
            background: #1e293b;
            color: #fff;
            padding: 16px;
            font-weight: 600;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        #chatbot-close-btn {
            background: transparent;
            border: none;
            color: #94a3b8;
            cursor: pointer;
            display: flex;
        }
        #chatbot-close-btn:hover {
            color: #fff;
        }
        #chatbot-messages {
            flex: 1;
            padding: 16px;
            overflow-y: auto;
            background: #f9fafb;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .chat-bubble {
            max-width: 80%;
            padding: 10px 14px;
            border-radius: 12px;
            font-size: 14px;
            line-height: 1.4;
            animation: fadeIn 0.3s ease;
            word-wrap: break-word;
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
        .chat-user {
            background: #3b82f6;
            color: #fff;
            align-self: flex-end;
            border-bottom-right-radius: 2px;
        }
        .chat-bot {
            background: #fff;
            color: #1f2937;
            align-self: flex-start;
            border: 1px solid #e5e7eb;
            border-bottom-left-radius: 2px;
        }
        #chatbot-input-area {
            display: flex;
            padding: 12px;
            background: #fff;
            border-top: 1px solid #e5e7eb;
        }
        #chatbot-input {
            flex: 1;
            border: 1px solid #d1d5db;
            padding: 10px 14px;
            border-radius: 20px;
            outline: none;
            font-size: 14px;
            transition: border-color 0.2s;
        }
        #chatbot-input:focus {
            border-color: #3b82f6;
        }
        #chatbot-send-btn {
            background: #3b82f6;
            color: #fff;
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin-left: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s;
        }
        #chatbot-send-btn:hover {
            background: #2563eb;
        }
        .typing-indicator {
            display: flex;
            gap: 4px;
            padding: 12px 14px;
            align-items: center;
        }
        .typing-dot {
            width: 6px;
            height: 6px;
            background: #9ca3af;
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out both;
        }
        .typing-dot:nth-child(1) { animation-delay: -0.32s; }
        .typing-dot:nth-child(2) { animation-delay: -0.16s; }
        @keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }
        
        /* Markdown formatting for bot replies */
        .chat-bot p { margin: 0 0 8px 0; }
        .chat-bot p:last-child { margin: 0; }
        .chat-bot ul { margin: 0; padding-left: 20px; }
        .chat-bot strong { font-weight: 600; }
    `;
    document.head.appendChild(style);

    // Provide fonts just in case
    const font = document.createElement('link');
    font.href = 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap';
    font.rel = 'stylesheet';
    document.head.appendChild(font);

    // Widget HTML
    const container = document.createElement('div');
    container.id = 'chatbot-widget-container';
    container.innerHTML = `
        <div id="chatbot-window">
            <div id="chatbot-header">
                <div style="display:flex; align-items:center; gap: 8px;">
                    <div style="width:10px; height:10px; background:#22c55e; border-radius:50%;"></div>
                    <span>Assistant virtuel</span>
                </div>
                <button id="chatbot-close-btn">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"></path></svg>
                </button>
            </div>
            <div id="chatbot-messages">
                <div class="chat-bubble chat-bot" id="initial-welcome">Chargement...</div>
            </div>
            <div id="chatbot-input-area">
                <input type="text" id="chatbot-input" placeholder="Écrivez votre message..." autocomplete="off">
                <button id="chatbot-send-btn">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="transform: translateX(-1px) translateY(1px) rotate(-45deg);"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"></path></svg>
                </button>
            </div>
        </div>
        <button id="chatbot-toggle-btn">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>
        </button>
    `;
    document.body.appendChild(container);

    const toggleBtn = document.getElementById('chatbot-toggle-btn');
    const closeBtn = document.getElementById('chatbot-close-btn');
    const windowEl = document.getElementById('chatbot-window');
    const inputEl = document.getElementById('chatbot-input');
    const sendBtn = document.getElementById('chatbot-send-btn');
    const messagesEl = document.getElementById('chatbot-messages');

    let history = [];

    function toggleChat() {
        const isOpen = windowEl.classList.contains('open');
        if (isOpen) {
            windowEl.style.opacity = '0';
            windowEl.style.transform = 'translateY(20px)';
            setTimeout(() => windowEl.classList.remove('open'), 300);
        } else {
            windowEl.style.display = 'flex';
            // Trigger reflow
            void windowEl.offsetWidth;
            windowEl.classList.add('open');
            windowEl.style.opacity = '1';
            windowEl.style.transform = 'translateY(0)';
            inputEl.focus();
        }
    }

    toggleBtn.addEventListener('click', toggleChat);
    closeBtn.addEventListener('click', toggleChat);

    function addMessage(text, isUser) {
        const div = document.createElement('div');
        div.className = `chat-bubble ${isUser ? 'chat-user' : 'chat-bot'}`;
        
        if (!isUser) {
            // Simple markdown bold conversion
            const bolded = text.replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>');
            // Line breaks
            div.innerHTML = bolded.replace(/\\n/g, '<br/>');
        } else {
            div.textContent = text;
        }
        
        messagesEl.appendChild(div);
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function showTyping() {
        const div = document.createElement('div');
        div.className = 'chat-bubble chat-bot typing-indicator';
        div.id = 'typing-indicator';
        div.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';
        messagesEl.appendChild(div);
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function hideTyping() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) indicator.remove();
    }

    async function sendMessage() {
        const text = inputEl.value.trim();
        if (!text) return;

        addMessage(text, true);
        inputEl.value = '';
        inputEl.disabled = true;

        showTyping();

        try {
            const response = await fetch(backendOrigin + '/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ client_id: clientId, message: text, history: history })
            });
            const data = await response.json();
            hideTyping();
            
            if (response.ok && data.response) {
                // Save to history
                history.push({role: 'user', message: text});
                history.push({role: 'model', message: data.response});
                addMessage(data.response, false);
            } else {
                addMessage("Erreur de connexion au serveur (Vérifiez la clé API Gemini sur le serveur).", false);
            }
        } catch (e) {
            hideTyping();
            addMessage("Une erreur s'est produite lors de la connexion au serveur local.", false);
        }

        inputEl.disabled = false;
        inputEl.focus();
    }

    sendBtn.addEventListener('click', sendMessage);
    inputEl.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    // Initialize welcome message
    (async function() {
        if (clientId) {
            try {
                const res = await fetch(backendOrigin + '/api/get-client-profile?id=' + encodeURIComponent(clientId));
                const data = await res.json();
                if (data.welcome) {
                    document.getElementById('initial-welcome').textContent = data.welcome;
                    return;
                }
            } catch (e) {}
        }
        document.getElementById('initial-welcome').textContent = "Bonjour ! Comment puis-je vous aider aujourd'hui ?";
    })();
})();
