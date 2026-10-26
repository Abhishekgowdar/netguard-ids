"""
Configuration management for NetGuard IDS
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
API_RELOAD = os.getenv("API_RELOAD", "True").lower() == "true"

# Network Capture Configuration
NETWORK_INTERFACE = os.getenv("NETWORK_INTERFACE", None)  # None = auto-detect
CAPTURE_FILTER = os.getenv("CAPTURE_FILTER", "")  # BPF filter
PACKET_COUNT = int(os.getenv("PACKET_COUNT", 0))  # 0 = infinite
PROMISCUOUS_MODE = os.getenv("PROMISCUOUS_MODE", "True").lower() == "true"

# Detection Configuration
SIGNATURE_DETECTION_ENABLED = True
ML_DETECTION_ENABLED = True

# Port Scan Detection
PORT_SCAN_THRESHOLD = int(os.getenv("PORT_SCAN_THRESHOLD", 50))  # ports
PORT_SCAN_TIME_WINDOW = int(os.getenv("PORT_SCAN_TIME_WINDOW", 60))  # seconds

# DDoS Detection
DDOS_THRESHOLD = int(os.getenv("DDOS_THRESHOLD", 1000))  # packets/second
DDOS_TIME_WINDOW = int(os.getenv("DDOS_TIME_WINDOW", 10))  # seconds

# Brute Force Detection
BRUTE_FORCE_THRESHOLD = int(os.getenv("BRUTE_FORCE_THRESHOLD", 50))  # failed attempts
BRUTE_FORCE_TIME_WINDOW = int(os.getenv("BRUTE_FORCE_TIME_WINDOW", 300))  # seconds

# ML Model Configuration
ML_MODEL_PATH = BASE_DIR / "ml-training" / "models" / "isolation_forest.pkl"
ML_ANOMALY_THRESHOLD = float(os.getenv("ML_ANOMALY_THRESHOLD", -0.5))  # Isolation Forest score
ML_BATCH_SIZE = int(os.getenv("ML_BATCH_SIZE", 100))

# Database Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{BASE_DIR / 'backend' / 'netguard.db'}"
)

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = BASE_DIR / "backend" / "logs" / "netguard.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Alert Configuration
ALERT_SEVERITY_LEVELS = {
    "LOW": 1,
    "MEDIUM": 5,
    "HIGH": 7,
    "CRITICAL": 9
}

# Email Alert Configuration (Optional)
EMAIL_ALERTS_ENABLED = os.getenv("EMAIL_ALERTS_ENABLED", "False").lower() == "true"
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
ALERT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO", "")

# WebSocket Configuration
WS_HEARTBEAT_INTERVAL = 30  # seconds

# CORS Configuration
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

# Create necessary directories
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

print(f"✅ Configuration loaded")
print(f"📂 Base directory: {BASE_DIR}")
print(f"🌐 API will run on: http://{API_HOST}:{API_PORT}")
print(f"🗄️  Database: {DATABASE_URL}")
