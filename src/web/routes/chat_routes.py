import os
import sys

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)


from flask import Blueprint, request, jsonify, current_app
import json

from .base_routes import BotManager

# Import your chatbot framework components
from core.kernel import ChatbotKernel
from core.errors import ChatbotError, ErrorHandler
from pipeline.input_handler import InputHandler
from pipeline.nlu import SimpleNLU, SpacyNLU
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
    
    # Initialize chatbot kernel with appropriate error handling
    kernel = ChatbotKernel()
    
    # Configure error handler with custom responses
    error_handler = ErrorHandler()
    error_handler.set_error_response('IntentError', "I don't understand what you mean. Can you rephrase that?")
    error_handler.set_error_response('ComponentNotFoundError', "Sorry, I'm not configured correctly.")
    kernel.error_handler = error_handler
    
    # Create NLU based on bot type (simple by default)
    bot_type = bots[bot_id].get('type', 'simple')
    if bot_type == 'spacy':
        nlu = SpacyNLU()
        # Add custom intents if defined
        if 'custom_intents' in bots[bot_id]:
            for intent_name, intent_data in bots[bot_id]['custom_intents'].items():
                nlu.add_custom_intent(
                    intent_name, 
                    keywords=intent_data.get('keywords', []),
                    patterns=intent_data.get('patterns', [])
                )
    else:
        nlu = SimpleNLU()
        nlu.patterns = bots[bot_id]['intents']
    
    # Create response generator with bot's responses
    response_gen = ResponseGenerator()
    response_gen.templates = bots[bot_id]['responses']
    
    # Register components
    kernel.register_component('input_handler', InputHandler())
    kernel.register_component('nlu', nlu)
    kernel.register_component('response_generator', response_gen)
    
    try:
        # Process message
        response = kernel.process_message(user_message)
        return jsonify({"response": response})
        
    except ChatbotError as e:
        # Use error handler for user-friendly error messages
        error_response = kernel.error_handler.handle_error(e)
        return jsonify({
            "response": error_response, 
            "error": True
        })
        
    except Exception as e:
        # Generic error handler for unexpected errors
        return jsonify({
            "response": "I'm experiencing technical difficulties at the moment.", 
            "error": True
        }), 500