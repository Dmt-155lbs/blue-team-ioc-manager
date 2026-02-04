"""
CRUD operations for the Threat model.
Separates database logic from API routes.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from . import models, schemas


def get_threats(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    threat_type: Optional[str] = None,
    severity: Optional[str] = None
) -> List[models.Threat]:
    """
    Retrieve threats with optional filtering.
    
    Args:
        db: Database session
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        threat_type: Filter by IOC type
        severity: Filter by severity level
    
    Returns:
        List of Threat objects
    """
    query = db.query(models.Threat)
    
    if threat_type:
        query = query.filter(models.Threat.type == threat_type)
    if severity:
        query = query.filter(models.Threat.severity == severity)
    
    return query.order_by(desc(models.Threat.date_detected)).offset(skip).limit(limit).all()


def get_threat_count(
    db: Session,
    threat_type: Optional[str] = None,
    severity: Optional[str] = None
) -> int:
    """Get total count of threats with optional filtering."""
    query = db.query(models.Threat)
    
    if threat_type:
        query = query.filter(models.Threat.type == threat_type)
    if severity:
        query = query.filter(models.Threat.severity == severity)
    
    return query.count()


def get_threat_by_id(db: Session, threat_id: int) -> Optional[models.Threat]:
    """Retrieve a single threat by ID."""
    return db.query(models.Threat).filter(models.Threat.id == threat_id).first()


def get_threat_by_value(db: Session, value: str) -> Optional[models.Threat]:
    """Check if a threat with this value already exists."""
    return db.query(models.Threat).filter(models.Threat.value == value).first()


def create_threat(db: Session, threat: schemas.ThreatCreate) -> models.Threat:
    """
    Create a new threat record.
    
    Args:
        db: Database session
        threat: Validated threat data
    
    Returns:
        Created Threat object
    """
    db_threat = models.Threat(
        type=threat.type.value,
        value=threat.value,
        severity=threat.severity.value,
        source=threat.source
    )
    db.add(db_threat)
    db.commit()
    db.refresh(db_threat)
    return db_threat


def delete_threat(db: Session, threat_id: int) -> bool:
    """
    Delete a threat by ID.
    
    Returns:
        True if deleted, False if not found
    """
    threat = get_threat_by_id(db, threat_id)
    if threat:
        db.delete(threat)
        db.commit()
        return True
    return False


def get_statistics(db: Session) -> dict:
    """Get threat statistics for dashboard."""
    total = db.query(models.Threat).count()
    
    by_type = {}
    for threat_type in ['IP', 'Hash', 'URL', 'Domain']:
        count = db.query(models.Threat).filter(models.Threat.type == threat_type).count()
        by_type[threat_type] = count
    
    by_severity = {}
    for severity in ['High', 'Medium', 'Low']:
        count = db.query(models.Threat).filter(models.Threat.severity == severity).count()
        by_severity[severity] = count
    
    return {
        "total": total,
        "by_type": by_type,
        "by_severity": by_severity
    }
