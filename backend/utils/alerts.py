"""
Alert management and notification system
"""
import logging
from typing import Dict, List
from collections import deque
from datetime import datetime

logger = logging.getLogger(__name__)


class AlertManager:
    """
    Manages alerts and notifications
    """

    def __init__(self, max_alerts: int = 1000):
        """
        Initialize alert manager

        Args:
            max_alerts: Maximum number of alerts to keep in memory
        """
        self.max_alerts = max_alerts
        self.recent_alerts = deque(maxlen=max_alerts)
        self.alert_count = 0
        self.severity_counts = {
            'LOW': 0,
            'MEDIUM': 0,
            'HIGH': 0,
            'CRITICAL': 0
        }

    def add_alert(self, alert: Dict):
        """
        Add new alert

        Args:
            alert: Alert dictionary
        """
        # Add timestamp if not present
        if 'timestamp' not in alert:
            alert['timestamp'] = datetime.now().isoformat()

        # Add to recent alerts
        self.recent_alerts.append(alert)
        self.alert_count += 1

        # Update severity counts
        severity_level = self._get_severity_level(alert.get('severity', 5))
        self.severity_counts[severity_level] += 1

        # Log alert
        severity = alert.get('severity', 5)
        alert_type = alert.get('type', 'Unknown')
        source_ip = alert.get('source_ip', 'Unknown')

        logger.warning(f"🚨 ALERT #{self.alert_count}: {alert_type} (Severity: {severity}) from {source_ip}")

    def get_recent_alerts(self, count: int = 100) -> List[Dict]:
        """Get recent alerts"""
        return list(self.recent_alerts)[-count:]

    def get_alert_count(self) -> int:
        """Get total alert count"""
        return self.alert_count

    def get_severity_counts(self) -> Dict:
        """Get alerts by severity"""
        return self.severity_counts.copy()

    def get_statistics(self) -> Dict:
        """Get alert statistics"""
        return {
            'total_alerts': self.alert_count,
            'recent_alerts': len(self.recent_alerts),
            'by_severity': self.severity_counts
        }

    def _get_severity_level(self, severity: int) -> str:
        """Convert severity number to level"""
        if severity >= 9:
            return 'CRITICAL'
        elif severity >= 7:
            return 'HIGH'
        elif severity >= 5:
            return 'MEDIUM'
        else:
            return 'LOW'


if __name__ == "__main__":
    # Test alert manager
    logging.basicConfig(level=logging.INFO)

    manager = AlertManager()

    # Add test alerts
    test_alerts = [
        {'type': 'Port Scan', 'severity': 7, 'source_ip': '192.168.1.100'},
        {'type': 'DDoS', 'severity': 9, 'source_ip': '192.168.1.101'},
        {'type': 'SQL Injection', 'severity': 8, 'source_ip': '192.168.1.102'},
    ]

    for alert in test_alerts:
        manager.add_alert(alert)

    print(f"\nTotal alerts: {manager.get_alert_count()}")
    print(f"Severity counts: {manager.get_severity_counts()}")
    print(f"Statistics: {manager.get_statistics()}")
