from flask import Blueprint, render_template, request, jsonify, current_app, Response
import os
import sys
import json
import uuid
import asyncio
from datetime import datetime

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from .base_routes import BotManager
from core.kernel import ChatbotKernel
from pipeline.input_handler import InputHandler
from pipeline.nlu import SimpleNLU, SpacyNLU
from pipeline.response_generator import ResponseGenerator

embed_routes = Blueprint('embed_routes', __name__)

# Store active bot instances
active_bots = {}

def initialize_bot(bot_config):
    """Initialize a chatbot kernel from configuration"""
    kernel = ChatbotKernel()
    
    # Initialize components
    input_handler = InputHandler()
    
    # Choose NLU type based on config
    nlu_type = bot_config.get('settings', {}).get('nlu_type', 'simple')
    if nlu_type == 'spacy':
        nlu = SpacyNLU()
    else:
        nlu = SimpleNLU()
        if 'intents' in bot_config:
            nlu.patterns = bot_config['intents']
    
    # Initialize response generator
    response_generator = ResponseGenerator()
    if 'responses' in bot_config:
        response_generator.templates = bot_config['responses']
    
    # Register components
    kernel.register_component('input_handler', input_handler)
    kernel.register_component('nlu', nlu)
    kernel.register_component('response_generator', response_generator)
    
    return kernel

@embed_routes.route('/bot/<bot_id>/embed-code')
def get_embed_code(bot_id):
    """Generate embeddable HTML/JavaScript code for the chatbot"""
    bots = BotManager.load_bots(current_app)
    
    if bot_id not in bots:
        return jsonify({'error': 'Bot not found'}), 404
    
    bot_config = bots[bot_id]
    settings = bot_config.get('settings', {})
    appearance = settings.get('appearance', {})
    
    # Generate embed code
    embed_script = f'''
<!-- E-CB Chatbot Embed -->
<div id="ecb-chatbot-{bot_id}"></div>
<script>
(function() {{
    var chatbotConfig = {{
        botId: '{bot_id}',
        apiUrl: '{request.url_root}api/chat/{bot_id}',
        theme: '{appearance.get("theme", "default")}',
        primaryColor: '{appearance.get("primary_color", "#007bff")}',
        botName: '{appearance.get("bot_name_display", bot_config.get("name", "Chatbot"))}',
        welcomeMessage: '{appearance.get("welcome_message", "Hello! How can I help you today?")}',
        embedStyle: '{settings.get("integration", {}).get("embed_style", "popup")}'
    }};
    
    var script = document.createElement('script');
    script.src = '{request.url_root}static/embed/chatbot-widget.js';
    script.onload = function() {{
        ECBChatbot.init(chatbotConfig);
    }};
    document.head.appendChild(script);
    
    var link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = '{request.url_root}static/embed/chatbot-widget.css';
    document.head.appendChild(link);
}})();
</script>
<!-- End E-CB Chatbot Embed -->
'''
    
    return jsonify({
        'embed_code': embed_script.strip(),
        'preview_url': f"{request.url_root}bot/{bot_id}/embed-preview",
        'api_endpoint': f"{request.url_root}api/chat/{bot_id}"
    })

@embed_routes.route('/bot/<bot_id>/embed-preview')
def embed_preview(bot_id):
    """Preview page for the embedded chatbot"""
    bots = BotManager.load_bots(current_app)
    
    if bot_id not in bots:
        return "Bot not found", 404
    
    bot_config = bots[bot_id]
    return render_template('embed_preview.html', bot=bot_config, bot_id=bot_id)

@embed_routes.route('/api/chat/<bot_id>', methods=['POST'])
def chat_api(bot_id):
    """API endpoint for chatbot interactions"""
    bots = BotManager.load_bots(current_app)
    
    if bot_id not in bots:
        return jsonify({'error': 'Bot not found'}), 404
    
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Message is required'}), 400
    
    user_message = data['message']
    session_id = data.get('session_id', str(uuid.uuid4()))
    
    try:
        # Initialize bot if not already active
        if bot_id not in active_bots:
            active_bots[bot_id] = initialize_bot(bots[bot_id])
        
        kernel = active_bots[bot_id]
        
        # Process message synchronously for now (can be made async later)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(kernel.process_message(user_message))
        loop.close()
        
        return jsonify({
            'response': response,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'bot_id': bot_id
        })
        
    except Exception as e:
        error_response = bots[bot_id].get('settings', {}).get('error_handling', {}).get('default_response', 
                                                                                        "I'm sorry, something went wrong.")
        return jsonify({
            'response': error_response,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'bot_id': bot_id,
            'error': str(e) if current_app.debug else None
        })

@embed_routes.route('/api/bot/<bot_id>/status')
def bot_status(bot_id):
    """Get bot status and basic information"""
    bots = BotManager.load_bots(current_app)
    
    if bot_id not in bots:
        return jsonify({'error': 'Bot not found'}), 404
    
    bot_config = bots[bot_id]
    settings = bot_config.get('settings', {})
    
    return jsonify({
        'bot_id': bot_id,
        'name': bot_config.get('name'),
        'description': bot_config.get('description'),
        'active': bot_id in active_bots,
        'integration_enabled': settings.get('integration', {}).get('enabled', True),
        'nlu_type': settings.get('nlu_type', 'simple')
    })

@embed_routes.route('/static/embed/chatbot-widget.js')
def chatbot_widget_js():
    """Serve the chatbot widget JavaScript"""
    js_content = '''
window.ECBChatbot = (function() {
    var config = {};
    var isOpen = false;
    var sessionId = null;
    
    function init(botConfig) {
        config = botConfig;
        sessionId = generateSessionId();
        createWidget();
        attachEventListeners();
    }
    
    function generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    function createWidget() {
        var container = document.getElementById('ecb-chatbot-' + config.botId);
        if (!container) return;
        
        if (config.embedStyle === 'popup') {
            createPopupWidget(container);
        } else {
            createInlineWidget(container);
        }
    }
    
    function createPopupWidget(container) {
        container.innerHTML = `
            <div id="ecb-chat-button" style="
                position: fixed;
                bottom: 20px;
                right: 20px;
                width: 60px;
                height: 60px;
                background-color: ${config.primaryColor};
                border-radius: 50%;
                cursor: pointer;
                box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1000;
                color: white;
                font-size: 24px;
            ">💬</div>
            
            <div id="ecb-chat-window" style="
                position: fixed;
                bottom: 90px;
                right: 20px;
                width: 350px;
                height: 500px;
                background: white;
                border-radius: 10px;
                box-shadow: 0 5px 30px rgba(0,0,0,0.3);
                display: none;
                flex-direction: column;
                z-index: 1001;
                font-family: Arial, sans-serif;
            ">
                <div style="
                    background-color: ${config.primaryColor};
                    color: white;
                    padding: 15px;
                    border-radius: 10px 10px 0 0;
                    font-weight: bold;
                ">${config.botName}</div>
                
                <div id="ecb-chat-messages" style="
                    flex: 1;
                    padding: 10px;
                    overflow-y: auto;
                    border-bottom: 1px solid #eee;
                ">
                    <div class="ecb-message ecb-bot-message">${config.welcomeMessage}</div>
                </div>
                
                <div style="display: flex; padding: 10px;">
                    <input type="text" id="ecb-message-input" placeholder="Type your message..." style="
                        flex: 1;
                        padding: 10px;
                        border: 1px solid #ddd;
                        border-radius: 20px;
                        outline: none;
                    ">
                    <button id="ecb-send-button" style="
                        margin-left: 10px;
                        padding: 10px 15px;
                        background-color: ${config.primaryColor};
                        color: white;
                        border: none;
                        border-radius: 20px;
                        cursor: pointer;
                    ">Send</button>
                </div>
            </div>
        `;
    }
    
    function createInlineWidget(container) {
        container.innerHTML = `
            <div id="ecb-chat-window" style="
                width: 100%;
                height: 500px;
                background: white;
                border: 1px solid #ddd;
                border-radius: 10px;
                display: flex;
                flex-direction: column;
                font-family: Arial, sans-serif;
            ">
                <div style="
                    background-color: ${config.primaryColor};
                    color: white;
                    padding: 15px;
                    border-radius: 10px 10px 0 0;
                    font-weight: bold;
                ">${config.botName}</div>
                
                <div id="ecb-chat-messages" style="
                    flex: 1;
                    padding: 10px;
                    overflow-y: auto;
                    border-bottom: 1px solid #eee;
                ">
                    <div class="ecb-message ecb-bot-message">${config.welcomeMessage}</div>
                </div>
                
                <div style="display: flex; padding: 10px;">
                    <input type="text" id="ecb-message-input" placeholder="Type your message..." style="
                        flex: 1;
                        padding: 10px;
                        border: 1px solid #ddd;
                        border-radius: 20px;
                        outline: none;
                    ">
                    <button id="ecb-send-button" style="
                        margin-left: 10px;
                        padding: 10px 15px;
                        background-color: ${config.primaryColor};
                        color: white;
                        border: none;
                        border-radius: 20px;
                        cursor: pointer;
                    ">Send</button>
                </div>
            </div>
        `;
    }
    
    function attachEventListeners() {
        var chatButton = document.getElementById('ecb-chat-button');
        var chatWindow = document.getElementById('ecb-chat-window');
        var sendButton = document.getElementById('ecb-send-button');
        var messageInput = document.getElementById('ecb-message-input');
        
        if (chatButton) {
            chatButton.onclick = function() {
                isOpen = !isOpen;
                chatWindow.style.display = isOpen ? 'flex' : 'none';
            };
        }
        
        if (sendButton) {
            sendButton.onclick = sendMessage;
        }
        
        if (messageInput) {
            messageInput.onkeypress = function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            };
        }
    }
    
    function sendMessage() {
        var messageInput = document.getElementById('ecb-message-input');
        var message = messageInput.value.trim();
        
        if (!message) return;
        
        addMessage(message, 'user');
        messageInput.value = '';
        
        fetch(config.apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId
            })
        })
        .then(response => response.json())
        .then(data => {
            addMessage(data.response, 'bot');
        })
        .catch(error => {
            addMessage('Sorry, there was an error processing your message.', 'bot');
        });
    }
    
    function addMessage(text, sender) {
        var messagesContainer = document.getElementById('ecb-chat-messages');
        var messageDiv = document.createElement('div');
        messageDiv.className = 'ecb-message ecb-' + sender + '-message';
        messageDiv.style.cssText = `
            margin: 5px 0;
            padding: 8px 12px;
            border-radius: 15px;
            max-width: 80%;
            word-wrap: break-word;
            display: inline-block;
            ${sender === 'user' ? 
                'background-color: ' + config.primaryColor + '; color: white; margin-left: auto; float: right; clear: both;' : 
                'background-color: #f1f1f1; color: black; float: left; clear: both;'
            }
        `;
        messageDiv.textContent = text;
        
        // Create a wrapper div to handle the floating properly
        var wrapperDiv = document.createElement('div');
        wrapperDiv.style.cssText = 'width: 100%; overflow: hidden; margin: 2px 0;';
        wrapperDiv.appendChild(messageDiv);
        
        messagesContainer.appendChild(wrapperDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    return {
        init: init
    };
})();
'''
    
    return Response(js_content, mimetype='application/javascript')

@embed_routes.route('/static/embed/chatbot-widget.css')
def chatbot_widget_css():
    """Serve the chatbot widget CSS"""
    css_content = '''
.ecb-message {
    word-wrap: break-word;
    animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.ecb-message {
    animation: fadeIn 0.3s ease-in;
}

#ecb-chat-button:hover {
    transform: scale(1.1);
    transition: transform 0.2s ease;
}

#ecb-send-button:hover {
    opacity: 0.9;
}

#ecb-message-input:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 5px rgba(0, 123, 255, 0.3);
}
'''
    
    return Response(css_content, mimetype='text/css') 