"""
Configuration file for Stock Prediction Web App
COMPLETE VERSION - ALL ATTRIBUTES DEFINED
"""

import os


class Config:
    """Application configuration"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-12345'
    DEBUG = True
    TESTING = False
    
    # Application settings
    APP_NAME = "Stock Price Predictor"
    VERSION = "1.0.0"
    
    # DEMO MODE - Set to True if yfinance is not working
    DEMO_MODE = False  # Set to True to use sample data
    
    # File paths
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    MODEL_DIR = os.path.join(BASE_DIR, 'models', 'saved_models')
    WATCHLIST_FILE = os.path.join(DATA_DIR, 'watchlist.json')
    
    # Model settings - LSTM Configuration
    SEQUENCE_LENGTH = 60  # Number of days to look back
    LSTM_UNITS = [50, 50, 25]  # Units in each LSTM layer
    DROPOUT_RATE = 0.2  # Dropout rate for regularization
    EPOCHS = 50  # Training epochs (not used when loading pre-trained)
    BATCH_SIZE = 32  # Batch size for training
    
    # Data settings
    TRAIN_SIZE = 0.8  # 80% train, 20% test
    PREDICTION_DAYS = 30  # Number of days to predict into future
    MIN_DATA_ROWS = 100  # Minimum rows required
    
    # API settings
    MAX_RETRIES = 3  # Number of retries for API calls
    REQUEST_TIMEOUT = 30  # Timeout in seconds
    RETRY_DELAY = 2  # Delay between retries in seconds
    
    # Cache settings
    CACHE_TIMEOUT = 300  # 5 minutes cache
    ENABLE_CACHE = False  # Set to True for production
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_TO_FILE = False
    LOG_FILE = os.path.join(BASE_DIR, 'app.log')
    
    # Security
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Rate limiting (for production)
    RATE_LIMIT_ENABLED = False
    RATE_LIMIT_PER_MINUTE = 60
    
    @staticmethod
    def init_app(app):
        """Initialize application"""
        # Create necessary directories
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        os.makedirs(Config.MODEL_DIR, exist_ok=True)
        
        # Create watchlist file if it doesn't exist
        if not os.path.exists(Config.WATCHLIST_FILE):
            import json
            with open(Config.WATCHLIST_FILE, 'w') as f:
                json.dump([], f)
        
        print(f"✓ Config initialized")
        print(f"  BASE_DIR: {Config.BASE_DIR}")
        print(f"  DATA_DIR: {Config.DATA_DIR}")
        print(f"  MODEL_DIR: {Config.MODEL_DIR}")
        print(f"  SEQUENCE_LENGTH: {Config.SEQUENCE_LENGTH}")
        print(f"  DEMO_MODE: {Config.DEMO_MODE}")


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    RATE_LIMIT_ENABLED = True
    ENABLE_CACHE = True


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    DEMO_MODE = True


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


# Quick test function
def test_config():
    """Test if config is working"""
    print("\n" + "="*60)
    print("TESTING CONFIG")
    print("="*60)
    
    print(f"\nSEQUENCE_LENGTH: {Config.SEQUENCE_LENGTH}")
    print(f"LSTM_UNITS: {Config.LSTM_UNITS}")
    print(f"DROPOUT_RATE: {Config.DROPOUT_RATE}")
    print(f"TRAIN_SIZE: {Config.TRAIN_SIZE}")
    print(f"PREDICTION_DAYS: {Config.PREDICTION_DAYS}")
    print(f"MODEL_DIR: {Config.MODEL_DIR}")
    print(f"DEMO_MODE: {Config.DEMO_MODE}")
    
    print("\n✓ Config is working properly!")
    
    return True


if __name__ == "__main__":
    test_config()