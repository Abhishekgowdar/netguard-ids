"""
Signature-based detection rules for known attack patterns
"""
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import re

logger = logging.getLogger(__name__)


class SignatureDetector:
    """
    Detects attacks using signature-based rules
    """

    def __init__(self,
                 port_scan_threshold: int = 50,
                 port_scan_window: int = 60,
                 ddos_threshold: int = 1000,
                 ddos_window: int = 10,
                 brute_force_threshold: int = 50,
                 brute_force_window: int = 300):
        """
        Initialize signature detector

        Args:
            port_scan_threshold: Number of ports to trigger port scan alert
            port_scan_window: Time window in seconds
            ddos_threshold: Packets per second to trigger DDoS alert
            ddos_window: Time window in seconds
            brute_force_threshold: Failed attempts to trigger brute force alert
            brute_force_window: Time window in seconds
        """
        self.port_scan_threshold = port_scan_threshold
        self.port_scan_window = port_scan_window
        self.ddos_threshold = ddos_threshold
        self.ddos_window = ddos_window
        self.brute_force_threshold = brute_force_threshold
        self.brute_force_window = brute_force_window

        # Track suspicious activities
        self.port_access = defaultdict(lambda: {'ports': set(), 'timestamps': []})
        self.traffic_count = defaultdict(lambda: {'count': 0, 'timestamps': []})
        self.failed_logins = defaultdict(lambda: {'count': 0, 'timestamps': []})

        # SQL injection patterns
        self.sql_patterns = [
            r"(\bunion\b.*\bselect\b)",
            r"(\bselect\b.*\bfrom\b.*\bwhere\b)",
            r"(\'.*or.*\'.*=.*\')",
            r"(\bdrop\b.*\btable\b)",
            r"(--\s*$)",
            r"(;\s*drop\s+table)",
            r"(exec\s*\()",
            r"(execute\s*\()",
        ]

        logger.info("✅ SignatureDetector initialized")

    def detect(self, packet_data: Dict) -> Optional[Dict]:
        """
        Analyze packet and detect known attack patterns

        Args:
            packet_data: Parsed packet dictionary

        Returns:
            Alert dictionary if threat detected, None otherwise
        """
        alerts = []

        # Check for port scan
        port_scan_alert = self._detect_port_scan(packet_data)
        if port_scan_alert:
            alerts.append(port_scan_alert)

        # Check for DDoS
        ddos_alert = self._detect_ddos(packet_data)
        if ddos_alert:
            alerts.append(ddos_alert)

        # Check for SQL injection
        sql_injection_alert = self._detect_sql_injection(packet_data)
        if sql_injection_alert:
            alerts.append(sql_injection_alert)

        # Check for suspicious protocols
        suspicious_proto_alert = self._detect_suspicious_protocols(packet_data)
        if suspicious_proto_alert:
            alerts.append(suspicious_proto_alert)

        # Return the highest severity alert
        if alerts:
            alerts.sort(key=lambda x: x['severity'], reverse=True)
            return alerts[0]

        return None

    def _detect_port_scan(self, packet_data: Dict) -> Optional[Dict]:
        """Detect port scanning attempts"""
        src_ip = packet_data.get('src_ip')
        dst_port = packet_data.get('dst_port')
        protocol = packet_data.get('protocol')

        if not src_ip or not dst_port or protocol != 'TCP':
            return None

        # Track ports accessed by this IP
        now = datetime.now()
        tracker = self.port_access[src_ip]
        tracker['ports'].add(dst_port)
        tracker['timestamps'].append(now)

        # Clean old timestamps
        cutoff_time = now - timedelta(seconds=self.port_scan_window)
        tracker['timestamps'] = [ts for ts in tracker['timestamps'] if ts > cutoff_time]

        # Check for port scan
        ports_scanned = len(tracker['ports'])
        if ports_scanned >= self.port_scan_threshold:
            logger.warning(f"🚨 Port scan detected from {src_ip} ({ports_scanned} ports)")

            # Reset tracker
            self.port_access[src_ip] = {'ports': set(), 'timestamps': []}

            return {
                'type': 'Port Scan',
                'severity': 7,  # HIGH
                'source_ip': src_ip,
                'target_ip': packet_data.get('dst_ip'),
                'description': f'Port scan detected: {ports_scanned} ports scanned in {self.port_scan_window}s',
                'ports_scanned': list(tracker['ports'])[:20],  # Limit to first 20 ports
                'timestamp': now.isoformat(),
                'confidence': 0.95
            }

        return None

    def _detect_ddos(self, packet_data: Dict) -> Optional[Dict]:
        """Detect DDoS attacks based on traffic volume"""
        dst_ip = packet_data.get('dst_ip')

        if not dst_ip:
            return None

        # Track traffic to this destination
        now = datetime.now()
        tracker = self.traffic_count[dst_ip]
        tracker['count'] += 1
        tracker['timestamps'].append(now)

        # Clean old timestamps
        cutoff_time = now - timedelta(seconds=self.ddos_window)
        tracker['timestamps'] = [ts for ts in tracker['timestamps'] if ts > cutoff_time]
        tracker['count'] = len(tracker['timestamps'])

        # Check for DDoS
        packets_per_second = tracker['count'] / self.ddos_window
        if tracker['count'] >= self.ddos_threshold:
            logger.warning(f"🚨 DDoS detected targeting {dst_ip} ({tracker['count']} packets in {self.ddos_window}s)")

            # Reset tracker
            self.traffic_count[dst_ip] = {'count': 0, 'timestamps': []}

            return {
                'type': 'DDoS Attack',
                'severity': 9,  # CRITICAL
                'source_ip': packet_data.get('src_ip'),
                'target_ip': dst_ip,
                'description': f'DDoS attack detected: {tracker["count"]} packets in {self.ddos_window}s ({packets_per_second:.0f} pkt/s)',
                'packet_count': tracker['count'],
                'timestamp': now.isoformat(),
                'confidence': 0.90
            }

        return None

    def _detect_sql_injection(self, packet_data: Dict) -> Optional[Dict]:
        """Detect SQL injection attempts in payload"""
        payload = packet_data.get('payload', '').lower()

        if not payload:
            return None

        # Check for SQL injection patterns
        for pattern in self.sql_patterns:
            if re.search(pattern, payload, re.IGNORECASE):
                logger.warning(f"🚨 SQL injection detected from {packet_data.get('src_ip')}")

                return {
                    'type': 'SQL Injection',
                    'severity': 8,  # HIGH
                    'source_ip': packet_data.get('src_ip'),
                    'target_ip': packet_data.get('dst_ip'),
                    'target_port': packet_data.get('dst_port'),
                    'description': f'SQL injection attempt detected in payload',
                    'payload_sample': payload[:100],
                    'timestamp': datetime.now().isoformat(),
                    'confidence': 0.85
                }

        return None

    def _detect_suspicious_protocols(self, packet_data: Dict) -> Optional[Dict]:
        """Detect suspicious protocol usage"""
        dst_port = packet_data.get('dst_port')
        protocol = packet_data.get('protocol')

        # Suspicious ports (common malware/attack ports)
        suspicious_ports = {
            1337, 31337,  # Leet speak ports (common for backdoors)
            12345, 12346,  # NetBus
            20034,  # NetBus Pro
            6666, 6667, 6668, 6669,  # IRC (often used by botnets)
            4444,  # Metasploit default
        }

        if dst_port in suspicious_ports:
            logger.warning(f"🚨 Suspicious port usage: {dst_port}")

            return {
                'type': 'Suspicious Port',
                'severity': 5,  # MEDIUM
                'source_ip': packet_data.get('src_ip'),
                'target_ip': packet_data.get('dst_ip'),
                'target_port': dst_port,
                'description': f'Connection to suspicious port {dst_port} detected',
                'timestamp': datetime.now().isoformat(),
                'confidence': 0.70
            }

        return None

    def cleanup_old_data(self):
        """Cleanup old tracking data to prevent memory leaks"""
        now = datetime.now()

        # Cleanup port scan tracker
        for ip in list(self.port_access.keys()):
            cutoff = now - timedelta(seconds=self.port_scan_window * 2)
            self.port_access[ip]['timestamps'] = [
                ts for ts in self.port_access[ip]['timestamps'] if ts > cutoff
            ]
            if not self.port_access[ip]['timestamps']:
                del self.port_access[ip]

        # Cleanup traffic tracker
        for ip in list(self.traffic_count.keys()):
            cutoff = now - timedelta(seconds=self.ddos_window * 2)
            self.traffic_count[ip]['timestamps'] = [
                ts for ts in self.traffic_count[ip]['timestamps'] if ts > cutoff
            ]
            if not self.traffic_count[ip]['timestamps']:
                del self.traffic_count[ip]


if __name__ == "__main__":
    # Test signature detector
    logging.basicConfig(level=logging.INFO)

    detector = SignatureDetector()

    # Test port scan detection
    print("\n=== Testing Port Scan Detection ===")
    for i in range(60):
        packet = {
            'src_ip': '192.168.1.100',
            'dst_ip': '192.168.1.1',
            'dst_port': 8000 + i,
            'protocol': 'TCP'
        }
        alert = detector.detect(packet)
        if alert:
            print(f"🚨 Alert: {alert}")

    # Test SQL injection detection
    print("\n=== Testing SQL Injection Detection ===")
    packet = {
        'src_ip': '192.168.1.100',
        'dst_ip': '192.168.1.1',
        'dst_port': 80,
        'protocol': 'TCP',
        'payload': "username=' OR '1'='1' --"
    }
    alert = detector.detect(packet)
    if alert:
        print(f"🚨 Alert: {alert}")
