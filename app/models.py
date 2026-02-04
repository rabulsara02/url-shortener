"""
SQLAlchemy ORM models for the URL shortener.

These models define the structure of our database tables.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """
    User model for API authentication.

    Each user has an API key for authentication and a rate limit
    to prevent abuse of the service.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    api_key = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    rate_limit = Column(Integer, default=100)  # requests per hour

    # Relationship: One user can have many URLs
    urls = relationship("URL", back_populates="user")


class URL(Base):
    """
    URL model for storing shortened URLs.

    This is the main table that maps short codes to original URLs.
    """
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String(6), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # Optional expiration
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationship: Each URL belongs to one user (optional)
    user = relationship("User", back_populates="urls")

    # Relationship: One URL can have many clicks
    clicks = relationship("Click", back_populates="url")


class Click(Base):
    """
    Click model for tracking URL visits.

    Every time someone visits a shortened URL, we record information
    about the click for analytics purposes.
    """
    __tablename__ = "clicks"

    id = Column(Integer, primary_key=True, index=True)
    url_id = Column(Integer, ForeignKey("urls.id"), nullable=False)
    clicked_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    referer = Column(String, nullable=True)

    # Relationship: Each click belongs to one URL
    url = relationship("URL", back_populates="clicks")
