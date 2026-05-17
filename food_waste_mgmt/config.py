# ============================================================
# config.py - Application Configuration
# ============================================================

import os
from datetime import timedelta

class Config:
    # --- Security ---
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-super-secret-key-change-in-production')
    
    # --- Database ---
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = 'shafeeq'
    MYSQL_DB = os.environ.get('MYSQL_DB', 'food_waste_mgmt')
    MYSQL_CURSORCLASS = 'DictCursor'

    # --- Session ---
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    # --- Google Maps ---
    GOOGLE_MAPS_API_KEY = ''  # Not needed - using free OpenStreetMap

    # --- Email (optional) ---
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@foodwaste.com')

    # --- Upload ---
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload

    # --- Food Safety ---
    MAX_FOOD_EXPIRY_HOURS = 24  # Warn if food expires within 2 hours
    AUTO_EXPIRE_CHECK_INTERVAL = 300  # seconds


class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
