"""
FastAPI application for NetGuard IDS
Provides REST API endpoints for the frontend dashboard
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

from config import CORS_ORIGINS
from database.db import Database
from database.models import Alert, TrafficLog
from utils.logger import setup_logger

# Setup logger
logger = setup_logger("netguard.api")

# Initialize FastAPI app
app = FastAPI(
    title="NetGuard IDS API",
    description="REST API for Network Intrusion Detection System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
Database.init_db()


# Pydantic models for requests/responses
class AlertResponse(BaseModel):
    id: int
    type: str
    severity: int
    source_ip: Optional[str]
    target_ip: Optional[str]
    target_port: Optional[int]
    protocol: Optional[str]
    description: Optional[str]
    timestamp: str
    confidence: float
    resolved: bool


class StatsResponse(BaseModel):
    total_alerts: int
    alerts_today: int
    alerts_last_hour: int
    critical_alerts: int
    high_alerts: int
    medium_alerts: int
    low_alerts: int


@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "name": "NetGuard IDS API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/alerts", response_model=List[AlertResponse])
def get_alerts(limit: int = 100, offset: int = 0):
    """
    Get recent alerts

    Args:
        limit: Maximum number of alerts to return
        offset: Number of alerts to skip

    Returns:
        List of alerts
    """
    try:
        session = Database.get_session()
        alerts = session.query(Alert).order_by(
            Alert.timestamp.desc()
        ).offset(offset).limit(limit).all()

        result = []
        for alert in alerts:
            result.append({
                'id': alert.id,
                'type': alert.type,
                'severity': alert.severity,
                'source_ip': alert.source_ip,
                'target_ip': alert.target_ip,
                'target_port': alert.target_port,
                'protocol': alert.protocol,
                'description': alert.description,
                'timestamp': alert.timestamp.isoformat() if alert.timestamp else None,
                'confidence': alert.confidence,
                'resolved': alert.resolved
            })

        session.close()
        return result

    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/alerts/{alert_id}")
def get_alert(alert_id: int):
    """
    Get specific alert by ID

    Args:
        alert_id: Alert ID

    Returns:
        Alert details
    """
    try:
        session = Database.get_session()
        alert = session.query(Alert).filter(Alert.id == alert_id).first()

        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")

        result = alert.to_dict()
        session.close()
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats", response_model=StatsResponse)
def get_statistics():
    """
    Get system statistics

    Returns:
        Statistics including alert counts
    """
    try:
        session = Database.get_session()

        # Total alerts
        total_alerts = session.query(Alert).count()

        # Alerts today
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        alerts_today = session.query(Alert).filter(
            Alert.timestamp >= today_start
        ).count()

        # Alerts last hour
        last_hour = datetime.now() - timedelta(hours=1)
        alerts_last_hour = session.query(Alert).filter(
            Alert.timestamp >= last_hour
        ).count()

        # By severity
        critical_alerts = session.query(Alert).filter(Alert.severity >= 9).count()
        high_alerts = session.query(Alert).filter(Alert.severity >= 7, Alert.severity < 9).count()
        medium_alerts = session.query(Alert).filter(Alert.severity >= 5, Alert.severity < 7).count()
        low_alerts = session.query(Alert).filter(Alert.severity < 5).count()

        session.close()

        return {
            'total_alerts': total_alerts,
            'alerts_today': alerts_today,
            'alerts_last_hour': alerts_last_hour,
            'critical_alerts': critical_alerts,
            'high_alerts': high_alerts,
            'medium_alerts': medium_alerts,
            'low_alerts': low_alerts
        }

    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/alerts/by-type")
def get_alerts_by_type():
    """
    Get alert counts grouped by type

    Returns:
        Dictionary with attack types and counts
    """
    try:
        session = Database.get_session()

        from sqlalchemy import func
        results = session.query(
            Alert.type,
            func.count(Alert.id).label('count')
        ).group_by(Alert.type).all()

        alert_types = {alert_type: count for alert_type, count in results}

        session.close()
        return alert_types

    except Exception as e:
        logger.error(f"Error fetching alerts by type: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/alerts/timeline")
def get_alerts_timeline(hours: int = 24):
    """
    Get alerts timeline for the last N hours

    Args:
        hours: Number of hours to look back

    Returns:
        List of hourly alert counts
    """
    try:
        session = Database.get_session()

        cutoff_time = datetime.now() - timedelta(hours=hours)

        from sqlalchemy import func
        results = session.query(
            func.strftime('%Y-%m-%d %H:00:00', Alert.timestamp).label('hour'),
            func.count(Alert.id).label('count')
        ).filter(
            Alert.timestamp >= cutoff_time
        ).group_by('hour').order_by('hour').all()

        timeline = [{'hour': hour, 'count': count} for hour, count in results]

        session.close()
        return timeline

    except Exception as e:
        logger.error(f"Error fetching timeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting NetGuard IDS API server...")
    logger.info(f"API will be available at: http://localhost:8000")
    logger.info("API documentation: http://localhost:8000/docs")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
