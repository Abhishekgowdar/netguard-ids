"""
Packet Parser - Extracts useful information from network packets
"""
import logging
from scapy.all import IP, TCP, UDP, ICMP, DNS, Raw
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class PacketParser:
    """
    Parse network packets and extract relevant features
    """

    @staticmethod
    def parse(packet) -> Optional[Dict]:
        """
        Parse a packet and extract features

        Args:
            packet: Scapy packet object

        Returns:
            Dictionary with packet features or None if parsing fails
        """
        try:
            # Initialize packet data
            packet_data = {
                'timestamp': datetime.now().isoformat(),
                'protocol': 'unknown',
                'src_ip': None,
                'dst_ip': None,
                'src_port': None,
                'dst_port': None,
                'length': len(packet),
                'flags': '',
                'payload': '',
                'info': ''
            }

            # Check if packet has IP layer
            if IP in packet:
                ip_layer = packet[IP]
                packet_data['src_ip'] = ip_layer.src
                packet_data['dst_ip'] = ip_layer.dst
                packet_data['ttl'] = ip_layer.ttl
                packet_data['protocol'] = PacketParser._get_protocol_name(ip_layer.proto)

                # TCP Protocol
                if TCP in packet:
                    tcp_layer = packet[TCP]
                    packet_data['src_port'] = tcp_layer.sport
                    packet_data['dst_port'] = tcp_layer.dport
                    packet_data['protocol'] = 'TCP'
                    packet_data['flags'] = PacketParser._get_tcp_flags(tcp_layer)
                    packet_data['seq'] = tcp_layer.seq
                    packet_data['ack'] = tcp_layer.ack

                    # Extract payload
                    if Raw in packet:
                        payload = packet[Raw].load
                        try:
                            packet_data['payload'] = payload.decode('utf-8', errors='ignore')[:200]
                        except:
                            packet_data['payload'] = str(payload)[:200]

                    packet_data['info'] = f"{packet_data['src_ip']}:{packet_data['src_port']} → {packet_data['dst_ip']}:{packet_data['dst_port']} [{packet_data['flags']}]"

                # UDP Protocol
                elif UDP in packet:
                    udp_layer = packet[UDP]
                    packet_data['src_port'] = udp_layer.sport
                    packet_data['dst_port'] = udp_layer.dport
                    packet_data['protocol'] = 'UDP'

                    # DNS Query
                    if DNS in packet:
                        dns_layer = packet[DNS]
                        if dns_layer.qd:
                            packet_data['dns_query'] = dns_layer.qd.qname.decode('utf-8', errors='ignore')
                            packet_data['info'] = f"DNS Query: {packet_data['dns_query']}"

                    packet_data['info'] = packet_data.get('info', f"{packet_data['src_ip']}:{packet_data['src_port']} → {packet_data['dst_ip']}:{packet_data['dst_port']} [UDP]")

                # ICMP Protocol
                elif ICMP in packet:
                    icmp_layer = packet[ICMP]
                    packet_data['protocol'] = 'ICMP'
                    packet_data['icmp_type'] = icmp_layer.type
                    packet_data['icmp_code'] = icmp_layer.code
                    packet_data['info'] = f"ICMP Type {icmp_layer.type} Code {icmp_layer.code}"

            return packet_data

        except Exception as e:
            logger.error(f"Error parsing packet: {e}")
            return None

    @staticmethod
    def _get_protocol_name(proto_num: int) -> str:
        """Convert protocol number to name"""
        protocols = {
            1: 'ICMP',
            6: 'TCP',
            17: 'UDP',
            47: 'GRE',
            50: 'ESP',
            51: 'AH',
            58: 'ICMPv6'
        }
        return protocols.get(proto_num, f'Protocol-{proto_num}')

    @staticmethod
    def _get_tcp_flags(tcp_layer) -> str:
        """Extract TCP flags as string"""
        flags = []
        if tcp_layer.flags.S:
            flags.append('SYN')
        if tcp_layer.flags.A:
            flags.append('ACK')
        if tcp_layer.flags.F:
            flags.append('FIN')
        if tcp_layer.flags.R:
            flags.append('RST')
        if tcp_layer.flags.P:
            flags.append('PSH')
        if tcp_layer.flags.U:
            flags.append('URG')
        return ','.join(flags) if flags else 'NONE'

    @staticmethod
    def extract_features_for_ml(packet_data: Dict) -> Dict:
        """
        Extract numerical features for ML model

        Args:
            packet_data: Parsed packet dictionary

        Returns:
            Dictionary with numerical features
        """
        features = {
            'duration': 0,  # Will be calculated over time
            'protocol_type': PacketParser._encode_protocol(packet_data.get('protocol', 'unknown')),
            'src_bytes': packet_data.get('length', 0),
            'dst_bytes': 0,  # Will be calculated from responses
            'flag': PacketParser._encode_flags(packet_data.get('flags', '')),
            'land': 1 if packet_data.get('src_ip') == packet_data.get('dst_ip') else 0,
            'wrong_fragment': 0,
            'urgent': 0,
        }
        return features

    @staticmethod
    def _encode_protocol(protocol: str) -> int:
        """Encode protocol as number for ML"""
        protocols = {'TCP': 0, 'UDP': 1, 'ICMP': 2}
        return protocols.get(protocol, 3)

    @staticmethod
    def _encode_flags(flags: str) -> int:
        """Encode TCP flags as number for ML"""
        flag_map = {
            'SYN': 1,
            'SYN,ACK': 2,
            'ACK': 3,
            'FIN': 4,
            'RST': 5,
            'PSH': 6
        }
        return flag_map.get(flags, 0)


if __name__ == "__main__":
    # Test parser
    from scapy.all import IP, TCP

    # Create a test packet
    test_packet = IP(src="192.168.1.1", dst="8.8.8.8") / TCP(sport=12345, dport=80, flags="S")

    parser = PacketParser()
    result = parser.parse(test_packet)

    print("Parsed packet:")
    for key, value in result.items():
        print(f"  {key}: {value}")
