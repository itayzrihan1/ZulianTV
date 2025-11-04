"""
Configuration management for ZulianTV Bot
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ALLOWED_USERS = [int(user_id.strip()) for user_id in os.getenv('ALLOWED_USERS', '').split(',') if user_id.strip()]

# Sonarr Configuration
SONARR_URL = os.getenv('SONARR_URL', 'http://sonarr:8989')
SONARR_API_KEY = os.getenv('SONARR_API_KEY')

# Radarr Configuration
RADARR_URL = os.getenv('RADARR_URL', 'http://radarr:7878')
RADARR_API_KEY = os.getenv('RADARR_API_KEY')

# Validate required configuration
def validate_config():
    """Validate that all required configuration is present"""
    errors = []

    if not TELEGRAM_BOT_TOKEN:
        errors.append("TELEGRAM_BOT_TOKEN is not set")

    if not ALLOWED_USERS:
        errors.append("ALLOWED_USERS is not set")

    if not SONARR_API_KEY:
        errors.append("SONARR_API_KEY is not set")

    if not RADARR_API_KEY:
        errors.append("RADARR_API_KEY is not set")

    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")
