"""
Run FastAPI server separately from the main IDS
This allows the dashboard to work even if packet capture isn't running
"""
import uvicorn
from api.app import app
from config import API_HOST, API_PORT
from utils.logger import setup_logger

logger = setup_logger("netguard.api")

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🌐 Starting NetGuard IDS API Server")
    logger.info("=" * 60)
    logger.info(f"API Server: http://{API_HOST}:{API_PORT}")
    logger.info(f"API Docs: http://{API_HOST}:{API_PORT}/docs")
    logger.info("=" * 60)

    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        log_level="info"
    )
