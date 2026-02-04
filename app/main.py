"""
FastAPI application entry point.

This is the main file that creates and configures the FastAPI application.
Run with: uvicorn app.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routes import urls


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    On startup: Creates all database tables if they don't exist.
    On shutdown: Any cleanup would go here.
    """
    # Startup: Create database tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")

    yield  # Application runs here

    # Shutdown: Add any cleanup code here if needed
    print("Application shutting down")


# Create the FastAPI application
app = FastAPI(
    title="URL Shortener API",
    description="A simple URL shortening service",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS (Cross-Origin Resource Sharing)
# This allows the API to be called from web browsers on different domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the URL routes
# The urls router handles all URL shortening endpoints
app.include_router(urls.router)


@app.get("/")
def root():
    """
    Root endpoint - returns a simple welcome message.

    Useful for health checks and verifying the API is running.
    """
    return {"message": "URL Shortener API"}
