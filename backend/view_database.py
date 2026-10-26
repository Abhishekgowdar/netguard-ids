"""
View NetGuard IDS Database Contents
Simple script to view all alerts in the database
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from database.db import Database
from database.models import Alert

def view_database():
    """View all alerts in database"""
    print("=" * 80)
    print("📊 NetGuard IDS - Database Viewer")
    print("=" * 80)
    print()

    # Get database session
    Database.init_db()
    session = Database.get_session()

    # Get all alerts
    alerts = session.query(Alert).order_by(Alert.timestamp.desc()).all()

    print(f"📂 Database Location: {Path(__file__).parent / 'netguard.db'}")
    print(f"📊 Total Alerts: {len(alerts)}")
    print()

    if len(alerts) == 0:
        print("⚠️  No alerts found in database!")
        session.close()
        return

    # Statistics
    from collections import Counter

    severity_counts = Counter()
    type_counts = Counter()

    for alert in alerts:
        if alert.severity >= 9:
            severity_counts['CRITICAL'] += 1
        elif alert.severity >= 7:
            severity_counts['HIGH'] += 1
        elif alert.severity >= 5:
            severity_counts['MEDIUM'] += 1
        else:
            severity_counts['LOW'] += 1

        type_counts[alert.type] += 1

    print("📈 Statistics:")
    print()
    print("By Severity:")
    for severity, count in severity_counts.most_common():
        print(f"   {severity}: {count}")

    print()
    print("By Type:")
    for alert_type, count in type_counts.most_common():
        print(f"   {alert_type}: {count}")

    print()
    print("=" * 80)
    print("🔴 Recent Alerts (Last 20)")
    print("=" * 80)
    print()

    # Display recent alerts
    for i, alert in enumerate(alerts[:20], 1):
        severity_emoji = {
            10: '🔴', 9: '🔴', 8: '🟠', 7: '🟠',
            6: '🟡', 5: '🟡', 4: '🟢', 3: '🟢', 2: '🟢', 1: '🟢'
        }
        emoji = severity_emoji.get(alert.severity, '⚪')

        print(f"{emoji} Alert #{alert.id} - {alert.type} (Severity: {alert.severity})")
        print(f"   Description: {alert.description[:80]}")
        print(f"   Source: {alert.source_ip} → Target: {alert.target_ip}:{alert.target_port}")
        print(f"   Protocol: {alert.protocol} | Confidence: {alert.confidence:.0%}")
        print(f"   Timestamp: {alert.timestamp}")
        print()

    print("=" * 80)
    print(f"💡 Showing 20 of {len(alerts)} total alerts")
    print("=" * 80)

    session.close()


def view_stats_only():
    """View just statistics"""
    session = Database.get_session()

    stats = Database.get_alert_stats(session)

    print("=" * 80)
    print("📊 Database Statistics")
    print("=" * 80)
    print()
    print(f"Total Alerts: {stats.get('total_alerts', 0)}")
    print()
    print("By Severity:")
    for severity, count in stats.get('by_severity', {}).items():
        print(f"   Severity {severity}: {count}")
    print()
    print("By Type:")
    for alert_type, count in stats.get('by_type', {}).items():
        print(f"   {alert_type}: {count}")
    print()
    print("=" * 80)

    session.close()


def clear_database():
    """Clear all alerts from database"""
    session = Database.get_session()

    count = session.query(Alert).count()

    print("=" * 80)
    print("⚠️  WARNING: Clear Database")
    print("=" * 80)
    print()
    print(f"This will delete {count} alerts from the database!")
    print()

    response = input("Are you sure? Type 'yes' to confirm: ")

    if response.lower() == 'yes':
        session.query(Alert).delete()
        session.commit()
        print()
        print(f"✅ Deleted {count} alerts from database")
    else:
        print()
        print("❌ Cancelled - no alerts deleted")

    session.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='View NetGuard IDS database')
    parser.add_argument('-s', '--stats', action='store_true', help='Show statistics only')
    parser.add_argument('-c', '--clear', action='store_true', help='Clear all alerts')

    args = parser.parse_args()

    if args.clear:
        clear_database()
    elif args.stats:
        view_stats_only()
    else:
        view_database()
