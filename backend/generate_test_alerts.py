"""
Generate Test Alerts for NetGuard IDS
Creates realistic fake alerts to test the dashboard
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from database.db import Database
from database.models import Alert

# Sample alert data
ALERT_TYPES = [
    {
        'type': 'Port Scan',
        'severity_range': (7, 9),
        'descriptions': [
            'Port scan detected: {} ports scanned in {}s',
            'Aggressive port scanning activity detected',
            'Sequential port scan from suspicious IP',
            'Stealth port scan detected using SYN packets'
        ],
        'protocols': ['TCP'],
        'target_ports': [22, 80, 443, 3306, 8080, 3389]
    },
    {
        'type': 'DDoS Attack',
        'severity_range': (8, 10),
        'descriptions': [
            'DDoS attack detected: {} packets in {}s ({} pkt/s)',
            'Distributed denial of service attack in progress',
            'Traffic flooding detected from multiple sources',
            'SYN flood attack detected'
        ],
        'protocols': ['TCP', 'UDP', 'ICMP'],
        'target_ports': [80, 443, 8080]
    },
    {
        'type': 'SQL Injection',
        'severity_range': (7, 9),
        'descriptions': [
            'SQL injection attempt detected in HTTP payload',
            'Malicious SQL keywords found in request',
            'Database attack prevented: SQL injection pattern detected',
            'Multiple SQL injection attempts from same source'
        ],
        'protocols': ['TCP'],
        'target_ports': [80, 443, 8080, 3000]
    },
    {
        'type': 'Brute Force Attack',
        'severity_range': (6, 8),
        'descriptions': [
            'Brute force login attempts detected: {} failed attempts',
            'Multiple authentication failures from single IP',
            'Credential stuffing attack detected',
            'Dictionary attack on SSH service'
        ],
        'protocols': ['TCP'],
        'target_ports': [22, 3389, 21, 23]
    },
    {
        'type': 'Suspicious Port Access',
        'severity_range': (5, 7),
        'descriptions': [
            'Connection to suspicious port {} detected',
            'Malware communication attempt detected',
            'Backdoor port access detected',
            'Known malicious port activity'
        ],
        'protocols': ['TCP', 'UDP'],
        'target_ports': [1337, 31337, 4444, 6666, 12345]
    },
    {
        'type': 'Anomaly Detected (ML)',
        'severity_range': (6, 9),
        'descriptions': [
            'ML model detected unusual network behavior (anomaly score: {:.3f})',
            'Abnormal traffic pattern detected by AI',
            'Zero-day attack suspected: unusual packet structure',
            'Machine learning flagged suspicious activity'
        ],
        'protocols': ['TCP', 'UDP', 'ICMP'],
        'target_ports': [80, 443, 8080, 3000, 5000]
    }
]

# Sample IPs (attacker sources)
ATTACKER_IPS = [
    '203.45.67.89',
    '45.142.212.61',
    '185.220.101.34',
    '94.102.49.173',
    '192.168.1.100',
    '10.0.0.55',
    '172.16.0.89',
    '198.51.100.45'
]

# Sample target IPs
TARGET_IPS = [
    '192.168.1.1',
    '192.168.1.10',
    '10.0.0.1',
    '172.16.0.1'
]


def generate_random_alert():
    """Generate a random realistic alert"""
    alert_template = random.choice(ALERT_TYPES)

    # Random severity within range
    severity = random.randint(*alert_template['severity_range'])

    # Random description
    description_template = random.choice(alert_template['descriptions'])

    # Format description with random values
    if '{}' in description_template:
        if 'Port scan' in description_template:
            ports = random.randint(50, 200)
            duration = random.randint(30, 120)
            description = description_template.format(ports, duration)
        elif 'DDoS' in description_template:
            packets = random.randint(1000, 50000)
            duration = random.randint(5, 60)
            pps = packets // duration
            description = description_template.format(packets, duration, pps)
        elif 'Brute force' in description_template:
            attempts = random.randint(50, 500)
            description = description_template.format(attempts)
        elif 'port {}' in description_template:
            port = random.choice(alert_template['target_ports'])
            description = description_template.format(port)
        elif 'score:' in description_template:
            score = random.uniform(-0.9, -0.4)
            description = description_template.format(score)
        else:
            description = description_template
    else:
        description = description_template

    # Random IPs and ports
    source_ip = random.choice(ATTACKER_IPS)
    target_ip = random.choice(TARGET_IPS)
    target_port = random.choice(alert_template['target_ports'])
    protocol = random.choice(alert_template['protocols'])

    # Random timestamp (within last 24 hours)
    hours_ago = random.uniform(0, 24)
    timestamp = datetime.now() - timedelta(hours=hours_ago)

    # Random confidence
    confidence = random.uniform(0.75, 0.99)

    return {
        'type': alert_template['type'],
        'severity': severity,
        'source_ip': source_ip,
        'target_ip': target_ip,
        'target_port': target_port,
        'protocol': protocol,
        'description': description,
        'confidence': confidence,
        'timestamp': timestamp
    }


def create_test_alerts(num_alerts=20):
    """Create multiple test alerts"""
    print("=" * 60)
    print("🧪 NetGuard IDS - Test Alert Generator")
    print("=" * 60)
    print()

    # Initialize database
    print("📂 Initializing database...")
    Database.init_db()
    session = Database.get_session()

    print(f"✨ Generating {num_alerts} test alerts...")
    print()

    created_alerts = []

    for i in range(num_alerts):
        alert_data = generate_random_alert()

        # Create alert
        alert = Alert(
            type=alert_data['type'],
            severity=alert_data['severity'],
            source_ip=alert_data['source_ip'],
            target_ip=alert_data['target_ip'],
            target_port=alert_data['target_port'],
            protocol=alert_data['protocol'],
            description=alert_data['description'],
            confidence=alert_data['confidence'],
            timestamp=alert_data['timestamp'],
            resolved=False
        )

        session.add(alert)
        created_alerts.append(alert_data)

        # Print summary
        severity_emoji = {
            10: '🔴', 9: '🔴', 8: '🟠', 7: '🟠',
            6: '🟡', 5: '🟡', 4: '🟢', 3: '🟢'
        }
        emoji = severity_emoji.get(alert_data['severity'], '⚪')

        print(f"{emoji} Alert {i+1}: {alert_data['type']} (Severity: {alert_data['severity']})")
        print(f"   {alert_data['description'][:80]}")

    # Commit all alerts
    session.commit()

    print()
    print("=" * 60)
    print(f"✅ Successfully created {num_alerts} test alerts!")
    print("=" * 60)
    print()

    # Statistics
    severity_counts = {}
    type_counts = {}

    for alert_data in created_alerts:
        severity = alert_data['severity']
        alert_type = alert_data['type']

        severity_counts[severity] = severity_counts.get(severity, 0) + 1
        type_counts[alert_type] = type_counts.get(alert_type, 0) + 1

    print("📊 Alert Statistics:")
    print()
    print("By Severity:")
    for severity in sorted(severity_counts.keys(), reverse=True):
        count = severity_counts[severity]
        if severity >= 9:
            level = "CRITICAL"
        elif severity >= 7:
            level = "HIGH"
        elif severity >= 5:
            level = "MEDIUM"
        else:
            level = "LOW"
        print(f"   {level} ({severity}): {count}")

    print()
    print("By Type:")
    for alert_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {alert_type}: {count}")

    print()
    print("🌐 Open the dashboard to see these alerts:")
    print("   http://localhost:3000")
    print()
    print("💡 Tip: Run this script multiple times to add more alerts!")
    print("=" * 60)

    session.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Generate test alerts for NetGuard IDS')
    parser.add_argument('-n', '--num', type=int, default=20, help='Number of alerts to generate (default: 20)')
    parser.add_argument('-c', '--clear', action='store_true', help='Clear existing alerts first')

    args = parser.parse_args()

    if args.clear:
        print("🗑️  Clearing existing alerts...")
        Database.init_db()
        session = Database.get_session()
        session.query(Alert).delete()
        session.commit()
        print("✅ Existing alerts cleared")
        print()
        session.close()

    create_test_alerts(args.num)
