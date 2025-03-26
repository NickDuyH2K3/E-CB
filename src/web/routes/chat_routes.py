import os
import sys

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)


from flask import Blueprint, request, jsonify, current_app
import json

from routes.base_routes import BotManager

# Import your chatbot framework components
from core.kernel import ChatbotKernel
from pipeline.input_handler import InputHandler
from pipeline.nlu import SimpleNLU
from pipeline.response_generator import ResponseGenerator

chat_routes = Blueprint('chat_routes', __name__)

@chat_routes.route('/api/bot/<bot_id>/chat', methods=['POST'])
def chat_with_bot(bot_id):
    """API endpoint for chatting with a bot"""
    # Load existing bots
    bots = BotManager.load_bots(current_app)
    
    if bot_id not in bots:
        return jsonify({"error": "Bot not found"}), 404
    
    user_message = request.json.get('message', '')
    
    # Initialize chatbot components
    kernel = ChatbotKernel()
    input_handler = InputHandler()
    
    # Create NLU with bot's intents
    nlu = SimpleNLU()
    nlu.patterns = bots[bot_id]['intents']
    
    # Create response generator with bot's responses
    response_gen = ResponseGenerator()
    response_gen.templates = bots[bot_id]['responses']
    
    # Register components
    kernel.register_component('input_handler', input_handler)
    kernel.register_component('nlu', nlu)
    kernel.register_component('response_generator', response_gen)
    
    # Process message
    response = kernel.process_message(user_message)
    
    return jsonify({"response": response})