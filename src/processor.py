import logging
from config import TEMP_ALERT_THRESHOLD
from src.database import get_recent_readings

logger = logging.getLogger(__name__)

def check_conditions(reading: dict) -> list:
    """Evaluates the current reading against alert conditions and returns a list of triggered alerts."""
    alerts = []
    
    if not reading:
        return alerts
        
    temp_c = reading.get("temperature_c")
    location = reading.get("location")
    
    if temp_c is None:
        return alerts

    # CHECK 1: HEAT_ALERT
    if temp_c >= TEMP_ALERT_THRESHOLD:
        alerts.append({
            "alert_type": "HEAT_ALERT",
            "message": f"Temperature in {location} is {temp_c}C, above threshold of {TEMP_ALERT_THRESHOLD}C.",
            "temperature_c": temp_c
        })
        logger.info(f"HEAT_ALERT triggered for {location} at {temp_c}C")

    # CHECK 2: RAPID_RISE
    # Get the last reading from the database
    recent = get_recent_readings(limit=1)
    if recent:
        last_reading = recent[0]
        last_temp = last_reading.get("temperature_c")
        
        if last_temp is not None:
            diff = temp_c - last_temp
            if diff >= 3.0:
                alerts.append({
                    "alert_type": "RAPID_RISE",
                    "message": f"Temperature rose by {diff:.1f}C in one cycle in {location}.",
                    "temperature_c": temp_c
                })
                logger.info(f"RAPID_RISE triggered for {location}. Rise: {diff:.1f}C")
                
    return alerts
