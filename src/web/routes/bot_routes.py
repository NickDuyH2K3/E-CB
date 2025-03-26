from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app, flash
import os
import sys
import json

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from routes.base_routes import BotManager

bot_routes = Blueprint('bot_routes', __name__)

@bot_routes.route('/bot/<bot_id>')
def bot_dashboard(bot_id):
    """Dashboard for a specific bot"""
    # Load existing bots
    bots = BotManager.load_bots(current_app)
    
    if bot_id not in bots:
        return redirect(url_for('base_routes.index'))
    
    return render_template('bot_dashboard.html', bot=bots[bot_id], bot_id=bot_id)

@bot_routes.route('/bot/<bot_id>/intents', methods=['GET', 'POST'])
def edit_intents(bot_id):
    """Edit intents for a specific bot"""
    # Load existing bots
    bots = BotManager.load_bots(current_app)
    
    if bot_id not in bots:
        return redirect(url_for('base_routes.index'))
    
    if request.method == 'POST':
        # Handle form submission to update intents
        intent_name = request.form.get('intent_name')
        phrases = request.form.get('phrases').split('\n')
        phrases = [phrase.strip() for phrase in phrases if phrase.strip()]
        
        # Update the bot's intents
        bots[bot_id]['intents'][intent_name] = phrases
        
        # Save updated configuration
        BotManager.save_bot(current_app, bot_id, bots[bot_id])
        
        return redirect(url_for('bot_routes.edit_intents', bot_id=bot_id))
    
    return render_template('edit_intents.html', bot=bots[bot_id], bot_id=bot_id)

@bot_routes.route('/bot/<bot_id>/responses', methods=['GET', 'POST'])
def edit_responses(bot_id):
    """Edit responses for a specific bot"""
    # Load existing bots
    bots = BotManager.load_bots(current_app)
    
    if bot_id not in bots:
        return redirect(url_for('base_routes.index'))
    
    if request.method == 'POST':
        # Handle form submission to update responses
        intent_name = request.form.get('intent_name')
        responses = request.form.get('responses').split('\n')
        responses = [response.strip() for response in responses if response.strip()]
        
        # Update the bot's responses
        bots[bot_id]['responses'][intent_name] = responses
        
        # Save updated configuration
        BotManager.save_bot(current_app, bot_id, bots[bot_id])
        
        flash(f'Responses for "{intent_name}" updated successfully!', 'success')
        return redirect(url_for('bot_routes.edit_responses', bot_id=bot_id))
    
    return render_template('edit_responses.html', bot=bots[bot_id], bot_id=bot_id)

@bot_routes.route('/bot/<bot_id>/chat')
def chat_interface(bot_id):
    """Chat interface for testing a bot"""
    # Load existing bots
    bots = BotManager.load_bots(current_app)
    
    if bot_id not in bots:
        return redirect(url_for('base_routes.index'))
    
    return render_template('chat.html', bot=bots[bot_id], bot_id=bot_id)