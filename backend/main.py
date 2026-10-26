"""
NetGuard IDS - Main Application
Real-time Network Intrusion Detection System
"""
import sys
import time
import signal
from pathlib import Path

# Setup Python path
sys.path.append(str(Path(__file__).parent))

from config import *
from utils.logger import setup_logger
from utils.alerts import AlertManager
from capture.sniffer import PacketSniffer
from capture.parser import PacketParser
from detection.signature_rules import SignatureDetector
from detection.ml_detector import MLDetector
from database.db import Database

# Setup logger
logger = setup_logger("netguard", LOG_FILE, LOG_LEVEL)


class NetGuardIDS:
    """
    Main IDS application class
    """

    def __init__(self):
        """Initialize NetGuard IDS"""
        logger.info("=" * 60)
        logger.info("🛡️  NetGuard IDS - Network Intrusion Detection System")
        logger.info("=" * 60)

        # Initialize components
        self.parser = PacketParser()
        self.signature_detector = SignatureDetector(
            port_scan_threshold=PORT_SCAN_THRESHOLD,
            port_scan_window=PORT_SCAN_TIME_WINDOW,
            ddos_threshold=DDOS_THRESHOLD,
            ddos_window=DDOS_TIME_WINDOW
        )
        self.ml_detector = MLDetector(
            model_path=ML_MODEL_PATH,
            threshold=ML_ANOMALY_THRESHOLD
        )
        self.alert_manager = AlertManager()

        # Initialize database
        logger.info("Initializing database...")
        Database.init_db()
        self.db_session = Database.get_session()

        # Initialize packet sniffer
        self.sniffer = PacketSniffer(
            interface=NETWORK_INTERFACE,
            filter_exp=CAPTURE_FILTER,
            promisc=PROMISCUOUS_MODE
        )

        # Statistics
        self.packets_processed = 0
        self.start_time = time.time()
        self.last_cleanup_time = time.time()

        # Running flag
        self.running = False

        logger.info("✅ NetGuard IDS initialized successfully")

    def process_packet(self, packet):
        """
        Process a captured packet

        Args:
            packet: Scapy packet object
        """
        try:
            # Parse packet
            packet_data = self.parser.parse(packet)

            if not packet_data:
                return

            self.packets_processed += 1

            # Log packet (optional - can be disabled for performance)
            # Database.save_traffic_log(self.db_session, packet_data)

            # Check for threats using signature detection
            if SIGNATURE_DETECTION_ENABLED:
                signature_alert = self.signature_detector.detect(packet_data)
                if signature_alert:
                    self._handle_alert(signature_alert)

            # Check for anomalies using ML
            if ML_DETECTION_ENABLED and self.ml_detector.is_available():
                ml_alert = self.ml_detector.detect(packet_data)
                if ml_alert:
                    self._handle_alert(ml_alert)

            # Periodic status update
            if self.packets_processed % 1000 == 0:
                self._print_statistics()

            # Periodic cleanup
            current_time = time.time()
            if current_time - self.last_cleanup_time > 300:  # Every 5 minutes
                self.signature_detector.cleanup_old_data()
                self.last_cleanup_time = current_time

        except Exception as e:
            logger.error(f"Error processing packet: {e}")

    def _handle_alert(self, alert: dict):
        """
        Handle detected threat

        Args:
            alert: Alert dictionary
        """
        # Add to alert manager (in-memory)
        self.alert_manager.add_alert(alert)

        # Save to database
        Database.save_alert(self.db_session, alert)

        # Print alert
        self._print_alert(alert)

    def _print_alert(self, alert: dict):
        """Print alert to console"""
        severity_symbols = {
            1: '🟢', 2: '🟢', 3: '🟢',
            4: '🟡', 5: '🟡', 6: '🟡',
            7: '🟠', 8: '🟠',
            9: '🔴', 10: '🔴'
        }

        severity = alert.get('severity', 5)
        symbol = severity_symbols.get(severity, '⚪')

        logger.warning("=" * 60)
        logger.warning(f"{symbol} THREAT DETECTED: {alert.get('type', 'Unknown')}")
        logger.warning(f"   Severity: {severity}/10")
        logger.warning(f"   Source: {alert.get('source_ip', 'Unknown')}")
        logger.warning(f"   Target: {alert.get('target_ip', 'Unknown')}:{alert.get('target_port', 'N/A')}")
        logger.warning(f"   Description: {alert.get('description', 'N/A')}")
        logger.warning(f"   Confidence: {alert.get('confidence', 1.0):.2%}")
        logger.warning(f"   Time: {alert.get('timestamp', 'Unknown')}")
        logger.warning("=" * 60)

    def _print_statistics(self):
        """Print current statistics"""
        elapsed_time = time.time() - self.start_time
        packets_per_second = self.packets_processed / elapsed_time if elapsed_time > 0 else 0

        logger.info("─" * 60)
        logger.info(f"📊 Statistics:")
        logger.info(f"   Packets processed: {self.packets_processed}")
        logger.info(f"   Processing rate: {packets_per_second:.2f} packets/second")
        logger.info(f"   Alerts: {self.alert_manager.get_alert_count()}")
        logger.info(f"   Runtime: {elapsed_time/60:.1f} minutes")
        logger.info("─" * 60)

    def start(self):
        """Start the IDS"""
        logger.info("")
        logger.info("🚀 Starting NetGuard IDS...")
        logger.info(f"   Interface: {self.sniffer.interface}")
        logger.info(f"   Signature Detection: {'✅ Enabled' if SIGNATURE_DETECTION_ENABLED else '❌ Disabled'}")
        logger.info(f"   ML Detection: {'✅ Enabled' if ML_DETECTION_ENABLED and self.ml_detector.is_available() else '❌ Disabled'}")
        logger.info("")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 60)

        self.running = True
        self.sniffer.start(self.process_packet)

        # Keep main thread alive
        try:
            while self.running and self.sniffer.is_running():
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop the IDS"""
        if not self.running:
            return

        logger.info("")
        logger.info("⏹️  Stopping NetGuard IDS...")

        self.running = False
        self.sniffer.stop()

        # Print final statistics
        self._print_statistics()

        # Print alert summary
        stats = self.alert_manager.get_statistics()
        logger.info("")
        logger.info("🚨 Alert Summary:")
        logger.info(f"   Total Alerts: {stats['total_alerts']}")
        for severity, count in stats['by_severity'].items():
            logger.info(f"   {severity}: {count}")

        # Close database session
        self.db_session.close()

        logger.info("")
        logger.info("✅ NetGuard IDS stopped successfully")
        logger.info("=" * 60)


def main():
    """Main entry point"""
    # Create IDS instance
    ids = NetGuardIDS()

    # Setup signal handlers
    def signal_handler(sig, frame):
        ids.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start IDS
    ids.start()


if __name__ == "__main__":
    main()
