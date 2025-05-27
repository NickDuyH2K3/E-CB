from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app, flash
import os
import sys
import json

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from .base_routes import BotManager

config_routes = Blueprint('config_routes', __name__)

@config_routes.route('/bot/<bot_id>/settings')
def bot_settings(bot_id):
    """Advanced settings page for a chatbot"""
    bots = BotManager.load_bots(current_app)
    
    if bot_id not in bots:
        return redirect(url_for('base_routes.index'))
    
    bot_config = bots[bot_id]
    
    # Ensure all configuration sections exist
    if 'settings' not in bot_config:
        bot_config['settings'] = {
            'nlu_type': 'simple',
            'debug': False,
            'error_handling': {
                'default_response': "I'm sorry, I didn't understand that.",
                'custom_responses': {}
            },
            'appearance': {
                'theme': 'default',
                'primary_color': '#007bff',
                'bot_name_display': bot_config.get('name', 'Chatbot'),
                'welcome_message': 'Hello! How can I help you today?'
            },
            'integration': {
                'enabled': True,
                'domains': [],
                'embed_style': 'popup'
            }
        }
        BotManager.save_bot(current_app, bot_id, bot_config)
    
    return render_template('bot_settings.html', bot=bot_config, bot_id=bot_id)

@config_routes.route('/bot/<bot_id>/settings/nlu', methods=['POST'])
def update_nlu_settings(bot_id):
    """Update NLU settings for a bot"""
    bots = BotManager.load_bots(current_app)
    
    if bot_id not in bots:
        return jsonify({'error': 'Bot not found'}), 404
    
    nlu_type = request.json.get('nlu_type', 'simple')
    
    if 'settings' not in bots[bot_id]:
        bots[bot_id]['settings'] = {}
    
    bots[bot_id]['settings']['nlu_type'] = nlu_type
    
    BotManager.save_bot(current_app, bot_id, bots[bot_id])
    
    return jsonify({'success': True, 'message': 'NLU settings updated'})

@config_routes.route('/bot/<bot_id>/settings/appearance', methods=['POST'])
def update_appearance_settings(bot_id):
    """Update appearance settings for a bot"""
    bots = BotManager.load_bots(current_app)
    
    if bot_id not in bots:
        return jsonify({'error': 'Bot not found'}), 404
    
    appearance_data = request.json
    
    if 'settings' not in bots[bot_id]:
        bots[bot_id]['settings'] = {}
    if 'appearance' not in bots[bot_id]['settings']:
        bots[bot_id]['settings']['appearance'] = {}
    
    # Update appearance settings
    bots[bot_id]['settings']['appearance'].update(appearance_data)
    
    BotManager.save_bot(current_app, bot_id, bots[bot_id])
    
    return jsonify({'success': True, 'message': 'Appearance settings updated'})

@config_routes.route('/bot/<bot_id>/settings/error-handling', methods=['POST'])
def update_error_handling(bot_id):
    """Update error handling settings for a bot"""
    bots = BotManager.load_bots(current_app)
    
    if bot_id not in bots:
        return jsonify({'error': 'Bot not found'}), 404
    
    error_data = request.json
    
    if 'settings' not in bots[bot_id]:
        bots[bot_id]['settings'] = {}
    if 'error_handling' not in bots[bot_id]['settings']:
        bots[bot_id]['settings']['error_handling'] = {}
    
    bots[bot_id]['settings']['error_handling'].update(error_data)
    
    BotManager.save_bot(current_app, bot_id, bots[bot_id])
    
    return jsonify({'success': True, 'message': 'Error handling settings updated'})

@config_routes.route('/bot/<bot_id>/export-config')
def export_config(bot_id):
    """Export bot configuration as JSON"""
    bots = BotManager.load_bots(current_app)
    
    if bot_id not in bots:
        return jsonify({'error': 'Bot not found'}), 404
    
    return jsonify(bots[bot_id]) 