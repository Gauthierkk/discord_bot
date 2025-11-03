"""
Configuration module for Discord bot
Handles environment variables and constants
"""

import logging
import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Bot configuration
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_TOKEN not found in environment variables")

# Bot settings
COMMAND_PREFIX = "!"
MAX_MESSAGES_FOR_AI = 200
MAX_DAYS_LOOKBACK = 7
MAX_HOURS_LOOKBACK = 168  # 7 days in hours

# AI settings
AI_TEXT_MODEL = "gpt-oss:20b-cloud"
AI_VISION_MODEL = "llava"  # Vision model for image analysis
