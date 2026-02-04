"""
URL shortening routes.

This module contains all the API endpoints for:
- Creating shortened URLs
- Redirecting short URLs to original URLs
- Getting statistics for shortened URLs
"""

import random
import string

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import URL, Click
from app.schemas import URLCreate, URLResponse, URLStats, ClickInfo

# Create a router for URL-related endpoints
router = APIRouter()

# Characters used for generating short codes (base62)
# This gives us 62^6 = 56+ billion possible combinations
BASE62_CHARS = string.ascii_letters + string.digits  # a-z, A-Z, 0-9


def generate_short_code(length: int = 6) -> str:
    """
    Generate a random short code using base62 characters.

    Args:
        length: Number of characters in the code (default: 6)

    Returns:
        A random string like "aB3xY9"
    """
    return "".join(random.choices(BASE62_CHARS, k=length))


def get_unique_short_code(db: Session) -> str:
    """
    Generate a short code that doesn't exist in the database.

    Keeps generating new codes until we find one that's not taken.
    With 56 billion possibilities, collisions are rare.

    Args:
        db: Database session

    Returns:
        A unique short code
    """
    while True:
        short_code = generate_short_code()

        # Check if this code already exists
        existing = db.query(URL).filter(URL.short_code == short_code).first()

        if not existing:
            return short_code


@router.post("/api/shorten", response_model=URLResponse)
def create_short_url(url_data: URLCreate, request: Request, db: Session = Depends(get_db)):
    """
    Create a shortened URL.

    Takes a long URL and returns a shortened version.

    Request body:
        {"url": "https://example.com/very/long/url"}

    Returns:
        {
            "short_code": "abc123",
            "short_url": "http://localhost:8000/abc123",
            "original_url": "https://example.com/very/long/url",
            "created_at": "2024-01-15T10:30:00"
        }
    """
    # Generate a unique short code
    short_code = get_unique_short_code(db)

    # Create the URL record
    new_url = URL(
        original_url=str(url_data.url),
        short_code=short_code
    )

    # Save to database
    db.add(new_url)
    db.commit()
    db.refresh(new_url)  # Refresh to get the generated ID and created_at

    # Build the full short URL using the request's base URL
    base_url = str(request.base_url).rstrip("/")
    short_url = f"{base_url}/{short_code}"

    return URLResponse(
        short_code=new_url.short_code,
        short_url=short_url,
        original_url=new_url.original_url,
        created_at=new_url.created_at
    )


@router.get("/api/stats/{short_code}", response_model=URLStats)
def get_url_stats(short_code: str, db: Session = Depends(get_db)):
    """
    Get statistics for a shortened URL.

    Returns the total click count and the 10 most recent clicks.

    Returns:
        {
            "short_code": "abc123",
            "original_url": "https://example.com",
            "click_count": 42,
            "recent_clicks": [...]
        }
    """
    # Find the URL by short code
    url = db.query(URL).filter(URL.short_code == short_code).first()

    if not url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    # Count total clicks
    click_count = db.query(Click).filter(Click.url_id == url.id).count()

    # Get the 10 most recent clicks
    recent_clicks = (
        db.query(Click)
        .filter(Click.url_id == url.id)
        .order_by(Click.clicked_at.desc())
        .limit(10)
        .all()
    )

    # Convert to response format
    recent_clicks_info = [
        ClickInfo(
            clicked_at=click.clicked_at,
            ip_address=click.ip_address,
            user_agent=click.user_agent,
            referer=click.referer
        )
        for click in recent_clicks
    ]

    return URLStats(
        short_code=url.short_code,
        original_url=url.original_url,
        click_count=click_count,
        recent_clicks=recent_clicks_info
    )


@router.get("/{short_code}")
def redirect_to_url(short_code: str, request: Request, db: Session = Depends(get_db)):
    """
    Redirect a short URL to its original URL.

    When someone visits a short URL, this endpoint:
    1. Looks up the original URL
    2. Records the click for analytics
    3. Redirects the user to the original URL

    Uses HTTP 307 (Temporary Redirect) to preserve the request method.
    """
    # Find the URL by short code
    url = db.query(URL).filter(URL.short_code == short_code).first()

    if not url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    # Record the click
    click = Click(
        url_id=url.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        referer=request.headers.get("referer")
    )
    db.add(click)
    db.commit()

    # Redirect to the original URL
    return RedirectResponse(url=url.original_url, status_code=307)
