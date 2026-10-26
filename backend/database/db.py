"""
Database connection and session management
"""
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
import sys
from pathlib import Path

# Add parent directory to path for config import
sys.path.append(str(Path(__file__).parent.parent))
from config import DATABASE_URL

logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Database:
    """Database helper class"""

    @staticmethod
    def init_db():
        """Initialize database (create tables)"""
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Database initialized successfully")
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise

    @staticmethod
    def get_session():
        """Get database session"""
        session = SessionLocal()
        try:
            return session
        except Exception as e:
            logger.error(f"Error creating database session: {e}")
            session.close()
            raise

    @staticmethod
    def save_alert(session, alert_data: dict):
        """Save alert to database"""
        from .models import Alert
        import json

        try:
            # Extract main fields
            alert = Alert(
                type=alert_data.get('type'),
                severity=alert_data.get('severity', 5),
                source_ip=alert_data.get('source_ip'),
                target_ip=alert_data.get('target_ip'),
                target_port=alert_data.get('target_port'),
                protocol=alert_data.get('protocol'),
                description=alert_data.get('description'),
                confidence=alert_data.get('confidence', 1.0),
                metadata=json.dumps(alert_data.get('metadata', {}))
            )

            session.add(alert)
            session.commit()
            session.refresh(alert)

            logger.info(f"💾 Alert saved to database (ID: {alert.id})")
            return alert

        except Exception as e:
            logger.error(f"Error saving alert: {e}")
            session.rollback()
            return None

    @staticmethod
    def save_traffic_log(session, packet_data: dict):
        """Save traffic log to database"""
        from .models import TrafficLog

        try:
            log = TrafficLog(
                source_ip=packet_data.get('src_ip'),
                dest_ip=packet_data.get('dst_ip'),
                source_port=packet_data.get('src_port'),
                dest_port=packet_data.get('dst_port'),
                protocol=packet_data.get('protocol'),
                packet_length=packet_data.get('length'),
                flags=packet_data.get('flags', ''),
                info=packet_data.get('info', '')
            )

            session.add(log)
            session.commit()

            return log

        except Exception as e:
            logger.error(f"Error saving traffic log: {e}")
            session.rollback()
            return None

    @staticmethod
    def get_recent_alerts(session, limit: int = 100):
        """Get recent alerts from database"""
        from .models import Alert

        try:
            alerts = session.query(Alert).order_by(Alert.timestamp.desc()).limit(limit).all()
            return [alert.to_dict() for alert in alerts]
        except Exception as e:
            logger.error(f"Error fetching alerts: {e}")
            return []

    @staticmethod
    def get_alert_stats(session):
        """Get alert statistics"""
        from .models import Alert
        from sqlalchemy import func

        try:
            total_alerts = session.query(func.count(Alert.id)).scalar()

            severity_counts = session.query(
                Alert.severity,
                func.count(Alert.id)
            ).group_by(Alert.severity).all()

            type_counts = session.query(
                Alert.type,
                func.count(Alert.id)
            ).group_by(Alert.type).all()

            return {
                'total_alerts': total_alerts,
                'by_severity': {sev: count for sev, count in severity_counts},
                'by_type': {typ: count for typ, count in type_counts}
            }

        except Exception as e:
            logger.error(f"Error fetching alert stats: {e}")
            return {}


if __name__ == "__main__":
    # Test database
    logging.basicConfig(level=logging.INFO)

    print("Initializing database...")
    Database.init_db()

    print("\nTesting database operations...")
    session = Database.get_session()

    # Test alert save
    test_alert = {
        'type': 'Port Scan',
        'severity': 7,
        'source_ip': '192.168.1.100',
        'target_ip': '192.168.1.1',
        'description': 'Test alert',
        'confidence': 0.95
    }

    saved_alert = Database.save_alert(session, test_alert)
    print(f"Saved alert: {saved_alert.to_dict() if saved_alert else 'Failed'}")

    # Get recent alerts
    alerts = Database.get_recent_alerts(session, limit=10)
    print(f"\nRecent alerts: {len(alerts)}")

    # Get stats
    stats = Database.get_alert_stats(session)
    print(f"\nStats: {stats}")

    session.close()
