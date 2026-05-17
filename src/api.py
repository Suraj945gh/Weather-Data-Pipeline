from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
import datetime
from config import TEMP_ALERT_THRESHOLD, WEATHER_LOCATION_NAME, FETCH_INTERVAL_MINUTES
from src.database import get_recent_readings, get_recent_alerts, get_db_status
from src.scheduler import run_pipeline_job

app = FastAPI(title="Weather Pipeline API")
templates = Jinja2Templates(directory="templates")

# We use app.state to hold our global status flags
app.state.scheduler_running = False

def get_alert_count_24h():
    """Calculates the number of alerts triggered in the last 24 hours."""
    alerts = get_recent_alerts(limit=1000) # Simple approach for small scale
    now = datetime.datetime.utcnow()
    count = 0
    for a in alerts:
        triggered_at_str = a.get("triggered_at")
        if triggered_at_str:
            try:
                # Handle isoformat
                dt = datetime.datetime.fromisoformat(triggered_at_str.replace("Z", "+00:00").split("+")[0])
                if (now - dt).total_seconds() <= 86400:
                    count += 1
            except Exception:
                pass
    return count

@app.get("/")
def read_root(request: Request):
    """Renders the main dashboard HTML."""
    readings = get_recent_readings(limit=20)
    latest = readings[0] if readings else None
    alerts = get_recent_alerts(limit=10)
    
    last_fetch_time = latest.get("fetched_at") if latest else "Never"
    
    # Format the timestamps for better display
    if last_fetch_time != "Never":
        try:
            dt = datetime.datetime.fromisoformat(last_fetch_time.replace("Z", "+00:00").split("+")[0])
            last_fetch_time = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        except:
            pass

    return templates.TemplateResponse(request=request, name="dashboard.html", context={
        "request": request,
        "latest": latest,
        "readings": readings,
        "alerts": alerts,
        "threshold": TEMP_ALERT_THRESHOLD,
        "location": WEATHER_LOCATION_NAME,
        "scheduler_running": app.state.scheduler_running,
        "db_connected": get_db_status(),
        "last_fetch_time": last_fetch_time,
        "alert_count_24h": get_alert_count_24h(),
        "fetch_interval": FETCH_INTERVAL_MINUTES
    })

@app.get("/status")
def get_status():
    """Returns the dashboard data as JSON."""
    readings = get_recent_readings(limit=20)
    latest = readings[0] if readings else None
    return {
        "latest": latest,
        "threshold": TEMP_ALERT_THRESHOLD,
        "location": WEATHER_LOCATION_NAME,
        "scheduler_running": app.state.scheduler_running,
        "db_connected": get_db_status(),
        "last_fetch_time": latest.get("fetched_at") if latest else "Never",
        "alert_count_24h": get_alert_count_24h()
    }

@app.get("/readings")
def get_readings_endpoint():
    """Returns the last 20 readings as JSON."""
    return get_recent_readings(limit=20)

@app.get("/alerts")
def get_alerts_endpoint():
    """Returns the last 10 alerts as JSON."""
    return get_recent_alerts(limit=10)

@app.post("/trigger-now")
def trigger_now():
    """Manually runs the pipeline job immediately."""
    run_pipeline_job()
    return {"message": "Pipeline triggered manually", "timestamp": datetime.datetime.utcnow().isoformat() + "Z"}

@app.get("/health")
def health_check():
    """System health check endpoint."""
    return {
        "status": "ok",
        "scheduler_active": app.state.scheduler_running,
        "db_connected": get_db_status(),
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }
