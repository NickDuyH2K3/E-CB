from flask import Flask
import os

# Import route blueprints
from routes.base_routes import base_routes
from routes.bot_routes import bot_routes
from routes.chat_routes import chat_routes
from routes.config_routes import config_routes
from routes.embed_routes import embed_routes
from routes.embed_routes_v2 import embed_routes_v2

def create_app():
    """Application factory function"""
    app = Flask(__name__)
    
    app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key_here')
    
    # Set bots directory
    app.config['BOTS_DIRECTORY'] = os.path.join(app.root_path, 'bots')
    
    # Ensure bots directory exists
    os.makedirs(app.config['BOTS_DIRECTORY'], exist_ok=True)
    
    # Register blueprints
    app.register_blueprint(base_routes)
    app.register_blueprint(bot_routes)
    app.register_blueprint(chat_routes)
    app.register_blueprint(config_routes)
    app.register_blueprint(embed_routes)
    app.register_blueprint(embed_routes_v2)
    
    return app

# Application instance
app = create_app()

if __name__ == '__main__':
    # Development server
    app.run(debug=True)