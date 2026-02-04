"""
SQLAlchemy ORM models for the IOC Manager.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Index
from .database import Base


class Threat(Base):
    """
    Represents an Indicator of Compromise (IOC).
    
    Attributes:
        id: Unique identifier (auto-incremented)
        type: Type of IOC (IP, Hash, URL, Domain)
        value: The actual indicator value
        severity: Threat severity level (High, Medium, Low)
        date_detected: Timestamp when the IOC was registered
        source: Optional source/origin of the IOC
    """
    __tablename__ = "threats"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type = Column(String(20), nullable=False, index=True)
    value = Column(String(500), nullable=False, unique=True)
    severity = Column(String(10), nullable=False, index=True)
    date_detected = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    source = Column(String(100), nullable=True)

    # Composite index for common query patterns
    __table_args__ = (
        Index('ix_threats_type_severity', 'type', 'severity'),
    )

    def __repr__(self):
        return f"<Threat(id={self.id}, type={self.type}, value={self.value})>"
