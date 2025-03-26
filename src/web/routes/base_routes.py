from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app
import json

import os
import sys

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

base_routes = Blueprint('base_routes', __name__)

class BotManager:
    """
    Centralized bot management class
    """
    @staticmethod
    def get_bots_dir(app):
        """Get the directory for storing bot configurations"""
        bots_dir = os.path.join(app.root_path, 'bots')
        if not os.path.exists(bots_dir):
            os.makedirs(bots_dir)
        return bots_dir

    @classmethod
    def load_bots(cls, app):
        """Load existing bots from JSON files"""
        bots = {}
        bots_dir = cls.get_bots_dir(app)
        
        for filename in os.listdir(bots_dir):
            if filename.endswith('.json'):
                bot_id = filename[:-5]  # Remove .json extension
                with open(os.path.join(bots_dir, filename), 'r') as f:
                    bots[bot_id] = json.load(f)
        
        return bots

    @classmethod
    def save_bot(cls, app, bot_id, bot_config):
        """Save bot configuration to a JSON file"""
        bots_dir = cls.get_bots_dir(app)
        filepath = os.path.join(bots_dir, f"{bot_id}.json")
        
        with open(filepath, 'w') as f:
            json.dump(bot_config, f, indent=4)

@base_routes.route('/')
def index():
    """Main dashboard showing all bots"""
    bots = BotManager.load_bots(current_app)
    return render_template('index.html', bots=bots)

@base_routes.route('/create', methods=['GET', 'POST'])
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
        
        # Load existing bots
        bots = BotManager.load_bots(current_app)
        
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
        BotManager.save_bot(current_app, bot_id, bot_config)
        
        return redirect(url_for('bot_routes.bot_dashboard', bot_id=bot_id))
    
    return render_template('create.html')