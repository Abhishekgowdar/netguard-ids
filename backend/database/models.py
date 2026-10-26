"""
Database models using SQLAlchemy
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Alert(Base):
    """Alert model for storing detected threats"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(100), nullable=False, index=True)
    severity = Column(Integer, nullable=False, index=True)
    source_ip = Column(String(45), index=True)  # IPv4 or IPv6
    target_ip = Column(String(45), index=True)
    target_port = Column(Integer)
    protocol = Column(String(20))
    description = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    confidence = Column(Float, default=1.0)
    resolved = Column(Boolean, default=False)

    # Additional metadata (stored as JSON-compatible text)
    metadata = Column(Text)  # JSON string for extra data

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'type': self.type,
            'severity': self.severity,
            'source_ip': self.source_ip,
            'target_ip': self.target_ip,
            'target_port': self.target_port,
            'protocol': self.protocol,
            'description': self.description,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'confidence': self.confidence,
            'resolved': self.resolved,
            'metadata': self.metadata
        }


class TrafficLog(Base):
    """Traffic log model for storing all captured packets"""
    __tablename__ = "traffic_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    source_ip = Column(String(45), index=True)
    dest_ip = Column(String(45), index=True)
    source_port = Column(Integer)
    dest_port = Column(Integer)
    protocol = Column(String(20), index=True)
    packet_length = Column(Integer)
    flags = Column(String(50))
    info = Column(Text)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'source_ip': self.source_ip,
            'dest_ip': self.dest_ip,
            'source_port': self.source_port,
            'dest_port': self.dest_port,
            'protocol': self.protocol,
            'packet_length': self.packet_length,
            'flags': self.flags,
            'info': self.info
        }
