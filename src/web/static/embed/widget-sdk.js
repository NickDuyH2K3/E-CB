/**
 * E-CB Chatbot Widget SDK
 * Version: 2.0.0
 * A modern, flexible chatbot embedding solution
 */

(function(window) {
    'use strict';

    const ECB_WIDGET_VERSION = '2.0.0';
    const DEFAULT_CONFIG = {
        // Core settings
        apiUrl: '',
        botId: '',
        
        // Appearance
        theme: 'modern',
        primaryColor: '#007bff',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
        borderRadius: '12px',
        
        // Behavior
        embedStyle: 'popup', // 'popup', 'inline', 'fullscreen', 'drawer'
        autoOpen: false,
        showWelcomeMessage: true,
        persistSession: true,
        
        // Messages
        welcomeMessage: 'Hello! How can I help you today?',
        placeholder: 'Type your message...',
        sendButtonText: 'Send',
        
        // Position (for popup style)
        position: 'bottom-right', // 'bottom-right', 'bottom-left', 'top-right', 'top-left'
        offset: { x: 20, y: 20 },
        
        // Size
        width: 350,
        height: 500,
        
        // Features
        enableTypingIndicator: true,
        enableFileUpload: false,
        enableEmojis: true,
        enableSuggestions: true,
        
        // Advanced
        debug: false,
        customCSS: '',
        onReady: null,
        onOpen: null,
        onClose: null,
        onMessage: null,
        onError: null
    };

    class ECBWidget {
        constructor(config = {}) {
            this.config = { ...DEFAULT_CONFIG, ...config };
            this.isOpen = false;
            this.sessionId = this.generateSessionId();
            this.elements = {};
            this.messageQueue = [];
            this.isTyping = false;
            
            this.validateConfig();
            this.init();
        }

        validateConfig() {
            if (!this.config.botId) {
                throw new Error('ECB Widget: botId is required');
            }
            if (!this.config.apiUrl) {
                this.config.apiUrl = `${window.location.origin}/api/chat/${this.config.botId}`;
            }
        }

        generateSessionId() {
            return 'ecb_session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        }

        init() {
            this.loadStyles();
            this.createWidget();
            this.attachEventListeners();
            
            if (this.config.persistSession) {
                this.loadSession();
            }
            
            if (this.config.onReady) {
                this.config.onReady(this);
            }
        }

        loadStyles() {
            const styleId = 'ecb-widget-styles';
            if (document.getElementById(styleId)) return;

            const style = document.createElement('style');
            style.id = styleId;
            style.textContent = this.getWidgetStyles();
            document.head.appendChild(style);

            // Load custom CSS if provided
            if (this.config.customCSS) {
                const customStyle = document.createElement('style');
                customStyle.textContent = this.config.customCSS;
                document.head.appendChild(customStyle);
            }
        }

        getWidgetStyles() {
            return `
                .ecb-widget {
                    --primary-color: ${this.config.primaryColor};
                    --font-family: ${this.config.fontFamily};
                    --border-radius: ${this.config.borderRadius};
                    font-family: var(--font-family);
                    z-index: 999999;
                }
                
                .ecb-popup-trigger {
                    position: fixed;
                    width: 60px;
                    height: 60px;
                    border-radius: 50%;
                    background: var(--primary-color);
                    color: white;
                    border: none;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 24px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }
                
                .ecb-popup-trigger:hover {
                    transform: scale(1.1);
                    box-shadow: 0 6px 25px rgba(0,0,0,0.2);
                }
                
                .ecb-chat-window {
                    position: fixed;
                    width: ${this.config.width}px;
                    height: ${this.config.height}px;
                    background: white;
                    border-radius: var(--border-radius);
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    display: flex;
                    flex-direction: column;
                    opacity: 0;
                    transform: translateY(20px) scale(0.9);
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    overflow: hidden;
                }
                
                .ecb-chat-window.open {
                    opacity: 1;
                    transform: translateY(0) scale(1);
                }
                
                .ecb-chat-header {
                    background: var(--primary-color);
                    color: white;
                    padding: 16px 20px;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                }
                
                .ecb-chat-messages {
                    flex: 1;
                    padding: 16px;
                    overflow-y: auto;
                    scroll-behavior: smooth;
                }
                
                .ecb-message {
                    margin: 8px 0;
                    animation: messageSlideIn 0.3s ease-out;
                }
                
                .ecb-message-content {
                    max-width: 80%;
                    padding: 12px 16px;
                    border-radius: 18px;
                    word-wrap: break-word;
                    line-height: 1.4;
                }
                
                .ecb-message.user .ecb-message-content {
                    background: var(--primary-color);
                    color: white;
                    margin-left: auto;
                    border-bottom-right-radius: 6px;
                }
                
                .ecb-message.bot .ecb-message-content {
                    background: #f1f3f5;
                    color: #333;
                    border-bottom-left-radius: 6px;
                }
                
                .ecb-typing-indicator {
                    display: flex;
                    align-items: center;
                    padding: 12px 16px;
                    background: #f1f3f5;
                    border-radius: 18px;
                    max-width: 60px;
                    margin: 8px 0;
                }
                
                .ecb-typing-dots {
                    display: flex;
                    gap: 4px;
                }
                
                .ecb-typing-dot {
                    width: 6px;
                    height: 6px;
                    border-radius: 50%;
                    background: #999;
                    animation: typingPulse 1.4s infinite;
                }
                
                .ecb-typing-dot:nth-child(2) { animation-delay: 0.2s; }
                .ecb-typing-dot:nth-child(3) { animation-delay: 0.4s; }
                
                .ecb-input-area {
                    padding: 16px;
                    border-top: 1px solid #e9ecef;
                    display: flex;
                    gap: 12px;
                    align-items: flex-end;
                }
                
                .ecb-input {
                    flex: 1;
                    padding: 12px 16px;
                    border: 2px solid #e9ecef;
                    border-radius: 24px;
                    outline: none;
                    resize: none;
                    font-family: inherit;
                    font-size: 14px;
                    transition: border-color 0.2s;
                }
                
                .ecb-input:focus {
                    border-color: var(--primary-color);
                }
                
                .ecb-send-button {
                    width: 44px;
                    height: 44px;
                    background: var(--primary-color);
                    color: white;
                    border: none;
                    border-radius: 50%;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: all 0.2s;
                }
                
                .ecb-send-button:hover:not(:disabled) {
                    transform: scale(1.05);
                }
                
                .ecb-send-button:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                }
                
                @keyframes messageSlideIn {
                    from {
                        opacity: 0;
                        transform: translateY(10px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
                
                @keyframes typingPulse {
                    0%, 60%, 100% { opacity: 0.3; }
                    30% { opacity: 1; }
                }
                
                /* Responsive design */
                @media (max-width: 480px) {
                    .ecb-chat-window {
                        width: calc(100vw - 20px) !important;
                        height: calc(100vh - 20px) !important;
                        top: 10px !important;
                        left: 10px !important;
                        right: 10px !important;
                        bottom: 10px !important;
                    }
                }
            `;
        }

        createWidget() {
            const container = document.getElementById(`ecb-chatbot-${this.config.botId}`) || document.body;
            
            switch (this.config.embedStyle) {
                case 'popup':
                    this.createPopupWidget(container);
                    break;
                case 'inline':
                    this.createInlineWidget(container);
                    break;
                case 'fullscreen':
                    this.createFullscreenWidget(container);
                    break;
                case 'drawer':
                    this.createDrawerWidget(container);
                    break;
                default:
                    this.createPopupWidget(container);
            }
        }

        createPopupWidget(container) {
            const widget = document.createElement('div');
            widget.className = 'ecb-widget ecb-popup-widget';
            
            // Position the popup trigger
            const position = this.config.position.split('-');
            const trigger = document.createElement('button');
            trigger.className = 'ecb-popup-trigger';
            trigger.innerHTML = '💬';
            trigger.style[position[1]] = this.config.offset.x + 'px';
            trigger.style[position[0]] = this.config.offset.y + 'px';
            
            // Position the chat window
            const chatWindow = this.createChatWindow();
            chatWindow.style[position[1]] = this.config.offset.x + 'px';
            chatWindow.style[position[0]] = (this.config.offset.y + 80) + 'px';
            
            widget.appendChild(trigger);
            widget.appendChild(chatWindow);
            container.appendChild(widget);
            
            this.elements.trigger = trigger;
            this.elements.chatWindow = chatWindow;
        }

        createInlineWidget(container) {
            const widget = document.createElement('div');
            widget.className = 'ecb-widget ecb-inline-widget';
            
            const chatWindow = this.createChatWindow();
            chatWindow.style.position = 'relative';
            chatWindow.style.opacity = '1';
            chatWindow.style.transform = 'none';
            chatWindow.classList.add('open');
            
            widget.appendChild(chatWindow);
            container.appendChild(widget);
            
            this.elements.chatWindow = chatWindow;
            this.isOpen = true;
        }

        createChatWindow() {
            const chatWindow = document.createElement('div');
            chatWindow.className = 'ecb-chat-window';
            
            // Header
            const header = document.createElement('div');
            header.className = 'ecb-chat-header';
            header.innerHTML = `
                <div>
                    <div style="font-weight: 600;">${this.config.botName || 'Chatbot'}</div>
                    <div style="font-size: 12px; opacity: 0.8;">Online</div>
                </div>
                ${this.config.embedStyle === 'popup' ? '<button class="ecb-close-button" style="background: none; border: none; color: white; font-size: 20px; cursor: pointer;">×</button>' : ''}
            `;
            
            // Messages area
            const messages = document.createElement('div');
            messages.className = 'ecb-chat-messages';
            
            // Input area
            const inputArea = document.createElement('div');
            inputArea.className = 'ecb-input-area';
            inputArea.innerHTML = `
                <textarea class="ecb-input" placeholder="${this.config.placeholder}" rows="1"></textarea>
                <button class="ecb-send-button">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                    </svg>
                </button>
            `;
            
            chatWindow.appendChild(header);
            chatWindow.appendChild(messages);
            chatWindow.appendChild(inputArea);
            
            this.elements.messages = messages;
            this.elements.input = inputArea.querySelector('.ecb-input');
            this.elements.sendButton = inputArea.querySelector('.ecb-send-button');
            this.elements.closeButton = header.querySelector('.ecb-close-button');
            
            // Add welcome message
            if (this.config.showWelcomeMessage) {
                this.addMessage(this.config.welcomeMessage, 'bot');
            }
            
            return chatWindow;
        }

        attachEventListeners() {
            // Trigger button
            if (this.elements.trigger) {
                this.elements.trigger.addEventListener('click', () => this.toggleChat());
            }
            
            // Close button
            if (this.elements.closeButton) {
                this.elements.closeButton.addEventListener('click', () => this.closeChat());
            }
            
            // Send button
            this.elements.sendButton.addEventListener('click', () => this.sendMessage());
            
            // Input field
            this.elements.input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
            
            // Auto-resize textarea
            this.elements.input.addEventListener('input', () => {
                this.elements.input.style.height = 'auto';
                this.elements.input.style.height = Math.min(this.elements.input.scrollHeight, 100) + 'px';
            });
        }

        toggleChat() {
            if (this.isOpen) {
                this.closeChat();
            } else {
                this.openChat();
            }
        }

        openChat() {
            this.isOpen = true;
            this.elements.chatWindow.style.display = 'flex';
            setTimeout(() => {
                this.elements.chatWindow.classList.add('open');
            }, 10);
            
            if (this.config.onOpen) {
                this.config.onOpen(this);
            }
        }

        closeChat() {
            this.isOpen = false;
            this.elements.chatWindow.classList.remove('open');
            setTimeout(() => {
                this.elements.chatWindow.style.display = 'none';
            }, 300);
            
            if (this.config.onClose) {
                this.config.onClose(this);
            }
        }

        async sendMessage() {
            const message = this.elements.input.value.trim();
            if (!message) return;
            
            this.addMessage(message, 'user');
            this.elements.input.value = '';
            this.elements.input.style.height = 'auto';
            this.elements.sendButton.disabled = true;
            
            if (this.config.enableTypingIndicator) {
                this.showTypingIndicator();
            }
            
            try {
                const response = await this.sendToAPI(message);
                this.hideTypingIndicator();
                this.addMessage(response.response, 'bot');
                
                if (this.config.onMessage) {
                    this.config.onMessage({ message, response: response.response, sender: 'bot' });
                }
            } catch (error) {
                this.hideTypingIndicator();
                this.addMessage('Sorry, there was an error processing your message.', 'bot');
                
                if (this.config.onError) {
                    this.config.onError(error);
                }
            } finally {
                this.elements.sendButton.disabled = false;
            }
        }

        async sendToAPI(message) {
            const response = await fetch(this.config.apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        }

        addMessage(text, sender) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `ecb-message ${sender}`;
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'ecb-message-content';
            contentDiv.textContent = text;
            
            messageDiv.appendChild(contentDiv);
            this.elements.messages.appendChild(messageDiv);
            this.elements.messages.scrollTop = this.elements.messages.scrollHeight;
            
            if (this.config.persistSession) {
                this.saveSession();
            }
        }

        showTypingIndicator() {
            if (this.elements.typingIndicator) return;
            
            const indicator = document.createElement('div');
            indicator.className = 'ecb-typing-indicator';
            indicator.innerHTML = `
                <div class="ecb-typing-dots">
                    <div class="ecb-typing-dot"></div>
                    <div class="ecb-typing-dot"></div>
                    <div class="ecb-typing-dot"></div>
                </div>
            `;
            
            this.elements.messages.appendChild(indicator);
            this.elements.messages.scrollTop = this.elements.messages.scrollHeight;
            this.elements.typingIndicator = indicator;
            this.isTyping = true;
        }

        hideTypingIndicator() {
            if (this.elements.typingIndicator) {
                this.elements.typingIndicator.remove();
                this.elements.typingIndicator = null;
                this.isTyping = false;
            }
        }

        saveSession() {
            if (!this.config.persistSession) return;
            
            const sessionData = {
                sessionId: this.sessionId,
                messages: Array.from(this.elements.messages.children)
                    .filter(el => !el.classList.contains('ecb-typing-indicator'))
                    .map(el => ({
                        text: el.querySelector('.ecb-message-content').textContent,
                        sender: el.classList.contains('user') ? 'user' : 'bot'
                    }))
            };
            
            localStorage.setItem(`ecb_session_${this.config.botId}`, JSON.stringify(sessionData));
        }

        loadSession() {
            const savedSession = localStorage.getItem(`ecb_session_${this.config.botId}`);
            if (!savedSession) return;
            
            try {
                const sessionData = JSON.parse(savedSession);
                this.sessionId = sessionData.sessionId;
                
                // Clear welcome message if we're loading a session
                if (this.config.showWelcomeMessage) {
                    this.elements.messages.innerHTML = '';
                }
                
                sessionData.messages.forEach(msg => {
                    this.addMessage(msg.text, msg.sender);
                });
            } catch (error) {
                console.warn('ECB Widget: Could not load session data', error);
            }
        }

        // Public API methods
        destroy() {
            if (this.elements.widget) {
                this.elements.widget.remove();
            }
            const styles = document.getElementById('ecb-widget-styles');
            if (styles) styles.remove();
        }

        updateConfig(newConfig) {
            this.config = { ...this.config, ...newConfig };
            // Re-initialize with new config
            this.destroy();
            this.init();
        }

        clearHistory() {
            this.elements.messages.innerHTML = '';
            if (this.config.showWelcomeMessage) {
                this.addMessage(this.config.welcomeMessage, 'bot');
            }
            localStorage.removeItem(`ecb_session_${this.config.botId}`);
        }
    }

    // Global API
    window.ECBWidget = ECBWidget;
    
    // Auto-initialization support
    window.addEventListener('DOMContentLoaded', () => {
        // Look for auto-init elements
        const autoInitElements = document.querySelectorAll('[data-ecb-auto-init]');
        autoInitElements.forEach(element => {
            const config = {
                botId: element.dataset.ecbBotId,
                ...JSON.parse(element.dataset.ecbConfig || '{}')
            };
            
            new ECBWidget(config);
        });
    });

})(window); 