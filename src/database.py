import sqlite3
import logging
import os
from config import DB_PATH

logger = logging.getLogger(__name__)

def get_connection():
    """Returns a connection to the SQLite database."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database by creating necessary tables if they do not exist."""
    logger.info("Initializing database...")
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS weather_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fetched_at TEXT,
                    location TEXT,
                    temperature_c REAL,
                    apparent_temperature_c REAL,
                    wind_speed_kmh REAL,
                    weather_code INTEGER
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    triggered_at TEXT,
                    alert_type TEXT,
                    message TEXT,
                    temperature_c REAL,
                    webhook_success BOOLEAN,
                    webhook_status_code INTEGER
                )
            ''')
            conn.commit()
        logger.info("Database initialization complete.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

def save_reading(data: dict):
    """Saves a weather reading dictionary into the weather_readings table."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO weather_readings (
                    fetched_at, location, temperature_c, apparent_temperature_c, wind_speed_kmh, weather_code
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                data.get("fetched_at"),
                data.get("location"),
                data.get("temperature_c"),
                data.get("apparent_temperature_c"),
                data.get("wind_speed_kmh"),
                data.get("weather_code")
            ))
            conn.commit()
    except Exception as e:
        logger.error(f"Error saving reading to database: {e}")

def save_alert(data: dict):
    """Saves an alert dictionary into the alerts_log table."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO alerts_log (
                    triggered_at, alert_type, message, temperature_c, webhook_success, webhook_status_code
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                data.get("triggered_at"),
                data.get("alert_type"),
                data.get("message"),
                data.get("temperature_c"),
                data.get("webhook_success"),
                data.get("webhook_status_code")
            ))
            conn.commit()
    except Exception as e:
        logger.error(f"Error saving alert to database: {e}")

def get_recent_readings(limit=20):
    """Returns the most recent weather readings up to the specified limit."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM weather_readings ORDER BY id DESC LIMIT ?', (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching recent readings: {e}")
        return []

def get_recent_alerts(limit=10):
    """Returns the most recent alerts up to the specified limit."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM alerts_log ORDER BY id DESC LIMIT ?', (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching recent alerts: {e}")
        return []

def get_db_status():
    """Returns True if the DB file exists and is readable, False otherwise."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            return True
    except Exception as e:
        logger.error(f"Database status check failed: {e}")
        return False
