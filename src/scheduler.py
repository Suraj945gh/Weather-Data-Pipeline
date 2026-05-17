import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from config import FETCH_INTERVAL_MINUTES
from src.ingester import fetch_weather
from src.processor import check_conditions
from src.alerter import send_alert
from src.database import save_reading, save_alert

logger = logging.getLogger(__name__)

def run_pipeline_job():
    """Main pipeline job: fetches data, evaluates it, alerts, and saves results."""
    logger.info("Job started: Running weather data pipeline cycle.")
    
    reading = fetch_weather()
    if not reading:
        logger.warning("Job skipped: No weather data fetched.")
        return
        
    save_reading(reading)
    
    alerts = check_conditions(reading)
    
    for alert in alerts:
        alert_result = send_alert(alert)
        # Combine alert data with webhook delivery result
        full_alert_record = {**alert, **alert_result}
        
        # Ensure triggered_at is set for database
        if "triggered_at" not in full_alert_record:
            full_alert_record["triggered_at"] = datetime.utcnow().isoformat() + "Z"
            
        save_alert(full_alert_record)
        
    logger.info(f"Job summary: Temp {reading['temperature_c']}C | Alerts Triggered: {len(alerts)}")

def start_scheduler():
    """Initializes and starts the APScheduler to run the pipeline job periodically."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_pipeline_job, 'interval', minutes=FETCH_INTERVAL_MINUTES)
    scheduler.start()
    logger.info(f"Scheduler started with interval: {FETCH_INTERVAL_MINUTES} minutes.")
    return scheduler
