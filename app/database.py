"""
Database connection setup using SQLAlchemy.

This module creates the database engine, session, and base class for models.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Create the SQLAlchemy engine
# The engine is the starting point for any SQLAlchemy application.
# It manages the connection pool to the database.
#
# For SQLite, we need connect_args={"check_same_thread": False}
# because SQLite only allows one thread to use a connection by default,
# but FastAPI uses multiple threads.
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

# Create a session factory
# Each request will get its own session from this factory.
# autocommit=False: We control when to commit transactions
# autoflush=False: We control when to flush changes to the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
# All SQLAlchemy models will inherit from this class
Base = declarative_base()


def get_db():
    """
    Dependency function that provides a database session.

    This is used with FastAPI's dependency injection system.
    It creates a new session for each request and closes it when done.

    Usage in routes:
        @app.get("/example")
        def example(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
