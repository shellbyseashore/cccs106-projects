"""Configuration management for the weather application."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Get the directory where this config file is located
BASE_DIR = Path(__file__).parent.resolve()
ENV_FILE = BASE_DIR / ".env"

# Load environment variables from .env file
# Try loading from explicit path first, then default location
if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE)
else:
    load_dotenv()  # Fallback to default location

# API Configuration
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()
OPENWEATHER_BASE_URL = os.getenv(
    "OPENWEATHER_BASE_URL", 
    "https://api.openweathermap.org/data/2.5/weather"
)
FORECAST_BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"

# Application Configuration
CACHE_DIR = Path("cache")
CACHE_EXPIRY_MINUTES = 30
HISTORY_FILE = Path("search_history.json")
MAX_HISTORY_ITEMS = 10

# Validate API key
if not OPENWEATHER_API_KEY:
    print("WARNING: OPENWEATHER_API_KEY not found in environment variables.")
    print("Please create a .env file with your OpenWeatherMap API key.")
    print("Get a free key at: https://openweathermap.org/api")
else:
    print(f"API key loaded successfully (length: {len(OPENWEATHER_API_KEY)})")

