import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    BOTS_DIRECTORY = os.environ.get('BOTS_DIRECTORY') or 'bots'
    
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    BASE_URL = 'http://127.0.0.1:5000'
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    BASE_URL = os.environ.get('BASE_URL') or 'https://your-domain.com'
    
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    BASE_URL = 'http://localhost:5000'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 