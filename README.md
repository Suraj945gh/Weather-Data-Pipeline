# Event-Driven Weather Data Pipeline

### What This Does
This system is an event-driven data pipeline that periodically fetches real-time weather data and checks it against defined thresholds. If conditions like extreme heat or rapid temperature rise are met, it triggers automated webhook alerts and logs all events to a database.

### System Architecture
```text
[Open-Meteo API] ---(fetch every 5m)---> [Ingester]
                                              |
                                              v
                                        [Processor] ---(evaluates thresholds)---> [Alerter] --(POST)--> [Webhook]
                                              |                                       |
                                              +-----------------v---------------------+
                                                          [SQLite Database]
                                                                ^
                                                                |
                                        [FastAPI Server] -------+
                                              |
                                              v
                                     [Web Dashboard (Port 8080)]
```

### Quick Start
Step 1: Clone repo
Step 2: Go to [webhook.site](https://webhook.site/), copy your unique URL
Step 3: `cp .env.example .env` and paste URL into `WEBHOOK_URL`
Step 4: `docker-compose up --build`
Step 5: Open `http://localhost:8080`

### Force an Alert (for testing)
Set `TEMP_ALERT_THRESHOLD=15.0` in `.env`, restart the container (`docker-compose restart`), and the alert fires immediately on the next cycle.
Check webhook.site for incoming POST.
Check `http://localhost:8080` alerts table to see the logged alert.

### Manual Trigger
Click "Trigger Pipeline Now" button on the dashboard.
OR: `curl -X POST http://localhost:8080/trigger-now`

### How to Verify Scheduler is Running
Watch `docker-compose logs -f`
Or check the "Last Fetch Time" card on the dashboard
Or run `curl http://localhost:8080/health`

### Project Structure
```text
pipeline/
├── src/
│   ├── __init__.py       # Package initializer
│   ├── ingester.py       # Fetches weather from Open-Meteo API
│   ├── processor.py      # Checks if alert conditions are met
│   ├── alerter.py        # Sends webhook POST on alert
│   ├── database.py       # SQLite setup and queries
│   ├── scheduler.py      # APScheduler recurring job
│   └── api.py            # FastAPI routes + Jinja2 HTML dashboard
├── templates/
│   └── dashboard.html    # Main HTML page with Bootstrap + Chart.js
├── logs/                 # Stores rotating system logs
├── data/                 # Stores the SQLite database file
├── main.py               # Entry point
├── config.py             # All config from .env
├── Dockerfile            # Container definition
├── docker-compose.yml    # Service orchestration
├── requirements.txt      # Python dependencies
└── .env.example          # Environment variables template
```

### Environment Variables
| Variable | Description | Default |
| -------- | ----------- | ------- |
| WEATHER_LAT | Latitude coordinate for weather data | 27.61 |
| WEATHER_LON | Longitude coordinate for weather data | 75.15 |
| WEATHER_LOCATION_NAME | Display name for the location | Sikar, Rajasthan |
| FETCH_INTERVAL_MINUTES | How often the pipeline runs | 5 |
| TEMP_ALERT_THRESHOLD | Temperature above which HEAT_ALERT fires | 38.0 |
| WEBHOOK_URL | The destination URL for alert POST requests | (Empty) |
| DB_PATH | Path to the SQLite DB file | data/pipeline.db |
| LOG_PATH | Path to the rotating log file | logs/pipeline.log |
| API_PORT | Port for the FastAPI server | 8080 |
