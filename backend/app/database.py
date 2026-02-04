"""
Database configuration and session management.
Supports SQLite (dev) and PostgreSQL (prod) via environment variable.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Use DATABASE_URL env var or default to SQLite for local development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ioc_manager.db")

# Handle PostgreSQL URLs from cloud providers (they use postgres://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite requires special connect_args
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency that provides a database session.
    Ensures proper cleanup after each request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
