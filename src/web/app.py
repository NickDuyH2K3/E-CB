from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import json
import sys

# Import your chatbot framework components
# Adjust these imports based on your actual project structure
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from core.kernel import ChatbotKernel
from pipeline.input_handler import InputHandler
from pipeline.nlu import SimpleNLU
from pipeline.response_generator import ResponseGenerator

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # For session management

# Store bot instances
bots = {}

# Load existing bots if any
def load_bots():
    bots_dir = os.path.join(app.root_path, 'bots')
    if not os.path.exists(bots_dir):
        os.makedirs(bots_dir)
    
    for filename in os.listdir(bots_dir):
        if filename.endswith('.json'):
            bot_id = filename[:-5]  # Remove .json extension
            with open(os.path.join(bots_dir, filename), 'r') as f:
                bots[bot_id] = json.load(f)

# Dashboard route
@app.route('/')
def index():
    """Main dashboard showing all bots"""
    return render_template('index.html', bots=bots)

# Create bot route
@app.route('/create', methods=['GET', 'POST'])
def create_bot():
    """Create a new chatbot"""
    if request.method == 'POST':
        bot_name = request.form.get('name')
        bot_description = request.form.get('description')
        
        # Simple validation
        if not bot_name:
            return render_template('create.html', error="Bot name is required")
        
        # Create a unique ID for the bot
        bot_id = bot_name.lower().replace(' ', '_')
        
        # Check if bot already exists
        if bot_id in bots:
            return render_template('create.html', error="A bot with this name already exists")
        
        # Create bot configuration
        bot_config = {
            'name': bot_name,
            'description': bot_description,
            'intents': {
                'greeting': ['hello', 'hi', 'hey'],
                'farewell': ['bye', 'goodbye', 'see you']
            },
            'responses': {
                'greeting': ['Hello!', 'Hi there!'],
                'farewell': ['Goodbye!', 'See you later!'],
                'unknown': ['I don\'t understand.', 'Could you rephrase that?']
            }
        }
        
        # Save bot configuration
        bots[bot_id] = bot_config
        bots_dir = os.path.join(app.root_path, 'bots')
        if not os.path.exists(bots_dir):
            os.makedirs(bots_dir)
        with open(os.path.join(bots_dir, f"{bot_id}.json"), 'w') as f:
            json.dump(bot_config, f, indent=4)
        
        return redirect(url_for('bot_dashboard', bot_id=bot_id))
    
    return render_template('create.html')

# Bot dashboard
@app.route('/bot/<bot_id>')
def bot_dashboard(bot_id):
    """Dashboard for a specific bot"""
    if bot_id not in bots:
        return redirect(url_for('index'))
    
    return render_template('bot_dashboard.html', bot=bots[bot_id], bot_id=bot_id)

# Edit intents
@app.route('/bot/<bot_id>/intents', methods=['GET', 'POST'])
def edit_intents(bot_id):
    """Edit intents for a specific bot"""
    if bot_id not in bots:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Handle form submission to update intents
        intent_name = request.form.get('intent_name')
        phrases = request.form.get('phrases').split('\n')
        phrases = [phrase.strip() for phrase in phrases if phrase.strip()]
        
        # Update the bot's intents
        bots[bot_id]['intents'][intent_name] = phrases
        
        # Save updated configuration
        with open(os.path.join(app.root_path, 'bots', f"{bot_id}.json"), 'w') as f:
            json.dump(bots[bot_id], f, indent=4)
        
        return redirect(url_for('edit_intents', bot_id=bot_id))
    
    return render_template('edit_intents.html', bot=bots[bot_id], bot_id=bot_id)

# Chat interface
@app.route('/bot/<bot_id>/chat')
def chat_interface(bot_id):
    """Chat interface for testing a bot"""
    if bot_id not in bots:
        return redirect(url_for('index'))
    
    return render_template('chat.html', bot=bots[bot_id], bot_id=bot_id)

# API endpoint for chatting
@app.route('/api/bot/<bot_id>/chat', methods=['POST'])
def chat_with_bot(bot_id):
    """API endpoint for chatting with a bot"""
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

# Main entry point
if __name__ == '__main__':
    load_bots()  # Load existing bots on startup
    app.run(debug=True)