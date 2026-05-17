import httpx
import logging
from datetime import datetime
from config import WEATHER_LAT, WEATHER_LON, WEATHER_LOCATION_NAME

logger = logging.getLogger(__name__)

def fetch_weather():
    """Fetches real-time weather data from Open-Meteo API and returns a parsed dictionary."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={WEATHER_LAT}&longitude={WEATHER_LON}&current=temperature_2m,apparent_temperature,wind_speed_10m,weather_code&timezone=Asia/Kolkata"
    
    try:
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        
        current = data.get("current", {})
        
        reading = {
            "temperature_c": current.get("temperature_2m"),
            "apparent_temperature_c": current.get("apparent_temperature"),
            "wind_speed_kmh": current.get("wind_speed_10m"),
            "weather_code": current.get("weather_code"),
            "fetched_at": datetime.utcnow().isoformat() + "Z",
            "location": WEATHER_LOCATION_NAME
        }
        
        logger.info(f"Successfully fetched weather for {WEATHER_LOCATION_NAME}: {reading['temperature_c']}C")
        return reading
        
    except Exception as e:
        logger.error(f"Failed to fetch weather data: {e}")
        return None
