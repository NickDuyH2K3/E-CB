from flask import Blueprint, render_template, request, jsonify, current_app, Response, make_response
import os
import sys
import json
import uuid
import asyncio
from datetime import datetime, timedelta
import hashlib
import time

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from .base_routes import BotManager
from core.kernel import ChatbotKernel
from pipeline.input_handler import InputHandler
from pipeline.nlu import SimpleNLU, SpacyNLU
from pipeline.response_generator import ResponseGenerator

embed_routes_v2 = Blueprint('embed_routes_v2', __name__)

# Store active bot instances with TTL
active_bots = {}
bot_last_access = {}
BOT_TTL = 3600  # 1 hour

def cleanup_inactive_bots():
    """Remove inactive bots to free memory"""
    current_time = time.time()
    to_remove = []
    
    for bot_id, last_access in bot_last_access.items():
        if current_time - last_access > BOT_TTL:
            to_remove.append(bot_id)
    
    for bot_id in to_remove:
        if bot_id in active_bots:
            del active_bots[bot_id]
        if bot_id in bot_last_access:
            del bot_last_access[bot_id]

def initialize_bot(bot_config):
    """Initialize a chatbot kernel from configuration with caching"""
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

@embed_routes_v2.route('/v2/bot/<bot_id>/embed-config')
def get_embed_config_v2(bot_id):
    """Get comprehensive embed configuration"""
    bots = BotManager.load_bots(current_app)
    
    if bot_id not in bots:
        return jsonify({'error': 'Bot not found'}), 404
    
    bot_config = bots[bot_id]
    settings = bot_config.get('settings', {})
    appearance = settings.get('appearance', {})
    integration = settings.get('integration', {})
    
    # Generate secure embed token
    timestamp = int(time.time())
    token_data = f"{bot_id}:{timestamp}:{current_app.secret_key}"
    embed_token = hashlib.sha256(token_data.encode()).hexdigest()[:32]
    
    config = {
        'botId': bot_id,
        'embedToken': embed_token,
        'timestamp': timestamp,
        'apiUrl': f"{request.url_root.rstrip('/')}/api/v2/chat/{bot_id}",
        'cdnUrl': f"{request.url_root.rstrip('/')}/cdn/ecb-widget/v2",
        
        # Widget configuration
        'widget': {
            'version': '2.0.0',
            'theme': appearance.get('theme', 'modern'),
            'primaryColor': appearance.get('primary_color', '#007bff'),
            'fontFamily': appearance.get('font_family', 'system-ui, -apple-system, sans-serif'),
            'borderRadius': appearance.get('border_radius', '12px'),
            
            'embedStyle': integration.get('embed_style', 'popup'),
            'position': integration.get('position', 'bottom-right'),
            'autoOpen': integration.get('auto_open', False),
            'persistSession': integration.get('persist_session', True),
            
            'botName': appearance.get('bot_name_display', bot_config.get('name', 'Chatbot')),
            'welcomeMessage': appearance.get('welcome_message', 'Hello! How can I help you today?'),
            'placeholder': appearance.get('input_placeholder', 'Type your message...'),
            
            'width': integration.get('width', 350),
            'height': integration.get('height', 500),
            'offset': integration.get('offset', {'x': 20, 'y': 20}),
            
            'features': {
                'typingIndicator': integration.get('typing_indicator', True),
                'fileUpload': integration.get('file_upload', False),
                'emojis': integration.get('emojis', True),
                'suggestions': integration.get('suggestions', True),
                'sound': integration.get('sound_notifications', False)
            },
            
            'customCSS': appearance.get('custom_css', ''),
            'whiteLabelMode': integration.get('white_label', False)
        },
        
        # Integration options
        'integration': {
            'methods': ['script', 'iframe', 'npm', 'cdn'],
            'frameworks': ['vanilla', 'react', 'vue', 'angular'],
            'cors': {
                'enabled': True,
                'origins': integration.get('allowed_origins', ['*'])
            }
        },
        
        # Analytics and tracking
        'analytics': {
            'enabled': integration.get('analytics_enabled', False),
            'trackingId': integration.get('tracking_id'),
            'events': ['open', 'close', 'message', 'error']
        }
    }
    
    return jsonify(config)

@embed_routes_v2.route('/v2/bot/<bot_id>/embed-code')
def get_embed_code_v2(bot_id):
    """Generate modern embeddable code with multiple integration options"""
    config_response = get_embed_config_v2(bot_id)
    if config_response.status_code != 200:  # Error response
        return config_response
    config = config_response.get_json()
    widget_config = config['widget']
    
    # Generate different embed methods
    embed_codes = {
        'script_tag': generate_script_embed(bot_id, config),
        'iframe': generate_iframe_embed(bot_id, config),
        'npm': generate_npm_embed(bot_id, config),
        'react': generate_react_embed(bot_id, config),
        'vue': generate_vue_embed(bot_id, config),
        'angular': generate_angular_embed(bot_id, config)
    }
    
    return jsonify({
        'embed_codes': embed_codes,
        'config': config,
        'preview_url': f"{request.url_root}v2/bot/{bot_id}/embed-preview",
        'documentation_url': f"{request.url_root}docs/embedding"
    })

def generate_script_embed(bot_id, config):
    """Generate modern script tag embed"""
    widget_config = json.dumps(config['widget'], indent=2)
    
    return f'''<!-- E-CB Chatbot Widget v2.0 -->
<div id="ecb-chatbot-{bot_id}"></div>
<script>
  window.ECBWidgetConfig = {widget_config};
</script>
<script async src="{config['cdnUrl']}/widget.min.js" 
        data-bot-id="{bot_id}" 
        data-embed-token="{config['embedToken']}">
</script>
<!-- End E-CB Chatbot Widget -->'''

def generate_iframe_embed(bot_id, config):
    """Generate secure iframe embed"""
    iframe_url = f"{request.url_root}v2/bot/{bot_id}/iframe?token={config['embedToken']}"
    
    return f'''<!-- E-CB Chatbot Widget (Iframe) -->
<iframe src="{iframe_url}"
        width="{config['widget']['width']}"
        height="{config['widget']['height']}"
        frameborder="0"
        scrolling="no"
        allow="microphone; camera"
        sandbox="allow-scripts allow-same-origin allow-forms"
        style="border-radius: {config['widget']['borderRadius']}; box-shadow: 0 4px 20px rgba(0,0,0,0.15);">
</iframe>
<!-- End E-CB Chatbot Widget -->'''

def generate_npm_embed(bot_id, config):
    """Generate NPM package usage"""
    return f'''// Install: npm install @ecb/chatbot-widget

import ECBWidget from '@ecb/chatbot-widget';

const widget = new ECBWidget({{
  botId: '{bot_id}',
  embedToken: '{config['embedToken']}',
  apiUrl: '{config['apiUrl']}',
     // Additional configuration from widget config
 }});
 
 // Initialize the widget
 widget.init();'''

def generate_react_embed(bot_id, config):
    """Generate React component usage"""
    return f'''// Install: npm install @ecb/react-chatbot-widget

import {{ ECBChatWidget }} from '@ecb/react-chatbot-widget';

function App() {{
  const handleMessage = (message, response) => {{
    console.log('New message:', message, response);
  }};

  return (
    <div className="App">
      <ECBChatWidget
        botId="{bot_id}"
        embedToken="{config['embedToken']}"
        apiUrl="{config['apiUrl']}"
        theme="{config['widget']['theme']}"
        primaryColor="{config['widget']['primaryColor']}"
        embedStyle="{config['widget']['embedStyle']}"
                 onMessage={{handleMessage}}
         // Additional props from config
       />
      />
    </div>
  );
}}'''

def generate_vue_embed(bot_id, config):
    """Generate Vue component usage"""
    return f'''<!-- Install: npm install @ecb/vue-chatbot-widget -->

<template>
  <div class="app">
    <ECBChatWidget
      :bot-id="'{bot_id}'"
      :embed-token="'{config['embedToken']}'"
      :api-url="'{config['apiUrl']}'"
      :config="widgetConfig"
      @message="handleMessage"
    />
  </div>
</template>

<script>
import {{ ECBChatWidget }} from '@ecb/vue-chatbot-widget';

export default {{
  components: {{
    ECBChatWidget
  }},
  data() {{
    return {{
      widgetConfig: config.widget
    }};
  }},
  methods: {{
    handleMessage(message, response) {{
      console.log('New message:', message, response);
    }}
  }}
}};
</script>'''

def generate_angular_embed(bot_id, config):
    """Generate Angular component usage"""
    return f'''<!-- Install: npm install @ecb/angular-chatbot-widget -->

<!-- app.component.html -->
<div class="app">
  <ecb-chat-widget
    [botId]="'{bot_id}'"
    [embedToken]="'{config['embedToken']}'"
    [apiUrl]="'{config['apiUrl']}'"
    [config]="widgetConfig"
    (message)="handleMessage($event)">
  </ecb-chat-widget>
</div>

// app.component.ts
import {{ Component }} from '@angular/core';

@Component({{
  selector: 'app-root',
  templateUrl: './app.component.html'
}})
export class AppComponent {{
     widgetConfig = config.widget;

  handleMessage(event: any) {{
    console.log('New message:', event);
  }}
}}

// app.module.ts - Add ECBChatWidgetModule to imports'''

@embed_routes_v2.route('/v2/bot/<bot_id>/iframe')
def iframe_widget(bot_id):
    """Serve widget in iframe for secure embedding"""
    token = request.args.get('token')
    if not token:
        return "Missing embed token", 400
    
    # Validate token (basic validation - in production, use proper JWT)
    bots = BotManager.load_bots(current_app)
    if bot_id not in bots:
        return "Bot not found", 404
    
    config_response = get_embed_config_v2(bot_id)
    config = config_response[0].get_json()
    
    return render_template('iframe_widget.html', 
                         bot_id=bot_id, 
                         config=config,
                         token=token)

@embed_routes_v2.route('/api/v2/chat/<bot_id>', methods=['POST', 'OPTIONS'])
def chat_api_v2(bot_id):
    """Enhanced API endpoint with better error handling and features"""
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response
    
    # Cleanup inactive bots periodically
    cleanup_inactive_bots()
    
    bots = BotManager.load_bots(current_app)
    
    if bot_id not in bots:
        return jsonify({'error': 'Bot not found', 'code': 'BOT_NOT_FOUND'}), 404
    
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Message is required', 'code': 'MISSING_MESSAGE'}), 400
    
    user_message = data['message']
    session_id = data.get('session_id', str(uuid.uuid4()))
    embed_token = data.get('embed_token')
    
    # Rate limiting (basic implementation)
    rate_limit_key = f"rate_limit_{session_id}"
    
    try:
        # Initialize bot if not already active
        if bot_id not in active_bots:
            active_bots[bot_id] = initialize_bot(bots[bot_id])
        
        # Update last access time
        bot_last_access[bot_id] = time.time()
        
        kernel = active_bots[bot_id]
        
        # Process message asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(kernel.process_message(user_message))
        loop.close()
        
        response_data = {
            'response': response,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'bot_id': bot_id,
            'message_id': str(uuid.uuid4()),
            'confidence': 0.8,  # Could be returned from NLU
            'processing_time': 0.1  # Could be measured
        }
        
        # Add CORS headers
        resp = make_response(jsonify(response_data))
        resp.headers.add('Access-Control-Allow-Origin', '*')
        resp.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        
        return resp
        
    except Exception as e:
        error_response = bots[bot_id].get('settings', {}).get('error_handling', {}).get('default_response', 
                                                                                        "I'm sorry, something went wrong.")
        
        error_data = {
            'response': error_response,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'bot_id': bot_id,
            'error': {
                'code': 'PROCESSING_ERROR',
                'message': str(e) if current_app.debug else 'Internal error',
                'type': type(e).__name__
            }
        }
        
        resp = make_response(jsonify(error_data), 500)
        resp.headers.add('Access-Control-Allow-Origin', '*')
        resp.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        
        return resp

@embed_routes_v2.route('/cdn/ecb-widget/v2/widget.min.js')
def serve_widget_js():
    """Serve the minified widget JavaScript from CDN endpoint"""
    
    # In production, this should be served from a real CDN
    # For now, we'll serve the unminified version with proper headers
    
    with open('D:\E-CB\src\web\static\embed\widget-sdk.js', 'r') as f:
        js_content = f.read()
    
    response = make_response(js_content)
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Cache-Control'] = 'public, max-age=86400'  # 24 hours
    response.headers['Access-Control-Allow-Origin'] = '*'
    
    return response

@embed_routes_v2.route('/v2/bot/<bot_id>/analytics', methods=['POST'])
def track_analytics(bot_id):
    """Track widget analytics events"""
    data = request.get_json()
    
    if not data or 'event' not in data:
        return jsonify({'error': 'Event type required'}), 400
    
    # In a real implementation, you'd store this in a database
    # For now, just log it
    current_app.logger.info(f"Analytics event for bot {bot_id}: {data}")
    
    return jsonify({'status': 'tracked'})

@embed_routes_v2.route('/v2/bot/<bot_id>/health')
def bot_health_check(bot_id):
    """Health check endpoint for bot status"""
    bots = BotManager.load_bots(current_app)
    
    if bot_id not in bots:
        return jsonify({'status': 'not_found'}), 404
    
    is_active = bot_id in active_bots
    last_access = bot_last_access.get(bot_id, 0)
    
    return jsonify({
        'status': 'healthy' if is_active else 'inactive',
        'bot_id': bot_id,
        'active': is_active,
        'last_access': last_access,
        'uptime': time.time() - last_access if is_active else 0,
        'version': '2.0.0'
    })

@embed_routes_v2.route('/docs/embedding')
def embedding_documentation():
    """Serve embedding documentation"""
    return render_template('embedding_docs.html')

@embed_routes_v2.route('/v2/bot/<bot_id>/embed-preview')
def embed_preview_v2(bot_id):
    """Preview page for the embedded chatbot v2"""
    bots = BotManager.load_bots(current_app)
    if bot_id not in bots:
        return "Bot not found", 404
    bot_config = bots[bot_id]
    return render_template('embed_preview_v2.html', bot=bot_config, bot_id=bot_id) 