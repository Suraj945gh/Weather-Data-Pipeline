import httpx
import logging
from datetime import datetime
from config import WEBHOOK_URL, WEATHER_LOCATION_NAME

logger = logging.getLogger(__name__)

def send_alert(alert: dict):
    """Sends an alert payload via POST request to the configured WEBHOOK_URL."""
    if not WEBHOOK_URL:
        logger.warning("WEBHOOK_URL is not configured. Skipping alert delivery.")
        return {"webhook_success": False, "webhook_status_code": 0}
        
    payload = {
        "alert_type": alert.get("alert_type"),
        "message": alert.get("message"),
        "temperature_c": alert.get("temperature_c"),
        "location": WEATHER_LOCATION_NAME,
        "triggered_at": datetime.utcnow().isoformat() + "Z"
    }
    
    try:
        response = httpx.post(WEBHOOK_URL, json=payload, timeout=10.0)
        success = response.status_code >= 200 and response.status_code < 300
        if success:
            logger.info(f"Webhook delivered successfully: {response.status_code}")
        else:
            logger.error(f"Webhook delivery failed with status: {response.status_code}")
            
        return {"webhook_success": success, "webhook_status_code": response.status_code}
        
    except Exception as e:
        logger.error(f"Error sending webhook: {e}")
        return {"webhook_success": False, "webhook_status_code": 0}
