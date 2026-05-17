import logging
import logging.handlers
import os
import uvicorn
from config import LOG_PATH, API_PORT
from src.database import init_db
from src.scheduler import start_scheduler, run_pipeline_job
from src.api import app

def setup_logging():
    """Configures logging for console and rotating file output."""
    # Ensure logs directory exists
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    
    # Root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # File handler (1MB max, 3 backups)
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_PATH, maxBytes=1_000_000, backupCount=3
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Pipeline starting up...")
    
    # Initialize the SQLite Database
    init_db()
    
    # Run the pipeline job once synchronously so we have data before the server starts
    logger.info("Running initial pipeline job...")
    run_pipeline_job()
    
    # Start the APScheduler for recurring jobs
    scheduler = start_scheduler()
    
    # Set the global flag so the API dashboard knows it's active
    app.state.scheduler_running = True
    
    try:
        # Start FastAPI application
        logger.info(f"Starting server on port {API_PORT}...")
        uvicorn.run(app, host="0.0.0.0", port=API_PORT)
    finally:
        # Graceful shutdown
        logger.info("Shutting down...")
        scheduler.shutdown(wait=False)
        logger.info("Shutdown complete.")
