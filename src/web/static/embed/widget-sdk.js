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
                
                .ecb-drawer-trigger {
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
                    z-index: 999999;
                }
                
                .ecb-drawer-trigger:hover {
                    transform: scale(1.1);
                    box-shadow: 0 6px 25px rgba(0,0,0,0.2);
                }
                
                .ecb-drawer-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100vw;
                    height: 100vh;
                    background: rgba(0,0,0,0.5);
                    opacity: 0;
                    visibility: hidden;
                    transition: opacity 0.3s ease, visibility 0.3s ease;
                    z-index: 999997;
                }
                
                .ecb-drawer-overlay.active {
                    opacity: 1;
                    visibility: visible;
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
                
                .ecb-inline-widget {
                    width: 100%;
                    max-width: 100%;
                    display: block;
                }
                
                .ecb-inline-widget .ecb-chat-window {
                    position: relative;
                    width: 100%;
                    height: auto;
                    min-height: 400px;
                    max-height: 600px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                    opacity: 1;
                    transform: none;
                    margin: 0;
                    overflow: visible;
                }
                
                .ecb-inline-widget .ecb-chat-messages {
                    min-height: 250px;
                    max-height: 350px;
                    overflow-y: auto;
                    flex: 1;
                }
                
                .ecb-inline-widget .ecb-input-area {
                    flex-shrink: 0;
                    position: relative;
                    bottom: 0;
                    width: 100%;
                    background: white;
                    border-top: 1px solid #e9ecef;
                    z-index: 10;
                    padding: 16px;
                    min-height: 70px;
                }
                
                .ecb-inline-widget .ecb-input {
                    min-height: 40px;
                    max-height: 100px;
                    background: white;
                    border: 2px solid #e9ecef;
                    font-size: 14px;
                    padding: 12px 16px;
                }
                
                .ecb-inline-widget .ecb-input:focus {
                    border-color: var(--primary-color);
                    box-shadow: 0 0 0 1px var(--primary-color);
                }
                
                .ecb-drawer-widget .ecb-chat-window {
                    position: fixed;
                    top: 0;
                    right: -400px;
                    width: 400px;
                    height: 100vh;
                    border-radius: 0;
                    transform: none;
                    opacity: 1;
                    transition: right 0.3s ease-in-out;
                    z-index: 999998;
                    box-shadow: -5px 0 20px rgba(0,0,0,0.2);
                }
                
                .ecb-drawer-widget .ecb-chat-window.open {
                    right: 0px;
                }
                
                .ecb-fullscreen-container {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100vw;
                    height: 100vh;
                    background: white;
                    z-index: 999999;
                    display: flex;
                    flex-direction: column;
                    opacity: 0;
                    visibility: hidden;
                    transition: opacity 0.3s ease, visibility 0.3s ease;
                }
                
                .ecb-fullscreen-container.open {
                    opacity: 1;
                    visibility: visible;
                }
                
                .ecb-fullscreen-trigger {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
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
                    z-index: 999999;
                }
                
                .ecb-fullscreen-trigger:hover {
                    transform: scale(1.1);
                    box-shadow: 0 6px 25px rgba(0,0,0,0.2);
                }
                
                .ecb-fullscreen-close {
                    position: absolute;
                    top: 20px;
                    right: 20px;
                    width: 40px;
                    height: 40px;
                    background: rgba(0,0,0,0.1);
                    color: #666;
                    border: none;
                    border-radius: 50%;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 24px;
                    transition: all 0.2s;
                    z-index: 1000000;
                }
                
                .ecb-fullscreen-close:hover {
                    background: rgba(0,0,0,0.2);
                }
                
                .ecb-chat-header {
                    background: var(--primary-color);
                    color: white;
                    padding: 16px 20px;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                }
                
                .ecb-close-button {
                    background: none;
                    border: none;
                    color: white;
                    font-size: 20px;
                    cursor: pointer;
                    padding: 4px;
                    border-radius: 4px;
                    transition: background-color 0.2s;
                }
                
                .ecb-close-button:hover {
                    background: rgba(255,255,255,0.1);
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
                    
                    .ecb-inline-widget .ecb-chat-window {
                        width: 100% !important;
                        height: auto !important;
                        position: relative !important;
                        top: auto !important;
                        left: auto !important;
                        right: auto !important;
                        bottom: auto !important;
                        min-height: 350px !important;
                        max-height: 500px !important;
                        overflow: visible !important;
                    }
                    
                    .ecb-inline-widget .ecb-chat-messages {
                        min-height: 200px !important;
                        max-height: 300px !important;
                    }
                    
                    .ecb-inline-widget .ecb-input-area {
                        min-height: 70px !important;
                        padding: 12px !important;
                    }
                    
                    .ecb-drawer-widget .ecb-chat-window {
                        width: 100vw !important;
                        right: -100vw !important;
                    }
                    
                    .ecb-drawer-widget .ecb-chat-window.open {
                        right: 0px !important;
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
            chatWindow.classList.add('open');
            
            widget.appendChild(chatWindow);
            container.appendChild(widget);
            
            this.elements.chatWindow = chatWindow;
            this.isOpen = true;
        }

        createDrawerWidget(container) {
            const widget = document.createElement('div');
            widget.className = 'ecb-widget ecb-drawer-widget';
            
            // Create trigger button
            const trigger = document.createElement('button');
            trigger.className = 'ecb-drawer-trigger';
            trigger.innerHTML = '💬';
            
            // Create drawer chat window
            const chatWindow = this.createChatWindow();
            
            // Create overlay
            const overlay = document.createElement('div');
            overlay.className = 'ecb-drawer-overlay';
            
            widget.appendChild(trigger);
            widget.appendChild(overlay);
            widget.appendChild(chatWindow);
            container.appendChild(widget);
            
            this.elements.trigger = trigger;
            this.elements.chatWindow = chatWindow;
            this.elements.overlay = overlay;
            
            // Override open/close methods for drawer behavior
            this.openChat = () => {
                this.isOpen = true;
                chatWindow.classList.add('open');
                overlay.classList.add('active');
                if (this.config.onOpen) this.config.onOpen(this);
            };
            
            this.closeChat = () => {
                this.isOpen = false;
                chatWindow.classList.remove('open');
                overlay.classList.remove('active');
                if (this.config.onClose) this.config.onClose(this);
            };
        }

        createFullscreenWidget(container) {
            const widget = document.createElement('div');
            widget.className = 'ecb-widget ecb-fullscreen-widget';
            
            // Create trigger button
            const trigger = document.createElement('button');
            trigger.className = 'ecb-fullscreen-trigger';
            trigger.innerHTML = '💬';
            
            // Create fullscreen chat container
            const fullscreenContainer = document.createElement('div');
            fullscreenContainer.className = 'ecb-fullscreen-container';
            
            // Create fullscreen header
            const fullscreenHeader = document.createElement('div');
            fullscreenHeader.style.background = this.config.primaryColor;
            fullscreenHeader.style.color = 'white';
            fullscreenHeader.style.padding = '15px 20px';
            fullscreenHeader.style.display = 'flex';
            fullscreenHeader.style.justifyContent = 'space-between';
            fullscreenHeader.style.alignItems = 'center';
            fullscreenHeader.innerHTML = `
                <div>
                    <h3 style="margin: 0; font-size: 18px;">${this.config.botName || 'Chatbot'}</h3>
                    <p style="margin: 0; font-size: 14px; opacity: 0.8;">Online</p>
                </div>
                <button class="ecb-fullscreen-close" style="background: none; border: none; color: white; font-size: 24px; cursor: pointer; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">×</button>
            `;
            
            // Create chat window for fullscreen
            const chatWindow = this.createChatWindow();
            chatWindow.style.position = 'relative';
            chatWindow.style.flex = '1';
            chatWindow.style.height = 'auto';
            chatWindow.style.borderRadius = '0';
            chatWindow.style.boxShadow = 'none';
            chatWindow.style.opacity = '1';
            chatWindow.style.transform = 'none';
            // Remove the default header since we have a custom one
            const defaultHeader = chatWindow.querySelector('.ecb-chat-header');
            if (defaultHeader) defaultHeader.remove();
            
            fullscreenContainer.appendChild(fullscreenHeader);
            fullscreenContainer.appendChild(chatWindow);
            
            widget.appendChild(trigger);
            widget.appendChild(fullscreenContainer);
            container.appendChild(widget);
            
            this.elements.trigger = trigger;
            this.elements.chatWindow = chatWindow;
            this.elements.fullscreenContainer = fullscreenContainer;
            this.elements.fullscreenClose = fullscreenHeader.querySelector('.ecb-fullscreen-close');
            
            // Override open/close methods for fullscreen behavior
            this.openChat = () => {
                this.isOpen = true;
                fullscreenContainer.classList.add('open');
                if (this.config.onOpen) this.config.onOpen(this);
            };
            
            this.closeChat = () => {
                this.isOpen = false;
                fullscreenContainer.classList.remove('open');
                if (this.config.onClose) this.config.onClose(this);
            };
            
            // Auto-open if this is fullscreen (since it's likely the only widget on the page)
            if (this.config.autoOpen) {
                setTimeout(() => this.openChat(), 100);
            }
        }

        createChatWindow() {
            const chatWindow = document.createElement('div');
            chatWindow.className = 'ecb-chat-window';
            
            // Header
            const header = document.createElement('div');
            header.className = 'ecb-chat-header';
            
            const showCloseButton = this.config.embedStyle === 'popup' || this.config.embedStyle === 'drawer';
            
            header.innerHTML = `
                <div>
                    <div style="font-weight: 600;">${this.config.botName || 'Chatbot'}</div>
                    <div style="font-size: 12px; opacity: 0.8;">Online</div>
                </div>
                ${showCloseButton ? '<button class="ecb-close-button" style="background: none; border: none; color: white; font-size: 20px; cursor: pointer;">×</button>' : ''}
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
            
            // Drawer overlay (click to close)
            if (this.elements.overlay) {
                this.elements.overlay.addEventListener('click', () => this.closeChat());
            }
            
            // Fullscreen close button
            if (this.elements.fullscreenClose) {
                this.elements.fullscreenClose.addEventListener('click', () => this.closeChat());
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
            // Remove all widget elements
            if (this.elements.widget) {
                this.elements.widget.remove();
            }
            
            // Clean up individual elements
            const elementsToRemove = [
                '.ecb-widget',
                '.ecb-popup-trigger',
                '.ecb-chat-window',
                '.ecb-drawer-overlay',
                '.ecb-fullscreen-container'
            ];
            
            elementsToRemove.forEach(selector => {
                const elements = document.querySelectorAll(selector);
                elements.forEach(el => el.remove());
            });
            
            // Remove styles (but check if other widgets are still using them)
            const otherWidgets = document.querySelectorAll('.ecb-widget');
            if (otherWidgets.length === 0) {
                const styles = document.getElementById('ecb-widget-styles');
                if (styles) styles.remove();
            }
            
            // Clear elements reference
            this.elements = {};
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