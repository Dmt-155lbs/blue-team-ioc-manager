"""
IOC Manager API - FastAPI Application
Centralized management of Indicators of Compromise for Blue Teams.
"""
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
import os

from . import crud, models, schemas
from .database import engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI with OpenAPI documentation
app = FastAPI(
    title="IOC Manager API",
    description="""
## Gestor de Indicadores de Compromiso (IOC Manager)

API REST para equipos de Blue Team que permite:

- **Registrar** indicadores de compromiso desde scripts o herramientas externas
- **Consultar** todos los IOCs almacenados con filtros opcionales
- **Visualizar** estadísticas de amenazas detectadas

### Tipos de IOC soportados:
- `IP` - Direcciones IP maliciosas
- `Hash` - Hashes de archivos (MD5, SHA1, SHA256)
- `URL` - URLs maliciosas
- `Domain` - Dominios sospechosos

### Niveles de severidad:
- `High` - Amenaza crítica, requiere acción inmediata
- `Medium` - Amenaza moderada, investigar pronto
- `Low` - Amenaza menor, monitorear
    """,
    version="1.0.0",
    contact={
        "name": "Blue Team SOC",
        "email": "soc@organization.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration - allow frontend to communicate with API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Health Check ====================

@app.get(
    "/health",
    response_model=schemas.HealthResponse,
    tags=["System"],
    summary="Health Check",
    description="Verify API and database connectivity status."
)
def health_check(db: Session = Depends(get_db)):
    """Check if the API and database are operational."""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "timestamp": datetime.utcnow()
    }


# ==================== Threats Endpoints ====================

@app.get(
    "/api/threats",
    response_model=List[schemas.ThreatResponse],
    tags=["Threats"],
    summary="List all threats",
    description="Retrieve all IOCs with optional filtering by type and severity."
)
def list_threats(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    type: Optional[str] = Query(None, description="Filter by IOC type (IP, Hash, URL, Domain)"),
    severity: Optional[str] = Query(None, description="Filter by severity (High, Medium, Low)"),
    db: Session = Depends(get_db)
):
    """
    Retrieve all registered IOCs.
    
    - **skip**: Pagination offset
    - **limit**: Maximum number of results (max 1000)
    - **type**: Optional filter by IOC type
    - **severity**: Optional filter by severity level
    """
    threats = crud.get_threats(db, skip=skip, limit=limit, threat_type=type, severity=severity)
    return threats


@app.post(
    "/api/threats",
    response_model=schemas.ThreatResponse,
    status_code=201,
    tags=["Threats"],
    summary="Register new threat",
    description="Add a new IOC to the database. The IOC value must be unique."
)
def create_threat(
    threat: schemas.ThreatCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new Indicator of Compromise.
    
    - **type**: Type of IOC (IP, Hash, URL, Domain)
    - **value**: The actual indicator (must be unique)
    - **severity**: Threat level (High, Medium, Low)
    - **source**: Optional source identifier
    """
    # Check for duplicate
    existing = crud.get_threat_by_value(db, threat.value)
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"IOC with value '{threat.value}' already exists (ID: {existing.id})"
        )
    
    return crud.create_threat(db, threat)


@app.get(
    "/api/threats/{threat_id}",
    response_model=schemas.ThreatResponse,
    tags=["Threats"],
    summary="Get threat by ID",
    description="Retrieve a specific IOC by its unique identifier."
)
def get_threat(threat_id: int, db: Session = Depends(get_db)):
    """Retrieve details of a specific threat."""
    threat = crud.get_threat_by_id(db, threat_id)
    if not threat:
        raise HTTPException(status_code=404, detail=f"Threat with ID {threat_id} not found")
    return threat


@app.delete(
    "/api/threats/{threat_id}",
    response_model=schemas.MessageResponse,
    tags=["Threats"],
    summary="Delete threat",
    description="Remove an IOC from the database."
)
def delete_threat(threat_id: int, db: Session = Depends(get_db)):
    """Delete a threat by ID."""
    if crud.delete_threat(db, threat_id):
        return {"message": f"Threat {threat_id} deleted successfully", "id": threat_id}
    raise HTTPException(status_code=404, detail=f"Threat with ID {threat_id} not found")


@app.get(
    "/api/threats/stats/summary",
    tags=["Threats"],
    summary="Get threat statistics",
    description="Retrieve aggregated statistics about stored IOCs."
)
def get_statistics(db: Session = Depends(get_db)):
    """Get threat count statistics grouped by type and severity."""
    return crud.get_statistics(db)


# ==================== Serve Frontend ====================

# Check if frontend directory exists (for Docker deployment)
frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
    
    @app.get("/", include_in_schema=False)
    def serve_frontend():
        return FileResponse(os.path.join(frontend_path, "index.html"))


# ==================== Root Redirect ====================

@app.get("/api", tags=["System"], include_in_schema=False)
def api_root():
    """API root - provides links to documentation."""
    return {
        "message": "IOC Manager API v1.0.0",
        "documentation": "/docs",
        "alternative_docs": "/redoc",
        "health": "/health"
    }
