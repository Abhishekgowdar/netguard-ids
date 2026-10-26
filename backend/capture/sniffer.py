"""
Packet Sniffer - Captures network traffic using Scapy
"""
import logging
from scapy.all import sniff, get_if_list, conf
from typing import Callable, Optional
import threading

logger = logging.getLogger(__name__)


class PacketSniffer:
    """
    Network packet sniffer using Scapy
    Captures packets and sends them to a callback function for processing
    """

    def __init__(self,
                 interface: Optional[str] = None,
                 filter_exp: str = "",
                 promisc: bool = True):
        """
        Initialize packet sniffer

        Args:
            interface: Network interface to capture on (None = auto-detect)
            filter_exp: BPF filter expression (e.g., "tcp port 80")
            promisc: Enable promiscuous mode
        """
        self.interface = interface or self._get_default_interface()
        self.filter_exp = filter_exp
        self.promisc = promisc
        self.running = False
        self.sniff_thread = None
        self.packet_callback = None

        logger.info(f"PacketSniffer initialized on interface: {self.interface}")
        logger.info(f"Promiscuous mode: {self.promisc}")
        if filter_exp:
            logger.info(f"Filter: {filter_exp}")

    def _get_default_interface(self) -> str:
        """Get the default network interface"""
        try:
            # Get list of available interfaces
            interfaces = get_if_list()

            # Try to find a suitable interface
            # Prefer: Ethernet, Wi-Fi, or first non-loopback interface
            for iface in interfaces:
                iface_lower = iface.lower()
                if any(keyword in iface_lower for keyword in ['ethernet', 'eth', 'wi-fi', 'wlan']):
                    logger.info(f"Auto-selected interface: {iface}")
                    return iface

            # Fallback to conf.iface
            default = conf.iface
            logger.info(f"Using default interface: {default}")
            return default
        except Exception as e:
            logger.error(f"Error detecting interface: {e}")
            logger.info("Available interfaces: " + ", ".join(get_if_list()))
            return conf.iface

    def start(self, callback: Callable):
        """
        Start packet capture in a separate thread

        Args:
            callback: Function to call for each captured packet
        """
        if self.running:
            logger.warning("Sniffer is already running")
            return

        self.packet_callback = callback
        self.running = True

        # Start sniffing in a separate thread
        self.sniff_thread = threading.Thread(target=self._sniff_packets, daemon=True)
        self.sniff_thread.start()

        logger.info("🔍 Packet capture started")

    def _sniff_packets(self):
        """Internal method to sniff packets"""
        try:
            sniff(
                iface=self.interface,
                prn=self._packet_handler,
                filter=self.filter_exp,
                promisc=self.promisc,
                store=False,  # Don't store packets in memory
                stop_filter=lambda x: not self.running
            )
        except PermissionError:
            logger.error("❌ Permission denied! Run as Administrator/root to capture packets")
            self.running = False
        except Exception as e:
            logger.error(f"❌ Error during packet capture: {e}")
            self.running = False

    def _packet_handler(self, packet):
        """Handle each captured packet"""
        try:
            if self.packet_callback and self.running:
                self.packet_callback(packet)
        except Exception as e:
            logger.error(f"Error in packet callback: {e}")

    def stop(self):
        """Stop packet capture"""
        if not self.running:
            logger.warning("Sniffer is not running")
            return

        self.running = False

        if self.sniff_thread:
            self.sniff_thread.join(timeout=5)

        logger.info("⏹️  Packet capture stopped")

    def is_running(self) -> bool:
        """Check if sniffer is running"""
        return self.running

    @staticmethod
    def list_interfaces():
        """List all available network interfaces"""
        interfaces = get_if_list()
        logger.info(f"Available interfaces: {', '.join(interfaces)}")
        return interfaces


if __name__ == "__main__":
    # Test packet sniffer
    logging.basicConfig(level=logging.INFO)

    def test_callback(packet):
        print(f"📦 Packet captured: {packet.summary()}")

    sniffer = PacketSniffer()
    print(f"Available interfaces: {sniffer.list_interfaces()}")
    print(f"Using interface: {sniffer.interface}")
    print("\nStarting capture (Ctrl+C to stop)...")

    try:
        sniffer.start(test_callback)
        # Keep main thread alive
        while sniffer.is_running():
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
        sniffer.stop()
