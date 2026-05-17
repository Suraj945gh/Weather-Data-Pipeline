import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

WEATHER_LAT = float(os.getenv("WEATHER_LAT", 27.61))
WEATHER_LON = float(os.getenv("WEATHER_LON", 75.15))
WEATHER_LOCATION_NAME = os.getenv("WEATHER_LOCATION_NAME", "Sikar, Rajasthan")
FETCH_INTERVAL_MINUTES = int(os.getenv("FETCH_INTERVAL_MINUTES", 5))
TEMP_ALERT_THRESHOLD = float(os.getenv("TEMP_ALERT_THRESHOLD", 38.0))
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
DB_PATH = os.getenv("DB_PATH", "data/pipeline.db")
LOG_PATH = os.getenv("LOG_PATH", "logs/pipeline.log")
API_PORT = int(os.getenv("API_PORT", 8080))
