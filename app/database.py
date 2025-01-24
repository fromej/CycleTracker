import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import secrets

# Determine base directory and database path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'menstrual_tracker.db')

# SQLite Database Configuration
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create engine with thread-safety configuration for SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create a configured "Session" class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for declarative models
Base = declarative_base()


def get_db():
    """
    Dependency that creates a new database session for each request
    and closes it after the request is completed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
