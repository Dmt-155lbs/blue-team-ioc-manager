"""
Pydantic schemas for request/response validation.
These schemas auto-generate the OpenAPI documentation.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, validator


class ThreatType(str, Enum):
    """Allowed IOC types."""
    IP = "IP"
    HASH = "Hash"
    URL = "URL"
    DOMAIN = "Domain"


class SeverityLevel(str, Enum):
    """Threat severity levels."""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class ThreatBase(BaseModel):
    """Base schema with common threat attributes."""
    type: ThreatType = Field(..., description="Type of IOC indicator")
    value: str = Field(..., min_length=1, max_length=500, description="The IOC value (IP, hash, URL, etc.)")
    severity: SeverityLevel = Field(..., description="Threat severity level")
    source: Optional[str] = Field(None, max_length=100, description="Source of the IOC (e.g., Firewall, SIEM)")

    @validator('value')
    def value_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Value cannot be empty or whitespace')
        return v.strip()


class ThreatCreate(ThreatBase):
    """Schema for creating a new threat (POST request body)."""
    pass

    class Config:
        schema_extra = {
            "example": {
                "type": "IP",
                "value": "192.168.1.50",
                "severity": "High",
                "source": "Firewall-01"
            }
        }


class ThreatResponse(ThreatBase):
    """Schema for threat response (includes id and date)."""
    id: int = Field(..., description="Unique threat identifier")
    date_detected: datetime = Field(..., description="Timestamp when the IOC was detected")

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "type": "IP",
                "value": "192.168.1.50",
                "severity": "High",
                "source": "Firewall-01",
                "date_detected": "2026-02-03T14:30:00"
            }
        }


class ThreatList(BaseModel):
    """Schema for paginated threat list response."""
    total: int = Field(..., description="Total number of threats")
    threats: List[ThreatResponse] = Field(..., description="List of threats")


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = Field(..., description="Service status")
    database: str = Field(..., description="Database connection status")
    timestamp: datetime = Field(..., description="Current server timestamp")


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    id: Optional[int] = None
