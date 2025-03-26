from flask import Flask
import os

# Import route blueprints
from routes.base_routes import base_routes
from routes.bot_routes import bot_routes
from routes.chat_routes import chat_routes

def create_app():
    """Application factory function"""
    app = Flask(__name__)
    
    # Configuration
    app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key_here')
    app.config['BOTS_DIRECTORY'] = os.path.join(app.root_path, 'bots')
    
    # Ensure bots directory exists
    os.makedirs(app.config['BOTS_DIRECTORY'], exist_ok=True)
    
    # Register blueprints
    app.register_blueprint(base_routes)
    app.register_blueprint(bot_routes)
    app.register_blueprint(chat_routes)
    
    return app

# Application instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)