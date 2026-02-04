"""
Pydantic schemas for request and response validation.

These schemas define the shape of data coming in (requests)
and going out (responses) of the API.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, HttpUrl


# ----- Request Schemas -----

class URLCreate(BaseModel):
    """
    Schema for creating a new shortened URL.

    The 'url' field must be a valid HTTP or HTTPS URL.
    Pydantic will automatically validate this for us.
    """
    url: HttpUrl


# ----- Response Schemas -----

class URLResponse(BaseModel):
    """
    Schema for the response when a URL is shortened.

    This is what we send back after successfully creating a short URL.
    """
    short_code: str
    short_url: str
    original_url: str
    created_at: datetime

    class Config:
        from_attributes = True  # Allows converting from SQLAlchemy models


class ClickInfo(BaseModel):
    """
    Schema for individual click information.

    Used in the stats response to show recent clicks.
    """
    clicked_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referer: Optional[str] = None

    class Config:
        from_attributes = True


class URLStats(BaseModel):
    """
    Schema for URL statistics response.

    Shows how many times a URL has been clicked and recent click details.
    """
    short_code: str
    original_url: str
    click_count: int
    recent_clicks: List[ClickInfo]
